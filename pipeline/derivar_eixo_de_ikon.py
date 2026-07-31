#!/usr/bin/env python3
"""
Abre o eixo `ikon` do Exemplar, e liga cada ikon ao gemeo class-feature.

O item 97 falava em "48 class-features inalcancaveis". Re-medido: os kinds
`ikon` (21) e `mythic-calling` (15) sao INTEIROS inalcancaveis, com par ou sem.
Fundir os pares nao resolveria -- tiraria a duplicidade e os dois lados
continuariam sem ser citados.

A causa esta na classe: o Exemplar concede `divine-spark-and-ikons` no nivel 1 e
a prosa oficial diz "Select three ikons", mas a classe nao tem eixo de ikon. Nao
ha lacuna de conteudo -- o AoN publica 21 ikons e a base tem os 21.

DUAS COISAS AQUI, e a segunda e a mesma licao do instinto do Barbaro:

  1. o eixo, com `escolhe: 3` -- o primeiro bloco da base que nao e `escolhe: 1`;
  2. `equivale_a` entre `wb:ikon/<slug>` e `wb:class-feature/<slug>`, porque o
     compendio `pf2e.classfeatures` do Foundry mistura ikon com class-feature de
     verdade e o mesmo conceito acabou com dois ids.

Spec: specs/2026-07-30-escolha-multipla-e-ikons.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_eixo_de_ikon.md
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

# a prosa de `divine-spark-and-ikons` e literal: "Select three ikons". A
# progressao do Exemplar nao tem outra linha de ikon, e o quarto vem de
# `wb:feat/additional-ikon`, que e slot aberto POR FEAT e nao entra aqui.
QUANTOS = 3
MARCA = "wb:class-feature/divine-spark-and-ikons"


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por_id = {r["id"]: r for r in base}

    ikons = sorted(r["id"] for r in base if r.get("kind") == "ikon")
    if not ikons:
        print("!! nenhum ikon na base -- nada a fazer", file=sys.stderr)
        return 1

    # 1) equivalencia com o gemeo class-feature de mesmo slug
    pares = []
    for iid in ikons:
        gemeo = "wb:class-feature/" + iid.rsplit("/", 1)[-1]
        if gemeo not in por_id:
            continue
        for a, b in ((iid, gemeo), (gemeo, iid)):
            if por_id[a].get("equivale_a") != b:
                por_id[a]["equivale_a"] = b
                por_id[a].setdefault("prov", {})["equivale_a"] = \
                    "derivado:ikon-com-gemeo-class-feature"
        pares.append((iid, gemeo))

    # 2) o eixo, na classe que concede a feature de ikon -- derivado, nao a mao
    tocadas = []
    for reg in base:
        if reg.get("kind") != "class" or MARCA not in json.dumps(reg):
            continue
        blocos = reg.setdefault("subclasses", [])
        if any(b.get("eixo") == "ikon" for b in blocos):
            continue
        blocos.append({
            "eixo": "ikon",
            "nivel": 1,
            "slot": "subclasse",
            "escolhe": QUANTOS,
            "opcoes": ikons,
            # `grants` esta vazio nos 21, dos dois lados do par: o efeito de
            # immanence/transcendence e prosa. A escolha MUDA a ficha (ela
            # aparece em `features`), entao nao e catalogo.
            "com_mecanica": ikons,
            "so_catalogo": [],
        })
        tocadas.append(reg["id"])

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Eixo de ikon", "",
           f"- classes com o eixo: **{len(tocadas)}** ({', '.join(tocadas) or '-'})",
           f"- opcoes: **{len(ikons)}**, e o eixo escolhe **{QUANTOS}**",
           f"- pares `ikon` <-> `class-feature` ligados: **{len(pares)}**", "",
           "Primeiro bloco da base com `escolhe` diferente de 1. A prosa de "
           "`divine-spark-and-ikons` diz \"Select three ikons\"; o quarto vem de "
           "`wb:feat/additional-ikon`, que e slot por feat e nao entra aqui.", "",
           "| ikon | gemeo class-feature |", "|---|---|"]
    for a, b in pares:
        rel.append(f"| `{a}` | `{b}` |")
    with open(f"{BASE}/relatorio_eixo_de_ikon.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"eixo de ikon: {len(tocadas)} classe(s), {len(ikons)} opcoes, "
          f"escolhe {QUANTOS}; {len(pares)} pares ligados")
    print(f"-> {BASE}/relatorio_eixo_de_ikon.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
