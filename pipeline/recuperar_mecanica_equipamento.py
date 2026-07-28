#!/usr/bin/env python3
"""
Recupera o bloco mecanico de arma, armadura e escudo que o extrator nao casou.

Nao e falta de fonte -- e falha de MATCHING, e a diferenca importa: o dado esta
no disco, so nao foi encontrado. Medido antes deste passo:

  110 de 1.041 armas sem `damage`      (10,6%)
   14 de   216 armaduras sem `ac_bonus` (6,5%)
    7 de   125 escudos sem `ac_bonus`   (5,6%)

E os afetados nao sao conteudo de nicho. Estavam ali `Fist` e `Shield Bash` --
que toda ficha usa -- e `Leather`, `Hide`, `Studded Leather` e `Unarmored`, as
armaduras mais comuns do jogo. Equipar couro nao mudava numero nenhum.

Duas causas distintas, as duas confirmadas na fonte:

1. **Sufixo divergente.** O Foundry escreve `Leather Armor`, `Hide Armor`,
   `Studded Leather Armor`; o AoN (e a nossa base) escrevem `Leather`, `Hide`,
   `Studded Leather`. Casar por nome exato nunca ia bater.
2. **Arma universal fora do pack de itens.** `Fist` e `Shield Bash` nao existem
   como arquivo no Foundry (o VTT os modela em outro lugar), mas estao no dump
   do AoN com dano e traits completos.

A ordem de precedencia segue a da base: **Foundry manda no numero mecanico**
(e a fonte que existe para isso), AoN entra quando o Foundry nao tem o item.

Preenche SO campo ausente. Nao sobrescreve valor existente -- se um registro ja
tem `ac_bonus`, ele nao e tocado, e uma eventual divergencia continua sendo
assunto de `auditar_conflitos.py`.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_mecanica_equipamento.md
"""
import glob
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

# sufixos que uma fonte poe e a outra nao
SUFIXOS = (" armor", " shield", " weapon")

