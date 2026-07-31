#!/usr/bin/env python3
"""
Extrator canonico de ACOES (kind=action) para o Waybuilder.

O pack `actionspf2e` do Foundry (`packs/pf2e/actions/` em disco) nao era lido
por extrator NENHUM, e nao havia kind `action` na base. Isso nao era catalogo
faltando -- era concessao quebrada em duas classes:

  - as 10 deeds do Gunslinger (`Ten Paces`, `One Shot, One Kill`,
    `Clear a Path`, `Living Fortification`, `Covered Reload`,
    `Raconteur's Reload`, `Reloading Strike`, `Touch and Go`,
    `Spring the Trap`, `Into the Fray`) -- concedidas pelas `Way of X`;
  - `Retributive Strike` e `Liberating Step`, concedidas pelas causas do
    Campeao.

E pior que ausencia: `Into the Fray` RESOLVIA, pelo homonimo
`wb:feat/into-the-fray` -- feat nivel 8, trait `archetype`, do arquetipo Viking.
Quem resolve `GrantItem` por nome com o pack de origem nao lido acerta o alvo
ERRADO em silencio. Por isso `PACK_PARA_KIND` ganha `actionspf2e: action` no
mesmo commit: sem isso, criar o kind PIORA o caso (passa a haver dois
candidatos e a preferencia por `feat` continua vencendo, agora sem nem o
alarme de "nao resolveu").

FONTE PRIMARIA E O FOUNDRY, e nao o AoN -- ao contrario de `tactic`. A
categoria `action` do AoN tem 3.979 docs e mistura acao de ATIVAR ITEM MAGICO
(Treasure Vault e irmaos, 918 citacoes): a populacao nao e a mesma. O AoN entra
so para completar prosa e o par legado/remaster.

SEM `level`, e de proposito: o campo nao existe na fonte, e nenhuma classe
lista acao na sua progressao (zero ocorrencias). O nivel de uma deed vem de
QUEM a concede. Inventar aqui seria arbitrar.

O PACK INTEIRO ENTRA (557), nao so as 317 referenciadas. Cortar por referencia
criaria dependencia de ordem no pipeline (o extrator dependeria de uma varredura
de quem cita quem) e deixaria o portao 9 com sub-regra por pasta em vez de uma
linha removida. O custo esta medido: ~25-39 KB gzip contra nucleo de 0,529 MB.
O item 97 ja fixou que catalogo nao citado nao e defeito.

Spec: specs/2026-07-31-kind-action.md
Medicao: docs/medicoes/2026-07-31_terreno-pack-actions.md
Saida: pipeline/saida/acoes.json
"""
import collections
import glob
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(AQUI)
SAIDA = os.path.join(PIPELINE, "saida")
BRUTOS = os.path.join(PIPELINE, "dados_brutos")

sys.path.insert(0, PIPELINE)
sys.path.insert(0, AQUI)
import comum          # noqa: E402
import traits_uniao   # noqa: E402
import aon_kinds      # noqa: E402

AON_ACTIONS = os.path.join(BRUTOS, "aon_dump", "action.json")

ESTATISTICAS: dict = {}


def _limpar(t) -> str:
    return aon_kinds.limpar(t)


def _docs_foundry():
    raiz = comum.packs_foundry(BRUTOS)
    if not raiz:
        return []
    docs = []
    for f in sorted(glob.glob(os.path.join(raiz, "actions", "**", "*.json"),
                              recursive=True)):
        if os.path.basename(f).startswith("_"):
            continue          # _folders.json nao e conteudo
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and d.get("type") == "action" and d.get("name"):
            d["_pasta"] = os.path.relpath(os.path.dirname(f),
                                          os.path.join(raiz, "actions"))
            docs.append(d)
    return docs


def _indice_aon():
    """Nome normalizado -> doc do AoN, so para completar prosa e o par
    legado/remaster. NAO define a populacao: a categoria `action` do AoN
    mistura acao de item magico, e casar por nome ali traria ruido se ela
    mandasse."""
    if not os.path.exists(AON_ACTIONS):
        return {}
    try:
        bruto = json.load(open(AON_ACTIONS, encoding="utf-8"))
    except Exception:
        return {}
    docs = bruto if isinstance(bruto, list) else (
        bruto.get("docs") or bruto.get("hits") or [])
    idx = {}
    for d in docs:
        if not isinstance(d, dict) or not d.get("name"):
            continue
        # doc que declara `remaster_id` e o LEGADO -- a regra vale para o
        # pipeline inteiro. Fica no indice mesmo assim, porque e ele quem
        # carrega o vinculo; quem escolhe o vigente e o passo de fusao.
        idx.setdefault(comum.normalizar(d["name"]), d)
    return idx


