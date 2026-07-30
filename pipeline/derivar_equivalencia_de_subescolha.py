#!/usr/bin/env python3
"""
Liga a sub-escolha que existe com DOIS ids: `<X>` e `<X> <eixo>`.

Um Barbaro que escolhe `Animal` no eixo `instinct` nao podia pegar nenhum dos 25
feats que exigem instinto, porque os `requires` citam
`wb:class-feature/animal-instinct` (vindo do Foundry) e a tela oferece
`wb:instinct/animal` (vindo do AoN). Os xrefs sao disjuntos e os nomes diferem
pelo sufixo do eixo, entao nao ha chave comum nem casamento por nome.

`colapsar_opcoes_irmas.py` nao alcanca o caso: ele casa por nome IGUAL e olha
uma opcao contra as outras do MESMO eixo. Aqui os nomes diferem e os gemeos
vivem em eixos diferentes (`instinct` e `outras-opcoes`).

DECLARA A EQUIVALENCIA em vez de reformar os eixos: mover a opcao vencedora de
um eixo para outro e mais risco do que o defeito pede.

Medido: 9 pares, todos no eixo `instinct` do Barbaro. A regra nao transborda
para nenhuma outra classe.

Spec: specs/2026-07-30-instinto-com-dois-ids.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_equivalencia_subescolha.md
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"


def chave(nome) -> str:
    return " ".join(str(nome or "").split()).casefold()


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    reg = {r["id"]: r for r in base}

    pares = []
    for r in base:
        if r.get("kind") != "class":
            continue
        # todas as opcoes da classe, de todos os eixos, com o eixo de origem
        opcoes = []
        for bloco in (r.get("subclasses") or []):
            for o in (bloco.get("opcoes") or []):
                if isinstance(o, str) and o in reg:
                    opcoes.append((o, str(bloco.get("eixo") or "")))
        por_nome = {}
        for o, _eixo in opcoes:
            por_nome.setdefault(chave(reg[o].get("name")), o)

        for o, eixo in opcoes:
            nome = chave(reg[o].get("name"))
            alvo = f"{nome} {eixo.replace('-', ' ')}".strip()
            gemeo = por_nome.get(alvo)
            if not gemeo or gemeo == o:
                continue
            for a, b in ((o, gemeo), (gemeo, o)):
                if reg[a].get("equivale_a") != b:
                    reg[a]["equivale_a"] = b
                    reg[a].setdefault("prov", {})["equivale_a"] = \
                        "derivado:nome-com-sufixo-do-eixo"
            pares.append((r.get("name"), eixo, o, gemeo))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Sub-escolha com dois ids", "",
           f"- pares ligados: **{len(pares)}**", "",
           "O mesmo instinto entra pelo AoN (`wb:instinct/animal`, nome "
           "\"Animal\") e pelo Foundry (`wb:class-feature/animal-instinct`, nome "
           "\"Animal Instinct\"). Os `requires` citam o segundo e a tela oferece "
           "o primeiro.", "",
           "| classe | eixo | opcao | gemeo |", "|---|---|---|---|"]
    for c, e, a, b in sorted(pares):
        rel.append(f"| {c} | {e} | `{a}` | `{b}` |")
    with open(f"{BASE}/relatorio_equivalencia_subescolha.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"equivalencia de sub-escolha: {len(pares)} pares ligados")
    print(f"-> {BASE}/relatorio_equivalencia_subescolha.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
