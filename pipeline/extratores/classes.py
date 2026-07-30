"""
Extrator canonico de CLASSES e CLASS-FEATURES do Pathfinder 2e (Waybuilder).

Contrato: Tartarus/Projetos/pessoal/waybuilder/specs/2026-07-26-schema-base.md

Fontes (fixadas):
  - foundryvtt/pf2e, commit 87f9e5028baaa10b70fdc766260b7886def17e04
    packs/pf2e/classes/*.json (27), packs/pf2e/class-features/*.json (827,
    sendo 1 arquivo de metadado de pasta descartado)
  - Pf2eToolsOrg/Pf2eTools, branch dev, data/class/class-<slug>[-pc1|-pc2].json
  - Archives of Nethys, elasticsearch.aonprd.com/aon/_search

Modelo de dados (fix 2026-07-26, ver spec "Nivel de class-feature pertence a
classe, nao a feature"): o Foundry guarda 1 arquivo por class-feature,
referenciado por N classes cada uma com nivel proprio. Uma class-feature e UM
registro compartilhado, SEM campo `level` -- quem diz em que nivel ela entra e
`wb:class/*.progressao`. A versao anterior deste extrator duplicava o registro
por (feature, classe dona); ver relatorio para a contagem do antes/depois.

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
import unicodedata
import urllib.error
import urllib.request
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
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

sys.path.insert(0, str(PIPELINE_DIR))
import comum  # noqa: E402

FOUNDRY_PIN = "87f9e5028baaa10b70fdc766260b7886def17e04"
# Clone local pinado no commit acima, dentro de dados_brutos/. Reconstruivel por
# `pipeline/buscar_fontes.sh`; sobrescrivel por env var.
FOUNDRY_SRC_DEFAULT = str(RAW_DIR / "foundry_repo")
FOUNDRY_SRC = os.environ.get("WB_FOUNDRY_REPO", FOUNDRY_SRC_DEFAULT)

AON_URL = "https://elasticsearch.aonprd.com/aon/_search"
PF2ETOOLS_RAW = "https://raw.githubusercontent.com/Pf2eToolsOrg/Pf2eTools/dev/data/class/{}"
HTTP_TIMEOUT = 20
HTTP_SLEEP = 0.03  # cortesia entre requests em cache miss

RANK_WORDS = {0: "untrained", 1: "trained", 2: "expert", 3: "master", 4: "legendary"}

FOUNDRY_FEATURE_UUID_PREFIX = "Compendium.pf2e.classfeatures.Item."

# Slugs das 27 classes reconhecidas no pin do Foundry (preenchido em runtime a
# partir dos arquivos de packs/pf2e/classes/, ver carregar_classes_foundry()).


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    # mesma convencao dos irmaos (equipamento.py, feats.py, referencia.py,
    # companheiros.py, aon_kinds.py): apostrofo SOME (Acrobat's -> Acrobats),
    # nao vira hifen -- estava divergindo aqui e trocando o id de toda
    # class-feature possessiva ("Acrobat's Calling" virava acrobat-s-calling
    # em vez de acrobats-calling, 47 ids no total, cache do AoN igualmente
    # invalidado por vir do slug antigo).
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("'", "").replace("’", "")
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
    Cacheia bruto (lista de _source + _id) por (categoria, nome).

    match_phrase casa qualquer nome que CONTENHA a frase buscada em sequencia
    -- buscar "Weapon Mastery" tambem traz hits como "Fighter Weapon Mastery"
    ou "Martial Weapon Mastery" (variantes por classe do proprio AoN). Quem
    consome o resultado precisa filtrar por igualdade exata quando quiser so
    o nome pedido (ver escolher_hit_aon_feature)."""
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


def prefetch_aon(pares: list[tuple[str, str]], workers: int = 12) -> None:
    """Popula o cache do AoN em paralelo antes das buscas sequenciais em
    aon_query() -- a latencia do elasticsearch.aonprd.com e ~1s/consulta
    (nao e overhead de handshake), entao paralelizar e o unico jeito de nao
    levar ~15min numa base fria de ~850 nomes distintos."""
    vistos = set()
    pendentes = []
    for nome, categoria in pares:
        chave = (categoria, nome)
        if chave in vistos:
            continue
        vistos.add(chave)
        cache_file = AON_CACHE / f"{slugify(categoria)}__{slugify(nome)}.json"
        if not cache_file.exists():
            pendentes.append((nome, categoria))

    if not pendentes:
        return
    print(
        f"[classes] prefetch AoN: {len(pendentes)} consultas novas em ate "
        f"{workers} conexoes paralelas...",
        file=sys.stderr,
    )
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(aon_query, nome, categoria) for nome, categoria in pendentes]
        for fut in as_completed(futs):
            fut.result()
            done += 1
            if done % 150 == 0:
                print(f"  ... {done}/{len(pendentes)}", file=sys.stderr)


def _nome_base(nome: str) -> str | None:
    """'Adept Benefit (Amulet)' -> 'Adept Benefit'. O Foundry as vezes quebra
    uma unica entrada do AoN em variantes parentizadas (por escolha de
    implemento, campo de pesquisa do alquimista etc.); o AoN normalmente so
    tem a base. ATENCAO: essas variantes tem conteudo DIFERENTE entre si
    (grants diferentes) -- sao registros legitimamente distintos (ver spec,
    "mesmo nome, conteudo diferente"). Essa funcao serve so pra achar um hit
    aproximado de fonte/rarity/pagina no AoN; nunca pra decidir o `name` do
    registro (ver escolher_hit_aon_feature + construir_registro_feature)."""
    if " (" in nome and nome.endswith(")"):
        return nome.split(" (", 1)[0].strip()
    return None


def resolver_hits_feature(nome: str) -> tuple[list[dict], bool]:
    """Cascata de busca pra class-feature: nome exato em category
    class-feature -> nome-base sem parenteses, mesma categoria (ex. 'Adept
    Benefit (Amulet)' -> 'Adept Benefit'). Fica restrito a categoria
    class-feature de proposito: uma cascata pra categoria "feat" foi testada
    e descartada -- "Advanced Alchemy" como class-feature (Alchemist nativo)
    e "Advanced Alchemy" como feat de arquetipo (Alchemist Dedication) sao
    coisas DIFERENTES com o mesmo nome; cruzar categoria arriscava emparelhar
    o registro errado (fonte/pagina/nivel de outra entidade). So usada
    depois do prefetch_aon_fallback_features() ter aquecido o cache.

    Devolve (hits, via_fallback) -- via_fallback=True quando so achou pelo
    nome-base (sem parenteses), o que sinaliza pro chamador que o `name` do
    hit NAO deve sobrescrever o nome canonico do Foundry (senao "Field
    Discovery (Bomber)" e "Field Discovery (Chirurgeon)" colapsam pro mesmo
    texto exibido "Field Discovery", mascarando que sao registros
    distintos)."""
    hits = aon_query(nome, "class-feature")
    if hits:
        return hits, False
    base = _nome_base(nome)
    if base:
        hits = aon_query(base, "class-feature")
        if hits:
            return hits, True
    return [], False


