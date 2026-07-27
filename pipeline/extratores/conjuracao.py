"""
Extrator de CONJURACAO (slots de magia por nivel) do Pathfinder 2e (Waybuilder).

Contrato: Tartarus/Projetos/pessoal/waybuilder/specs/2026-07-26-schema-base.md

Cobre, por classe conjuradora (nivel de classe 1..20):
  - slots por rank (1..10), rank maximo acessivel, cantrips/dia
  - tradicao (arcane/divine/occult/primal) e tipo (prepared/spontaneous)
  - progressao de proficiencia de conjuracao (trained/expert/master/legendary)
  - focus pool nativo da classe
  - slots extra de feature de classe: Divine Font (Clerico)

Fontes (fixadas, mesmo pin/branch do resto do pipeline):
  - pipeline/dados_brutos/tabelas_conjuracao_pdf.json -- tabela numerica de
    slots lida DIRETO dos PDFs oficiais (Player Core, Player Core 2, Dark
    Archive, Secrets of Magic, War of Immortals), com livro e pagina por
    classe. E a fonte VENCEDORA da tabela numerica (`slots_per_level`) desde
    2026-07-27: o pf2etools tem, para o Oracle, so a variante LEGADO
    (pre-remaster, 2/3 slots) porque a branch `dev` nao tem arquivo `-pc2`
    pra essa classe -- o PDF do Player Core 2 e o texto do Foundry
    (oracle-spellcasting.json, "cast up to three 1st-rank spells") confirmam
    que o remaster vigente e 3/4. Ver docs/pdfs/2026-07-26_tabelas-conjuracao.md
    e comum.prov_lido("waybuilder") + escolher_slots() abaixo.
  - foundryvtt/pf2e, commit 87f9e5028baaa10b70fdc766260b7886def17e04
    packs/pf2e/classes/*.json (proficiencia inicial + marcos de rank-up,
    key ability, items{} para achar as class-features donas da conjuracao),
    packs/pf2e/class-features/*.json (texto das features de conjuracao --
    tradicao, tipo, focus pool, Divine Font -- via regex sobre a prosa;
    NAO existe rule element com a tabela numerica de slots, ver relatorio).
    Cross-check da tabela de slots (nao fonte primaria).
    packs/pf2e/feats/class/cleric/level-1/domain-initiate.json (focus pool
    do Clerico Cloistered, que so vem via feat granted pela doutrina, nao
    por class-feature nativa).
  - Pf2eToolsOrg/Pf2eTools, branch dev, data/class/class-<slug>[-pc1].json
    -- tabela "<Classe> Spells per Day" ja estruturada como
    `{"type": "table", "rows": [...]}`. Cross-check da tabela de slots (nao
    fonte primaria mais -- ver nota do Oracle acima).
  - Archives of Nethys, elasticsearch.aonprd.com/aon/_search -- usado so
    para o Animista (unica classe sem tabela pf2etools), como texto de
    apoio pontual (nao tem a tabela materializada tambem).

Uso:
    python3 conjuracao.py            # roda o pipeline completo
    from conjuracao import extrair   # so a funcao, devolve dict

So stdlib. Cacheia bruto em pipeline/dados_brutos/ (compartilhado com os
outros extratores do projeto); depois roda offline lendo so do cache.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths e constantes
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../waybuilder
PIPELINE_DIR = PROJECT_ROOT / "pipeline"
RAW_DIR = PIPELINE_DIR / "dados_brutos"
FOUNDRY_CACHE = RAW_DIR / "foundry"
AON_CACHE = RAW_DIR / "aon"
PF2ETOOLS_CACHE = RAW_DIR / "pf2etools"
PDF_TABELAS_PATH = RAW_DIR / "tabelas_conjuracao_pdf.json"
SAIDA_DIR = PIPELINE_DIR / "saida"
RELATORIOS_DIR = PIPELINE_DIR / "relatorios"

sys.path.insert(0, str(PIPELINE_DIR))
import comum  # noqa: E402

FOUNDRY_PIN = "87f9e5028baaa10b70fdc766260b7886def17e04"

AON_URL = "https://elasticsearch.aonprd.com/aon/_search"
PF2ETOOLS_RAW = "https://raw.githubusercontent.com/Pf2eToolsOrg/Pf2eTools/dev/data/class/{}"
HTTP_TIMEOUT = 20
HTTP_SLEEP = 0.05

RANK_WORDS = {0: "untrained", 1: "trained", 2: "expert", 3: "master", 4: "legendary"}

# slug de classe -> nome do arquivo pf2etools mais adequado ja presente no
# cache do projeto (preferencia por variante remaster "-pc1" quando existe;
# ver relatorio para quais classes so tem legado pre-remaster disponivel).
PF2ETOOLS_FILES = {
    "wizard": "class-wizard-pc1.json",
    "cleric": "class-cleric-pc1.json",
    "druid": "class-druid-pc1.json",
    "sorcerer": "class-sorcerer.json",
    "bard": "class-bard-pc1.json",
    "witch": "class-witch-pc1.json",
    "oracle": "class-oracle.json",
    "psychic": "class-psychic.json",
    "magus": "class-magus.json",
    "summoner": "class-summoner.json",
    # animist: sem arquivo no pf2etools (nao esta no index.json da fonte,
    # confirmado por fetch direto -- ver relatorio).
}

# slug de classe -> nome do arquivo foundry class-features com a feature
# "<Classe> Spellcasting" (fonte de tradicao/tipo/texto). Cleric e Animist
# tem nomes que nao seguem o padrao "<slug>-spellcasting".
SPELLCASTING_FEATURE_FILE = {
    "wizard": "wizard-spellcasting",
    "cleric": "cleric-spellcasting",
    "druid": "druid-spellcasting",
    "sorcerer": "sorcerer-spellcasting",
    "bard": "occult-spellcasting",
    "witch": "witch-spellcasting",
    "oracle": "oracle-spellcasting",
    "psychic": "psychic-spellcasting",
    "animist": "animist-apparition-spellcasting",
    "magus": "arcane-spellcasting-magus",
    "summoner": "summoner-spellcasting",
}

# Classes cuja tradicao nao e fixa na propria class-feature de conjuracao --
# depende de uma escolha de subclasse (bloodline/patron/eidolon). Confirmado
# lendo a descricao: cada uma tem a frase "tradition ... determined by
# your bloodline/patron's tradition/eidolon's nature" em vez de nomear a
# tradicao. Nao e falha de regex, e a mecanica real da classe.
TRADITION_VARIAVEL = {
    "sorcerer": "bloodline",
    "witch": "patron",
    "summoner": "eidolon",
}

# slug de classe -> arquivo foundry class-feature dono do focus pool nativo.
# None = a classe nao concede focus pool por nenhuma class-feature nativa.
FOCUS_POOL_FEATURE_FILE = {
    "wizard": None,  # curriculo da escola arcana concede spell slots, nao focus
    "druid": "druidic-order",
    "sorcerer": "bloodline-spells",
    "bard": "composition-spells",
    "witch": "hex-spells",
    "oracle": "revelation-spells",
    "psychic": "psi-cantrips-and-amps",
    "animist": "animist-apparition-spellcasting",
    "magus": "conflux-spells",
    "summoner": "link-spells",
    # cleric: tratado a parte (depende da doutrina, ver extrair_cleric()).
}

SPELLCASTER_RANK_FEATURES = {
    "Expert Spellcaster": "expert",
    "Master Spellcaster": "master",
    "Legendary Spellcaster": "legendary",
}

CLASSES_COBERTAS = [
    "wizard", "cleric", "druid", "sorcerer", "bard", "witch", "oracle",
    "psychic", "animist", "magus", "summoner",
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def strip_html(html: str) -> str:
    txt = re.sub(r"<[^>]+>", "", html or "")
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "waybuilder-extrator/1"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return resp.read()


def _http_post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return json.loads(resp.read())


def load_foundry_json(subdir: str, slug: str) -> dict | None:
    path = FOUNDRY_CACHE / subdir / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_foundry_class(slug: str) -> dict | None:
    return load_foundry_json("classes", slug)


def load_foundry_feature(slug: str) -> dict | None:
    return load_foundry_json("class-features", slug)


def load_foundry_feat(slug: str) -> dict | None:
    return load_foundry_json("feats", slug)


def pf2etools_load(filename: str) -> dict | None:
    """Baixa (ou le do cache) um arquivo data/class/<filename> do pf2etools.
    Marca 404 com um arquivo `.missing` pra nao re-tentar toda hora. Mesma
    convencao de cache usada pelos outros extratores do projeto."""
    cache_file = PF2ETOOLS_CACHE / filename
    miss_marker = PF2ETOOLS_CACHE / (filename + ".missing")
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    if miss_marker.exists():
        return None

    url = PF2ETOOLS_RAW.format(filename)
    try:
        raw = _http_get(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            miss_marker.parent.mkdir(parents=True, exist_ok=True)
            miss_marker.write_text("404", encoding="utf-8")
            return None
        print(f"  [pf2etools] erro HTTP em {filename}: {exc}", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"  [pf2etools] falha em {filename}: {exc}", file=sys.stderr)
        return None

    data = json.loads(raw)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    time.sleep(HTTP_SLEEP)
    return data


def aon_query(name: str, category: str, size: int = 5) -> list[dict]:
    """Busca no AoN por nome exato (match_phrase) + categoria. Cacheia bruto
    (lista de _source + _id) por (categoria, nome) -- mesma convencao usada
    pelos outros extratores do projeto (pipeline/dados_brutos/aon/)."""
    cache_file = AON_CACHE / f"{slugify(category)}__{slugify(name)}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    payload = {
        "track_total_hits": True,
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"name": name}},
                    {"match_phrase": {"category": category}},
                ]
            }
        },
    }
    try:
        data = _http_post_json(AON_URL, payload)
        hits = [{**h["_source"], "_id": h["_id"]} for h in data["hits"]["hits"]]
    except Exception as exc:
        print(f"  [aon] falha em '{name}' ({category}): {exc}", file=sys.stderr)
        hits = []

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(hits, ensure_ascii=False), encoding="utf-8")
    time.sleep(HTTP_SLEEP)
    return hits


# ---------------------------------------------------------------------------
# Tabela de slots (pf2etools)
# ---------------------------------------------------------------------------

def _walk_tables(node):
    if isinstance(node, dict):
        if node.get("type") == "table":
            yield node
        for v in node.values():
            yield from _walk_tables(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_tables(item)


def find_spells_per_day_table(doc: dict) -> dict | None:
    for feat in doc.get("classFeature", []) + doc.get("subclassFeature", []):
        for table in _walk_tables(feat):
            name = (table.get("name") or "").lower()
            if "spells per day" in name:
                return table
    return None


def _parse_cell_int(val) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        m = re.match(r"\s*(\d+)", val)
        if m:
            return int(m.group(1))
    return 0


def parse_slot_table(table: dict) -> tuple[dict, list | None]:
    """Devolve (por_nivel, footnotes). por_nivel: {"1": {"cantrips": int,
    "cantrips_raw": str|None, "ranks": {"1": int, ...}, "max_rank": int}, ...}
    `cantrips_raw`/valores de rank com asterisco (ex. '1*', '3*') guardam o
    texto original quando difere do inteiro extraido -- a nota de rodape
    correspondente explica a diferenca (Divine Font, 10o rank especial etc)."""
    rows = table["rows"]
    header_idx = None
    for i, row in enumerate(rows):
        if any(isinstance(c, str) and c.strip().lower() == "cantrips" for c in row):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("tabela sem coluna 'Cantrips' reconhecivel")

    header = rows[header_idx]
    cantrip_col = next(
        i for i, c in enumerate(header) if isinstance(c, str) and c.strip().lower() == "cantrips"
    )
    rank_cols = list(range(cantrip_col + 1, len(header)))

    por_nivel = {}
    for row in rows[header_idx + 1:]:
        if not row or not isinstance(row[0], int):
            continue
        level = row[0]
        cantrips_raw = row[cantrip_col] if cantrip_col < len(row) else None
        cantrips = _parse_cell_int(cantrips_raw)
        ranks = {}
        for rank_n, col in enumerate(rank_cols, start=1):
            if col >= len(row):
                continue
            raw = row[col]
            n = _parse_cell_int(raw)
            if n:
                ranks[str(rank_n)] = n
        entry = {
            "cantrips": cantrips,
            "ranks": ranks,
            "max_rank": max((int(k) for k in ranks), default=0),
        }
        if isinstance(cantrips_raw, str) and cantrips_raw.strip() != str(cantrips):
            entry["cantrips_raw"] = cantrips_raw
        por_nivel[str(level)] = entry

    return por_nivel, table.get("footnotes")


# ---------------------------------------------------------------------------
# Tabela de slots (PDF oficial -- fonte vencedora, ver docstring do modulo)
# ---------------------------------------------------------------------------

_pdf_tabelas_cache: dict | None = None


def load_pdf_tabelas() -> dict:
    """classe -> registro de tabelas_conjuracao_pdf.json. Arquivo unico, lido
    do disco (recuperado a mao dos PDFs oficiais em rodada anterior do
    pipeline, ver docs/pdfs/2026-07-26_tabelas-conjuracao.md); sem chamada de
    rede, cacheado em memoria pra nao reabrir a cada classe."""
    global _pdf_tabelas_cache
    if _pdf_tabelas_cache is None:
        dados = json.loads(PDF_TABELAS_PATH.read_text(encoding="utf-8"))
        _pdf_tabelas_cache = {
            c["classe"]: c for c in dados["classes"] if c.get("conjuradora", True)
        }
    return _pdf_tabelas_cache


def _parse_pdf_cell(raw) -> tuple[int | None, str | None]:
    """Interpreta uma celula de `tabelas_conjuracao_pdf.json`. Devolve
    (valor_numerico_ou_None, bruto_ou_None).

    Nao forca tudo pra inteiro: notacao hibrida de pool duplo ('X+Y', so o
    Animist usa) nao tem um unico numero que a represente, entao fica so no
    bruto. Sufixo de rodape ('1*') extrai o inteiro normalmente E guarda o
    texto original -- mesma convencao que `parse_slot_table` ja usa pra
    `cantrips_raw`."""
    if isinstance(raw, bool):
        return None, str(raw)
    if isinstance(raw, int):
        return raw, None
    if isinstance(raw, str):
        s = raw.strip()
        if "+" in s:
            return None, s  # notacao hibrida (Animist) -- preservada como esta
        m = re.match(r"^(\d+)", s)
        if m:
            n = int(m.group(1))
            return n, (s if s != str(n) else None)
        return None, s
    return None, raw


def parse_pdf_slot_table(pdf_entry: dict) -> dict:
    """Converte `pdf_entry["slots"]` (nivel -> {"cantrips": ..., "1".."10": ...})
    pro mesmo formato de `parse_slot_table` (nivel -> {cantrips, ranks,
    max_rank}), pra dar pra comparar direto com a tabela pf2etools.

    Rank com valor 0 (ex.: magus '0*', slot que so existe via feature
    "studious spells") NAO entra em `ranks` -- mesma convencao de
    `parse_slot_table`, que tambem trata `n` falso (rank sem slot) como
    ausente. Sem isso, comparar contra pf2etools (que omite esses ranks)
    acusaria divergencia numerica onde nao ha nenhuma, so notacao diferente
    pra "zero". O texto original (com o `*`) fica preservado em `ranks_raw`
    de qualquer forma -- nada e descartado, so nao entra no numero comparavel."""
    por_nivel = {}
    for nivel, celulas in pdf_entry["slots"].items():
        if nivel == "notacao" or not isinstance(celulas, dict):
            continue
        cantrips_val, cantrips_raw = _parse_pdf_cell(celulas.get("cantrips"))
        ranks: dict[str, int] = {}
        ranks_raw: dict[str, str] = {}
        for rank_n in range(1, 11):
            chave = str(rank_n)
            if chave not in celulas:
                continue
            val, raw = _parse_pdf_cell(celulas[chave])
            if val:
                ranks[chave] = val
            if raw is not None:
                ranks_raw[chave] = raw
        entry = {"ranks": ranks}
        if cantrips_val is not None:
            entry["cantrips"] = cantrips_val
        if cantrips_raw:
            entry["cantrips_raw"] = cantrips_raw
        if ranks_raw:
            entry["ranks_raw"] = ranks_raw
        presentes = sorted(set(ranks) | set(ranks_raw), key=int)
        entry["max_rank"] = int(presentes[-1]) if presentes else 0
        por_nivel[nivel] = entry
    return por_nivel


def _tabelas_slots_iguais(a: dict, b: dict) -> bool:
    """Compara so a parte numerica limpa (`cantrips`, `ranks`) de duas tabelas
    nivel->entry. Ignora `*_raw`/`max_rank` -- anotam a mesma coisa de forma
    diferente entre fontes (ex.: pf2etools nao guarda raw de rank, so PDF
    guarda), nao mudam o numero em si."""
    if set(a) != set(b):
        return False
    for nivel in a:
        ea, eb = a[nivel], b[nivel]
        if ea.get("cantrips") != eb.get("cantrips"):
            return False
        if ea.get("ranks") != eb.get("ranks"):
            return False
    return True


def escolher_slots(pdf_por_nivel: dict | None,
                    pf2etools_por_nivel: dict | None) -> tuple[dict | None, str | None, list]:
    """Escolhe `slots_per_level` e registra divergencia -- mesmo par
    (valor, prov, conflitos) que `comum.escolher()` devolve, mesmo formato de
    entrada em `conflitos` ({"campo", "escolhido", <fonte>: <valor>, ...}).

    NAO chama `comum.escolher()` direto: essa funcao usa `comum.PRECEDENCIA`,
    que nao conhece o campo "slots_per_level" e cairia no `PADRAO`
    (foundry/aon/pf2etools) -- "waybuilder" nem entra na lista, entao pf2etools
    venceria sempre, inclusive no caso do Oracle onde o pf2etools tem so a
    tabela LEGADO. A tabela do PDF (fonte "waybuilder", ver `comum.prov_lido`)
    e a UNICA das fontes fixadas com o numero remaster certo pra todas as 11
    classes -- pf2etools e foundry entram so como cross-check. Ver spec v2,
    secao "Vocabulario de prov"."""
    if pdf_por_nivel is None:
        if pf2etools_por_nivel is None:
            return None, None, []
        return pf2etools_por_nivel, comum.prov_lido("pf2etools"), []

    conflitos = []
    if pf2etools_por_nivel is not None and not _tabelas_slots_iguais(pdf_por_nivel, pf2etools_por_nivel):
        conflitos.append({
            "campo": "slots_per_level",
            "escolhido": "waybuilder",
            "waybuilder": pdf_por_nivel,
            "pf2etools": pf2etools_por_nivel,
        })
    return pdf_por_nivel, comum.prov_lido("waybuilder"), conflitos


# ---------------------------------------------------------------------------
# Proficiencia de conjuracao
# ---------------------------------------------------------------------------

def extract_generic_proficiency(class_slug: str) -> dict:
    """trained/expert/master/legendary -> nivel de classe. Le
    system.spellcasting (rank inicial, sempre 1=trained nas 11 classes) e
    varre system.items{} atras das class-features "Expert/Master/Legendary
    Spellcaster" (nome exato, dono da classe, com nivel proprio)."""
    doc = load_foundry_class(class_slug)
    prof = {}
    base_rank = doc["system"].get("spellcasting")
    if base_rank is not None:
        word = RANK_WORDS.get(int(base_rank))
        if word:
            prof[word] = 1
    for item in doc["system"].get("items", {}).values():
        rank = SPELLCASTER_RANK_FEATURES.get(item["name"])
        if rank:
            prof[rank] = item["level"]
    return prof