def extrair():
    est = collections.Counter()
    docs = _docs_foundry()
    est["foundry_docs"] = len(docs)
    if not docs:
        print("!! sem repo do Foundry -- extrator de acoes pulado",
              file=sys.stderr)
        ESTATISTICAS.clear()
        ESTATISTICAS.update(est)
        return []

    aon = _indice_aon()
    est["aon_docs_indexados"] = len(aon)

    # colisao de slug: dois docs com o mesmo nome normalizado existem quando a
    # mesma acao tem versao legada e remaster no pack. O legado leva `-legacy`,
    # mesma convencao de `taticas_kits`. Sem isto o segundo sobrescreveria o
    # primeiro em silencio, que e o defeito que o portao 8 existe para pegar.
    por_slug = collections.defaultdict(list)
    for d in docs:
        por_slug[aon_kinds.slug(d["name"])].append(d)

    registros = []
    for sl, grupo in sorted(por_slug.items()):
        if not sl:
            continue
        if len(grupo) > 1:
            est["colisoes_de_slug"] += 1
            # remaster primeiro: ele fica com o slug limpo
            grupo = sorted(grupo, key=lambda d: not (
                ((d.get("system") or {}).get("publication") or {}).get("remaster")))
        for i, d in enumerate(grupo):
            sufixo = "" if i == 0 else f"-legacy{'' if i == 1 else i}"
            registros.append(_registro(d, sl + sufixo, aon, est))

    ESTATISTICAS.clear()
    ESTATISTICAS.update(est)
    return registros


def _registro(d, sl, aon, est) -> dict:
    sistema = d.get("system") or {}
    pub = sistema.get("publication") or {}
    tr = sistema.get("traits") or {}

    traits, aliases_traits, _ = traits_uniao.unir(
        {"foundry": [str(t) for t in (tr.get("value") or [])]})

    doc_aon = aon.get(comum.normalizar(d["name"]))
    if doc_aon:
        est["casaram_com_aon"] += 1

    prov = {
        "name": "foundry",
        "traits": "foundry",
        "rarity": "foundry",
        "source": "foundry",
        "action_type": "foundry",
    }

    texto = _limpar((sistema.get("description") or {}).get("value"))
    if texto:
        prov["text"] = "foundry"
    elif doc_aon and _limpar(doc_aon.get("text")):
        texto = _limpar(doc_aon.get("text"))
        prov["text"] = "aon"
        est["prosa_veio_do_aon"] += 1

    reg = {
        "id": f"wb:action/{sl}",
        "kind": "action",
        "name": d["name"],
        # SEM nivel: a fonte nao tem o campo. Ver o docstring.
        "level": None,
        "traits": traits,
        "rarity": tr.get("rarity") or "common",
        "source": {
            "book": pub.get("title"),
            "page": None,
            "license": pub.get("license"),
            "remaster": bool(pub.get("remaster")),
        },
        "requires": None,
        "grants": [],
        # `mechanized: false` e o caso normal (principio zero): a acao e texto
        # que o jogador resolve na mesa. O que o construtor precisa dela e
        # EXISTIR para ser concedida -- nao calcular o efeito dela.
        "mechanized": False,
        "action_type": (sistema.get("actionType") or {}).get("value"),
        "action_cost": (sistema.get("actions") or {}).get("value"),
        "category": sistema.get("category"),
        "xref": {
            "foundry": str(d.get("_id") or ""),
            "aon": (f"action-{doc_aon['id']}" if doc_aon and
                    not str(doc_aon.get("id", "")).startswith("action-")
                    else (doc_aon or {}).get("id")),
            "pf2etools": None,
        },
        "prov": prov,
        "conflitos": [],
        "texto": texto,
    }
    if aliases_traits:
        reg["aliases_traits"] = aliases_traits
    if reg["category"]:
        prov["category"] = "foundry"

    # A fonte NAO declara rule element de construcao para a acao em si (elas
    # sao o ALVO da concessao, nao a origem dela), entao `None` -- "a fonte nao
    # declarou mecanica" -- e nao `False`, que significaria perda real.
    reg["grants_completos"], reg["requires_parseado"] = comum.mecanizacao(
        "action", False, False, False, False)
    return reg


if __name__ == "__main__":
    regs = extrair()
    os.makedirs(SAIDA, exist_ok=True)
    destino = os.path.join(SAIDA, "acoes.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(regs, fh, ensure_ascii=False, indent=2)
    est = ESTATISTICAS
    print(f"{len(regs)} registros extraidos -> {destino}")
    print(f"  docs no pack do Foundry: {est.get('foundry_docs', 0)}")
    print(f"  colisoes de slug (legado x remaster): {est.get('colisoes_de_slug', 0)}")
    print(f"  casaram por nome com o AoN: {est.get('casaram_com_aon', 0)}"
          f" (indice: {est.get('aon_docs_indexados', 0)})")
    print(f"  prosa vinda do AoN por ausencia no Foundry: {est.get('prosa_veio_do_aon', 0)}")