def prefetch_aon_fallback_features(nomes: list[str]) -> None:
    """2a leva de prefetch: so pros nomes que ficaram sem hit em
    (nome, class-feature) na 1a leva. Precisa rodar depois do prefetch_aon()
    inicial, porque so sabemos quem precisa de fallback lendo o cache."""
    pares = []
    for nome in nomes:
        hits = aon_query(nome, "class-feature")
        if hits:
            continue
        base = _nome_base(nome)
        if base:
            pares.append((base, "class-feature"))
    prefetch_aon(pares)


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
    """Usado so pro registro de CLASS (uma consulta por classe, sem ambiguidade
    de dono). Filtra por classe/nivel quando informado, depois escolhe a
    geracao certa. Devolve (hit, nivel_bateu)."""
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


def escolher_hit_aon_feature(
    hits: list[dict], nome: str, quer_remaster: bool, classes_donas: list[str], exigir_nome: bool
) -> dict | None:
    """Escolha de hit do AoN pra um class-feature COMPARTILHADO. O AoN indexa
    uma classe-feature compartilhada como 1 documento POR CLASSE DONA (as
    vezes ate com nome diferente por classe, ex. Ranger's legacy
    "Martial Weapon Mastery" pro que o Foundry hoje consolidou como "Weapon
    Mastery") -- e so podemos emitir 1 registro, entao a escolha e
    deterministica: exige nome exatamente igual ao do Foundry quando
    `exigir_nome=True` (match_phrase traz superstrings tipo "Fighter Weapon
    Mastery" pra busca de "Weapon Mastery", que precisam ser descartadas),
    filtra pela geracao certa, e prefere o hit cuja classe seja uma das donas
    (a primeira em ordem alfabetica, pra ser reproduzivel) -- na falta de um
    hit de classe dona, cai pro primeiro do pool."""
    pool = hits
    if exigir_nome:
        pool = [h for h in pool if h.get("name") == nome]
    if not pool:
        return None
    alvo_ger = [h for h in pool if _hit_is_legacy(h) != quer_remaster]
    pool2 = alvo_ger or pool
    for c in sorted(classes_donas):
        candidatos = [h for h in pool2 if h.get("class") == c]
        if candidatos:
            return candidatos[0]
    return pool2[0]


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
    "n_features_multi_classe": 0,
    "distribuicao_owners": Counter(),  # N donas -> quantas features tem N donas
    "n_classe_inferida_por_trait": 0,
    "ownership_resolvido_por_uuid": 0,  # items{} com name cacheado desatualizado, resolvido via uuid
    "ownership_nao_resolvido": [],  # (classe, nome_item, nivel) sem match nem por nome nem por uuid
    "mesmo_nome_conteudo_diferente": [],  # (nome_base, [nomes distintos]) -- grupos mantidos separados de proposito
    "mechanized_true": 0,
    "mechanized_false": 0,
    "mechanized_false_motivos": defaultdict(int),
    "aon_class_sem_match": [],
    "aon_feature_sem_match": [],
    "aon_feature_nome_exato": 0,
    "aon_feature_nome_aproximado": 0,
    "pf2etools_class_cobertura": {},  # classe -> (arquivo usado | None, nota)
    "pf2etools_classes_sem_arquivo": [],
    "conflitos_level": [],  # (nome_feature, classe, foundry, pf2etools)
    "campos_nao_mapeados": defaultdict(int),
    "prereq_prosa_nao_traduzida": [],
    "colisoes_de_id": [],  # (id_original, id_novo, nome, xref_foundry) -- rede de seguranca, ver verificar_colisoes_de_id
    "progressao_cobertura": {},  # classe -> (len(progressao), total_items_da_classe)
}


def verificar_colisoes_de_id(registros: list[dict]) -> None:
    """Rede de seguranca: com o fix de modelagem (1 registro por class-feature,
    sem prefixo de classe no slug), a unica forma de colisao de id seria dois
    arquivos do Foundry com o MESMO `name` -- confirmado por inspecao que nao
    ha nenhum caso hoje (826 arquivos, 826 nomes distintos; ver relatorio,
    secao 'Colisoes de id'). Mantido como guarda porque o build deve FALHAR
    de forma auditavel, nunca sobrescrever um registro em silencio."""
    vistos: dict[str, dict] = {}
    for r in registros:
        rid = r["id"]
        if rid in vistos:
            STATS["colisoes_de_id"].append(
                (vistos[rid]["id"], rid + "-dup", r["name"], r["xref"].get("foundry"))
            )
            r["id"] = rid + "-dup"
            r["text"] = r["text"] + "-dup"
        else:
            vistos[rid] = r


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

    # `tinha_mecanica=True` incondicional, e nao `bool(grants)`: `class` nasce
    # de `montar_grants_classe()`, que le hp/perception/savingThrows/attacks --
    # campos estruturados que TODA classe tem. Nunca ha ausencia de declaracao
    # aqui, entao `null` mentiria. Spec:
    # specs/2026-07-30-cobertura-de-grants-completos.md
    grants_completos, requires_parseado = comum.mecanizacao(
        "class", True, bool(rules_extra), False, True)

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
        "progressao": [],  # preenchido depois de processar as class-features, ver extrair()
        "text": f"wb:text/class/{slug}",
        "mechanized": mechanized,
        "grants_completos": grants_completos,
        "requires_parseado": requires_parseado,
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
            "progressao": "foundry",
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

def _uuid_suffix(uuid: str | None) -> str | None:
    """'Compendium.pf2e.classfeatures.Item.Martial Weapon Mastery' ->
    'Martial Weapon Mastery'. So usado como fallback de casamento -- ver
    montar_indice_ownership."""
    if not uuid or not uuid.startswith(FOUNDRY_FEATURE_UUID_PREFIX):
        return None
    return uuid[len(FOUNDRY_FEATURE_UUID_PREFIX):]


