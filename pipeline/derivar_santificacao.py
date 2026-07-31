#!/usr/bin/env python3
"""
Le o MODAL da santificacao e abre o eixo -- a primeira sub-escolha filtrada.

O item 99 achou que os class-features do Foundry declaram os eixos em regras
`ChoiceSet`. `Deity (Champion)`, `Deity (Cleric)` e `Vindicator` trazem o mesmo:
tres opcoes (`holy`, `unholy`, `none`), cada uma condicionada a DIVINDADE
escolhida. Era exatamente o que a spec `divindade-na-ficha` declarou faltar.

A ARMADILHA, e ela e a razao deste passo existir: a base guarda `sanctification`
como lista achatada (`["holy"]`), e inferir dela "uma opcao so = obrigatoria"
estaria errado em 408 divindades. A prosa do AoN traz o modal e o extrator o
descarta:

    can choose holy               265        must choose unholy     87
    can choose unholy             143        must choose holy       23
    none                          112        (nao casou)            14
    can choose holy or unholy      73

Cayden Cailean tem `["holy"]` e a prosa diz "can choose holy" -- ele NAO obriga.
So 110 divindades obrigam.

Emite `sanctification_escolha` (`can` / `must` / null) e os tres registros de
opcao, cada um com o seu `requires`. Filtrar aqui e MARCAR, nunca esconder:
`candidatos()` ja avalia o `requires` de cada opcao e devolve `atende: false`.

Spec: specs/2026-07-30-santificacao-escolhida.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_santificacao.md
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

FRASE = re.compile(r"Divine Sanctification\s+(.{0,40}?)\s+Divine Skill", re.S)
MARCA_DEIDADE = "wb:class-feature/deity-"

OPCOES = [
    ("holy", "Holy", {"deity_sanctification": "holy"}),
    ("unholy", "Unholy", {"deity_sanctification": "unholy"}),
    # `none` cabe quando a divindade NAO OBRIGA -- e literalmente o predicado do
    # Foundry: `nor must:holy, must:unholy`.
    ("none", "Sem santificacao", {"deity_sanctification": "none"}),
]


def modal_de(texto: str):
    """`can`, `must` ou None, lido da prosa do AoN."""
    m = FRASE.search(str(texto or ""))
    if not m:
        return None
    frase = " ".join(m.group(1).split()).lower()
    if frase.startswith("must choose"):
        return "must"
    if frase.startswith("can choose"):
        return "can"
    return None          # "none" -- a divindade nao tem santificacao nenhuma


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    caminho = f"{BRUTOS}/aon_dump/deity.json"
    if not os.path.exists(caminho):
        print(f"!! sem dump de divindade em {caminho}", file=sys.stderr)
        return 1
    prosa = {}
    for d in json.load(open(caminho, encoding="utf-8")):
        if isinstance(d, dict) and d.get("id"):
            prosa[str(d["id"])] = str(d.get("text") or "")

    contagem = collections.Counter()
    for reg in base:
        if reg.get("kind") != "deity":
            continue
        modal = modal_de(prosa.get(str((reg.get("xref") or {}).get("aon"))))
        contagem[modal] += 1
        if modal:
            reg["sanctification_escolha"] = modal
            reg.setdefault("prov", {})["sanctification_escolha"] = \
                "aon~inferido:prosa"

    # os tres registros de opcao. Nao existem no AoN nem no Foundry como
    # documento: sao o eixo em si, e por isso a licenca e a fonte sao nossas.
    existentes = {r["id"] for r in base}
    criados = []
    for chave, nome, requires in OPCOES:
        rid = f"wb:sanctification/{chave}"
        if rid in existentes:
            continue
        base.append({
            "id": rid, "kind": "sanctification", "name": nome,
            "level": None, "traits": [] if chave == "none" else [chave],
            "rarity": "common",
            "source": {"book": "Player Core", "page": None,
                       "license": "ORC", "remaster": True},
            "requires": requires,
            "grants": [],
            "mechanized": False,
            # o efeito mecanico de ser holy/unholy e mecanica CONDICIONAL, a
            # familia ja recusada com numero tres vezes
            "grants_completos": None,
            "requires_parseado": True,
            "text": None,
            "xref": {},
            "prov": {"name": "waybuilder", "traits": "waybuilder",
                     "rarity": "waybuilder", "source": "waybuilder",
                     "requires": "waybuilder"},
        })
        criados.append(rid)

    opcoes = [f"wb:sanctification/{c}" for c, _, _ in OPCOES]
    tocadas = []
    for reg in base:
        if reg.get("kind") != "class" or MARCA_DEIDADE not in json.dumps(reg):
            continue
        blocos = reg.setdefault("subclasses", [])
        if any(b.get("eixo") == "sanctification" for b in blocos):
            continue
        blocos.append({
            "eixo": "sanctification", "nivel": 1, "slot": "subclasse",
            "escolhe": 1, "opcoes": opcoes,
            "com_mecanica": opcoes, "so_catalogo": [],
        })
        tocadas.append(reg["id"])

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Santificacao", "",
           f"- registros de opcao criados: **{len(criados)}**",
           f"- classes com o eixo: **{len(tocadas)}** ({', '.join(tocadas) or '-'})",
           "", "## Modal lido da prosa do AoN", "",
           "Inferir da lista achatada (`[\"holy\"]` = obriga) estaria errado em "
           "**408** divindades: `can choose holy` sozinho sao 265.", "",
           "| modal | divindades |", "|---|---:|"]
    for k, v in contagem.most_common():
        rel.append(f"| {k or '(sem santificacao)'} | {v} |")
    with open(f"{BASE}/relatorio_santificacao.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"santificacao: {len(criados)} opcoes, {len(tocadas)} classes, "
          f"modal {dict(contagem)}")
    print(f"-> {BASE}/relatorio_santificacao.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
