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
import json, os, sys, collections

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


def grants_de_background(r):
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
        g.append({"grant_feat": [str(x) for x in lista]})
    return g


def grants_de_heranca(r):
    g = []
    if r.get("ancestry"):
        g.append({"requires_ancestry": r["ancestry"]})
    return g


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

    for r in base:
        conversor = CONVERSORES.get(r.get("kind"))
        if conversor is None:
            continue
        derivados = conversor(r)
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
