#!/usr/bin/env python3
"""
Faz ancestria, heranca e background emitirem `grants`, como todo o resto.

A spec define UMA linguagem de efeito (`grants`), e ela so era respeitada em
`class`. Na pratica o mesmo conceito morava em tres formatos:

    class       grants: [{hp_per_level: 10}, {proficiency: {...}}]
    ancestry    campos soltos: hp, size, speed, boosts, senses, languages, flaw
    background  outro conjunto: boosts, skill_training, attribute, skill, feat

Um motor que quisesse derivar estatistica precisava conhecer os tres, e cada
tipo novo de conteudo viraria caso especial. Pior: `mechanized`, que a spec
define como `== bool(grants)`, marcava 50 ancestrias e 502 backgrounds como
`false` -- "o jogador resolve na mao" -- quando o efeito deles e perfeitamente
calculavel e ja estava estruturado.

Os campos originais **permanecem**. Isto adiciona a projecao canonica, nao
substitui: quem le `r["hp"]` continua funcionando, e nada se perde.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_efeitos.md
"""
import ast, collections, json, os, re, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"


def grants_de_ancestria(r):
    g = []
    if isinstance(r.get("hp"), int):
        g.append({"hp_ancestry": r["hp"]})
    if r.get("size"):
        g.append({"size": r["size"]})
    if isinstance(r.get("speed"), int):
        g.append({"speed": {"land": r["speed"]}})
    for b in (r.get("boosts") or []):
        if isinstance(b, dict) and "ability_boost" in b:
            g.append(b)
    # `flaw` vem como dict, nao lista -- iterar direto entrega as chaves
    defeitos = r.get("flaw") or []
    if isinstance(defeitos, dict):
        defeitos = [defeitos]
    for f in defeitos:
        if isinstance(f, dict):
            g.append(f)
    for s in (r.get("senses") or []):
        g.append({"sense": s})
    idiomas = r.get("languages")
    if isinstance(idiomas, dict):
        if idiomas.get("auto"):
            g.append({"language": {"auto": idiomas["auto"]}})
        if idiomas.get("bonus") or idiomas.get("free"):
            g.append({"language": {"free": idiomas.get("bonus") or idiomas.get("free")}})
    elif isinstance(idiomas, list) and idiomas:
        g.append({"language": {"auto": idiomas}})
    return g


