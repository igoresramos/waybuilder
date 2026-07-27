#!/usr/bin/env python3
"""
Camada de reconciliacao da base canonica do Waybuilder.

Os extratores rodam em paralelo e cada um so enxerga a propria familia de
entidade. Esta camada e serial de proposito: ela e a unica que ve a base
inteira, e por isso e a unica que consegue

  1. normalizar grafia de nome e de livro entre fontes
  2. fundir registros que colidem no mesmo id canonico
  3. detectar pares legado/remaster que os extratores nao uniram
  4. registrar toda divergencia em `conflitos`, nunca escolher em silencio

Entrada: pipeline/saida/*.json
Saida:   pipeline/base/index.json + pipeline/base/relatorio_reconciliacao.md
"""
import json, os, re, sys, unicodedata, collections
import traits_uniao

AQUI = os.path.dirname(os.path.abspath(__file__))
ENTRADA = ["classes.json", "feats.json", "magias.json", "ancestrias.json",
           "equipamento.json", "companheiros.json", "referencia.json",
           "rituais.json"]

# precedencia por campo, conforme specs/2026-07-26-schema-base.md
PRECEDENCIA = {
    "grants":   ["foundry", "pf2etools", "aon"],
    "requires": ["pf2etools", "foundry", "aon"],
    "name":     ["aon", "foundry", "pf2etools"],
    "traits":   ["aon", "foundry", "pf2etools"],
    "rarity":   ["aon", "foundry", "pf2etools"],
    "text":     ["aon", "foundry", "pf2etools"],
    "source":   ["aon", "foundry", "pf2etools"],
    "level":    ["foundry", "pf2etools", "aon"],
}
PADRAO = ["foundry", "aon", "pf2etools"]


