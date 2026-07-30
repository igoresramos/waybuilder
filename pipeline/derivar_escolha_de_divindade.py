#!/usr/bin/env python3
"""
Abre o eixo `deity` nas classes que exigem uma divindade.

A base tem 488 divindades com `divine_font`, `domains`, `favored_weapon` e
`divine_attribute` estruturados, e ZERO consumidores -- `deity` nao aparecia uma
vez em `motor/motor.py`. O motivo e que a escolha nao existia: as duas classes
que a exigem chegam por rotas diferentes e nenhuma virava eixo.

  - Clerigo: `wb:class-feature/deity-cleric` dentro do balaio `outras-opcoes`
    de nivel 1 (o item 69);
  - Campeao: `wb:class-feature/deity-champion` em `progressao`, como feature
    concedida.

O eixo `doctrine` do Clerigo nao cobre -- ele so tem cloistered, warpriest e
battle-creed.

NAO INVENTA MAQUINARIA: `slots_de_subclasse` ja generaliza sobre qualquer
`eixo`, e a escolha ja e persistida em `escolhas[].slot == "subclasse"`. Um id
de divindade so aparece neste bloco, entao nenhuma escolha de outro eixo o
satisfaz por acidente.

Spec: specs/2026-07-30-divindade-na-ficha.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_escolha_de_divindade.md
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    divindades = sorted(r["id"] for r in base if r.get("kind") == "deity")
    if not divindades:
        print("!! nenhuma divindade na base -- nada a fazer", file=sys.stderr)
        return 1

    # a classe que EXIGE divindade e a que cita `class-feature/deity-<algo>`,
    # venha pela progressao ou pelo balaio. Derivado, nao lista a mao.
    marcas = {r["id"] for r in base if r.get("kind") == "class-feature"
              and r["id"].rsplit("/", 1)[-1].startswith("deity")}

    tocadas = []
    for reg in base:
        if reg.get("kind") != "class":
            continue
        blob = json.dumps(reg)
        if not any(m in blob for m in marcas):
            continue
        blocos = reg.setdefault("subclasses", [])
        if any(b.get("eixo") == "deity" for b in blocos):
            continue
        blocos.append({
            "eixo": "deity",
            "nivel": 1,
            "slot": "subclasse",
            "escolhe": 1,
            "opcoes": divindades,
            # nenhuma divindade concede mecanica por `grants`: o que ela muda na
            # ficha (fonte, dominio, arma favorita) e lido por termo proprio, e
            # nao por concessao. Declarar o catalogo inteiro como `so_catalogo`
            # seria mentir na direcao oposta -- a escolha MUDA numero.
            "com_mecanica": divindades,
            "so_catalogo": [],
        })
        reg.setdefault("prov", {})["subclasses"] = \
            reg.get("prov", {}).get("subclasses") or "derivado:exige-divindade"
        tocadas.append(reg["id"])

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Eixo de divindade", "",
           f"- classes com o eixo: **{len(tocadas)}** ({', '.join(sorted(tocadas))})",
           f"- opcoes por eixo: **{len(divindades)}**", "",
           "A classe que exige divindade e derivada de quem cita "
           "`class-feature/deity-*`, e nao de lista a mao. Hoje sao Clerigo "
           "(pelo balaio `outras-opcoes`) e Campeao (pela `progressao`).", "",
           "## O que a escolha destrava", "",
           "38 clausulas de `requires_residuo` dependiam so dela: 11 de "
           "divindade nomeada, 13 de fonte, 5 de seguir divindade, 3 de "
           "dominio e 6 de arma favorita / pericia divina / santificacao."]
    with open(f"{BASE}/relatorio_escolha_de_divindade.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"eixo de divindade: {len(tocadas)} classes, {len(divindades)} opcoes")
    print(f"-> {BASE}/relatorio_escolha_de_divindade.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
