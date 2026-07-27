#!/usr/bin/env python3
"""
Segunda passada, direcionada pelo pedido do Igor (mensagem intermediaria):
"nao e o Ancestral Paragon especificamente -- e se ALGUMA OUTRA coisa no dado
consegue ciclar durante jogo normal". Perguntas:

  1) O grafo RESOLVIVEL (grant_feat/grant_item com alvo fixo, sem uuid
     dinamico) tem ciclo de verdade (>=2 nos), fora dos auto-ciclos triviais
     (A concede A mesmo, que o motor ja poda por posse)?
  2) Qual a cadeia mais funda que ocorre em jogo normal (dedicacao -> feat,
     subclasse -> feature -> spell, etc), olhando SO pro que resolve estatico?

So leitura, nao escreve nada.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(os.path.dirname(AQUI))
INDEX = os.path.join(PROJETO, "pipeline", "base", "index.json")

with open(INDEX, encoding="utf-8") as fh:
    registros = json.load(fh)
por_id = {r["id"]: r for r in registros}


def alvos_de_grant(g: dict):
    alvos = []
    if "grant_feat" in g:
        val = g["grant_feat"]
        lista = val if isinstance(val, list) else [val]
        for v in lista:
            if isinstance(v, str) and v.startswith("wb:") and "{" not in v:
                alvos.append(v)
    if "grant_item" in g:
        gi = g["grant_item"]
        uuid = gi.get("uuid") if isinstance(gi, dict) else gi
        if isinstance(uuid, str) and "{" not in uuid:
            for rid, r in por_id.items():
                xf = (r.get("xref") or {}).get("foundry")
                if xf and uuid in xf:
                    alvos.append(rid)
                    break
    return alvos


grafo = {}
for r in registros:
    alvos = []
    for g in r.get("grants") or []:
        if isinstance(g, dict):
            alvos += alvos_de_grant(g)
    if alvos:
        grafo[r["id"]] = alvos

auto_ciclos = [rid for rid, alvos in grafo.items() if rid in alvos]
print(f"Auto-ciclos (A concede A mesma, trivial -- personagem ja possui a "
      f"origem, entao o motor poda por posse antes de recursar): {len(auto_ciclos)}")
for rid in auto_ciclos:
    print(f"  {rid} ({por_id[rid].get('name')})")
print()

# grafo SEM auto-arestas, pra procurar ciclo de verdade (>=2 nos)
grafo_sem_self = {rid: [a for a in alvos if a != rid] for rid, alvos in grafo.items()}
grafo_sem_self = {rid: alvos for rid, alvos in grafo_sem_self.items() if alvos}


def achar_todos_ciclos():
    cor = {}
    pilha = []
    ciclos = []

    def visita(no):
        cor[no] = 1
        pilha.append(no)
        for alvo in grafo_sem_self.get(no, []):
            if cor.get(alvo, 0) == 0:
                visita(alvo)
            elif cor.get(alvo) == 1:
                i = pilha.index(alvo)
                ciclos.append(pilha[i:] + [alvo])
        pilha.pop()
        cor[no] = 2

    for no in grafo_sem_self:
        if cor.get(no, 0) == 0:
            visita(no)
    return ciclos


ciclos = achar_todos_ciclos()
print(f"Ciclos de verdade (>=2 nos, fora do auto-ciclo trivial) no grafo "
      f"resolvivel inteiro (19705 registros, todos os kinds): {len(ciclos)}")
for c in ciclos:
    print("  " + " -> ".join(f"{rid}({por_id[rid].get('name')})" for rid in c))
print()

# maior cadeia SIMPLES (sem repetir no) no grafo sem auto-arestas
melhor = []


def dfs(no, caminho, visitados):
    global melhor
    if len(caminho) > len(melhor):
        melhor = list(caminho)
    for alvo in grafo_sem_self.get(no, []):
        if alvo in visitados:
            continue
        caminho.append(alvo)
        visitados.add(alvo)
        dfs(alvo, caminho, visitados)
        caminho.pop()
        visitados.discard(alvo)


for rid in grafo_sem_self:
    dfs(rid, [rid], {rid})

print(f"Cadeia mais funda no grafo RESOLVIVEL inteiro (auto-arestas removidas), "
      f"{len(melhor)} nos:")
for rid in melhor:
    r = por_id[rid]
    print(f"  {rid} ({r.get('name')}, kind={r.get('kind')})")
print()

# especifico: feat de ancestria que concede (resolvivel) feat GERAL, e depois
# esse feat geral concede mais alguma coisa (fecharia direcao ancestry->general->?)
gerais_concedidos_por_ancestria = set()
for r in registros:
    if r.get("kind") != "feat" or r.get("feat_category") != "ancestry":
        continue
    for g in r.get("grants") or []:
        if not isinstance(g, dict) or "grant_feat" not in g:
            continue
        alvos = g["grant_feat"]
        alvos = alvos if isinstance(alvos, list) else [alvos]
        for a in alvos:
            if isinstance(a, str) and a in por_id and por_id[a].get("feat_category") == "general":
                gerais_concedidos_por_ancestria.add(a)

print(f"Feats GERAIS concedidos (resolvivel, estatico) por algum feat de "
      f"ancestria: {len(gerais_concedidos_por_ancestria)}")
for gid in sorted(gerais_concedidos_por_ancestria):
    alvos_do_geral = grafo.get(gid, [])
    print(f"  {gid} ({por_id[gid].get('name')}) -- ele proprio concede algo "
          f"mais? {alvos_do_geral or 'NAO (folha)'}")
