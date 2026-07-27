"""
Extrator canonico de RELIQUIAS (kind=relic) e IDIOMAS (kind=language) para o
Waybuilder.

Os dois kinds entraram na spec pela mesma porta, na auditoria de 26/07 (ver
docs/2026-07-26_auditoria-ampla.md, secao A4): omissao ao escrever a lista de
"Kinds em escopo" original, nao falha de extrator. Zero registros em 18.176
antes deste extrator. Censo do AoN (docs com `category` igual e sem
`remaster_id`): **122 relics vigentes**, **117 languages vigentes**.

Fontes fixadas (ver specs/2026-07-26-schema-base.md, "Fontes fixadas"):
  - aon:       dump local do Elasticsearch aonprd.com --
               pipeline/dados_brutos/aon_relics.json (219 docs, legado+remaster
               juntos) e aon_languages.json (155 docs, idem). Deduplicados aqui
               via `remaster_id`/`legacy_id`, mesmo criterio dos irmaos.
  - foundry:   AUSENTE pros dois kinds. Confirmado por busca no checkout
               pinado (packs/pf2e/**): nao existe item type "relic" nem
               "language" -- Foundry nao modela nenhum dos dois como item de
               sistema (relic e regra de GM sem rule element; idioma e so um
               CONFIG de enum de string dentro do pf2e system, nunca um Item).
               Ver relatorio, secao "Fontes", pra evidencia da busca.
  - pf2etools: AUSENTE pros dois kinds. Nao ha `relics-*.json` nem
               `languages-*.json` em pipeline/dados_brutos/pf2etools/, e grep
               por "relic"/"language" nos arquivos existentes (_listing.json,
               baseitems.json) nao acha nada.

Consequencia direta: os dois kinds sao **mono-fonte AoN**. Nao ha precedencia
de campo pra aplicar (nada disputa), so leitura direta com `comum.prov_lido
("aon")`. `comum.escolher()` nao entra em jogo por isso -- nao ha candidato
concorrente pra escolher entre.

Estrutura por doc AoN (achado na extracao, ver relatorio):
  - Cada doc de `category=relic` e um UNICO gift (Minor/Major/Grand), nao um
    "relic" completo com os tres graus embutidos -- confirmado batendo nome
    contra grau: 122 vigentes = 122 nomes unicos, zero doc com mais de um
    grau sob o mesmo nome. A trilha de progressao (spec: "gift/aspect:
    minor/major/grand") vive no campo proprio `relic.grade`, derivado do
    campo `type` ("Relic Minor Gift" -> "minor"), e `relic.aspect` (tema
    compartilhado por varios gifts, ex.: 6 gifts sob o aspecto "Air").
  - `category=language` e mais simples: um doc por idioma, sem sub-grau.

`grants_completos`/`requires_parseado` (comum.mecanizacao, spec v2 -- NAO o
campo `mechanized` da v1, que rituais.py ainda usa por ter sido escrito antes
de comum.py existir; ver relatorio):
  - language: em KINDS_SEM_GRANTS (comum.py) -> `grants_completos` sempre
    None ("nao se aplica" -- idioma nao concede nada que o builder calcule).
  - relic: NAO esta em KINDS_SEM_GRANTS. Todo gift TEM mecanica (um efeito de
    "Activate" com dano/beneficio, ex.: "1d12 electricity damage"), mas a
    linguagem de `grants` da spec (proficiency/ability_boost/feat_slot/
    skill_training/hp_per_level/spell_slots/focus_pool/flat_modifier) nao
    cobre "ativar uma habilidade tipo magia com efeito arbitrario" -- e nao
    ha rule element do Foundry pra converter (Foundry nao modela relic).
    Por isso `grants_completos=False` em 100% dos 122: mecanica existe,
    conversao nao foi tentada por falta de vocabulario no DSL. Registrado
    como gap conhecido no relatorio, nao escondido.
  - `requires`: nenhum dos dois kinds produz predicado formal. `language`
    nunca tem pre-requisito (requires_parseado=True vacuo). `relic` tem
    `prerequisite` em 17/122 -- texto preservado em `requires_texto`, nunca
    parseado (nenhum termo da linguagem de predicado da spec -- class_level/
    character_level/ability/proficiency/has/trait/spellcasting_tradition --
    modela propriedade do ITEM como "the relic is a worn item" ou "the relic
    is 5th level or higher"; 6 dos 17 referenciam outro gift pelo nome
    ["creative spark gift"] e poderiam em tese virar `{"has": "wb:relic/..."}`,
    mas isso nao foi tentado -- decisao consciente de nao inventar uso novo
    de operador sem spec, ver relatorio). `requires_parseado=False` nesses 17.

stdlib-only. Le pipeline/dados_brutos/ e pipeline/normalizacao_traits.json
(via comum.py), offline, sem rede.
"""
from __future__ import annotations

