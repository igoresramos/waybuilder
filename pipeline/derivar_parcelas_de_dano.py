#!/usr/bin/env python3
"""
As duas parcelas de dano que a ficha nunca teve: Weapon Specialization e furia.

## Lacuna 1 -- Weapon Specialization, em 26 das 27 classes

`wb:class-feature/weapon-specialization` tem `grants: []`. O Foundry declara em
`FlatModifier` + dois `AdjustModifier` sobre `unarmed-damage`/`weapon-damage`,
com o predicado no rank DA ARMA: +2 expert, +3 master, +4 legendary. E
`Greater Weapon Specialization` e `mode: multiply, value: 2` -- DOBRA, nao soma.

26 classes concedem (todas menos o Exemplar). Ou seja, todo personagem do nivel
7 pra cima estava com o dano errado na ficha, faltando de 2 a 8.

## Lacuna 2 -- dano de furia

`AdjustModifier` com `slug: "rage"` sao 37 regras em 15 registros, e nada mais
na base usa esse slug. Hoje os nove instintos tem `grants: []`: escolher
instinto nao muda um numero sequer. `mode: upgrade` = MAIOR VENCE, nao soma --
o instinto substitui o +2 do `Rage`, nao acumula.

## O grau amarra na FEATURE, nao no numero

O Foundry escreve o grau 2 como `{"gte": ["self:level", 7]}`, e `self:level` la
e nivel de PERSONAGEM. Aqui os dois numeros diferem, entao traduzir ao pe da
letra seria escolher, nao ler. O grau vira `has` da class-feature que aquele
nivel compra -- forma que o proprio Foundry usa no Elemental Instinct
(`feature:weapon-specialization`), e que a regra 3 da houserule ja decidiu.

A CHAVE E O `_id` DO FOUNDRY, nunca o nome: `Greater Weapon Specialization`
existe tres vezes na base com ids diferentes (colisao desmembrada).

Spec: specs/2026-07-30-dano-de-furia.md
Entrada: pipeline/base/index.json + dados_brutos/foundry_repo/
Saida:   index.json enriquecido + base/relatorio_parcelas_de_dano.md
"""
import collections
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

RANK_POR_NUMERO = {2: "expert", 3: "master", 4: "legendary"}

# Gatilho de rolagem, nao de construcao. Um grau com qualquer um destes no
# predicado vira CONDICIONAL: aparece na ficha com a condicao escrita e NAO
# entra no total. Marcar, nunca esconder.
CONDICOES = {
    "draconic-rage": "draconic rage",
    "spirit-rage": "spirit rage",
    "wooden-rage": "wooden rage",
    "rotting-rage": "rotting rage",
    "item:oversized": "arma oversized",
}

# `target:caster` e alvo, nao ficha -- o grau inteiro sai (spec).
FORA = {"target:caster"}

# Efeito ativo ou acao gasta na rodada: nao e construcao de personagem.
# `Elemental Evolution` e do eidolon do Summoner, outra ficha.
REGISTROS_FORA = {"Effect: Share Rage", "Guard's Fury", "Mighty Rage",
                  "Elemental Evolution"}


def tokens(pred) -> set:
    """Achata o predicado num conjunto de strings comparaveis.

    `not` NAO desce. Achatar cego trocava o sinal: o grau 13 do Superstition
    tem `{"not": "target:caster"}` -- o caso ORDINARIO, contra quem nao e
    conjurador -- e ele saia como se exigisse `target:caster`, sendo entao
    descartado por `FORA`. O relatorio mostrou 3, 7 onde a spec dizia 3, 7, 13,
    e foi assim que apareceu.
    """
    fora = set()
    for p in (pred or []):
        if isinstance(p, str):
            fora.add(p)
        elif isinstance(p, dict):
            for chave, v in p.items():
                if chave == "not":
                    continue
                fora |= tokens(v if isinstance(v, list) else [v])
    return fora


