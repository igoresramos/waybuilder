#!/usr/bin/env python3
"""
O impulso do Kineticist passa a exigir o elemento que o jogador abriu.

MAIOR DEFEITO UNICO DA BANCADA: 24 das 314 divergencias contra o Pathbuilder
eram impulsos -- `Aerial Boomerang`, `Burning Jet`, `Armor in Earth`,
`Flashforge` --, todos oferecidos por nos e recusados por ele, com ele certo. O
`requires` de um impulso dizia apenas `class_level: {kineticist: >= 1}`, e nada
exigia o elemento: um Kineticist de Ar e Fogo via os 116, inclusive os de
Madeira e Metal.

A REGRA, verbatim da fonte (dump do AoN, texto da classe):

    Composite: A composite impulse combines multiple elements. You can gain an
    impulse with the composite trait only if your kinetic elements include ALL
    the elements listed in the impulse's traits.

Entao e `all`, nao `any`. E a base concorda consigo mesma: os 16 impulsos de
dois elementos sao exatamente os 16 com trait `composite`.

Os 5 sem elemento nenhum (`Command Elemental`, `Counter Element`,
`Purify Element`, `Fearsome Familiar`, `Imperious Aura`) sao agnosticos por
desenho e ficam INTOCADOS.

O termo e `has` e nao `subclass`: o eixo `kinetic-gate` e `escolhe: 2`, e
`subclass` foi desenhado para eixo de escolha unica -- medido, ele responde
False ate para o gate escolhido.

Spec: specs/2026-07-31-gate-elemental-do-kineticist.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_gate_elemental.md
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

ELEMENTOS = ("air", "earth", "fire", "metal", "water", "wood")


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    ids = {r["id"] for r in base}

    # o gate tem de existir na base, senao o `has` aponta para o vazio e o
    # impulso fica insatisfazivel por construcao
    faltando = [e for e in ELEMENTOS
                if f"wb:class-feature/{e}-gate" not in ids]
    if faltando:
        print(f"!! gates ausentes na base: {faltando} -- passo pulado",
              file=sys.stderr)
        return 0

    tocados, agnosticos = [], []
    for reg in base:
        traits = reg.get("traits") or []
        if "impulse" not in traits:
            continue
        elems = [e for e in ELEMENTOS if e in traits]
        if not elems:
            # agnostico por desenho: qualquer Kineticist pega
            agnosticos.append(reg.get("name"))
            continue
        termos = [{"has": f"wb:class-feature/{e}-gate"} for e in elems]
        # "include ALL the elements listed" -- `all`, nunca `any`
        novo = termos[0] if len(termos) == 1 else {"all": termos}
        atual = reg.get("requires")
        # `all`, e nao `and`: o avaliador conhece `all`/`any`/`not`, e chave
        # desconhecida no topo do predicado passa em SILENCIO -- dois passos
        # meus viraram no-op assim em 31/07.
        reg["requires"] = {"all": [atual, novo]} if atual else novo
        reg.setdefault("prov", {})["requires"] = "derivado:gate-elemental"
        tocados.append((reg.get("name"), elems, "composite" in traits))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    por_elem = collections.Counter(e for _, es, _ in tocados for e in es)
    comp = sum(1 for _, _, c in tocados if c)
    rel = ["# Gate elemental do Kineticist", "",
           f"- impulsos gateados: **{len(tocados)}**",
           f"- deles, `composite` (exigem DOIS gates): **{comp}**",
           f"- agnosticos, intocados: **{len(agnosticos)}** "
           f"({', '.join(sorted(x for x in agnosticos if x))})", "",
           "Era o maior defeito unico da bancada: 24 das 314 divergencias "
           "contra o Pathbuilder eram impulsos que nos ofereciamos e ele "
           "recusava, com ele certo. O `requires` dizia so `class_level >= 1`.",
           "",
           "A regra e da fonte, verbatim: \"You can gain an impulse with the "
           "composite trait only if your kinetic elements include ALL the "
           "elements listed\" -- entao `all`, nunca `any`.", "",
           "| elemento | impulsos |", "|---|---:|"]
    for e, q in por_elem.most_common():
        rel.append(f"| {e} | {q} |")
    rel += ["", "| impulso | exige | composite |", "|---|---|---|"]
    for nome, elems, c in sorted(tocados):
        rel.append(f"| {nome} | {', '.join(elems)} | {'sim' if c else ''} |")
    with open(f"{BASE}/relatorio_gate_elemental.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"gate elemental: {len(tocados)} impulsos gateados "
          f"({comp} composite), {len(agnosticos)} agnosticos intocados")
    print(f"-> {BASE}/relatorio_gate_elemental.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
