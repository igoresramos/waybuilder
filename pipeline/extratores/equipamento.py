"""Extrator canonico de EQUIPAMENTO, ARMAS, ARMADURAS e ESCUDOS do
Pathfinder 2e (Waybuilder).

Obedece `specs/2026-07-26-schema-base.md`:

  - envelope com `id`, `kind`, `prov` por campo e `conflitos`
  - `mechanized` separa o que o app calcula do que so exibe
  - `requires` sugere, nunca bloqueia -- Principio zero

Precedencia por campo (igual aos extratores irmaos):

  campos mecanicos estruturados
  (categoria, dano, bulk, ac, runas...)  foundry  (unica com o dado em campo proprio)
  name/traits/rarity/text ............... aon      (e a Paizo)
  level .................................. foundry, conferido contra aon
  source .................................. aon, cai para foundry

Modelagem de runas: runas fundamentais e de propriedade sao itens `equipment`
por direito proprio no Foundry (usage.value = "etched-onto-<weapon|armor|shield>").
Nao existe "+1 Striking Longsword" como registro separado -- o app compoe o
item final em tempo de construcao, a partir do item base + runas anexadas.
O registro do item base carrega o snapshot `runes` do Foundry (slots/valor,
normalmente zerado no item mundano) para o app saber que aquele item aceita
runas daquele tipo; o registro da runa carrega `rune.tipo`/`rune.aplica_em`.

Somente biblioteca padrao. Ponto de entrada: `extrair() -> list[dict]`.
"""

from __future__ import annotations

import glob
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
PROJETO = os.path.dirname(PIPELINE)
BRUTOS = os.path.join(PIPELINE, "dados_brutos")

FOUNDRY_COMMIT = "87f9e5028baaa10b70fdc766260b7886def17e04"

_CANDIDATOS_FOUNDRY = [
    os.environ.get("WB_FOUNDRY_PACKS", ""),
    os.path.join(BRUTOS, "foundry_repo", "packs", "pf2e"),
    os.path.join(BRUTOS, "foundry", "packs", "pf2e"),
]


def _packs_foundry() -> str:
    for c in _CANDIDATOS_FOUNDRY:
        if c and os.path.isdir(os.path.join(c, "equipment")):
            return c
    raise SystemExit(
        "packs do Foundry nao encontrados. Defina WB_FOUNDRY_PACKS apontando "
        "para <clone>/packs/pf2e (commit %s)." % FOUNDRY_COMMIT
    )


# --------------------------------------------------------------------------
# Utilitarios (identicos aos extratores irmaos)
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
# Kind: Foundry `type` -> kind do schema
# --------------------------------------------------------------------------

# So estes tres tipos do Foundry viram kind proprio; todo o resto (consumable,
# treasure, ammo, backpack, kit, equipment) cai em `equipment` -- e o unico
# kind generico previsto na spec para "o resto do inventario".
KIND_FOUNDRY = {"weapon": "weapon", "armor": "armor", "shield": "shield"}


def kind_de(foundry_type: str) -> str:
    return KIND_FOUNDRY.get(foundry_type, "equipment")


# --------------------------------------------------------------------------
# Runas: deteccao de item-runa dentro do pacote `equipment` do Foundry
# --------------------------------------------------------------------------

USAGE_RUNA_RE = re.compile(r"^etched-onto-(?:an?-)?(weapon|armor|shield)s?$")

RUNA_TIPO_POR_SLUG = (
    (re.compile(r"^weapon-potency-(\d)$"), "potency"),
    (re.compile(r"^armor-potency-(\d)$"), "potency"),
    (re.compile(r"^(greater-|major-)?striking-rune(-\w+)?$"), "striking"),
    (re.compile(r"^(greater-|major-)?resilient-rune(-\w+)?$"), "resilient"),
    (re.compile(r"^reinforcing-rune-(lesser|moderate|greater|major|supreme)$"), "reinforcing"),
)

GRAU_POTENCY = {"1": 1, "2": 2, "3": 3, "4": 4}
GRAU_PALAVRA = {"lesser": 1, "minor": 1, "moderate": 2, "greater": 3, "major": 3, "supreme": 4}