def norm(s):
    """Mesma normalizacao de `resolver_referencias.py` -- nao inventar terceira."""
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("\u2019", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def nome_do_alvo(x):
    """O alvo de `grant_feat` chega em tres formas; devolve o NOME de cada uma.

    Ate 2026-07-29 a linha era `[str(x) for x in lista]`, e `str()` sobre um
    dict devolve o `repr` -- por isso 400 dos 926 alvos da base eram a string
    `"{'name': 'Hobnobber', 'foundry_uuid': '...'}"`. O dado para resolver
    estava DENTRO do valor o tempo todo.

    Spec: `specs/2026-07-29-grant-feat-de-background.md`
    """
    if isinstance(x, dict):
        return x.get("name")
    if isinstance(x, str):
        if x.startswith("wb:"):
            return None                       # ja e id, nao ha o que resolver
        if x.startswith("{"):
            try:
                return (ast.literal_eval(x) or {}).get("name")
            except (ValueError, SyntaxError):
                return None
        return x
    return None


def grants_de_background(r, indice_feat=None):
    g = []
    for b in (r.get("boosts") or []):
        if isinstance(b, dict) and "ability_boost" in b:
            g.append(b)
    treino = r.get("skill_training") or {}
    if treino.get("skills") or treino.get("lore"):
        g.append({"skill_training": {"auto": list(treino.get("skills") or []),
                                     "lore": list(treino.get("lore") or [])}})
    elif r.get("skill"):
        pericias = r["skill"] if isinstance(r["skill"], list) else [r["skill"]]
        g.append({"skill_training": {"auto": [str(x) for x in pericias]}})
    concedidos = r.get("feats_granted") or r.get("feat")
    if concedidos:
        lista = concedidos if isinstance(concedidos, list) else [concedidos]
        alvos = []
        for x in lista:
            if isinstance(x, str) and x.startswith("wb:"):
                alvos.append(x)
                continue
            resolvido = (indice_feat or {}).get(norm(nome_do_alvo(x)))
            # nao resolveu: mantem o original para o motor seguir avisando, e o
            # relatorio do build conta -- o numero fica visivel em vez de mudo
            alvos.append(resolvido or str(x))
        g.append({"grant_feat": alvos})
    return g


def grants_de_heranca(r):
    g = []
    if r.get("ancestry"):
        g.append({"requires_ancestry": r["ancestry"]})
    return g


# O pack do UUID do Foundry diz o kind, e e o que desempata nome homonimo:
# `Quick Alchemy` existe como class-feature E como feat, `Rage` como
# class-feature E como trait. Ver `resolver_grant_item`.
PACK_PARA_KIND = {
    "feats-srd": "feat",
    "classfeatures": "class-feature",
    "equipment-srd": "equipment",
    "spells-srd": "spell",
    "ancestryfeatures": "class-feature",
    "heritages": "heritage",
    "bestiary-ability-glossary-srd": None,
    # era `None` ("a base nao modela `action` como kind") ate 31/07, quando o
    # pack passou a ser extraido -- spec 2026-07-31-kind-action.md
    "actionspf2e": "action",
}


def resolver_grant_item(base):
    """`grant_item` aponta para o Foundry, nunca para a base -- 0 de 619.

    O UUID termina com o NOME (`Compendium.pf2e.feats-srd.Item.Alchemical
    Crafting`), nao com o `_id`, e por isso a ponte `xref.foundry`, que casa por
    id, resolvia zero. O motor so aplica alvo que comeca com `wb:`, entao
    nenhuma das 619 concessoes entregava nada -- mesmo defeito do item 70, com
    outra roupa.

    Resolve por nome normalizado, com o pack do UUID como desempate. Alvo que
    nao resolve MANTEM o UUID original: o motor segue avisando e o numero
    aparece no relatorio, em vez de virar um id inventado.

    Spec: `specs/2026-07-29-grant-item-por-nome.md`
    """
    por_nome = collections.defaultdict(list)
    for r in base:
        if r.get("name"):
            por_nome[norm(r["name"])].append(r)

    contagem = collections.Counter()
    for r in base:
        for g in (r.get("grants") or []):
            if not isinstance(g, dict) or "grant_item" not in g:
                continue
            gi = g["grant_item"]
            uuid = gi.get("uuid") if isinstance(gi, dict) else gi
            uuid = str(uuid or "")
            if not uuid or "{" in uuid or uuid.startswith("wb:"):
                contagem["dinamico ou ja resolvido"] += 1
                continue
            # `Compendium.pf2e.classfeatures.Item.Quick Alchemy`
            #  0          1    2              3    4
            # o pack e o TERCEIRO campo; `partes[1]` e sempre `pf2e` e nao
            # desempata nada.
            partes = uuid.split(".")
            nome = partes[-1]
            pack = partes[2] if len(partes) > 3 else None
            candidatos = por_nome.get(norm(nome), [])
            if len(candidatos) > 1 and pack in PACK_PARA_KIND:
                alvo_kind = PACK_PARA_KIND[pack]
                candidatos = [c for c in candidatos if c.get("kind") == alvo_kind]
            if len(candidatos) == 1:
                if isinstance(gi, dict):
                    gi["wb"] = candidatos[0]["id"]
                else:
                    g["grant_item"] = {"uuid": uuid, "wb": candidatos[0]["id"]}
                contagem["resolvido"] += 1
            else:
                contagem["nao resolvido" if not candidatos else "ambiguo"] += 1
    return contagem


CONVERSORES = {
    "ancestry": grants_de_ancestria,
    "background": grants_de_background,
    "heritage": grants_de_heranca,
}


def main():
    base = json.load(open(f"{BASE}/index.json"))
    contagem = collections.Counter()
    tipos = collections.Counter()
    exemplos = {}

    # nome normalizado -> id do feat. Montado aqui porque e o unico ponto do
    # pipeline que tem a base inteira em maos na hora de escrever o grant.
    indice_feat = {}
    for r in base:
        if r.get("kind") == "feat" and r.get("name"):
            indice_feat.setdefault(norm(r["name"]), r["id"])

    for r in base:
        conversor = CONVERSORES.get(r.get("kind"))
        if conversor is None:
            continue
        derivados = (conversor(r, indice_feat)
                     if conversor is grants_de_background else conversor(r))
        if not derivados:
            contagem[f"{r['kind']}: sem efeito derivavel"] += 1
            continue
        existentes = list(r.get("grants") or [])
        chaves = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in existentes}
        novos = [x for x in derivados
                 if json.dumps(x, sort_keys=True, ensure_ascii=False) not in chaves]
        if not novos:
            continue
        r["grants"] = existentes + novos
        r["mechanized"] = True          # a spec define mechanized == bool(grants)
        r.setdefault("prov", {})["grants"] = (
            (r.get("prov") or {}).get("grants", "") + "+derivado:campos-do-kind"
        ).lstrip("+")
        contagem[r["kind"]] += 1
        for x in novos:
            for k in x:
                tipos[k] += 1
        exemplos.setdefault(r["kind"], (r["id"], r.get("name"), novos))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    contagem_gi = resolver_grant_item(base)
    print("grant_item:", dict(contagem_gi))

    com_grants = sum(1 for r in base if r.get("grants"))
    print(f"registros que ganharam grants: {sum(v for k, v in contagem.items() if ':' not in k)}")
    for k, n in contagem.most_common():
        print(f"  {k:34} {n:>5}")
    print(f"\ntipos de efeito emitidos: {dict(tipos.most_common(12))}")
    print(f"base com grants: {com_grants} de {len(base)} ({com_grants/len(base):.1%})")

    linhas = ["# Modelo de efeito unificado", "",
              "A spec define UMA linguagem de efeito (`grants`) e ela so era",
              "respeitada em `class`. Ancestria usava campos soltos, background",
              "usava outro conjunto. Os campos originais permanecem -- isto",
              "adiciona a projecao canonica, nao substitui.", "",
              f"- registros que ganharam `grants`: "
              f"**{sum(v for k, v in contagem.items() if ':' not in k)}**",
              f"- base com `grants`: **{com_grants}** de {len(base)} "
              f"({com_grants/len(base):.1%})", "", "## Por kind", ""]
    linhas += [f"- `{k}`: {n}" for k, n in contagem.most_common()]
    linhas += ["", "## Exemplos", ""]
    for kind, (wid, nome, novos) in sorted(exemplos.items()):
        linhas.append(f"### {kind} -- `{wid}` ({nome})\n")
        linhas.append("```json\n" + json.dumps(novos, ensure_ascii=False, indent=1) + "\n```")
    open(f"{BASE}/relatorio_efeitos.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_efeitos.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
