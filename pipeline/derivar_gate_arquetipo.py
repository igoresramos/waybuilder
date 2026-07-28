#!/usr/bin/env python3
"""
Todo feat de arquetipo exige a dedicacao daquele arquetipo.

E regra universal do PF2e, escrita uma vez no livro e nunca repetida em cada
feat: "You can't select a feat from an archetype unless you have its dedication
feat." Como a frase nao esta na prosa de cada feat, nenhuma das tres fontes a
escreve em `requires` -- e o resultado, medido, e que **407 dos 1.902 feats de
arquetipo** nao citam a propria dedicacao. Sem este passo da para pegar
`Absorb Spell` sem nunca ter pego `Spellmaster Dedication`.

Isto NAO e inventar dado: e materializar uma regra do livro que a fonte deixou
implicita. A diferenca em relacao a fabricar trait de heranca (recusado neste
projeto) e que aqui a regra existe, escrita, e vale para todos sem excecao.

O gate entra como conjuncao, preservando o `requires` que ja houver -- um feat
que exigia `Athletics treinado` passa a exigir `Athletics treinado E a
dedicacao`, nunca so a dedicacao.

Feat cuja dedicacao nao foi identificada fica intocado e aparece no relatorio;
melhor um gate faltando do que um gate errado.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_gate_arquetipo.md
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"


def cita(requires, alvo: str) -> bool:
    """O predicado ja menciona este id em qualquer profundidade?"""
    return alvo in json.dumps(requires or {})


def com_gate(requires, dedicacao: str):
    """Acrescenta `has: <dedicacao>` preservando o que ja existia."""
    gate = {"has": dedicacao}
    if not requires:
        return {"all": [gate]}
    if isinstance(requires, dict) and isinstance(requires.get("all"), list):
        return {**requires, "all": [*requires["all"], gate]}
    # qualquer outra forma (um termo solto, `any`, `not`) vira conjuncao
    return {"all": [requires, gate]}


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    feats = [r for r in base if r.get("kind") == "feat"]

    # a dedicacao de cada arquetipo. Um arquetipo com duas dedicacoes seria
    # ambiguo -- nao ha nenhum, e se aparecer o passo prefere nao decidir.
    por_arquetipo = {}
    ambiguos = set()
    for r in feats:
        traits = r.get("traits") or []
        arq = r.get("archetype")
        if "dedication" not in traits or not arq:
            continue
        if arq in por_arquetipo:
            ambiguos.add(arq)
        por_arquetipo[arq] = r["id"]
    for a in ambiguos:
        por_arquetipo.pop(a, None)

    aplicados, ja_tinham, sem_dedicacao = [], 0, []
    for r in feats:
        traits = r.get("traits") or []
        if "archetype" not in traits or "dedication" in traits:
            continue
        arq = r.get("archetype")
        if not arq:
            sem_dedicacao.append((r["id"], "sem campo `archetype`"))
            continue
        ded = por_arquetipo.get(arq)
        if not ded:
            sem_dedicacao.append((r["id"], f"arquetipo {arq} sem dedicacao unica"))
            continue
        if r["id"] == ded:
            continue
        if cita(r.get("requires"), ded):
            ja_tinham += 1
            continue
        r["requires"] = com_gate(r.get("requires"), ded)
        r["gate_arquetipo_derivado"] = True
        aplicados.append((r["id"], ded))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    linhas = [
        "# Gate de arquetipo derivado", "",
        "Regra do livro que nenhuma fonte escreve em `requires`: um feat de "
        "arquetipo exige a dedicacao daquele arquetipo.", "",
        f"- feats de arquetipo com gate JA presente: **{ja_tinham}**",
        f"- gate derivado agora: **{len(aplicados)}**",
        f"- sem dedicacao identificavel (intocados): **{len(sem_dedicacao)}**", "",
        "## Intocados", "",
        "| feat | motivo |", "|---|---|",
    ]
    for fid, motivo in sorted(sem_dedicacao)[:60]:
        linhas.append(f"| `{fid}` | {motivo} |")
    if len(sem_dedicacao) > 60:
        linhas.append(f"| ... | mais {len(sem_dedicacao) - 60} |")

    with open(f"{BASE}/relatorio_gate_arquetipo.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")

    print(f"gate de arquetipo: {len(aplicados)} derivados, "
          f"{ja_tinham} ja tinham, {len(sem_dedicacao)} intocados")
    print(f"-> {BASE}/relatorio_gate_arquetipo.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
