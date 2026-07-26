"""
Extrator canonico de ANCESTRIAS, HERANCAS (heritages) e BACKGROUNDS do Pathfinder 2e.

Contrato: /home/igor0/Tartarus/Projetos/pessoal/waybuilder/specs/2026-07-26-schema-base.md

Fontes (fixadas):
- Foundry pf2e (pin ver FOUNDRY_COMMIT abaixo) -- vencedora de campos estruturados
  (hp, size, speed, boosts, flaw, languages, senses, grants).
- AoN Elasticsearch (dump local em pipeline/dados_brutos/aon_*.json) -- vencedora
  de text/name/traits/rarity/source e da ponte remaster_id/legacy_id.
- pf2etools (dump local em pipeline/dados_brutos/pf2etools/) -- terceira opiniao,
  usada so para detectar divergencia (nao vence nenhum campo nesta kind).

Enumeracao: o conjunto de registros emitidos vem do Foundry (e o que o construtor
usa de fato -- "Escopo cortado no que o construtor usa", ver LESSONS.md). AoN e
usado para enriquecer e para o relatorio de mapa Legacy->Remaster (que precisa do
conjunto AoN inteiro, incluindo o que o Foundry nao tem).

stdlib-only. Roda offline a partir de pipeline/dados_brutos/.
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
PIPELINE_DIR = HERE.parent
DADOS_BRUTOS = PIPELINE_DIR / "dados_brutos"
SAIDA_DIR = PIPELINE_DIR / "saida"
RELATORIOS_DIR = PIPELINE_DIR / "relatorios"

FOUNDRY_REPO = Path(
    "/tmp/claude-1000/-mnt-c-Users-igor0/39eadbed-e8eb-4194-8557-74f05193fdc1"
    "/scratchpad/pf2e-research/pf2e"
)
FOUNDRY_COMMIT = "87f9e5028baaa10b70fdc766260b7886def17e04"
FOUNDRY_PACKS = FOUNDRY_REPO / "packs" / "pf2e"

PF2ETOOLS_DIR = DADOS_BRUTOS / "pf2etools"

REMASTER_CUTOFF = "2023-11-15"  # data de publicacao do Player Core no AoN

ABILITIES = {"str", "dex", "con", "int", "wis", "cha"}
ABILITY_FULL_TO_SHORT = {
    "strength": "str", "dexterity": "dex", "constitution": "con",
    "intelligence": "int", "wisdom": "wis", "charisma": "cha",
}


# ---------------------------------------------------------------------------
# Helpers genericos
# ---------------------------------------------------------------------------

def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def slug_from_filename(path):
    return Path(path).stem


def ability_short(name):
    """Normaliza nome de habilidade pro codigo de 3 letras. Retorna None se
    nao reconhecer (ex.: AoN as vezes guarda prosa solta em `attribute`,
    tipo "Two free ability boosts" em vez de tokens)."""
    if not name:
        return None
    n = name.strip().lower()
    if n in ABILITIES:
        return n
    return ABILITY_FULL_TO_SHORT.get(n)


def boost_effect(value_list):
    """Traduz uma lista de boosts do Foundry (['con'] ou lista de 6) pra
    linguagem de efeito do schema. Retorna None se a lista estiver vazia
    (slot sem boost)."""
    vals = [v for v in value_list if v]
    if not vals:
        return None
    if len(vals) >= 6:
        return {"ability_boost": {"livre": True, "quantidade": 1}}
    return {"ability_boost": {"opcoes": vals, "quantidade": 1}}


def flaw_effect(value_list):
    vals = [v for v in value_list if v]
    if not vals:
        return None
    return {"ability_flaw": {"opcoes": vals}}


PAGE_RE = re.compile(r"pg\.\s*(\d+)")


def parse_page(primary_source_raw):
    """`primary_source_raw` do AoN e string simples (\"Player Core pg. 42\"),
    nao lista -- ao contrario de `source_raw`, que e lista."""
    if not primary_source_raw or not isinstance(primary_source_raw, str):
        return None
    m = PAGE_RE.search(primary_source_raw)
    return int(m.group(1)) if m else None


RARITY_WORDS = {"common", "uncommon", "rare", "unique"}


def normalize_traits(trait_list, rarity):
    """Slugifica traits do AoN (Title Case -> kebab-case lowercase) e
    descarta o pseudo-trait de raridade que o AoN injeta na lista
    (trait_group=[\"Rarity\"]) quando a raridade nao e comum -- ja temos
    campo `rarity` proprio, nao faz sentido duplicar como trait."""
    out = []
    for t in trait_list or []:
        tl = t.strip().lower()
        if tl in RARITY_WORDS:
            continue
        out.append(re.sub(r"[^a-z0-9]+", "-", tl).strip("-"))
    return out


# ---------------------------------------------------------------------------
# Carregamento Foundry
# ---------------------------------------------------------------------------

def load_foundry_ancestries():
    out = {}
    for f in sorted((FOUNDRY_PACKS / "ancestries").glob("*.json")):
        d = _load_json(f)
        if not isinstance(d, dict) or d.get("type") != "ancestry":
            continue
        out[slug_from_filename(f)] = d
    return out


def load_foundry_heritages():
    out = {}
    for f in sorted((FOUNDRY_PACKS / "heritages").rglob("*.json")):
        if f.name == "_folders.json":
            continue
        d = _load_json(f)
        if not isinstance(d, dict) or d.get("type") != "heritage":
            continue
        out[slug_from_filename(f)] = d
    return out


def load_foundry_backgrounds():
    out = {}
    for f in sorted((FOUNDRY_PACKS / "backgrounds").glob("*.json")):
        if f.name == "_folders.json":
            continue
        d = _load_json(f)
        if not isinstance(d, dict) or d.get("type") != "background":
            continue
        out[slug_from_filename(f)] = d
    return out


# ---------------------------------------------------------------------------
# Carregamento AoN (dump local, ver pipeline/dados_brutos/_dump_aon_ancestrias.py)
# ---------------------------------------------------------------------------

def load_aon(kind):
    path = DADOS_BRUTOS / f"aon_{kind}.json"
    if not path.exists():
        return []
    return _load_json(path)


def index_aon_by_name(docs):
    idx = {}
    for d in docs:
        idx.setdefault(d["name"].strip().lower(), []).append(d)
    return idx


PAREN_RE = re.compile(r"\([^)]*\)")


def normalize_name(name):
    """Normalizacao frouxa pra pareamento de segunda tentativa: derruba
    parenteses, hifen vira espaco, colapsa espaco. Existe porque Foundry e
    AoN as vezes grafam o mesmo registro de jeitos diferentes -- ex.:
    Foundry \"Oenopion-Ooze Tender\" x AoN \"Oenopion Ooze-Tender\", Foundry
    \"Refugee (PC2)\" x AoN \"Refugee\", Foundry \"Reclaimer Investigator\" x
    AoN \"Reclaimed Investigator\" (essa ultima nao normaliza igual de
    proposito -- e uma divergencia de grafia real, nao so pontuacao;
    fica registrada em `relatorio['pareamento_fuzzy']` pra revisao manual)."""
    n = PAREN_RE.sub("", name).strip().lower()
    n = n.replace("-", " ")
    n = re.sub(r"\s+", " ", n).strip()
    return n


def index_aon_by_normalized_name(docs):
    idx = {}
    for d in docs:
        idx.setdefault(normalize_name(d["name"]), []).append(d)
    return idx


def lookup_aon_candidates(name, exact_idx, normalized_idx, relatorio, kind):
    """Match exato primeiro; se vazio, tenta nome normalizado e registra
    o par pra auditoria manual (grafia pode ter mudado de verdade, nao so
    pontuacao)."""
    key = name.strip().lower()
    candidates = exact_idx.get(key)
    if candidates:
        return candidates
    norm_candidates = normalized_idx.get(normalize_name(name))
    if norm_candidates:
        relatorio["pareamento_fuzzy"].append(
            f"{kind}: Foundry \"{name}\" ~ AoN \"{norm_candidates[0]['name']}\" "
            f"({norm_candidates[0]['id']})"
        )
        return norm_candidates
    return []


def pick_aon_doc(candidates, foundry_remaster):
    """Entre varios docs AoN com o mesmo nome, escolhe o que casa com a
    edicao do registro Foundry (remaster ou legacy)."""
    if not candidates:
        return None, "nenhum-candidato"
    if len(candidates) == 1:
        return candidates[0], "unico-candidato"
    with_legacy_id = [c for c in candidates if c.get("legacy_id")]
    without_legacy_id = [c for c in candidates if not c.get("legacy_id")]
    if foundry_remaster:
        if with_legacy_id:
            return with_legacy_id[0], "match-remaster-por-legacy_id"
    else:
        if without_legacy_id:
            # entre os sem legacy_id, prefere o que NAO aponta remaster_id
            # pra outro (i.e. o mais "antigo" quando ha varios legados)
            no_fwd = [c for c in without_legacy_id if not c.get("remaster_id")]
            return (no_fwd or without_legacy_id)[0], "match-legacy-sem-bridge"
    # fallback: maior release_date se remaster, menor se legacy
    ordered = sorted(candidates, key=lambda c: c.get("release_date") or "")
    return (ordered[-1] if foundry_remaster else ordered[0]), "fallback-por-data"


# ---------------------------------------------------------------------------
# Carregamento pf2etools (terceira opiniao, so pra divergencia)
# ---------------------------------------------------------------------------

def load_pf2etools_ancestries():
    idx = {}
    d = PF2ETOOLS_DIR / "ancestries"
    if not d.exists():
        return idx
    for f in sorted(d.glob("ancestry-*.json")):
        data = _load_json(f)
        for a in data.get("ancestry", []):
            idx.setdefault(a["name"].strip().lower(), []).append(a)
    return idx


def load_pf2etools_backgrounds():
    idx = {}
    d = PF2ETOOLS_DIR / "backgrounds"
    if not d.exists():
        return idx
    for f in sorted(d.glob("backgrounds-*.json")):
        data = _load_json(f)
        for b in data.get("background", []):
            idx.setdefault(b["name"].strip().lower(), []).append(b)
    return idx


# ---------------------------------------------------------------------------
# Construcao dos registros
# ---------------------------------------------------------------------------

def build_ancestry_heritage_map(foundry_heritages):
    """slug de ancestria -> lista de wb:heritage/<slug> diretamente ligados
    (nao inclui as versatile heritages, que valem pra qualquer ancestria)."""
    m = {}
    for hslug, h in foundry_heritages.items():
        anc = h["system"].get("ancestry")
        if anc is None:
            continue
        aslug = anc.get("slug")
        if not aslug:
            continue
        m.setdefault(aslug, []).append(f"wb:heritage/{hslug}")
    for k in m:
        m[k].sort()
    return m


def extract_ancestries(foundry_ancestries, aon_idx, aon_norm_idx, p2t_idx, heritage_map, relatorio):
    records = []
    for slug, d in sorted(foundry_ancestries.items()):
        s = d["system"]
        name = d["name"]
        pub = s.get("publication", {})
        is_remaster = bool(pub.get("remaster"))

        candidates = lookup_aon_candidates(name, aon_idx, aon_norm_idx, relatorio, "ancestry")
        aon_doc, match_kind = pick_aon_doc(candidates, is_remaster)
        if aon_doc is None:
            relatorio["ancestry_sem_aon"].append(name)

        prov = {}

        # --- name/traits/rarity/source: aon vence, fallback foundry ---
        if aon_doc:
            out_name = aon_doc.get("name", name)
            prov["name"] = "aon"
            rarity = aon_doc.get("rarity") or s.get("traits", {}).get("rarity")
            prov["rarity"] = "aon"
            aon_traits = normalize_traits(aon_doc.get("trait"), rarity)
            traits = aon_traits or list(s.get("traits", {}).get("value", []))
            prov["traits"] = "aon" if aon_traits else "foundry"
        else:
            out_name = name
            prov["name"] = "foundry"
            rarity = s.get("traits", {}).get("rarity")
            prov["rarity"] = "foundry"
            traits = list(s.get("traits", {}).get("value", []))
            prov["traits"] = "foundry"

        source = {
            "license": pub.get("license"),
            "remaster": is_remaster,
        }
        prov["source"] = "foundry"
        if aon_doc:
            source["book"] = aon_doc.get("primary_source")
            source["page"] = parse_page(aon_doc.get("primary_source_raw"))
            prov["source"] = "aon+foundry"
        else:
            source["book"] = pub.get("title")
            source["page"] = None

        # --- campos estruturados: foundry vence ---
        hp = s.get("hp")
        size = s.get("size")
        speed = s.get("speed")
        prov["hp"] = prov["size"] = prov["speed"] = "foundry"

        boosts = []
        for _, slot in sorted(s.get("boosts", {}).items(), key=lambda kv: kv[0]):
            eff = boost_effect(slot.get("value", []))
            if eff:
                boosts.append(eff)
        prov["boosts"] = "foundry" if boosts else None

        flaw = None
        for _, slot in sorted(s.get("flaws", {}).items(), key=lambda kv: kv[0]):
            eff = flaw_effect(slot.get("value", []))
            if eff:
                flaw = eff
                break
        prov["flaw"] = "foundry" if flaw else None

        addl = s.get("additionalLanguages", {})
        languages = {
            "fixos": list(s.get("languages", {}).get("value", [])),
            "extras": {
                "quantidade": addl.get("count", 0),
                "opcoes": list(addl.get("value", [])),
            },
        }
        if addl.get("custom"):
            languages["extras"]["custom"] = addl["custom"]
        prov["languages"] = "foundry"

        vision = s.get("vision")
        senses = {}
        if vision == "darkvision":
            senses = {"darkvision": True}
        elif vision == "low-light-vision":
            senses = {"low_light": True}
        prov["senses"] = "foundry"

        heritages = heritage_map.get(slug, [])
        prov["heritages"] = "foundry"

        conflitos = []
        if aon_doc:
            # cruza hp/size/speed/boosts/flaw com o AoN quando ele tem o campo
            if aon_doc.get("hp") is not None and aon_doc["hp"] != hp:
                conflitos.append({
                    "campo": "hp", "foundry": hp, "aon": aon_doc.get("hp"),
                    "escolhido": "foundry",
                })
            aon_speed = (aon_doc.get("speed") or {}).get("land")
            if aon_speed is not None and speed is not None and aon_speed != speed:
                conflitos.append({
                    "campo": "speed", "foundry": speed, "aon": aon_speed,
                    "escolhido": "foundry",
                })
            # AoN as vezes guarda `attribute` como prosa solta em vez de
            # tokens (ex.: Human = ["Two free ability boosts"]) -- so
            # compara quando toda a lista e parseavel (token = "Free" ou
            # nome de habilidade reconhecido), senao a comparacao e ruido.
            raw_attrs = aon_doc.get("attribute") or []
            attrs_parseaveis = all(
                a.lower() == "free" or ability_short(a) is not None
                for a in raw_attrs
            )
            fnd_boosts = set()
            for _, slot in s.get("boosts", {}).items():
                v = slot.get("value", [])
                if 1 <= len(v) < 6:
                    fnd_boosts.update(v)
            if attrs_parseaveis:
                aon_boosts = {
                    ability_short(a) for a in raw_attrs if a.lower() != "free"
                }
                if aon_boosts != fnd_boosts:
                    conflitos.append({
                        "campo": "boosts_fixos", "foundry": sorted(fnd_boosts),
                        "aon": sorted(aon_boosts), "escolhido": "foundry",
                    })

            raw_flaws = aon_doc.get("attribute_flaw") or []
            flaws_parseaveis = all(ability_short(a) is not None for a in raw_flaws)
            fnd_flaw = set(flaw["ability_flaw"]["opcoes"]) if flaw else set()
            if flaws_parseaveis:
                aon_flaw = {ability_short(a) for a in raw_flaws}
                if aon_flaw != fnd_flaw:
                    conflitos.append({
                        "campo": "flaw", "foundry": sorted(fnd_flaw),
                        "aon": sorted(aon_flaw), "escolhido": "foundry",
                    })

        p2t_candidates = p2t_idx.get(name.strip().lower(), [])
        if p2t_candidates:
            # so registra divergencia grosseira de hp/speed pra relatorio,
            # pf2etools nao vence nenhum campo nesta kind
            p = p2t_candidates[0]
            if p.get("hp") is not None and p["hp"] != hp:
                relatorio["divergencia_pf2etools"].append(
                    f"ancestry/{slug}: hp foundry={hp} pf2etools={p.get('hp')}"
                )

        xref = {
            "foundry": f"Compendium.pf2e.ancestries.Item.{d.get('_id')}",
        }
        if aon_doc:
            xref["aon"] = aon_doc["id"]
        if p2t_candidates:
            xref["pf2etools"] = f"ancestries/ancestry-{slug}"

        record = {
            "id": f"wb:ancestry/{slug}",
            "kind": "ancestry",
            "name": out_name,
            "traits": traits,
            "rarity": rarity,
            "source": source,
            "hp": hp,
            "size": size,
            "speed": speed,
            "boosts": boosts,
            "flaw": flaw,
            "languages": languages,
            "senses": senses,
            "heritages": heritages,
            "text": f"wb:text/ancestry/{slug}",
            "mechanized": True,
            "xref": xref,
            "prov": {k: v for k, v in prov.items() if v is not None},
        }
        if conflitos:
            record["conflitos"] = conflitos
        records.append(record)

        if not boosts:
            relatorio["ancestry_boosts_ausente"].append(name)
        if not flaw:
            relatorio["ancestry_flaw_ausente"].append(name)

    return records


def extract_heritages(foundry_heritages, aon_idx, aon_norm_idx, relatorio):
    records = []
    for slug, d in sorted(foundry_heritages.items()):
        s = d["system"]
        name = d["name"]
        pub = s.get("publication", {})
        is_remaster = bool(pub.get("remaster"))
        anc = s.get("ancestry")
        ancestry_id = f"wb:ancestry/{anc['slug']}" if anc else None

        candidates = lookup_aon_candidates(name, aon_idx, aon_norm_idx, relatorio, "heritage")
        aon_doc, _ = pick_aon_doc(candidates, is_remaster)
        if aon_doc is None:
            relatorio["heritage_sem_aon"].append(name)

        prov = {}
        if aon_doc:
            out_name = aon_doc.get("name", name)
            prov["name"] = "aon"
            rarity = aon_doc.get("rarity") or s.get("traits", {}).get("rarity")
            prov["rarity"] = "aon"
            aon_traits = normalize_traits(aon_doc.get("trait"), rarity)
            traits = aon_traits or list(s.get("traits", {}).get("value", []))
            prov["traits"] = "aon" if aon_traits else "foundry"
        else:
            out_name = name
            prov["name"] = "foundry"
            rarity = s.get("traits", {}).get("rarity")
            prov["rarity"] = "foundry"
            traits = list(s.get("traits", {}).get("value", []))
            prov["traits"] = "foundry"

        source = {"license": pub.get("license"), "remaster": is_remaster}
        prov["source"] = "foundry"
        if aon_doc:
            source["book"] = aon_doc.get("primary_source")
            source["page"] = parse_page(aon_doc.get("primary_source_raw"))
            prov["source"] = "aon+foundry"
        else:
            source["book"] = pub.get("title")
            source["page"] = None

        # --- grants: traducao limitada dos rule elements do Foundry ---
        rules = s.get("rules", [])
        grants = []
        mapped_keys = set()
        for r in rules:
            key = r.get("key")
            if key == "FlatModifier":
                selector = r.get("selector")
                grants.append({"flat_modifier": {
                    "selector": selector,
                    "type": r.get("type"),
                    "value": r.get("value"),
                }})
                mapped_keys.add(key)
        rule_keys = [r.get("key") for r in rules]
        mechanized = (not rules) or all(k in mapped_keys for k in rule_keys)
        prov["grants"] = "foundry"

        xref = {"foundry": f"Compendium.pf2e.heritages.Item.{d.get('_id')}"}
        if aon_doc:
            xref["aon"] = aon_doc["id"]

        record = {
            "id": f"wb:heritage/{slug}",
            "kind": "heritage",
            "name": out_name,
            "ancestry": ancestry_id,
            "traits": traits,
            "rarity": rarity,
            "source": source,
            "grants": grants,
            "text": f"wb:text/heritage/{slug}",
            "mechanized": mechanized,
            "xref": xref,
            "prov": {k: v for k, v in prov.items() if v is not None},
        }
        records.append(record)

        if not mechanized:
            relatorio["heritage_grants_parcial"] += 1
        if not rules:
            relatorio["heritage_sem_rule_elements"] += 1

    return records


def extract_backgrounds(foundry_backgrounds, aon_idx, aon_norm_idx, p2t_idx, relatorio):
    records = []
    for slug, d in sorted(foundry_backgrounds.items()):
        s = d["system"]
        name = d["name"]
        pub = s.get("publication", {})
        is_remaster = bool(pub.get("remaster"))

        candidates = lookup_aon_candidates(name, aon_idx, aon_norm_idx, relatorio, "background")
        aon_doc, _ = pick_aon_doc(candidates, is_remaster)
        if aon_doc is None:
            relatorio["background_sem_aon"].append(name)

        prov = {}
        if aon_doc:
            out_name = aon_doc.get("name", name)
            prov["name"] = "aon"
            rarity = aon_doc.get("rarity") or s.get("traits", {}).get("rarity")
            prov["rarity"] = "aon"
            aon_traits = normalize_traits(aon_doc.get("trait"), rarity)
            traits = aon_traits or list(s.get("traits", {}).get("value", []))
            prov["traits"] = "aon" if aon_traits else "foundry"
        else:
            out_name = name
            prov["name"] = "foundry"
            rarity = s.get("traits", {}).get("rarity")
            prov["rarity"] = "foundry"
            traits = list(s.get("traits", {}).get("value", []))
            prov["traits"] = "foundry"

        source = {"license": pub.get("license"), "remaster": is_remaster}
        prov["source"] = "foundry"
        if aon_doc:
            source["book"] = aon_doc.get("primary_source")
            source["page"] = parse_page(aon_doc.get("primary_source_raw"))
            prov["source"] = "aon+foundry"
        else:
            source["book"] = pub.get("title")
            source["page"] = None

        boosts = []
        for _, slot in sorted(s.get("boosts", {}).items(), key=lambda kv: kv[0]):
            eff = boost_effect(slot.get("value", []))
            if eff:
                boosts.append(eff)
        prov["boosts"] = "foundry" if boosts else None

        ts = s.get("trainedSkills", {})
        skill_training = {
            "skills": list(ts.get("value", [])),
            "lore": list(ts.get("lore", [])),
        }
        prov["skill_training"] = "foundry"

        items = s.get("items", {})
        feats_granted = [
            {"name": v.get("name"), "foundry_uuid": v.get("uuid")}
            for v in items.values()
        ]
        prov["feats_granted"] = "foundry" if feats_granted else None

        p2t_candidates = p2t_idx.get(name.strip().lower(), [])
        if p2t_candidates:
            p = p2t_candidates[0]
            p2t_skills = set(p.get("skills", []))
            fnd_skills = {sk.lower() for sk in skill_training["skills"]}
            if p2t_skills and p2t_skills != fnd_skills:
                relatorio["divergencia_pf2etools"].append(
                    f"background/{slug}: skills foundry={sorted(fnd_skills)} "
                    f"pf2etools={sorted(p2t_skills)}"
                )

        xref = {"foundry": f"Compendium.pf2e.backgrounds.Item.{d.get('_id')}"}
        if aon_doc:
            xref["aon"] = aon_doc["id"]
        if p2t_candidates:
            xref["pf2etools"] = f"backgrounds/{slug}"

        record = {
            "id": f"wb:background/{slug}",
            "kind": "background",
            "name": out_name,
            "traits": traits,
            "rarity": rarity,
            "source": source,
            "boosts": boosts,
            "skill_training": skill_training,
            "feats_granted": feats_granted,
            "text": f"wb:text/background/{slug}",
            "mechanized": True,
            "xref": xref,
            "prov": {k: v for k, v in prov.items() if v is not None},
        }
        records.append(record)

        if not boosts:
            relatorio["background_boosts_ausente"].append(name)
        if not skill_training["skills"] and not skill_training["lore"]:
            relatorio["background_skill_training_ausente"].append(name)
        if not feats_granted:
            relatorio["background_feat_ausente"].append(name)

    return records


# ---------------------------------------------------------------------------
# Mapa Legacy -> Remaster (a partir do conjunto AoN inteiro, nao so o Foundry)
# ---------------------------------------------------------------------------

def foundry_name_set(foundry_dict):
    return {d["name"].strip().lower() for d in foundry_dict.values()}


def foundry_normalized_name_set(foundry_dict):
    return {normalize_name(d["name"]) for d in foundry_dict.values()}


def build_legacy_remaster_map(aon_docs, foundry_names, foundry_names_norm, kind):
    renomeados = []
    sem_substituto = []
    for doc in aon_docs:
        rid = doc.get("remaster_id")
        if not rid:
            continue  # so nos interessa quem tem ponte pra frente
        # doc e legado com substituto -- resolve o nome do alvo
        target_ids = rid if isinstance(rid, list) else [rid]
        for tid in target_ids:
            target = next((x for x in aon_docs if x["id"] == tid), None)
            if target and target["name"].strip().lower() != doc["name"].strip().lower():
                renomeados.append({
                    "legacy": doc["name"], "legacy_id": doc["id"],
                    "remaster": target["name"], "remaster_id": target["id"],
                })

    for doc in aon_docs:
        is_legacy_era = (doc.get("release_date") or "9999") < REMASTER_CUTOFF
        if not is_legacy_era:
            continue
        if doc.get("remaster_id"):
            continue  # tem ponte, nao e "sem substituto"
        if doc["name"].strip().lower() in foundry_names:
            continue  # ainda oferecido (conteudo legado nunca remasterizado)
        if normalize_name(doc["name"]) in foundry_names_norm:
            continue  # mesmo conteudo, so grafia/pontuacao diverge do Foundry
        sem_substituto.append({
            "name": doc["name"], "id": doc["id"],
            "source": doc.get("primary_source"),
            "release_date": doc.get("release_date"),
        })

    return renomeados, sem_substituto


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------

def extrair():
    """Ponto de entrada do extrator. Retorna a lista combinada de registros
    (ancestry + heritage + background) no formato do schema-base."""
    foundry_ancestries = load_foundry_ancestries()
    foundry_heritages = load_foundry_heritages()
    foundry_backgrounds = load_foundry_backgrounds()

    aon_ancestries = load_aon("ancestries")
    aon_heritages = load_aon("heritages")
    aon_backgrounds = load_aon("backgrounds")

    aon_anc_idx = index_aon_by_name(aon_ancestries)
    aon_her_idx = index_aon_by_name(aon_heritages)
    aon_bg_idx = index_aon_by_name(aon_backgrounds)
    aon_anc_norm_idx = index_aon_by_normalized_name(aon_ancestries)
    aon_her_norm_idx = index_aon_by_normalized_name(aon_heritages)
    aon_bg_norm_idx = index_aon_by_normalized_name(aon_backgrounds)

    p2t_anc_idx = load_pf2etools_ancestries()
    p2t_bg_idx = load_pf2etools_backgrounds()

    heritage_map = build_ancestry_heritage_map(foundry_heritages)

    relatorio = {
        "ancestry_sem_aon": [], "heritage_sem_aon": [], "background_sem_aon": [],
        "ancestry_boosts_ausente": [], "ancestry_flaw_ausente": [],
        "background_boosts_ausente": [], "background_skill_training_ausente": [],
        "background_feat_ausente": [],
        "heritage_grants_parcial": 0, "heritage_sem_rule_elements": 0,
        "divergencia_pf2etools": [],
        "pareamento_fuzzy": [],
    }

    records = []
    records += extract_ancestries(foundry_ancestries, aon_anc_idx, aon_anc_norm_idx, p2t_anc_idx, heritage_map, relatorio)
    records += extract_heritages(foundry_heritages, aon_her_idx, aon_her_norm_idx, relatorio)
    records += extract_backgrounds(foundry_backgrounds, aon_bg_idx, aon_bg_norm_idx, p2t_bg_idx, relatorio)

    # anexa o mapa legacy->remaster e o relatorio como atributo da funcao,
    # pra quem quiser gerar o relatorio sem reprocessar tudo
    anc_renamed, anc_removed = build_legacy_remaster_map(
        aon_ancestries, foundry_name_set(foundry_ancestries),
        foundry_normalized_name_set(foundry_ancestries), "ancestry")
    her_renamed, her_removed = build_legacy_remaster_map(
        aon_heritages, foundry_name_set(foundry_heritages),
        foundry_normalized_name_set(foundry_heritages), "heritage")
    bg_renamed, bg_removed = build_legacy_remaster_map(
        aon_backgrounds, foundry_name_set(foundry_backgrounds),
        foundry_normalized_name_set(foundry_backgrounds), "background")

    extrair.ultimo_relatorio = {
        "contagens": {
            "ancestry": len(foundry_ancestries),
            "heritage": len(foundry_heritages),
            "background": len(foundry_backgrounds),
            "aon_ancestry_total": len(aon_ancestries),
            "aon_heritage_total": len(aon_heritages),
            "aon_background_total": len(aon_backgrounds),
        },
        "gaps": relatorio,
        "legacy_remaster": {
            "ancestry": {"renomeados": anc_renamed, "sem_substituto": anc_removed},
            "heritage": {"renomeados": her_renamed, "sem_substituto": her_removed},
            "background": {"renomeados": bg_renamed, "sem_substituto": bg_removed},
        },
    }

    return records


def _md_list(items, limit=None):
    if not items:
        return "(nenhum)\n"
    shown = items if limit is None else items[:limit]
    out = "".join(f"- {i}\n" for i in shown)
    if limit is not None and len(items) > limit:
        out += f"- ... (+{len(items) - limit})\n"
    return out


def gerar_relatorio_md(registros, meta):
    c = meta["contagens"]
    gaps = meta["gaps"]
    lr = meta["legacy_remaster"]

    by_kind = {"ancestry": [], "heritage": [], "background": []}
    for r in registros:
        by_kind[r["kind"]].append(r)

    lines = []
    lines.append("# Relatorio -- Ancestrias, Heranças e Backgrounds (PF2e)\n")
    lines.append(
        "Extrator: `pipeline/extratores/ancestrias.py`. Fontes: Foundry pf2e "
        f"(commit `{FOUNDRY_COMMIT}`), AoN (dump Elasticsearch), pf2etools "
        "(branch dev, terceira opiniao).\n"
    )

    lines.append("## Contagem por kind\n")
    lines.append("| kind | registros emitidos | boosts estruturados | flaw/skill_training estruturados |")
    lines.append("|---|---|---|---|")
    n_anc = len(by_kind["ancestry"])
    anc_boosts_ok = n_anc - len(gaps["ancestry_boosts_ausente"])
    anc_flaw_ok = n_anc - len(gaps["ancestry_flaw_ausente"])
    lines.append(f"| ancestry | {n_anc} | {anc_boosts_ok}/{n_anc} | {anc_flaw_ok}/{n_anc} (flaw) |")
    n_her = len(by_kind["heritage"])
    her_mech = n_her - gaps["heritage_grants_parcial"]
    lines.append(f"| heritage | {n_her} | n/a | {her_mech}/{n_her} totalmente mecanizados (`mechanized=true`) |")
    n_bg = len(by_kind["background"])
    bg_boosts_ok = n_bg - len(gaps["background_boosts_ausente"])
    bg_skill_ok = n_bg - len(gaps["background_skill_training_ausente"])
    lines.append(f"| background | {n_bg} | {bg_boosts_ok}/{n_bg} | {bg_skill_ok}/{n_bg} (skill_training) |")
    lines.append("")
    lines.append(
        f"Nenhum registro emitido veio so de prosa: todos os {n_anc + n_her + n_bg} "
        "registros sao enumerados a partir do Foundry, que sempre traz os campos "
        "estruturados em campo proprio (boosts/flaw/hp/speed/skill_training). "
        "\"Ausente\" acima significa RAW genuino (ex.: Human sem flaw, Amnesiac "
        "sem skill_training), nao falha de parsing -- ver secao de campos nao mapeados.\n"
    )

    lines.append("## Mapa Legacy -> Remaster (fonte: AoN, conjunto completo)\n")
    lines.append(
        f"AoN tem {c['aon_ancestry_total']} docs de ancestry, {c['aon_heritage_total']} "
        f"de heritage e {c['aon_background_total']} de background (Legacy + Remaster "
        "somados). Cruzamento via `remaster_id`/`legacy_id`.\n"
    )
    for kind, label in [("ancestry", "Ancestrias"), ("heritage", "Heranças"), ("background", "Backgrounds")]:
        renomeados = lr[kind]["renomeados"]
        removidos = lr[kind]["sem_substituto"]
        lines.append(f"### {label}\n")
        lines.append(f"- Renomeados (par Legacy->Remaster com nome diferente, via `remaster_id`): {len(renomeados)}\n")
        for r in renomeados:
            lines.append(f"  - {r['legacy']} ({r['legacy_id']}) -> {r['remaster']} ({r['remaster_id']})\n")
        lines.append(
            f"- Legacy sem substituto (era pre-remaster, sem `remaster_id`, e o nome "
            f"nao aparece no Foundry -- ou seja, saiu de circulacao): {len(removidos)}\n"
        )
        for r in removidos:
            lines.append(f"  - {r['name']} ({r['source']}, {r['release_date']}) -- `{r['id']}`\n")
        lines.append("")

    lines.append(
        "**Nota sobre Aasimar/Tiefling -> Nephilim:** o AoN nao tem `remaster_id` "
        "ligando Aasimar (`heritage-84`, Advanced Player's Guide) nem Tiefling "
        "(`heritage-86`, Advanced Player's Guide) a nada -- por isso aparecem acima "
        "em \"sem substituto\", nao em \"renomeados\". Confirmado por leitura direta: "
        "nenhuma das duas existe no Foundry (nem como heritage remaster nem legacy), "
        "e o texto de Nephilim (`heritage-280`, Player Core, presente no Foundry como "
        "versatile heritage) e mecanicamente identico ao template de Aasimar/Tiefling "
        "(\"ganha o trait X, visao adicional, escolhe feats de X ou da ancestria\"), so "
        "generalizado pra herança unica que cobre celestial/fiend/monitor. E fusao "
        "estrutural, nao substituicao 1:1 -- por isso o AoN nao registrou ponte "
        "automatica e o merge tem que ser manual.\n"
    )

    lines.append("## Campos nao mapeados\n")
    lines.append(
        "- **`ancestry.items`** (equipamento concedido, ex.: Clan Dagger do Dwarf, "
        "presente em 36/50 ancestrias do Foundry): fora do escopo pedido "
        "(hp/size/speed/boosts/flaw/languages/traits/senses/heritages). Nao emitido.\n"
    )
    lines.append(
        "- **`heritage.grants` parcial**: o Foundry usa ~20 tipos de rule element "
        "distintos nas heranças (GrantItem, ActiveEffectLike, ItemAlteration, Sense, "
        "Resistance, AdjustDegreeOfSuccess, RollOption, Strike, BaseSpeed, ChoiceSet, "
        "Note, CreatureSize, ActorTraits, TokenLight, DamageDice, Aura, AdjustModifier, "
        "AdjustStrike, Weakness). So `FlatModifier` foi traduzido pra linguagem de "
        f"efeito do schema (bate 1:1 com o exemplo do contrato). "
        f"`mechanized=true` em {n_her - gaps['heritage_grants_parcial']}/{n_her} "
        f"registros ({gaps['heritage_sem_rule_elements']} deles por nao terem rule "
        "element nenhum -- heranças puramente narrativas). O resto precisa do "
        "interpretador de rule elements (item de trabalho proprio, ja registrado em "
        "LESSONS.md do projeto).\n"
    )
    lines.append(
        "- **`background.feats_granted` como lista, nao campo singular**: 2 "
        "backgrounds (Hermean Heritor, Returned) concedem 2 feats, nao 1. Campo "
        "sai como lista em vez de objeto unico.\n"
    )
    lines.append(
        f"- **Ancestrias sem par no AoN**: {len(gaps['ancestry_sem_aon'])} -- {', '.join(gaps['ancestry_sem_aon']) or '(nenhuma)'}\n"
    )
    lines.append(
        f"- **Heranças sem par no AoN**: {len(gaps['heritage_sem_aon'])}\n"
    )
    lines.append(_md_list(gaps["heritage_sem_aon"], limit=20))
    lines.append(
        f"- **Backgrounds sem par no AoN**: {len(gaps['background_sem_aon'])}\n"
    )
    lines.append(_md_list(gaps["background_sem_aon"], limit=20))

    lines.append(
        f"- **Pareamento por nome normalizado (fallback)**: {len(gaps['pareamento_fuzzy'])} "
        "registros so casaram com AoN depois de derrubar parenteses/hifen (grafia "
        "diverge entre Foundry e AoN, mesmo registro). Sem esse fallback, esses "
        "apareceriam como \"sem par\" ou, do lado do mapa Legacy->Remaster, como "
        "\"removido\":\n"
    )
    lines.append(_md_list(gaps["pareamento_fuzzy"], limit=20))

    lines.append("## Divergencias entre fontes\n")
    lines.append(
        "Conflitos formais (campo por campo, foundry vs aon) ficam no array "
        "`conflitos` de cada registro em `ancestrias.json`. Abaixo, divergencias "
        "encontradas contra a terceira fonte (pf2etools), que nao vence nenhum "
        "campo nesta kind mas serve de checagem:\n"
    )
    lines.append(_md_list(gaps["divergencia_pf2etools"], limit=40))

    lines.append("## Casos RAW notaveis (nao sao bug do extrator)\n")
    lines.append(_md_list([
        "Human: dois boosts livres, zero flaw (RAW correto pos-remaster).",
        "Amnesiac (background, Player Core 2): 3 boosts livres, sem skill_training, "
        "sem feat -- background genuinamente atipico.",
        "Farmhand e outros ~60 backgrounds: sem feat concedido (`feats_granted=[]`) "
        "-- RAW, nao falha de extracao.",
        "Faction Opportunist (background): lore com string livre "
        "\"or Mercantile Lore\" dentro da lista -- dado cru do Foundry, mantido "
        "como veio (nao normalizado).",
        "19/50 ancestrias e 121/326 heranças no Foundry ainda sao Legacy/OGL "
        "(`source.remaster=false`) -- nunca foram remasterizadas oficialmente "
        "(ex.: Android, Anadi, Kitsune, Sprite, Strix, Skeleton).",
    ]))

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    registros = extrair()
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAIDA_DIR / "ancestrias.json", "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=2)
    print(f"gravados {len(registros)} registros em {SAIDA_DIR / 'ancestrias.json'}")

    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
    md = gerar_relatorio_md(registros, extrair.ultimo_relatorio)
    with open(RELATORIOS_DIR / "ancestrias.md", "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"relatorio gravado em {RELATORIOS_DIR / 'ancestrias.md'}")