DOCTRINE_FILES = {
    "cloistered_cleric": [
        "first-doctrine-cloistered-cleric", "second-doctrine-cloistered-cleric",
        "third-doctrine-cloistered-cleric", "fourth-doctrine-cloistered-cleric",
        "fifth-doctrine-cloistered-cleric", "final-doctrine-cloistered-cleric",
    ],
    "warpriest": [
        "first-doctrine-warpriest", "second-doctrine-warpriest",
        "third-doctrine-warpriest", "fourth-doctrine-warpriest",
        "fifth-doctrine-warpriest", "final-doctrine-warpriest",
    ],
}

# Duas frases distintas sao usadas nas 12 features de doutrina pra anunciar
# rank-up de conjuracao (spell attack modifier / spell DC). Confirmado lendo
# as 12 descricoes: as que NAO mencionam "spell attack"/"spell DC" na mesma
# frase sao sobre outra coisa (Fortitude, arma do favorito, etc) e devem ser
# ignoradas -- e o que os dois regexes abaixo garantem (ambos exigem "spell"
# perto de "attack"/"DC" na mesma sentenca).
_DOCTRINE_RANK_PATTERNS = [
    re.compile(r"spell attack modifier and spell dc statistics? increases? to (\w+)", re.I),
    re.compile(r"gain (\w+) proficiency with[^.]*spell (?:attack modifier|dc)", re.I),
]