def montar_indice_ownership(
    classes_foundry: dict[str, dict], nomes_feature_conhecidos: set[str]
) -> dict[str, list[tuple[str, int]]]:
    """nome_da_feature (nome ATUAL do arquivo) -> [(nome_da_classe, nivel_nessa_classe), ...]

    Cada entrada de `system.items{}` de uma classe carrega um `name` cacheado
    no momento em que o item foi adicionado ao compendio -- as vezes esse
    cache fica desatualizado depois que a feature e renomeada rio abaixo
    (achado real: Ranger cacheia "Weapon Mastery" corretamente, mas Cleric
    ainda cacheia "Deity" pro item que hoje se chama "Deity (Cleric)"). Casa
    primeiro pelo `name` cacheado; quando isso falha, cai pro sufixo do
    `uuid` (que referencia por nome tambem, mas pode estar defasado na
    direcao oposta -- por isso so e tentado depois do `name` direto, nunca
    antes). Sem essa 2a tentativa, 14 dos 520 vinculos classe->feature
    ficariam invisiveis (ver relatorio, secao 'Casamento de ownership')."""
    idx: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for nome_classe, cdata in classes_foundry.items():
        for item in (cdata["system"].get("items") or {}).values():
            nome_item = item["name"]
            nivel = item["level"]
            if nome_item in nomes_feature_conhecidos:
                idx[nome_item].append((nome_classe, nivel))
                continue
            suf = _uuid_suffix(item.get("uuid"))
            if suf and suf in nomes_feature_conhecidos:
                idx[suf].append((nome_classe, nivel))
                STATS["ownership_resolvido_por_uuid"] += 1
                continue
            STATS["ownership_nao_resolvido"].append((nome_classe, nome_item, nivel))
    return idx


# ---------------------------------------------------------------------------
# Construcao do registro de CLASS-FEATURE
# ---------------------------------------------------------------------------

def montar_grants_feature(sys_: dict) -> tuple[list[dict], bool, list[str], bool]:
    """Devolve (grants, mechanized, motivos_nao_mecanizado, tinha_mecanica).

    `tinha_mecanica` e o que separa "a fonte nao declarou nada" de "declarou e
    eu nao converti" -- as duas viravam `grants: []` sem distincao. Sao 164
    features cujo doc do Foundry nao tem `subfeatures` nem `rules`, contra 608
    que tem e nao saem convertidas. Ver
    specs/2026-07-30-cobertura-de-grants-completos.md.
    """
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

    return grants, mechanized, motivos, bool(profs or subf_extra or rules)


def registrar_prereq_nao_traduzido(sys_: dict, nome: str) -> None:
    """`requires` fica ausente quando o Foundry tem `prerequisites.value`
    (prosa livre, sem marcacao {@feat}/{@skill} como no pf2etools -- que e a
    fonte vencedora pra `requires` mas nao guarda prerequisito estruturado no
    nivel de class-feature). Traduzir a prosa pra linguagem de predicado
    exigiria parsing de linguagem natural -- fora de escopo desta passada.
    So registra, nao inventa estrutura (ver relatorio)."""
    prereq = (sys_.get("prerequisites") or {}).get("value") or []
    if prereq:
        STATS["prereq_prosa_nao_traduzida"].append((nome, [p.get("value") for p in prereq]))


def inferir_classe_por_trait(
    traits_valor: list[str], classes_foundry: dict[str, dict]
) -> str | None:
    """Fallback pra features de subclasse (instintos, doutrinas, bloodlines,
    edges de cacador etc.) que NAO aparecem no items{} de nenhuma classe --
    a ligacao so existe via trait. So infere quando exatamente 1 trait bate
    com uma classe conhecida (ambiguidade real e rara, ver relatorio)."""
    nome_por_slug = {slug_classe(n): n for n in classes_foundry}
    bateu = [nome_por_slug[t] for t in traits_valor if t in nome_por_slug]
    if len(bateu) == 1:
        return bateu[0]
    return None


