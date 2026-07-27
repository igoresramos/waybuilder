#!/usr/bin/env python3
"""
Fusao de conteudo renomeado entre Legacy e Remaster.

Politica, decidida pelo Igor:
  - nome nao importa. Power Attack e Vicious Swing sao a mesma coisa.
  - o que importa e a REGRA e o CONTEUDO. Nada se perde.

Par confirmado vira UM registro, com todos os nomes preservados em `aliases`.
Nenhum registro e descartado -- inclusive o que a Paizo cortou.

## Por que esta versao existe

A anterior casava por **similaridade de prosa** (Jaccard >= 0.62 sobre os
primeiros 900 caracteres) e deletava o lado legado. Auditoria de 2026-07-26:

  - 597 registros deletados; amostra de 60 contra o `remaster_id` do AoN
    confirmou **35%** como fusao correta
  - 393 dos 597 (65,8%) fundiram registros com `level`, `price_cp` ou `damage`
    diferentes -- ou seja, itens distintos
  - `wb:equipment/aeon-stone` engoliu **24 pedras distintas** (Amber Sphere,
    Black Disc, Agate Ellipsoid...), cada uma com efeito proprio, porque a prosa
    de todas comeca igual
  - `Poi` virou `Shield Bash`; `Tonfa` virou `Shuan Ji`, do mesmo livro

Prosa curta e generica casa 1.00 com dezenas de entidades. O sinal estava
errado: prosa parecida nao e evidencia de identidade.

Agora a chave e o `remaster_id`/`legacy_id` do **AoN**, que e a fonte que
carrega a ponte legado/remaster de proposito. Prosa entra so como desempate,
quando um legado aponta para mais de um sucessor. E antes de fundir, campo
estruturado que discorda **veta** a fusao -- par declarado com `level` ou
`price_cp` diferente vai para revisao, nao para o merge.

Entrada: pipeline/base/index.json (+ base/text/, dados_brutos/aon_dump/)
Saida:   pipeline/base/index.json reescrito + relatorio_fusao.md
"""
import json, os, re, collections, unicodedata, glob, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
AON_DUMP = f"{AQUI}/dados_brutos/aon_dump"

# Campos que, divergindo, provam que os dois registros nao sao a mesma entidade.
# `traits` fica de fora de proposito: o Remaster renomeia trait com frequencia
# (gnoll -> kholo), e isso e justamente o que a ponte existe para reconciliar.
CAMPOS_VETO = ("level", "price_cp", "damage", "kind")

STOP = set("a an the you your of to and or with in on for is are that this it as by from at "
           "be can if when have has gain gains use uses make makes than then not no".split())


