"""Extrator canonico de COMPANHEIROS do Pathfinder 2e (Waybuilder).

Familia inteira de "Ator secundario" descrita em
`specs/2026-07-26-schema-personagem.md` -- secao "Todo companheiro e um Ator".
A regra que governa a separacao em `kind`:

    Se alguma regra do jogo consegue falar de um e nao do outro, sao tipos
    diferentes.

Kinds emitidos:

  animal-companion   subtype: especie | especializacao | avancado | unico
                      (especie = a criatura em si; os outros tres sao opcoes
                      de avanco que qualquer especie pode receber -- nenhuma
                      regra do jogo mira "avancado" sem mirar tambem
                      "especie", entao ficam no mesmo kind, como
                      class-feature varia por classe sem virar kind novo)
  familiar-ability    habilidade avulsa que familiar OU master pode escolher
  familiar-specific   familiar de receita fixa (Faerie Dragon etc), com
                      contagem de habilidades exigida e a lista concedida
  eidolon             tipo de eidolon do Summoner (Beast, Construct, ...)
  apparition          espirito do Animist (Tian Xia / War of Immortals) --
                      descoberto durante a extracao: mesma familia funcional
                      do eidolon (Ator com "tipo" que so certas regras miram),
                      mas feat/pericia de Animist fala dele e nao do eidolon,
                      logo kind proprio.

Volume alvo (medido no AoN, `_wb_dump_companheiros.py`):
  animal-companion .................... 114
  animal-companion-specialization ...... 17  (subtype especializacao)
  animal-companion-advanced ............  8  (subtype avancado)
  animal-companion-unique ..............  1  (subtype unico)
  familiar-ability ..................... 191
  familiar-specific .....................47
  eidolon ................................13
  apparition ..............................14
  TOTAL ..................................405

Fontes e precedencia (ver specs/2026-07-26-schema-base.md):

  O Foundry so tem `familiar-abilities` como Item de primeira classe (com
  `system.rules`). Animal companion, especializacoes, familiar-specific,
  eidolon e apparition NAO existem no Foundry como dado estruturado -- por
  isso o AoN e a fonte dominante em toda a familia, exceto `grants` de
  familiar-ability (foundry, unica com rule elements).

  name/traits/rarity/text/level/stats .... aon (unica fonte com statblock)
  grants de familiar-ability .............. foundry quando casa por nome
  license/remaster de familiar-ability .... foundry (`publication`)
  license/remaster do resto ............... heuristica: sem `remaster_id`
                                             (nao foi substituido) = ORC/
                                             remaster corrente; com
                                             `remaster_id` = OGL/legado.
                                             MESMA heuristica que feats.py
                                             usa como fallback -- aqui e a
                                             unica fonte, entao fica marcada
                                             como incerta no `prov`.

Dump do AoN: `pipeline/dados_brutos/_wb_dump_companheiros.py` ->
`pipeline/dados_brutos/aon_companheiros.json` (405 docs, categorias listadas
acima, indice elasticsearch `aon`).

Somente biblioteca padrao. Ponto de entrada: `extrair() -> list[dict]`.
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

# --------------------------------------------------------------------------
# Caminhos
# --------------------------------------------------------------------------

AQUI = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(AQUI)
BRUTOS = os.path.join(PIPELINE, "dados_brutos")

sys.path.insert(0, PIPELINE)
import comum  # noqa: E402

FOUNDRY_COMMIT = "87f9e5028baaa10b70fdc766260b7886def17e04"

_CANDIDATOS_FOUNDRY = [
    os.environ.get("WB_FOUNDRY_PACKS", ""),
    os.path.join(BRUTOS, "foundry", "packs", "pf2e"),
    "/tmp/claude-1000/-mnt-c-Users-igor0/39eadbed-e8eb-4194-8557-74f05193fdc1"
    "/scratchpad/pf2e-research/pf2e/packs/pf2e",
]

AON_COMPANHEIROS = os.path.join(BRUTOS, "aon_companheiros.json")


def _packs_foundry():
    for c in _CANDIDATOS_FOUNDRY:
        if c and os.path.isdir(os.path.join(c, "familiar-abilities")):
            return c
    return None  # familia tolera degradar sem foundry: so familiar-ability usa


# --------------------------------------------------------------------------
# Utilitarios (mesmo padrao de feats.py/ancestrias.py)
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
    n = n.lower().replace("’", "'")
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


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------

def carregar_aon():
    if not os.path.exists(AON_COMPANHEIROS):
        raise SystemExit(
            "aon_companheiros.json nao encontrado. Rode "
            "pipeline/dados_brutos/_wb_dump_companheiros.py primeiro.")
    return _ler_json(AON_COMPANHEIROS)


def carregar_foundry_familiar_abilities(packs):
    """chave(nome) -> {id, rules, publication, traits}"""
    out = {}
    if not packs:
        return out
    raiz = os.path.join(packs, "familiar-abilities")
    for caminho in _andar(raiz):
        try:
            d = _ler_json(caminho)
        except Exception:
            continue
        if not isinstance(d, dict) or d.get("type") != "action":
            continue
        s = d.get("system", {}) or {}
        nome = d.get("name")
        if not nome:
            continue
        out[chave(nome)] = {
            "id": d.get("_id"),
            "rules": s.get("rules", []) or [],
            "publication": s.get("publication", {}) or {},
            "traits": [slug(t) for t in (s.get("traits", {}) or {}).get("value", []) or []],
        }
    return out


# --------------------------------------------------------------------------
# Foundry rule elements -> grants (vocabulario pequeno: e so o que aparece
# nos 101 itens de familiar-abilities, ver relatorio)
# --------------------------------------------------------------------------

RE_NEUTROS = {"Note", "RollOption", "TokenLight"}


def converter_grants_familiar(regras, ignoradas):
    grants = []
    perdeu = False
    for r in regras or []:
        k = r.get("key")
        if k in RE_NEUTROS:
            ignoradas[k] += 1
            continue
        if k == "ActorTraits":
            grants.append({"actor_traits": r.get("add")})
        elif k == "Resistance":
            grants.append({"resistance": {"tipo": r.get("type"), "valor": r.get("value")}})
        elif k == "Immunity":
            grants.append({"immunity": r.get("type")})
        elif k == "BaseSpeed":
            grants.append({"speed": {"tipo": r.get("selector"), "valor": r.get("value")}})
        elif k == "Sense":
            grants.append({"sense": {"tipo": r.get("selector"),
                                     "acuidade": r.get("acuity"),
                                     "alcance": r.get("range")}})
        elif k == "FlatModifier":
            g = {"selector": r.get("selector"), "value": r.get("value")}
            if r.get("type"):
                g["type"] = r["type"]
            grants.append({"flat_modifier": g})
        elif k == "ChoiceSet":
            grants.append({"choice": {"flag": r.get("flag")}})
        elif k == "GrantItem":
            grants.append({"grant_item": {"uuid": r.get("uuid")}})
        else:
            ignoradas[k] += 1
            perdeu = True
    return grants, perdeu


# --------------------------------------------------------------------------
# Parsing de prosa do AoN (animal-companion / eidolon)
# --------------------------------------------------------------------------

ATAQUE_RE = re.compile(
    r"Melee\s+(?:Single Action|Two Actions|Three Actions|Free Action|Reaction)\s+"
    r"([A-Za-z][A-Za-z '\-]*?)(?:\s*\(([^)]*)\))?,\s*Damage\s+"
    r"(\d+d\d+(?:\s*[+-]\s*\d+)?)\s+([A-Za-z]+)", re.I)


def parse_ataques(texto: str):
    out = []
    for m in ATAQUE_RE.finditer(texto or ""):
        nome, traits, dano, tipo = m.groups()
        item = {"nome": nome.strip(), "dano": dano.replace(" ", ""), "tipo": tipo.lower()}
        if traits:
            item["traits"] = [slug(t) for t in traits.split(",")]
        out.append(item)
    return out


_LABELS_COMPANHEIRO = ["Size", "Melee", "Str", "Dex", "Con", "Int", "Wis", "Cha",
                        "Hit Points", "Skill", "Senses", "Speed",
                        "Support Benefit", "Advanced Maneuver"]


def _campo_rotulado(texto: str, rotulo: str, seguintes):
    if not texto:
        return None
    alt = "|".join(re.escape(l) for l in seguintes) if seguintes else None
    if alt:
        pat = re.compile(re.escape(rotulo) + r"\s+(.*?)(?=\s+(?:" + alt + r")\b|$)", re.S)
    else:
        pat = re.compile(re.escape(rotulo) + r"\s+(.*)$", re.S)
    m = pat.search(texto)
    if not m:
        return None
    v = m.group(1).strip()
    return v or None


ATAQUE_SUGERIDO_RE = re.compile(r"Suggested Attacks\s+(.*?)\s+[A-Z][\w\s]*?-\s*Str", re.S)


def parse_ataques_sugeridos(texto: str):
    m = ATAQUE_SUGERIDO_RE.search(texto or "")
    if not m:
        return []
    out = []
    for item in m.group(1).split(","):
        item = item.strip()
        mm = re.match(r"^(.+?)\s*\(([^)]*)\)$", item)
        if mm:
            out.append({"nome": mm.group(1).strip(), "tipo": mm.group(2).strip().lower()})
        elif item:
            out.append({"nome": item})
    return out


# --------------------------------------------------------------------------
# Envelope
# --------------------------------------------------------------------------

PAG_RE = re.compile(r"pg\.\s*(\d+)")


def _fonte(doc, prov):
    livro = doc.get("primary_source")
    if not livro:
        return None
    m = PAG_RE.search(doc.get("primary_source_raw") or "")
    remaster = not doc.get("remaster_id")
    source = {
        "book": livro,
        "page": int(m.group(1)) if m else None,
        "license": "ORC" if remaster else "OGL",
        "remaster": remaster,
    }
    prov["source"] = "aon(heuristica:remaster_id)"
    return source


def montar(doc, kind, est, subtype=None):
    nome = doc.get("name")
    sl = slug(nome)
    prov = {"name": "aon"}

    traits = [slug(t) for t in (doc.get("trait") or [])]
    if traits:
        prov["traits"] = "aon"

    rarity = doc.get("rarity") or None
    if rarity:
        prov["rarity"] = "aon"

    level = doc.get("level")
    if level is not None:
        prov["level"] = "aon"

    source = _fonte(doc, prov)

    text_ref = None
    if doc.get("text"):
        prov["text"] = "aon"
        text_ref = "wb:text/%s/%s" % (kind, sl)

    # baseline: nenhuma destas kinds tem fonte de rule elements no Foundry
    # (so familiar-ability tem, e sobrescreve abaixo quando casa por nome) --
    # sem mecanica nenhuma pra converter, `grants_completos` e sucesso (true),
    # nao perda. Nenhuma tem pre-requisito, entao `requires_parseado` e true.
    grants_completos, requires_parseado = comum.mecanizacao(kind, False, False, False, True)
    reg = {
        "id": "wb:%s/%s" % (kind, sl),
        "kind": kind,
        "name": nome,
        "level": level,
        "traits": traits,
        "rarity": rarity,
        "source": source,
        "requires": None,
        "grants": [],
        "text": text_ref,
        "grants_completos": grants_completos,
        "requires_parseado": requires_parseado,
        "xref": {"aon": doc.get("id")},
        "prov": prov,
    }
    if subtype:
        reg["subtype"] = subtype
    if doc.get("remaster_id"):
        reg["remaster_de"] = doc["remaster_id"]
    if doc.get("legacy_id"):
        reg["legado_de"] = doc["legacy_id"]
    est["registros"] += 1
    est["por_kind"][kind if not subtype else "%s:%s" % (kind, subtype)] += 1
    return reg


ATTR_CAMPOS = [("strength", "str"), ("dexterity", "dex"), ("constitution", "con"),
               ("intelligence", "int"), ("wisdom", "wis"), ("charisma", "cha")]


def _dedup_por_nome(lista, contador_homonimos):
    """Legado e remaster do mesmo nome sao o MESMO registro (mesmo padrao de
    feats.py): fica a versao remaster (sem `remaster_id` = nao foi
    substituida = e a corrente). Sem isso, nome duplicado -> `wb:` id
    duplicado, que quebra a identidade unica do schema."""
    por_chave = {}
    for d in lista:
        k = chave(d.get("name") or "")
        if not k:
            continue
        atual = por_chave.get(k)
        if atual is None:
            por_chave[k] = d
            continue
        contador_homonimos[k] += 1
        atual_remaster = not atual.get("remaster_id")
        novo_remaster = not d.get("remaster_id")
        if novo_remaster and not atual_remaster:
            por_chave[k] = d
    return list(por_chave.values())


# --------------------------------------------------------------------------
# Extracao
# --------------------------------------------------------------------------

def extrair():
    aon = carregar_aon()
    packs = _packs_foundry()
    foundry_fa = carregar_foundry_familiar_abilities(packs)

    por_cat_bruto = defaultdict(list)
    for d in aon:
        por_cat_bruto[d.get("category")].append(d)

    homonimos = Counter()
    por_cat = {k: _dedup_por_nome(v, homonimos) for k, v in por_cat_bruto.items()}

    est = {
        "aon_total": len(aon),
        "por_categoria_aon_bruto": Counter({k: len(v) for k, v in por_cat_bruto.items()}),
        "por_categoria_aon_dedup": Counter({k: len(v) for k, v in por_cat.items()}),
        "homonimos_legado_remaster": sum(homonimos.values()),
        "registros": 0,
        "por_kind": Counter(),
        "foundry_familiar_abilities": len(foundry_fa),
        "familiar_ability_casadas_foundry": 0,
        "familiar_ability_grants_completos_true": 0,
        "familiar_ability_grants_completos_false": 0,
        "rules_ignoradas": Counter(),
        "animal_companion_ataques_parseados": 0,
        "animal_companion_sem_ataque_no_texto": 0,
        "animal_companion_com_melee_mas_sem_parse": 0,
        "eidolon_ataques_sugeridos_parseados": 0,
        "familiar_specific_habilidades_resolvidas": 0,
        "familiar_specific_habilidades_nao_resolvidas": 0,
        "niveis_animal_companion_maior_que_1": [],
    }

    registros = []

    # ---- animal-companion: especie -----------------------------------
    for d in por_cat.get("animal-companion", []):
        reg = montar(d, "animal-companion", est, subtype="especie")
        atributos = {abrev: d.get(campo) for campo, abrev in ATTR_CAMPOS
                     if d.get(campo) is not None}
        texto = d.get("text") or ""
        ataques = parse_ataques(texto)
        if ataques:
            est["animal_companion_ataques_parseados"] += 1
        elif "Melee" in texto:
            est["animal_companion_com_melee_mas_sem_parse"] += 1
        else:
            est["animal_companion_sem_ataque_no_texto"] += 1
        reg["stats"] = {
            "atributos": atributos or None,
            "tamanho": (d.get("size") or [None])[0],
            "velocidade": d.get("speed"),
            "sentidos": d.get("sense") or None,
            "pericia_inicial": d.get("skill") or [],
            "hp": d.get("hp"),
            "montaria": bool(d.get("mount")),
            "ataques": ataques,
            "support_benefit": _campo_rotulado(texto, "Support Benefit", ["Advanced Maneuver"]),
            "advanced_maneuver": _campo_rotulado(texto, "Advanced Maneuver", []),
        }
        if reg["stats"]["atributos"]:
            reg["prov"]["stats"] = "aon"
        if level := d.get("level"):
            if level > 1:
                est["niveis_animal_companion_maior_que_1"].append((d.get("name"), level))
        registros.append(reg)

    # ---- animal-companion: especializacao / avancado / unico ---------
    for cat_aon, subtype in [("animal-companion-specialization", "especializacao"),
                              ("animal-companion-advanced", "avancado"),
                              ("animal-companion-unique", "unico")]:
        for d in por_cat.get(cat_aon, []):
            reg = montar(d, "animal-companion", est, subtype=subtype)
            registros.append(reg)

    # ---- familiar-ability ----------------------------------------------
    fa_slug_por_chave = {}
    for d in por_cat.get("familiar-ability", []):
        reg = montar(d, "familiar-ability", est)
        reg["tipo_habilidade"] = d.get("ability_type")
        k = chave(d.get("name") or "")
        fa_slug_por_chave[k] = slug(d.get("name"))
        f = foundry_fa.get(k)
        if f:
            est["familiar_ability_casadas_foundry"] += 1
            reg["xref"]["foundry"] = "Compendium.pf2e.familiar-abilities.Item." + (f["id"] or "")
            grants, perdeu = converter_grants_familiar(f["rules"], est["rules_ignoradas"])
            reg["grants"] = grants
            if grants:
                reg["prov"]["grants"] = "foundry"
            reg["grants_completos"], reg["requires_parseado"] = comum.mecanizacao(
                "familiar-ability", bool(f["rules"]), perdeu, False, True)
            if reg["grants_completos"]:
                est["familiar_ability_grants_completos_true"] += 1
            else:
                est["familiar_ability_grants_completos_false"] += 1
            pub = f.get("publication") or {}
            if pub.get("license"):
                if reg["source"] is None:
                    reg["source"] = {"book": None, "page": None}
                reg["source"]["license"] = pub["license"]
                reg["source"]["remaster"] = bool(pub.get("remaster"))
                reg["prov"]["source"] = (reg["prov"].get("source") or "aon") + "+foundry(licenca)"
            if f["traits"] and not reg["traits"]:
                reg["traits"] = f["traits"]
                reg["prov"]["traits"] = "foundry"
        else:
            # sem casamento no Foundry: nenhuma fonte de rule element pra esta
            # habilidade, nada a converter -- baseline de `montar()` (true) fica.
            est["familiar_ability_grants_completos_true"] += 1
        registros.append(reg)

    # ---- familiar-specific -----------------------------------------------
    for d in por_cat.get("familiar-specific", []):
        reg = montar(d, "familiar-specific", est)
        reg["required_abilities"] = d.get("required_abilities")
        habs = d.get("familiar_ability") or []
        if isinstance(habs, str):
            habs = [h.strip() for h in habs.split(",") if h.strip()]
        resolvidos = []
        for h in habs:
            k = chave(h)
            sl = fa_slug_por_chave.get(k)
            if sl:
                resolvidos.append("wb:familiar-ability/" + sl)
                est["familiar_specific_habilidades_resolvidas"] += 1
            else:
                resolvidos.append("wb:familiar-ability/" + slug(h) + "?nao-resolvido")
                est["familiar_specific_habilidades_nao_resolvidas"] += 1
        reg["concede_habilidades"] = resolvidos
        if resolvidos:
            reg["prov"]["concede_habilidades"] = "aon"
        registros.append(reg)

    # ---- eidolon -----------------------------------------------------
    for d in por_cat.get("eidolon", []):
        reg = montar(d, "eidolon", est)
        texto = d.get("text") or ""
        ataques_sug = parse_ataques_sugeridos(texto)
        if ataques_sug:
            est["eidolon_ataques_sugeridos_parseados"] += 1
        reg["stats"] = {
            "tradicao": d.get("tradition"),
            "plano_natal": d.get("home_plane"),
            "tamanho": (d.get("size") or [None])[0],
            "velocidade": d.get("speed"),
            "sentidos": d.get("sense") or None,
            "pericias": d.get("skill") or [],
            "ataques_sugeridos": ataques_sug,
        }
        registros.append(reg)

    # ---- apparition (Animist) -----------------------------------------
    for d in por_cat.get("apparition", []):
        reg = montar(d, "apparition", est)
        reg["stats"] = {
            "pericias": d.get("skill") or [],
            "magias": d.get("spell"),
        }
        registros.append(reg)

    est["conflitos_totais"] = 0  # fonte unica (aon) por campo em quase tudo; sem 2a fonte pra divergir
    ESTATISTICAS.clear()
    ESTATISTICAS.update(est)
    return registros


ESTATISTICAS = {}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    registros = extrair()
    saida = os.path.join(PIPELINE, "saida", "companheiros.json")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=1)

    est = ESTATISTICAS
    print("registros totais ..... %d" % est["registros"])
    for k, v in sorted(est["por_kind"].items()):
        print("  %-32s %d" % (k, v))
    print()
    print("familiar-ability casadas c/ foundry .. %d / %d" % (
        est["familiar_ability_casadas_foundry"], est["por_kind"].get("familiar-ability", 0)))
    print("familiar-ability grants_completos true/false %d / %d" % (
        est["familiar_ability_grants_completos_true"], est["familiar_ability_grants_completos_false"]))
    print("animal-companion ataques parseados ... %d" % est["animal_companion_ataques_parseados"])
    print("animal-companion com Melee sem parse . %d" % est["animal_companion_com_melee_mas_sem_parse"])
    print("eidolon ataques sugeridos parseados .. %d" % est["eidolon_ataques_sugeridos_parseados"])
    print("familiar-specific habilidades ok/falha %d / %d" % (
        est["familiar_specific_habilidades_resolvidas"],
        est["familiar_specific_habilidades_nao_resolvidas"]))
    print("animal companions com level>1 (exoticos, gate por nivel) ..", len(est["niveis_animal_companion_maior_que_1"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
