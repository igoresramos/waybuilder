#!/usr/bin/env python3
"""
"expert in a skill with the Recall Knowledge action" sai do residuo e vira termo.

Tres feats ofereciam-se a quem nao podia pega-los, porque a clausula real ficou
em `requires_residuo` -- prosa nunca convertida -- e o `requires` guardava
apenas o gate de nivel:

    automatic-knowledge    expert  ...   requires: character_level >= 2
    dubious-knowledge      trained ...   requires: character_level >= 1
    masterful-obfuscation  master  ...   so o gate de nivel

Quem apontou foi o Pathbuilder, em 12 sondas de `skill_feat` rodadas em
paralelo -- a primeira vez que a bancada cobriu skill feat fora de
Fighter/Rogue. Os tres saiam DISPONIVEIS do nosso lado e recusados do dele, no
nivel certo.

A forma nao nomeia pericia: pergunta se EXISTE alguma com aquele rank. E o
mesmo desenho de `lore:*` (item 95) e `weapon:*`, e o motor ganhou
`skill:recall-knowledge` junto com este passo.

Spec: specs/2026-07-31-pericia-de-recall-knowledge.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_pericia_de_recall.md
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

# ancorada no COMECO da clausula: varredura por semelhanca traria "trained in
# Society" e companhia, que sao pericia NOMEADA e ja tem termo proprio
FORMA = re.compile(
    r"^(trained|expert|master|legendary)\s+in\s+a\s+skill\s+with\s+the\s+"
    r"recall\s+knowledge\s+action\b", re.I)


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    tocados = []
    for reg in base:
        residuo = reg.get("requires_residuo") or []
        if not residuo:
            continue
        fica, rank = [], None
        for clausula in residuo:
            m = FORMA.match(str(clausula).strip())
            if m and rank is None:
                rank = m.group(1).lower()
                continue
            fica.append(clausula)
        if rank is None:
            continue
        termo = {"proficiency": {"skill:recall-knowledge": {">=": rank}}}
        atual = reg.get("requires")
        # nunca substitui o que ja existia -- o gate de nivel continua valendo
        reg["requires"] = {"and": [atual, termo]} if atual else termo
        # residuo resolvido que fica no residuo MENTE sobre o tamanho do que
        # falta ler; sai daqui.
        if fica:
            reg["requires_residuo"] = fica
        else:
            reg.pop("requires_residuo", None)
        reg.setdefault("prov", {})["requires"] = "derivado:residuo-recall-knowledge"
        tocados.append((reg["id"], rank))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Pericia de Recall Knowledge", "",
           f"- clausulas convertidas em termo: **{len(tocados)}**", "",
           "A forma nao nomeia pericia -- pergunta se EXISTE alguma com aquele "
           "rank --, entao vira `skill:recall-knowledge`, mesmo desenho de "
           "`lore:*` e `weapon:*`. Sem isso os tres feats saiam DISPONIVEIS "
           "para quem nao podia pega-los, com o `requires` guardando so o gate "
           "de nivel.", "",
           "| registro | rank exigido |", "|---|---|"]
    for rid, rank in tocados:
        rel.append(f"| `{rid}` | {rank} |")
    with open(f"{BASE}/relatorio_pericia_de_recall.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"pericia de recall: {len(tocados)} clausula(s) convertida(s)")
    print(f"-> {BASE}/relatorio_pericia_de_recall.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
