#!/usr/bin/env python3
"""
Feat com trait `archetype` e campo `archetype` VAZIO -- 73 deles.

Sem o campo, o feat nao pertence a arquetipo nenhum: `derivar_gate_arquetipo.py`
nao lhe aplica a regra "so com a dedicacao", ele nao aparece na lista do
arquetipo, e o item 46 quase o contou como orfao de outra coisa.

A ancora esta no proprio `requires`: 49 dos 73 exigem um feat de DEDICACAO, e
dedicacao carrega o arquetipo. Nao ha o que inventar -- e leitura.

Os outros 24 nao tem dedicacao no `requires`, e ficam como estao: chutar
arquetipo por semelhanca de nome poria o feat na lista errada, que e pior que
deixa-lo sem lista.

SEGUNDA METADE -- o homonimo classe x arquetipo. 12 ocorrencias em 11 registros
onde `requires`/`grants` aponta para o feat de ARQUETIPO tendo o `class-feature`
de mesmo nome ao lado (`quick-alchemy` 6, `advanced-alchemy` 2,
`champions-reaction` 2, `keen-recollection` 1, `surprise-attack` 1).

CUIDADO COM A CONTAGEM, e esta e a licao: uma medicao automatizada deu 40
porque contou todo `wb:feat/X` com `wb:class-feature/X` homonimo, sem checar se
o feat citado era de arquetipo. `shield-block` (trait `general`, 12 citacoes) e
`reactive-strike` (trait de classe, 5) NAO sao defeito -- feat e feature de
mesmo nome ali e RAW correto, e o motor ja os resolve por alias.

Spec: specs/2026-07-31-arquetipo-do-feat.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_arquetipo_do_feat.md
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

CITA = re.compile(r"wb:feat/[a-z0-9'\-]+")


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por = {r["id"]: r for r in base}
    feats = [r for r in base if r.get("kind") == "feat"]

    # -- 1) re-ancorar pelo `requires` --------------------------------------
    de_dedicacao = {r["id"]: r["archetype"] for r in feats
                    if "dedication" in (r.get("traits") or []) and r.get("archetype")}
    ancorados, sem_ancora = [], []
    for reg in feats:
        if reg.get("archetype") or "archetype" not in (reg.get("traits") or []):
            continue
        citados = set(CITA.findall(json.dumps(reg.get("requires"), ensure_ascii=False)))
        alvos = {de_dedicacao[c] for c in citados if c in de_dedicacao}
        if len(alvos) != 1:
            # zero: nao ha dedicacao no requires. Mais de uma: `Skill Mastery`
            # aceita Rogue OU Investigator -- ancorar num dos dois seria
            # escolher, e escolher errado poe o feat na lista errada.
            sem_ancora.append((reg["id"], len(alvos)))
            continue
        reg["archetype"] = next(iter(alvos))
        reg.setdefault("prov", {})["archetype"] = "derivado:dedicacao-no-requires"
        ancorados.append((reg["id"], reg["archetype"]))

    # -- 2) o homonimo classe x arquetipo -----------------------------------
    # so conta quando o alvo E de arquetipo: feat geral e feat de classe com
    # class-feature homonima sao RAW correto, e o motor ja resolve por alias.
    cf_por_nome = {}
    for r in base:
        if r.get("kind") == "class-feature":
            cf_por_nome.setdefault((r.get("name") or "").lower(), r["id"])

    homonimos = collections.Counter()
    for reg in base:
        for campo in ("requires", "grants"):
            bruto = json.dumps(reg.get(campo), ensure_ascii=False)
            for fid in set(CITA.findall(bruto)):
                alvo = por.get(fid)
                if not alvo or "archetype" not in (alvo.get("traits") or []):
                    continue
                gemeo = cf_por_nome.get((alvo.get("name") or "").lower())
                if gemeo:
                    homonimos[(reg["id"], campo, fid, gemeo)] += 1

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    por_arq = collections.Counter(a for _, a in ancorados)
    rel = ["# Arquetipo do feat", "",
           f"- feats re-ancorados pelo `requires`: **{len(ancorados)}**",
           f"- sem ancora (ficam como estao): **{len(sem_ancora)}**", "",
           "Chutar arquetipo por semelhanca de nome poria o feat na lista "
           "ERRADA, que e pior que deixa-lo sem lista. `Skill Mastery` aceita "
           "Rogue OU Investigator -- ancorar num dos dois seria escolher.", "",
           "| arquetipo | feats |", "|---|---:|"]
    for a, q in por_arq.most_common():
        rel.append(f"| `{a}` | {q} |")
    rel += ["", "## Homonimo classe x arquetipo (item 100)", "",
            f"- ocorrencias reais: **{len(homonimos)}**", "",
            "So conta quando o alvo E de arquetipo. Uma medicao automatizada "
            "deu 40 porque nao checava isso: `shield-block` (trait `general`) e "
            "`reactive-strike` (trait de classe) tem class-feature homonima e "
            "**nao sao defeito** -- e RAW correto, e o motor ja resolve por "
            "alias.", "",
            "| registro | campo | aponta para | class-feature homonima |",
            "|---|---|---|---|"]
    for (rid, campo, fid, gemeo) in sorted(homonimos):
        rel.append(f"| `{rid}` | `{campo}` | `{fid}` | `{gemeo}` |")
    with open(f"{BASE}/relatorio_arquetipo_do_feat.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"arquetipo do feat: {len(ancorados)} re-ancorados, "
          f"{len(sem_ancora)} sem ancora, {len(homonimos)} homonimos reais")
    print(f"-> {BASE}/relatorio_arquetipo_do_feat.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
