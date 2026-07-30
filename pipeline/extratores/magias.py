"""
Extrator canonico de MAGIAS (kind=spell) para o Waybuilder.

Fontes fixadas (ver pipeline/dados_brutos/foundry/PIN pro commit pinado):
  - foundry:   foundryvtt/pf2e, commit 87f9e5028baaa10b70fdc766260b7886def17e04
               packs/pf2e/spells/{spells,focus}/**  (rituais excluidos: categoria
               separada na AoN, fora do escopo desta extracao)
  - aon:       dump local do Elasticsearch aonprd.com, category=spell (2.461 docs,
               legado + remaster juntos; deduplicados aqui via remaster_id/legacy_id)
  - pf2etools: Pf2eToolsOrg/Pf2eTools, branch dev, data/spells/spells-*.json (58 arquivos)

Precedencia por campo (ver specs/2026-07-26-schema-base.md):
  - heightened, defesa, escalonamento_de_dano, acoes/alcance/area/duracao -> foundry
    (mecanica executavel, rank numerico e rule elements)
  - text, name, traits, rarity, source/remaster -> aon (Paizo, mais completa)
  - rank (level) -> foundry, conferido contra pf2etools; divergencia vira conflito
  - tradicoes -> foundry, conferido contra pf2etools

stdlib-only. Le apenas pipeline/dados_brutos/ (offline, sem rede).
"""
from __future__ import annotations

import glob
import json
import os
import re
import unicodedata
import sys
from html.parser import HTMLParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(BASE_DIR, "dados_brutos")
FOUNDRY_SPELLS_DIR = os.path.join(DADOS, "foundry", "spells")
AON_SPELLS_FILE = os.path.join(DADOS, "aon_spells.json")  # lista flat de _source, mesmo padrao de aon_feats.json etc.
PF2ETOOLS_DIR = os.path.join(DADOS, "pf2etools")

