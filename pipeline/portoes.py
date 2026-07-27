#!/usr/bin/env python3
"""
Os 7 portoes de qualidade da spec (specs/2026-07-26-schema-base.md).

Antes desta implementacao so o portao 5 existia, dentro do reconciliador, e o
portao 7 era **tautologico**: perguntava por nome duplicado no mesmo kind
*depois* de a fusao ter unido as duplicatas. Era exatamente a fresta por onde
`death-from-above` passou -- dois feats distintos virando um registro quimera.
Por isso o portao 7 roda na fase `pre-fusao`, nao no fim.

Fases:
  pre-fusao  base recem-reconciliada, antes de fundir_renomeados.py
  final      base pronta para emitir

Uso:
    python3 portoes.py --fase pre-fusao
    python3 portoes.py --fase final
    python3 portoes.py --fase final --gravar-cobertura   # fixa a linha de base

Saida: relatorio em base/relatorio_portoes.md, codigo 1 se algum portao falha.
"""
import json, os, re, sys, glob, collections, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"
AON_DUMP = f"{BRUTOS}/aon_dump"
COBERTURA = f"{BASE}/_cobertura.json"

# Campos cujo preenchimento exige `prov`. `mechanized`, `kind` e `id` sao
# derivados do proprio pipeline, nao vieram de fonte -- nao entram.
CAMPOS_COM_PROV = ["name", "level", "traits", "rarity", "source",
                   "requires", "grants", "text"]

# Sufixos de variante legitima: -greater/-major/-true sao itens distintos por
# design da Paizo, nao colisao de identidade. Falso positivo conhecido.
SUFIXO_VARIANTE = re.compile(
    r"-(greater|lesser|major|minor|true|moderate|supreme|standard"
    r"|mk-?\d+|type-?[ivx]+|\d+)$")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def preenchido(v):
    return v not in (None, "", [], {})


# ---------------------------------------------------------------------------
# Indices das fontes, para os portoes que precisam comparar valor por fonte
# ---------------------------------------------------------------------------

def indice_aon():
    """id do AoN -> registro. Usa o dump completo; sem ele, o portao 2 desliga."""
    idx = {}
    for f in glob.glob(f"{AON_DUMP}/*.json"):
        if os.path.basename(f).startswith("_"):
            continue
        try:
            for r in json.load(open(f)):
                if isinstance(r, dict) and r.get("id"):
                    idx[str(r["id"])] = r
        except Exception:
            continue
    return idx


def indice_foundry():
    """_id do Foundry -> registro, com cache em disco (28k arquivos)."""
    cache = f"{BRUTOS}/_idx_foundry_campos.json"
    if os.path.exists(cache):
        return json.load(open(cache))
    raiz = os.environ.get("WB_FOUNDRY_PACKS", f"{BRUTOS}/foundry_repo/packs/pf2e")
    if not os.path.isdir(raiz):
        return {}
    idx = {}
    for f in glob.glob(f"{raiz}/**/*.json", recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict) or not d.get("_id"):
            continue
        sistema = d.get("system") or {}
        pub = sistema.get("publication") or sistema.get("source") or {}
        idx[d["_id"]] = {
            "name": d.get("name"),
            "level": (sistema.get("level") or {}).get("value"),
            "book": (pub.get("title") if isinstance(pub, dict) else None)
                    or (pub.get("value") if isinstance(pub, dict) else None),
            "rarity": (sistema.get("traits") or {}).get("rarity"),
        }
    json.dump(idx, open(cache, "w"), separators=(",", ":"))
    return idx


# ---------------------------------------------------------------------------
# Os portoes
# ---------------------------------------------------------------------------

def portao_1_prov(base, ctx):
    """Todo campo preenchido tem `prov`."""
    faltas = collections.Counter()
    exemplos = collections.defaultdict(list)
    for r in base:
        prov = r.get("prov") or {}
        for c in CAMPOS_COM_PROV:
            if preenchido(r.get(c)) and c not in prov:
                faltas[c] += 1
                if len(exemplos[c]) < 5:
                    exemplos[c].append(r["id"])
    return sum(faltas.values()), [
        f"`{c}`: {n} sem prov (ex.: {', '.join(exemplos[c])})"
        for c, n in faltas.most_common()]


