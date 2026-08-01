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

sys.path.insert(0, AQUI)
import comum   # noqa: E402

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
    # `comum.packs_foundry()` e nao caminho fixo: o clone chega como `foundry/`
    # ou `foundry_repo/` conforme quem o baixou, e o caminho fixo `foundry/`
    # caia no lado errado NESTA maquina -- `fontes: foundry=0 itens`, em
    # silencio. Este passo ficou de fora da correcao que ja tinha alcancado
    # portoes, emitir_textos, aplicar_subclasses e converter_rule_elements.
    # Custo medido do silencio: 53 armas perdiam `damage` a cada rebuild
    # (`Blowgun` entre elas), e a base versionada sobrevivia so porque
    # carregava o dado de um build antigo, feito quando o clone tinha o outro
    # nome. `**` porque os packs sao em subpasta por categoria.
    raiz_foundry = comum.packs_foundry(BRUTOS)
    padrao = (os.path.join(raiz_foundry, "equipment", "**", "*.json")
              if raiz_foundry else f"{BRUTOS}/foundry/packs/pf2e/equipment/*.json")
    for caminho in glob.glob(padrao, recursive=True):
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
# Dano FIXO, sem dado: o AoN escreve `1 P` para Blowgun e Dart Umbrella, e e
# RAW -- as duas causam 1 ponto, nao 1dX. Exigir `dN` deixava as duas sem
# `damage` e portanto fora da aba de Ataques, com o dado inteiro no disco.
FIXO = re.compile(r"^\s*(\d+)\s*(?![dD]\d)")
TIPO_CURTO = {"b": "bludgeoning", "p": "piercing", "s": "slashing"}


def tipo_de_dano(bruto: str, declarado) -> str | None:
    """A LETRA da string manda; `damage_type[]` e so o desempate.

    O dump do AoN traz `damage_type` HARDCODED em `["Piercing"]` para as 11
    armas de combinacao `(Melee)`, mesmo quando a propria string discorda:
    `Gun Sword (Melee)` tem `damage: "1d8 S"` e `damage_type: ["Piercing"]` no
    MESMO documento. Ler o campo estruturado gravava `piercing` em arma
    cortante.

    O bug e da fonte e e antigo, mas dormia enquanto `do_aon()` lia zero itens
    por caminho errado. Consertar o caminho o ACORDOU, e trocou um `None`
    honesto por um valor errado plausivel -- que e pior, porque ninguem
    desconfia dele.
    """
    m = re.search(r"\d\s*(?:d\d+)?\s*([BPS])\b", str(bruto or ""), re.I)
    if m:
        return TIPO_CURTO[m.group(1).lower()]
    return str(declarado[0]).lower() if declarado else None


