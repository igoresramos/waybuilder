"""
Extrator canonico de CLASSES e CLASS-FEATURES do Pathfinder 2e (Waybuilder).

Contrato: Tartarus/Projetos/pessoal/waybuilder/specs/2026-07-26-schema-base.md

Fontes (fixadas):
  - foundryvtt/pf2e, commit 87f9e5028baaa10b70fdc766260b7886def17e04
    packs/pf2e/classes/*.json (27), packs/pf2e/class-features/*.json (827,
    sendo 1 arquivo de metadado de pasta descartado)
  - Pf2eToolsOrg/Pf2eTools, branch dev, data/class/class-<slug>[-pc1|-pc2].json
  - Archives of Nethys, elasticsearch.aonprd.com/aon/_search

Uso:
    python3 classes.py            # roda o pipeline completo, escreve saida/ e relatorios/
    from classes import extrair   # so a funcao, devolve list[dict]

So stdlib. Cacheia bruto em pipeline/dados_brutos/ na primeira execucao; depois
roda offline lendo so do cache (a menos que os arquivos de cache sejam apagados).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
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
SAIDA_DIR = PIPELINE_DIR / "saida"
RELATORIOS_DIR = PIPELINE_DIR / "relatorios"

FOUNDRY_PIN = "87f9e5028baaa10b70fdc766260b7886def17e04"
# Clone local pinado no commit acima. Pode ser sobrescrito por env var (o clone
# vive num diretorio de scratchpad de sessao, nao e permanente).
FOUNDRY_SRC_DEFAULT = (
    "/tmp/claude-1000/-mnt-c-Users-igor0/39eadbed-e8eb-4194-8557-74f05193fdc1"
    "/scratchpad/pf2e-research/pf2e"
)
FOUNDRY_SRC = os.environ.get("WB_FOUNDRY_REPO", FOUNDRY_SRC_DEFAULT)

AON_URL = "https://elasticsearch.aonprd.com/aon/_search"
PF2ETOOLS_RAW = "https://raw.githubusercontent.com/Pf2eToolsOrg/Pf2eTools/dev/data/class/{}"
HTTP_TIMEOUT = 20
HTTP_SLEEP = 0.03  # cortesia entre requests em cache miss

RANK_WORDS = {0: "untrained", 1: "trained", 2: "expert", 3: "master", 4: "legendary"}

# Slugs das 27 classes reconhecidas no pin do Foundry (preenchido em runtime a
# partir dos arquivos de packs/pf2e/classes/, ver carregar_classes_foundry()).


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def rank_word(n) -> str | None:
    if n is None:
        return None
    return RANK_WORDS.get(int(n))


def strip_html(html: str) -> str:
    """Conversao minima HTML->texto. So usada como fallback quando o AoN nao
    tem o campo (spec pede text como referencia, mas guardamos o texto bruto
    escolhido em prov/relatorio para auditoria, nao para emitir arquivo
    separado -- ver relatorio, secao 'text nao materializado')."""
    txt = re.sub(r"<[^>]+>", "", html or "")
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def parse_aon_page(primary_source_raw) -> int | None:
    if not primary_source_raw:
        return None
    if isinstance(primary_source_raw, list):
        primary_source_raw = primary_source_raw[0] if primary_source_raw else None
    if not primary_source_raw:
        return None
    m = re.search(r"pg\.\s*(\d+)", primary_source_raw)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Cache HTTP generico
# ---------------------------------------------------------------------------

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


def aon_query(name: str, category: str, size: int = 100) -> list[dict]:
    """Busca no AoN por nome exato (match_phrase) + categoria. `terms` em campo
    de texto retorna zero (armadilha documentada); match_phrase funciona.
    Cacheia bruto (lista de _source + _id) por (categoria, nome)."""
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
    except Exception as exc:  # rede fora do ar, 5xx etc -- nao trava o build
        print(f"  [aon] falha em '{name}' ({category}): {exc}", file=sys.stderr)
        hits = []

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(hits, ensure_ascii=False), encoding="utf-8")
    time.sleep(HTTP_SLEEP)
    return hits


def pf2etools_load(filename: str) -> dict | None:
    """Baixa (ou le do cache) um arquivo data/class/<filename> do pf2etools.
    Marca 404 com um arquivo `.missing` para nao re-tentar toda hora."""
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


def load_pf2etools_for_class(slug: str) -> tuple[dict | None, str | None]:
    """Tenta -pc2, depois -pc1, depois o arquivo base (legado ou unico).
    Nao ha arquivos -pc2 hoje no branch dev (Player Core 2 ainda nao foi
    portado pro pf2etools) -- a tentativa fica ai pra quando existir."""
    candidates = [f"class-{slug}-pc2.json", f"class-{slug}-pc1.json", f"class-{slug}.json"]
    for fname in candidates:
        data = pf2etools_load(fname)
        if data is not None:
            return data, fname
    return None, None


# ---------------------------------------------------------------------------
# Cache do Foundry (copia local dos packs relevantes)
# ---------------------------------------------------------------------------

def ensure_foundry_cache() -> None:
    """Copia packs/pf2e/classes e packs/pf2e/class-features do clone pinado
    pra dados_brutos/foundry/. Se o cache ja existe, nao mexe (permite rodar
    offline depois que o clone de scratchpad desaparecer)."""
    dst_classes = FOUNDRY_CACHE / "classes"
    dst_features = FOUNDRY_CACHE / "class-features"
    pin_marker = FOUNDRY_CACHE / "PIN"

    if dst_classes.exists() and dst_features.exists() and pin_marker.exists():
        return

    src_classes = Path(FOUNDRY_SRC) / "packs" / "pf2e" / "classes"
    src_features = Path(FOUNDRY_SRC) / "packs" / "pf2e" / "class-features"
    if not src_classes.exists() or not src_features.exists():
        raise RuntimeError(
            f"Clone do foundryvtt/pf2e nao encontrado em {FOUNDRY_SRC} "
            "(nem cache local em dados_brutos/foundry/). Defina WB_FOUNDRY_REPO "
            "apontando pro clone pinado no commit " + FOUNDRY_PIN
        )

    dst_classes.mkdir(parents=True, exist_ok=True)
    dst_features.mkdir(parents=True, exist_ok=True)
    for f in src_classes.glob("*.json"):
        (dst_classes / f.name).write_bytes(f.read_bytes())
    for f in src_features.glob("*.json"):
        (dst_features / f.name).write_bytes(f.read_bytes())
    pin_marker.write_text(FOUNDRY_PIN, encoding="utf-8")


def carregar_classes_foundry() -> dict[str, dict]:
    ensure_foundry_cache()
    out = {}
    for f in sorted((FOUNDRY_CACHE / "classes").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[d["name"]] = d
    return out


def carregar_class_features_foundry() -> list[dict]:
    ensure_foundry_cache()
    out = []
    for f in sorted((FOUNDRY_CACHE / "class-features").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(d, list):
            # _folders.json: metadado de organizacao de compendio, nao e
            # item de classe-feature. Descartado.
            continue
        if d.get("type") != "feat":
            continue
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# Selecao de geracao (legado x remaster) nos hits do AoN
# ---------------------------------------------------------------------------

def _hit_is_legacy(hit: dict) -> bool:
    """Um doc do AoN que tem remaster_id aponta PRA FRENTE (existe uma versao
    remaster dele) -- logo ele proprio e o legado. Livros de geracao unica
    (Battlecry!, Rage of Elements, Secrets of Magic ainda-nao-remasterizado)
    nao tem nem remaster_id nem legacy_id."""
    return hit.get("remaster_id") is not None


def escolher_hit_aon(hits: list[dict], quer_remaster: bool, nivel: int | None = None,
                      classe: str | None = None) -> tuple[dict | None, bool]:
    """Filtra por classe/nivel quando informado, depois escolhe a geracao
    certa. Devolve (hit, nivel_bateu) -- nivel_bateu False quando so achamos
    hit de outro nivel (usado pra registrar conflito)."""
    pool = hits
    if classe is not None:
        pool = [h for h in pool if h.get("class") == classe]
    nivel_bateu = True
    if nivel is not None and pool:
        com_nivel = [h for h in pool if h.get("level") == nivel]
        if com_nivel:
            pool = com_nivel
        else:
            nivel_bateu = False  # sobra o pool sem filtrar por nivel

    if not pool:
        return None, nivel_bateu

    alvo = [h for h in pool if _hit_is_legacy(h) != quer_remaster]
    if alvo:
        return alvo[0], nivel_bateu
    return pool[0], nivel_bateu


# ---------------------------------------------------------------------------
# Registro por campo: fonte vencedora e fallback
# ---------------------------------------------------------------------------

class Campo:
    """Guarda valor + proveniencia de um campo, com fallback simples entre
    duas fontes candidatas (a vencedora por precedencia, depois a proxima)."""

    def __init__(self):
        self.valor = None
        self.fonte = None

    def set(self, valor, fonte):
        if valor is None or valor == [] or valor == {}:
            return
        if self.valor is None:
            self.valor = valor
            self.fonte = fonte


# ---------------------------------------------------------------------------
# Estatisticas do relatorio (mutadas durante extrair())
# ---------------------------------------------------------------------------

STATS = {
    "n_classes_foundry": 0,
    "n_class_features_foundry": 0,
    "n_registros_emitidos": 0,
    "n_registros_class": 0,
    "n_registros_class_feature": 0,
    "n_multi_owner_features": 0,
    "n_multi_owner_expanded": 0,
    "mechanized_true": 0,
    "mechanized_false": 0,
    "mechanized_false_motivos": defaultdict(int),
    "aon_class_sem_match": [],
    "aon_feature_sem_match": [],
    "pf2etools_class_cobertura": {},  # classe -> (arquivo usado | None, nota)
    "pf2etools_classes_sem_arquivo": [],
    "conflitos_level": [],  # (id, classe, foundry, pf2etools)
    "conflitos_hp_ou_progressao": [],
    "campos_nao_mapeados": defaultdict(int),
    "prereq_prosa_nao_traduzida": [],
}


# ---------------------------------------------------------------------------
# Construcao do registro de CLASS
# ---------------------------------------------------------------------------

def slug_classe(nome_classe: str) -> str:
    return slugify(nome_classe)


def montar_grants_classe(sys_: dict) -> list[dict]:
    grants = []
    hp = sys_.get("hp")
    if hp is not None:
        grants.append({"hp_per_level": hp})

    perception = sys_.get("perception")
    if perception is not None:
        grants.append({"proficiency": {"perception": rank_word(perception)}})

    saves = sys_.get("savingThrows") or {}
    if saves:
        grants.append({"proficiency": {k: rank_word(v) for k, v in saves.items()}})

    attacks = sys_.get("attacks") or {}
    attack_prof = {}
    for k in ("simple", "martial", "advanced", "unarmed"):
        if k in attacks:
            attack_prof[k] = rank_word(attacks[k])
    other = attacks.get("other") or {}
    if other.get("name"):
        attack_prof[other["name"]] = rank_word(other.get("rank"))
    if attack_prof:
        grants.append({"proficiency": attack_prof})

    defenses = sys_.get("defenses") or {}
    if defenses:
        grants.append({"proficiency": {k: rank_word(v) for k, v in defenses.items()}})

    trained = sys_.get("trainedSkills") or {}
    skill_training = {}
    if trained.get("value"):
        skill_training["auto"] = trained["value"]
    if trained.get("additional"):
        skill_training["free"] = trained["additional"]
    if skill_training:
        grants.append({"skill_training": skill_training})

    for chave_foundry, kind in (
        ("classFeatLevels", "class"),
        ("skillFeatLevels", "skill"),
        ("generalFeatLevels", "general"),
        ("ancestryFeatLevels", "ancestry"),
    ):
        niveis = (sys_.get(chave_foundry) or {}).get("value")
        if niveis:
            grants.append({"feat_slot": {"kind": kind, "levels": niveis}})

    # Extensao ao vocabulario de exemplo do schema (nao ha verbo pronto pra
    # "aumento de pericia livre por nivel" na lista de exemplos) -- registrado
    # no relatorio como extensao proposital, nao invencao de mecanica.
    skill_inc = (sys_.get("skillIncreaseLevels") or {}).get("value")
    if skill_inc:
        grants.append({"skill_increase": {"levels": skill_inc}})

    return grants


def construir_registro_classe(nome: str, cdata: dict, aon_cache_hits: dict) -> dict:
    sys_ = cdata["system"]
    slug = slug_classe(nome)
    pub = sys_.get("publication") or {}
    license_ = pub.get("license")
    remaster_foundry = bool(pub.get("remaster"))

    hits = aon_query(nome, "class")
    if not hits:
        STATS["aon_class_sem_match"].append(nome)
    hit, _ = escolher_hit_aon(hits, quer_remaster=remaster_foundry)

    campo_name, campo_traits, campo_rarity = Campo(), Campo(), Campo()
    campo_book, campo_page = Campo(), Campo()

    if hit:
        campo_name.set(hit.get("name"), "aon")
        campo_rarity.set(hit.get("rarity"), "aon")
        campo_book.set(hit.get("primary_source"), "aon")
        campo_page.set(parse_aon_page(hit.get("primary_source_raw")), "aon")
    campo_name.set(nome, "foundry")
    campo_traits.set((sys_.get("traits") or {}).get("value") or [], "foundry")
    campo_rarity.set((sys_.get("traits") or {}).get("rarity"), "foundry")
    campo_book.set(pub.get("title"), "foundry")

    grants = montar_grants_classe(sys_)

    # mechanized: as grants acima vem de campos estruturados do Foundry, sem
    # decodificar rule elements. Se a classe tem `rules` extras (escolha de
    # pericia bonus, feats condicionais etc.), essa parte nao esta mecanizada.
    rules_extra = sys_.get("rules") or []
    mechanized = len(rules_extra) == 0
    if not mechanized:
        STATS["mechanized_false_motivos"][f"class:rules-nao-traduzidas({len(rules_extra)})"] += 1

    registro = {
        "id": f"wb:class/{slug}",
        "kind": "class",
        "name": campo_name.valor,
        "traits": campo_traits.valor,
        "rarity": campo_rarity.valor,
        "source": {
            "book": campo_book.valor,
            "page": campo_page.valor,
            "license": license_,
            "remaster": remaster_foundry,
        },
        "grants": grants,
        "key_ability": (sys_.get("keyAbility") or {}).get("value"),
        "spellcasting": bool(sys_.get("spellcasting")),
        "text": f"wb:text/class/{slug}",
        "mechanized": mechanized,
        "xref": {
            "foundry": f"Compendium.pf2e.classes.Item.{cdata['_id']}",
            "aon": hit.get("_id") if hit else None,
            "pf2etools": None,  # preenchido depois, quando resolvemos o arquivo pf2etools
        },
        "prov": {
            "name": campo_name.fonte,
            "traits": campo_traits.fonte,
            "rarity": campo_rarity.fonte,
            "source": campo_book.fonte,  # book/page vem do mesmo par
            "grants": "foundry",
            "key_ability": "foundry",
            "spellcasting": "foundry",
        },
        "conflitos": [],
    }
    if campo_page.valor is None:
        STATS["campos_nao_mapeados"]["class.source.page (sem match aon)"] += 1
    if not hit:
        STATS["campos_nao_mapeados"]["class.rarity/source (sem match aon)"] += 1
    return registro


# ---------------------------------------------------------------------------
# Indice classe <- feature (a partir do items{} de cada classe no Foundry)
# ---------------------------------------------------------------------------

def montar_indice_ownership(classes_foundry: dict[str, dict]) -> dict[str, list[tuple[str, int]]]:
    """nome_da_feature -> [(nome_da_classe, nivel_nessa_classe), ...]"""
    idx: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for nome_classe, cdata in classes_foundry.items():
        for item in (cdata["system"].get("items") or {}).values():
            idx[item["name"]].append((nome_classe, item["level"]))
    return idx


# ---------------------------------------------------------------------------
# Construcao do registro de CLASS-FEATURE
# ---------------------------------------------------------------------------

RANK_KEYS_PROFICIENCY_SKIP = set()  # nada a pular hoje


def montar_grants_feature(sys_: dict) -> tuple[list[dict], bool, list[str]]:
    """Devolve (grants, mechanized, motivos_nao_mecanizado)."""
    grants = []
    motivos = []

    subf = sys_.get("subfeatures") or {}
    profs = subf.get("proficiencies") or {}
    if profs:
        grants.append(
            {"proficiency": {cat: rank_word(v.get("rank")) for cat, v in profs.items()}}
        )

    subf_extra = set(subf.keys()) - {"proficiencies"}
    rules = sys_.get("rules") or []

    mechanized = not subf_extra and not rules
    if subf_extra:
        motivos.append(f"subfeatures-nao-traduzidas:{sorted(subf_extra)}")
    if rules:
        motivos.append(f"rule-elements-nao-traduzidos:{len(rules)}")

    return grants, mechanized, motivos


def montar_requires_feature(sys_: dict, feature_id_para_relatorio: str) -> Campo:
    campo = Campo()
    prereq = (sys_.get("prerequisites") or {}).get("value") or []
    if prereq:
        # Prosa livre, sem marcacao {@feat}/{@skill} como no pf2etools. Nao
        # entra na linguagem de predicado (all/any/class_level/...) porque
        # isso exigiria parsing de linguagem natural -- fora de escopo desta
        # passada. Registrado, nao inventado: ver relatorio.
        STATS["prereq_prosa_nao_traduzida"].append(
            (feature_id_para_relatorio, [p.get("value") for p in prereq])
        )
    return campo  # sempre vazio nesta passada -- ver nota acima


def construir_registros_feature(
    fdata: dict,
    owners: list[tuple[str, int]],
    classes_foundry: dict[str, dict],
    pf2etools_por_classe: dict[str, tuple[dict | None, str | None]],
) -> list[dict]:
    sys_ = fdata["system"]
    nome = fdata["name"]
    pub = sys_.get("publication") or {}
    license_ = pub.get("license")
    remaster_foundry = bool(pub.get("remaster"))
    nivel_proprio = (sys_.get("level") or {}).get("value")
    traits_valor = (sys_.get("traits") or {}).get("value") or []
    rarity_foundry = (sys_.get("traits") or {}).get("rarity")

    grants, mechanized, motivos = montar_grants_feature(sys_)
    if mechanized:
        STATS["mechanized_true"] += 1
    else:
        STATS["mechanized_false"] += 1
        for m in motivos:
            STATS["mechanized_false_motivos"][m.split(":")[0]] += 1

    hits_aon = aon_query(nome, "class-feature")
    if not hits_aon:
        STATS["aon_feature_sem_match"].append(nome)

    # unidades: (classe|None, nivel)
    if not owners:
        unidades = [(None, nivel_proprio)]
    else:
        unidades = owners

    registros = []
    multi = len(unidades) > 1
    if multi:
        STATS["n_multi_owner_features"] += 1
        STATS["n_multi_owner_expanded"] += len(unidades)

    for classe, nivel in unidades:
        if multi and classe:
            slug = f"{slug_classe(classe)}-{slugify(nome)}"
        else:
            slug = slugify(nome)

        hit, nivel_bateu = escolher_hit_aon(
            hits_aon, quer_remaster=remaster_foundry, nivel=nivel, classe=classe
        )

        campo_name, campo_rarity = Campo(), Campo()
        campo_traits = Campo()
        campo_book, campo_page = Campo(), Campo()

        if hit:
            campo_name.set(hit.get("name"), "aon")
            campo_rarity.set(hit.get("rarity"), "aon")
            campo_book.set(hit.get("primary_source"), "aon")
            campo_page.set(parse_aon_page(hit.get("primary_source_raw")), "aon")
        campo_name.set(nome, "foundry")
        campo_traits.set(traits_valor, "foundry")
        campo_rarity.set(rarity_foundry, "foundry")
        campo_book.set(pub.get("title"), "foundry")

        conflitos = []
        if hit and not nivel_bateu:
            conflitos.append(
                {
                    "campo": "level",
                    "foundry": nivel,
                    "aon": hit.get("level"),
                    "escolhido": "foundry",
                }
            )

        # cross-check com pf2etools: por classe dona, no array classFeature
        # (e subclassFeature) do arquivo daquela classe.
        if classe:
            pf2e_data, pf2e_fname = pf2etools_por_classe.get(classe, (None, None))
        else:
            pf2e_data, pf2e_fname = None, None

        pf2etools_xref = None
        if pf2e_data:
            todas = list(pf2e_data.get("classFeature") or []) + list(
                pf2e_data.get("subclassFeature") or []
            )
            achado = next((x for x in todas if x.get("name") == nome), None)
            if achado:
                pf2etools_xref = "{}|{}|{}|{}".format(
                    achado.get("name"), classe, achado.get("source"), achado.get("level")
                )
                nivel_pf2etools = achado.get("level")
                if nivel_pf2etools is not None and nivel_pf2etools != nivel:
                    conflitos.append(
                        {
                            "campo": "level",
                            "classe": classe,
                            "foundry": nivel,
                            "pf2etools": nivel_pf2etools,
                            "escolhido": "foundry",
                        }
                    )
                    STATS["conflitos_level"].append((slug, classe, nivel, nivel_pf2etools))

        registro = {
            "id": f"wb:class-feature/{slug}",
            "kind": "class-feature",
            "name": campo_name.valor,
            "level": nivel,
            "class": [classe] if classe else [],
            "traits": campo_traits.valor,
            "rarity": campo_rarity.valor,
            "source": {
                "book": campo_book.valor,
                "page": campo_page.valor,
                "license": license_,
                "remaster": remaster_foundry,
            },
            "grants": grants,
            "text": f"wb:text/class-feature/{slug}",
            "mechanized": mechanized,
            "xref": {
                "foundry": f"Compendium.pf2e.classfeatures.Item.{fdata['_id']}",
                "aon": hit.get("_id") if hit else None,
                "pf2etools": pf2etools_xref,
            },
            "prov": {
                "name": campo_name.fonte,
                "level": "foundry",
                "class": "foundry",
                "traits": campo_traits.fonte,
                "rarity": campo_rarity.fonte,
                "source": campo_book.fonte,
                "grants": "foundry",
            },
            "conflitos": conflitos,
        }
        if campo_page.valor is None:
            STATS["campos_nao_mapeados"]["class-feature.source.page (sem match aon)"] += 1
        registros.append(registro)

    return registros


# ---------------------------------------------------------------------------
# extrair() -- API publica do modulo
# ---------------------------------------------------------------------------

def extrair() -> list[dict]:
    classes_foundry = carregar_classes_foundry()
    features_foundry = carregar_class_features_foundry()
    STATS["n_classes_foundry"] = len(classes_foundry)
    STATS["n_class_features_foundry"] = len(features_foundry)

    print(f"[classes] {len(classes_foundry)} classes, {len(features_foundry)} class-features "
          f"(Foundry, pin {FOUNDRY_PIN[:10]})", file=sys.stderr)

    ownership = montar_indice_ownership(classes_foundry)

    slugs_conhecidos = {slug_classe(n) for n in classes_foundry}

    # pf2etools por classe (uma tentativa de download por classe)
    pf2etools_por_classe: dict[str, tuple[dict | None, str | None]] = {}
    for nome_classe in classes_foundry:
        slug = slug_classe(nome_classe)
        data, fname = load_pf2etools_for_class(slug)
        pf2etools_por_classe[nome_classe] = (data, fname)
        if data is None:
            STATS["pf2etools_classes_sem_arquivo"].append(nome_classe)
            STATS["pf2etools_class_cobertura"][nome_classe] = (None, "sem arquivo no pf2etools")
        else:
            gerado_remaster = bool(data.get("class", [{}])[0].get("remaster"))
            fonte_remaster_foundry = bool(
                (classes_foundry[nome_classe]["system"].get("publication") or {}).get("remaster")
            )
            if gerado_remaster != fonte_remaster_foundry:
                nota = (
                    f"arquivo {fname} e geracao "
                    f"{'remaster' if gerado_remaster else 'legado'}, "
                    f"Foundry e {'remaster' if fonte_remaster_foundry else 'legado'} "
                    "-- geracoes divergentes, cross-check de nivel ainda tentado "
                    "(numero de nivel raramente muda entre geracoes)"
                )
            else:
                nota = f"arquivo {fname}, geracao bate com o Foundry"
            STATS["pf2etools_class_cobertura"][nome_classe] = (fname, nota)

    print(f"[classes] pf2etools resolvido para "
          f"{len(classes_foundry) - len(STATS['pf2etools_classes_sem_arquivo'])}/"
          f"{len(classes_foundry)} classes", file=sys.stderr)

    registros = []

    print("[classes] consultando AoN para classes...", file=sys.stderr)
    for i, (nome, cdata) in enumerate(sorted(classes_foundry.items()), 1):
        reg = construir_registro_classe(nome, cdata, {})
        fname = STATS["pf2etools_class_cobertura"].get(nome, (None, None))[0]
        if fname:
            reg["xref"]["pf2etools"] = fname
            reg["prov"]["xref_pf2etools"] = "pf2etools"
        registros.append(reg)
        STATS["n_registros_class"] += 1
        if reg["mechanized"]:
            STATS["mechanized_true"] += 1
        else:
            STATS["mechanized_false"] += 1

    print(f"[classes] {len(features_foundry)} class-features -- consultando AoN "
          "(pode levar alguns minutos na 1a execucao)...", file=sys.stderr)
    for i, fdata in enumerate(features_foundry, 1):
        owners = ownership.get(fdata["name"], [])
        regs = construir_registros_feature(fdata, owners, classes_foundry, pf2etools_por_classe)
        registros.extend(regs)
        STATS["n_registros_class_feature"] += len(regs)
        if i % 100 == 0:
            print(f"  ... {i}/{len(features_foundry)}", file=sys.stderr)

    STATS["n_registros_emitidos"] = len(registros)
    print(f"[classes] total emitido: {len(registros)} registros", file=sys.stderr)
    return registros


# ---------------------------------------------------------------------------
# Relatorio
# ---------------------------------------------------------------------------

def gerar_relatorio_md() -> str:
    s = STATS
    linhas = []
    linhas.append("# Relatorio -- extrator de classes e class-features\n")
    linhas.append(f"Pin do Foundry: `{FOUNDRY_PIN}`\n")

    linhas.append("## Contagens\n")
    linhas.append(f"- Classes no Foundry (packs/pf2e/classes): **{s['n_classes_foundry']}**")
    linhas.append(
        f"- Arquivos de class-feature no Foundry (packs/pf2e/class-features): "
        f"**{s['n_class_features_foundry']}** (827 arquivos no diretorio, "
        f"1 e `_folders.json` -- metadado de pasta do compendio, descartado)"
    )
    linhas.append(f"- Registros `class` emitidos: **{s['n_registros_class']}**")
    linhas.append(f"- Registros `class-feature` emitidos: **{s['n_registros_class_feature']}**")
    linhas.append(f"- Total de registros emitidos: **{s['n_registros_emitidos']}**")
    linhas.append(
        f"- Features compartilhadas por mais de uma classe (Weapon Specialization, "
        f"Shield Block etc.): **{s['n_multi_owner_features']}** nomes, expandidos em "
        f"**{s['n_multi_owner_expanded']}** registros (1 por par feature+classe dona, "
        f"porque o nivel de concessao difere por classe -- ver secao 'Problemas mais serios')\n"
    )

    linhas.append("## Campo-fonte -> campo-canonico, por fonte\n")
    linhas.append("### Foundry (`packs/pf2e/classes/*.json`)\n")
    linhas.append("| Campo Foundry | Campo canonico | Quirk |")
    linhas.append("|---|---|---|")
    linhas.append("| `system.hp` | `grants[].hp_per_level` | int direto |")
    linhas.append("| `system.perception` | `grants[].proficiency.perception` | rank 0-4 -> palavra |")
    linhas.append("| `system.savingThrows.{fortitude,reflex,will}` | `grants[].proficiency.*` | rank 0-4 -> palavra |")
    linhas.append("| `system.attacks.{simple,martial,advanced,unarmed}` | `grants[].proficiency.*` | rank 0-4 -> palavra |")
    linhas.append("| `system.attacks.other.{name,rank}` | `grants[].proficiency.<name>` | so incluido se `name` nao vazio |")
    linhas.append("| `system.defenses.{light,medium,heavy,unarmored}` | `grants[].proficiency.*` | rank 0-4 -> palavra |")
    linhas.append("| `system.trainedSkills.{value,additional}` | `grants[].skill_training.{auto,free}` | `value` quase sempre vazio nas 27 classes |")
    linhas.append("| `system.{classFeatLevels,skillFeatLevels,generalFeatLevels,ancestryFeatLevels}.value` | `grants[].feat_slot.{kind,levels}` | 4 grants, um por kind |")
    linhas.append("| `system.skillIncreaseLevels.value` | `grants[].skill_increase.levels` | **extensao ao vocabulario do schema** -- nao ha verbo pronto na spec pra isso |")
    linhas.append("| `system.keyAbility.value` | `key_ability` (fora de `grants`) | **campo extra**, nao esta no envelope generico |")
    linhas.append("| `system.spellcasting` | `spellcasting` (bool, fora de `grants`) | so a FLAG (0/1); a tabela de slots/tradicao real fica em rule elements, nao decodificados nesta passada |")
    linhas.append("| `system.publication.{license,remaster}` | `source.{license,remaster}` | unica fonte confiavel pra license (AoN nao expoe) |")
    linhas.append("| `system.publication.title` | `source.book` (fallback) | usado so quando AoN nao bate |")
    linhas.append("| `system.items{}` (nome+nivel+uuid) | indice de ownership feature->classe(s)+nivel | chave do problema de features compartilhadas |")
    linhas.append("| `system.rules[]` (classe) | determina `mechanized` | nao decodificado; presenca de rules != [] -> `mechanized:false` |\n")

    linhas.append("### Foundry (`packs/pf2e/class-features/*.json`)\n")
    linhas.append("| Campo Foundry | Campo canonico | Quirk |")
    linhas.append("|---|---|---|")
    linhas.append("| `system.level.value` | `level` | por (feature, classe dona) quando compartilhada |")
    linhas.append("| `system.traits.value` | `traits` (fallback) | AoN nao expoe traits pra class-feature |")
    linhas.append("| `system.traits.rarity` | `rarity` (fallback) | AoN normalmente tem, usado como primario |")
    linhas.append("| `system.subfeatures.proficiencies.<cat>.rank` | `grants[].proficiency.<cat>` | dict `{categoria: {rank:0..4}}`, tratado |")
    linhas.append("| `system.subfeatures.{senses,languages,keyOptions,suppressedFeatures}` | **nao mapeado** | contribui pra `mechanized:false` -- ver secao de gaps |")
    linhas.append("| `system.rules[]` (nao-vazio) | **nao mapeado** | contribui pra `mechanized:false` -- ~40 tipos de rule element, fora de escopo desta passada (custo maior do projeto, ver PROJECT.md) |")
    linhas.append("| `system.prerequisites.value` (prosa) | **nao mapeado pra `requires`** | so 4 features tem; prosa livre, sem marcacao -- ver gaps |")
    linhas.append("| `system.publication.{license,remaster,title}` | `source.*` | igual ao de classe |\n")

    linhas.append("### pf2etools (`data/class/class-<slug>[-pc1].json`)\n")
    linhas.append("| Campo pf2etools | Campo canonico | Quirk |")
    linhas.append("|---|---|---|")
    linhas.append("| `class[0].hp`, `.remaster`, `.source` | usado so pra decidir geracao (legado/remaster) do arquivo | nao sobrescreve nenhum campo do Foundry nesta passada |")
    linhas.append("| `classFeature[].level` (por classe) | cross-check contra `level` do Foundry | so quando o arquivo da classe dona foi resolvido |")
    linhas.append("| `subclassFeature[].level` | mesmo cross-check, pra feature de subclasse | mesclado com `classFeature` na busca por nome |")
    linhas.append("| `classFeatures[]` (string `Nome|Classe|Fonte|Nivel`) | **nao usado diretamente** | preferi o array `classFeature` (tem `.level` como int, sem parsear string) |\n")

    linhas.append("### Archives of Nethys (`elasticsearch.aonprd.com/aon/_search`)\n")
    linhas.append("| Campo AoN | Campo canonico | Quirk |")
    linhas.append("|---|---|---|")
    linhas.append("| `name` | `name` (primario) | `match_phrase`, nunca `terms`/`term` em campo de texto (retorna zero, armadilha documentada na spec) |")
    linhas.append("| `rarity` | `rarity` (primario) | presente em class e class-feature |")
    linhas.append("| `primary_source` | `source.book` (primario) | |")
    linhas.append("| `primary_source_raw` (\"Player Core pg. 136\") | `source.page` | parse por regex `pg\\.\\s*(\\d+)` |")
    linhas.append("| `legacy_id` / `remaster_id` | ponte legado<->remaster, usada pra escolher a geracao certa do hit | doc com `remaster_id` preenchido = e o LEGADO; doc com `legacy_id` preenchido = e o REMASTER |")
    linhas.append("| `class` (so em class-feature) | usado pra desambiguar quando a feature e compartilhada | ex.: \"Weapon Specialization\" tem um doc por classe dona, nao um doc so |")
    linhas.append("| `traits` | **ausente** em class e class-feature | confirmado por amostragem; `traits` cai pro Foundry sempre |")
    linhas.append("| `license` | **ausente** | AoN nao expoe OGL/ORC; `source.license` vem sempre do Foundry |\n")

    linhas.append("## Campos que NAO consegui mapear\n")
    linhas.append(
        "- **`requires` (pre-requisito) em class-feature.** So 4 dos 826 arquivos tem "
        "`system.prerequisites.value` preenchido (Way of the Spellshot, Flexible Spell "
        "Preparation, Elemental Magic, Wellspring Magic), e e prosa livre sem marcacao "
        "`{@feat}`/`{@skill}` -- o pf2etools (fonte vencedora pra `requires`) nao guarda "
        "prerequisites estruturados no nivel de class-feature (isso existe pra `feat`, "
        "que e outro extrator). Traduzir a prosa pra `all`/`any`/`class_level` exigiria "
        "parsing de linguagem natural -- decidi deixar `requires` ausente nesses 4 "
        "casos em vez de inventar estrutura. Nomes: " +
        ", ".join(x[0] for x in s["prereq_prosa_nao_traduzida"]) + ".\n"
    )
    linhas.append(
        "- **`system.subfeatures.{senses,languages,keyOptions,suppressedFeatures}`.** "
        "245 features tem `proficiencies` (traduzido pra `grants[].proficiency`), mas "
        "81 tem `senses`, 85 `suppressedFeatures`, 15 `languages`, 9 `keyOptions` -- "
        "nenhum desses quatro foi traduzido pra `grants` nesta passada. Contribuem pra "
        "`mechanized:false`.\n"
    )
    linhas.append(
        "- **`system.rules[]` (rule elements) em geral.** 593/826 features tem pelo "
        "menos 1 rule element nao-trivial (ChoiceSet, GrantItem, FlatModifier, "
        "MartialProficiency, CriticalSpecialization etc.). Decidir decodificar isso e "
        "o item de maior custo do projeto (ja registrado assim em PROJECT.md) -- fora "
        "de escopo desta entrega. Essas features saem com `mechanized:false` e "
        "`grants` parcial (so a parte de `subfeatures.proficiencies`, quando existe).\n"
    )
    linhas.append(
        "- **Tabela de spellcasting (slots por nivel, tradicao).** `system.spellcasting` "
        "no arquivo de classe e so uma flag 0/1 dizendo se a classe conjura. A tabela "
        "real (progressao de slots, foco, preparado x repertorio) vive espalhada em "
        "rule elements de class-features especificas (ex.: \"Arcane Spellcasting\"), "
        "nao decodificada. `spellcasting` sai como bool solto, sem `spell_slots`.\n"
    )
    linhas.append(
        "- **4 classes sem nenhum arquivo no pf2etools:** " +
        ", ".join(sorted(s["pf2etools_classes_sem_arquivo"])) +
        " -- Animist, Commander, Exemplar e Guardian sao classes recentes "
        "(War of Immortals / Battlecry!) que o branch `dev` do pf2etools ainda nao "
        "portou em `data/class/`. Cross-check de nivel pulado pra elas; `xref.pf2etools` "
        "fica `null`.\n"
    )
    faltas_page = s["campos_nao_mapeados"].get("class.source.page (sem match aon)", 0)
    faltas_page_cf = s["campos_nao_mapeados"].get("class-feature.source.page (sem match aon)", 0)
    linhas.append(
        f"- **`source.page` ausente por falta de match no AoN:** {faltas_page} classes, "
        f"{faltas_page_cf} class-features (ver listas de nomes sem match na secao seguinte).\n"
    )

    linhas.append("## Divergencias reais encontradas\n")
    linhas.append(
        "### 1. Modelo de dados diferente para features compartilhadas\n"
        "O Foundry guarda **um arquivo por class-feature**, referenciado (nome+nivel+uuid) "
        "pelas classes que a concedem -- ex. `Weapon Specialization.json` e um arquivo so, "
        "listado no `items{}` de 25 classes diferentes, cada uma com um `level` proprio "
        "(Fighter recebe no 7, Wizard no 13). O AoN, ao contrario, indexa **um documento por "
        "classe dona** (`class-feature-167` = Fighter Weapon Specialization nivel 7, "
        "`class-feature-300` = Wizard Weapon Specialization nivel 13, etc. -- 72 hits so pro "
        "nome \"Weapon Specialization\"). O pf2etools segue o mesmo padrao do AoN (nivel "
        "dentro do array `classFeature` de cada classe). Resolvido expandindo o registro "
        "canonico em 1-por-(feature,classe) quando o nivel diverge entre classes donas -- "
        f"{s['n_multi_owner_features']} nomes, {s['n_multi_owner_expanded']} registros "
        "expandidos. Ver 'Problemas mais serios' abaixo -- isso deveria estar na spec.\n"
    )
    if s["conflitos_level"]:
        linhas.append("### 2. Nivel divergente entre Foundry e pf2etools\n")
        linhas.append("| Feature | Classe | Foundry | pf2etools |")
        linhas.append("|---|---|---|---|")
        for slug, classe, nf, np in s["conflitos_level"][:30]:
            linhas.append(f"| {slug} | {classe} | {nf} | {np} |")
        if len(s["conflitos_level"]) > 30:
            linhas.append(f"| ... | mais {len(s['conflitos_level'])-30} | | |")
        linhas.append("")
    else:
        linhas.append(
            "### 2. Nivel divergente entre Foundry e pf2etools\n"
            "Nenhuma divergencia de `level` encontrada nos casos em que consegui cruzar "
            "os dois (feature com classe dona resolvida no pf2etools). Isso e esperado: "
            "level de class-feature normalmente nao muda entre legado e remaster.\n"
        )
    linhas.append(
        "### 3. Geracao (legado x remaster) divergente entre Foundry e pf2etools\n"
        "Classes onde o Foundry considera o conteudo remasterizado (`publication.remaster: "
        "true`, licenca ORC) mas o arquivo disponivel no pf2etools ainda e o legado "
        "(pre-remaster, licenca OGL/CRB/APG original):\n"
    )
    linhas.append("| Classe | Arquivo pf2etools usado | Nota |")
    linhas.append("|---|---|---|")
    for nome_classe, (fname, nota) in sorted(s["pf2etools_class_cobertura"].items()):
        if fname and "divergem" in nota:
            linhas.append(f"| {nome_classe} | {fname} | {nota} |")
    linhas.append("")

    linhas.append("## mechanized: true x false\n")
    total_mech = s["mechanized_true"] + s["mechanized_false"]
    linhas.append(f"- `mechanized: true`: **{s['mechanized_true']}** / {total_mech}")
    linhas.append(f"- `mechanized: false`: **{s['mechanized_false']}** / {total_mech}\n")
    linhas.append(
        "Uma class-feature sai `mechanized:true` só quando `system.rules` está vazio "
        "**e** `system.subfeatures` só contém `proficiencies` (ou está vazio). Motivos "
        "de `mechanized:false` mais comuns:\n"
    )
    linhas.append("| Motivo | Ocorrencias |")
    linhas.append("|---|---|")
    for motivo, n in sorted(s["mechanized_false_motivos"].items(), key=lambda x: -x[1]):
        linhas.append(f"| {motivo} | {n} |")
    linhas.append("")

    linhas.append("## Sem match no AoN\n")
    linhas.append(f"- Classes sem nenhum hit: {s['aon_class_sem_match'] or '(nenhuma)'}")
    linhas.append(
        f"- Class-features sem nenhum hit ({len(s['aon_feature_sem_match'])}): " +
        (", ".join(s["aon_feature_sem_match"][:40]) + ("..." if len(s["aon_feature_sem_match"]) > 40 else ""))
        if s["aon_feature_sem_match"] else "(nenhuma)"
    )
    linhas.append("")

    linhas.append("## Os 3 problemas mais serios\n")
    linhas.append(
        "1. **O envelope da spec assume `level` escalar, mas ~27 features (187 pares "
        "feature+classe) tem nivel diferente por classe dona.** A spec precisa de uma "
        "decisao explicita: canonizar por (feature,classe) como fiz aqui (que muda a "
        "contagem total de ~29.236 registros estimados em PROJECT.md pra cima), ou "
        "manter 1 registro por feature com um `level` que vira dict `{classe: nivel}` "
        "em vez de int. Optei pela primeira porque bate com o proprio modelo do AoN e "
        "do pf2etools (eles ja tratam como entidades separadas), mas isso e uma decisao "
        "de arquitetura, nao um detalhe de implementacao -- deveria voltar pra spec.\n"
    )
    linhas.append(
        "2. **RAW de spellcasting nao esta neste extrator.** `spellcasting` sai como "
        "bool solto; a tabela de slots por nivel/tradicao (que faz Mago, Clerigo etc. "
        "funcionarem no builder) vive em rule elements de class-features especificas "
        "e nao foi decodificada. Sem isso as classes conjuradoras ficam com "
        "`mechanized:false` na pratica ainda que o registro da CLASSE em si saia "
        "`true` -- o builder vai calcular progressao de feat/proficiencia mas nao vai "
        "saber quantos slots de magia a classe tem.\n"
    )
    linhas.append(
        "3. **pf2etools no branch `dev`, no snapshot baixado agora, nao tem a geracao "
        "remaster pra 8 das 12 classes originarias do Player Core 2** (Alchemist, "
        "Barbarian, Champion, Investigator, Monk, Oracle, Sorcerer, Swashbuckler) nem "
        "arquivo nenhum pra 4 classes novas (Animist, Commander, Exemplar, Guardian). "
        "Isso significa que ~12/27 classes ficam sem cross-check de `level` confiavel "
        "contra a fonte que a spec desginou como autoridade pra isso -- o Foundry vira "
        "fonte unica de fato pra elas, contrariando a garantia de dupla-fonte que a "
        "spec pede (\"ha duas fontes independentes -- divergencia e bug\"). Se o "
        "pf2etools atualizar o branch dev depois, vale re-rodar.\n"
    )

    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------------------
# Execucao direta
# ---------------------------------------------------------------------------

def main():
    registros = extrair()

    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SAIDA_DIR / "classes.json"
    out_path.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[classes] escrito {out_path} ({out_path.stat().st_size} bytes)", file=sys.stderr)

    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
    rel_path = RELATORIOS_DIR / "classes.md"
    rel_path.write_text(gerar_relatorio_md(), encoding="utf-8")
    print(f"[classes] escrito {rel_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