def detectar_runa(sl: str, usage_value: str, level):
    """Devolve dict {tipo, aplica_em, grau} ou None se o item nao e runa."""
    if not usage_value:
        return None
    m = USAGE_RUNA_RE.match(usage_value)
    if not m:
        return None
    aplica_em = m.group(1)
    tipo = "property"  # default: runa de propriedade (flaming, keen, ...)
    grau = None
    for rx, t in RUNA_TIPO_POR_SLUG:
        mm = rx.match(sl)
        if mm:
            tipo = t
            if mm.groups() and mm.group(1) in GRAU_POTENCY:
                grau = GRAU_POTENCY[mm.group(1)]
            break
    if grau is None:
        for palavra, g in GRAU_PALAVRA.items():
            if palavra in sl:
                grau = g
                break
    return {"tipo": tipo, "aplica_em": aplica_em, "grau": grau}


# --------------------------------------------------------------------------
# Preco: normaliza para pecas de cobre (cp), unidade canonica
# --------------------------------------------------------------------------

CP_POR_MOEDA = {"cp": 1, "sp": 10, "gp": 100, "pp": 1000}


def preco_cp_foundry(valor: dict):
    if not isinstance(valor, dict) or not valor:
        return None
    total = 0
    for moeda, qtd in valor.items():
        total += CP_POR_MOEDA.get(moeda, 0) * (qtd or 0)
    return total


# --------------------------------------------------------------------------
# Rule elements -> grants (minimo: so o que afeta matematica direta da ficha)
# --------------------------------------------------------------------------

RE_CONVERTIDOS = {"FlatModifier", "Resistance", "Immunity", "Weakness", "DamageDice"}
RE_NEUTROS = {
    "Note", "RollOption", "TokenLight", "TokenEffectIcon", "AdjustDegreeOfSuccess",
    "SubstituteRoll", "RollTwice", "AdjustModifier", "AdjustStrike", "DamageAlteration",
    "Strike", "Aura", "EphemeralEffect", "ItemAlteration", "ActiveEffectLike",
    "ChoiceSet", "GrantItem",
}


def converter_grants(regras, contagem_ignoradas):
    grants = []
    perdeu = False
    for r in regras or []:
        k = r.get("key")
        if k in RE_NEUTROS:
            contagem_ignoradas[k] += 1
            continue
        if k not in RE_CONVERTIDOS:
            contagem_ignoradas[k] += 1
            perdeu = True
            continue
        if k == "FlatModifier":
            g = {"selector": r.get("selector"), "value": r.get("value")}
            if r.get("type"):
                g["type"] = r["type"]
            if r.get("predicate"):
                g["condicional"] = True
            grants.append({"flat_modifier": g})
        elif k == "Resistance":
            grants.append({"resistance": {"tipo": r.get("type"), "valor": r.get("value")}})
        elif k == "Immunity":
            grants.append({"immunity": r.get("type")})
        elif k == "Weakness":
            grants.append({"weakness": {"tipo": r.get("type"), "valor": r.get("value")}})
        elif k == "DamageDice":
            grants.append({"damage_dice": {"selector": r.get("selector"),
                                           "quantidade": r.get("diceNumber")}})
    return grants, perdeu


# --------------------------------------------------------------------------
# Carga do Foundry
# --------------------------------------------------------------------------

def carregar_foundry(packs):
    raiz = os.path.join(packs, "equipment")
    itens = []
    for caminho in _andar(raiz):
        try:
            d = _ler_json(caminho)
        except Exception:
            continue
        if not isinstance(d, dict) or "system" not in d:
            continue
        itens.append(d)
    return itens


