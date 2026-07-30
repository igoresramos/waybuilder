#!/usr/bin/env python3
"""
Leva `tradition` do catalogo do AoN para a class-feature que o jogador ESCOLHE.

O Feiticeiro, a Bruxa e o Invocador nao tem tradicao fixa: quem a define e a
subclasse. O AoN publica isso como campo estruturado (`tradition: ["Occult"]`) e
`aon_kinds.py` ja o emite -- mas no registro do kind dedicado
(`wb:bloodline/genie`), que **nao e o registro que o jogador pega**.

A opcao viva no eixo de subclasse e a class-feature:

    wb:class/sorcerer -> subclasses[].opcoes = ["wb:class-feature/bloodline-genie", ...]

e ela nao tem como chegar na tradicao sozinha: sai com `xref.aon: None`, e o
dump `aon_class_features.json` (1.254 registros) nao tem o campo em nenhum.
Sao dois catalogos paralelos que nunca se falaram -- a mesma causa raiz que
`colapsar_opcoes_irmas.py` (passo 7d) trata para a duplicidade de identidade.

O CASAMENTO E POR NOME, MAS COM TRAVA PELA CLASSE DONA. Nao e enfeite:
`psychopomp` existe como bloodline E como eidolon, e sem a trava
`wb:eidolon/psychopomp` casaria com a class-feature do Feiticeiro. Medido:
48 pares, 0 ambiguos, 0 sem par.

Este passo NAO apaga o lado de origem -- os dois passam a responder a mesma
coisa, e o registro do kind dedicado segue buscavel.

ORDEM: depois de `colapsar_opcoes_irmas.py` (7d), que e quem decide qual dos
dois irmaos e a opcao viva.

Spec: specs/2026-07-30-tradicao-por-subclasse.md
Entrada: pipeline/base/index.json
Saida:   index.json enriquecido + base/relatorio_tradicao_de_subclasse.md
"""
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

# eixo -> classe dona. A trava que impede `psychopomp` de casar no lugar errado.
DONO = {"bloodline": "Sorcerer", "patron": "Witch", "eidolon": "Summoner"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).lower()
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    levados, sem_tradicao, sem_par, ambiguos = [], [], [], []
    for kind, classe in DONO.items():
        irmas = [r for r in base
                 if r.get("kind") == "class-feature" and classe in (r.get("class") or [])]
        for r in [x for x in base if x.get("kind") == kind]:
            n = norm(r.get("name"))
            # as tres formas que a fonte usa para o mesmo conceito:
            # `Baba Yaga`, `Bloodline: Genie`, `Angel Eidolon`
            alvos = [c for c in irmas
                     if norm(c.get("name")) in (n, f"{n} {kind}", f"{kind} {n}")]
            if len(alvos) > 1:
                ambiguos.append((r["id"], [a["id"] for a in alvos]))
                continue
            if not alvos:
                sem_par.append(r["id"])
                continue
            trad = r.get("tradition")
            if not trad:
                # ausencia REAL na fonte, nao falha de casamento: o Draconic
                # remaster declara tradicao variavel, que depende do exemplar.
                sem_tradicao.append((r["id"], alvos[0]["id"]))
                continue
            alvo = alvos[0]
            alvo["tradition"] = trad
            alvo.setdefault("prov", {})["tradition"] = f"aon~inferido:nome-aproximado"
            levados.append((r["id"], alvo["id"], trad))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = [
        "# Tradicao de conjuracao levada para a opcao viva", "",
        f"- pares com tradicao levada: **{len(levados)}**",
        f"- pares sem tradicao na fonte: **{len(sem_tradicao)}**",
        f"- sem par: **{len(sem_par)}** | ambiguos: **{len(ambiguos)}**", "",
        "Ambiguo ou sem par e defeito DESTE passo. Sem tradicao na fonte nao e:",
        "a fonte declara variavel e o motor avisa em vez de arbitrar.", "",
        "## Levadas", "", "| origem | opcao viva | tradicao |", "|---|---|---|",
    ]
    for a, b, t in sorted(levados):
        rel.append(f"| {a} | {b} | {t} |")
    rel += ["", "## Sem tradicao na fonte", "", "| origem | opcao viva |", "|---|---|"]
    for a, b in sorted(sem_tradicao):
        rel.append(f"| {a} | {b} |")
    if sem_par or ambiguos:
        rel += ["", "## DEFEITO deste passo", ""]
        for x in sem_par:
            rel.append(f"- sem par: {x}")
        for a, b in ambiguos:
            rel.append(f"- ambiguo: {a} -> {b}")
    with open(f"{BASE}/relatorio_tradicao_de_subclasse.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"tradicao levada para a opcao viva: {len(levados)} pares "
          f"({len(sem_tradicao)} sem tradicao na fonte)")
    if sem_par or ambiguos:
        print(f"  ! {len(sem_par)} sem par, {len(ambiguos)} ambiguos", file=sys.stderr)
    print(f"-> {BASE}/relatorio_tradicao_de_subclasse.md")
    return 1 if (sem_par or ambiguos) else 0


if __name__ == "__main__":
    sys.exit(main())
