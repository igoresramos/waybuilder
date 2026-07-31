#!/usr/bin/env python3
"""
`Field Discovery (Bomber)` nao e escolha: o campo de pesquisa ja decidiu.

Sobraram 68 opcoes de balaio cujo nome termina num parentese que casa EXATAMENTE
o nome de uma opcao de subclasse da propria classe -- as quatro
`Field Discovery (X)` do Alquimista, os dez `Initiate Benefit (X)` do
Taumaturgo. Hoje o app oferece as quatro lado a lado e um Bomber pode escolher a
do Chirurgeon.

POR QUE GATE E NAO REMOCAO: nenhuma das 68 e concedida pelo dono
(`wb:class-feature/bomber` tem `grants: []`), entao tira-las do balaio as
tornaria INALCANCAVEIS -- familia do item 97, oposto do principio zero. O termo
`subclass` ja roda em 281 registros desde a spec do Inventor, e faz o certo:
a opcao FICA na lista, marcada, com o motivo escrito.

Spec: specs/2026-07-31-variante-por-subclasse.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_variante_por_subclasse.md
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

SUFIXO = re.compile(r"\(([^)]+)\)\s*$")


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por_id = {r["id"]: r for r in base}

    tocados, pulados = [], []
    for classe in base:
        if classe.get("kind") != "class":
            continue
        slug = classe["id"].rsplit("/", 1)[-1]
        # nome da opcao -> ids que o carregam. Lista, e nao id unico, porque a
        # guarda de DONO UNICO depende de saber quando ha mais de um.
        donos = collections.defaultdict(list)
        for bloco in (classe.get("subclasses") or []):
            if bloco.get("eixo") == "outras-opcoes":
                continue
            for o in (bloco.get("opcoes") or []):
                nome = (por_id.get(o) or {}).get("name")
                if nome:
                    donos[nome.lower()].append(o)

        for bloco in (classe.get("subclasses") or []):
            if bloco.get("eixo") != "outras-opcoes":
                continue
            for o in (bloco.get("opcoes") or []):
                reg = por_id.get(o)
                if reg is None:
                    continue
                m = SUFIXO.search(reg.get("name") or "")
                if not m:
                    continue
                # casamento EXATO, sem normalizacao esperta: `(Level 13)` nao e
                # subclasse, `(Sorcerer)` nao e opcao de subclasse do Feiticeiro
                achados = donos.get(m.group(1).lower()) or []
                if not achados:
                    continue
                if len(set(achados)) > 1:
                    # licao do `initial-modification` do Inventor: com mais de
                    # um dono, gatear num deles faz a opcao sumir para quem
                    # escolheu outro
                    pulados.append((classe["id"], reg["id"], "mais de um dono"))
                    continue
                termo = {"subclass": {slug: achados[0]}}
                atual = reg.get("requires")
                if atual:
                    # nunca substitui o que ja existia
                    reg["requires"] = {"and": [atual, termo]}
                else:
                    reg["requires"] = termo
                reg.setdefault("prov", {})["requires"] = "derivado:sufixo-de-subclasse"
                tocados.append((classe.get("name"), reg.get("name"), achados[0]))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    por_classe = collections.Counter(c for c, _, _ in tocados)
    rel = ["# Variante por subclasse", "",
           f"- opcoes de balaio gateadas: **{len(tocados)}**",
           f"- puladas pela guarda de dono unico: **{len(pulados)}**", "",
           "O nome termina num parentese que casa EXATAMENTE o nome de uma "
           "opcao de subclasse da propria classe, entao nao ha o que escolher: "
           "um Alquimista Bomber recebe `Field Discovery (Bomber)` e as outras "
           "tres nao sao opcao dele.", "",
           "GATE e nao remocao: nenhuma das 68 e concedida pelo dono "
           "(`wb:class-feature/bomber` tem `grants: []`), e tira-las do balaio "
           "as tornaria INALCANCAVEIS. Elas ficam na lista, MARCADAS.", "",
           "| classe | gateadas |", "|---|---:|"]
    for c, q in por_classe.most_common():
        rel.append(f"| {c} | {q} |")
    rel += ["", "| classe | opcao | exige a subclasse |", "|---|---|---|"]
    for c, nome, dono in tocados:
        rel.append(f"| {c} | {nome} | `{dono}` |")
    if pulados:
        rel += ["", "### Pulados", "", "| classe | opcao | motivo |", "|---|---|---|"]
        for cid, rid, motivo in pulados:
            rel.append(f"| `{cid}` | `{rid}` | {motivo} |")
    with open(f"{BASE}/relatorio_variante_por_subclasse.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"variante por subclasse: {len(tocados)} gateadas, {len(pulados)} puladas")
    print(f"-> {BASE}/relatorio_variante_por_subclasse.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
