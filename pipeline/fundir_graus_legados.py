#!/usr/bin/env python3
"""
Funde o GRAU legado que a fusao principal nao alcanca.

O Remaster renomeou `Cloak of Elvenkind` para `Cloak of Illusions`, e
`fundir_renomeados.py` fez o trabalho dele no grau BASE. Mas o AoN declara
`remaster_id` so no doc base (`equipment-424` -> `equipment-3069`) e nao nos
docs de grau (`equipment-424-514`), entao `Cloak of Elvenkind (Greater)` ficou
de pe ao lado de `Cloak of Illusions (Greater)` -- o mesmo item, nivel 12, duas
vezes.

A fusao principal esta certa em nao inventar par. Este passo cobre so o caso em
que o par ja EXISTE, provado pelo alias que ela mesma escreveu.

TRES CONDICOES JUNTAS, e nao uma heuristica de nome:
  1. o nome-base do legado e alias de um registro canonico;
  2. o canonico tem o MESMO sufixo de grau;
  3. os dois estao no MESMO nivel.
Nivel diferente veta -- mesmo criterio de "divergencia estrutural veta a fusao"
que a fusao principal ja aplica em 392 pares. Kind diferente tambem veta: foi o
que descartou `vigilant-eye`, cujo nome-base casa com o alias de uma MAGIA.

ORDEM: depois de 7 (fusao) e de 7c (aliases em requires), porque depende dos
aliases que a fusao escreveu.

Spec: specs/2026-07-30-grau-legado-nao-fundido.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_graus_legados.md
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

GRAU = re.compile(r"^(.*?)\s*\((greater|major|lesser|moderate|true|supreme)\)$",
                  re.I)


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    # nome legado (minusculo) -> registros que o declaram como alias
    por_alias = {}
    for r in base:
        for a in (r.get("aliases") or []):
            por_alias.setdefault(str(a).strip().lower(), []).append(r)

    por_nome_kind = {}
    for r in base:
        chave = (r.get("kind"), str(r.get("name") or "").strip().lower())
        por_nome_kind.setdefault(chave, []).append(r)

    fundidos, vetados = [], []
    remover = set()
    for r in list(base):
        m = GRAU.match(str(r.get("name") or "").strip())
        if not m:
            continue
        nome_base, grau = m.group(1).strip().lower(), m.group(2).lower()
        canonicos = por_alias.get(nome_base) or []
        if not canonicos:
            continue
        canon = canonicos[0]
        if canon.get("kind") != r.get("kind"):
            vetados.append((r["id"], canon["id"], "kind diferente"))
            continue
        alvo_nome = f"{str(canon.get('name') or '').strip().lower()} ({grau})"
        alvos = por_nome_kind.get((r.get("kind"), alvo_nome)) or []
        if not alvos:
            vetados.append((r["id"], canon["id"], "canonico nao tem este grau"))
            continue
        alvo = alvos[0]
        if alvo.get("level") != r.get("level"):
            vetados.append((r["id"], alvo["id"], "nivel divergente"))
            continue

        aliases = alvo.setdefault("aliases", [])
        if r.get("name") and r["name"] not in aliases:
            aliases.append(r["name"])
        for a in (r.get("aliases") or []):
            if a not in aliases:
                aliases.append(a)
        alvo.setdefault("historico", []).append(
            {"absorveu": r["id"], "por": "grau-legado-nao-fundido"})
        remover.add(r["id"])
        fundidos.append((r["id"], alvo["id"], r.get("level")))

    base = [r for r in base if r["id"] not in remover]
    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Grau legado fundido no canonico", "",
           f"- fundidos: **{len(fundidos)}**",
           f"- vetados: **{len(vetados)}**", "",
           "O AoN declara `remaster_id` so no doc BASE; o grau ficava de pe com "
           "o nome antigo. Tres condicoes juntas: nome-base e alias do "
           "canonico, mesmo sufixo de grau, MESMO nivel.", "",
           "## Fundidos", "", "| legado | canonico | nivel |", "|---|---|---:|"]
    for a, b, n in sorted(fundidos):
        rel.append(f"| {a} | {b} | {n} |")
    rel += ["", "## Vetados", "", "| legado | candidato | motivo |", "|---|---|---|"]
    for a, b, motivo in sorted(vetados):
        rel.append(f"| {a} | {b} | {motivo} |")
    with open(f"{BASE}/relatorio_graus_legados.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"graus legados: {len(fundidos)} fundidos, {len(vetados)} vetados")
    print(f"-> {BASE}/relatorio_graus_legados.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