def norm_foundry(d):
    s = d.get("system", {}) or {}
    pub = s.get("publication", {}) or {}
    traits_v = (s.get("traits", {}) or {}).get("value", []) or []
    tipo = d.get("type")
    preco_valor = ((s.get("price", {}) or {}).get("value")) or {}
    n = {
        "nome": d.get("name"),
        "tipo": tipo,
        "level": (s.get("level", {}) or {}).get("value"),
        "traits": [slug(t) for t in traits_v],
        "rarity": (s.get("traits", {}) or {}).get("rarity"),
        "descricao": (s.get("description", {}) or {}).get("value"),
        "livro": pub.get("title"),
        "licenca": pub.get("license"),
        "remaster": pub.get("remaster"),
        "id": d.get("_id"),
        "rules": s.get("rules", []) or [],
        "bulk": (s.get("bulk", {}) or {}).get("value"),
        "preco_cp": preco_cp_foundry(preco_valor),
        "preco_raw": preco_valor or None,
        "usage": (s.get("usage", {}) or {}).get("value"),
        "base_item": s.get("baseItem"),
        "hardness": s.get("hardness"),
        "hp": (s.get("hp", {}) or {}).get("max"),
    }
    if tipo == "weapon":
        dano = s.get("damage", {}) or {}
        n["categoria"] = s.get("category")
        n["grupo"] = s.get("group")
        n["dano"] = {"dados": dano.get("dice"), "dado": dano.get("die"),
                     "tipo": dano.get("damageType")} if dano.get("die") else None
        n["alcance"] = s.get("range")
        n["reload"] = (s.get("reload", {}) or {}).get("value")
        n["runes"] = s.get("runes") or {}
    elif tipo == "armor":
        n["categoria"] = s.get("category")
        n["grupo"] = s.get("group")
        n["ac_bonus"] = s.get("acBonus")
        n["dex_cap"] = s.get("dexCap")
        n["check_penalty"] = s.get("checkPenalty")
        n["speed_penalty"] = s.get("speedPenalty")
        n["strength"] = s.get("strength")
        n["runes"] = s.get("runes") or {}
    elif tipo == "shield":
        n["ac_bonus"] = s.get("acBonus")
        n["speed_penalty"] = s.get("speedPenalty")
        n["runes"] = s.get("runes") or {}
    return n


# --------------------------------------------------------------------------
# Carga do AoN (cache local; formato identico ao dump dos irmaos)
# --------------------------------------------------------------------------

RARIDADES = {"common", "uncommon", "rare", "unique"}


def carregar_aon(categoria):
    # `aon_dump/<categoria>.json` e o dump completo do indice (dump_aon.py) --
    # as categorias do AoN se chamam exatamente weapon/armor/shield/equipment.
    # Os dois caminhos antigos NUNCA existiram em disco: a funcao devolvia lista
    # vazia em silencio e o extrator saia mono-fonte, com 5.698 registros no
    # lugar de 7.496, exit code 0.
    for cand in (os.path.join(BRUTOS, "aon_dump", "%s.json" % categoria),
                 os.path.join(BRUTOS, "aon_equipment_%s.json" % categoria),
                 os.path.join(BRUTOS, "aon", "aon_equipment_%s.json" % categoria)):
        if os.path.exists(cand):
            return _ler_json(cand)
    print("  ! sem dump do AoN para '%s' -- rode dump_aon.py" % categoria,
          file=sys.stderr)
    return []


def norm_aon(a):
    src = a.get("primary_source_raw") or ""
    m = re.search(r"pg\.\s*(\d+)", src)
    tr = [slug(t) for t in (a.get("trait") or a.get("trait_raw") or [])]
    tr = [t for t in tr if t not in RARIDADES]
    return {
        "nome": a.get("name"),
        "level": a.get("level"),
        "traits": tr,
        "rarity": (a.get("rarity") or "").lower() or None,
        "livro": a.get("primary_source"),
        "pagina": int(m.group(1)) if m else None,
        "texto": a.get("text"),
        "resumo": a.get("summary"),
        "id": a.get("id"),
        "url": a.get("url"),
        "remaster_id": a.get("remaster_id") or [],
        "legacy_id": a.get("legacy_id") or [],
        "pfs": a.get("pfs"),
        "excluir": a.get("exclude_from_search"),
        "preco_cp": a.get("price"),
        "bulk_raw": a.get("bulk_raw"),
        "item_category": a.get("item_category"),
        "item_subcategory": a.get("item_subcategory"),
    }


# --------------------------------------------------------------------------
# Carga do pf2etools (terceira opiniao -- so `baseitems.json`, catalogo
# curado de armas/armaduras/escudos base; nao ha cache local dos ~150
# arquivos `items-<livro>.json` de itens magicos, entao a cobertura de
# pf2etools nesta extracao fica restrita aos itens base)
# --------------------------------------------------------------------------

_SIGLAS_PF2E = None


def expandir_sigla_pf2etools(s):
    """'G&G' -> 'Guns & Gears', pelo mapa gerado de js/parser.js da propria fonte."""
    global _SIGLAS_PF2E
    if _SIGLAS_PF2E is None:
        caminho = os.path.join(PIPELINE, "siglas_pf2etools.json")
        try:
            _SIGLAS_PF2E = json.load(open(caminho)).get("siglas") or {}
        except Exception:
            _SIGLAS_PF2E = {}
    return _SIGLAS_PF2E.get(str(s or "").strip(), s)


