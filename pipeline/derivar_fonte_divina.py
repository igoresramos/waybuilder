#!/usr/bin/env python3
"""
Abre o eixo `divine-font` do Clerigo -- o par da santificacao.

A spec `divindade-na-ficha` fechou o eixo de divindade e declarou o limite: para
as 137 divindades que permitem heal E harm, o motor nao sabia qual o jogador
pegou e por isso nao reprovava nenhuma das duas. O desenho que faltava chegou
com `santificacao-escolhida`, e o Foundry declara este eixo do mesmo jeito --
`Divine Font` tem um `ChoiceSet` com duas opcoes, cada uma condicionada a
`deity:primary:font:*`.

DOIS TERMOS, e nao um: `deity_font_permitido` (a DIVINDADE permite?) no
`requires` das opcoes, e `deity_font` (a fonte do PERSONAGEM e esta?) nas 13
clausulas de feat. Usar o mesmo nos dois lugares seria circular -- a opcao
`heal` exigiria que a fonte ja fosse `heal`.

So o Clerigo cita `wb:class-feature/divine-font`; o Campeao escolhe
santificacao, nao fonte.

Spec: specs/2026-07-30-fonte-divina-escolhida.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_fonte_divina.md
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

MARCA = "wb:class-feature/divine-font"
OPCOES = [("heal", "Fonte de cura"), ("harm", "Fonte de dano")]


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    existentes = {r["id"] for r in base}
    criados = []
    for chave, nome in OPCOES:
        rid = f"wb:divine-font/{chave}"
        if rid in existentes:
            continue
        base.append({
            "id": rid, "kind": "divine-font", "name": nome,
            "level": None, "traits": [], "rarity": "common",
            "source": {"book": "Player Core", "page": None,
                       "license": "ORC", "remaster": True},
            "requires": {"deity_font_permitido": chave},
            "grants": [],
            "mechanized": False,
            # quantos usos por dia e o slot extra sao mecanica de RECURSO, nao
            # de construcao -- fora do escopo, como a spec declara
            "grants_completos": None,
            "requires_parseado": True,
            "text": None,
            "xref": {},
            "prov": {"name": "waybuilder", "traits": "waybuilder",
                     "rarity": "waybuilder", "source": "waybuilder",
                     "requires": "waybuilder"},
        })
        criados.append(rid)

    opcoes = [f"wb:divine-font/{c}" for c, _ in OPCOES]
    tocadas = []
    for reg in base:
        if reg.get("kind") != "class" or MARCA not in json.dumps(reg):
            continue
        blocos = reg.setdefault("subclasses", [])
        if any(b.get("eixo") == "divine-font" for b in blocos):
            continue
        blocos.append({
            "eixo": "divine-font", "nivel": 1, "slot": "subclasse",
            "escolhe": 1, "opcoes": opcoes,
            "com_mecanica": opcoes, "so_catalogo": [],
        })
        tocadas.append(reg["id"])

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    quantas = collections.Counter()
    for r in base:
        if r.get("kind") == "deity":
            quantas[len(r.get("divine_font") or [])] += 1

    rel = ["# Fonte divina", "",
           f"- registros de opcao criados: **{len(criados)}**",
           f"- classes com o eixo: **{len(tocadas)}** ({', '.join(tocadas) or '-'})",
           "",
           "O eixo so existe para quem cita `class-feature/divine-font`, e so o "
           "Clerigo cita. O Campeao escolhe santificacao, nao fonte.", "",
           "| fontes que a divindade permite | divindades |", "|---|---:|"]
    for k, v in sorted(quantas.items()):
        rel.append(f"| {k} | {v} |")
    rel += ["", "As de DUAS eram exatamente as que o motor nao conseguia "
            "responder antes deste eixo."]
    with open(f"{BASE}/relatorio_fonte_divina.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"fonte divina: {len(criados)} opcoes, {len(tocadas)} classe(s); "
          f"divindades por n de fontes {dict(sorted(quantas.items()))}")
    print(f"-> {BASE}/relatorio_fonte_divina.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