sys.path.insert(0, BASE_DIR)
import comum  # noqa: E402


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def slugify(name: str) -> str:
    # NFKD antes do corte: sem isto o acento vira caractere invalido e a letra
    # some junto -- `Deja Vu` (com acento) saia como `wb:spell/d-j-vu`, e
    # qualquer referencia pelo nome limpo ficava orfa. Era 1 registro de 1.655,
    # mas o defeito e da funcao e nao do registro: a proxima magia acentuada
    # cairia igual. Mesma normalizacao que `aon_kinds.slug` ja usava.
    s = unicodedata.normalize("NFKD", str(name or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().strip()
    s = s.replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def norm_name(name: str) -> str:
    """Normaliza nome pra casamento entre fontes (case/pontuacao insensitive)."""
    s = name.lower().strip()
    s = s.replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        return "".join(self.parts)


def strip_html(html: str) -> str:
    if not html:
        return ""
    p = _HTMLStripper()
    p.feed(html)
    text = p.get_text()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


_DIE_RE = re.compile(r"(\d+)d(\d+)(?:([+-]\d+))?")


def dice_average(formula: str) -> float:
    """Media de uma formula de dados tipo '2d6+3' ou '1d6'. Soma termos separados por + entre grupos."""
    if not formula:
        return 0.0
    total = 0.0
    for m in _DIE_RE.finditer(formula):
        n, die, mod = int(m.group(1)), int(m.group(2)), m.group(3)
        total += n * (die + 1) / 2
        if mod:
            total += int(mod)
    if not _DIE_RE.search(formula):
        # formula so numerica, ex: "1" (splash)
        try:
            total += float(formula)
        except ValueError:
            pass
    return total


# --------------------------------------------------------------------------
# Carga: foundry
# --------------------------------------------------------------------------

def load_foundry_spells() -> list[dict]:
    docs = []
    for sub in ("spells", "focus"):
        pattern = os.path.join(FOUNDRY_SPELLS_DIR, sub, "**", "*.json")
        for path in glob.glob(pattern, recursive=True):
            with open(path, encoding="utf-8") as f:
                try:
                    d = json.load(f)
                except json.JSONDecodeError:
                    continue
            if not isinstance(d, dict) or d.get("type") != "spell":
                continue
            d["_source_kind"] = sub  # "spells" ou "focus"
            docs.append(d)
    return docs


def foundry_defense(system: dict, traits_value: list[str]) -> tuple[dict | None, str]:
    """Retorna (defesa, motivo) a partir de system.defense + traits."""
    df = system.get("defense")
    if df:
        save = df.get("save")
        if save:
            return {"save": save.get("statistic"), "basico": bool(save.get("basic"))}, "foundry:defense.save"
        passive = df.get("passive")
        if passive:
            stat = passive.get("statistic") or ""
            if stat == "ac":
                return {"ataque": True}, "foundry:defense.passive-ac"
            if stat.endswith("-dc"):
                return {"save": stat[:-3], "basico": False}, "foundry:defense.passive-dc"
    if "attack" in traits_value:
        return {"ataque": True}, "foundry:trait-attack"
    return None, "foundry:none"


def foundry_heightened(system: dict, damage: dict) -> tuple[list[dict], str]:
    h = system.get("heightening")
    if not h:
        return [], "foundry:none"
    tipo = h.get("type")
    out = []
    if tipo == "interval":
        passo = h.get("interval", 1)
        efeito_parts = []
        for key, delta in (h.get("damage") or {}).items():
            base_type = None
            if key in damage:
                base_type = damage[key].get("type")
            if base_type:
                efeito_parts.append(f"+{delta} {base_type}")
            else:
                efeito_parts.append(f"+{delta}")
        area_delta = h.get("area")
        if area_delta:
            efeito_parts.append(f"+{area_delta} ft area")
        if not efeito_parts:
            efeito_parts.append("(ver texto)")
        out.append({"tipo": "incremental", "passo": passo, "efeito": ", ".join(efeito_parts)})
        return out, "foundry:heightening.interval"
    if tipo == "fixed":
        levels = h.get("levels", {})
        for rank_str, override in sorted(levels.items(), key=lambda kv: int(kv[0])):
            efeito_parts = []
            ov_damage = override.get("damage")
            if ov_damage:
                for key, dval in ov_damage.items():
                    if isinstance(dval, dict):
                        formula = dval.get("formula")
                        dtype = dval.get("type")
                        if formula and dtype:
                            efeito_parts.append(f"{formula} {dtype}")
                        elif formula:
                            efeito_parts.append(formula)
                        elif dtype:
                            efeito_parts.append(f"tipo->{dtype}")
                    else:
                        efeito_parts.append(str(dval))
            ov_area = override.get("area")
            if ov_area:
                efeito_parts.append(f"area {ov_area.get('value')} {ov_area.get('type')}")
            ov_target = override.get("target")
            if ov_target and ov_target.get("value"):
                efeito_parts.append(f"alvo: {ov_target['value']}")
            if not efeito_parts:
                efeito_parts.append("(ver texto)")
            out.append({"tipo": "fixo", "rank": int(rank_str), "efeito": "; ".join(efeito_parts)})
        return out, "foundry:heightening.fixed"
    return [], "foundry:unknown-type"


def foundry_escalonamento(system: dict) -> dict | None:
    damage = system.get("damage") or {}
    if not damage:
        return None
    base = []
    for key, entry in damage.items():
        base.append({
            "formula": entry.get("formula"),
            "tipo": entry.get("type"),
            "categoria": entry.get("category"),
            "kinds": entry.get("kinds", []),
        })
    h = system.get("heightening") or {}
    incremento = None
    if h.get("type") == "interval" and h.get("damage"):
        incremento = {
            "tipo": "incremental",
            "passo": h.get("interval", 1),
            "por_entrada": [{"chave": k, "delta": v} for k, v in h["damage"].items()],
        }
    elif h.get("type") == "fixed":
        por_rank = {}
        for rank_str, override in (h.get("levels") or {}).items():
            if override.get("damage"):
                por_rank[rank_str] = override["damage"]
        if por_rank:
            incremento = {"tipo": "fixo", "por_rank": por_rank}
    return {"dano_base": base, "incremento": incremento}


def escalonamento_ganho_medio_por_rank(esc: dict) -> float | None:
    """Media (soma das medias de dado) do ganho por rank, pra rankear 'escalonamento mais forte'."""
    if not esc or not esc.get("incremento"):
        return None
    inc = esc["incremento"]
    total = 0.0
    if inc["tipo"] == "incremental":
        passo = inc.get("passo") or 1
        for item in inc["por_entrada"]:
            total += dice_average(str(item["delta"])) / passo
    elif inc["tipo"] == "fixo":
        # media do ganho entre ranks consecutivos registrados
        base_avg = sum(dice_average(d.get("formula", "")) for d in esc["dano_base"])
        ranks = sorted(int(r) for r in inc["por_rank"].keys())
        if not ranks:
            return None
        prev_avg = base_avg
        prev_rank = None
        gains = []
        for r in ranks:
            entry = inc["por_rank"][str(r)]
            cur_avg = 0.0
            matched_any = False
            for key, dval in entry.items():
                if isinstance(dval, dict) and dval.get("formula"):
                    cur_avg += dice_average(dval["formula"])
                    matched_any = True
            if not matched_any:
                continue
            span = r - (prev_rank if prev_rank is not None else (r - 1))
            if span <= 0:
                span = 1
            gains.append((cur_avg - prev_avg) / span)
            prev_avg = cur_avg
            prev_rank = r
        if not gains:
            return None
        total = sum(gains) / len(gains)
    return total if total > 0 else None


# --------------------------------------------------------------------------
# Carga: AoN
# --------------------------------------------------------------------------

def load_aon_spells() -> list[dict]:
    with open(AON_SPELLS_FILE, encoding="utf-8") as f:
        return json.load(f)


def dedupe_aon_legacy_remaster(docs: list[dict]) -> tuple[list[dict], dict]:
    """
    AoN guarda legado e remaster como docs separados, ligados por remaster_id/legacy_id.
    Escolhe UM doc canonico por conceito de magia:
      - doc com legacy_id preenchido (= e a versao remaster) -> canonico
      - doc com remaster_id apontando pra um doc existente no set -> descartado como
        standalone, mas guardado como xref/legado do canonico
      - doc sem nenhum dos dois, ou cujo remaster_id nao existe no set -> canonico
        (magia so-legado, nunca remasterizada, ou so-remaster nova)
    Retorna (lista_canonicos, mapa_id->doc_legado_correspondente)
    """
    by_id = {d["id"]: d for d in docs if d.get("id")}
    legacy_of = {}  # canonical_id -> legacy_doc
    canonical = []
    consumed_as_legacy = set()

    for d in docs:
        rid_list = d.get("remaster_id") or []
        if rid_list:
            target_id = rid_list[0]
            if target_id in by_id:
                consumed_as_legacy.add(d["id"])

    for d in docs:
        if d["id"] in consumed_as_legacy:
            continue
        canonical.append(d)

    for d in docs:
        rid_list = d.get("remaster_id") or []
        if rid_list and rid_list[0] in by_id:
            legacy_of[rid_list[0]] = d

    return canonical, legacy_of


# --------------------------------------------------------------------------
# Carga: pf2etools
# --------------------------------------------------------------------------

def load_pf2etools_spells() -> dict:
    """Retorna nome_normalizado -> lista de entradas (pode haver reprints)."""
    by_name = {}
    for path in sorted(glob.glob(os.path.join(PF2ETOOLS_DIR, "spells-*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for s in data.get("spell", []):
            key = norm_name(s["name"])
            by_name.setdefault(key, []).append(s)
    return by_name


# --------------------------------------------------------------------------
# Extracao principal
# --------------------------------------------------------------------------

TRADITIONS = {"arcane", "divine", "occult", "primal"}

# A9 (auditoria 2026-07-26): 463 dos 513 spells sem `tradicoes` sao focus
# spells cuja tradicao vem da classe que concede, nao da magia -- aceitavel
# por design (spec: "requires sugere, nunca bloqueia"; a tradicao real varia
# por build, ex.: Witch depende do patron escolhido). Quando o unico dado que
# aponta a origem e o trait de classe, o campo declara a derivacao em vez de
# ficar nulo ou de chutar uma tradicao especifica que pode estar errada.
CLASSES_DERIVAM_TRADICAO = {"bard", "witch", "psychic", "summoner"}


def extrair() -> list[dict]:
    """Extrai a lista canonica de magias (kind=spell). Cada registro traz
    'text' (id de referencia wb:text/spell/<slug>, por contrato do schema-base)
    e 'texto' (a prosa em si, embutida aqui porque este extrator produz um
    unico arquivo de saida -- o split index/text/<kind>.json e passo de um
    build multi-kind posterior, fora do escopo deste extrator)."""
    foundry_docs = load_foundry_spells()
    foundry_by_name: dict[str, list[dict]] = {}
    for d in foundry_docs:
        key = norm_name(d["name"])
        foundry_by_name.setdefault(key, []).append(d)

    aon_docs = load_aon_spells()
    aon_canonical, aon_legacy_of = dedupe_aon_legacy_remaster(aon_docs)
    # indice completo para os ALIASES: `aon_legacy_of` guarda UM legado por
    # canonico (o ultimo a escrever), e `Cleanse Affliction` tem TRES
    # antecessores (Neutralize Poison, Remove Disease, Remove Curse). O
    # `legacy_id` do proprio doc canonico e a lista inteira.
    aon_por_id = {str(d.get("id")): d for d in aon_docs if d.get("id")}

    pf2etools_by_name = load_pf2etools_spells()

    registros = []

    for aon in aon_canonical:
        name = aon["name"]
        slug = slugify(name)
        key = norm_name(name)
        wb_id = f"wb:spell/{slug}"

        fdocs = foundry_by_name.get(key, [])
        fdoc = fdocs[0] if fdocs else None
        fsys = fdoc["system"] if fdoc else None

        pf_entries = pf2etools_by_name.get(key, [])
        pf = pf_entries[0] if pf_entries else None

        legacy_doc = aon_legacy_of.get(aon["id"])

        prov: dict[str, str] = {}
        conflitos = []

        # --- name / rarity / traits / source (aon vence) ---
        registro_name = name
        prov["name"] = "aon"

        rarity = aon.get("rarity")
        prov["rarity"] = "aon" if rarity else None

        aon_traits = [t.lower() for t in (aon.get("trait") or [])]
        traits = aon_traits
        prov["traits"] = "aon" if traits else None

        aon_tradition = [t.lower() for t in (aon.get("tradition") or [])]

        source_book = aon.get("primary_source") or (aon.get("source") or [None])[0]
        source_page = None
        # "primary_source_raw" nao foi baixado no dump (nao estava no _source
        # filter); a pagina vem do campo "text" (formato "... Source <Livro> pg. N ...").
        m = re.search(r"pg\.\s*(\d+)", aon.get("text") or "")
        if m:
            source_page = int(m.group(1))
        is_remaster = bool(legacy_doc) or not bool(aon.get("remaster_id"))
        # regra real: se este doc TEM legacy_id -> ele E a versao remaster.
        is_remaster = bool(aon.get("legacy_id"))
        license_ = fsys["publication"]["license"] if fsys else None
        prov_source = "foundry" if fsys else None
        if not license_:
            # fallback: OGL pra fontes pre-remaster conhecidas, ORC pos Player Core.
            license_ = None
        source = {
            "book": source_book,
            "page": source_page,
            "license": license_,
            "remaster": is_remaster if fsys is None else bool(fsys["publication"]["remaster"]),
        }
        prov["source"] = prov_source or "aon"

        # --- rank (foundry vence, conferido contra pf2etools) ---
        foundry_rank = fsys["level"]["value"] if fsys else None
        aon_rank = aon.get("level")
        pf_rank = pf.get("level") if pf else None
        rank = foundry_rank if foundry_rank is not None else aon_rank
        prov["rank"] = "foundry" if foundry_rank is not None else "aon"
        if foundry_rank is not None and pf_rank is not None and foundry_rank != pf_rank:
            conflitos.append({"campo": "rank", "foundry": foundry_rank, "pf2etools": pf_rank, "aon": aon_rank, "escolhido": "foundry"})
        elif foundry_rank is None and aon_rank is not None and pf_rank is not None and aon_rank != pf_rank:
            conflitos.append({"campo": "rank", "aon": aon_rank, "pf2etools": pf_rank, "escolhido": "aon"})

        # A9 (auditoria 2026-07-26): 0 dos 1.639 spells tinha `level` -- so
        # `rank`, que e o nome remaster do campo. Um filtro de nivel no
        # cliente descartava a magia inteira em silencio. `rank` continua
        # canonico; `level` e espelho declarado com o MESMO valor (spec v2).
        level = rank
        prov["level"] = comum.prov_inferido("waybuilder", "espelho-rank")

        # --- tradicoes (foundry vence, conferido contra pf2etools/aon) ---
        # Bug corrigido (A9): `foundry_tradition == []` (o foundry TEM o campo
        # mas ele veio vazio) estava sendo tratado igual a "foundry decidiu
        # que nao ha tradicao" e nunca caia pro fallback da AoN. Fica
        # indistinguivel de fato de "sem dado nenhum" (None) so quando a AoN
        # tambem nao tem nada -- e exatamente o caso dos focus spells. Quando
        # a AoN TEM tradicao (ex.: Soulshelter Vessel, Suffocate), o campo do
        # foundry vazio nao pode vencer por precedencia vazia.
        foundry_tradition = sorted(fsys["traits"]["traditions"]) if fsys else None
        pf_tradition = sorted(t.lower() for t in pf.get("traditions", [])) if (pf and pf.get("traditions")) else None
        tradicoes = foundry_tradition if foundry_tradition else (sorted(aon_tradition) if aon_tradition else [])
        prov["tradicoes"] = "foundry" if foundry_tradition else ("aon" if aon_tradition else None)
        if foundry_tradition is not None and pf_tradition is not None and foundry_tradition != pf_tradition:
            conflitos.append({"campo": "tradicoes", "foundry": foundry_tradition, "pf2etools": pf_tradition, "escolhido": "foundry"})

        # Das que sobram sem tradicao nenhuma: quando o unico sinal disponivel
        # e um trait de classe cuja tradicao e variavel/derivada (bard,
        # witch, psychic, summoner), declara a derivacao em vez de deixar
        # `tradicoes` mudo -- nao inventa um valor especifico de tradicao.
        tradicao_de_classe = None
        if not tradicoes:
            donas = CLASSES_DERIVAM_TRADICAO & set(traits)
            if donas:
                tradicao_de_classe = sorted(donas)[0]
                prov["tradicao_de_classe"] = comum.prov_inferido("waybuilder", "traits")

        # --- campos mecanicos / estruturais (foundry vence) ---
        acoes = fsys["time"]["value"] if fsys else None
        prov["acoes"] = "foundry" if acoes is not None else None
        alcance = fsys["range"]["value"] if fsys else None
        prov["alcance"] = "foundry" if alcance is not None else None
        area = None
        if fsys and fsys.get("area"):
            area = {"tipo": fsys["area"].get("type"), "valor": fsys["area"].get("value")}
            prov["area"] = "foundry"
        duracao = None
        if fsys and fsys.get("duration") and (fsys["duration"].get("value") or fsys["duration"].get("sustained")):
            duracao = {"valor": fsys["duration"].get("value") or None, "sustentada": fsys["duration"].get("sustained", False)}
            prov["duracao"] = "foundry"

        # --- campos criticos ---
        damage = fsys.get("damage") if fsys else None
        damage = damage or {}
        defesa, defesa_motivo = (None, "sem-foundry")
        if fsys:
            defesa, defesa_motivo = foundry_defense(fsys, fsys["traits"]["value"])
        # heal-only override: se todas as entradas de dano sao EXCLUSIVAMENTE
        # "healing" (sem "damage"), uma defesa de save nao se aplica ao uso principal.
        if defesa and defesa.get("save") and damage:
            kinds_all = [k for e in damage.values() for k in (e.get("kinds") or [])]
            if kinds_all and all(k == "healing" for k in kinds_all):
                defesa, defesa_motivo = None, "foundry:heal-only-override"
        prov["defesa"] = defesa_motivo if fsys else None
        # divergencia conhecida: foundry diz "sem defesa" mas a AoN tem saving_throw
        # estruturado preenchido (gap de dados do foundry). Registrado, nao corrigido
        # (foundry continua vencendo por precedencia), mas fica auditavel.
        if defesa is None and fsys is not None:
            aon_saving_throw = aon.get("saving_throw")
            if aon_saving_throw:
                conflitos.append({
                    "campo": "defesa", "foundry": None, "aon_saving_throw": aon_saving_throw,
                    "escolhido": "foundry (gap conhecido, ver LOG)",
                })

        heightened, heightened_motivo = ([], "sem-foundry")
        if fsys:
            heightened, heightened_motivo = foundry_heightened(fsys, damage)
        prov["heightened"] = heightened_motivo if fsys else None

        escalonamento = foundry_escalonamento(fsys) if fsys else None
        prov["escalonamento_de_dano"] = "foundry" if escalonamento else None

        # heightened so em prosa (nao estruturado): AoN/foundry description menciona
        # "Heightened" mas nao ha heightening estruturado no foundry.
        desc_html = fsys["description"]["value"] if fsys else (aon.get("text") or "")
        heightened_only_prosa = bool(re.search(r"Heightened\s*\(", desc_html or "")) and not heightened

        # --- texto (aon vence) ---
        texto_plain = strip_html(desc_html) if fsys else (aon.get("summary") or aon.get("text") or "")
        if aon.get("text"):
            texto_plain = aon["text"].strip()
        text_ref = f"wb:text/spell/{slug}"
        prov["text"] = "aon" if aon.get("text") else ("foundry" if fsys else None)

        # --- xref ---
        xref = {"aon": aon["id"]}
        if legacy_doc:
            xref["aon_legacy"] = legacy_doc["id"]
        if fdoc:
            xref["foundry"] = f"Compendium.pf2e.spells-{fdoc['_source_kind']}.Item.{fdoc['_id']}"
        if pf:
            src_abbrev = pf.get("source", "")
            xref["pf2etools"] = f"{slug}_{src_abbrev}".lower()

        # --- grants_completos / requires_parseado (A2 da auditoria) ---------
        # `spell` esta em comum.KINDS_SEM_REQUISITO (nao tem `requires` nesta
        # extracao -- sem pre-requisito pra magia), entao requires_parseado
        # sai `null` (nao se aplica), nao `false`. `perdeu_mecanica` e o caso
        # concreto e observavel de perda parcial pra spell: o foundry tinha
        # texto de elevacao ("Heightened (...)") mas nao a estrutura
        # `system.heightening` pra converter.
        grants_completos, requires_parseado = comum.mecanizacao(
            "spell",
            tinha_mecanica=fsys is not None,
            perdeu_mecanica=heightened_only_prosa,
            tem_requires_texto=False,
            requires_saiu=False,
        )

        # O Remaster renomeou 159 magias e a base guardava so o nome NOVO --
        # `Magic Missile` nao achava `Force Barrage` nem na busca do app nem no
        # `cleric_spell` das divindades. O AoN declara o par; era o extrator que
        # jogava o nome antigo fora.
        # Spec: `specs/2026-07-30-alias-de-magia-renomeada.md`
        aliases = []
        for lid in (aon.get("legacy_id") or []):
            leg = aon_por_id.get(str(lid))
            nome_leg = (leg or {}).get("name")
            if nome_leg and norm_name(nome_leg) != norm_name(registro_name) \
                    and nome_leg not in aliases:
                aliases.append(nome_leg)

        registro = {
            "id": wb_id,
            "kind": "spell",
            "name": registro_name,
            "rank": rank,
            "level": level,
            "tradicoes": tradicoes,
            "tradicao_de_classe": tradicao_de_classe,
            "traits": traits,
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
            "text": text_ref,
            "texto": texto_plain,
            "grants_completos": grants_completos,
            "requires_parseado": requires_parseado,
            "xref": xref,
            "prov": {k: v for k, v in prov.items() if v is not None},
        }
        if aliases:
            registro["aliases"] = aliases
            registro["prov"]["aliases"] = "aon"
        if conflitos:
            registro["conflitos"] = conflitos

        registros.append(registro)

    return registros


if __name__ == "__main__":
    regs = extrair()
    print(f"{len(regs)} registros extraidos")