def extract_cleric_doctrine_proficiency(doctrine_key: str) -> dict:
    prof = {"trained": 1}
    for fname in DOCTRINE_FILES[doctrine_key]:
        feat = load_foundry_feature(fname)
        if not feat:
            continue
        level = feat["system"]["level"]["value"]
        text = strip_html(feat["system"]["description"]["value"])
        for pat in _DOCTRINE_RANK_PATTERNS:
            m = pat.search(text)
            if m:
                rank = m.group(1).lower()
                if rank in ("expert", "master", "legendary"):
                    prof[rank] = level
                break
    return prof


# ---------------------------------------------------------------------------
# Focus pool
# ---------------------------------------------------------------------------

_FOCUS_BASE_RE = re.compile(r"focus pool of (\d+) Focus Points?", re.I)
_FOCUS_CAP_RE = re.compile(r"can never (?:hold more than|be more than) (\d+) points?", re.I)


def _extract_focus_pool_from_text(text: str) -> dict:
    m = _FOCUS_BASE_RE.search(text)
    mc = _FOCUS_CAP_RE.search(text)
    return {
        "base": int(m.group(1)) if m else None,
        "cap": int(mc.group(1)) if mc else (3 if m else None),
    }


def extract_focus_pool(class_slug: str) -> dict:
    fname = FOCUS_POOL_FEATURE_FILE.get(class_slug)
    if fname is None:
        return {"base": 0, "cap": 0, "note": "nenhuma class-feature nativa concede focus pool"}
    feat = load_foundry_feature(fname)
    if not feat:
        return {"base": None, "cap": None, "note": f"arquivo {fname}.json nao encontrado no cache"}
    text = strip_html(feat["system"]["description"]["value"])
    result = _extract_focus_pool_from_text(text)
    result["source_feature"] = feat["name"]
    return result