import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
import comum  # noqa: E402
DADOS = os.path.join(BASE_DIR, "dados_brutos")
SAIDA = os.path.join(BASE_DIR, "saida")
AON_RELICS_FILE = os.path.join(DADOS, "aon_relics.json")
AON_LANGUAGES_FILE = os.path.join(DADOS, "aon_languages.json")

RARITY_WORDS = {"common", "uncommon", "rare", "unique"}

_GRADE_BY_TYPE = {
    "Relic Minor Gift": "minor",
    "Relic Major Gift": "major",
    "Relic Grand Gift": "grand",
}


# --------------------------------------------------------------------------
# Carga + dedup legado/remaster (mesmo criterio de rituais.py: doc SEM
# remaster_id e o vigente -- e a definicao literal do censo usado na
# auditoria, "category do AoN descontando remaster_id". Nao reusar o
# dedupe_aon_legacy_remaster genérico de rituais.py aqui: achado na extracao
# de language, 4 docs trazem remaster_id=["0"] (sentinela de "removido sem
# sucessor no remaster", id "0" nao existe no arquivo) -- esses SAO
# corretamente excluidos pela regra "sem remaster_id", mas o dedupe generico
# os contava como canonicos por nao resolver o alvo. Ver relatorio.)
# --------------------------------------------------------------------------

