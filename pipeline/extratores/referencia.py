"""Extrator canonico de REFERENCIA (traits, pericias, divindades, dominios) do
Pathfinder 2e (Waybuilder).

Obedece `specs/2026-07-26-schema-base.md`:

  - envelope com `id`, `kind`, `prov` por campo e `conflitos`
  - `grants_completos` / `requires_parseado` separam o que o app calcula do
    que so exibe (ver `comum.mecanizacao`) -- as 4 kinds daqui nao produzem
    `grants` por natureza, entao `grants_completos` sai sempre `null`
  - "Principio zero": edict/anathema ficam como TEXTO, nunca como predicado

Estas 4 categorias nao tem `requires` nem `level` intrinseco (nao sao
feats/spells), e nao tem rule elements no Foundry -- o Foundry so guarda um
dicionario slug->rotulo pra trait (`src/scripts/config/traits.ts`), sem
mecanica propria. Por isso a precedencia de campo colapsa: AoN vence tudo
(name/traits/rarity/source/text), e e a UNICA fonte de conteudo estrutural
pra divindade/dominio/skill. O Foundry so entra pra completar `license`
(cross-referenciado por titulo de livro, igual feats.py faz).

Fontes:
  - AoN: elasticsearch.aonprd.com/aon/_search, categoria trait/skill/deity/domain
  - Foundry (commit 87f9e5028baaa10b70fdc766260b7886def17e04): so p/ tabela
    livro -> (license, remaster), via packs/pf2e/feats/**/*.json
  - pf2etools (branch dev): checagem cruzada de nomes (terceira opiniao),
    nao contribui campo nenhum -- ver relatorio, secao pf2etools

Somente biblioteca padrao. Ponto de entrada: `extrair() -> list[dict]`.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from collections import Counter, defaultdict

# --------------------------------------------------------------------------
# Caminhos
# --------------------------------------------------------------------------

AQUI = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(AQUI)
PROJETO = os.path.dirname(PIPELINE)
BRUTOS = os.path.join(PIPELINE, "dados_brutos")
SAIDA = os.path.join(PIPELINE, "saida")
RELATORIOS = os.path.join(PIPELINE, "relatorios")

sys.path.insert(0, PIPELINE)
import comum  # noqa: E402

FOUNDRY_COMMIT = "87f9e5028baaa10b70fdc766260b7886def17e04"
_CANDIDATOS_FOUNDRY = [
    os.environ.get("WB_FOUNDRY_PACKS", ""),
    os.path.join(BRUTOS, "foundry", "packs", "pf2e"),
    "/tmp/claude-1000/-mnt-c-Users-igor0/39eadbed-e8eb-4194-8557-74f05193fdc1"
    "/scratchpad/pf2e-research/pf2e/packs/pf2e",
]

AON_URL = "https://elasticsearch.aonprd.com/aon/_search"
AON_HEADERS = {"Content-Type": "application/json", "User-Agent": "waybuilder-extrator/1"}
# Sem User-Agent a resposta do elasticsearch.aonprd.com trava (nao e erro,
# fica pendurada) -- armadilha paga na extracao. Respostas grandes (>150KB)
# tambem sofrem throttling de banda; por isso pagina em blocos pequenos.
HTTP_TIMEOUT = 20
HTTP_SLEEP = 0.15
PAGE_SIZE = 80

AON_FIELDS = {
    "trait": ["id", "name", "category", "rarity", "primary_source", "primary_source_raw",
              "source", "source_raw", "trait", "trait_group", "trait_raw", "summary",
              "resistance", "weakness", "speed", "skill_mod", "remaster_id", "legacy_id",
              "url", "type", "exclude_from_search", "release_date"],
    "skill": ["id", "name", "category", "rarity", "primary_source", "primary_source_raw",
              "source", "attribute", "summary", "remaster_id", "legacy_id", "url", "type",
              "exclude_from_search", "release_date"],
    "deity": ["id", "name", "category", "rarity", "primary_source", "primary_source_raw",
              "source", "alignment", "area_of_concern", "area_of_concern_raw", "attribute",
              "anathema", "edict", "epithet", "divine_font", "domain", "domain_primary",
              "domain_alternate", "favored_weapon", "follower_alignment", "cleric_spell",
              "deity_category", "pantheon", "sanctification", "sanctification_raw",
              "summary", "remaster_id", "legacy_id", "url", "type", "exclude_from_search",
              "release_date"],
    "domain": ["id", "name", "category", "rarity", "primary_source", "primary_source_raw",
               "source", "domain", "domain_spell", "advanced_domain_spell", "apocryphal_spell",
               "advanced_apocryphal_spell", "deity", "summary", "remaster_id", "legacy_id",
               "url", "type", "exclude_from_search", "release_date"],
}

AON_CACHE_FILE = {"trait": "aon_traits.json", "skill": "aon_skills.json",
                   "deity": "aon_deities.json", "domain": "aon_domains.json"}


def _packs_foundry() -> str | None:
    for c in _CANDIDATOS_FOUNDRY:
        if c and os.path.isdir(os.path.join(c, "feats")):
            return c
    return None


# --------------------------------------------------------------------------
# Utilitarios
# --------------------------------------------------------------------------

_NAO_ALNUM = re.compile(r"[^a-z0-9]+")


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().replace("'", "").replace("’", "")
    t = _NAO_ALNUM.sub("-", t).strip("-")
    return t


def chave(nome: str) -> str:
    n = unicodedata.normalize("NFKD", nome or "")
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.lower()
    n = re.sub(r"\s+", " ", n)
    return n.strip(" .")


def _ler_json(caminho):
    with open(caminho, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _andar(raiz):
    for base, _dirs, arqs in os.walk(raiz):
        for a in arqs:
            if a.endswith(".json") and not a.startswith("_"):
                yield os.path.join(base, a)


ATRIBUTOS = {
    "strength": "str", "dexterity": "dex", "constitution": "con",
    "intelligence": "int", "wisdom": "wis", "charisma": "cha",
}


# --------------------------------------------------------------------------
# AoN: busca paginada por categoria, com cache em disco
# --------------------------------------------------------------------------

def _http_post_json(payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(AON_URL, data=body, headers=AON_HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return json.loads(resp.read())


def _fetch_categoria_aon(cat):
    fields = AON_FIELDS[cat]
    todos = []
    frm = 0
    total = None
    size = PAGE_SIZE
    while total is None or frm < total:
        payload = {"track_total_hits": True, "size": size, "from": frm, "_source": fields,
                   "query": {"bool": {"must": [{"match_phrase": {"category": cat}}]}}}
        tentativa = 0
        while True:
            tentativa += 1
            try:
                data = _http_post_json(payload)
                break
            except Exception as exc:
                print(f"  [aon:{cat}] from={frm} tentativa {tentativa} falhou: {exc}",
                      file=sys.stderr)
                if tentativa >= 5:
                    if size > 10:
                        size = max(10, size // 2)
                        payload["size"] = size
                        tentativa = 0
                    else:
                        raise
                time.sleep(1.0)
        total = data["hits"]["total"]["value"]
        hits = [{**h["_source"], "_id": h["_id"]} for h in data["hits"]["hits"]]
        if not hits:
            break
        todos.extend(hits)
        frm += len(hits)
        time.sleep(HTTP_SLEEP)
    return todos


def carregar_aon_categoria(cat):
    cache_file = os.path.join(BRUTOS, AON_CACHE_FILE[cat])
    if os.path.exists(cache_file):
        return _ler_json(cache_file)
    print(f"[referencia] cache miss, buscando '{cat}' no AoN ao vivo...", file=sys.stderr)
    hits = _fetch_categoria_aon(cat)
    with open(cache_file, "w", encoding="utf-8") as fh:
        json.dump(hits, fh, ensure_ascii=False)
    return hits


# --------------------------------------------------------------------------
# Tabela livro -> (license, remaster), cross-referenciada via Foundry
# --------------------------------------------------------------------------

_PREFIXO_PATHFINDER = re.compile(r"^pathfinder\s+")
_SUFIXO_REMASTERED = re.compile(r"\s*\(remastered\)\s*$")


def _chave_livro(titulo):
    """Normaliza titulo de livro pra casar Foundry ('Pathfinder Player Core')
    com AoN ('Player Core') -- o Foundry prefixa 'Pathfinder ', o AoN nao."""
    k = chave(titulo)
    k = _SUFIXO_REMASTERED.sub("", k)
    k = _PREFIXO_PATHFINDER.sub("", k)
    return k.strip()


# Packs varridos pra tabela livro->licenca. `feats` sozinho so cobre livros
# com feats; trait/deity/domain citam livros de bestiario, GM e deidade
# (Bestiary, GM Core, Divine Mysteries, Gods & Magic) que so aparecem em
# outros packs -- por isso a varredura cobre varios.
_PACKS_PARA_LICENCA = (
    "feats", "spells", "equipment", "deities", "hazards", "actions",
    "class-features", "ancestries", "backgrounds",
)


def construir_licencas_por_livro():
    """Varre varios packs do Foundry coletando `system.publication` por
    TITULO de livro -- nenhuma das 4 categorias desta extracao tem item
    proprio no Foundry com publication completa em volume suficiente (a
    excecao e `deities/`, so ~51 arquivos, tratada a parte em
    construir_licencas_deity())."""
    tabela = {}
    packs = _packs_foundry()
    if not packs:
        print("[referencia] Foundry nao encontrado -- licenca ficara incompleta.",
              file=sys.stderr)
        return tabela
    for nome_pack in _PACKS_PARA_LICENCA:
        raiz = os.path.join(packs, nome_pack)
        if not os.path.isdir(raiz):
            continue
        for caminho in _andar(raiz):
            try:
                d = _ler_json(caminho)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            pub = ((d.get("system") or {}).get("publication") or {})
            titulo, licenca = pub.get("title"), pub.get("license")
            if titulo and licenca:
                tabela.setdefault(_chave_livro(titulo), (licenca, bool(pub.get("remaster"))))
    return tabela


def construir_licencas_deity():
    """Nome de deidade -> (license, remaster, book), direto de
    packs/pf2e/deities/*.json. Mais preciso que cruzar por livro: cobre so
    ~51 das 486 deidades do AoN (Foundry so inclui as "jogaveis"), mas onde
    bate e por NOME, nao por titulo aproximado."""
    tabela = {}
    packs = _packs_foundry()
    if not packs:
        return tabela
    raiz = os.path.join(packs, "deities")
    if not os.path.isdir(raiz):
        return tabela
    for caminho in _andar(raiz):
        try:
            d = _ler_json(caminho)
        except Exception:
            continue
        if not isinstance(d, dict) or not d.get("name"):
            continue
        pub = ((d.get("system") or {}).get("publication") or {})
        if pub.get("license"):
            tabela[chave(d["name"])] = (pub["license"], bool(pub.get("remaster")), pub.get("title"))
    return tabela


def carregar_foundry_deities():
    """chave(nome) -> doc completo do Foundry, pra cobertura mutua (achado
    A10): 6 nomes que existem so no Foundry, sem par no AoN nem por nome
    exato nem normalizado -- Alocer, Chinostes, Norns, Atheists and Free
    Agents, Lissala (The Order of Virtue), The Curtain Call. `_andar` ja
    desce em subdiretorio (deities/ tem 34, um por panteao/categoria) --
    `construir_licencas_deity()` ja lia todos pra tabela de licenca; so
    ninguem promovia o nome pra registro `wb:deity/*` quando faltava no AoN."""
    out = {}
    packs = _packs_foundry()
    if not packs:
        return out
    raiz = os.path.join(packs, "deities")
    if not os.path.isdir(raiz):
        return out
    for caminho in _andar(raiz):
        try:
            d = _ler_json(caminho)
        except Exception:
            continue
        if not isinstance(d, dict) or d.get("type") != "deity" or not d.get("name"):
            continue
        out[chave(d["name"])] = d
    return out


def extrair_deities_foundry_only(foundry_deities, aon_deity_names, domain_slugs, est):
    """Deidades que so existem no Foundry -- mono-fonte (`xref` so com
    `foundry`), legitimo pelo portao 5. `Lissala (The Order of Virtue)` e
    tratada como entidade PROPRIA, distinta de `Lissala` (que o AoN tem):
    mesma convencao de `normalize_name()` em ancestrias.py, que nao derruba
    parenteses porque eles distinguem variantes reais."""
    registros = []
    for k, d in sorted(foundry_deities.items()):
        if k in aon_deity_names:
            continue
        nome = d["name"]
        sl = slug(nome)
        if not sl:
            continue
        s = d.get("system", {}) or {}
        pub = s.get("publication") or {}
        prov = {"name": "foundry"}
        source = None
        if pub.get("title") or pub.get("license"):
            source = {"book": pub.get("title"), "page": None,
                      "license": pub.get("license"), "remaster": bool(pub.get("remaster"))}
            prov["source"] = "foundry"
        grants_completos, requires_parseado = comum.mecanizacao("deity", False, False, False, True)
        reg = {
            "id": f"wb:deity/{sl}",
            "kind": "deity",
            "name": nome,
            "level": None,
            "traits": [],
            "rarity": None,
            "source": source,
            "requires": None,
            "grants": [],
            "text": f"wb:text/deity/{sl}",
            "grants_completos": grants_completos,
            "requires_parseado": requires_parseado,
            "xref": {"foundry": f"Compendium.pf2e.deities.Item.{d.get('_id')}"},
            "prov": prov,
        }
        atributos = [ATRIBUTOS.get(a.lower(), a.lower()) for a in (s.get("attribute") or [])]
        if atributos:
            reg["divine_attribute"] = atributos
            reg["prov"]["divine_attribute"] = "foundry"
        font = s.get("font") or []
        if font:
            reg["divine_font"] = [f.lower() for f in font]
            reg["prov"]["divine_font"] = "foundry"
        doms = s.get("domains") or {}
        doms_primarios, doms_alt = doms.get("primary") or [], doms.get("alternate") or []
        if doms_primarios or doms_alt:
            reg["domains"] = {
                "primary": _refs(doms_primarios, "domain", domain_slugs),
                "alternate": _refs(doms_alt, "domain", domain_slugs),
            }
            reg["prov"]["domains"] = "foundry"
        arma = s.get("weapons") or []
        if arma:
            reg["favored_weapon"] = [f"wb:equipment/{slug(a)}" for a in arma]
            reg["prov"]["favored_weapon"] = "foundry"
        sanct = (s.get("sanctification") or {}).get("what") or []
        if sanct:
            reg["sanctification"] = [x.lower() for x in sanct]
            reg["prov"]["sanctification"] = "foundry"
        registros.append(reg)
    est["deity_so_foundry"] = len(registros)
    return registros


def _fonte(primary_source, primary_source_raw, licencas):
    if not primary_source:
        return None, None
    m = re.search(r"pg\.\s*(\d+)", primary_source_raw or "")
    info = licencas.get(_chave_livro(primary_source))
    src = {"book": primary_source, "page": int(m.group(1)) if m else None}
    if info:
        src["license"], src["remaster"] = info
    else:
        src["license"], src["remaster"] = None, None
    return src, ("foundry(licenca)" if info else None)


# --------------------------------------------------------------------------
# Dedup por nome (legado x remaster) -- mesmo criterio de feats.py/ancestrias.py
# --------------------------------------------------------------------------

def _dedup_por_nome(hits):
    """Agrupa por nome normalizado. Quando ha par legado/remaster (ligados
    por remaster_id/legacy_id), fica so o remaster -- e a linha viva."""
    porchave = defaultdict(list)
    for h in hits:
        porchave[chave(h.get("name") or "")].append(h)
    escolhidos = {}
    homonimos = 0
    for k, grupo in porchave.items():
        if not k:
            continue
        if len(grupo) == 1:
            escolhidos[k] = grupo[0]
            continue
        homonimos += len(grupo) - 1
        remaster = [g for g in grupo if not g.get("remaster_id")]
        escolhidos[k] = remaster[0] if remaster else grupo[0]
    return escolhidos, homonimos


# --------------------------------------------------------------------------
# Extracao por kind
# --------------------------------------------------------------------------

RARIDADES = {"common", "uncommon", "rare", "unique"}


def _envelope(kind, sl, nome, rarity, source, extra_xref=None, hit=None,
              prov_extra=None, text_disponivel=False):
    prov = {"name": "aon", "traits": "aon", "rarity": "aon", "source": "aon"}
    if prov_extra:
        prov.update(prov_extra)
    # trait/skill/deity/domain nao produzem `grants` por natureza (KINDS_SEM_GRANTS)
    # -- `grants_completos` sai null, nunca false. Nenhuma tem pre-requisito.
    grants_completos, requires_parseado = comum.mecanizacao(kind, False, False, False, True)
    reg = {
        "id": f"wb:{kind}/{sl}",
        "kind": kind,
        "name": nome,
        "level": None,
        "traits": [],
        "rarity": rarity,
        "source": source,
        "requires": None,
        "grants": [],
        "text": f"wb:text/{kind}/{sl}" if text_disponivel else None,
        "grants_completos": grants_completos,
        "requires_parseado": requires_parseado,
        "xref": {"aon": hit.get("id")} if hit else {},
        "prov": prov,
    }
    if extra_xref:
        reg["xref"].update(extra_xref)
    if hit and hit.get("remaster_id"):
        reg["remaster_de"] = hit["remaster_id"]
    if hit and hit.get("legacy_id"):
        reg["legado_de"] = hit["legacy_id"]
    return reg


def extrair_traits(hits, licencas, est):
    escolhidos, homonimos = _dedup_por_nome(hits)
    est["trait_homonimos"] = homonimos
    registros = []
    mecanicos = 0
    com_grupo = 0
    for k in sorted(escolhidos):
        h = escolhidos[k]
        nome = h["name"]
        sl = slug(nome)
        if not sl:
            continue
        rarity = (h.get("rarity") or "").lower() or None
        source, motivo = _fonte(h.get("primary_source"), h.get("primary_source_raw"), licencas)
        prov_extra = {"source": motivo} if motivo else {}
        reg = _envelope("trait", sl, nome, rarity, source, hit=h,
                         prov_extra=prov_extra, text_disponivel=bool(h.get("summary")))
        grupos = h.get("trait_group") or []
        if grupos:
            reg["trait_group"] = grupos
            com_grupo += 1
        # Nenhum trait do AoN carrega resistance/weakness/speed/skill_mod
        # preenchidos (campos do schema compartilhado, usados por outras
        # categorias) -- confirmado por varredura: 0/907. Traits sao
        # vocabulario puro; a mecanica mora em quem TEM o trait, nao nele.
        if h.get("resistance") or h.get("weakness") or h.get("speed") or h.get("skill_mod"):
            reg["trait_mecanico"] = True
            mecanicos += 1
        registros.append(reg)
    est["trait_registros"] = len(registros)
    est["trait_com_grupo"] = com_grupo
    est["trait_mecanicos"] = mecanicos
    return registros


def extrair_skills(hits, licencas, est):
    escolhidos, homonimos = _dedup_por_nome(hits)
    est["skill_homonimos"] = homonimos
    registros = []
    for k in sorted(escolhidos):
        h = escolhidos[k]
        nome = h["name"]
        sl = slug(nome)
        if not sl:
            continue
        rarity = (h.get("rarity") or "").lower() or None
        source, motivo = _fonte(h.get("primary_source"), h.get("primary_source_raw"), licencas)
        prov_extra = {"source": motivo} if motivo else {}
        reg = _envelope("skill", sl, nome, rarity, source, hit=h,
                         prov_extra=prov_extra, text_disponivel=bool(h.get("summary")))
        atributos = [ATRIBUTOS.get(a.lower(), a.lower()) for a in (h.get("attribute") or [])]
        if atributos:
            reg["attribute"] = atributos
            reg["prov"]["attribute"] = "aon"
        # As 16 pericias nucleares (Acrobatics..Thievery) tem `attribute`.
        # As entradas sem `attribute` sao exemplos de Lore (Agriculture,
        # Boating...) publicados no Kingmaker AP como skill catalogavel --
        # nao sao pericias novas, sao instancias de "Lore: <tema>".
        reg["lore"] = not bool(atributos)
        registros.append(reg)
    est["skill_registros"] = len(registros)
    est["skill_core"] = sum(1 for r in registros if not r["lore"])
    est["skill_lore_exemplo"] = sum(1 for r in registros if r["lore"])
    return registros


def _refs(nomes, kind, indice_slugs):
    out = []
    for n in nomes or []:
        s = slug(n)
        out.append(f"wb:{kind}/{s}" if s in indice_slugs else n)
    return out


def extrair_domains(hits, licencas, est, deity_slugs):
    escolhidos, homonimos = _dedup_por_nome(hits)
    est["domain_homonimos"] = homonimos
    registros = []
    domain_slugs = {slug(h["name"]) for h in escolhidos.values() if h.get("name")}
    com_spell = 0
    for k in sorted(escolhidos):
        h = escolhidos[k]
        nome = h["name"]
        sl = slug(nome)
        if not sl:
            continue
        rarity = (h.get("rarity") or "").lower() or None
        source, motivo = _fonte(h.get("primary_source"), h.get("primary_source_raw"), licencas)
        prov_extra = {"source": motivo} if motivo else {}
        reg = _envelope("domain", sl, nome, rarity, source, hit=h,
                         prov_extra=prov_extra, text_disponivel=bool(h.get("summary")))
        spells = {}
        for campo_aon, chave_saida in (
            ("domain_spell", "initiate"), ("advanced_domain_spell", "advanced"),
            ("apocryphal_spell", "apocryphal_initiate"),
            ("advanced_apocryphal_spell", "apocryphal_advanced"),
        ):
            v = h.get(campo_aon)
            if v:
                nomes = v if isinstance(v, list) else [v]
                spells[chave_saida] = [f"wb:spell/{slug(n)}" for n in nomes]
        if spells:
            reg["domain_spells"] = spells
            reg["prov"]["domain_spells"] = "aon"
            com_spell += 1
        deidades = h.get("deity") or []
        if deidades:
            reg["deities"] = _refs(deidades, "deity", deity_slugs)
            reg["prov"]["deities"] = "aon"
        registros.append(reg)
    est["domain_registros"] = len(registros)
    est["domain_com_spell"] = com_spell
    est["domain_slugs"] = domain_slugs
    return registros


def extrair_deities(hits, licencas, licencas_deity, est, domain_slugs):
    escolhidos, homonimos = _dedup_por_nome(hits)
    est["deity_homonimos"] = homonimos
    registros = []
    com_font = com_dom = com_attr = com_weapon = com_sanct = 0
    completo = 0
    licenca_direta = 0
    for k in sorted(escolhidos):
        h = escolhidos[k]
        nome = h["name"]
        sl = slug(nome)
        if not sl:
            continue
        rarity = (h.get("rarity") or "").lower() or None
        source, motivo = _fonte(h.get("primary_source"), h.get("primary_source_raw"), licencas)
        direta = licencas_deity.get(chave(nome))
        if direta and source:
            source["license"], source["remaster"] = direta[0], direta[1]
            motivo = "foundry(deities, por nome)"
            licenca_direta += 1
        prov_extra = {"source": motivo} if motivo else {}
        reg = _envelope("deity", sl, nome, rarity, source, hit=h,
                         prov_extra=prov_extra, text_disponivel=bool(h.get("summary")))

        atributos = [ATRIBUTOS.get(a.lower(), a.lower()) for a in (h.get("attribute") or [])]
        if atributos:
            reg["divine_attribute"] = atributos
            reg["prov"]["divine_attribute"] = "aon"
            com_attr += 1

        font = h.get("divine_font") or []
        if font:
            reg["divine_font"] = [f.lower() for f in font]
            reg["prov"]["divine_font"] = "aon"
            com_font += 1

        doms_primarios = h.get("domain_primary") or h.get("domain") or []
        doms_alt = h.get("domain_alternate") or []
        if doms_primarios or doms_alt:
            reg["domains"] = {
                "primary": _refs(doms_primarios, "domain", domain_slugs),
                "alternate": _refs(doms_alt, "domain", domain_slugs),
            }
            reg["prov"]["domains"] = "aon"
            com_dom += 1

        arma = h.get("favored_weapon") or []
        if arma:
            reg["favored_weapon"] = [f"wb:equipment/{slug(a)}" for a in arma]
            reg["prov"]["favored_weapon"] = "aon"
            com_weapon += 1

        sanct = h.get("sanctification") or []
        if sanct:
            reg["sanctification"] = [s.lower() for s in sanct]
            reg["prov"]["sanctification"] = "aon"
            com_sanct += 1

        # Principio zero: edict/anathema sao PROSA, nunca predicado. Alinhamento
        # e "area_of_concern" idem -- contexto pro jogador, mesa resolve.
        if h.get("edict"):
            reg["edict"] = h["edict"]
            reg["prov"]["edict"] = "aon"
        if h.get("anathema"):
            reg["anathema"] = h["anathema"]
            reg["prov"]["anathema"] = "aon"
        if h.get("alignment"):
            reg["alignment"] = h["alignment"]
            reg["prov"]["alignment"] = "aon"
        if h.get("follower_alignment"):
            reg["follower_alignment"] = h["follower_alignment"]
        if h.get("area_of_concern"):
            reg["area_of_concern"] = h["area_of_concern"]
        if h.get("epithet"):
            reg["epithet"] = h["epithet"]
        if h.get("pantheon"):
            reg["pantheon"] = h["pantheon"]
        if h.get("cleric_spell"):
            reg["cleric_spell"] = [f"wb:spell/{slug(s)}" for s in h["cleric_spell"]]

        if atributos and font and (doms_primarios or doms_alt):
            completo += 1
        registros.append(reg)
    est["deity_registros"] = len(registros)
    est["deity_com_font"] = com_font
    est["deity_com_domains"] = com_dom
    est["deity_com_attribute"] = com_attr
    est["deity_com_weapon"] = com_weapon
    est["deity_com_sanctification"] = com_sanct
    est["deity_triplice_completa"] = completo
    est["deity_licenca_direta_foundry"] = licenca_direta
    return registros


# --------------------------------------------------------------------------
# Traits orfaos: citados pelos extratores irmaos, ausentes daqui
# --------------------------------------------------------------------------

def traits_orfaos(trait_slugs):
    usados = Counter()
    fontes = defaultdict(set)
    for nome_arquivo in ("feats.json", "magias.json", "ancestrias.json",
                          "classes.json", "conjuracao.json", "equipamento.json",
                          "companheiros.json"):
        caminho = os.path.join(SAIDA, nome_arquivo)
        if not os.path.exists(caminho):
            continue
        try:
            dados = _ler_json(caminho)
        except Exception:
            continue
        if not isinstance(dados, list):
            continue
        for reg in dados:
            for t in (reg.get("traits") or []):
                ts = slug(t) if not re.match(r"^[a-z0-9-]+$", t or "") else t
                usados[ts] += 1
                fontes[ts].add(nome_arquivo)
    orfaos = {t: n for t, n in usados.items() if t not in trait_slugs}
    return usados, orfaos, fontes


# --------------------------------------------------------------------------
# Extracao principal
# --------------------------------------------------------------------------

ESTATISTICAS = {}


def extrair():
    est = {}

    licencas = construir_licencas_por_livro()
    licencas_deity = construir_licencas_deity()
    est["livros_com_licenca"] = len(licencas)
    est["deities_com_licenca_direta_foundry"] = len(licencas_deity)

    trait_hits = carregar_aon_categoria("trait")
    skill_hits = carregar_aon_categoria("skill")
    deity_hits = carregar_aon_categoria("deity")
    domain_hits = carregar_aon_categoria("domain")
    est["aon_trait_bruto"] = len(trait_hits)
    est["aon_skill_bruto"] = len(skill_hits)
    est["aon_deity_bruto"] = len(deity_hits)
    est["aon_domain_bruto"] = len(domain_hits)

    reg_traits = extrair_traits(trait_hits, licencas, est)
    reg_skills = extrair_skills(skill_hits, licencas, est)

    deity_slugs_prelim = {slug(h["name"]) for h in deity_hits if h.get("name")}
    reg_domains = extrair_domains(domain_hits, licencas, est, deity_slugs_prelim)
    domain_slugs = est["domain_slugs"]
    reg_deities = extrair_deities(deity_hits, licencas, licencas_deity, est, domain_slugs)

    # deities so-Foundry (achado A10): cobertura mutua, mesmo padrao aplicado
    # a heritage/familiar-ability -- o Foundry tem nome que o AoN nao indexa.
    foundry_deities = carregar_foundry_deities()
    aon_deity_names = {chave(h.get("name", "")) for h in deity_hits}
    reg_deities_foundry = extrair_deities_foundry_only(
        foundry_deities, aon_deity_names, domain_slugs, est)
    reg_deities += reg_deities_foundry

    # licenca: cobertura
    todos = reg_traits + reg_skills + reg_domains + reg_deities
    sem_licenca = sum(1 for r in todos if not (r.get("source") or {}).get("license"))
    est["registros_sem_licenca"] = sem_licenca
    est["registros_total"] = len(todos)

    # traits orfaos (citados pelos extratores irmaos, ausentes aqui)
    trait_slugs = {r["name"] and slug(r["name"]) for r in reg_traits}
    trait_slugs.discard(None)
    usados, orfaos, fontes_orfaos = traits_orfaos(trait_slugs)
    est["traits_citados_total"] = len(usados)
    est["traits_orfaos_total"] = len(orfaos)
    est["traits_orfaos_top"] = sorted(orfaos.items(), key=lambda x: -x[1])[:30]
    est["traits_orfaos_fontes"] = {t: sorted(fontes_orfaos[t]) for t, _ in est["traits_orfaos_top"]}

    # pf2etools: checagem cruzada de nomes (nao contribui campo)
    pf_dir = os.path.join(BRUTOS, "pf2etools")
    pf_stats = {}
    for cat, key, arq in (("trait", "trait", "traits.json"), ("deity", "deity", "deities.json"),
                          ("domain", "domain", "domains.json"), ("skill", "skill", "skills.json")):
        caminho = os.path.join(pf_dir, arq)
        if not os.path.exists(caminho):
            continue
        try:
            d = _ler_json(caminho)
            nomes = {chave(x.get("name", "")) for x in d.get(key, [])}
        except Exception:
            continue
        nossos = {chave(r["name"]) for r in
                  {"trait": reg_traits, "deity": reg_deities,
                   "domain": reg_domains, "skill": reg_skills}[cat]}
        pf_stats[cat] = {"pf2etools": len(nomes), "so_pf2etools": len(nomes - nossos),
                         "so_nosso": len(nossos - nomes)}
    est["pf2etools_crosscheck"] = pf_stats

    ESTATISTICAS.clear()
    ESTATISTICAS.update(est)
    return todos


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    registros = extrair()
    os.makedirs(SAIDA, exist_ok=True)
    caminho_saida = os.path.join(SAIDA, "referencia.json")
    with open(caminho_saida, "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=1)

    est = ESTATISTICAS
    por_kind = Counter(r["kind"] for r in registros)
    print("registros por kind:")
    for k in ("trait", "skill", "deity", "domain"):
        print(f"  {k:8s} {por_kind.get(k, 0)}")
    print(f"total ................ {len(registros)}")
    print()
    print(f"traits mecanicos (resistance/weakness/speed/skill_mod): "
          f"{est['trait_mecanicos']}/{est['trait_registros']}")
    print(f"traits com trait_group (taxonomia): "
          f"{est['trait_com_grupo']}/{est['trait_registros']}")
    print(f"skills core / exemplos de lore: {est['skill_core']} / {est['skill_lore_exemplo']}")
    print(f"deities com divine_font: {est['deity_com_font']}/{est['deity_registros']}")
    print(f"deities com domains: {est['deity_com_domains']}/{est['deity_registros']}")
    print(f"deities com attribute: {est['deity_com_attribute']}/{est['deity_registros']}")
    print(f"deities com triplice completa (font+domain+attribute): "
          f"{est['deity_triplice_completa']}/{est['deity_registros']}")
    print(f"registros sem license: {est['registros_sem_licenca']}/{est['registros_total']}")
    print(f"deities com license direta do Foundry (por nome): "
          f"{est['deity_licenca_direta_foundry']}")
    print()
    print(f"traits citados pelos extratores irmaos: {est['traits_citados_total']}")
    print(f"traits orfaos (citados, ausentes aqui): {est['traits_orfaos_total']}")
    for t, n in est["traits_orfaos_top"][:15]:
        print(f"  {n:4d}  {t}  <- {', '.join(est['traits_orfaos_fontes'][t])}")

    with open(os.path.join(SAIDA, "_referencia_estatisticas.json"), "w", encoding="utf-8") as fh:
        ser = dict(est)
        ser["traits_orfaos_top"] = [[t, n] for t, n in ser["traits_orfaos_top"]]
        ser["domain_slugs"] = sorted(ser.get("domain_slugs") or [])
        json.dump(ser, fh, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
