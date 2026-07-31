#!/usr/bin/env python3
"""
`otherTags` entra na base, e com ela nascem os eixos do Kineticist e do Commander.

O item 99 achava que faltava um avaliador de query. Ele JA EXISTE
(`_casa_filtro`, nos dois motores, com or/and/not/nor/xor/lte). O que faltava
era o VOCABULARIO: `_atomo_de_filtro` entende `trait`, `level`, `category` e
`rarity`, e os filtros da base usam `item:tag` 54 vezes -- ignorado, e atomo
ignorado CONTA COMO SATISFEITO.

Esse default e certo para ESTREITAR slot de feat (o principio zero manda nao
esvaziar em silencio) e DESTRUTIVO para DEFINIR eixo, porque o eixo sairia com
os 19.604 registros dentro. Por isso a ordem importa: a tag entra na base, o
motor aprende o atomo, e SO ENTAO o filtro vira eixo.

Kineticist e Commander sao as duas unicas classes com ZERO bloco de subclasse,
e as duas dependem de tag:

    Kinetic Gate   filter: ["item:tag:kineticist-kinetic-gate"]
    Tactics        filter: ["item:trait:tactic",
                            {"or": ["item:tag:commander-mobility-tactic",
                                    "item:tag:commander-offensive-tactic"]}]

O bloco guarda o FILTRO, nunca a lista: congelar a lista no build
dessincroniza na primeira mudanca de fonte, e `candidatos()` ja sabe avaliar.

Spec: specs/2026-07-31-tag-e-eixo-por-query.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_eixo_por_tag.md
"""
import collections
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

# `flag` distintas no mesmo registro sao escolhas distintas: o Commander tem
# `firstTactic`..`fifthTactic`, que sao CINCO taticas, nao uma.
EIXOS = [
    {"eixo": "kinetic-gate", "feature": "Kinetic Gate", "nivel": 1,
     "flags": ("elementOne", "elementTwo")},
    {"eixo": "tactic", "feature": "Tactics", "nivel": 1,
     "flags": ("firstTactic", "secondTactic", "thirdTactic",
               "fourthTactic", "fifthTactic")},
]


def foundry():
    sys.path.insert(0, AQUI)
    import comum
    raiz = comum.packs_foundry(BRUTOS)
    idx = {}
    for f in glob.glob(f"{raiz}/**/*.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and d.get("_id"):
            idx[d["_id"]] = d
    return idx


def id_foundry(reg) -> str:
    return str((reg.get("xref") or {}).get("foundry") or "").rsplit(".", 1)[-1]


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    fnd = foundry()
    if not fnd:
        print("!! sem repo do Foundry -- passo pulado", file=sys.stderr)
        return 0

    # -- 1) `tags` na base ---------------------------------------------------
    com_tag, por_kind = 0, collections.Counter()
    for reg in base:
        d = fnd.get(id_foundry(reg))
        if not d:
            continue
        ot = ((d.get("system") or {}).get("traits") or {}).get("otherTags") or []
        ot = [str(t) for t in ot if isinstance(t, str)]
        if not ot:
            continue
        reg["tags"] = sorted(set(ot))
        reg.setdefault("prov", {})["tags"] = "foundry"
        com_tag += 1
        por_kind[reg.get("kind")] += 1

    # -- 2) os eixos ---------------------------------------------------------
    # o filtro sai do PROPRIO ChoiceSet do Foundry, verbatim -- nunca a mao
    por_nome = collections.defaultdict(list)
    for d in fnd.values():
        n = str(d.get("name") or "")
        if n:
            por_nome[n].append(d)

    tocadas, relatorio = [], []
    for cfg in EIXOS:
        filtros, achados = None, 0
        for d in por_nome.get(cfg["feature"], []):
            for r in ((d.get("system") or {}).get("rules") or []):
                if not isinstance(r, dict) or r.get("key") != "ChoiceSet":
                    continue
                if r.get("flag") not in cfg["flags"]:
                    continue
                escolhas = r.get("choices")
                if isinstance(escolhas, dict) and escolhas.get("filter"):
                    filtros = escolhas["filter"]
                    achados += 1
        if filtros is None:
            print(f"!! eixo `{cfg['eixo']}`: nenhum ChoiceSet com filtro em "
                  f"`{cfg['feature']}` -- a fonte mudou", file=sys.stderr)
            return 1

        # a class-feature na NOSSA base, e a classe que a concede
        alvo = next((r["id"] for r in base
                     if r.get("kind") == "class-feature"
                     and str(r.get("name") or "") == cfg["feature"]), None)
        if alvo is None:
            print(f"!! eixo `{cfg['eixo']}`: `{cfg['feature']}` nao esta na base",
                  file=sys.stderr)
            return 1
        classes = [r for r in base if r.get("kind") == "class"
                   and any(e.get("concede") == alvo
                           for e in (r.get("progressao") or []))]
        if not classes:
            print(f"!! eixo `{cfg['eixo']}`: nenhuma classe concede `{alvo}`",
                  file=sys.stderr)
            return 1
        for classe in classes:
            blocos = classe.setdefault("subclasses", [])
            if any(b.get("eixo") == cfg["eixo"] for b in blocos):
                continue
            blocos.append({
                "eixo": cfg["eixo"], "nivel": cfg["nivel"], "slot": "subclasse",
                "escolhe": achados,
                # sem `opcoes`: quem responde e `candidatos()`, avaliando o
                # filtro. Congelar a lista aqui dessincroniza na primeira
                # mudanca de fonte.
                "opcoes": [], "com_mecanica": [], "so_catalogo": [],
                "filtro": filtros,
            })
            tocadas.append(f"{classe['id']} / {cfg['eixo']}")
            relatorio.append((classe["id"], cfg["eixo"], achados,
                              json.dumps(filtros, ensure_ascii=False)))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Tags e eixos por query", "",
           f"- registros que ganharam `tags`: **{com_tag}** (eram **0**)",
           f"- por kind: {dict(por_kind.most_common(6))}", "",
           "`item:tag` era usado 54 vezes nos filtros da base e o motor o "
           "IGNORAVA -- e atomo ignorado conta como SATISFEITO. Isso e certo "
           "para estreitar slot de feat e destrutivo para definir eixo, que e "
           "por isso que a tag entra antes do eixo.", "",
           f"- eixos criados: **{len(tocadas)}**", "",
           "| classe | eixo | escolhe | filtro |", "|---|---|---:|---|"]
    for cid, eixo, quantos, filtro in relatorio:
        rel.append(f"| `{cid}` | `{eixo}` | {quantos} | `{filtro}` |")
    rel += ["", "O bloco guarda o FILTRO, nunca a lista: `candidatos()` avalia "
            "com `_casa_filtro`, que ja existia e ja rodava."]
    with open(f"{BASE}/relatorio_eixo_por_tag.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"eixo por tag: {com_tag} registros com `tags`, "
          f"{len(tocadas)} eixo(s) criado(s)")
    print(f"-> {BASE}/relatorio_eixo_por_tag.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