def do_aon():
    """nome normalizado -> bloco mecanico, dos dumps de equipamento."""
    saida = {}
    # Os nomes `aon_equipment_*.json` nao existem em disco desde que a fonte foi
    # refeita dentro de `dados_brutos/` -- o dump por categoria do AoN grava
    # `aon_dump/weapon.json` e irmaos. O passo lia `aon=0 itens` e seguia
    # calado, e por isso `Blowgun` (dano FIXO `1 P`, que so o AoN traz) ficava
    # sem `damage` mesmo com o arquivo no disco. Os nomes antigos ficam na
    # lista: se um dia voltarem, valem.
    mapa = {
        "aon_dump/weapon.json": "weapon",
        "aon_dump/armor.json": "armor",
        "aon_dump/shield.json": "shield",
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
                bruto = str(s.get("damage") or "")
                m = DADO.search(bruto)
                tipos = s.get("damage_type") or []
                tipo_dmg = tipo_de_dano(bruto, tipos)
                if m and tipo_dmg:
                    bloco["damage"] = {
                        "dados": int(m.group(1) or 1),
                        "dado": m.group(2).lower(),
                        "tipo": tipo_dmg,
                    }
                elif tipo_dmg and FIXO.match(bruto):
                    # sem a chave `dado`, e nao com `dado: None`: os dois motores
                    # fazem `dano.get("dado", "")` / `Object.hasOwn`, entao a
                    # chave presente com None imprimiria "None" na ficha
                    bloco["damage"] = {
                        "dados": int(FIXO.match(bruto).group(1)),
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


# `Base Armor Chain Mail`, `Base Shield Steel Shield` -- o cabecalho do item
# magico DIZ de quem ele herda. Nenhuma das tres fontes poe isso em campo,
# porque no PF2e a armadura magica herda a base e o livro nao repete os numeros.
BASE_DE = re.compile(r"\bBase (?:Armor|Shield|Weapon)\s+(.+?)(?=\s+(?:---|Source|Price|Usage|Bulk|Base )|$)")


def prosa_por_kind(kind: str) -> dict:
    caminho = f"{BASE}/text/{kind}.json"
    if not os.path.exists(caminho):
        return {}
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def herdar_da_base(base, curados, sobraram):
    """Segunda passada: item magico herda o bloco da armadura/escudo base.

    Ex.: `Celestial Armor` traz `Base Armor Chain Mail` no texto -- e uma chain
    mail magica, e usa os numeros dela. Sem isto, equipar Celestial Armor dava
    CA de personagem pelado, num item de 2.500 gp.
    """
    por_nome = {}
    for r in base:
        if r.get("kind") in CRITICO and r.get(CRITICO[r["kind"]]) is not None:
            por_nome[(r["kind"], norm(r.get("name")))] = r

    textos = {k: prosa_por_kind(k) for k in ("armor", "shield", "weapon")}
    herdados, restam = [], []
    for rid, nome, kind in sobraram:
        reg = next((x for x in base if x["id"] == rid), None)
        if reg is None:
            continue
        texto = textos.get(kind, {}).get(reg.get("text") or "", "")
        m = BASE_DE.search(texto or "")
        if not m:
            restam.append((rid, nome, kind))
            continue
        alvo = None
        for c in chaves(m.group(1).strip()):
            alvo = por_nome.get((kind, c))
            if alvo:
                break
        if alvo is None:
            restam.append((rid, nome, kind))
            continue
        campos = []
        for campo, valor in alvo.items():
            if campo in ("id", "name", "kind", "text", "prov", "xref", "source",
                         "traits", "rarity", "level", "grants", "requires",
                         "aliases", "historico", "legado_de", "runes",
                         "mecanica_recuperada", "herdado_de"):
                continue
            if reg.get(campo) in (None, "", {}):
                reg[campo] = valor
                campos.append(campo)
        if campos:
            reg["herdado_de"] = alvo["id"]
            herdados.append((rid, nome, kind, alvo["name"], campos))
        else:
            restam.append((rid, nome, kind))
    return herdados, restam


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

    # `Unarmored` nao e armadura, e a AUSENCIA dela -- e por isso nao tem
    # numero em fonte nenhuma. Declarar o zero explicito e melhor que deixar
    # nulo: o motor para de precisar de caso especial e a ficha mostra 0.
    for r in base:
        if r.get("kind") == "armor" and norm(r.get("name")) == "unarmored":
            r.setdefault("ac_bonus", 0)
            r.setdefault("armor_category", "unarmored")
            sobraram = [x for x in sobraram if x[0] != r["id"]]
            curados.append((r["id"], r.get("name"), "armor", "definicao",
                            ["ac_bonus", "armor_category"]))

    herdados, sobraram = herdar_da_base(base, curados, sobraram)

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    linhas = [
        "# Mecanica de equipamento recuperada", "",
        "Nao era falta de fonte -- era falha de matching. Duas causas: o Foundry "
        "escreve `Leather Armor` onde o AoN escreve `Leather`, e as armas "
        "universais (`Fist`, `Shield Bash`) nao existem como arquivo no Foundry, "
        "so no dump do AoN.", "",
        f"- registros curados por fonte: **{len(curados)}**",
        f"- herdados do item base (`Base Armor X` no texto): **{len(herdados)}**",
        f"- ainda sem o campo critico: **{len(sobraram)}**", "",
        "## Herdados", "",
        "| id | nome | kind | herda de | campos |", "|---|---|---|---|---|",
    ] + [
        f"| `{i}` | {n} | {k} | {alvo} | {', '.join(c)} |"
        for i, n, k, alvo, c in sorted(herdados)[:60]
    ] + ["",
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

    print(f"curados: {len(curados)} | herdados: {len(herdados)} "
          f"| ainda sem: {len(sobraram)}")
    print(f"-> {BASE}/relatorio_mecanica_equipamento.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
