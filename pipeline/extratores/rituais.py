"""
Extrator canonico de RITUAIS (kind=ritual) para o Waybuilder.

Rituais entraram na spec depois (ver specs/2026-07-26-schema-base.md, secao
"Kinds em escopo"): omissao ao escrever a lista original, nao falha de
extrator. Zero registros em 18.176 antes deste extrator.

Fontes fixadas (ver pipeline/dados_brutos/foundry/PIN pro commit pinado):
  - foundry:   foundryvtt/pf2e, commit 87f9e5028baaa10b70fdc766260b7886def17e04
               packs/pf2e/spells/rituals/**  (150 docs, type="spell" com bloco
               system.ritual proprio -- pasta copiada pra dados_brutos/ neste
               extrator porque magias.py explicitamente a deixou de fora,
               "rituais excluidos: categoria separada na AoN, fora do escopo
               desta extracao")
  - aon:       dump local do Elasticsearch aonprd.com, category=ritual (201 docs,
               legado + remaster juntos; deduplicados aqui via remaster_id/legacy_id,
               mesmo algoritmo de magias.py) -- pipeline/dados_brutos/aon_rituals.json,
               gerado por _dump_aon_rituais.py
  - pf2etools: INDISPONIVEL para rituais. pipeline/dados_brutos/pf2etools/ tem
               spells-*.json mas nenhum ritual dentro (nao baixado nesta rodada,
               nao existe arquivo rituals-*.json no dump local). Cross-check de
               `level` cai para foundry-vs-aon (as duas fontes independentes que
               existem), documentado no relatorio.

Cobertura: ao contrario de magias (onde AoN e superset e dirige o loop), aqui
o Foundry tem MAIS conceitos unicos que o AoN canonico (150 vs 145 pos-dedupe):
6 rituais de Adventure Path/PFS scenario que a AoN nao indexa em category=ritual,
e 1 ritual (Rite of the Blood Crown) so na AoN sem par no Foundry. Por isso este
extrator itera a UNIAO dos nomes normalizados das duas fontes, no lugar de usar
uma fonte como loop principal e a outra so como lookup -- outra decisao ja
documentada no relatorio.

Precedencia por campo (ver specs/2026-07-26-schema-base.md):
  - defesa, heightened, escalonamento_de_dano, acoes/alcance/area/duracao -> foundry
    (mecanica executavel, rule elements) -- mesmos campos e mesma logica de magias.py,
    reaproveitados via import (ritual e spell no Foundry: mesmo schema system.*)
  - text, name, traits, rarity, source/remaster -> aon (Paizo, mais completa)
  - level -> foundry, conferido contra aon (pf2etools indisponivel pra rituais)
  - traits -> UNIAO das fontes (regra nova da spec, nao precedencia -- ver merge_traits).
    Mapa legado->remaster lido de pipeline/normalizacao_traits.json (fonte
    compartilhada entre extratores, nao hardcoded aqui).

Campos proprios de ritual (nao existem em magias.py, empacotados no bloco
"ritual" pra nao poluir o envelope -- ver relatorio pra justificativa completa
dos nomes em ingles, termos do proprio stat block de PF2e):
  cast, cost, secondary_casters, secondary_casters_note, primary_check,
  secondary_checks, requirements, results (por grau de sucesso).

mechanized e sempre False: ritual nao tem `grants` (nada que o builder calcule
pra personagem -- e conhecimento/utilidade resolvido na mesa), mesmo quando ha
dado estrutural do Foundry (tempo, custo, pericias). Ver spec: "mechanized: false
nao e lacuna, e caso normal."

stdlib-only. Le pipeline/dados_brutos/ e pipeline/normalizacao_traits.json
(offline, sem rede).
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import magias  # noqa: E402  -- reaproveita slugify/norm_name/strip_html/foundry_* (mesmo schema Foundry)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(BASE_DIR, "dados_brutos")
FOUNDRY_RITUALS_DIR = os.path.join(DADOS, "foundry", "spells", "rituals")
AON_RITUALS_FILE = os.path.join(DADOS, "aon_rituals.json")
NORMALIZACAO_TRAITS_FILE = os.path.join(BASE_DIR, "normalizacao_traits.json")


# --------------------------------------------------------------------------
# Uniao de traits (regra nova da spec -- ver "traits e uniao, nao precedencia")
# --------------------------------------------------------------------------

def _load_legacy_to_remaster_traits() -> dict:
    """Mapa legado -> remaster, fonte unica pipeline/normalizacao_traits.json
    (17 renomeados com prov por entrada). Nao hardcoded aqui -- esse arquivo e
    compartilhado entre extratores e e a fonte de verdade da regra 1 da spec.
    `removidos_sem_sucessor` (9 traits de escola/alinhamento que sumiram sem
    substituto) fica so documentado, nao filtrado daqui: mante-los na uniao
    preserva a informacao legado (a spec pede "nada e descartado"), e o proprio
    arquivo existe justamente pra essa divergencia nao ser lida como colisao
    de identidade (portao de qualidade 6) -- ver relatorio."""
    with open(NORMALIZACAO_TRAITS_FILE, encoding="utf-8") as f:
        return json.load(f)["renomeados"]


LEGACY_TO_REMASTER_TRAITS = _load_legacy_to_remaster_traits()

RARITY_WORDS = {"common", "uncommon", "rare", "unique"}

_PARAM_SUFFIX_RE = re.compile(r"^(.+?)-(?:aim-d\d+|d\d+|\d+)$")


def _absorb_granularity(traits: set[str]) -> set[str]:
    """Trait parametrizado absorve o base (ex: two-hand-d12 absorve two-hand)."""
    bases_with_param = set()
    for t in traits:
        m = _PARAM_SUFFIX_RE.match(t)
        if m:
            bases_with_param.add(m.group(1))
    return traits - bases_with_param


def merge_traits(foundry_traits: list[str] | None, aon_traits: list[str] | None) -> tuple[list[str], list[str], list[str]]:
    """Uniao das tres regras da spec. Retorna (traits, fontes_contribuintes, aliases_legado)."""
    f = {t.lower() for t in (foundry_traits or [])}
    a = {t.lower() for t in (aon_traits or []) if t.lower() not in RARITY_WORDS}

    aliases = set()

    def map_legacy(s: set[str]) -> set[str]:
        out = set()
        for t in s:
            mapped = LEGACY_TO_REMASTER_TRAITS.get(t)
            if mapped:
                out.add(mapped)
                aliases.add(t)
            else:
                out.add(t)
        return out

    union = _absorb_granularity(map_legacy(f) | map_legacy(a))

    fontes = []
    if f:
        fontes.append("foundry")
    if a:
        fontes.append("aon")

    return sorted(union), fontes, sorted(aliases)


# --------------------------------------------------------------------------
# Carga: foundry
# --------------------------------------------------------------------------

def load_foundry_rituals() -> list[dict]:
    """Rituais do Foundry.

    Nao existe pasta `rituals/` no repo: ritual e uma magia com o bloco
    `system.ritual` preenchido, dentro de `packs/pf2e/spells/`. O caminho antigo
    (`dados_brutos/foundry/spells/rituals/`) era um recorte feito a mao numa
    sessao anterior; quando ele sumiu, a funcao passou a devolver lista vazia em
    silencio e 6 rituais **exclusivos do Foundry** sumiram da base --
    `Unfettered Mark`, `Destroy Mindscape` e outros 4 de Adventure Path, que o
    AoN nao indexa em `category=ritual`.
    """
    candidatos = [
        os.environ.get("WB_FOUNDRY_PACKS", ""),
        os.path.join(DADOS, "foundry_repo", "packs", "pf2e"),
    ]
    docs, vistos = [], set()
    for raiz in candidatos:
        if not raiz or not os.path.isdir(os.path.join(raiz, "spells")):
            continue
        for path in glob.glob(os.path.join(raiz, "spells", "**", "*.json"),
                              recursive=True):
            try:
                with open(path, encoding="utf-8") as f:
                    d = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(d, dict) or d.get("type") != "spell":
                continue
            if not (d.get("system") or {}).get("ritual"):
                continue
            if d.get("_id") in vistos:
                continue
            vistos.add(d.get("_id"))
            docs.append(d)
        break

    # recorte antigo, se ainda existir -- nunca perde o que ja tinha
    for path in glob.glob(os.path.join(FOUNDRY_RITUALS_DIR, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(d, dict) and d.get("type") == "spell" and d.get("_id") not in vistos:
            vistos.add(d.get("_id"))
            docs.append(d)

    if not docs:
        print("  ! nenhum ritual do Foundry encontrado -- rode buscar_fontes.sh",
              file=sys.stderr)
    return docs


# --------------------------------------------------------------------------
# Carga: AoN
# --------------------------------------------------------------------------

def load_aon_rituals() -> list[dict]:
    with open(AON_RITUALS_FILE, encoding="utf-8") as f:
        return json.load(f)


def dedupe_aon_legacy_remaster(docs: list[dict]) -> tuple[list[dict], dict]:
    """Mesmo algoritmo de magias.py (ver docstring la): doc com legacy_id
    preenchido = versao remaster, canonica. Doc consumido como legado fica em
    xref.aon_legacy do canonico."""
    by_id = {d["id"]: d for d in docs if d.get("id")}
    legacy_of = {}
    consumed_as_legacy = set()

    for d in docs:
        rid_list = d.get("remaster_id") or []
        if rid_list and rid_list[0] in by_id:
            consumed_as_legacy.add(d["id"])

    canonical = [d for d in docs if d["id"] not in consumed_as_legacy]

    for d in docs:
        rid_list = d.get("remaster_id") or []
        if rid_list and rid_list[0] in by_id:
            legacy_of[rid_list[0]] = d

    return canonical, legacy_of


# --------------------------------------------------------------------------
# Resultado por grau de sucesso (bloco proprio de ritual -- ver relatorio)
# --------------------------------------------------------------------------

_DEGREE_KEYS = {
    "Critical Success": "critical_success",
    "Success": "success",
    "Failure": "failure",
    "Critical Failure": "critical_failure",
}
_DEGREE_MARK_RE = re.compile(r"<strong>(Critical Success|Success|Failure|Critical Failure)</strong>")


def parse_degree_of_success(html: str) -> dict:
    """Extrai o texto associado a cada grau de sucesso (Critical Success/Success/
    Failure/Critical Failure), na ordem em que aparecem no HTML. So os 4 rotulos
    canonicos contam como marcador -- qualquer outro <strong> no meio (ex:
    'Onset', 'Heightened (+1)') fica dentro do texto do grau anterior."""
    if not html:
        return {}
    marks = list(_DEGREE_MARK_RE.finditer(html))
    if not marks:
        return {}
    out = {}
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(html)
        chunk = html[start:end]
        text = magias.strip_html(chunk).strip(" .:\n")
        key = _DEGREE_KEYS[m.group(1)]
        if key in out:  # rotulo repetido (raro) -- concatena
            out[key] = out[key] + " " + text
        else:
            out[key] = text
    return out


_DEGREE_MARK_PLAIN_RE = re.compile(r"\b(Critical Success|Success|Failure|Critical Failure)\b")


def parse_degree_of_success_plain(text: str) -> dict:
    """Mesma ideia de parse_degree_of_success, mas pro texto plano da AoN (sem
    tag html). So entra em jogo quando o foundry nao tem HTML de descricao pra
    aquele ritual (stub vazio) mas a AoN tem a prosa completa -- caso de 4
    rituais do Season of Ghosts no foundry pinado. Restrito ao trecho depois do
    separador '---' (fronteira entre stat block e prosa na AoN) pra nao casar
    'Success'/'Failure' soltos em outro lugar do texto."""
    if not text or "---" not in text:
        return {}
    prose = text.split("---", 1)[1]
    marks = list(_DEGREE_MARK_PLAIN_RE.finditer(prose))
    if not marks:
        return {}
    out = {}
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(prose)
        key = _DEGREE_KEYS[m.group(1)]
        chunk = prose[start:end].strip()
        if key in out:
            out[key] = out[key] + " " + chunk
        else:
            out[key] = chunk
    return out


# --------------------------------------------------------------------------
# Extracao principal
# --------------------------------------------------------------------------

def extrair() -> list[dict]:
    """Extrai a lista canonica de rituais (kind=ritual). Cada registro traz
    'text' (id de referencia wb:text/ritual/<slug>, por contrato do schema-base)
    e 'texto' (a prosa em si, embutida aqui pelo mesmo motivo de magias.py --
    o split index/text/<kind>.json e passo de build multi-kind posterior)."""
    foundry_docs = load_foundry_rituals()
    foundry_by_name: dict[str, dict] = {}
    for d in foundry_docs:
        foundry_by_name[magias.norm_name(d["name"])] = d

    aon_docs = load_aon_rituals()
    aon_canonical, aon_legacy_of = dedupe_aon_legacy_remaster(aon_docs)
    aon_by_name: dict[str, dict] = {magias.norm_name(d["name"]): d for d in aon_canonical}

    # uniao dos nomes das duas fontes -- ao contrario de magias.py, aqui o
    # Foundry tem conceitos que a AoN nao indexa em category=ritual (ver
    # docstring do modulo), entao nenhuma das duas pode ser o loop unico.
    all_keys = sorted(set(foundry_by_name) | set(aon_by_name))

    registros = []

    for key in all_keys:
        fdoc = foundry_by_name.get(key)
        fsys = fdoc["system"] if fdoc else None
        aon = aon_by_name.get(key)

        name = aon["name"] if aon else fdoc["name"]
        slug = magias.slugify(name)
        wb_id = f"wb:ritual/{slug}"

        legacy_doc = aon_legacy_of.get(aon["id"]) if aon else None

        prov: dict[str, str] = {}
        conflitos = []

        # --- name (aon vence quando existe, senao foundry) ---
        prov["name"] = "aon" if aon else "foundry"

        # --- rarity (aon vence; foundry como fallback quando aon nao existe) ---
        rarity = aon.get("rarity") if aon else None
        if not rarity and fsys:
            rarity = fsys["traits"].get("rarity")
            prov["rarity"] = "foundry" if rarity else None
        elif rarity:
            prov["rarity"] = "aon"

        # --- traits: uniao, nao precedencia ---
        foundry_traits_raw = fsys["traits"]["value"] if fsys else None
        aon_traits_raw = aon.get("trait") if aon else None
        traits, traits_fontes, aliases_traits = merge_traits(foundry_traits_raw, aon_traits_raw)
        if traits_fontes:
            prov["traits"] = traits_fontes

        # --- source / license / remaster (aon vence pro livro/pagina/remaster;
        # license so existe no foundry, como em magias.py) ---
        source_book = None
        source_page = None
        prov_source = None
        if aon:
            source_book = aon.get("primary_source") or (aon.get("source") or [None])[0]
            if source_book:
                source_book = source_book.strip()  # achado: alguns titulos da AoN vem com \r\n colado
            raw = aon.get("primary_source_raw") or aon.get("text") or ""
            m = re.search(r"pg\.\s*(\d+)", raw)
            if m:
                source_page = int(m.group(1))
            if source_book:
                prov_source = "aon"
        if not source_book and fsys:
            source_book = fsys["publication"]["title"].strip()
            prov_source = "foundry"
        license_ = fsys["publication"]["license"] if fsys else None
        is_remaster_aon = bool(aon.get("legacy_id")) if aon else False
        source = {
            "book": source_book,
            "page": source_page,
            "license": license_,
            "remaster": bool(fsys["publication"]["remaster"]) if fsys else is_remaster_aon,
        }
        prov["source"] = prov_source

        # --- level (foundry vence, conferido contra aon -- pf2etools indisponivel) ---
        foundry_level = fsys["level"]["value"] if fsys else None
        aon_level = aon.get("level") if aon else None
        level = foundry_level if foundry_level is not None else aon_level
        prov["level"] = "foundry" if foundry_level is not None else ("aon" if aon_level is not None else None)
        if foundry_level is not None and aon_level is not None and foundry_level != aon_level:
            conflitos.append({"campo": "level", "foundry": foundry_level, "aon": aon_level, "escolhido": "foundry"})

        # --- campos mecanicos compartilhados com spell (foundry vence) ---
        acoes = fsys["time"]["value"] if fsys else (aon.get("actions") if aon else None)
        prov["acoes"] = "foundry" if (fsys and fsys["time"]["value"]) else ("aon" if aon and aon.get("actions") else None)
        alcance = None
        if fsys and fsys.get("range", {}).get("value"):
            alcance = fsys["range"]["value"]
            prov["alcance"] = "foundry"
        elif aon and aon.get("range_raw"):
            alcance = aon["range_raw"]
            prov["alcance"] = "aon"
        area = None
        if fsys and fsys.get("area"):
            area = {"tipo": fsys["area"].get("type"), "valor": fsys["area"].get("value")}
            prov["area"] = "foundry"
        duracao = None
        if fsys and fsys.get("duration") and (fsys["duration"].get("value") or fsys["duration"].get("sustained")):
            duracao = {"valor": fsys["duration"].get("value") or None, "sustentada": fsys["duration"].get("sustained", False)}
            prov["duracao"] = "foundry"

        defesa, defesa_motivo = (None, "sem-foundry")
        if fsys:
            defesa, defesa_motivo = magias.foundry_defense(fsys, fsys["traits"]["value"])
        prov["defesa"] = defesa_motivo if fsys else None

        heightened, heightened_motivo = ([], "sem-foundry")
        if fsys:
            heightened, heightened_motivo = magias.foundry_heightened(fsys, fsys.get("damage") or {})
        prov["heightened"] = heightened_motivo if fsys else None

        escalonamento = magias.foundry_escalonamento(fsys) if fsys else None
        prov["escalonamento_de_dano"] = "foundry" if escalonamento else None

        desc_html = fsys["description"]["value"] if fsys else ""  # aon nao traz HTML, so texto plano
        heightened_only_prosa = bool(re.search(r"Heightened\s*\(", desc_html or "")) and not heightened

        # --- texto (aon vence; foundry description como fallback) ---
        if aon and aon.get("text"):
            texto_plain = aon["text"].strip()
            prov["text"] = "aon"
        elif fsys:
            texto_plain = magias.strip_html(desc_html)
            prov["text"] = "foundry"
        else:
            texto_plain = ""
            prov["text"] = None
        text_ref = f"wb:text/ritual/{slug}"

        # --- bloco proprio de ritual (prov granular por sub-campo nao vale a
        # pena aqui -- prov["ritual"] cobre o bloco inteiro, como magias.py faz
        # com "area"/"duracao") ---
        cost = fsys.get("cost", {}).get("value") if fsys else (aon.get("cost") if aon else None)
        cost = cost or None

        primary_check = None
        secondary_checks = None
        prov_ritual_block = None
        foundry_secondary_casters = None
        if fsys and fsys.get("ritual"):
            rit = fsys["ritual"]
            primary_check = (rit.get("primary") or {}).get("check") or None
            secondary_checks = (rit.get("secondary") or {}).get("checks") or None
            foundry_secondary_casters = (rit.get("secondary") or {}).get("casters")
            prov_ritual_block = "foundry"
        elif aon:
            primary_check = (aon.get("primary_check") or "").strip() or None
            secondary_checks = (aon.get("secondary_check") or "").strip() or None
            prov_ritual_block = "aon"

        # secondary_casters: achado na extracao -- o foundry usa 0 tambem como
        # placeholder pra "quantidade variavel/qualificada" (nao so pra "zero
        # ajudantes"), e nunca diverge da AoN quando o numero e um inteiro fixo
        # de verdade (168 comparados, 13 divergiam, as 13 TODAS com foundry=0).
        # Por isso so pra este sub-campo o foundry NAO vence quando vale 0:
        # cai pro numero parseado da AoN, com o texto excedente (ex: "must be
        # the ritual's target", "up to 5") preservado em secondary_casters_note.
        aon_secondary_casters = aon.get("secondary_casters") if aon else None
        aon_casters_raw = (aon.get("secondary_casters_raw") or "") if aon else ""
        secondary_casters_note = None
        if aon_casters_raw:
            resto = aon_casters_raw.split(",", 1)
            candidato_nota = resto[1].strip() if len(resto) > 1 else None
            # sem virgula mas com texto alem do numero puro (ex: "up to 5", "1 to 9")
            if candidato_nota is None and aon_secondary_casters is not None \
                    and aon_casters_raw.strip() != str(aon_secondary_casters):
                candidato_nota = aon_casters_raw.strip()
            secondary_casters_note = candidato_nota

        if foundry_secondary_casters is not None and foundry_secondary_casters != 0:
            secondary_casters = foundry_secondary_casters
            if aon_secondary_casters is not None and aon_secondary_casters != foundry_secondary_casters:
                conflitos.append({
                    "campo": "ritual.secondary_casters", "foundry": foundry_secondary_casters,
                    "aon": aon_secondary_casters, "escolhido": "foundry",
                })
        elif aon_secondary_casters is not None:
            secondary_casters = aon_secondary_casters
            if foundry_secondary_casters == 0:
                conflitos.append({
                    "campo": "ritual.secondary_casters", "foundry": 0,
                    "aon": aon_secondary_casters,
                    "escolhido": "aon (foundry=0 e placeholder de quantidade variavel, ver LOG)",
                })
        else:
            secondary_casters = foundry_secondary_casters  # None, ou 0 legitimo sem info da AoN pra contestar

        requirements = fsys.get("requirements") if fsys else None
        requirements = requirements or None

        results = parse_degree_of_success(desc_html) if desc_html else {}
        if not results and aon and aon.get("text"):
            results = parse_degree_of_success_plain(aon["text"])

        ritual_block = {
            "cast": acoes,
            "cost": cost,
            "secondary_casters": secondary_casters,
            "secondary_casters_note": secondary_casters_note,
            "primary_check": primary_check,
            "secondary_checks": secondary_checks,
            "requirements": requirements,
            "results": results,
        }
        if prov_ritual_block:
            prov["ritual"] = prov_ritual_block

        # --- xref ---
        xref = {}
        if aon:
            xref["aon"] = aon["id"]
        if legacy_doc:
            xref["aon_legacy"] = legacy_doc["id"]
        if fdoc:
            xref["foundry"] = f"Compendium.pf2e.spells-rituals.Item.{fdoc['_id']}"

        registro = {
            "id": wb_id,
            "kind": "ritual",
            "name": name,
            "level": level,
            "traits": traits,
            "aliases_traits": aliases_traits,
            "rarity": rarity,
            "source": source,
            "acoes": acoes,
            "alcance": alcance,
            "area": area,
            "duracao": duracao,
            "heightened": heightened,
            "heightened_so_prosa": heightened_only_prosa,
            "defesa": defesa,
            "escalonamento_de_dano": escalonamento,
            "ritual": ritual_block,
            "text": text_ref,
            "texto": texto_plain,
            "mechanized": False,
            "xref": xref,
            "prov": {k: v for k, v in prov.items() if v is not None},
        }
        if conflitos:
            registro["conflitos"] = conflitos

        registros.append(registro)

    return registros


if __name__ == "__main__":
    regs = extrair()
    saida = os.path.join(BASE_DIR, "saida", "rituais.json")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", encoding="utf-8") as fh:
        json.dump(regs, fh, ensure_ascii=False, indent=2)
    print(f"{len(regs)} registros extraidos -> {saida}")