def toks(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return {w for w in re.findall(r"[a-z]{3,}", s) if w not in STOP}


def carregar_aon():
    idx = {}
    for f in glob.glob(f"{AON_DUMP}/*.json"):
        if os.path.basename(f).startswith("_"):
            continue
        try:
            for d in json.load(open(f)):
                if isinstance(d, dict) and d.get("id"):
                    idx[str(d["id"])] = d
        except Exception:
            continue
    return idx


def como_lista(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def main():
    base = json.load(open(f"{BASE}/index.json"))
    aon = carregar_aon()
    if not aon:
        print(f"ERRO: sem dump do AoN em {AON_DUMP}. Rode `python3 dump_aon.py` "
              f"antes -- sem a ponte legado/remaster esta etapa nao tem chave "
              f"confiavel e NAO deve cair para prosa.", file=sys.stderr)
        return 1

    T = {}
    if os.path.isdir(f"{BASE}/text"):
        for f in os.listdir(f"{BASE}/text"):
            T.update(json.load(open(f"{BASE}/text/{f}")))

    def prosa(r):
        t = T.get(r.get("text") or "", "")
        return toks(re.sub(r"^\s*\S.{0,80}?Source .{0,60}?pg\.\s*\d+", "", t)[:900])

    por_aon = collections.defaultdict(list)
    for r in base:
        a = (r.get("xref") or {}).get("aon")
        if a:
            por_aon[str(a)].append(r)

    # --- 1. pares declarados pelo AoN -------------------------------------
    # `remaster_id` no doc legado aponta o sucessor; `legacy_id` no remaster
    # aponta a origem. Coletamos os dois sentidos e deduplicamos.
    candidatos = collections.defaultdict(set)      # legado_aon -> {remaster_aon}
    for aid, regs in por_aon.items():
        d = aon.get(aid)
        if not d:
            continue
        for alvo in como_lista(d.get("remaster_id")):
            if str(alvo) in por_aon:
                candidatos[aid].add(str(alvo))
        for origem in como_lista(d.get("legacy_id")):
            if str(origem) in por_aon:
                candidatos[str(origem)].add(aid)

    # --- 2. desempate por prosa quando ha mais de um sucessor -------------
    resolvidos, ambiguos = {}, []
    for legado, alvos in candidatos.items():
        alvos = {a for a in alvos if a != legado}
        if not alvos:
            continue
        if len(alvos) == 1:
            resolvidos[legado] = next(iter(alvos))
            continue
        pl = prosa(por_aon[legado][0])
        melhor, score = None, -1.0
        for a in sorted(alvos):
            pa = prosa(por_aon[a][0])
            j = len(pl & pa) / len(pl | pa) if (pl or pa) else 0.0
            if j > score:
                score, melhor = j, a
        resolvidos[legado] = melhor
        ambiguos.append((legado, sorted(alvos), melhor, round(score, 3)))

    # --- 3. veto por campo estruturado divergente -------------------------
    def valor(r, campo):
        return r.get(campo) if campo != "price_cp" else (
            r.get("price_cp") if "price_cp" in r else (r.get("price") or {}).get("cp")
            if isinstance(r.get("price"), dict) else None)

    fusoes, vetados = [], []
    for legado_aon, remaster_aon in sorted(resolvidos.items()):
        rl = por_aon[legado_aon][0]
        rr = por_aon[remaster_aon][0]
        if rl["id"] == rr["id"]:
            continue
        divergem = []
        for campo in CAMPOS_VETO:
            a, b = valor(rl, campo), valor(rr, campo)
            if a is not None and b is not None and a != b:
                divergem.append(f"{campo}: {a!r} != {b!r}")
        if divergem:
            vetados.append((rl, rr, divergem))
            continue
        fusoes.append((rl, rr))

    # --- 4. aplicar ------------------------------------------------------
    absorvidos = set()
    por_id = {r["id"]: r for r in base}
    for legado, remaster in fusoes:
        if legado["id"] in absorvidos or remaster["id"] in absorvidos:
            continue
        alvo = por_id[remaster["id"]]
        aliases = set(alvo.get("aliases") or [])
        aliases.add(legado.get("name"))
        aliases.update(legado.get("aliases") or [])
        aliases.discard(alvo.get("name"))
        alvo["aliases"] = sorted(a for a in aliases if a)
        alvo.setdefault("xref", {}).update(
            {f"legado_{k}": v for k, v in (legado.get("xref") or {}).items()})
        alvo.setdefault("historico", []).append({
            "nome_legado": legado.get("name"),
            "livro_legado": (legado.get("source") or {}).get("book"),
            "id_legado": legado["id"],
            "chave": "aon:remaster_id",
        })
        absorvidos.add(legado["id"])

    final = [r for r in base if r["id"] not in absorvidos]
    json.dump(final, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    com_alias = sum(1 for r in final if r.get("aliases"))
    print(f"pares declarados pelo AoN: {len(resolvidos)}")
    print(f"  vetados por campo estruturado divergente: {len(vetados)}")
    print(f"  desempatados por prosa (sucessor multiplo): {len(ambiguos)}")
    print(f"base: {len(base)} -> {len(final)} registros ({len(absorvidos)} absorvidos)")
    print(f"registros com alias: {com_alias}")

    linhas = ["# Fusao de renomeados", "",
              "Chave: `remaster_id`/`legacy_id` do AoN. Prosa **nao** cria par --",
              "entra so para desempatar sucessor multiplo. Campo estruturado",
              "divergente veta a fusao.", "",
              f"- pares declarados pelo AoN: **{len(resolvidos)}**",
              f"- fundidos: **{len(absorvidos)}**",
              f"- vetados por divergencia estrutural: **{len(vetados)}**",
              f"- desempatados por prosa: **{len(ambiguos)}**",
              f"- base: {len(base)} -> **{len(final)}** registros",
              f"- registros com alias: **{com_alias}**", "",
              "## Vetados -- par declarado, conteudo divergente", "",
              "O AoN liga os dois, mas um campo estruturado discorda. Revisar a mao;",
              "fundir aqui apagaria dado.", ""]
    for rl, rr, motivo in vetados[:60]:
        linhas.append(f"- `{rl['id']}` x `{rr['id']}` -- {'; '.join(motivo)}")
    if ambiguos:
        linhas += ["", "## Sucessor multiplo, desempatado por prosa", ""]
        for legado, alvos, escolhido, score in ambiguos[:40]:
            linhas.append(f"- `{legado}` -> {alvos} escolheu `{escolhido}` ({score})")
    linhas += ["", "## Fusoes aplicadas", ""]
    for legado, remaster in fusoes:
        if legado["id"] in absorvidos:
            linhas.append(f"- **{legado.get('name')}** -> **{remaster.get('name')}** "
                          f"_({legado.get('kind')})_")
    open(f"{BASE}/relatorio_fusao.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_fusao.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
