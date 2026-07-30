#!/usr/bin/env python3
"""
Le `attribute` e `skill` do AoN nos backgrounds que ficaram sem beneficio.

Dez backgrounds da base tinham `boosts` E `skill_training` vazios -- escolher
`Refugee` na criacao nao mudava um numero da ficha. Os dez NAO existem no
Foundry (verificado arquivo a arquivo), e a enumeracao da base vem de la; eles
entraram pelo AoN, de onde o extrator le so os campos textuais.

O AoN tem `attribute` e `skill` em nove dos dez. E lacuna de leitura, nao de
fonte -- a quinta encontrada no mesmo dia.

SO PREENCHE O QUE ESTA VAZIO: registro vindo do Foundry ja tem o dado
estruturado e nao e tocado.

Spec: specs/2026-07-30-background-sem-beneficio.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_beneficio_background.md
"""
import glob
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

CODIGO = {"strength": "str", "dexterity": "dex", "constitution": "con",
          "intelligence": "int", "wisdom": "wis", "charisma": "cha"}


def docs_do_aon() -> dict:
    saida = {}
    for caminho in glob.glob(f"{BRUTOS}/aon*.json") + glob.glob(f"{BRUTOS}/aon_dump/*.json"):
        try:
            with open(caminho, encoding="utf-8") as fh:
                dados = json.load(fh)
        except Exception:
            continue
        for doc in (dados if isinstance(dados, list) else dados.get("docs") or []):
            if isinstance(doc, dict) and doc.get("id"):
                saida[doc["id"]] = doc
    return saida


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    aon = docs_do_aon()

    preenchidos, sem_fonte, escolhas_de_lore = [], [], []
    for reg in base:
        if reg.get("kind") != "background":
            continue
        if reg.get("boosts") or reg.get("skill_training"):
            continue
        doc = aon.get((reg.get("xref") or {}).get("aon")) or {}
        attrs = [CODIGO.get(str(a).strip().lower()) for a in (doc.get("attribute") or [])]
        attrs = sorted(a for a in attrs if a)
        pericias = [str(s).strip() for s in (doc.get("skill") or []) if str(s).strip()]
        if not attrs and not pericias:
            sem_fonte.append(reg["id"])
            continue

        if attrs:
            # o segundo boost, livre, e regra do livro e nao vem da fonte:
            # todo background da um.
            reg["boosts"] = [
                {"ability_boost": {"opcoes": attrs, "quantidade": 1}},
                {"ability_boost": {"livre": True, "quantidade": 1}},
            ]
            reg.setdefault("prov", {})["boosts"] = "aon"

        skills, lore = [], []
        for s in pericias:
            if " or " in s.lower():
                # "Driving Lore or Piloting Lore" e ESCOLHA, nao nome. Inventar
                # uma pericia com esse nome seria pior que a lacuna.
                escolhas_de_lore.append((reg["id"], s))
                continue
            if s.lower().endswith("lore"):
                lore.append(s)
            else:
                skills.append(re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-"))
        if skills or lore:
            reg["skill_training"] = {"skills": skills, "lore": lore}
            reg.setdefault("prov", {})["skill_training"] = "aon"
        preenchidos.append((reg["id"], attrs, skills, lore))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Beneficio de background lido do AoN", "",
           f"- preenchidos: **{len(preenchidos)}**",
           f"- sem dado no AoN tambem: **{len(sem_fonte)}**",
           f"- entradas de Lore com escolha (` or `), deixadas de fora: "
           f"**{len(escolhas_de_lore)}**", "",
           "| background | boosts | pericias | lore |", "|---|---|---|---|"]
    for i, a, s, l in sorted(preenchidos):
        rel.append(f"| {i} | {', '.join(a) or '-'} | {', '.join(s) or '-'} | "
                   f"{', '.join(l) or '-'} |")
    if sem_fonte:
        rel += ["", "## Sem `attribute` nem `skill` no AoN", ""]
        rel += [f"- `{i}`" for i in sorted(sem_fonte)]
    if escolhas_de_lore:
        rel += ["", "## Lore com escolha -- o schema nao tem forma para isso", ""]
        rel += [f"- `{i}`: {s}" for i, s in sorted(escolhas_de_lore)]
    with open(f"{BASE}/relatorio_beneficio_background.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"beneficio de background: {len(preenchidos)} preenchidos, "
          f"{len(sem_fonte)} sem fonte, {len(escolhas_de_lore)} lore com escolha")
    print(f"-> {BASE}/relatorio_beneficio_background.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