def foundry():
    """`_id` do Foundry -> (nome, rules)."""
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
            regras = (d.get("system") or {}).get("rules") or []
            if regras:
                idx[d["_id"]] = (d.get("name") or "", regras)
    return idx


def id_foundry(reg) -> str:
    """`Compendium.pf2e.classfeatures.Item.XXXX` -> `XXXX`."""
    return str((reg.get("xref") or {}).get("foundry") or "").rsplit(".", 1)[-1]


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por = {r["id"]: r for r in base}
    fnd = foundry()
    if not fnd:
        print("!! sem repo do Foundry -- passo pulado", file=sys.stderr)
        return 0

    # -- Weapon Specialization ------------------------------------------------
    # o mapa por rank sai do `FlatModifier` + `AdjustModifier` do proprio
    # registro; o multiplicador, do `mode: multiply`.
    ws_tocados, ws_relatorio = [], []
    for reg in base:
        nome, regras = fnd.get(id_foundry(reg), ("", []))
        if "weapon specialization" not in nome.lower():
            continue
        por_rank, multiplicador = {}, None
        for r in regras:
            if not isinstance(r, dict) or r.get("slug") != "weapon-specialization":
                continue
            valor = r.get("value")
            if r.get("key") == "AdjustModifier" and r.get("mode") == "multiply":
                multiplicador = valor
                continue
            if not isinstance(valor, int):
                continue
            marcas = tokens(r.get("predicate"))
            rank = next((RANK_POR_NUMERO[n] for n in (4, 3, 2)
                         if f"item:proficiency:rank:{n}" in marcas), None)
            # o `FlatModifier` base usa `gte rank 2`, sem rank literal
            por_rank[rank or "expert"] = valor
        if not por_rank and multiplicador is None:
            continue
        efeito = ({"por_rank": por_rank} if por_rank
                  else {"multiplicador": multiplicador})
        grants = reg.setdefault("grants", [])
        if not any("weapon_specialization" in g for g in grants
                   if isinstance(g, dict)):
            grants.append({"weapon_specialization": efeito})
            reg.setdefault("prov", {})["grants"] = \
                reg.get("prov", {}).get("grants") or "foundry:rule-elements"
            ws_tocados.append(reg["id"])
            ws_relatorio.append((reg["id"], json.dumps(efeito, ensure_ascii=False)))

    # -- dano de furia --------------------------------------------------------
    # os graus amarram na feature que o nivel compra, lida da progressao do
    # PROPRIO Barbaro -- nunca de id escrito a mao.
    barbaro = por.get("wb:class/barbarian") or {}
    prog = {e.get("concede") for e in (barbaro.get("progressao") or [])}
    def da_progressao(fragmento, sem=None):
        # `sem` existe porque casar por fragmento solto pegava o registro
        # errado: ordenado, `greater-weapon-specialization-barbarian` vem ANTES
        # de `weapon-specialization`, entao o grau 2 passou a exigir o Greater
        # e um Barbaro 7 de instinto Fury saia com +3 em vez de +7.
        return next((c for c in sorted(prog)
                     if c and fragmento in c and (not sem or sem not in c)), None)

    gws = da_progressao("greater-weapon-specialization")
    ws = da_progressao("weapon-specialization", sem="greater")
    if not (gws and ws):
        print("!! progressao do Barbaro sem weapon specialization", file=sys.stderr)
        return 1

    # o +2 de base nao esta na class-feature `Rage` -- ela so tem um `GrantItem`
    # apontando para a ACAO `Rage`, e e a acao que carrega o `FlatModifier`.
    # Achado por FORMA, nao por id escrito a mao: tirando os registros ja
    # recusados, `FlatModifier` com `slug: rage` existe uma vez so no Foundry
    # inteiro. O `Effect: Share Rage` tem o segundo, e a assercao o pegou.
    base_rage = [r for nome, regras in fnd.values() if nome not in REGISTROS_FORA
                 for r in regras
                 if isinstance(r, dict) and r.get("key") == "FlatModifier"
                 and r.get("slug") == "rage" and isinstance(r.get("value"), int)]
    if len(base_rage) != 1:
        print(f"!! esperava 1 FlatModifier slug=rage, achei {len(base_rage)}",
              file=sys.stderr)
        return 1
    if "wb:class-feature/rage" in por:
        por["wb:class-feature/rage"]["rage_damage"] = {
            "graus": [{"valor": base_rage[0]["value"], "requires": None}],
            "condicao": None}
        por["wb:class-feature/rage"].setdefault("prov", {})["rage_damage"] = \
            "foundry:rule-elements"

    rage_tocados, rage_relatorio, descartados = [], [], collections.Counter()
    rage_tocados.append("wb:class-feature/rage")
    rage_relatorio.append(("wb:class-feature/rage", "Rage (base)", None,
                           [base_rage[0]["value"]]))
    for reg in base:
        nome, regras = fnd.get(id_foundry(reg), ("", []))
        if nome in REGISTROS_FORA:
            descartados[nome] += 1
            continue
        graus, condicao = [], None
        for r in regras:
            if not isinstance(r, dict) or r.get("slug") != "rage":
                continue
            valor = r.get("value")
            if not isinstance(valor, int):
                descartados["valor nao inteiro"] += 1
                continue
            marcas = tokens(r.get("predicate"))
            if marcas & FORA:
                descartados["alvo do combate"] += 1
                continue
            achada = next((v for k, v in CONDICOES.items() if k in marcas), None)
            if achada:
                condicao = achada
            if any("greater-weapon-specialization" in m for m in marcas):
                exige = {"has": gws}
            elif any("weapon-specialization" in m for m in marcas) or \
                    any(m == "self:level" for m in marcas):
                exige = {"has": ws}
            else:
                exige = None
            graus.append({"valor": valor, "requires": exige})
        if not graus:
            continue
        # `mode: upgrade` = maior vence. Ordenar do menor para o maior deixa a
        # leitura obvia e o motor escolhe o maior que ATENDE.
        graus.sort(key=lambda g: g["valor"])
        efeito = {"graus": graus, "condicao": condicao}
        for alvo in {reg["id"], reg.get("equivale_a")} - {None}:
            if alvo in por:
                por[alvo]["rage_damage"] = efeito
                por[alvo].setdefault("prov", {})["rage_damage"] = \
                    "foundry:rule-elements"
                rage_tocados.append(alvo)
        rage_relatorio.append((reg["id"], nome, condicao,
                               [g["valor"] for g in graus]))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Parcelas de dano", "",
           "## Weapon Specialization", "",
           f"- registros tocados: **{len(ws_tocados)}**", "",
           "Estava `grants: []` em todos. 26 das 27 classes concedem: todo "
           "personagem do nivel 7 pra cima tinha o dano errado na ficha.", "",
           "| registro | efeito |", "|---|---|"]
    for rid, efeito in sorted(ws_relatorio):
        rel.append(f"| `{rid}` | `{efeito}` |")
    rel += ["", "## Dano de furia", "",
            f"- registros com `rage_damage`: **{len(set(rage_tocados))}**",
            f"- descartados: **{sum(descartados.values())}** "
            f"({', '.join(f'{k} {v}' for k, v in descartados.most_common()) or '-'})",
            "", "`mode: upgrade` = maior vence, nao soma: o instinto SUBSTITUI "
            "o +2 do Rage.", "",
            "| registro | nome | condicao | graus |", "|---|---|---|---|"]
    for rid, nome, cond, valores in sorted(rage_relatorio):
        rel.append(f"| `{rid}` | {nome} | {cond or '--'} | "
                   f"{', '.join(str(v) for v in valores)} |")
    with open(f"{BASE}/relatorio_parcelas_de_dano.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"parcelas de dano: weapon specialization em {len(ws_tocados)} "
          f"registros, rage_damage em {len(set(rage_tocados))}")
    print(f"-> {BASE}/relatorio_parcelas_de_dano.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