CRITICO = {
    "weapon": "damage",
    "armor": "ac_bonus",
    "shield": "ac_bonus",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def chaves(nome: str):
    """O nome como esta, e sem o sufixo que so uma das fontes usa."""
    saida = {norm(nome)}
    baixo = str(nome or "").lower()
    for s in SUFIXOS:
        if baixo.endswith(s):
            saida.add(norm(baixo[: -len(s)]))
    return saida


# --------------------------------------------------------------------------
# leitura das fontes
# --------------------------------------------------------------------------

def do_foundry():
    """nome normalizado -> bloco mecanico, dos packs de equipamento."""
    saida = {}
    for caminho in glob.glob(f"{BRUTOS}/foundry/packs/pf2e/equipment/*.json"):
        try:
            with open(caminho, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        tipo, s = d.get("type"), d.get("system") or {}
        bloco = {}
        if tipo == "armor":
            bloco = {
                "ac_bonus": s.get("acBonus"), "dex_cap": s.get("dexCap"),
                "check_penalty": s.get("checkPenalty"),
                "speed_penalty": s.get("speedPenalty"),
                "strength": s.get("strength"),
                "armor_category": s.get("category"), "group": s.get("group"),
            }
        elif tipo == "shield":
            bloco = {
                "ac_bonus": s.get("acBonus"),
                "hardness": s.get("hardness"),
                "hp": (s.get("hp") or {}).get("max"),
                "speed_penalty": s.get("speedPenalty"),
            }
        elif tipo == "weapon":
            dmg = s.get("damage") or {}
            if dmg.get("die") and dmg.get("damageType"):
                bloco = {
                    "damage": {"dados": dmg.get("dice") or 1,
                               "dado": dmg.get("die"),
                               "tipo": dmg.get("damageType")},
                    "weapon_category": s.get("category"),
                    "group": s.get("group"),
                }
        bloco = {k: v for k, v in bloco.items() if v not in (None, "")}
        if not bloco:
            continue
        # a chave inclui o TIPO. Sem isso `Hide` (armadura) casava com o
        # primeiro item cujo nome colapsasse em "hide" na ordem arbitraria do
        # glob, e entrou `ac_bonus: 2` onde a fonte diz 3.
        for c in chaves(d.get("name")):
            saida.setdefault((tipo, c), bloco)
    return saida


DADO = re.compile(r"(\d*)\s*(d\d+)", re.I)
TIPO_CURTO = {"b": "bludgeoning", "p": "piercing", "s": "slashing"}


def do_aon():
    """nome normalizado -> bloco mecanico, dos dumps de equipamento."""
    saida = {}
    mapa = {
        "aon_equipment_weapon.json": "weapon",
        "aon_equipment_armor.json": "armor",
        "aon_equipment_shield.json": "shield",
    }
    for arquivo, tipo in mapa.items():
        caminho = f"{BRUTOS}/{arquivo}"
        if not os.path.exists(caminho):
            continue
        with open(caminho, encoding="utf-8") as fh:
            bruto = json.load(fh)
        docs = bruto if isinstance(bruto, list) else (bruto.get("hits") or [])
        for d in docs:
            s = d.get("_source", d)
            bloco = {}
            if tipo == "weapon":
                m = DADO.search(str(s.get("damage") or ""))
                tipos = s.get("damage_type") or []
                if m and tipos:
                    bloco["damage"] = {
                        "dados": int(m.group(1) or 1),
                        "dado": m.group(2).lower(),
                        "tipo": str(tipos[0]).lower(),
                    }
                if s.get("weapon_category"):
                    bloco["weapon_category"] = str(s["weapon_category"]).lower()
                if s.get("weapon_group"):
                    bloco["group"] = str(s["weapon_group"]).lower()
            else:
                for de, para in (("ac_bonus", "ac_bonus"), ("dex_cap", "dex_cap"),
                                 ("check_penalty", "check_penalty"),
                                 ("speed_penalty", "speed_penalty"),
                                 ("strength", "strength"), ("hardness", "hardness"),
                                 ("hp", "hp")):
                    if s.get(de) is not None:
                        bloco[para] = s[de]
            bloco = {k: v for k, v in bloco.items() if v not in (None, "")}
            if not bloco:
                continue
            for c in chaves(s.get("name")):
                saida.setdefault((tipo, c), bloco)
    return saida


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    foundry, aon = do_foundry(), do_aon()
    print(f"fontes: foundry={len(foundry)} itens, aon={len(aon)} itens")

    curados, sobraram = [], []
    for r in base:
        kind = r.get("kind")
        critico = CRITICO.get(kind)
        if not critico or r.get(critico) not in (None, "", {}):
            continue

        origem = None
        for c in chaves(r.get("name")):
            # Foundry manda no numero mecanico; AoN cobre o que ele nao tem.
            # A busca e por (tipo, nome) -- armadura so casa com armadura.
            if (kind, c) in foundry:
                bloco, origem = foundry[(kind, c)], "foundry"
                break
            if (kind, c) in aon:
                bloco, origem = aon[(kind, c)], "aon"
                break
        if origem is None:
            sobraram.append((r["id"], r.get("name"), kind))
            continue

        preenchidos = []
        for campo, valor in bloco.items():
            if r.get(campo) in (None, "", {}):
                r[campo] = valor
                preenchidos.append(campo)
        if preenchidos:
            r["mecanica_recuperada"] = origem
            curados.append((r["id"], r.get("name"), kind, origem, preenchidos))
        else:
            sobraram.append((r["id"], r.get("name"), kind))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    linhas = [
        "# Mecanica de equipamento recuperada", "",
        "Nao era falta de fonte -- era falha de matching. Duas causas: o Foundry "
        "escreve `Leather Armor` onde o AoN escreve `Leather`, e as armas "
        "universais (`Fist`, `Shield Bash`) nao existem como arquivo no Foundry, "
        "so no dump do AoN.", "",
        f"- registros curados: **{len(curados)}**",
        f"- ainda sem o campo critico: **{len(sobraram)}**", "",
        "## Curados", "", "| id | nome | kind | fonte | campos |", "|---|---|---|---|---|",
    ]
    for i, n, k, o, campos in sorted(curados)[:80]:
        linhas.append(f"| `{i}` | {n} | {k} | {o} | {', '.join(campos)} |")
    if len(curados) > 80:
        linhas.append(f"| ... | | | | mais {len(curados) - 80} |")

    linhas += ["", "## Ainda sem", "", "| id | nome | kind |", "|---|---|---|"]
    for i, n, k in sorted(sobraram)[:80]:
        linhas.append(f"| `{i}` | {n} | {k} |")
    if len(sobraram) > 80:
        linhas.append(f"| ... | | mais {len(sobraram) - 80} |")

    with open(f"{BASE}/relatorio_mecanica_equipamento.md", "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")

    print(f"curados: {len(curados)} | ainda sem: {len(sobraram)}")
    print(f"-> {BASE}/relatorio_mecanica_equipamento.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