def _ler_json(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def _limpar_texto(t):
    """Mesma regra de emitir_textos.py:limpar() -- links markdown do AoN
    vazam pro campo `text` bruto (achado na extracao: 6/117 languages, ex.
    'Aishmayar Source [Pathfinder #218: Titanbane ](/Sources.aspx?ID=274)
    pg. 72'). emitir_textos.py reprocessa a prosa de novo a partir do
    dados_brutos na hora de montar base/text/<kind>.json (nao le este
    campo), mas o `texto` embutido aqui tambem precisa sair limpo -- e o
    que os extratores irmaos entregam."""
    if not t:
        return ""
    t = _MD_LINK_RE.sub(r"\1", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()


def carregar_vigentes(caminho):
    docs = _ler_json(caminho)
    vigentes = [d for d in docs if d.get("id") and d.get("name") and not d.get("remaster_id")]
    return docs, vigentes


# --------------------------------------------------------------------------
# Campos comuns aos dois kinds
# --------------------------------------------------------------------------

def _fonte(aon):
    """source.book/page a partir de primary_source(_raw). Sempre prov aon --
    mono-fonte, nada pra escolher. `license` fica None aqui de proposito: o
    reconciliador (reconciliar.py, passo 4) ja infere license ausente a
    partir de book+remaster com `comum.prov_inferido("waybuilder", "livro")`
    -- e o mesmo caminho que magias.py/rituais.py deixam pros proprios
    registros sem match no Foundry, nao ha motivo pra duplicar a heuristica
    aqui."""
    book = aon.get("primary_source") or (aon.get("source") or [None])[0]
    book = comum.limpar_livro(book)
    page = None
    raw = aon.get("primary_source_raw") or ""
    m = re.search(r"pg\.\s*(\d+)", raw)
    if m:
        page = int(m.group(1))
    # regra ja estabelecida em magias.py/rituais.py: doc COM legacy_id e a
    # versao remaster (a AoN so preenche legacy_id no lado remaster do par).
    is_remaster = bool(aon.get("legacy_id"))
    return {"book": book, "page": page, "license": None, "remaster": is_remaster}


def _aliases(aon):
    return list(aon.get("legacy_name") or [])


def _traits(aon):
    """Uniao (mono-fonte, mas ainda passa pelo mapa legado->remaster e pela
    absorcao por granularidade da spec -- ex.: 'chaotic' em traits de relic
    vira alias sem sucessor, nao emitido). Palavras de raridade sao
    filtradas: o AoN duplica a raridade dentro do array `trait` (ex.:
    "Azata's Grace" tem trait=[..., "uncommon"] com rarity="uncommon"), e
    `rarity` ja e campo proprio do envelope -- mesma regra de merge_traits()
    em rituais.py."""
    brutos = [t for t in (aon.get("trait") or []) if t.lower() not in RARITY_WORDS]
    if not brutos:
        return [], []
    traits, aliases_traits, _ = comum.uniao_traits({"aon": brutos})
    return traits, aliases_traits


# --------------------------------------------------------------------------
# language (KINDS_SEM_GRANTS)
# --------------------------------------------------------------------------

def extrair_languages(vigentes, est):
    registros = []
    sem_prosa_real = 0
    for aon in sorted(vigentes, key=lambda d: d["name"]):
        nome = aon["name"]
        sl = comum.slug_trait(nome)
        if not sl:
            continue
        traits, aliases_traits = _traits(aon)
        rarity = (aon.get("rarity") or "").lower() or None
        source = _fonte(aon)
        texto = _limpar_texto(aon.get("text"))
        if not texto:
            # nao deveria acontecer (0/117 medido), mas o contrato exige
            # `text` sempre preenchido -- sem prosa nenhuma o registro nao
            # pode ser emitido (mesma regra do portao 5, xref/fonte vazia).
            est["sem_texto_descartados"] += 1
            continue
        # achado: a AoN nao traz prosa descritiva pra language, so a linha
        # "<Nome> Source <Livro> pg. N" que o proprio `text` bruto ja e --
        # ver relatorio. Ainda assim satisfaz "text sempre preenchido": o
        # campo tem conteudo real (curto), nao e vazio.
        if len(texto) < 90:
            sem_prosa_real += 1

        prov = {"name": "aon", "source": "aon"}
        if rarity:
            prov["rarity"] = "aon"
        if traits:
            prov["traits"] = "aon"
        aliases = _aliases(aon)
        if aliases:
            prov["aliases"] = "aon"

        grants_completos, requires_parseado = comum.mecanizacao(
            "language", tinha_mecanica=False, perdeu_mecanica=False,
            tem_requires_texto=False, requires_saiu=False)

        xref = {"aon": aon["id"]}
        legacy_id = (aon.get("legacy_id") or [None])[0]
        if legacy_id:
            xref["aon_legacy"] = legacy_id
        if not xref:
            est["xref_vazio_descartados"] += 1
            continue

        registro = {
            "id": f"wb:language/{sl}",
            "kind": "language",
            "name": nome,
            "aliases": aliases,
            "level": None,
            "traits": traits,
            "rarity": rarity,
            "source": source,
            "requires": None,
            "grants": [],
            "text": f"wb:text/language/{sl}",
            "texto": texto,
            "grants_completos": grants_completos,
            "requires_parseado": requires_parseado,
            "xref": xref,
            "prov": prov,
        }
        if aliases_traits:
            registro["aliases_traits"] = aliases_traits
        registros.append(registro)

    est["language_registros"] = len(registros)
    est["language_sem_prosa_real"] = sem_prosa_real
    return registros


# --------------------------------------------------------------------------
# relic (trilha de progressao propria: campo `relic.aspect` + `relic.grade`)
# --------------------------------------------------------------------------

def extrair_relics(vigentes, est):
    registros = []
    com_prereq = 0
    prereq_gift_ref = 0
    for aon in sorted(vigentes, key=lambda d: d["name"]):
        nome = aon["name"]
        sl = comum.slug_trait(nome)
        if not sl:
            continue
        traits, aliases_traits = _traits(aon)
        rarity = (aon.get("rarity") or "").lower() or None
        source = _fonte(aon)
        texto = _limpar_texto(aon.get("text"))
        if not texto:
            est["sem_texto_descartados"] += 1
            continue

        grade = _GRADE_BY_TYPE.get(aon.get("type") or "")
        aspect = [a.lower() for a in (aon.get("aspect") or [])]
        element = [e.lower() for e in (aon.get("element") or [])] or None
        school = (aon.get("school") or "").lower() or None
        relic_block = {"aspect": aspect, "grade": grade}
        if element:
            relic_block["element"] = element
        if school:
            relic_block["school"] = school

        prerequisite = (aon.get("prerequisite") or "").strip() or None
        if prerequisite:
            com_prereq += 1
            if prerequisite.lower().endswith(" gift"):
                prereq_gift_ref += 1

        grants_completos, requires_parseado = comum.mecanizacao(
            "relic", tinha_mecanica=True, perdeu_mecanica=True,
            tem_requires_texto=bool(prerequisite), requires_saiu=False)

        prov = {"name": "aon", "source": "aon", "text": "aon", "relic": "aon"}
        if rarity:
            prov["rarity"] = "aon"
        if traits:
            prov["traits"] = "aon"
        aliases = _aliases(aon)
        if aliases:
            prov["aliases"] = "aon"
        if prerequisite:
            prov["requires_texto"] = "aon"

        xref = {"aon": aon["id"]}
        legacy_id = (aon.get("legacy_id") or [None])[0]
        if legacy_id:
            xref["aon_legacy"] = legacy_id
        if not xref:
            est["xref_vazio_descartados"] += 1
            continue

        registro = {
            "id": f"wb:relic/{sl}",
            "kind": "relic",
            "name": nome,
            "aliases": aliases,
            "level": None,
            "traits": traits,
            "rarity": rarity,
            "source": source,
            "requires": None,
            "grants": [],
            "relic": relic_block,
            "text": f"wb:text/relic/{sl}",
            "texto": texto,
            "grants_completos": grants_completos,
            "requires_parseado": requires_parseado,
            "xref": xref,
            "prov": prov,
        }
        if aliases_traits:
            registro["aliases_traits"] = aliases_traits
        if prerequisite:
            registro["requires_texto"] = prerequisite
        registros.append(registro)

    est["relic_registros"] = len(registros)
    est["relic_com_prereq"] = com_prereq
    est["relic_prereq_gift_ref"] = prereq_gift_ref
    return registros


# --------------------------------------------------------------------------
# Extracao principal
# --------------------------------------------------------------------------

def extrair():
    est = {"sem_texto_descartados": 0, "xref_vazio_descartados": 0}

    relic_docs, relic_vigentes = carregar_vigentes(AON_RELICS_FILE)
    lang_docs, lang_vigentes = carregar_vigentes(AON_LANGUAGES_FILE)
    est["aon_relic_bruto"] = len(relic_docs)
    est["aon_relic_vigente"] = len(relic_vigentes)
    est["aon_language_bruto"] = len(lang_docs)
    est["aon_language_vigente"] = len(lang_vigentes)

    reg_relics = extrair_relics(relic_vigentes, est)
    reg_languages = extrair_languages(lang_vigentes, est)

    registros = reg_relics + reg_languages
    ESTATISTICAS.clear()
    ESTATISTICAS.update(est)
    return registros


ESTATISTICAS: dict = {}


if __name__ == "__main__":
    regs = extrair()
    saida = os.path.join(SAIDA, "relicos_idiomas.json")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", encoding="utf-8") as fh:
        json.dump(regs, fh, ensure_ascii=False, indent=2)
    print(f"{len(regs)} registros extraidos -> {saida}")
    est = ESTATISTICAS
    print(f"  relic:    {est['relic_registros']} (censo AoN vigente: {est['aon_relic_vigente']})")
    print(f"  language: {est['language_registros']} (censo AoN vigente: {est['aon_language_vigente']})")
    if est["sem_texto_descartados"] or est["xref_vazio_descartados"]:
        print(f"  descartados sem texto: {est['sem_texto_descartados']}, "
              f"sem xref: {est['xref_vazio_descartados']}")
