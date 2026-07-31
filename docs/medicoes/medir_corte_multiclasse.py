#!/usr/bin/env python3
"""
Item 46 -- as quatro validacoes que a propria anotacao do Igor exigiu antes de
decidir se o arquetipo de multiclasse sai.

Nao decide nada. Mede, e imprime numero para cada uma das quatro perguntas:

    (a) algum feat que SOBRA depende de um feat que SAI?
    (b) o que se perde de conteudo unico?
    (c) o que acontece com o piso da regra 21?
    (d) para quantos arquetipos o Free Archetype (regra 2) passa a apontar?

O recorte e DERIVADO do trait `multiclass`, nunca de lista a mao -- lista a mao
ja errou tres vezes neste projeto.

Saida: docs/2026-07-30_corte-multiclasse.md (escrito a mao a partir daqui)
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/../../pipeline/base/index.json"


def ids_citados(o) -> set:
    return set(re.findall(r"wb:feat/[a-z0-9'\-]+", json.dumps(o, ensure_ascii=False)))


def main() -> int:
    with open(BASE, encoding="utf-8") as fh:
        base = json.load(fh)
    por = {r["id"]: r for r in base}

    classes = {(r.get("name") or "").lower() for r in base if r.get("kind") == "class"}
    arqs = [r for r in base if r.get("kind") == "archetype"]
    feats = [r for r in base if r.get("kind") == "feat"]

    # o recorte, derivado por DUAS vias independentes que tem de bater
    dedicacoes = {r["id"] for r in feats if "multiclass" in (r.get("traits") or [])}
    arq_por_nome = {r["id"] for r in arqs if (r.get("name") or "").lower() in classes}
    arq_por_ded = {por[d].get("archetype") for d in dedicacoes} - {None}
    print("== recorte ==")
    print(f"arquetipos de multiclasse por NOME        : {len(arq_por_nome)}")
    print(f"arquetipos de multiclasse por DEDICACAO   : {len(arq_por_ded)}")
    print(f"as duas vias divergem em                  : "
          f"{sorted(arq_por_nome ^ arq_por_ded) or 'nada'}")
    corte_arq = arq_por_nome | arq_por_ded

    atribuidos = {r["id"] for r in feats if r.get("archetype") in corte_arq}

    # ORFAOS: trait `archetype`, sem `archetype` atribuido, mas cujo requires
    # cita uma dedicacao do corte. Sao feats do arquetipo cortado que a
    # atribuicao nao pegou -- se ficarem, ficam sem porta de entrada.
    orfaos = {r["id"] for r in feats
              if r["id"] not in atribuidos
              and "archetype" in (r.get("traits") or [])
              and not r.get("archetype")
              and ids_citados(r.get("requires")) & dedicacoes}
    corte_feat = atribuidos | orfaos
    print(f"\nfeats atribuidos ao arquetipo cortado     : {len(atribuidos)}")
    print(f"feats ORFAOS que pertencem ao corte       : {len(orfaos)}")
    print(f"total de feats no corte                   : {len(corte_feat)}")
    print(f"feats que sobram                          : {len(feats) - len(corte_feat)}")

    # ---------------------------------------------------------------- (a)
    print("\n== (a) dependencia de quem SOBRA em quem SAI ==")
    quebras = collections.defaultdict(list)
    for r in feats:
        if r["id"] in corte_feat:
            continue
        alvo = ids_citados(r.get("requires")) & corte_feat
        if not alvo:
            continue
        # tres naturezas distintas, e so uma e quebra de verdade
        nome_alvo = {(por[a].get("name") or "").lower() for a in alvo}
        homonimo = any(x.get("kind") == "class-feature"
                       and (x.get("name") or "").lower() in nome_alvo for x in base)
        if homonimo:
            natureza = "homonimo (existe class-feature de mesmo nome)"
        elif r.get("archetype") and r["archetype"] not in corte_arq:
            natureza = "QUEBRA REAL (arquetipo que sobra depende do que sai)"
        else:
            natureza = "orfao nao classificado"
        quebras[natureza].append((r["id"], sorted(alvo)))
    for nat, itens in sorted(quebras.items()):
        print(f"\n  {nat}: {len(itens)}")
        for rid, alvo in sorted(itens):
            print(f"    {rid:40} -> {', '.join(alvo)}")

    # ---------------------------------------------------------------- (b)
    print("\n== (b) conteudo unico que sai ==")
    concessoes = collections.Counter()
    for fid in corte_feat:
        for g in (por[fid].get("grants") or []):
            for k in g:
                concessoes[k] += 1
    for k, v in concessoes.most_common():
        print(f"  {k:28} {v}")
    spell = sorted(f for f in corte_feat
                   if "spellcasting" in (por[f].get("name") or "").lower())
    print(f"\n  feats de spellcasting no corte: {len(spell)}")
    for f in spell:
        print(f"    {por[f]['name']:34} lvl {por[f].get('level')}")

    # ---------------------------------------------------------------- (c)
    print("\n== (c) piso da regra 21 ==")
    tradicoes = collections.Counter()
    for fid in corte_feat:
        for g in (por[fid].get("grants") or []):
            if "spellcasting" in g or "spell_slots" in g:
                tradicoes[json.dumps(g, ensure_ascii=False)[:80]] += 1
    for k, v in tradicoes.most_common(10):
        print(f"  {v:3}  {k}")
    conj_fora = [r["id"] for r in feats
                 if r["id"] not in corte_feat
                 and "dedication" in (r.get("traits") or [])
                 and any("spell" in json.dumps(g) for g in (r.get("grants") or []))]
    print(f"\n  dedicacoes de conjuracao que SOBRAM: {len(conj_fora)}")
    for c in sorted(conj_fora)[:20]:
        print(f"    {c}")

    # ---------------------------------------------------------------- (d)
    print("\n== (d) alcance do Free Archetype ==")
    sobram = [r for r in arqs if r["id"] not in corte_arq]
    com_ded = [r for r in sobram
               if any(f.get("archetype") == r["id"]
                      and "dedication" in (f.get("traits") or []) for f in feats)]
    print(f"  arquetipos hoje                : {len(arqs)}")
    print(f"  arquetipos depois do corte     : {len(sobram)}")
    print(f"  desses, com feat de dedicacao  : {len(com_ded)}")
    print(f"  sem porta de entrada na base   : {len(sobram) - len(com_ded)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
