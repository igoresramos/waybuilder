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
    if not name:
        return None
    n = name.strip().lower()
    if n in ABILITIES:
        return n
    return ABILITY_FULL_TO_SHORT.get(n, n)


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


def parse_page(source_raw_list):
    if not source_raw_list:
        return None
    m = PAGE_RE.search(source_raw_list[0])
    return int(m.group(1)) if m else None


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


def extract_ancestries(foundry_ancestries, aon_idx, p2t_idx, heritage_map, relatorio):
    records = []
    for slug, d in sorted(foundry_ancestries.items()):
        s = d["system"]
        name = d["name"]
        pub = s.get("publication", {})
        is_remaster = bool(pub.get("remaster"))

        candidates = aon_idx.get(name.strip().lower(), [])
        aon_doc, match_kind = pick_aon_doc(candidates, is_remaster)
        if aon_doc is None:
            relatorio["ancestry_sem_aon"].append(name)

        prov = {}

        # --- name/traits/rarity/source: aon vence, fallback foundry ---
        if aon_doc:
            out_name = aon_doc.get("name", name)
            prov["name"] = "aon"
            traits = aon_doc.get("trait") or list(s.get("traits", {}).get("value", []))
            prov["traits"] = "aon"
            rarity = aon_doc.get("rarity") or s.get("traits", {}).get("rarity")
            prov["rarity"] = "aon"
        else:
            out_name = name
            prov["name"] = "foundry"
            traits = list(s.get("traits", {}).get("value", []))
            prov["traits"] = "foundry"
            rarity = s.get("traits", {}).get("rarity")
            prov["rarity"] = "foundry"

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
            aon_boosts = {ability_short(a) for a in (aon_doc.get("attribute") or []) if a.lower() != "free"}
            fnd_boosts = set()
            for _, slot in s.get("boosts", {}).items():
                v = slot.get("value", [])
                if 1 <= len(v) < 6:
                    fnd_boosts.update(v)
            if aon_boosts and aon_boosts != fnd_boosts:
                conflitos.append({
                    "campo": "boosts_fixos", "foundry": sorted(fnd_boosts),
                    "aon": sorted(aon_boosts), "escolhido": "foundry",
                })
            aon_flaw = {ability_short(a) for a in (aon_doc.get("attribute_flaw") or [])}
            fnd_flaw = set(flaw["ability_flaw"]["opcoes"]) if flaw else set()
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


def extract_heritages(foundry_heritages, aon_idx, relatorio):
    records = []
    for slug, d in sorted(foundry_heritages.items()):
        s = d["system"]
        name = d["name"]
        pub = s.get("publication", {})
        is_remaster = bool(pub.get("remaster"))
        anc = s.get("ancestry")
        ancestry_id = f"wb:ancestry/{anc['slug']}" if anc else None

        candidates = aon_idx.get(name.strip().lower(), [])
        aon_doc, _ = pick_aon_doc(candidates, is_remaster)
        if aon_doc is None:
            relatorio["heritage_sem_aon"].append(name)

        prov = {}
        if aon_doc:
            out_name = aon_doc.get("name", name)
            prov["name"] = "aon"
            traits = aon_doc.get("trait") or list(s.get("traits", {}).get("value", []))
            prov["traits"] = "aon"
            rarity = aon_doc.get("rarity") or s.get("traits", {}).get("rarity")
            prov["rarity"] = "aon"
        else:
            out_name = name
            prov["name"] = "foundry"
            traits = list(s.get("traits", {}).get("value", []))
            prov["traits"] = "foundry"
            rarity = s.get("traits", {}).get("rarity")
            prov["rarity"] = "foundry"

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


def extract_backgrounds(foundry_backgrounds, aon_idx, p2t_idx, relatorio):
    records = []
    for slug, d in sorted(foundry_backgrounds.items()):
        s = d["system"]
        name = d["name"]
        pub = s.get("publication", {})
        is_remaster = bool(pub.get("remaster"))

        candidates = aon_idx.get(name.strip().lower(), [])
        aon_doc, _ = pick_aon_doc(candidates, is_remaster)
        if aon_doc is None:
            relatorio["background_sem_aon"].append(name)

        prov = {}
        if aon_doc:
            out_name = aon_doc.get("name", name)
            prov["name"] = "aon"
            traits = aon_doc.get("trait") or list(s.get("traits", {}).get("value", []))
            prov["traits"] = "aon"
            rarity = aon_doc.get("rarity") or s.get("traits", {}).get("rarity")
            prov["rarity"] = "aon"
        else:
            out_name = name
            prov["name"] = "foundry"
            traits = list(s.get("traits", {}).get("value", []))
            prov["traits"] = "foundry"
            rarity = s.get("traits", {}).get("rarity")
            prov["rarity"] = "foundry"

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


def build_legacy_remaster_map(aon_docs, foundry_names, kind):
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
    }

    records = []
    records += extract_ancestries(foundry_ancestries, aon_anc_idx, p2t_anc_idx, heritage_map, relatorio)
    records += extract_heritages(foundry_heritages, aon_her_idx, relatorio)
    records += extract_backgrounds(foundry_backgrounds, aon_bg_idx, p2t_bg_idx, relatorio)

    # anexa o mapa legacy->remaster e o relatorio como atributo da funcao,
    # pra quem quiser gerar o relatorio sem reprocessar tudo
    anc_renamed, anc_removed = build_legacy_remaster_map(
        aon_ancestries, foundry_name_set(foundry_ancestries), "ancestry")
    her_renamed, her_removed = build_legacy_remaster_map(
        aon_heritages, foundry_name_set(foundry_heritages), "heritage")
    bg_renamed, bg_removed = build_legacy_remaster_map(
        aon_backgrounds, foundry_name_set(foundry_backgrounds), "background")

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


if __name__ == "__main__":
    from gerar_relatorio_ancestrias import main as gerar_relatorio
    registros = extrair()
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAIDA_DIR / "ancestrias.json", "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=2)
    print(f"gravados {len(registros)} registros em {SAIDA_DIR / 'ancestrias.json'}")
    gerar_relatorio(registros, extrair.ultimo_relatorio)
