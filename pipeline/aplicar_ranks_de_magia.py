#!/usr/bin/env python3
"""
Le `heighten_level` do AoN e emite `ranks` nas magias.

O item 79(d) reclamava que "nao da para separar 'sem elevacao' de 'lacuna'":
`heightened` estruturado cobria 31% e o resto era chave vazia, que significava
as duas coisas ao mesmo tempo.

O AoN publica `heighten_level` nos 2.461 docs de magia -- a lista de ranks que a
magia ocupa. Cruzado com a base, a ambiguidade some: das 1.125 chaves vazias,
664 estao CERTAS (a magia nao eleva) e 461 sao lacuna de verdade.

`ranks` responde as duas perguntas sem inventar flag: um unico rank quer dizer
"so no proprio", mais de um quer dizer "eleva". Lista vazia seria ambigua de
novo, entao nunca se emite vazia.

O QUE MUDA a cada degrau (`heightened`) continua como esta: o AoN publica os
degraus (`heighten`: ["+2"], ["3rd","5th"]) e NAO publica o efeito de cada um --
o `efeito` dos nossos 511 vem do Foundry. Preencher com degrau sem efeito
trocaria lacuna honesta por campo meio-cheio.

Spec: specs/2026-07-30-ranks-de-elevacao.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_ranks_de_magia.md
"""
import collections
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"


def ranks_do_aon() -> dict:
    saida = {}
    for caminho in glob.glob(f"{BRUTOS}/aon*.json") + glob.glob(f"{BRUTOS}/aon_dump/*.json"):
        try:
            with open(caminho, encoding="utf-8") as fh:
                dados = json.load(fh)
        except Exception:
            continue
        docs = dados if isinstance(dados, list) else dados.get("docs") or []
        for doc in docs:
            if not isinstance(doc, dict) or doc.get("category") != "spell":
                continue
            hl = doc.get("heighten_level")
            if not isinstance(hl, list) or not hl:
                continue
            ranks = sorted({int(x) for x in hl if isinstance(x, int)})
            if ranks:
                saida[doc.get("id")] = ranks
    return saida


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    tabela = ranks_do_aon()
    c = collections.Counter()
    divergentes = []
    for reg in base:
        if reg.get("kind") != "spell":
            continue
        ranks = tabela.get((reg.get("xref") or {}).get("aon"))
        if not ranks:
            c["sem par no AoN"] += 1
            continue
        reg["ranks"] = ranks
        reg.setdefault("prov", {})["ranks"] = "aon"
        eleva = len(ranks) > 1
        tem = bool(reg.get("heightened"))
        if eleva and tem:
            c["eleva, com efeito estruturado"] += 1
        elif eleva:
            c["eleva, SEM efeito estruturado (lacuna)"] += 1
        elif tem:
            c["AoN diz que nao eleva, mas temos estrutura"] += 1
            divergentes.append(reg["id"])
        else:
            c["nao eleva -- ausencia CORRETA"] += 1

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Ranks de elevacao, lidos de `heighten_level` do AoN", "",
           "A chave `heightened` vazia significava duas coisas -- 'nao eleva' e "
           "'nao sei' --, e por isso nao informava nada. Com `ranks`, um unico "
           "rank quer dizer 'so no proprio' e mais de um quer dizer 'eleva'.",
           "", "| situacao | magias |", "|---|---:|"]
    for k, v in c.most_common():
        rel.append(f"| {k} | {v} |")
    if divergentes:
        rel += ["", "## Divergentes -- temos estrutura e o AoN diz que nao eleva",
                "", "Possivel par legacy/remaster mal casado. O dado NAO e "
                "apagado: apagar estrutura por divergencia de uma fonte seria "
                "pior que a divergencia.", ""]
        rel += [f"- `{i}`" for i in sorted(divergentes)]
    with open(f"{BASE}/relatorio_ranks_de_magia.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"ranks de magia: {sum(v for k, v in c.items() if k != 'sem par no AoN')} "
          f"magias com `ranks`, {c['eleva, SEM efeito estruturado (lacuna)']} "
          f"lacunas identificadas")
    print(f"-> {BASE}/relatorio_ranks_de_magia.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