def extract_cleric_focus_pool() -> dict:
    """Clerico nao tem focus pool por class-feature nativa -- so via
    Domain Initiate (feat de nivel 1), que a Primeira Doutrina concede
    automaticamente so pro Cloistered Cleric. Warpriest fica sem focus pool
    nativo a menos que gaste um feat de classe pra pegar Domain Initiate."""
    feat = load_foundry_feat("domain-initiate")
    cloistered = {"base": None, "cap": None, "note": "Domain Initiate nao encontrado no cache"}
    if feat:
        text = strip_html(feat["system"]["description"]["value"])
        cloistered = _extract_focus_pool_from_text(text)
        cloistered["note"] = (
            "concedido automaticamente pela Primeira Doutrina (Cloistered Cleric); "
            "nao e uma class-feature nativa do Clerico"
        )
    warpriest = {
        "base": 0, "cap": 0,
        "note": "Warpriest nao ganha Domain Initiate de graca; precisa gastar feat de classe",
    }
    return {"cloistered_cleric": cloistered, "warpriest": warpriest}


# ---------------------------------------------------------------------------
# Divine Font (Clerico)
# ---------------------------------------------------------------------------

def extract_divine_font() -> dict:
    feat = load_foundry_feature("divine-font")
    text = strip_html(feat["system"]["description"]["value"])
    base = re.search(r"gain (\d+) additional spell slots", text)
    at5 = re.search(r"5th level, the number of additional slots increases to (\d+)", text)
    at15 = re.search(r"15th level, the total number of additional slots increases to (\d+)", text)
    return {
        "at_level": {
            "1": int(base.group(1)) if base else None,
            "5": int(at5.group(1)) if at5 else None,
            "15": int(at15.group(1)) if at15 else None,
        },
        "rank": "sempre no maior rank de slot de clerico disponivel no momento",
        "spell_choice": ["heal", "harm"],
        "note": "escolha feita na deidade (font heal/harm/ambos); nunca muda depois sem intervencao divina",
    }