def normalizar(s):
    """Nome comparavel: sem acento, sem pontuacao, caixa baixa, espaco unico."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[-‐-―_/]+", " ", s)   # hifen de qualquer tipo vira espaco
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def normalizar_livro(b):
    """'Pathfinder Dark Archive (Remastered)' e 'Dark Archives (Remastered)' -> mesma chave."""
    n = normalizar(b)
    n = re.sub(r"^pathfinder ", "", n)
    n = re.sub(r"\bremastered\b", "remaster", n)
    n = re.sub(r"\barchives\b", "archive", n)      # Dark Archive(s)
    n = re.sub(r"\bcores?\b", "core", n)
    # o Foundry prefixa a linha editorial que o AoN nao usa:
    # 'Pathfinder Lost Omens Highhelm' e 'Highhelm' sao a mesma obra
    n = re.sub(r"^lost omens ", "", n)
    n = re.sub(r"^adventure path ", "", n)
    return n.strip()


_CANONICO = None


def canonizar_livro(b):
    """Grafia unica por obra, do mapa gerado a partir do AoN.

    `normalizar_livro` ja existia mas so rodava na COMPARACAO -- o valor
    emitido continuava saindo em duas grafias para 26 obras (11.116 registros),
    e 161 registros carregavam `\\r\\n` literal dentro do titulo.
    """
    global _CANONICO
    if _CANONICO is None:
        caminho = f"{AQUI}/canonico_livros.json"
        _CANONICO = (json.load(open(caminho)).get("canonico") or {}
                     if os.path.exists(caminho) else {})
    if not b:
        return b
    limpo = " ".join(str(b).replace("\r", " ").replace("\n", " ").split())
    return _CANONICO.get(normalizar_livro(limpo), limpo)


def carregar():
    regs = []
    for arq in ENTRADA:
        caminho = f"{AQUI}/saida/{arq}"
        if not os.path.exists(caminho):
            print(f"  ! ausente: {arq}", file=sys.stderr)
            continue
        d = json.load(open(caminho))
        lista = d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list)), [])
        for r in lista:
            if isinstance(r, dict) and r.get("id"):
                r.setdefault("_origem", arq)
                # canoniza ANTES de comparar: senao a mesma obra em duas grafias
                # vira conflito falso, e o valor emitido sai nas duas formas
                src = r.get("source")
                if isinstance(src, dict) and src.get("book"):
                    src["book"] = canonizar_livro(src["book"])
                regs.append(r)
    return regs


def fundir(grupo):
    """Funde N registros do mesmo id canonico, registrando divergencia."""
    base = dict(grupo[0])
    conflitos = list(base.get("conflitos") or [])
    prov = dict(base.get("prov") or {})
    xref = dict(base.get("xref") or {})

    # `traits` e uniao, nunca disputa: resolvido antes do laco de precedencia
    por_fonte_traits = {}
    for r in grupo:
        if r.get("traits"):
            fonte = (r.get("prov") or {}).get("traits") or r.get("_origem") or "desconhecida"
            por_fonte_traits.setdefault(str(fonte), []).extend(r["traits"])

    for outro in grupo[1:]:
        for k, v in outro.items():
            if k.startswith("_") or k in ("conflitos", "prov", "xref", "traits"):
                continue
            atual = base.get(k)
            if atual is None or atual == "" or atual == []:
                base[k] = v
                prov[k] = (outro.get("prov") or {}).get(k, "desconhecida")
            elif v not in (None, "", []) and json.dumps(atual, sort_keys=True, default=str) != \
                                             json.dumps(v, sort_keys=True, default=str):
                ordem = PRECEDENCIA.get(k, PADRAO)
                fa = prov.get(k, "desconhecida")
                fb = (outro.get("prov") or {}).get(k, "desconhecida")
                ia = ordem.index(fa) if fa in ordem else 99
                ib = ordem.index(fb) if fb in ordem else 99
                escolhido = fa if ia <= ib else fb
                if ib < ia:
                    base[k] = v
                    prov[k] = fb
                conflitos.append({"campo": k, fa: atual, fb: v, "escolhido": escolhido})
        xref.update(outro.get("xref") or {})
        prov.update({k: v for k, v in (outro.get("prov") or {}).items() if k not in prov})
        conflitos += list(outro.get("conflitos") or [])

    if por_fonte_traits:
        finais, aliases, fontes = traits_uniao.unir(por_fonte_traits)
        base["traits"] = finais
        if aliases:
            base["aliases_traits"] = sorted(
                set(base.get("aliases_traits") or []) | set(aliases))
        prov["traits"] = fontes

    base["prov"], base["xref"] = prov, xref
    if conflitos:
        base["conflitos"] = conflitos
    base.pop("_origem", None)
    return base


def main():
    regs = carregar()
    print(f"carregados: {len(regs)} registros de {len(ENTRADA)} familias")

    # --- 1. fundir colisoes de id ---
    por_id = collections.defaultdict(list)
    for r in regs:
        por_id[r["id"]].append(r)
    colisoes = {k: v for k, v in por_id.items() if len(v) > 1}
    base = [fundir(v) if len(v) > 1 else {k2: v2 for k2, v2 in v[0].items() if k2 != "_origem"}
            for v in por_id.values()]
    print(f"colisoes de id fundidas: {len(colisoes)}  ->  base com {len(base)} registros")

    # --- 1b. traits: refazer como uniao onde o extrator aplicou precedencia ---
    # Os extratores escolheram uma fonte antes de o reconciliador ver o dado,
    # mas gravaram cada faceta em `conflitos` -- da para reconstruir sem
    # re-rodar extrator nenhum.
    reparados = sum(1 for r in base if traits_uniao.unir_do_conflito(r))
    com_alias_trait = sum(1 for r in base if r.get("aliases_traits"))
    print(f"traits refeitos como uniao: {reparados}  "
          f"(registros com aliases_traits: {com_alias_trait})")

    # --- 2. suspeitas de par nao unido: mesmo kind + mesmo nome normalizado ---
    por_chave = collections.defaultdict(list)
    for r in base:
        por_chave[(r.get("kind"), normalizar(r.get("name")))].append(r)
    suspeitos = {k: v for k, v in por_chave.items() if len(v) > 1}
    print(f"suspeitas de par nao unido (mesmo kind+nome normalizado): {len(suspeitos)}")

    # --- 2b. inferir license ausente, marcando a inferencia ---
    LIVROS_ORC = {"player core", "player core 2", "gm core", "monster core",
                  "npc core", "war of immortals", "battlecry", "shining kingdoms",
                  "howl of the wild", "rage of elements", "divine mysteries"}
    inferidas = 0
    for r in base:
        src = r.get("source") or {}
        r["source"] = src
        if src.get("license"):
            continue
        livro = normalizar_livro(src.get("book") or "")
        if src.get("remaster") is True or livro in LIVROS_ORC:
            src["license"] = "ORC"
        elif livro:
            src["license"] = "OGL"      # tudo anterior ao Remaster
        else:
            continue                    # sem livro nao da para inferir
        r.setdefault("prov", {})["source.license"] = "inferida:livro"
        inferidas += 1
    print(f"license inferida a partir do livro: {inferidas}")

    # --- 2b2. duplicata de nome curto vinda so do pf2etools ---
    # `wb:armor/hide` e `wb:armor/hide-armor` sao o mesmo item: o pf2etools
    # grafa sem o substantivo do kind. Esses registros vinham sem `source`, e o
    # portao 5 os reportava como "sem license" -- o sintoma foi lido errado
    # desde o inicio: e falha de CASAMENTO, nao falta de licenca.
    por_kind_nome = {}
    for r in base:
        por_kind_nome[(r.get("kind"), normalizar(r.get("name")))] = r
    curtos = []
    for r in base:
        if (r.get("source") or {}).get("book"):
            continue
        if list((r.get("xref") or {}).keys()) != ["pf2etools"]:
            continue
        kind = r.get("kind")
        nome = normalizar(r.get("name"))
        alvo = por_kind_nome.get((kind, f"{nome} {kind}"))
        if alvo is not None and alvo["id"] != r["id"]:
            aliases = set(alvo.get("aliases") or []) | {r.get("name")}
            aliases.discard(alvo.get("name"))
            alvo["aliases"] = sorted(a for a in aliases if a)
            alvo.setdefault("xref", {}).update(
                {f"pf2etools_curto": (r.get("xref") or {}).get("pf2etools")})
            curtos.append(r["id"])
    if curtos:
        base = [r for r in base if r["id"] not in set(curtos)]
        print(f"duplicatas de nome curto (pf2etools) fundidas: {len(curtos)} -> {curtos}")

    # --- 2c. descartar artefato organizacional (pasta do Foundry, nao conteudo) ---
    def e_artefato(r):
        return (not (r.get("source") or {}).get("book")
                and not r.get("traits")
                and r.get("level") is None
                and not r.get("grants"))
    descartados = [r["id"] for r in base if e_artefato(r)]
    base = [r for r in base if not e_artefato(r)]
    if descartados:
        print(f"artefatos organizacionais descartados: {len(descartados)} -> {descartados}")

    # --- 3. portoes de qualidade ---
    falhas = collections.Counter()
    for r in base:
        if not r.get("prov"):
            falhas["sem prov"] += 1
        if not ((r.get("source") or {}).get("license")):
            falhas["sem license"] += 1
        if not r.get("id", "").startswith("wb:"):
            falhas["id fora do padrao"] += 1
    ids = collections.Counter(r["id"] for r in base)
    dups = [i for i, n in ids.items() if n > 1]
    if dups:
        falhas["id duplicado apos fusao"] = len(dups)

    os.makedirs(f"{AQUI}/base", exist_ok=True)
    json.dump(base, open(f"{AQUI}/base/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    kinds = collections.Counter(r.get("kind") for r in base)
    com_conf = sum(1 for r in base if r.get("conflitos"))

    linhas = ["# Relatorio de reconciliacao", "",
              f"- registros de entrada: **{len(regs)}**",
              f"- colisoes de id fundidas: **{len(colisoes)}**",
              f"- base final: **{len(base)}** registros",
              f"- registros com divergencia registrada: **{com_conf}**",
              f"- suspeitas de par nao unido: **{len(suspeitos)}**", "",
              "## Por kind", ""]
    linhas += [f"- `{k}`: {n}" for k, n in kinds.most_common()]
    linhas += ["", "## Portoes de qualidade", ""]
    linhas += ([f"- FALHA {k}: {n}" for k, n in falhas.items()] if falhas
               else ["- todos passaram"])
    if suspeitos:
        linhas += ["", "## Suspeitas de par nao unido (amostra)", "",
                   "Mesmo kind e mesmo nome normalizado, ids diferentes.", ""]
        for (kind, nome), v in list(suspeitos.items())[:40]:
            ids_s = ", ".join(f"`{x['id']}`" for x in v)
            livros = ", ".join(sorted({str((x.get('source') or {}).get('book')) for x in v}))
            linhas.append(f"- **{kind}** / _{nome}_ -> {ids_s}  ({livros})")
    open(f"{AQUI}/base/relatorio_reconciliacao.md", "w").write("\n".join(linhas) + "\n")

    print(f"\nportoes: {'FALHOU -> ' + str(dict(falhas)) if falhas else 'todos passaram'}")
    print(f"kinds: {dict(kinds)}")
    print(f"-> base/index.json  ({os.path.getsize(f'{AQUI}/base/index.json')/1e6:.1f} MB)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
