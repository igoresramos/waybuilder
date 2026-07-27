#!/usr/bin/env python3
"""
`traits` e uniao das fontes, nao precedencia (specs/2026-07-26-schema-base.md).

Precedencia cabe quando as fontes disputam o mesmo slot com valores
alternativos. `traits` nao e isso: cada fonte descreve uma faceta parcial do
mesmo objeto, entao escolher uma joga fora o que a outra sabia.

Medido: traits respondia por 88% dos 2.299 conflitos da base e quase nenhum era
divergencia real. A escolha destruia dado -- `bastard-sword` guardava
`two-hand` no lugar de `two-hand-d12`, perdendo o dado de dano -- e injetava
nome legado de ancestria (`tiefling`, `ifrit`) numa base remaster-first.

Ordem, conforme a spec:
  1. mapa legado -> remaster; o termo legado vai para `aliases_traits`
  2. absorcao por granularidade: `two-hand-d12` absorve `two-hand`
  3. uniao do que sobrar, ordenada
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
MAPA = os.path.join(AQUI, "normalizacao_traits.json")

_cache = None


def carregar_mapa():
    global _cache
    if _cache is None:
        with open(MAPA) as fh:
            d = json.load(fh)
        _cache = {
            "renomeados": d.get("renomeados") or {},
            "removidos": set(d.get("removidos_sem_sucessor") or []),
            "familias": set((d.get("familias_parametrizadas") or {}).keys()),
        }
    return _cache


def normalizar_termo(t):
    return re.sub(r"\s+", "-", str(t or "").strip().lower())


def unir(valores_por_fonte):
    """{fonte: [traits]} -> (traits_finais, aliases_traits, fontes_que_contribuiram).

    `removidos_sem_sucessor` (escolas de magia, alinhamento) NAO sao descartados:
    o principio "nada e descartado" vale, e num jogo caseiro sem a restricao da
    Paizo eles continuam valendo. Vao para `aliases_traits`.
    """
    mapa = carregar_mapa()
    finais, aliases, fontes = set(), set(), []

    for fonte, lista in sorted(valores_por_fonte.items()):
        if not lista:
            continue
        fontes.append(fonte)
        for bruto in lista:
            t = normalizar_termo(bruto)
            if not t:
                continue
            if t in mapa["renomeados"]:
                aliases.add(t)
                finais.add(mapa["renomeados"][t])
            elif t in mapa["removidos"]:
                aliases.add(t)          # cortado pela Paizo, mantido para a mesa
            else:
                finais.add(t)

    # absorcao por granularidade: o parametrizado engole o base
    for familia in mapa["familias"]:
        if familia in finais and any(
                t != familia and t.startswith(familia + "-") for t in finais):
            finais.discard(familia)

    return sorted(finais), sorted(aliases), fontes


def unir_do_conflito(registro):
    """Refaz a uniao a partir do conflito de `traits` ja registrado.

    Os extratores aplicaram precedencia antes de o reconciliador ver o dado, mas
    gravaram os valores de cada fonte em `conflitos`. Da para reconstruir a
    uniao sem re-rodar extrator nenhum. Devolve True se mudou algo.
    """
    conflitos = registro.get("conflitos") or []
    de_traits = [c for c in conflitos if c.get("campo") == "traits"]
    if not de_traits:
        return False

    por_fonte = {}
    for c in de_traits:
        for chave, valor in c.items():
            if chave in ("campo", "escolhido") or not isinstance(valor, list):
                continue
            por_fonte.setdefault(chave, []).extend(valor)
    # o valor que ficou no registro tambem conta como faceta
    if registro.get("traits"):
        por_fonte.setdefault("_emitido", []).extend(registro["traits"])
    if not por_fonte:
        return False

    finais, aliases, fontes = unir(por_fonte)
    antes = list(registro.get("traits") or [])
    registro["traits"] = finais
    if aliases:
        registro["aliases_traits"] = sorted(set(registro.get("aliases_traits") or []) | set(aliases))
    registro.setdefault("prov", {})["traits"] = [f for f in fontes if f != "_emitido"]
    # a divergencia deixa de ser divergencia: virou uniao
    registro["conflitos"] = [c for c in conflitos if c.get("campo") != "traits"]
    if not registro["conflitos"]:
        registro.pop("conflitos")
    return finais != antes