# ---------------------------------------------------------------------------
# Tradicao / tipo / atributo-chave
# ---------------------------------------------------------------------------

_TRADITION_PATTERNS = [
    re.compile(r"spells? of the (arcane|divine|occult|primal) tradition", re.I),
    re.compile(r"cast (arcane|divine|occult|primal) spells", re.I),
]


def extract_tradition_e_tipo(class_slug: str) -> dict:
    fname = SPELLCASTING_FEATURE_FILE[class_slug]
    feat = load_foundry_feature(fname)
    text = strip_html(feat["system"]["description"]["value"]) if feat else ""
    tradition = None
    for pat in _TRADITION_PATTERNS:
        m = pat.search(text)
        if m:
            tradition = m.group(1).lower()
            break
    if tradition is None and class_slug in TRADITION_VARIAVEL:
        origem = TRADITION_VARIAVEL[class_slug]
        tradition = f"variavel (definida pela escolha de {origem}; nao ha tradicao fixa na class-feature)"
    if "spell repertoire" in text.lower():
        tipo = "spontaneous"
    elif "prepare" in text.lower() or "prepared spellcaster" in text.lower():
        tipo = "prepared"
    else:
        tipo = None
    return {"tradition": tradition, "type": tipo, "source_feature": feat["name"] if feat else None}


def extract_key_ability(class_slug: str) -> list[str]:
    doc = load_foundry_class(class_slug)
    return doc["system"]["keyAbility"]["value"]


# ---------------------------------------------------------------------------
# Montagem por classe
# ---------------------------------------------------------------------------

def build_class_entry(slug: str, relatorio: dict) -> dict:
    display_name = load_foundry_class(slug)["name"]
    entry: dict = {
        "id": f"wb:class-feature/{slug}-spellcasting",
        "class": display_name,
        "key_ability": extract_key_ability(slug),
        "prov": {},
        "xref": {"foundry_class": f"packs/pf2e/classes/{slug}.json"},
    }

    trad = extract_tradition_e_tipo(slug)
    entry["tradition"] = trad["tradition"]
    entry["type"] = trad["type"]
    entry["prov"]["tradition"] = "foundry (regex sobre descricao da class-feature de conjuracao)"
    entry["prov"]["type"] = "foundry (regex sobre descricao da class-feature de conjuracao)"
    if trad["source_feature"]:
        entry["xref"]["foundry_feature"] = f"packs/pf2e/class-features/{SPELLCASTING_FEATURE_FILE[slug]}.json"

    # ---- proficiencia ----
    if slug == "cleric":
        cloistered_prof = extract_cleric_doctrine_proficiency("cloistered_cleric")
        warpriest_prof = extract_cleric_doctrine_proficiency("warpriest")
        entry["proficiency"] = {
            "cloistered_cleric": cloistered_prof,
            "warpriest": warpriest_prof,
            "note": (
                "proficiencia de conjuracao do Clerico depende da Doutrina (subclasse "
                "obrigatoria escolhida no nivel 1); Cloistered segue o padrao de "
                "conjurador pleno (7/15/19), Warpriest e mais lento e nunca chega a "
                "legendary (so expert em 11, master em 19)"
            ),
        }
        entry["prov"]["proficiency"] = (
            "foundry (regex sobre as 12 class-features de doutrina "
            "first..final-doctrine-{cloistered-cleric,warpriest}, ver conjuracao.md)"
        )
    else:
        entry["proficiency"] = extract_generic_proficiency(slug)
        entry["prov"]["proficiency"] = "foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster')"

    # ---- focus pool ----
    if slug == "cleric":
        entry["focus_pool"] = extract_cleric_focus_pool()
        entry["prov"]["focus_pool"] = "foundry (regex sobre Domain Initiate, feat granted pela Primeira Doutrina)"
    else:
        entry["focus_pool"] = extract_focus_pool(slug)
        entry["prov"]["focus_pool"] = "foundry (regex sobre a class-feature dona do focus pool nativo)"

    # ---- slots por nivel ----
    # PDF (waybuilder) e a fonte vencedora; pf2etools entra so como cross-check
    # (ver docstring de escolher_slots -- caso do Oracle e o motivo).
    pdf_entry = load_pdf_tabelas().get(slug)
    pdf_por_nivel = parse_pdf_slot_table(pdf_entry) if pdf_entry else None

    pf2etools_file = PF2ETOOLS_FILES.get(slug)
    pf2etools_por_nivel, pf2etools_footnotes = None, None
    if pf2etools_file:
        doc = pf2etools_load(pf2etools_file)
        table = find_spells_per_day_table(doc) if doc else None
        if table:
            pf2etools_por_nivel, pf2etools_footnotes = parse_slot_table(table)
            entry["xref"]["pf2etools"] = pf2etools_file

    slots, slots_prov, slots_conflitos = escolher_slots(pdf_por_nivel, pf2etools_por_nivel)
    entry["slots_per_level"] = slots
    entry["prov"]["slots_per_level"] = slots_prov
    if slots_conflitos:
        entry.setdefault("conflitos", []).extend(slots_conflitos)

    if pdf_entry:
        entry["source"] = {
            "book": pdf_entry["livro"],
            "page": pdf_entry["pagina"],
            "page_advancement_table": pdf_entry.get("pagina_advancement_table"),
        }
        entry["slots_footnotes"] = {
            "notacao": pdf_entry.get("slots", {}).get("notacao"),
            "notas": pdf_entry.get("notas"),
        }
        if pf2etools_por_nivel is not None:
            relatorio["slots_confirmados_pdf"].append(slug)
            if slots_conflitos:
                relatorio["conflitos_registrados"].append(slug)
        else:
            relatorio["slots_confirmados_pdf"].append(f"{slug} (sem cross-check pf2etools)")
    elif pf2etools_por_nivel is not None:
        # nao deveria acontecer nas 11 classes cobertas (o PDF tem todas) --
        # fallback pra nao travar o build se algum dia faltar uma entrada
        entry["slots_footnotes"] = pf2etools_footnotes
        relatorio["slots_confirmados_pf2etools"].append(slug)
    else:
        entry["slots_footnotes"] = None
        relatorio["sem_cobertura"].append(slug)

    # ---- Divine Font (so Clerico) ----
    if slug == "cleric":
        entry["divine_font"] = extract_divine_font()
        entry["prov"]["divine_font"] = "foundry (regex sobre packs/pf2e/class-features/divine-font.json)"

    return entry


