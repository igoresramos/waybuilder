#!/usr/bin/env python3
"""
Fusao de conteudo renomeado entre Legacy e Remaster.

Politica, decidida pelo Igor:
  - nome nao importa. Power Attack e Vicious Swing sao a mesma coisa.
  - o que importa e a REGRA e o CONTEUDO. Nada se perde.

Entao: par confirmado vira UM registro, com todos os nomes preservados em
`aliases` para a busca achar por qualquer um deles. Nenhum registro e
descartado -- inclusive o que a Paizo cortou (alinhamento, etc.), que num jogo
caseiro sem essa restricao continua valido.

Guarda contra falso positivo: prosa curta e generica ("your proficiency rank
for Reflex saves increases to master") casa 1.00 com dezenas de features. Por
isso exige TOKENS_MIN termos distintivos alem do score.

Entrada: pipeline/base/index.json (+ base/text/)
Saida:   pipeline/base/index.json reescrito + relatorio_fusao.md
"""
import json, os, re, collections, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

SCORE_MIN = 0.62      # similaridade de prosa
TOKENS_MIN = 15       # termos distintivos: barra prosa generica
STOP = set("a an the you your of to and or with in on for is are that this it as by from at "
           "be can if when have has gain gains use uses make makes than then not no".split())


def toks(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return {w for w in re.findall(r"[a-z]{3,}", s) if w not in STOP}


def main():
    base = json.load(open(f"{BASE}/index.json"))
    T = {}
    for f in os.listdir(f"{BASE}/text"):
        T.update(json.load(open(f"{BASE}/text/{f}")))

    def prosa(r):
        t = T.get(r.get("text") or "", "")
        return toks(re.sub(r"^\s*\S.{0,80}?Source .{0,60}?pg\.\s*\d+", "", t)[:900])

    lic = lambda r: (r.get("source") or {}).get("license")
    orc = [(r, prosa(r)) for r in base if lic(r) == "ORC"]
    orc = [(r, p) for r, p in orc if len(p) >= TOKENS_MIN]
    por_kind = collections.defaultdict(list)
    for r, p in orc:
        por_kind[r.get("kind")].append((r, p))

    pares, generico = [], 0
    for r in base:
        if lic(r) != "OGL":
            continue
        p = prosa(r)
        if len(p) < TOKENS_MIN:
            generico += 1
            continue
        melhor, score = None, 0.0
        for cand, pc in por_kind.get(r.get("kind"), []):
            i = len(p & pc)
            if not i:
                continue
            j = i / len(p | pc)
            if j > score:
                score, melhor = j, cand
        if score >= SCORE_MIN and melhor is not None and melhor["id"] != r["id"]:
            pares.append((r, melhor, score))

    # funde: o registro remaster absorve nome e xref do legado
    absorvidos = set()
    por_id = {r["id"]: r for r in base}
    for legado, remaster, score in pares:
        if legado["id"] in absorvidos:
            continue
        alvo = por_id[remaster["id"]]
        aliases = set(alvo.get("aliases") or [])
        aliases.add(legado.get("name"))
        aliases.update(legado.get("aliases") or [])
        aliases.discard(alvo.get("name"))
        alvo["aliases"] = sorted(a for a in aliases if a)
        alvo.setdefault("xref", {}).update(
            {f"legado_{k}": v for k, v in (legado.get("xref") or {}).items()})
        alvo.setdefault("historico", []).append(
            {"nome_legado": legado.get("name"),
             "livro_legado": (legado.get("source") or {}).get("book"),
             "similaridade": round(score, 3)})
        absorvidos.add(legado["id"])

    final = [r for r in base if r["id"] not in absorvidos]
    json.dump(final, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    com_alias = sum(1 for r in final if r.get("aliases"))
    print(f"base: {len(base)} -> {len(final)} registros")
    print(f"pares fundidos: {len(absorvidos)}")
    print(f"registros com alias: {com_alias}")
    print(f"pulados por prosa curta/generica: {generico}")

    linhas = ["# Fusao de renomeados", "",
              "Politica: nome nao importa, regra e conteudo importam. Par confirmado vira",
              "um registro so; todos os nomes ficam em `aliases`. **Nada e descartado.**", "",
              f"- base: {len(base)} -> **{len(final)}** registros",
              f"- pares fundidos: **{len(absorvidos)}**",
              f"- registros com alias: **{com_alias}**",
              f"- pulados por prosa curta demais para julgar: {generico}",
              f"- criterio: similaridade >= {SCORE_MIN} **e** >= {TOKENS_MIN} termos distintivos",
              "", "## Fusoes", ""]
    for legado, remaster, score in sorted(pares, key=lambda x: -x[2]):
        if legado["id"] in absorvidos:
            linhas.append(f"- `{score:.2f}` **{legado.get('name')}** "
                          f"-> **{remaster.get('name')}** _({legado.get('kind')})_")
    open(f"{BASE}/relatorio_fusao.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_fusao.md")


if __name__ == "__main__":
    main()
