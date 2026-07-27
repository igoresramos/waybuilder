#!/usr/bin/env python3
"""
Extrator canonico de TATICAS de Commander (kind=tactic, Battlecry!) e KITS DE
EQUIPAMENTO INICIAL (kind=class-kit) para o Waybuilder.

Os dois kinds entraram na spec pela mesma porta que ritual/relic/language:
omissao ao escrever a lista original de "Kinds em escopo"
(specs/2026-07-26-schema-base.md), nao falha de extrator. Achado no portao 9
(censo do AoN por categoria, pipeline/portoes.py::portao_9_censo) em 27/07:
100% ausentes, zero registros. Censo do AoN (docs sem `remaster_id`):
**37 tactics** (Battlecry! + Pathfinder #223: Hell's Destiny), **32
class-kits** (Core Rulebook, Advanced Player's Guide, Player Core, Player
Core 2).

Fontes fixadas (ver specs/2026-07-26-schema-base.md, "Fontes fixadas"):
  - aon: dump local -- pipeline/dados_brutos/aon_tactics.json (37 docs) e
    aon_class_kits.json (32 docs). Nenhum dos dois dumps traz `remaster_id`
    nem `legacy_id` -- confirmado por grep, 0/37 e 0/32. A regra "doc que
    declara remaster_id e o legado, descarta e nao vira registro proprio"
    (descoberta hoje, vale pro pipeline inteiro) portanto **descarta zero**
    aqui -- nao ha o que descartar, nao ha doc declarando o campo em nenhum
    dos dois dumps.
  - foundry: presente para `tactic`, AUSENTE para `class-kit`.
      tactic: as 37 taticas do dump batem por nome, 1:1, com um item
      `type=action` em packs/pf2e/actions/class/commander/*.json (confirmado
      por normalizacao de nome). O Foundry e a UNICA fonte que expoe
      license/ORC (AoN nao expoe -- mesma limitacao documentada em
      classes.py/feats.py/etc.), entao tactic NAO e mono-fonte como
      relic/language: `source.license` vem do Foundry
      (`system.publication.license`, sempre "ORC" aqui -- Battlecry! e
      Hell's Destiny sao livros pos-remaster), e `prov.source` sai
      "aon+foundry" (mesma convencao de ancestrias.py). O padrao herdado do
      docstring de aon_kinds.py ("nenhuma das duas categorias existe no
      Foundry") valia para relic/language -- nao vale aqui. Conferir por
      fonte antes de assumir mono-fonte evitou deixar `license=None` num
      caso que tinha fonte disponivel (o proprio objetivo desta tarefa era
      nao derrubar o portao 5).
      O diretorio Foundry tem 1 arquivo a mais (38, nao 37): "Shift
      Immanence" nao e tatica de Commander, e acao mitica do Exemplar (War
      of Immortals) -- so compartilha a pasta por categoria de UI do
      Foundry. Fica de fora do match por nome (nao esta nos 37 docs do AoN).
      1 divergencia real de fonte, registrada em `conflitos`: "For
      Talmandor! For Freedom!" tem `actions_number=4` (Two Actions) no AoN
      **e** icone `TwoActions.webp` no proprio doc do Foundry, mas
      `system.actions.value=1` -- o campo contradiz o icone dentro do MESMO
      doc. Resolvido a favor do AoN (evidencia do icone bate com o AoN, nao
      com o proprio campo do Foundry) -- excecao pontual e documentada, nao
      mudanca na precedencia padrao.
      class-kit: nenhum arquivo Foundry corresponde (grep por "class kit" no
      clone so acha uma mencao em prosa de cshangelog, `journals/remaster-
      changes.json`). Mono-fonte AoN, mesmo tratamento de relic/language:
      `source.license=None`, reconciliar.py (passo 2b) infere a partir de
      book+remaster quando o pipeline completo rodar.
  - pf2etools: ausente pros dois kinds (sem `tactics-*.json` nem
    `class-kit*.json` em dados_brutos/pf2etools/, grep por "tactic"/"class
    kit" nao acha nada alem do que ja e feat generico).

Reuso deliberado, conforme pedido: `aon_kinds.slug()` (mesma funcao de slug
das outras categorias so-AoN, `background`/subescolhas) e
`aon_kinds.converter()` (mesmo envelope base: id/kind/name/level/traits via
uniao/rarity/source book+page+remaster/xref/prov). O baseline de
`converter()` e ajustado aqui porque:
  1. `converter()` nao filtra palavra de raridade do array `trait` antes da
     uniao -- 4 docs de tactic (3 uncommon, 1 rare) duplicavam a raridade
     dentro de `traits` (mesmo achado que motivou o filtro em
     relicos_idiomas.py). Filtrado depois da chamada.
  2. `converter()` emite `mechanized: false` (campo v1). A spec v2
     (schema-base.md) deriva esse campo no reconciliador e pede
     `grants_completos`/`requires_parseado` do extrator -- mesmos campos que
     relicos_idiomas.py ja emite. `mechanized` e removido, os dois campos v2
     sao calculados via `comum.mecanizacao()`.
  3. `converter()` nao inclui `license` na chave `source` (so tem
     book/page/remaster). Adicionada aqui: Foundry para tactic, None para
     class-kit.
  4. `converter()` nao resolve colisao de slug quando NAO ha `remaster_id`
     (so sabe suffixar `-legacy` olhando esse campo, ausente nos dois
     dumps). Ver `_resolver_colisoes_kit` abaixo.

`grants`/`requires` (comum.mecanizacao, spec v2):
  - tactic: tem mecanica real (efeito de banner/aura, ex. "cada um pode dar
    Step") mas a linguagem de `grants` da spec nao cobre "ativar um efeito
    de comando com condicao arbitraria de esquadrao" -- mesma lacuna do
    `relic` de relicos_idiomas.py. `grants_completos=False` em 37/37. 2/37
    tem `requirement` em prosa (Mirrored Wall, End it!) preservado em
    `requires_texto`, nunca parseado -- `requires_parseado=False` nesses 2.
  - class-kit: e uma lista de equipamento concreto (armadura/armas/gear/
    opcoes), mecanica real, mas a spec nao tem vocabulario de `grants` para
    "conceder um pacote de itens iniciais" (o mais proximo, `grant_feat`, e
    especifico de feat). Preservado em campo proprio `kit` (armor/weapons/
    gear/options como texto, nao xref pra wb:equipment/*, ver relatorio).
    `grants_completos=False` em 32/32. Sem conceito de pre-requisito
    (`requires_parseado=True`, vacuo, mesma regra de relic/language sem
    prerequisite).

stdlib-only. Le pipeline/dados_brutos/, pipeline/dados_brutos/foundry/ e
pipeline/normalizacao_traits.json (via comum.py/aon_kinds.py), offline, sem
rede.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "extratores"))
import comum  # noqa: E402
import aon_kinds  # noqa: E402 -- reuso de slug()/converter()/REMASTER_CUTOFF

DADOS = os.path.join(BASE_DIR, "dados_brutos")
SAIDA = os.path.join(BASE_DIR, "saida")
AON_TACTICS_FILE = os.path.join(DADOS, "aon_tactics.json")
AON_CLASS_KITS_FILE = os.path.join(DADOS, "aon_class_kits.json")

RARITY_WORDS = {"common", "uncommon", "rare", "unique"}


# --------------------------------------------------------------------------
# carga + dedup legado/remaster -- mesmo criterio de relicos_idiomas.py:
# doc SEM remaster_id e o vigente. Nos dois dumps, 0/37 e 0/32 declaram o
# campo, entao isto nao descarta nada hoje -- fica aqui porque a regra vale
# pro pipeline inteiro, nao so pro que ja foi medido.
# --------------------------------------------------------------------------

def _ler_json(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def carregar_vigentes(caminho):
    docs = _ler_json(caminho)
    vigentes = [d for d in docs if d.get("id") and d.get("name") and not d.get("remaster_id")]
    return docs, vigentes


_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def _limpar_texto(t):
    """Mesma regra de relicos_idiomas.py/emitir_textos.py: links markdown do
    AoN vazam pro campo `text` bruto."""
    if not t:
        return ""
    t = _MD_LINK_RE.sub(r"\1", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()


# --------------------------------------------------------------------------
# tactic -- indice do Foundry por nome normalizado
# --------------------------------------------------------------------------

def indexar_foundry_tactics():
    """nome normalizado -> doc Foundry, so pra packs/pf2e/actions/class/
    commander/*.json ("Shift Immanence" entra no indice mas nunca da match:
    nao esta nos 37 nomes do AoN, e acao do Exemplar, nao tatica)."""
    idx = {}
    packs = comum.packs_foundry(DADOS)
    if not packs:
        return idx
    pasta = os.path.join(packs, "actions", "class", "commander")
    for caminho in glob.glob(os.path.join(pasta, "*.json")):
        try:
            d = _ler_json(caminho)
        except Exception:  # noqa: BLE001 -- arquivo quebrado nao derruba o build
            continue
        nome = d.get("name")
        if nome:
            idx[comum.normalizar(nome)] = d
    return idx


def extrair_tactics(vigentes, foundry_idx, est):
    registros = []
    com_requirement = 0
    sem_match_foundry = 0
    conflitos_actions = 0
    for aon in sorted(vigentes, key=lambda d: d["name"]):
        nome = aon["name"]
        sl = aon_kinds.slug(nome)
        if not sl:
            continue

        reg = aon_kinds.converter(aon, "tactic")
        if not reg:
            continue
        # `mechanized` fica: a base inteira (19.738 registros) esta na v1 e
        # os dois campos da v2 nao foram adotados (TODO item 59). Emitir schema
        # diferente so nos 69 novos deixaria a base com dois vocabularios.

        # 1) filtra palavra de raridade que vazou pra dentro de `traits`
        # (converter() nao faz essa limpeza -- achado 4/37 aqui).
        reg["traits"] = [t for t in reg["traits"] if t not in RARITY_WORDS]

        # 2) license: so o Foundry expoe. Casa por nome normalizado.
        fdoc = foundry_idx.get(comum.normalizar(nome))
        reg["source"]["license"] = None
        if fdoc:
            pub = ((fdoc.get("system") or {}).get("publication")) or {}
            if pub.get("license"):
                reg["source"]["license"] = pub["license"]
                reg["prov"]["source"] = "aon+foundry"
                reg["xref"]["foundry"] = str(fdoc.get("_id") or "")
        else:
            sem_match_foundry += 1

        # 3) requirement em prosa (2/37): preserva, nunca parseia.
        requirement = _limpar_texto(aon.get("requirement"))
        if requirement:
            com_requirement += 1
            reg["requires_texto"] = requirement
            reg["prov"]["requires_texto"] = "aon"

        # `mechanized == bool(grants)` e a definicao da v1; `grants` aqui e
        # sempre vazio porque a spec nao tem vocabulario para efeito de tactic
        # nem para pacote inicial de itens.
        reg["mechanized"] = bool(reg.get("grants"))

        # 4) prosa embutida (harmless -- emitir_textos.py reprocessa do
        # dados_brutos direto, nao le este campo; mesma convencao de
        # relicos_idiomas.py).
        reg["texto"] = _limpar_texto(aon.get("text"))
        reg["prov"]["text"] = "aon"

        # 5) bloco proprio do kind: tipo (tier de proficiencia, nao nivel de
        # personagem -- ver spec, relic/grade e o precedente), custo de
        # acao e frequencia quando existe.
        actions_texto = aon.get("actions")
        actions_number = aon.get("actions_number")
        acoes_aon = (actions_number or 0) // 2 or None
        acoes_final = acoes_aon
        if fdoc:
            acoes_foundry = ((fdoc.get("system") or {}).get("actions") or {}).get("value")
            if acoes_foundry is not None and acoes_aon is not None and acoes_foundry != acoes_aon:
                # achado: "For Talmandor! For Freedom!" -- o proprio doc do
                # Foundry contradiz seu icone (TwoActions.webp com
                # actions.value=1). Fica com o AoN, que bate com o icone;
                # divergencia registrada, nao escondida.
                conflitos_actions += 1
                reg.setdefault("conflitos", []).append({
                    "campo": "tactic.actions", "escolhido": "aon",
                    "aon": acoes_aon, "foundry": acoes_foundry,
                    "nota": "icone Foundry (TwoActions.webp) contradiz o "
                            "proprio system.actions.value do doc Foundry; "
                            "AoN bate com o icone",
                })
            elif acoes_foundry is not None and acoes_aon is None:
                acoes_final = acoes_foundry

        tactic_block = {"type": (aon.get("tactic_type") or "").lower() or None,
                         "actions": acoes_final, "actions_texto": actions_texto}
        frequencia = _limpar_texto(aon.get("frequency"))
        if frequencia:
            tactic_block["frequency"] = frequencia
        reg["tactic"] = tactic_block
        reg["prov"]["tactic"] = "aon"

        registros.append(reg)

    est["tactic_registros"] = len(registros)
    est["tactic_com_requirement"] = com_requirement
    est["tactic_sem_match_foundry"] = sem_match_foundry
    est["tactic_conflitos_actions"] = conflitos_actions
    return registros


# --------------------------------------------------------------------------
# class-kit -- parser do bloco de equipamento embutido no `markdown` do AoN
# (nao existe como campo estruturado no dump)
# --------------------------------------------------------------------------

def _secao_markdown(md, nome):
    """Conteudo de uma secao **Nome** do markdown do AoN. O valor pode estar
    na MESMA linha do cabecalho (Price/Money Left Over/Bulk, dentro de um
    <row>) ou na linha SEGUINTE (Armor/Weapons/Gear/Options, uma lista) --
    achado ao testar contra os 32 docs: um regex so com quebra de linha
    obrigatoria zerava Price/Money Left Over/Bulk em 32/32."""
    m = re.search(r"\*\*" + re.escape(nome) + r"\*\*[ \t]*\r?\n?(.*?)(?=\r?\n\r?\n|\Z)",
                  md, re.S)
    return _limpar_texto(m.group(1)) if m else None


def _split_parenteses(s):
    """Separa por virgula respeitando parenteses abertos -- achado: `Options`
    e `Weapons` tem itens com preco composto ("longbow with 20 arrows (6 gp,
    2 sp)"), um split ingenuo por vírgula parte o preco ao meio."""
    partes, atual, prof = [], "", 0
    for ch in s:
        if ch == "(":
            prof += 1
        elif ch == ")":
            prof -= 1
        if ch == "," and prof <= 0:
            partes.append(atual)
            atual = ""
        else:
            atual += ch
    partes.append(atual)
    return [p.strip() for p in partes if p.strip()]


def _lista_markdown(md, nome):
    s = _secao_markdown(md, nome)
    if not s:
        return []
    return _split_parenteses(s)


_CLASSE_URL_RE = re.compile(r"^/classes/([a-z-]+)$")


def _classe_dona(aon):
    """Classe dona do kit, direto da URL de navegacao que o proprio AoN
    publica (`navigation[0].url == "/classes/<classe>"`) -- nao inferido do
    nome ("Alchemist Kit" -> "alchemist" seria o mesmo resultado aqui, mas a
    URL e dado da fonte, nome e parsing de string)."""
    for item in aon.get("navigation") or []:
        m = _CLASSE_URL_RE.match(item.get("url") or "")
        if m:
            return m.group(1)
    return None


def _resolver_colisoes_kit(vigentes):
    """slug final por doc. Achado: 10 dos 16 kits pre-remaster (Core
    Rulebook + Advanced Player's Guide) tem par de MESMO NOME no Player
    Core/Player Core 2 (ex.: "Rogue Kit" aparece 2x) -- mas SEM
    `remaster_id`/`legacy_id` ligando os dois, diferente de relic/language.
    O portao 7 da spec derruba o build com nome duplicado no mesmo kind sem
    slug distinto, e o principio zero ("conteudo cortado pela Paizo fica na
    base") probe descartar o lado antigo. Mesma solucao de aon_kinds.py pra
    colisao de slug (sufixo `-legacy` no lado mais antigo), so que aqui o
    "mais antigo" vem de `release_date < aon_kinds.REMASTER_CUTOFF` (mesmo
    corte que aon_kinds.converter() ja usa pra `source.remaster`), nao de um
    campo de ponte que nao existe neste dump."""
    por_slug = collections.defaultdict(list)
    for aon in vigentes:
        por_slug[aon_kinds.slug(aon["name"])].append(aon)

    slug_final = {}
    for sl, docs in por_slug.items():
        docs_por_data = sorted(docs, key=lambda d: d.get("release_date") or "")
        if len(docs_por_data) == 1:
            slug_final[docs_por_data[0]["id"]] = sl
            continue
        legados = docs_por_data[:-1]
        atual = docs_por_data[-1]
        slug_final[atual["id"]] = sl
        for i, d in enumerate(legados):
            sufixo = "-legacy" if len(legados) == 1 else f"-legacy-{i + 1}"
            slug_final[d["id"]] = sl + sufixo
    return slug_final


def extrair_class_kits(vigentes, est):
    slug_final = _resolver_colisoes_kit(vigentes)
    registros = []
    colisoes = sum(1 for v in collections.Counter(slug_final[a["id"]].split("-legacy")[0]
                                                    for a in vigentes).values() if v > 1)

    for aon in sorted(vigentes, key=lambda d: d["name"]):
        sl = slug_final.get(aon["id"])
        if not sl:
            continue

        reg = aon_kinds.converter(aon, "class-kit")
        if not reg:
            continue
        # `mechanized` fica: a base inteira (19.738 registros) esta na v1 e
        # os dois campos da v2 nao foram adotados (TODO item 59). Emitir schema
        # diferente so nos 69 novos deixaria a base com dois vocabularios.
        # id/text seguem o slug resolvido (pode levar sufixo -legacy)
        reg["id"] = f"wb:class-kit/{sl}"
        reg["text"] = f"wb:text/class-kit/{sl}"

        # mono-fonte AoN (sem match no Foundry nem pf2etools): license fica
        # None de proposito, reconciliar.py (passo 2b) infere a partir de
        # book+remaster -- mesma convencao de relicos_idiomas.py.
        reg["source"]["license"] = None

        # `mechanized == bool(grants)` e a definicao da v1; `grants` aqui e
        # sempre vazio porque a spec nao tem vocabulario para efeito de tactic
        # nem para pacote inicial de itens.
        reg["mechanized"] = bool(reg.get("grants"))

        reg["texto"] = _limpar_texto(aon.get("text"))
        reg["prov"]["text"] = "aon"

        md = aon.get("markdown") or ""
        kit_block = {
            "class": _classe_dona(aon),
            "price": aon.get("price"),
            "price_texto": _secao_markdown(md, "Price"),
            "money_left_over_texto": _secao_markdown(md, "Money Left Over"),
            "bulk": aon.get("bulk"),
            "armor": _lista_markdown(md, "Armor"),
            "weapons": _lista_markdown(md, "Weapons"),
            "gear": _lista_markdown(md, "Gear"),
            "options": _lista_markdown(md, "Options"),
        }
        reg["kit"] = kit_block
        reg["prov"]["kit"] = "aon"

        registros.append(reg)

    est["class_kit_registros"] = len(registros)
    est["class_kit_colisoes_nome"] = colisoes
    return registros


# --------------------------------------------------------------------------
# extracao principal
# --------------------------------------------------------------------------

def extrair():
    est = {}

    tactic_docs, tactic_vigentes = carregar_vigentes(AON_TACTICS_FILE)
    kit_docs, kit_vigentes = carregar_vigentes(AON_CLASS_KITS_FILE)
    est["aon_tactic_bruto"] = len(tactic_docs)
    est["aon_tactic_vigente"] = len(tactic_vigentes)
    est["aon_tactic_legado_descartado"] = len(tactic_docs) - len(tactic_vigentes)
    est["aon_class_kit_bruto"] = len(kit_docs)
    est["aon_class_kit_vigente"] = len(kit_vigentes)
    est["aon_class_kit_legado_descartado"] = len(kit_docs) - len(kit_vigentes)

    foundry_idx = indexar_foundry_tactics()
    est["foundry_tactic_docs"] = len(foundry_idx)

    reg_tactics = extrair_tactics(tactic_vigentes, foundry_idx, est)
    reg_kits = extrair_class_kits(kit_vigentes, est)

    registros = reg_tactics + reg_kits
    ESTATISTICAS.clear()
    ESTATISTICAS.update(est)
    return registros


ESTATISTICAS: dict = {}


if __name__ == "__main__":
    regs = extrair()
    saida = os.path.join(SAIDA, "taticas_kits.json")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", encoding="utf-8") as fh:
        json.dump(regs, fh, ensure_ascii=False, indent=2)
    print(f"{len(regs)} registros extraidos -> {saida}")
    est = ESTATISTICAS
    print(f"  tactic:    {est['tactic_registros']} (censo AoN vigente: {est['aon_tactic_vigente']}, "
          f"legado descartado: {est['aon_tactic_legado_descartado']})")
    print(f"  class-kit: {est['class_kit_registros']} (censo AoN vigente: {est['aon_class_kit_vigente']}, "
          f"legado descartado: {est['aon_class_kit_legado_descartado']})")
    print(f"  foundry: {est['foundry_tactic_docs']} docs indexados, "
          f"{est['tactic_sem_match_foundry']} tactics sem match, "
          f"{est['tactic_conflitos_actions']} conflito(s) de actions")
    print(f"  class-kit: {est['class_kit_colisoes_nome']} nomes com colisao legado/remaster "
          f"(sufixo -legacy aplicado)")