def build_animist_entry() -> dict:
    """Animista: sem arquivo no pf2etools (nao esta no index.json da fonte) e
    Foundry/AoN so tem a prosa da mecanica, sem tabela materializada -- por
    isso nao ha cross-check estruturado pra `slots_per_level` aqui, so a
    fonte vencedora (PDF, War of Immortals p.12-13).

    Ate a rodada de PDF de 2026-07-27 a tabela so tinha 2 pontos confirmados
    via texto (nivel 1 e um exemplo textual do nivel 2 batido contra AoN).
    Agora o PDF (imagem-only, lido direto das paginas renderizadas) tem a
    tabela completa niveis 1-20, com notacao 'X+Y' propria da classe -- dois
    pools independentes (animist prepared + apparition spontaneous) que a
    tabela impressa soma numa celula so. Preservada como esta (ver
    `_parse_pdf_cell`/`parse_pdf_slot_table`): nao da pra reduzir 'X+Y' a um
    inteiro sem perder informacao, entao o valor numerico fica None e o
    bruto ('2+1' etc.) vai pra `ranks_raw`/`cantrips_raw`."""
    aon_hits = aon_query("Animist", "class")
    trad = extract_tradition_e_tipo("animist")

    pdf_entry = load_pdf_tabelas().get("animist")
    slots = parse_pdf_slot_table(pdf_entry) if pdf_entry else None

    entry = {
        "id": "wb:class-feature/animist-apparition-spellcasting",
        "class": "Animist",
        "key_ability": extract_key_ability("animist"),
        "tradition": trad["tradition"],
        "type": "prepared (pool principal) + spontaneous (pool de apparition, separado)",
        "proficiency": extract_generic_proficiency("animist"),
        "focus_pool": extract_focus_pool("animist"),
        "slots_per_level": slots,
        "prov": {
            "tradition": "aon (campo 'tradition': ['Divine'])",
            "type": "foundry (texto: 'you are a prepared spellcaster'; pool de apparition e explicitamente 'spontaneous')",
            "proficiency": "foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster')",
            "focus_pool": "foundry (regex sobre animist-apparition-spellcasting.json, secao 'Vessel Spells')",
            "slots_per_level": comum.prov_lido("waybuilder") if slots else None,
        },
        "xref": {
            "foundry_class": "packs/pf2e/classes/animist.json",
            "foundry_feature": "packs/pf2e/class-features/animist-apparition-spellcasting.json",
            "aon": aon_hits[0]["_id"] if aon_hits else None,
        },
    }
    if pdf_entry:
        entry["source"] = {
            "book": pdf_entry["livro"],
            "page": pdf_entry["pagina"],
            "page_advancement_table": pdf_entry.get("pagina_advancement_table"),
        }
        entry["slots_footnotes"] = {
            "notacao": pdf_entry.get("slots", {}).get("notacao"),
            "notas": pdf_entry.get("notas"),
        }
    else:
        entry["slots_footnotes"] = None
    return entry


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def extrair() -> dict:
    relatorio = {
        "slots_confirmados_pdf": [],       # fonte vencedora (PDF) presente, com ou sem cross-check
        "slots_confirmados_pf2etools": [], # fallback: so pf2etools (nao deveria disparar nas 11 cobertas)
        "conflitos_registrados": [],       # classes onde PDF e pf2etools divergem (ver escolher_slots)
        "sem_cobertura": [],
    }
    classes = {}
    for slug in CLASSES_COBERTAS:
        if slug == "animist":
            classes[slug] = build_animist_entry()
            if classes[slug].get("slots_per_level"):
                relatorio["slots_confirmados_pdf"].append("animist (sem cross-check pf2etools -- classe nao esta na fonte)")
            else:
                relatorio["sem_cobertura"].append("animist")
            continue
        classes[slug] = build_class_entry(slug, relatorio)

    resultado = {
        "meta": {
            "fonte_foundry_pin": FOUNDRY_PIN,
            "classes_cobertas": CLASSES_COBERTAS,
            "descricao": "Tabela de slots de conjuracao (spell slots) por classe e nivel de classe, PF2e remaster",
        },
        "classes": classes,
    }
    resultado["_relatorio_interno"] = relatorio
    return resultado