def portao_2_level(base, ctx):
    """`level` divergente entre fontes sem entrada em `conflitos`."""
    aon, foundry = ctx["aon"], ctx["foundry"]
    if not aon and not foundry:
        return 0, ["DESLIGADO: sem dump do AoN nem clone do Foundry em disco"]
    achados = []
    for r in base:
        if r.get("kind") == "class-feature":
            continue          # level de class-feature vive na progressao da classe
        xr = r.get("xref") or {}
        niveis = {}
        a = aon.get(str(xr.get("aon", "")))
        if a and a.get("level") is not None:
            niveis["aon"] = a["level"]
        fid = str(xr.get("foundry", "")).split(".")[-1]
        f = foundry.get(fid)
        if f and f.get("level") is not None:
            niveis["foundry"] = f["level"]
        if len(set(niveis.values())) > 1:
            ja = any(c.get("campo") == "level" for c in (r.get("conflitos") or []))
            if not ja:
                achados.append(f"`{r['id']}`: {niveis} sem conflito registrado")
    return len(achados), achados[:40]


def portao_3_requires(base, ctx):
    """Nenhum `requires` cita id `wb:` inexistente."""
    ids = {r["id"] for r in base}
    alias = {}
    for r in base:
        for a in (r.get("aliases") or []):
            alias[f"wb:{r['kind']}/{norm(a).replace(' ', '-')}"] = r["id"]

    def refs(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "has" and isinstance(v, str):
                    yield v
                else:
                    yield from refs(v)
        elif isinstance(o, list):
            for x in o:
                yield from refs(x)

    orfaos = collections.Counter()
    for r in base:
        for ref in refs(r.get("requires")):
            if ref.startswith("wb:") and ref not in ids and ref not in alias:
                orfaos[ref] += 1
    return sum(orfaos.values()), [f"`{i}` citado {n}x" for i, n in orfaos.most_common(30)]


def portao_4_cobertura(base, ctx):
    """Cobertura por kind nao cai em relacao ao build anterior."""
    if not os.path.exists(COBERTURA):
        return 0, ["linha de base ausente -- grave com --gravar-cobertura"]
    ant = json.load(open(COBERTURA))
    atual = collections.Counter(r.get("kind") for r in base)
    quedas = []
    for kind, n in (ant.get("por_kind") or {}).items():
        if atual.get(kind, 0) < n:
            quedas.append(f"`{kind}`: {n} -> {atual.get(kind, 0)}")
    total_ant = ant.get("total", 0)
    if len(base) < total_ant:
        quedas.append(f"**total**: {total_ant} -> {len(base)}")
    return len(quedas), quedas


def portao_5_license(base, ctx):
    """Todo registro emitido tem `license`."""
    sem = [r["id"] for r in base if not (r.get("source") or {}).get("license")]
    return len(sem), [f"`{i}`" for i in sem[:30]]


def portao_6_traits(base, ctx):
    """Sobra `traits` categoricamente disjunto depois da uniao -- suspeita de colisao."""
    achados = []
    for r in base:
        for c in (r.get("conflitos") or []):
            if c.get("campo") != "traits":
                continue
            conjuntos = [set(v) for k, v in c.items()
                         if k not in ("campo", "escolhido") and isinstance(v, list)]
            # conjunto vazio e disjunto de tudo por vacuidade -- ausencia de
            # informacao, nao evidencia de que sao duas entidades
            conjuntos = [s for s in conjuntos if s]
            if len(conjuntos) >= 2 and not set.intersection(*conjuntos):
                achados.append(f"`{r['id']}`: {[sorted(s) for s in conjuntos]}")
    return len(achados), achados[:40]


def _grupos_de_identidade(docs):
    """Agrupa docs do AoN que sao o mesmo conteudo em edicoes diferentes.

    `remaster_id`/`legacy_id` ligam a versao legada a sua sucessora. Dois docs
    ligados assim nao sao ambiguidade -- sao o mesmo feat antes e depois do
    Remaster. O que sobra depois de agrupar e que e homonimo de verdade.
    """
    pai = {str(d.get("id")): str(d.get("id")) for d in docs}

    def raiz(x):
        while pai.get(x, x) != x:
            pai[x] = pai.get(pai[x], pai[x])
            x = pai[x]
        return x

    for d in docs:
        i = str(d.get("id"))
        for chave in ("remaster_id", "legacy_id"):
            # o AoN emite esses campos como LISTA ('remaster_id': ['feat-4388']),
            # nao como escalar -- tratar como string casa zero pares
            alvo = d.get(chave)
            for a in (alvo if isinstance(alvo, list) else [alvo]):
                if a is None:
                    continue
                a = str(a)
                if a in pai:
                    ra, rb = raiz(i), raiz(a)
                    if ra != rb:
                        pai[ra] = rb
    grupos = collections.defaultdict(list)
    for d in docs:
        grupos[raiz(str(d.get("id")))].append(d)
    return list(grupos.values())


def portao_7_homonimo(base, ctx):
    """Casamento ambiguo: a fonte tem N entidades para o nome que a base casou com 1.

    A versao anterior deste portao perguntava se dois registros da base tinham o
    mesmo nome no mesmo kind. Nunca disparava -- em nenhuma fase -- porque a
    ambiguidade nunca chega a produzir dois registros: o extrator casa por nome,
    escolhe **um** candidato entre os N da fonte, e os outros somem sem rastro.

    Medido em 2026-07-26: `Death from Above` tem 1 doc no Foundry (nivel 8,
    archetype) e 2 no AoN (feat-7610 archetype nivel 8; feat-7380 mitico nivel
    16). A base emitiu nivel 8 com traits `mythic` -- cruzou o Foundry com o
    doc errado do AoN e perdeu o outro feat inteiro. Idem `Reckless Abandon`,
    com 4 docs no AoN formando 2 pares legacy/remaster distintos.
    """
    aon = ctx["aon"]
    if not aon:
        return 0, ["DESLIGADO: sem dump do AoN em disco (rode dump_aon.py)"]

    por_nome = collections.defaultdict(list)
    for d in aon.values():
        cat = str(d.get("category") or "")
        if cat:
            por_nome[(cat, norm(d.get("name")))].append(d)

    # casos ja resolvidos por desmembrar_colisoes.py: o irmao existe, entao a
    # multiplicidade na fonte deixou de ser ambiguidade nao tratada
    ja_desmembrados = {r["desmembrado_de"] for r in base if r.get("desmembrado_de")}

    achados = []
    for r in base:
        if r.get("desmembrado_de") or r["id"] in ja_desmembrados:
            continue
        # class-feature e UM registro compartilhado por N classes, por decisao da
        # spec ("nivel de class-feature pertence a classe"). O AoN indexa um doc
        # por classe concedente -- `Alertness` tem 12 --, entao multiplicidade
        # ali e o modelo funcionando, nao colisao.
        if r.get("kind") == "class-feature":
            continue
        chave = (r.get("kind"), norm(r.get("name")))
        candidatos = por_nome.get(chave)
        if not candidatos or len(candidatos) < 2:
            continue
        grupos = _grupos_de_identidade(candidatos)
        if len(grupos) < 2:
            continue          # so pares legacy/remaster: fusao legitima
        slug = r["id"].split("/", 1)[-1]
        if SUFIXO_VARIANTE.search(slug):
            continue          # ja desmembrado com sufixo

        # Criterio da propria spec: "conflito com valores categoricamente
        # disjuntos nao e divergencia de fonte -- e sinal de que duas entidades
        # foram fundidas". Grupos que batem em level E traits sao a mesma coisa
        # em duas edicoes (par legacy/remaster que o AoN nao declarou); grupos
        # que divergem sao entidades diferentes disputando o mesmo slug.
        assinaturas = {(g[0].get("level"),
                        tuple(sorted(map(str, g[0].get("trait") or []))))
                       for g in grupos}
        casado = str((r.get("xref") or {}).get("aon") or "")
        resumo = "; ".join(
            f"{g[0].get('id')}(nv{g[0].get('level')},"
            f"{','.join(map(str, g[0].get('trait') or []))[:28]})"
            for g in grupos[:4])
        linha = (f"`{r['id']}` casou com `{casado or '-'}` mas o AoN tem "
                 f"{len(grupos)} entidades: {resumo}")
        if len(assinaturas) > 1:
            achados.append(("colisao", linha))
        else:
            achados.append(("par-nao-declarado", linha))

    graves = [l for t, l in achados if t == "colisao"]
    brandos = [l for t, l in achados if t == "par-nao-declarado"]
    detalhe = [f"**COLISAO** {l}" for l in graves[:40]]
    if brandos:
        detalhe.append(f"")
        detalhe.append(f"_Alem disso, {len(brandos)} casos de mesmo level e mesmos "
                       f"traits -- par legacy/remaster que o AoN nao declarou via "
                       f"`remaster_id`. Fusao legitima, nao bloqueia o build._")
        detalhe += [f"- {l}" for l in brandos[:15]]
    return len(graves), detalhe


PORTOES = [
    (1, "prov por campo preenchido", portao_1_prov, ("pre-fusao", "final")),
    (2, "level divergente sem conflito", portao_2_level, ("pre-fusao", "final")),
    (3, "requires citando id inexistente", portao_3_requires, ("final",)),
    (4, "cobertura caindo vs build anterior", portao_4_cobertura, ("final",)),
    (5, "license ausente", portao_5_license, ("pre-fusao", "final")),
    (6, "traits disjunto apos uniao", portao_6_traits, ("pre-fusao", "final")),
    (7, "homonimo no mesmo kind", portao_7_homonimo, ("pre-fusao",)),
]


def main():
    fase = "final"
    if "--fase" in sys.argv:
        fase = sys.argv[sys.argv.index("--fase") + 1]
    if fase not in ("pre-fusao", "final"):
        print(f"fase invalida: {fase}", file=sys.stderr)
        return 2

    base = json.load(open(f"{BASE}/index.json"))
    ctx = {"aon": indice_aon(), "foundry": indice_foundry()}
    print(f"fase {fase}: {len(base)} registros  "
          f"(indices: aon={len(ctx['aon'])}, foundry={len(ctx['foundry'])})")

    linhas = [f"# Portoes de qualidade -- fase `{fase}`", "",
              f"- registros avaliados: **{len(base)}**", ""]
    falhou = 0
    for num, nome, fn, fases in PORTOES:
        if fase not in fases:
            linhas.append(f"## Portao {num} -- {nome}\n\nNAO SE APLICA nesta fase.\n")
            print(f"  portao {num}  n/a   {nome}")
            continue
        n, detalhe = fn(base, ctx)
        ok = n == 0
        falhou += 0 if ok else 1
        print(f"  portao {num}  {'OK  ' if ok else 'FALHA'}  {nome}: {n}")
        linhas.append(f"## Portao {num} -- {nome}\n")
        linhas.append(f"**{'PASSOU' if ok else 'FALHOU'}** -- {n} ocorrencia(s).\n")
        linhas += [f"- {d}" for d in detalhe]
        linhas.append("")

    if "--gravar-cobertura" in sys.argv:
        json.dump({"total": len(base),
                   "por_kind": dict(collections.Counter(r.get("kind") for r in base))},
                  open(COBERTURA, "w"), indent=1)
        print(f"  linha de base de cobertura gravada em {COBERTURA}")

    open(f"{BASE}/relatorio_portoes_{fase}.md", "w").write("\n".join(linhas) + "\n")
    print(f"-> base/relatorio_portoes_{fase}.md   "
          f"({'todos passaram' if not falhou else str(falhou) + ' portao(es) falhando'})")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