def carregar_pf2etools_base():
    """`baseitems.json` (armas/armaduras/escudos base) + `items-<livro>.json`.

    O comentario acima dizia que nao havia cache local dos `items-<livro>.json`
    e por isso a cobertura do pf2etools ficava restrita aos itens base. Depois
    que a fonte passou a ser clonada inteira (2026-07-26) sao 90 arquivos com
    2.632 itens magicos -- deixar de fora era descartar a terceira opiniao
    justamente onde o catalogo e maior.
    """
    itens = []
    caminho = os.path.join(BRUTOS, "pf2etools", "baseitems.json")
    if os.path.exists(caminho):
        try:
            itens.extend(_ler_json(caminho).get("baseitem", []) or [])
        except Exception:
            pass
    for arq in sorted(glob.glob(os.path.join(BRUTOS, "pf2etools", "items-*.json"))):
        try:
            itens.extend(_ler_json(arq).get("item", []) or [])
        except Exception:
            continue
    return itens


def norm_pf2etools(it):
    # `baseitems.json` grava `category` como string; `items-<livro>.json` grava
    # como lista ("category": ["Poison"]). Aceitar so um dos dois estoura no
    # primeiro item magico.
    cat_bruta = it.get("category") or ""
    if isinstance(cat_bruta, list):
        cat_bruta = cat_bruta[0] if cat_bruta else ""
    cat = str(cat_bruta).lower()
    kind = {"weapon": "weapon", "armor": "armor", "shield": "shield"}.get(cat, "equipment")
    return {
        "nome": it.get("name"),
        "kind": kind,
        "level": it.get("level", 0),
        "fonte": it.get("source"),
        "pagina": it.get("page"),
        "remaster": bool(it.get("remaster")),
        "traits": [slug(re.sub(r"\s*<[^>]*>", "", t)) for t in (it.get("traits") or [])],
        "bulk": it.get("bulk"),
        "hands": it.get("hands"),
        "weaponData": it.get("weaponData") or {},
        "armorData": it.get("armorData") or {},
        "shieldData": it.get("shieldData") or {},
    }


# --------------------------------------------------------------------------
# Extracao
# --------------------------------------------------------------------------

ESTATISTICAS = {}