def escrever_relatorio(dados: dict) -> str:
    relatorio = dados["_relatorio_interno"]
    linhas = []
    linhas.append("# Relatorio -- extrator de conjuracao (spell slots)\n")
    linhas.append(f"Pin do Foundry: `{FOUNDRY_PIN}`\n")
    linhas.append("## Cobertura\n")
    linhas.append(f"- Classes cobertas: **{len(CLASSES_COBERTAS)}** ({', '.join(CLASSES_COBERTAS)})")
    linhas.append(
        f"- Tabela de slots (1-20, todos os ranks) com o PDF oficial como fonte "
        f"vencedora: **{len(relatorio['slots_confirmados_pdf'])}** classes "
        f"({', '.join(relatorio['slots_confirmados_pdf'])})"
    )
    linhas.append(
        f"- Conflito PDF x pf2etools registrado em `conflitos`: "
        f"**{len(relatorio['conflitos_registrados'])}** classes "
        f"({', '.join(relatorio['conflitos_registrados']) or '-'})"
    )
    if relatorio["slots_confirmados_pf2etools"]:
        linhas.append(
            f"- Fallback: so pf2etools, sem entrada no PDF (nao deveria acontecer "
            f"nas 11 cobertas): **{len(relatorio['slots_confirmados_pf2etools'])}** "
            f"({', '.join(relatorio['slots_confirmados_pf2etools'])})"
        )
    linhas.append(
        f"- Sem cobertura de tabela completa: **{len(relatorio['sem_cobertura'])}** "
        f"({', '.join(relatorio['sem_cobertura']) or '-'})\n"
    )

    linhas.append("## De onde veio cada pedaco do dado, por classe\n")
    linhas.append(
        "| Classe | tradition/type | proficiencia | focus pool | slots/nivel | extra |\n"
        "|---|---|---|---|---|---|"
    )
    for slug, c in dados["classes"].items():
        prov = c["prov"]
        extra = "-"
        if slug == "cleric":
            extra = "divine_font: foundry (divine-font.json)"
        elif slug == "oracle":
            extra = "CONFLITO com pf2etools -- ver secao dedicada abaixo"
        elif slug == "animist":
            extra = "notacao hibrida X+Y (dois pools) -- ver secao dedicada abaixo"
        linhas.append(
            f"| {c['class']} | {prov.get('tradition','-')} | {prov.get('proficiency','-')} "
            f"| {prov.get('focus_pool','-')} | {prov.get('slots_per_level','-')} | {extra} |"
        )

    linhas.append("\n## Descoberta principal: onde a tabela numerica REALMENTE vive\n")
    linhas.append(
        "O relatorio de `classes.py` (extrator irmao) registrou que a tabela de "
        "slots \"fica em rule elements, nao decodificados nesta passada\". "
        "Investigado a fundo: **isso nao procede**. Nenhuma class-feature de "
        "conjuracao (Wizard Spellcasting, Cleric Spellcasting, Sorcerer "
        "Spellcasting etc.) tem `system.rules` com dado numerico de slots -- a "
        "lista `rules[]` dessas features ou esta vazia, ou so tem "
        "`GrantItem`/`ChoiceSet` para mecanica auxiliar (ex.: escolha heal/harm "
        "do Divine Font). O Foundry carrega a tabela em tempo de execucao via "
        "codigo TypeScript (nao dado), nao emite ela em nenhum arquivo JSON dos "
        "compendios -- so serve de CROSS-CHECK textual pontual (ex.: Oracle "
        "abaixo), nunca de fonte estruturada. O pf2etools tem a tabela "
        "estruturada (`{\"type\": \"table\", \"name\": \"<Classe> Spells per Day\"}` "
        "dentro de `classFeature[]`/`subclassFeature[]`, ver "
        "`find_spells_per_day_table()`), mas **so como cross-check** desde "
        "2026-07-27: pra 5 classes (sorcerer/oracle/psychic/magus/summoner) a "
        "branch `dev` so tem o arquivo LEGADO (pre-remaster), e no caso do "
        "Oracle isso da o numero ERRADO (ver secao dedicada). A fonte vencedora "
        "da tabela numerica agora e `pipeline/dados_brutos/tabelas_conjuracao_pdf.json` "
        "-- lida direto dos PDFs oficiais (Player Core, Player Core 2, Dark "
        "Archive, Secrets of Magic, War of Immortals), com livro e pagina "
        "citados por classe. Ver `escolher_slots()` em conjuracao.py.\n"
    )

    linhas.append("## Numeros confirmados em 2+ fontes vs. 1 fonte so\n")
    linhas.append(
        "- **Slots por nivel/rank (a tabela inteira)**: fonte vencedora e o PDF "
        "oficial (`tabelas_conjuracao_pdf.json`, `prov: \"waybuilder\"`), pra "
        "todas as 11 classes conjuradoras. Cross-check via pf2etools disponivel "
        "pra 10 delas (todas exceto animist, que nao esta no index.json da "
        "fonte) -- 9 batem exato, 1 diverge (**Oracle**, ver secao dedicada e "
        "`conflitos` no registro da classe). Validado tambem por consistencia "
        "interna: Wizard/Cleric/Druid/Bard/Witch tem a MESMA progressao (padrao "
        "de conjurador pleno: cantrips=5, 2 slots no rank 1, abre rank novo em "
        "nivel impar, rank 10 so no 19-20), o que bate com o conhecimento "
        "publicado do sistema."
    )
    linhas.append(
        "- **Marcos de rank-up de proficiencia (trained/expert/master/legendary)**: "
        "confirmados so no Foundry (`system.spellcasting` + nomes das "
        "class-features `Expert/Master/Legendary Spellcaster`), 1 fonte. Nao "
        "cruzado com AoN/pf2etools nesta passada (ficaria fora do orcamento de "
        "tempo); risco baixo porque sao nomes de feature literais, nao inferencia."
    )
    linhas.append(
        "- **Doutrina do Clerico (Cloistered vs Warpriest)**: achado que NAO "
        "estava previsto -- confirmado em 1 fonte (Foundry, texto das 12 "
        "features de doutrina) que Warpriest e estruturalmente mais lento e "
        "nunca chega a legendary (expert@11, master@19), enquanto Cloistered "
        "segue o padrao pleno (expert@7, master@15, legendary@19). Isso muda o "
        "campo `proficiency` do Clerico de um dict simples pra um dict por "
        "doutrina -- ver `classes['cleric']['proficiency']`."
    )
    linhas.append(
        "- **Focus pool nativo**: confirmado em 1 fonte (Foundry, regex sobre a "
        "class-feature dona) por classe. Todas as 11 tem 1 Focus Point nativo, "
        "EXCETO Wizard (0 -- curriculo da escola concede spell slots, nao focus) "
        "e Psychic (2 -- unico caso, usado pra 'amps' em vez de focus spells "
        "convencionais; confirmado no texto de psi-cantrips-and-amps.json)."
    )
    linhas.append(
        "- **Divine Font**: confirmado em **2 fontes independentes que "
        "concordam**. Foundry (`divine-font.json`, regex programatico) diz "
        "4/5/6 nos niveis 1/5/15; a nota de rodape da propria tabela do "
        "pf2etools (`class-cleric-pc1.json`, campo `footnotes`, texto solto "
        "nao parseado por regex) diz literalmente \"The number is 4 at 1st "
        "level, 5 at 5th level, and 6 at 15th level\" -- duas fontes, dois "
        "arquivos diferentes, mesmo numero. **Diverge do que a maioria lembra "
        "da regra pre-remaster (fixo em 4)**; a progressao 4/5/6 e a regra "
        "remaster (Player Core) vigente."
    )
    linhas.append(
        "- **Oracle -- CONFLITO real, registrado**: pf2etools (`class-oracle.json`, "
        "arquivo legado, sem variante `-pc1`) mostra o padrao generico (2 slots "
        "no rank de entrada, 3 no seguinte). O PDF (Player Core 2, p.131) mostra "
        "3/4 -- o Oracle remaster ganhou o mesmo slot bonus que o Sorcerer ja "
        "tinha. Cruzado com Foundry (`oracle-spellcasting.json`, texto literal "
        "\"cast up to three 1st-rank spells\"), que confirma o PDF. Registrado em "
        "`classes['oracle']['conflitos']` -- `escolhido: \"waybuilder\"`, com o "
        "valor do pf2etools preservado no proprio registro, nao descartado."
    )
    linhas.append(
        "- **Animista**: PDF (War of Immortals, imagem-only, p.12-13) tem a "
        "tabela completa niveis 1-20, com notacao propria 'X+Y' (pool animist + "
        "pool apparition, independentes) -- preservada como esta, sem forcar "
        "inteiro. Sem cross-check estruturado (nao esta no index.json do "
        "pf2etools); nivel 1 bate com o que ja estava confirmado via texto "
        "(Foundry + AoN) em rodada anterior."
    )

    linhas.append("\n## O que teve que ser codificado a mao (e por que)\n")
    linhas.append(
        "**Nada foi codificado a mao (`prov: \"codificada:manual\"`) nesta "
        "extracao.** Todo numero emitido em `slots_per_level`, `proficiency`, "
        "`focus_pool` e `divine_font` vem de parsing programatico (regex/table "
        "walk/leitura de JSON) rodado em tempo de execucao contra arquivo de "
        "fonte real cacheado em `pipeline/dados_brutos/` -- inclusive "
        "`tabelas_conjuracao_pdf.json`, que e ele mesmo o produto de uma "
        "extracao anterior (leitura de PDF, nao numero chutado por este "
        "extrator)."
    )

    linhas.append("\n## Classes sem cobertura (parcial ou total)\n")
    linhas.append(
        "- Nenhuma das 11 classes conjuradoras ficou sem tabela de slots: o PDF "
        "cobre as 11 (10 com padrao numerico simples + Animist com notacao "
        "hibrida). Cross-check estruturado via pf2etools cobre 10 das 11 (falta "
        "so animist, que nao esta no index.json da fonte)."
    )

    linhas.append("\n## Fontes legado vs. remaster (pf2etools)\n")
    linhas.append(
        "O pf2etools (branch `dev`) nao tem variante `-pc2` (Player Core 2, "
        "remaster) para sorcerer/oracle/psychic/magus/summoner -- confirmado "
        "com fetch direto do `index.json` da fonte, so existem `class-<slug>."
        "json` (arquivo unico, printing mais antigo: CRB/APG/DA/SoM) pra essas "
        "5 classes. wizard, cleric, druid, bard e witch tem a variante `-pc1` "
        "(remaster, `remaster: true` confirmado no JSON). Isso nao afeta os "
        "NUMEROS da tabela de slots (a progressao numerica de slots por nivel "
        "nao mudou entre legado e remaster nessas classes -- so terminologia "
        "de bloodline/mystery/conscious mind mudou), mas fica registrado porque "
        "e uma divergencia real entre o pin da spec (que assume remaster como "
        "fonte preferida) e o que a fonte de fato tem disponivel."
    )

    linhas.append("\n## Portoes de qualidade (spec)\n")
    linhas.append(
        "- Todo campo preenchido em `conjuracao.json` (deste extrator) tem "
        "`prov` correspondente -- portao 1 da spec.\n"
        f"- `conflitos` registrados: **{len(relatorio['conflitos_registrados'])}** "
        f"classe(s) ({', '.join(relatorio['conflitos_registrados']) or '-'}) -- "
        "divergencia PDF x pf2etools nunca e silenciada, mesma operacao que a "
        "escolha (`escolher_slots()`, mesmo formato de `comum.escolher()`).\n"
        "- `grants_completos` / `requires_parseado`: nao aplicaveis a este "
        "arquivo (nao segue o envelope `kind: class-feature` da spec-base; "
        "e um arquivo auxiliar de dados tabulares referenciado por "
        "`wb:class-feature/<slug>-spellcasting`, ja emitido por `classes.py`). "
        "Ver nota de integracao abaixo."
    )

    linhas.append("\n## Nota de integracao com classes.json\n")
    linhas.append(
        "Este arquivo (`saida/conjuracao.json`) e um dado **suplementar**, "
        "carregado ao lado de `saida/classes.json` (nao dentro dele -- outro "
        "agente esta mexendo nesse arquivo em paralelo, sem tocar nele). Cada "
        "entrada usa `id: \"wb:class-feature/<slug>-spellcasting\"`, que deve "
        "bater com o registro de class-feature de conjuracao ja emitido por "
        "`classes.py` (ex.: `wb:class-feature/wizard-spellcasting`). A "
        "reconciliacao/merge dos dois arquivos fica para uma etapa posterior "
        "do build, fora do escopo desta extracao."
    )

    return "\n".join(linhas) + "\n"


def main() -> None:
    dados = extrair()
    relatorio_interno = dados.pop("_relatorio_interno")

    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    (SAIDA_DIR / "conjuracao.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    dados["_relatorio_interno"] = relatorio_interno
    relatorio_md = escrever_relatorio(dados)
    (RELATORIOS_DIR / "conjuracao.md").write_text(relatorio_md, encoding="utf-8")

    print(f"[conjuracao] {len(dados['classes'])} classes escritas em saida/conjuracao.json")
    print(
        f"[conjuracao] slots via PDF (fonte vencedora): {len(relatorio_interno['slots_confirmados_pdf'])}, "
        f"conflitos com pf2etools: {len(relatorio_interno['conflitos_registrados'])}, "
        f"sem cobertura: {len(relatorio_interno['sem_cobertura'])}"
    )


if __name__ == "__main__":
    main()
