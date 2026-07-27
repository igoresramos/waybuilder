#!/usr/bin/env python3
"""
Analise READ-ONLY da base: mapeia grant_feat/grant_item que apontam para
outro registro que TAMBEM concede algo (feat que concede feat).

Nao escreve em pipeline/base/index.json nem em pipeline/saida/ -- so le.
Uso: python3 motor/testes_ciclos/mapear_cadeias.py
"""
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(os.path.dirname(AQUI))
INDEX = os.path.join(PROJETO, "pipeline", "base", "index.json")

with open(INDEX, encoding="utf-8") as fh:
    registros = json.load(fh)
por_id = {r["id"]: r for r in registros}

UUID_RE = re.compile(r"Compendium\.[^.]+\.[^.]+\.Item\.(\w+)")


def alvos_de_grant(g: dict):
    """Extrai os wb:id apontados por um item de `grants`, quando resolvivel."""
    alvos = []
    dinamico = False
    if "grant_feat" in g:
        val = g["grant_feat"]
        lista = val if isinstance(val, list) else [val]
        for v in lista:
            if isinstance(v, str) and v.startswith("wb:"):
                alvos.append(v)
            elif isinstance(v, str) and "{" in v:
                dinamico = True
    if "grant_item" in g:
        gi = g["grant_item"]
        uuid = gi.get("uuid") if isinstance(gi, dict) else gi
        if isinstance(uuid, str):
            if "{" in uuid:
                dinamico = True
            else:
                # tenta casar por xref.foundry
                for rid, r in por_id.items():
                    xf = (r.get("xref") or {}).get("foundry")
                    if xf and uuid in xf:
                        alvos.append(rid)
                        break
    return alvos, dinamico


# 1) construir grafo: wb:id -> lista de wb:id concedidos (resolviveis) + flag dinamico
grafo = {}
registros_com_grant_dinamico = []
registros_com_grant_resolvel = []
total_grants_feat_ou_item = 0

for r in registros:
    grants = r.get("grants") or []
    alvos_totais = []
    tem_dinamico = False
    for g in grants:
        if not isinstance(g, dict):
            continue
        if "grant_feat" not in g and "grant_item" not in g:
            continue
        total_grants_feat_ou_item += 1
        alvos, dinamico = alvos_de_grant(g)
        alvos_totais += alvos
        tem_dinamico = tem_dinamico or dinamico
    if alvos_totais:
        grafo[r["id"]] = alvos_totais
        registros_com_grant_resolvel.append(r["id"])
    if tem_dinamico:
        registros_com_grant_dinamico.append(r["id"])

print(f"Total de registros na base: {len(registros)}")
print(f"Registros com >=1 grant_feat/grant_item (bruto, resolvivel ou nao): "
      f"{sum(1 for r in registros if any(isinstance(g, dict) and ('grant_feat' in g or 'grant_item' in g) for g in (r.get('grants') or [])))}")
print(f"Total de items grant_feat/grant_item somados: {total_grants_feat_ou_item}")
print(f"Registros com grant DINAMICO (uuid com {{...}} ou grant_feat com {{...}}): "
      f"{len(registros_com_grant_dinamico)}")
print(f"Registros com grant RESOLVIVEL para outro wb:id: {len(registros_com_grant_resolvel)}")
print()

# 2) quantos registros encadeiam (A concede B, e B por sua vez tambem concede algo)?
encadeiam = [rid for rid, alvos in grafo.items() if any(a in grafo for a in alvos)]
print(f"Registros cujo alvo concedido TAMBEM concede algo (encadeamento real, "
      f"so contando resolvivel): {len(encadeiam)}")
for rid in encadeiam[:20]:
    nome = por_id.get(rid, {}).get("name", rid)
    alvos_encadeados = [a for a in grafo[rid] if a in grafo]
    print(f"  {rid} ({nome}) -> {alvos_encadeados}")
print()

# 3) DFS para achar a cadeia resolvivel mais longa e ciclos reais
def dfs_maior_cadeia(inicio):
    """Maior caminho simples a partir de `inicio`, evitando repetir no (visitados)."""
    melhor = [inicio]

    def rec(no, caminho, visitados):
        nonlocal melhor
        if len(caminho) > len(melhor):
            melhor = list(caminho)
        for alvo in grafo.get(no, []):
            if alvo in visitados:
                continue
            caminho.append(alvo)
            visitados.add(alvo)
            rec(alvo, caminho, visitados)
            caminho.pop()
            visitados.discard(alvo)

    rec(inicio, [inicio], {inicio})
    return melhor


maior_cadeia_global = []
for rid in grafo:
    c = dfs_maior_cadeia(rid)
    if len(c) > len(maior_cadeia_global):
        maior_cadeia_global = c

print(f"Cadeia RESOLVIVEL mais longa encontrada ({len(maior_cadeia_global)} nos):")
for rid in maior_cadeia_global:
    print(f"  {rid} ({por_id.get(rid, {}).get('name', '?')})")
print()

# 4) ciclos de verdade (A alcanca A de novo) na parte resolvivel do grafo
def achar_ciclo():
    cor = {}  # 0=branco,1=cinza,2=preto
    pilha = []

    def visita(no):
        cor[no] = 1
        pilha.append(no)
        for alvo in grafo.get(no, []):
            if cor.get(alvo, 0) == 0:
                res = visita(alvo)
                if res:
                    return res
            elif cor.get(alvo) == 1:
                i = pilha.index(alvo)
                return pilha[i:] + [alvo]
        pilha.pop()
        cor[no] = 2
        return None

    for no in grafo:
        if cor.get(no, 0) == 0:
            res = visita(no)
            if res:
                return res
    return None


ciclo = achar_ciclo()
if ciclo:
    print("CICLO ENCONTRADO na parte resolvivel do grafo:")
    print(" -> ".join(f"{rid}({por_id.get(rid, {}).get('name','?')})" for rid in ciclo))
else:
    print("Nenhum ciclo na parte RESOLVIVEL do grafo (grant_item/grant_feat que "
          "apontam pra id fixo).")
print()

print("NOTA: o caso relatado pelo Igor (ancestral-paragon <-> feat de ancestria) "
      "usa grant_item com uuid DINAMICO (depende da escolha do jogador), que "
      "portanto NAO aparece no grafo resolvivel acima -- so seria fechado em "
      "tempo de execucao, apos o jogador escolher.")