def extrair():
    packs = _packs_foundry()

    f_brutos = carregar_foundry(packs)
    foundry = [norm_foundry(d) for d in f_brutos]

    a_weapon = [norm_aon(a) for a in carregar_aon("weapon")]
    a_armor = [norm_aon(a) for a in carregar_aon("armor")]
    a_shield = [norm_aon(a) for a in carregar_aon("shield")]
    a_equipment = [norm_aon(a) for a in carregar_aon("equipment")]
    aon_por_kind = {"weapon": a_weapon, "armor": a_armor, "shield": a_shield,
                    "equipment": a_equipment}

    t_brutos = [norm_pf2etools(it) for it in carregar_pf2etools_base()]
    tools_por_kind = defaultdict(list)
    for t in t_brutos:
        tools_por_kind[t["kind"]].append(t)

    # licenca por livro, aprendida do proprio Foundry (mesmo truque dos irmaos)
    licenca_por_livro = {}
    for rf in foundry:
        if rf["livro"] and rf["licenca"]:
            licenca_por_livro.setdefault(chave(rf["livro"]),
                                         (rf["licenca"], bool(rf["remaster"])))

    def completar_licenca(src, prov_dict):
        if not src or src.get("license"):
            return
        info = licenca_por_livro.get(chave(src.get("book") or ""))
        if info:
            src["license"], src["remaster"] = info[0], info[1]
            prov_dict["source"] = (prov_dict.get("source") or "aon") + "+foundry(licenca)"

    est = {
        "foundry_total": len(foundry),
        "aon_weapon": len(a_weapon), "aon_armor": len(a_armor),
        "aon_shield": len(a_shield), "aon_equipment": len(a_equipment),
        "pf2etools_base_total": len(t_brutos),
        "por_kind": Counter(),
        "com_estrutura_mecanica": Counter(),
        "so_prosa": Counter(),
        "runas_detectadas": Counter(),
        "cobertura_fontes": Counter(),
        "conflitos_por_campo": Counter(),
        "homonimos": Counter(),
        "kind_reconciliado": Counter(),
        "mechanized_true": 0,
        "mechanized_false": 0,
        "rules_ignoradas": Counter(),
        "sem_source": 0,
    }

    # ---- agrupamento por (kind, chave-do-nome) -------------------------
    porchave = defaultdict(lambda: {"foundry": None, "pf2etools": None, "aon": None})

    def melhor(atual, novo, remaster_novo):
        if atual is None:
            return novo
        est["homonimos"][novo.get("_kind", "?")] += 1
        return novo if remaster_novo and not atual.get("_remaster") else atual

    # O Foundry classifica pelo `type` do item (mecanica real: e uma arma, uma
    # armadura...). O AoN as vezes cataloga o mesmo item magico especifico
    # (ex.: um item que E uma arma, mas a Paizo lista na pagina generica de
    # "Equipment") sob `category: equipment`. Sem reconciliar isso, o mesmo
    # nome vira DOIS registros -- um `weapon` orfao (so foundry) e um
    # `equipment` orfao (so aon) -- ao inves de um so, enriquecido pelas duas
    # fontes. O Foundry decide o kind quando tem opiniao; as outras fontes so
    # decidem para nomes que o Foundry nao tem.
    for r in foundry:
        k = (kind_de(r["tipo"]), chave(r["nome"]))
        r["_remaster"] = bool(r["remaster"])
        r["_kind"] = k[0]
        porchave[k]["foundry"] = melhor(porchave[k]["foundry"], r, r["_remaster"])

    kind_por_chave_foundry = {}
    for r in foundry:
        kind_por_chave_foundry.setdefault(chave(r["nome"]), kind_de(r["tipo"]))

    for kind_nome, lst in tools_por_kind.items():
        for r in lst:
            ch = chave(r["nome"])
            k = (kind_por_chave_foundry.get(ch, kind_nome), ch)
            r["_remaster"] = r["remaster"]
            r["_kind"] = k[0]
            porchave[k]["pf2etools"] = melhor(porchave[k]["pf2etools"], r, r["_remaster"])

    for kind_nome, lst in aon_por_kind.items():
        for r in lst:
            if r.get("excluir"):
                continue
            ch = chave(r["nome"])
            k = (kind_por_chave_foundry.get(ch, kind_nome), ch)
            r["_remaster"] = not r["remaster_id"]
            r["_kind"] = k[0]
            porchave[k]["aon"] = melhor(porchave[k]["aon"], r, r["_remaster"])
            if k[0] != kind_nome:
                est["kind_reconciliado"][kind_nome + "->" + k[0]] += 1

    registros = []
    ignoradas = est["rules_ignoradas"]

    for (kind, k), grupo in sorted(porchave.items()):
        f, t, a = grupo["foundry"], grupo["pf2etools"], grupo["aon"]
        base = a or f or t
        nome = base["nome"]
        sl = slug(nome)
        if not sl:
            continue

        combo = "".join(c for c, v in (("F", f), ("T", t), ("A", a)) if v)
        est["cobertura_fontes"][kind + ":" + combo] += 1
        est["por_kind"][kind] += 1

        prov = {}
        conflitos = []

        prov["name"] = "aon" if a else ("foundry" if f else "pf2etools")
        if a and a["texto"]:
            prov["text"] = "aon"

        # level
        niveis = {}
        if f and f["level"] is not None:
            niveis["foundry"] = f["level"]
        if t and t["level"] is not None:
            niveis["pf2etools"] = t["level"]
        if a and a["level"] is not None:
            niveis["aon"] = a["level"]
        level = None
        if niveis:
            for fonte in ("foundry", "pf2etools", "aon"):
                if fonte in niveis:
                    level = niveis[fonte]
                    prov["level"] = fonte
                    break
            if len(set(niveis.values())) > 1:
                c = {"campo": "level", "escolhido": prov["level"]}
                c.update(niveis)
                conflitos.append(c)
                est["conflitos_por_campo"]["level"] += 1

        # traits / rarity
        traits = None
        if a and a["traits"]:
            traits, prov["traits"] = a["traits"], "aon"
        elif f and f["traits"]:
            traits, prov["traits"] = f["traits"], "foundry"
        elif t and t["traits"]:
            traits, prov["traits"] = t["traits"], "pf2etools"
        if f and a and f["traits"] and a["traits"] and set(f["traits"]) != set(a["traits"]):
            conflitos.append({"campo": "traits", "foundry": sorted(f["traits"]),
                              "aon": sorted(a["traits"]), "escolhido": "aon"})
            est["conflitos_por_campo"]["traits"] += 1

        rarity = None
        if a and a["rarity"]:
            rarity, prov["rarity"] = a["rarity"], "aon"
        elif f and f["rarity"]:
            rarity, prov["rarity"] = f["rarity"], "foundry"

        # source
        source = None
        if a and a["livro"]:
            source = {"book": a["livro"], "page": a["pagina"]}
            prov["source"] = "aon"
            if f and f["licenca"]:
                source["license"] = f["licenca"]
                source["remaster"] = bool(f["remaster"])
            else:
                source["license"] = None
                source["remaster"] = False
        elif f and f["livro"]:
            source = {"book": f["livro"], "license": f["licenca"],
                      "remaster": bool(f["remaster"])}
            prov["source"] = "foundry"
        elif t and t["fonte"]:
            # Terceiro ramo, que faltava: item que so existe no pf2etools saia
            # com `source` vazio por construcao, ainda que `norm_pf2etools` ja
            # lesse `fonte` e `pagina`. Eram `Nine-Ring Sword`,
            # `Wind and Fire Wheel` e `Heavy Power Suit` -- os 3 registros que
            # seguravam o portao 5, lidos como "sem licenca" quando o problema
            # era outro. A fonte grava sigla ("G&G"), expandida pelo mapa que
            # `gerar_siglas_pf2etools.py` extrai do proprio repo.
            source = {"book": expandir_sigla_pf2etools(t["fonte"]),
                      "page": t["pagina"], "remaster": bool(t["remaster"])}
            prov["source"] = "pf2etools"
        completar_licenca(source, prov)
        if source is None or not source.get("license"):
            est["sem_source"] += 1

        # ---- campos mecanicos estruturados (foundry vence) --------------
        mec = {}
        if f:
            if f["bulk"] is not None:
                mec["bulk"] = f["bulk"]
                prov["bulk"] = "foundry"
            if f["preco_cp"] is not None:
                mec["price_cp"] = f["preco_cp"]
                prov["price_cp"] = "foundry"
            if f["usage"]:
                mec["usage"] = f["usage"]
                prov["usage"] = "foundry"
            if f["base_item"]:
                mec["base_item"] = f["base_item"]
                prov["base_item"] = "foundry"

            if kind == "weapon":
                if f.get("categoria"):
                    mec["weapon_category"] = f["categoria"]
                    prov["weapon_category"] = "foundry"
                if f.get("grupo"):
                    mec["group"] = f["grupo"]
                    prov["group"] = "foundry"
                if f.get("dano"):
                    mec["damage"] = f["dano"]
                    prov["damage"] = "foundry"
                if f.get("alcance") is not None:
                    mec["range"] = f["alcance"]
                    prov["range"] = "foundry"
                if f.get("reload") not in (None, "-", ""):
                    mec["reload"] = f["reload"]
                    prov["reload"] = "foundry"
                usage = f.get("usage") or ""
                if usage == "held-in-one-hand":
                    mec["hands"] = 1
                elif usage == "held-in-two-hands":
                    mec["hands"] = 2
                if mec.get("hands"):
                    prov["hands"] = "foundry"
                if f.get("runes"):
                    mec["runes"] = f["runes"]
                    prov["runes"] = "foundry"

            elif kind == "armor":
                if f.get("categoria"):
                    mec["armor_category"] = f["categoria"]
                    prov["armor_category"] = "foundry"
                if f.get("grupo"):
                    mec["group"] = f["grupo"]
                    prov["group"] = "foundry"
                for campo, chave_fonte in (
                    ("ac_bonus", "ac_bonus"), ("dex_cap", "dex_cap"),
                    ("check_penalty", "check_penalty"), ("speed_penalty", "speed_penalty"),
                    ("strength", "strength"),
                ):
                    v = f.get(chave_fonte)
                    if v is not None:
                        mec[campo] = v
                        prov[campo] = "foundry"
                if f.get("runes"):
                    mec["runes"] = f["runes"]
                    prov["runes"] = "foundry"

            elif kind == "shield":
                if f.get("ac_bonus") is not None:
                    mec["ac_bonus"] = f["ac_bonus"]
                    prov["ac_bonus"] = "foundry"
                if f.get("hardness") is not None:
                    mec["hardness"] = f["hardness"]
                    prov["hardness"] = "foundry"
                if f.get("hp") is not None:
                    mec["hp"] = f["hp"]
                    mec["bt"] = f["hp"] // 2
                    prov["hp"] = "foundry"
                    prov["bt"] = "foundry"
                if f.get("speed_penalty") is not None:
                    mec["speed_penalty"] = f["speed_penalty"]
                    prov["speed_penalty"] = "foundry"
                if f.get("runes"):
                    mec["runes"] = f["runes"]
                    prov["runes"] = "foundry"

            else:  # equipment
                mec["equipment_type"] = f["tipo"]
                prov["equipment_type"] = "foundry"
                runa = detectar_runa(sl, f.get("usage"), level)
                if runa:
                    mec["rune"] = runa
                    prov["rune"] = "foundry"
                    est["runas_detectadas"][runa["tipo"]] += 1

        elif a:
            # sem foundry: so temos preco/bulk crus do AoN, sem estrutura fina
            if a.get("preco_cp") is not None:
                mec["price_cp"] = a["preco_cp"]
                prov["price_cp"] = "aon"
            if a.get("bulk_raw"):
                mec["bulk_raw"] = a["bulk_raw"]
                prov["bulk_raw"] = "aon"

        if mec:
            est["com_estrutura_mecanica"][kind] += 1
        else:
            est["so_prosa"][kind] += 1

        # ---- grants (rule elements do Foundry) ---------------------------
        grants, perdeu = ([], False)
        if f and f["rules"]:
            grants, perdeu = converter_grants(f["rules"], ignoradas)
            if grants:
                prov["grants"] = "foundry"

        mechanized = not perdeu
        if mechanized:
            est["mechanized_true"] += 1
        else:
            est["mechanized_false"] += 1

        reg = {
            "id": "wb:%s/%s" % (kind, sl),
            "kind": kind,
            "name": nome,
            "level": level,
            "traits": traits or [],
            "rarity": rarity,
            "source": source,
            "requires": None,
            "grants": grants,
            "text": ("wb:text/%s/%s" % (kind, sl)) if "text" in prov else None,
            "mechanized": mechanized,
            "xref": {},
            "prov": prov,
        }
        reg.update(mec)
        if f:
            reg["xref"]["foundry"] = "Compendium.pf2e.equipment-srd.Item." + f["id"]
        if a:
            reg["xref"]["aon"] = a["id"]
            if a["remaster_id"]:
                reg["remaster_de"] = a["remaster_id"]
            if a["legacy_id"]:
                reg["legado_de"] = a["legacy_id"]
        if t:
            reg["xref"]["pf2etools"] = "baseitems#" + sl
        if conflitos:
            reg["conflitos"] = conflitos
        registros.append(reg)

    ESTATISTICAS.clear()
    ESTATISTICAS.update(est)
    return registros


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    registros = extrair()
    saida = os.path.join(PIPELINE, "saida", "equipamento.json")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=1)

    est = ESTATISTICAS
    ser = {}
    for k, v in est.items():
        ser[k] = dict(v) if isinstance(v, Counter) else v
    with open(os.path.join(PIPELINE, "saida", "_equipamento_estatisticas.json"),
              "w", encoding="utf-8") as fh:
        json.dump(ser, fh, ensure_ascii=False, indent=1)

    print("registros por kind:")
    for k, v in est["por_kind"].most_common():
        print("  %-10s %d" % (k, v))
    print("total ................ %d" % sum(est["por_kind"].values()))
    print()
    print("com estrutura mecanica / so prosa, por kind:")
    for k in est["por_kind"]:
        print("  %-10s %5d estruturados / %5d so-prosa" % (
            k, est["com_estrutura_mecanica"].get(k, 0), est["so_prosa"].get(k, 0)))
    print()
    print("kind reconciliado (aon/pf2etools divergia do foundry): %s" %
          dict(est["kind_reconciliado"]))
    print("runas detectadas: %s" % dict(est["runas_detectadas"]))
    print("mechanized true/false: %d / %d" % (est["mechanized_true"], est["mechanized_false"]))
    print("sem source/licenca: %d" % est["sem_source"])
    print("conflitos por campo: %s" % dict(est["conflitos_por_campo"]))
    print()
    print("cobertura de fontes (kind:combo), top 20:")
    for combo, n in est["cobertura_fontes"].most_common(20):
        print("  %5d  %s" % (n, combo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
