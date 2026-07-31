#!/usr/bin/env python3
"""
`grandeur cause` era prosa em `requires_residuo`. Vira requisito de verdade.

Achado na 5a rodada de comparacao com o Pathbuilder, com as cinco classes que
faltavam. No Campeao 1, CINCO feats em que nos dizemos que atende e ele diz que
nao -- e ele acerta:

    Brilliant Flash        res=['grandeur cause']
    Iron Repercussions     res=['obedience cause']
    Nimble Reprisal        res=['justice cause']
    Ongoing Selfishness    res=['desecration cause']
    Vicious Vengeance      res=['iniquity cause']

O `requires` deles so tinha `class_level >= 1`, entao a exigencia de CAUSA nao
existia para o motor: um Campeao de qualquer causa recebia os cinco.

A forma e sempre `<nome da opcao> <nome do eixo>`. Medido na base inteira: 26
clausulas em 26 registros, em sete eixos (cause, muse, hybrid-study,
subconscious-mind, racket, mystery, research-field).

POR QUE AQUI E NAO NO PARSER: o parser de `feats.py` roda na EXTRACAO, e os
eixos so existem depois de `aplicar_subclasses.py`. Na hora em que a clausula e
lida nao ha com o que casar.

Spec: specs/2026-07-30-requisito-de-subescolha.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_requisito_subescolha.md
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

# `outras-opcoes` nao e eixo de verdade (item 69) e `deity` tem 488 nomes, que
# casariam por acidente.
EIXOS_FORA = {"outras-opcoes", "deity"}


def limpar(s) -> str:
    return " ".join(str(s or "").split()).strip().rstrip(".").lower()


def sem_parenteses(s) -> str:
    return re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por_id = {r["id"]: r for r in base}

    # mapa `<opcao> <eixo>` -> {(classe, id)}
    mapa = collections.defaultdict(set)
    for reg in base:
        if reg.get("kind") != "class":
            continue
        classe = reg["id"].rsplit("/", 1)[-1]
        for bloco in (reg.get("subclasses") or []):
            eixo = str(bloco.get("eixo") or "")
            if eixo in EIXOS_FORA:
                continue
            termo = eixo.replace("-", " ")
            for oid in (bloco.get("opcoes") or []):
                nome = sem_parenteses(limpar((por_id.get(oid) or {}).get("name")))
                if nome:
                    mapa[f"{nome} {termo}"].add((classe, oid))

    # chave que aponta para mais de uma classe e DESCARTADA: mapear para a
    # errada e pior que deixar em prosa. Sao as tres do eixo `sanctification`,
    # cujas opcoes sao os mesmos ids no Clerigo e no Campeao.
    ambiguas = {k for k, v in mapa.items() if len(v) > 1}
    resolvido = {k: next(iter(v)) for k, v in mapa.items() if len(v) == 1}

    aplicados, por_eixo = [], collections.Counter()
    for reg in base:
        residuo = reg.get("requires_residuo") or []
        if not residuo:
            continue
        sobra, novos = [], []
        for clausula in residuo:
            alvo = resolvido.get(limpar(clausula)) if isinstance(clausula, str) else None
            if alvo is None:
                sobra.append(clausula)
                continue
            classe, oid = alvo
            novos.append({"subclass": {classe: oid}})
            por_eixo[oid.rsplit("/", 1)[-1]] += 1
            aplicados.append((reg["id"], clausula, classe, oid))
        if not novos:
            continue
        atual = reg.get("requires")
        partes = ([atual] if atual not in (None, {}, []) else []) + novos
        reg["requires"] = partes[0] if len(partes) == 1 else {"all": partes}
        reg.setdefault("prov", {})["requires"] = \
            reg.get("prov", {}).get("requires") or "derivado:opcao-com-sufixo-de-eixo"
        if sobra:
            reg["requires_residuo"] = sobra
        else:
            reg.pop("requires_residuo", None)

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Requisito de sub-escolha lido do residuo", "",
           f"- clausulas convertidas: **{len(aplicados)}**",
           f"- chaves possiveis (opcao x eixo): **{len(mapa)}**",
           f"- descartadas por ambiguidade: **{len(ambiguas)}** "
           f"({', '.join(sorted(ambiguas)) or '-'})", "",
           "Achado na 5a rodada com o Pathbuilder: cinco feats do Campeao que "
           "nos liberavamos e ele barrava, todos por causa (`grandeur cause` e "
           "companhia) presa em `requires_residuo`.", "",
           "| registro | clausula | vira |", "|---|---|---|"]
    for rid, c, classe, oid in sorted(aplicados):
        rel.append(f"| `{rid}` | {c} | `{classe}` -> `{oid}` |")
    with open(f"{BASE}/relatorio_requisito_subescolha.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"requisito de sub-escolha: {len(aplicados)} clausulas convertidas, "
          f"{len(ambiguas)} chaves ambiguas descartadas")
    print(f"-> {BASE}/relatorio_requisito_subescolha.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