def construir_registro_feature(
    fdata: dict,
    owners: list[tuple[str, int]],
    classes_foundry: dict[str, dict],
    pf2etools_por_classe: dict[str, tuple[dict | None, str | None]],
    progressao_por_classe: dict[str, list[dict]],
) -> dict:
    """1 registro por arquivo do Foundry -- SEM `level` (spec: nivel pertence
    a progressao da classe, nao a feature). `owners` ja vem ordenado por nome
    de classe (determinismo). Cada (classe, nivel) em `owners` vira uma
    entrada em progressao_por_classe[classe] apontando pro id deste registro."""
    sys_ = fdata["system"]
    nome = fdata["name"]
    pub = sys_.get("publication") or {}
    license_ = pub.get("license")
    remaster_foundry = bool(pub.get("remaster"))
    nivel_proprio = (sys_.get("level") or {}).get("value")
    traits_valor = (sys_.get("traits") or {}).get("value") or []
    rarity_foundry = (sys_.get("traits") or {}).get("rarity")

    registrar_prereq_nao_traduzido(sys_, nome)

    grants, mechanized, motivos, tinha_mecanica = montar_grants_feature(sys_)
    grants_completos, requires_parseado = comum.mecanizacao(
        "class-feature", tinha_mecanica, not mechanized, False, True)
    if mechanized:
        STATS["mechanized_true"] += 1
    else:
        STATS["mechanized_false"] += 1
        for m in motivos:
            STATS["mechanized_false_motivos"][m.split(":")[0]] += 1

    # unidades: (classe, nivel) -- direto do items{} (owners) ou inferido por
    # trait quando a feature e orfa (subclasse concedida via rule element).
    classe_inferida = False
    if owners:
        unidades = owners
    else:
        classe_unica = inferir_classe_por_trait(traits_valor, classes_foundry)
        if classe_unica:
            classe_inferida = True
            unidades = [(classe_unica, nivel_proprio)]
            STATS["n_classe_inferida_por_trait"] += 1
        else:
            unidades = []

    classes_donas = sorted({c for c, _ in unidades})
    slug = slugify(nome)
    feature_id = f"wb:class-feature/{slug}"

    hits_aon, via_fallback = resolver_hits_feature(nome)
    if not hits_aon:
        STATS["aon_feature_sem_match"].append(nome)

    hit_exato = None
    if not via_fallback:
        hit_exato = escolher_hit_aon_feature(hits_aon, nome, remaster_foundry, classes_donas, exigir_nome=True)
    hit_aprox = hit_exato or escolher_hit_aon_feature(hits_aon, nome, remaster_foundry, classes_donas, exigir_nome=False)
    if hit_exato:
        STATS["aon_feature_nome_exato"] += 1
    elif hit_aprox:
        STATS["aon_feature_nome_aproximado"] += 1

    campo_name, campo_rarity = Campo(), Campo()
    campo_traits = Campo()
    campo_book, campo_page = Campo(), Campo()

    # `name` so aceita AoN quando o hit bateu nome EXATO -- um hit aproximado
    # (via nome-base) nunca pode sobrescrever, senao variantes com conteudo
    # diferente ("Field Discovery (Bomber)" x "(Chirurgeon)") colapsam pro
    # mesmo texto exibido e a distincao se perde (ver resolver_hits_feature).
    if hit_exato:
        campo_name.set(hit_exato.get("name"), "aon")
    campo_name.set(nome, "foundry")

    if hit_aprox:
        fonte_aon = "aon" if hit_aprox is hit_exato else "aon (nome aproximado)"
        campo_rarity.set(hit_aprox.get("rarity"), fonte_aon)
        campo_book.set(hit_aprox.get("primary_source"), fonte_aon)
        campo_page.set(parse_aon_page(hit_aprox.get("primary_source_raw")), fonte_aon)
    # Feature compartilhada carrega no Foundry o trait de TODAS as classes
    # donas (e assim que o filtro de feats do Foundry funciona) -- e um dado
    # legitimamente coletivo agora que o registro tambem e coletivo, entao
    # nao ha mais filtragem por dono (a versao anterior filtrava porque cada
    # registro representava so 1 classe; ver LOG do defeito consertado).
    campo_traits.set(traits_valor, "foundry")
    campo_rarity.set(rarity_foundry, "foundry")
    campo_book.set(pub.get("title"), "foundry")

    conflitos = []
    pf2etools_matches = []
    for classe, nivel in unidades:
        pf2e_data, _ = pf2etools_por_classe.get(classe, (None, None))
        if not pf2e_data:
            continue
        todas = list(pf2e_data.get("classFeature") or []) + list(
            pf2e_data.get("subclassFeature") or []
        )
        achado = next((x for x in todas if x.get("name") == nome), None)
        if not achado:
            continue
        pf2etools_matches.append(
            "{}|{}|{}|{}".format(achado.get("name"), classe, achado.get("source"), achado.get("level"))
        )
        nivel_pf2etools = achado.get("level")
        if nivel_pf2etools is not None and nivel_pf2etools != nivel:
            conflitos.append(
                {
                    "campo": "progressao.nivel",
                    "classe": classe,
                    "foundry": nivel,
                    "pf2etools": nivel_pf2etools,
                    "escolhido": "foundry",
                }
            )
            STATS["conflitos_level"].append((nome, classe, nivel, nivel_pf2etools))

    hit_para_xref = hit_exato or hit_aprox
    if classes_donas:
        prov_class = "foundry (inferido de traits)" if classe_inferida else "foundry"
    else:
        prov_class = None

    # direto = veio do items{} da propria classe; inferido = so achado via
    # trait unico (feature de subclasse sem slot de nivel fixo). As duas
    # coisas viram progressao igual, mas o relatorio precisa saber separar
    # pra medir cobertura de items{} sem se confundir com o volume extra que
    # a inferencia por trait adiciona (ver STATS["progressao_cobertura"]).
    direto = bool(owners)

    registro = {
        "id": feature_id,
        "kind": "class-feature",
        "name": campo_name.valor,
        "class": classes_donas,
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
        "grants_completos": grants_completos,
        "requires_parseado": requires_parseado,
        "xref": {
            "foundry": f"Compendium.pf2e.classfeatures.Item.{fdata['_id']}",
            "aon": hit_para_xref.get("_id") if hit_para_xref else None,
            "pf2etools": pf2etools_matches or None,
        },
        "prov": {
            "name": campo_name.fonte,
            "class": prov_class,
            "traits": campo_traits.fonte,
            "rarity": campo_rarity.fonte,
            "source": campo_book.fonte,
            "grants": "foundry",
        },
        "conflitos": conflitos,
    }
    if campo_page.valor is None:
        STATS["campos_nao_mapeados"]["class-feature.source.page (sem match aon)"] += 1

    for classe, nivel in unidades:
        progressao_por_classe[classe].append(
            {"nivel": nivel, "concede": feature_id, "_direto": direto}
        )

    return registro


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

    nomes_feature_conhecidos = {f["name"] for f in features_foundry}
    ownership = montar_indice_ownership(classes_foundry, nomes_feature_conhecidos)

    # pf2etools por classe (uma tentativa de download por classe)
    pf2etools_por_classe: dict[str, tuple[dict | None, str | None]] = {}
    for nome_classe in classes_foundry:
        slug = slug_classe(nome_classe)
        data, fname = load_pf2etools_for_class(slug)
        pf2etools_por_classe[nome_classe] = (data, fname)
        if data is None:
            STATS["pf2etools_classes_sem_arquivo"].append(nome_classe)
            STATS["pf2etools_class_cobertura"][nome_classe] = (None, "sem arquivo no pf2etools", True)
        else:
            gerado_remaster = bool(data.get("class", [{}])[0].get("remaster"))
            fonte_remaster_foundry = bool(
                (classes_foundry[nome_classe]["system"].get("publication") or {}).get("remaster")
            )
            geracao_bate = gerado_remaster == fonte_remaster_foundry
            if not geracao_bate:
                nota = (
                    f"arquivo {fname} e geracao "
                    f"{'remaster' if gerado_remaster else 'legado'}, "
                    f"Foundry e {'remaster' if fonte_remaster_foundry else 'legado'} "
                    "-- geracoes divergentes, cross-check de nivel ainda tentado "
                    "(numero de nivel raramente muda entre geracoes)"
                )
            else:
                nota = f"arquivo {fname}, geracao bate com o Foundry"
            STATS["pf2etools_class_cobertura"][nome_classe] = (fname, nota, geracao_bate)

    print(f"[classes] pf2etools resolvido para "
          f"{len(classes_foundry) - len(STATS['pf2etools_classes_sem_arquivo'])}/"
          f"{len(classes_foundry)} classes", file=sys.stderr)

    pares_aon = [(nome, "class") for nome in classes_foundry] + [
        (f["name"], "class-feature") for f in features_foundry
    ]
    prefetch_aon(pares_aon)
    prefetch_aon_fallback_features([f["name"] for f in features_foundry])

    print("[classes] consultando AoN para classes...", file=sys.stderr)
    registros_class: dict[str, dict] = {}
    for nome, cdata in sorted(classes_foundry.items()):
        reg = construir_registro_classe(nome, cdata, {})
        fname = STATS["pf2etools_class_cobertura"].get(nome, (None, None))[0]
        if fname:
            reg["xref"]["pf2etools"] = fname
            reg["prov"]["xref_pf2etools"] = "pf2etools"
        registros_class[nome] = reg
        STATS["n_registros_class"] += 1
        if reg["mechanized"]:
            STATS["mechanized_true"] += 1
        else:
            STATS["mechanized_false"] += 1

    print(f"[classes] {len(features_foundry)} class-features -- consultando AoN "
          "(pode levar alguns minutos na 1a execucao)...", file=sys.stderr)
    progressao_por_classe: dict[str, list[dict]] = defaultdict(list)
    registros_feature = []
    for i, fdata in enumerate(features_foundry, 1):
        owners = sorted(ownership.get(fdata["name"], []), key=lambda x: x[0])
        reg = construir_registro_feature(
            fdata, owners, classes_foundry, pf2etools_por_classe, progressao_por_classe
        )
        registros_feature.append(reg)
        STATS["n_registros_class_feature"] += 1
        if i % 100 == 0:
            print(f"  ... {i}/{len(features_foundry)}", file=sys.stderr)

    # anexa a progressao (nivel + feature concedida) em cada classe -- e aqui
    # que o nivel de uma class-feature compartilhada passa a viver. Separa
    # contribuicao "direta" (veio do items{} da classe) de "inferida" (so
    # achada via trait unico, tipicamente escolha de subclasse) so pra medir
    # cobertura -- o registro final de progressao nao carrega essa distincao
    # (nao esta na spec), so nivel+concede.
    for nome_classe, reg in registros_class.items():
        entradas_raw = sorted(
            progressao_por_classe.get(nome_classe, []),
            key=lambda e: (e["nivel"], e["concede"]),
        )
        n_direto = sum(1 for e in entradas_raw if e["_direto"])
        n_inferido = len(entradas_raw) - n_direto
        reg["progressao"] = [
            {"nivel": e["nivel"], "concede": e["concede"]} for e in entradas_raw
        ]
        total_items = len(
            (classes_foundry[nome_classe]["system"].get("items") or {})
        )
        STATS["progressao_cobertura"][nome_classe] = (n_direto, total_items, n_inferido)

    registros = list(registros_class.values()) + registros_feature
    verificar_colisoes_de_id(registros)

    # distribuicao de N donas por feature + grupos "mesmo nome, conteudo
    # diferente" (variantes parentizadas que NAO foram colapsadas em nome,
    # ver escolher_hit_aon_feature)
    grupos_nome_base: dict[str, list[str]] = defaultdict(list)
    for reg in registros_feature:
        n = len(reg["class"])
        STATS["distribuicao_owners"][n] += 1
        if n >= 2:
            STATS["n_features_multi_classe"] += 1
        base = _nome_base(reg["name"]) or reg["name"]
        grupos_nome_base[base].append(reg["name"])
    for base, nomes in grupos_nome_base.items():
        distintos = sorted(set(nomes))
        if len(distintos) > 1:
            STATS["mesmo_nome_conteudo_diferente"].append((base, distintos))
    STATS["mesmo_nome_conteudo_diferente"].sort(key=lambda x: (-len(x[1]), x[0]))

    STATS["n_registros_emitidos"] = len(registros)
    STATS["mechanized_true"] = sum(1 for r in registros if r["mechanized"])
    STATS["mechanized_false"] = sum(1 for r in registros if not r["mechanized"])
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
    linhas.append(
        "Este extrator foi reescrito em 2026-07-26 pra corrigir um defeito de "
        "modelagem: a versao anterior duplicava o registro de uma class-feature "
        "compartilhada por (feature, classe dona), porque tratava `level` como "
        "campo escalar da feature. Ver spec, secao 'Nivel de class-feature "
        "pertence a classe, nao a feature'. Esta secao inicial documenta o "
        "antes/depois; o resto do relatorio segue o formato de sempre.\n"
    )

    linhas.append("## Antes x depois (fix de modelagem)\n")
    total_antes = 1013
    class_feature_antes = 986
    reducao = class_feature_antes - s["n_registros_class_feature"]
    pct_reducao = (reducao / class_feature_antes * 100) if class_feature_antes else 0
    linhas.append(f"- Registros `class-feature` **antes** (1 por par feature+classe dona): **{class_feature_antes}**")
    linhas.append(f"- Registros `class-feature` **depois** (1 por arquivo do Foundry, sem `level`): **{s['n_registros_class_feature']}**")
    linhas.append(f"- Reducao por deduplicacao: **{reducao}** registros (**{pct_reducao:.1f}%**)")
    linhas.append(f"- Total de registros emitidos: antes **{total_antes}**, depois **{s['n_registros_emitidos']}**\n")

    linhas.append("## Contagens\n")
    linhas.append(f"- Classes no Foundry (packs/pf2e/classes): **{s['n_classes_foundry']}**")
    linhas.append(
        f"- Arquivos de class-feature no Foundry (packs/pf2e/class-features): "
        f"**{s['n_class_features_foundry']}** (827 arquivos no diretorio, "
        f"1 e `_folders.json` -- metadado de pasta do compendio, descartado)"
    )
    linhas.append(f"- Registros `class` emitidos: **{s['n_registros_class']}**")
    linhas.append(f"- Registros `class-feature` emitidos: **{s['n_registros_class_feature']}** (1:1 com arquivos do Foundry)")
    linhas.append(f"- Total de registros emitidos: **{s['n_registros_emitidos']}**")
    linhas.append(
        f"- Features com **2 ou mais** classes donas (compartilhadas de fato -- Weapon "
        f"Specialization, Shield Block etc.): **{s['n_features_multi_classe']}**, cada uma "
        f"emitida como **1 registro** com N entradas de `progressao` (uma por classe), "
        f"em vez dos N registros duplicados de antes"
    )
    linhas.append(
        f"- Features sem dono direto no `items{{}}` de nenhuma classe (instintos, doutrinas, "
        f"bloodlines, edges de cacador etc.) recuperadas via trait unico: "
        f"**{s['n_classe_inferida_por_trait']}** (`prov.class = \"foundry (inferido de "
        f"traits)\"`)"
    )
    linhas.append(
        f"- Vinculos classe->feature resolvidos via sufixo do `uuid` do Foundry (o `name` "
        f"cacheado em `items{{}}` estava desatualizado -- achado real, ver secao "
        f"'Casamento de ownership'): **{s['ownership_resolvido_por_uuid']}**"
    )
    linhas.append(
        f"- Vinculos classe->feature que ficaram sem match (nem por nome nem por uuid): "
        f"**{len(s['ownership_nao_resolvido'])}**\n"
    )

    linhas.append("### Distribuicao de N classes donas por feature\n")
    linhas.append("| N classes donas | Quantas features |")
    linhas.append("|---|---|")
    for n in sorted(s["distribuicao_owners"]):
        linhas.append(f"| {n} | {s['distribuicao_owners'][n]} |")
    linhas.append("")

    linhas.append("## Casamento de ownership (items{} -> arquivo de feature)\n")
    if s["ownership_resolvido_por_uuid"]:
        linhas.append(
            "`system.items{}` de uma classe guarda um `name` cacheado no momento em que o "
            "item foi vinculado ao compendio. Achado real: esse cache fica desatualizado "
            "em alguns casos -- ex. Ranger referencia corretamente `\"Weapon Mastery\"`, mas "
            "Cleric ainda cacheia `\"Deity\"` pro item que hoje se chama `\"Deity (Cleric)\"`. "
            "O casamento tenta primeiro o `name` cacheado; quando falha, cai pro sufixo do "
            "`uuid` (que referencia por nome tambem, mas pode estar desatualizado na direcao "
            "oposta -- por isso so e tentado depois do `name` direto). Sem essa 2a tentativa, "
            f"**{s['ownership_resolvido_por_uuid']}** vinculos ficariam invisiveis e as "
            "classes correspondentes sairiam com `progressao` incompleta."
        )
    if s["ownership_nao_resolvido"]:
        linhas.append("\nAinda sem match (nem por nome nem por uuid):\n")
        linhas.append("| Classe | Nome no items{} | Nivel |")
        linhas.append("|---|---|---|")
        for c, n, lvl in s["ownership_nao_resolvido"]:
            linhas.append(f"| {c} | {n} | {lvl} |")
    linhas.append("")

    linhas.append("## Progressao por classe\n")
    linhas.append(
        "`progressao` de uma classe mistura 2 origens: entradas **diretas** (vieram do "
        "`items{}` da propria classe -- feat de nivel fixo) e entradas **inferidas** (a "
        "feature nao tem slot de nivel fixo, foi recuperada via trait unico -- tipicamente "
        "escolha de subclasse: instinto, doutrina, bloodline etc.). Cobertura so faz sentido "
        "medida contra a parte direta; a parte inferida e um extra legitimo, nao uma "
        "duplicata (por isso um total de `progressao` MAIOR que `items{}` e esperado e "
        "normal, nao e sinal de erro).\n"
    )
    completas = [c for c, (feito, total, _inf) in s["progressao_cobertura"].items() if feito == total]
    incompletas = [
        (c, feito, total, inf) for c, (feito, total, inf) in s["progressao_cobertura"].items() if feito != total
    ]
    linhas.append(
        f"- Classes com `progressao` direta cobrindo 100% das entradas de `items{{}}`: "
        f"**{len(completas)}** / {s['n_registros_class']}"
    )
    if incompletas:
        linhas.append("\nIncompletas na parte direta (entradas de `items{}` que nao viraram "
                       "`progressao` nem por nome nem por uuid -- ver secao 'Casamento de "
                       "ownership' pros nomes exatos que faltaram):\n")
        linhas.append("| Classe | progressao direta | items{} total | progressao inferida (extra) |")
        linhas.append("|---|---|---|---|")
        for c, feito, total, inf in sorted(incompletas):
            linhas.append(f"| {c} | {feito} | {total} | {inf} |")
    else:
        linhas.append("\nTodas as 27 classes tem `progressao` direta completa em relacao ao "
                       "`items{}` do Foundry (depois do fallback por uuid).")
    linhas.append("")

    linhas.append("## Casos de mesmo nome, conteudo diferente (mantidos separados)\n")
    grupos = s["mesmo_nome_conteudo_diferente"]
    linhas.append(
        f"Grupos onde a base do nome (antes do sufixo parentizado) se repete, mas o "
        f"conteudo e diferente por classe/variante -- **mantidos como registros "
        f"distintos**, com `id`/slug proprios (nunca colapsados em nome): "
        f"**{len(grupos)}** grupos, **{sum(len(v) for _, v in grupos)}** registros no total.\n"
    )
    if grupos:
        linhas.append("| Nome-base | Variantes distintas | N |")
        linhas.append("|---|---|---|")
        for base, nomes in grupos[:20]:
            linhas.append(f"| {base} | {', '.join(nomes)} | {len(nomes)} |")
        if len(grupos) > 20:
            linhas.append(f"| ... | mais {len(grupos) - 20} grupos | |")
    linhas.append(
        "\nExemplo do proprio criterio da spec: `Field Discovery` do Alchemist tem a "
        "versao generica (nivel 5, escolhida antes de definir o campo de pesquisa) mais "
        "4 variantes por campo de pesquisa (Bomber/Chirurgeon/Mutagenist/Toxicologist), "
        "cada uma com `grants` proprio -- 5 registros. `Deity` tem 2 variantes "
        "(`Deity (Champion)`, `Deity (Cleric)`) porque a mecanica de escolher divindade "
        "difere por classe. Nenhum desses foi fundido.\n"
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
    linhas.append("| `system.items{}` (nome+nivel+uuid) | `progressao[].{nivel,concede}` da classe | **campo novo** -- nivel de class-feature agora mora aqui, nao na feature |")
    linhas.append("| `system.rules[]` (classe) | determina `mechanized` | nao decodificado; presenca de rules != [] -> `mechanized:false` |\n")

    linhas.append("### Foundry (`packs/pf2e/class-features/*.json`)\n")
    linhas.append("| Campo Foundry | Campo canonico | Quirk |")
    linhas.append("|---|---|---|")
    linhas.append("| `system.level.value` | **nao emitido na feature** | vira `progressao[].nivel` na(s) classe(s) dona(s), ver acima |")
    linhas.append("| `system.traits.value` | `traits` (fallback) | AoN nao expoe traits pra class-feature; sem filtragem por dono (feature compartilhada tem trait de todas as classes de fato) |")
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
    linhas.append("| `classFeature[].level` (por classe) | cross-check contra `progressao[].nivel` dessa classe | so quando o arquivo da classe dona foi resolvido; conflito vira `conflitos[]` na FEATURE (campo `progressao.nivel`), com `classe` anotada |")
    linhas.append("| `subclassFeature[].level` | mesmo cross-check, pra feature de subclasse | mesclado com `classFeature` na busca por nome |")
    linhas.append("| `classFeatures[]` (string `Nome|Classe|Fonte|Nivel`) | **nao usado diretamente** | preferi o array `classFeature` (tem `.level` como int, sem parsear string) |\n")

    linhas.append("### Archives of Nethys (`elasticsearch.aonprd.com/aon/_search`)\n")
    linhas.append("| Campo AoN | Campo canonico | Quirk |")
    linhas.append("|---|---|---|")
    linhas.append("| `name` | `name` (primario) | so aceito quando bate EXATO com o nome do Foundry -- AoN indexa 1 doc por classe dona (as vezes com nome distinto, ex. `\"Martial Weapon Mastery\"` = nome legado de Ranger pro que hoje e `\"Weapon Mastery\"`); um match aproximado nunca sobrescreve `name` (ver `escolher_hit_aon_feature`) |")
    linhas.append("| `rarity`, `primary_source`, `primary_source_raw` | `rarity`/`source.book`/`source.page` | aceito com match exato OU aproximado (nome-base sem parenteses); representa 1 classe dona escolhida deterministicamente (a 1a em ordem alfabetica com hit), nao a media/uniao de todas -- ver 'Problemas que restam' |")
    linhas.append("| `legacy_id` / `remaster_id` | ponte legado<->remaster, usada pra escolher a geracao certa do hit | doc com `remaster_id` preenchido = e o LEGADO; doc com `legacy_id` preenchido = e o REMASTER |")
    linhas.append("| `class` (so em class-feature) | usado pra escolher o hit quando a feature e compartilhada | ex.: \"Weapon Mastery\" tem ate 13 docs (1 por classe dona) so pra geracao remaster |")
    linhas.append("| `traits` | **ausente** em class e class-feature | confirmado por amostragem; `traits` cai pro Foundry sempre |")
    linhas.append("| `license` | **ausente** | AoN nao expoe OGL/ORC; `source.license` vem sempre do Foundry |\n")

    linhas.append("## Cobertura de `grants` (mechanized true/false)\n")
    total_mech = s["mechanized_true"] + s["mechanized_false"]
    pct_true_depois = (s["mechanized_true"] / total_mech * 100) if total_mech else 0
    pct_true_antes = (312 / 1013 * 100)
    linhas.append(f"- Antes: `mechanized:true` **312** / 1013 (**{pct_true_antes:.1f}%**)")
    linhas.append(f"- Depois: `mechanized:true` **{s['mechanized_true']}** / {total_mech} (**{pct_true_depois:.1f}%**)")
    linhas.append(
        "\nA logica de traducao pra `grants` (subfeatures.proficiencies + presenca de "
        "`rules`) **nao mudou** -- e a mesma formula de antes, aplicada por arquivo do "
        "Foundry. A cobertura *proporcional* (percentual) fica estatisticamente equivalente; "
        "o que mudou foi so o denominador, porque antes cada feature compartilhada inflava "
        "tanto o numerador quanto o denominador N vezes (1 por classe dona, todas com o "
        "mesmo `mechanized`). A leitura correta: **cobertura de grants nao melhorou nem "
        "piorou em essencia -- so parou de ser contada em duplicidade.**\n"
    )
    linhas.append("| Motivo (mechanized:false) | Ocorrencias |")
    linhas.append("|---|---|")
    for motivo, n in sorted(s["mechanized_false_motivos"].items(), key=lambda x: -x[1]):
        linhas.append(f"| {motivo} | {n} |")
    linhas.append("")

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
        "Nenhum desses quatro foi traduzido pra `grants` nesta passada -- contribuem pra "
        "`mechanized:false` (ver tabela de motivos acima).\n"
    )
    linhas.append(
        "- **`system.rules[]` (rule elements) em geral.** Maioria das 826 features tem "
        "pelo menos 1 rule element nao-trivial (ChoiceSet, GrantItem, FlatModifier, "
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
    linhas.append(
        "- **`source.page`/`source.book` de uma feature compartilhada representa 1 classe "
        "dona, nao todas.** Quando N classes tem a mesma feature, cada uma pode ter sido "
        "publicada numa pagina diferente do livro daquela classe (ex.: Weapon Mastery pg. "
        "104 no capitulo do Champion, pg. 166 no do Ranger). O registro unico so guarda "
        "uma pagina (a 1a classe dona em ordem alfabetica com hit exato no AoN) -- perda "
        "de informacao aceita conscientemente em troca de nao duplicar o registro. Se "
        "isso importar pro builder, a pagina por classe teria que virar parte da "
        "`progressao`, nao do registro da feature -- decisao de spec, nao de "
        "implementacao.\n"
    )

    linhas.append("## Divergencias reais encontradas\n")
    if s["conflitos_level"]:
        linhas.append("### 1. Nivel divergente entre Foundry e pf2etools (por classe dona)\n")
        linhas.append("| Feature | Classe | Foundry | pf2etools |")
        linhas.append("|---|---|---|---|")
        for nome, classe, nf, np in s["conflitos_level"][:30]:
            linhas.append(f"| {nome} | {classe} | {nf} | {np} |")
        if len(s["conflitos_level"]) > 30:
            linhas.append(f"| ... | mais {len(s['conflitos_level'])-30} | | |")
        linhas.append("")
    else:
        linhas.append(
            "### 1. Nivel divergente entre Foundry e pf2etools (por classe dona)\n"
            "Nenhuma divergencia de nivel encontrada nos casos em que consegui cruzar "
            "os dois (feature com classe dona resolvida no pf2etools). Isso e esperado: "
            "nivel de class-feature normalmente nao muda entre legado e remaster.\n"
        )
    linhas.append(
        "### 2. Geracao (legado x remaster) divergente entre Foundry e pf2etools\n"
        "Classes onde o Foundry considera o conteudo remasterizado (`publication.remaster: "
        "true`, licenca ORC) mas o arquivo disponivel no pf2etools ainda e o legado "
        "(pre-remaster, licenca OGL/CRB/APG original):\n"
    )
    linhas.append("| Classe | Arquivo pf2etools usado | Nota |")
    linhas.append("|---|---|---|")
    for nome_classe, (fname, nota, geracao_bate) in sorted(s["pf2etools_class_cobertura"].items()):
        if fname and not geracao_bate:
            linhas.append(f"| {nome_classe} | {fname} | {nota} |")
    linhas.append("")

    linhas.append("## Sem match no AoN\n")
    linhas.append(f"- Classes sem nenhum hit: {s['aon_class_sem_match'] or '(nenhuma)'}")
    linhas.append(
        f"- Class-features com match de nome EXATO: **{s['aon_feature_nome_exato']}**"
    )
    linhas.append(
        f"- Class-features so com match APROXIMADO (nome-base, sem parenteses -- usado so "
        f"pra rarity/source/page, nunca pra `name`): **{s['aon_feature_nome_aproximado']}**"
    )
    linhas.append(
        f"- Class-features sem nenhum hit ({len(s['aon_feature_sem_match'])}): " +
        (", ".join(s["aon_feature_sem_match"][:40]) + ("..." if len(s["aon_feature_sem_match"]) > 40 else ""))
        if s["aon_feature_sem_match"] else "(nenhuma)"
    )
    linhas.append(
        "\nInvestigacao da passada anterior (mantida valida): a causa dominante do 'sem "
        "match' nao e falha de busca -- o AoN usa **categorias proprias pras escolhas de "
        "subclasse**, diferentes de `class-feature` (`mystery`, `patron`, `instinct`, "
        "`doctrine`, `order` etc.). Uma cascata de categorias alternativas e viavel mas "
        "arriscada sem validacao campo-a-campo (colisao real testada com `category:feat` "
        "-- \"Advanced Alchemy\" existe como class-feature nativa do Alchemist E como feat "
        "de arquetipo, duas entidades diferentes com o mesmo nome) -- fica pra uma proxima "
        "passada, nao mexida nesta.\n"
    )

    if s["colisoes_de_id"]:
        linhas.append("## Colisoes de id\n")
        linhas.append(
            "Com o fix de modelagem (slug de class-feature nunca mais prefixado por classe), "
            "as 3 colisoes conhecidas da passada anterior (Druid/Psychic/Wizard Weapon "
            "Expertise, orfaos que colidiam com o slug expandido `<classe>-weapon-expertise`) "
            "deixaram de existir -- o slug compartilhado hoje e so `weapon-expertise`, sem "
            "prefixo. As colisoes abaixo sao NOVAS, encontradas nesta rodada:\n"
        )
        linhas.append("| Id original | Id novo | Nome | xref.foundry |")
        linhas.append("|---|---|---|---|")
        for antigo, novo, nome, xref in s["colisoes_de_id"]:
            linhas.append(f"| `{antigo}` | `{novo}` | {nome} | {xref} |")
        linhas.append("")
    else:
        linhas.append("## Colisoes de id\n")
        linhas.append(
            "Nenhuma. Com o fix de modelagem, o slug de uma class-feature nunca mais leva "
            "prefixo de classe (e sempre `slugify(name)` puro) -- as 3 colisoes da passada "
            "anterior (Druid/Psychic/Wizard Weapon Expertise colidindo com o slug prefixado "
            "`<classe>-weapon-expertise`) deixaram de ser possiveis por construcao: os 826 "
            "arquivos do Foundry tem 826 nomes distintos, confirmado por inspecao direta. "
            "`verificar_colisoes_de_id()` continua rodando como rede de seguranca (o build "
            "deve falhar de forma auditavel, nunca sobrescrever em silencio), mas nao "
            "encontrou nada pra desambiguar nesta rodada.\n"
        )

    linhas.append("## Problemas que restam (nao resolvidos nesta passada)\n")
    linhas.append(
        "1. **RAW de spellcasting nao esta neste extrator.** `spellcasting` sai como "
        "bool solto; a tabela de slots por nivel/tradicao (que faz Mago, Clerigo etc. "
        "funcionarem no builder) vive em rule elements de class-features especificas "
        "e nao foi decodificada. Sem isso as classes conjuradoras ficam com "
        "`mechanized:false` na pratica ainda que o registro da CLASSE em si saia "
        "`true` -- o builder vai calcular progressao de feat/proficiencia mas nao vai "
        "saber quantos slots de magia a classe tem.\n"
    )
    linhas.append(
        "2. **pf2etools no branch `dev`, no snapshot baixado agora, nao tem a geracao "
        "remaster pra 8 das 12 classes originarias do Player Core 2** (Alchemist, "
        "Barbarian, Champion, Investigator, Monk, Oracle, Sorcerer, Swashbuckler) nem "
        "arquivo nenhum pra 4 classes novas (Animist, Commander, Exemplar, Guardian). "
        "Isso significa que ~12/27 classes ficam sem cross-check de nivel confiavel "
        "contra a fonte que a spec designou como autoridade pra isso -- o Foundry vira "
        "fonte unica de fato pra elas, contrariando a garantia de dupla-fonte que a "
        "spec pede (\"ha duas fontes independentes -- divergencia e bug\"). Se o "
        "pf2etools atualizar o branch dev depois, vale re-rodar.\n"
    )
    linhas.append(
        "3. **`source.page`/`source.book` de feature compartilhada representa so 1 classe "
        "dona** (a 1a em ordem alfabetica com hit exato no AoN), nao a pagina real em "
        "cada capitulo de classe -- ver secao 'Campos que NAO consegui mapear'. Se o "
        "builder precisar mostrar \"pg. X no capitulo do Fighter, pg. Y no do Wizard\", "
        "isso e uma decisao de spec (page por entrada de `progressao`?), nao um bug "
        "deste extrator.\n"
    )
    if s["ownership_nao_resolvido"]:
        linhas.append(
            f"4. **{len(s['ownership_nao_resolvido'])} vinculos classe->feature sem match** "
            "mesmo depois do fallback por uuid (ver secao 'Casamento de ownership' pros "
            "nomes exatos) -- normalizacoes adicionais (`(Level N)`, `(Choice)` etc.) ficam "
            "pra uma proxima passada se o volume justificar.\n"
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
