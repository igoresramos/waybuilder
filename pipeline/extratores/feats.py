"""Extrator canonico de FEATS e ARQUETIPOS do Pathfinder 2e (Waybuilder).

Obedece `specs/2026-07-26-schema-base.md`:

  - envelope com `id`, `kind`, `prov` por campo e `conflitos`
  - `requires` na linguagem de predicado (all/any/not, >=, <=, ==)
  - `grants` na linguagem de efeito
  - `mechanized` separa o que o app calcula do que so exibe

Precedencia por campo:

  grants ......... foundry   (unica com rule elements)
  requires ....... pf2etools (unica com {@feat}/{@skill} marcados)
  name/traits/
  rarity/text .... aon       (e a Paizo)
  level .......... foundry, conferido contra pf2etools e aon
  source ......... aon, cai para foundry

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
PROJETO = os.path.dirname(PIPELINE)
BRUTOS = os.path.join(PIPELINE, "dados_brutos")

FOUNDRY_COMMIT = "87f9e5028baaa10b70fdc766260b7886def17e04"

_CANDIDATOS_FOUNDRY = [
    os.environ.get("WB_FOUNDRY_PACKS", ""),
    os.path.join(BRUTOS, "foundry", "packs", "pf2e"),
    "/tmp/claude-1000/-mnt-c-Users-igor0/39eadbed-e8eb-4194-8557-74f05193fdc1"
    "/scratchpad/pf2e-research/pf2e/packs/pf2e",
]


def _packs_foundry() -> str:
    for c in _CANDIDATOS_FOUNDRY:
        if c and os.path.isdir(os.path.join(c, "feats")):
            return c
    raise SystemExit(
        "packs do Foundry nao encontrados. Defina WB_FOUNDRY_PACKS apontando "
        "para <clone>/packs/pf2e (commit %s)." % FOUNDRY_COMMIT
    )


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
    """Chave de casamento de nome: minusculo, sem pontuacao, sem sufixo de fonte."""
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
# Vocabularios
# --------------------------------------------------------------------------

RANK_NUM = {0: "untrained", 1: "trained", 2: "expert", 3: "master", 4: "legendary"}
RANKS = ("untrained", "trained", "expert", "master", "legendary")

PERICIAS = {
    "acrobatics", "arcana", "athletics", "crafting", "deception", "diplomacy",
    "intimidation", "medicine", "nature", "occultism", "performance", "religion",
    "society", "stealth", "survival", "thievery", "perception",
}

ATRIBUTOS = {
    "strength": "str", "dexterity": "dex", "constitution": "con",
    "intelligence": "int", "wisdom": "wis", "charisma": "cha",
    "str": "str", "dex": "dex", "con": "con", "int": "int", "wis": "wis", "cha": "cha",
}

TRADICOES = ("arcane", "divine", "occult", "primal")

# Alvos de proficiencia que nao sao pericia. A chave e a mesma usada em `grants`.
PROFICIENCIA_OUTRA = {
    "simple weapons": "simple", "all simple weapons": "simple",
    "martial weapons": "martial", "all martial weapons": "martial",
    "advanced weapons": "advanced", "all advanced weapons": "advanced",
    "martial firearms": "martial", "simple firearms": "simple",
    "unarmed attacks": "unarmed", "unarmed attack": "unarmed",
    "light armor": "light", "medium armor": "medium", "heavy armor": "heavy",
    "light": "light", "medium": "medium", "heavy": "heavy",
    "unarmored defense": "unarmored", "unarmored": "unarmored",
    "fortitude saves": "fortitude", "fortitude": "fortitude",
    "reflex saves": "reflex", "reflex": "reflex",
    "will saves": "will", "will": "will",
    "perception": "perception",
    "spell attacks": "spell-attack", "spell attack rolls": "spell-attack",
    "spell dcs": "spell-dc", "class dc": "class-dc",
}

# Sufixos de escolha de subclasse: "{@class Magus|...} hybrid study".
SUFIXO_SUBCLASSE = re.compile(
    r"\s+(hybrid study|muse|methodology|order|doctrine|bloodline|instinct|"
    r"racket|way|research field|conscious mind|subconscious mind|cause|"
    r"tenet|discipline|specialty|innovation|element|implement|hunter's edge|"
    r"deity|mystery|patron|lesson|school|thesis|style|form|apparition)s?$", re.I)

# ---- rule elements do Foundry -------------------------------------------

# Convertidos para `grants` (afetam a ficha / a construcao do personagem).
RE_CONVERTIDOS = {
    "FlatModifier", "ActiveEffectLike", "MartialProficiency", "Resistance",
    "Immunity", "Weakness", "BaseSpeed", "Sense", "FastHealing", "TempHP",
    "CreatureSize", "DexterityModifierCap", "CriticalSpecialization",
    "ActorTraits", "GrantItem", "ChoiceSet", "CraftingAbility",
    "SpecialResource", "SpecialStatistic", "DamageDice", "MultipleAttackPenalty",
}

# Ignorados de proposito: automacao de rolagem em mesa, nao construcao de ficha.
# Nao penalizam `mechanized`.
RE_NEUTROS = {
    "Note", "RollOption", "TokenLight", "TokenEffectIcon", "AdjustDegreeOfSuccess",
    "SubstituteRoll", "RollTwice", "AdjustModifier", "AdjustStrike",
    "DamageAlteration", "Strike", "Aura", "EphemeralEffect", "ItemAlteration",
}


# --------------------------------------------------------------------------
# Tokenizacao das tags do pf2etools
# --------------------------------------------------------------------------

TAG_RE = re.compile(r"\{@(\w+)\s+([^{}]*)\}")
MARCA_RE = re.compile(r"\x01(\d+)\x02")


def tokenizar(texto: str):
    """Troca cada `{@tipo corpo}` por uma marca opaca. Devolve (texto, tags).

    Necessario para poder quebrar em `,`/`and`/`or` sem cortar dentro do nome
    de uma entidade marcada.
    """
    tags = []

    def sub(m):
        tags.append((m.group(1), [p.strip() for p in m.group(2).split("|")]))
        return "\x01%d\x02" % (len(tags) - 1)

    anterior = None
    while anterior != texto:
        anterior = texto
        texto = TAG_RE.sub(sub, texto)
    return texto, tags


def expandir(texto: str, tags) -> str:
    def sub(m):
        tipo, partes = tags[int(m.group(1))]
        return partes[0]

    return MARCA_RE.sub(sub, texto)


def assinatura(texto: str, tags) -> str:
    """Forma normalizada de um atomo, para agrupar padroes nao cobertos."""
    def sub(m):
        tipo, _partes = tags[int(m.group(1))]
        return "{" + tipo + "}"

    s = MARCA_RE.sub(sub, texto)
    s = re.sub(r"\d+", "N", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def so_marca(texto: str):
    t = texto.strip()
    m = MARCA_RE.fullmatch(t)
    return int(m.group(1)) if m else None


# --------------------------------------------------------------------------
# Quebra em conectores logicos (nivel de texto, marcas sao opacas)
# --------------------------------------------------------------------------

_PALAVRA_CONECTOR = {
    "or": re.compile(r"\s+or\s+", re.I),
    "and": re.compile(r"\s+and\s+", re.I),
}


def _dividir_virgulas(texto: str):
    """Quebra em `,` de topo. Devolve (partes_limpas, conector)."""
    cru = [p for p in texto.split(",")]
    if len(cru) < 2:
        return [texto], "all"
    lideres = []
    partes = []
    for i, p in enumerate(cru):
        p = p.strip()
        lid = ""
        m = re.match(r"^(and|or|either|and either|or either)\s+", p, re.I)
        if m:
            lid = m.group(1).lower()
            p = p[m.end():].strip()
        if i:
            lideres.append(lid)
        partes.append(p)
    partes = [p for p in partes if p]
    if len(partes) < 2:
        return [texto], "all"
    tem_and = any(l.startswith("and") for l in lideres)
    tem_or = any(l.startswith("or") for l in lideres)
    conector = "any" if (tem_or and not tem_and) else "all"
    return partes, conector


def _dividir_palavra(texto: str, palavra: str):
    partes = [p.strip() for p in _PALAVRA_CONECTOR[palavra].split(texto)]
    return [p for p in partes if p]


# --------------------------------------------------------------------------
# Indices de resolucao de nome -> id wb:
# --------------------------------------------------------------------------

class Indices:
    def __init__(self):
        self.feat = {}           # chave -> slug
        self.class_feature = {}  # chave -> slug
        self.classe = {}         # chave -> slug
        self.arquetipo = {}      # chave -> slug
        self.tracos = set()
        self.ancestralidades = set()

    def resolver(self, nome: str):
        k = chave(nome)
        if not k:
            return None
        if k in self.feat:
            return "wb:feat/" + self.feat[k]
        if k in self.class_feature:
            return "wb:class-feature/" + self.class_feature[k]
        # "Foo (Bar)" -> "Foo"
        base = re.sub(r"\s*\([^)]*\)\s*$", "", k).strip()
        if base != k:
            if base in self.feat:
                return "wb:feat/" + self.feat[base]
            if base in self.class_feature:
                return "wb:class-feature/" + self.class_feature[base]
        return None


# --------------------------------------------------------------------------
# Parser de pre-requisito
# --------------------------------------------------------------------------

RANK_RE = re.compile(
    r"^(?:you (?:must )?(?:are|be)\s+|must be\s+|be\s+|being\s+)?"
    r"(untrained|trained|expert|master|legendary)\s+(?:proficiency\s+)?in\s+(.+)$", re.I)

ATRIB_VAL_RE = re.compile(
    r"^(strength|dexterity|constitution|intelligence|wisdom|charisma)\s+(\d+)$", re.I)
ATRIB_MOD_RE = re.compile(
    r"^(strength|dexterity|constitution|intelligence|wisdom|charisma|"
    r"str|dex|con|int|wis|cha)\s*\+(\d+)$", re.I)

NIVEL_RE = re.compile(r"^(?:character\s+)?level\s+(\d+)(?:\+)?$", re.I)
NIVEL_ORD_RE = re.compile(r"^(\d+)(?:st|nd|rd|th)[\s-]*level(?:\s+character)?$", re.I)
NIVEL_FRASE_RE = re.compile(
    r"^(?:you are\s+)?(?:at least\s+)?(\d+)(?:st|nd|rd|th)[\s-]*level(?:\s+or higher)?$",
    re.I)

TRADICAO_RE = re.compile(
    r"^(?:the\s+)?ability to cast (arcane|divine|occult|primal) spells"
    r"(?:\s+from spell slots)?$", re.I)

QUALQUER_CONJURACAO_RE = re.compile(
    r"^(?:you (?:have|are)\s+|able to cast\s+|ability to cast\s+)?"
    r"(?:a\s+)?(?:spellcasting class feature|spells from spell slots|"
    r"able to cast spells|ability to cast spells)$", re.I)

CAST_SPELL_RE = re.compile(
    r"^(?:the\s+)?(?:ability|able) to cast (\x01\d+\x02)"
    r"(?:\s+as an? .*)?$", re.I)

HERANCA_RE = re.compile(r"^(.+?)\s+heritage$", re.I)
TRACO_RE = re.compile(r"^(.+?)\s+trait$", re.I)

CLASSE_NIVEL_RE = re.compile(r"^(\w[\w\s]*?)\s+level\s+(\d+)$", re.I)

LORE_RE = re.compile(r"^(.+?)\s+lore$", re.I)

LIXO_PREFIXO = re.compile(
    r"^(?:you must\s+|you\s+|must\s+|have\s+|having\s+|possess\s+|the\s+)", re.I)


class ResultadoPredicado:
    __slots__ = ("pred", "falhas")

    def __init__(self, pred=None, falhas=None):
        self.pred = pred
        self.falhas = falhas or []


class Parser:
    """Transforma a prosa de pre-requisito em predicado do schema."""

    def __init__(self, idx: Indices):
        self.idx = idx
        self.falhas = []

    # -- entrada -----------------------------------------------------------
    def parse(self, bruto: str):
        self.falhas = []
        if not bruto or not bruto.strip():
            return ResultadoPredicado(None, [])
        texto, tags = tokenizar(bruto.strip())
        texto = texto.strip().rstrip(".")
        pred = self._expr(texto, tags)
        if pred is None:
            return ResultadoPredicado(None, self.falhas)
        return ResultadoPredicado(self._simplificar(pred), [])

    # -- combinadores ------------------------------------------------------
    @staticmethod
    def _simplificar(pred):
        if isinstance(pred, dict) and len(pred) == 1:
            op = next(iter(pred))
            if op in ("all", "any"):
                itens = []
                for i in pred[op]:
                    i = Parser._simplificar(i)
                    # achata grupo aninhado do mesmo operador
                    if isinstance(i, dict) and len(i) == 1 and op in i:
                        itens.extend(i[op])
                    else:
                        itens.append(i)
                if len(itens) == 1:
                    return itens[0]
                return {op: itens}
        return pred

    def _combinar(self, op, partes, tags):
        saida = []
        for p in partes:
            r = self._expr(p, tags)
            if r is None:
                return None
            saida.append(r)
        if len(saida) == 1:
            return saida[0]
        return {op: saida}

    # -- gramatica ---------------------------------------------------------
    def _expr(self, texto, tags):
        texto = texto.strip().strip(".").strip()
        if not texto:
            return None

        # 1. ponto-e-virgula: AND de topo
        if ";" in texto:
            partes = [p.strip() for p in texto.split(";") if p.strip()]
            partes = [re.sub(r"^(and|or)\s+", "", p, flags=re.I) for p in partes]
            if len(partes) > 1:
                return self._combinar("all", partes, tags)

        # 2. clausula de rank com lista propria de pericias
        #    ("expert in Acrobatics, Athletics, or Stealth")
        r = self._clausula_rank(texto, tags)
        if r is not None:
            return r

        # 3. virgulas
        partes, conector = _dividir_virgulas(texto)
        if len(partes) > 1:
            return self._combinar(conector, partes, tags)

        # 4. either ... or ...
        m = re.match(r"^either\s+(.+)$", texto, re.I)
        if m:
            alt = _dividir_palavra(m.group(1), "or")
            if len(alt) > 1:
                return self._combinar("any", alt, tags)
            texto = m.group(1)

        # 5. or
        alt = _dividir_palavra(texto, "or")
        if len(alt) > 1:
            return self._combinar("any", alt, tags)

        # 6. and
        conj = _dividir_palavra(texto, "and")
        if len(conj) > 1:
            return self._combinar("all", conj, tags)

        # 7. atomo
        return self._atomo(texto, tags)

    # -- clausula de rank --------------------------------------------------
    def _clausula_rank(self, texto, tags):
        m = RANK_RE.match(texto)
        if not m:
            return None
        rank = m.group(1).lower()
        resto = m.group(2).strip()
        # a lista so vale se TODO item for pericia; senao a frase e outra coisa
        itens = re.split(r",\s*|\s+or\s+|\s+and\s+", resto)
        itens = [re.sub(r"^(?:and|or|either)\s+", "", i.strip(), flags=re.I)
                 for i in itens]
        itens = [i for i in itens if i]
        if not itens:
            return None
        pericias = []
        for i in itens:
            p = self._pericia(i, tags)
            if p is None:
                return None
            pericias.append(p)
        conector = "any" if re.search(r"\s+or\s+", resto, re.I) else "all"
        preds = [{"proficiency": {p: {">=": rank}}} for p in pericias]
        if len(preds) == 1:
            return preds[0]
        return {conector: preds}

    def _pericia(self, texto, tags):
        """Alvo de proficiencia: pericia, Lore, arma, armadura, salvaguarda."""
        t = texto.strip().strip(".")
        t = re.sub(r"^(?:a|an|any|all|any kind of)\s+", "", t, flags=re.I).strip()
        i = so_marca(t)
        if i is not None:
            tipo, partes = tags[i]
            if tipo == "item":
                return "weapon:" + slug(partes[0])
            if tipo != "skill":
                return None
            # {@skill Lore||Warfare Lore} -> o rotulo real esta em partes[2]
            nome = partes[2] if len(partes) >= 3 and partes[2] else partes[0]
        else:
            nome = expandir(t, tags)
        n = chave(nome)
        if n in PERICIAS:
            return n
        if n in PROFICIENCIA_OUTRA:
            return PROFICIENCIA_OUTRA[n]
        m = LORE_RE.match(n)
        if m:
            return "lore:" + slug(m.group(1))
        if n in ("lore", "a lore skill", "lore skill", "any lore", "any lore skill",
                 "one lore skill"):
            return "lore:*"
        if n in ("weapon", "kind of weapon", "weapons"):
            return "weapon:*"
        return None

    # -- atomo -------------------------------------------------------------
    def _atomo(self, texto, tags):
        t = texto.strip().strip(".").strip()
        if not t:
            return None

        # a) marca unica -> entidade tipada
        i = so_marca(t)
        if i is not None:
            p = self._tag(tags[i])
            if p is not None:
                return p
            self._falhar(t, tags)
            return None

        # b) atributo
        m = ATRIB_VAL_RE.match(t)
        if m:
            return {"ability": {ATRIBUTOS[m.group(1).lower()]: {">=": int(m.group(2))}}}
        m = ATRIB_MOD_RE.match(t)
        if m:
            # Foundry escreve o modificador; o schema guarda o valor do atributo
            return {"ability": {ATRIBUTOS[m.group(1).lower()]:
                                {">=": 10 + 2 * int(m.group(2))}}}

        # c) nivel de personagem
        for rx in (NIVEL_RE, NIVEL_ORD_RE, NIVEL_FRASE_RE):
            m = rx.match(t)
            if m:
                return {"character_level": {">=": int(m.group(1))}}

        # d) tradicao de conjuracao
        m = TRADICAO_RE.match(t)
        if m:
            return {"spellcasting_tradition": m.group(1).lower()}
        if QUALQUER_CONJURACAO_RE.match(t):
            return {"any": [{"spellcasting_tradition": x} for x in TRADICOES]}
        m = CAST_SPELL_RE.match(t)
        if m:
            j = so_marca(m.group(1))
            if j is not None and tags[j][0] == "spell":
                return {"has": "wb:spell/" + slug(tags[j][1][0])}

        # d2) "<X> heritage" / "<X> trait"
        m = HERANCA_RE.match(t)
        if m:
            alvo = m.group(1).strip()
            j = so_marca(alvo)
            if j is not None and tags[j][0] == "ancestry":
                p = self._tag(tags[j])
                if p is not None:
                    return p
            nome = expandir(alvo, tags).strip()
            if nome:
                return {"has": "wb:heritage/" + slug(nome)}
        m = TRACO_RE.match(t)
        if m:
            alvo = m.group(1).strip()
            j = so_marca(alvo)
            if j is not None and tags[j][0] == "trait":
                return {"trait": slug(tags[j][1][0])}
            nome = expandir(alvo, tags).strip()
            if nome and " " not in nome:
                return {"trait": slug(nome)}

        # d3) marca de classe/ancestralidade seguida de substantivo de subclasse
        m = re.match(r"^(\x01\d+\x02)(\s+.+)$", t)
        if m and SUFIXO_SUBCLASSE.search(m.group(2)):
            j = so_marca(m.group(1))
            if j is not None and tags[j][0] in ("class", "ancestry"):
                p = self._tag(tags[j])
                if p is not None:
                    return p

        # e) clausula de rank residual (sem lista)
        r = self._clausula_rank(t, tags)
        if r is not None:
            return r

        # f) nivel de classe: "fighter level 5"
        m = CLASSE_NIVEL_RE.match(t)
        if m and chave(m.group(1)) in self.idx.classe:
            return {"class_level": {self.idx.classe[chave(m.group(1))]:
                                    {">=": int(m.group(2))}}}

        # g) nome nu, com e sem prefixo de ruido
        for cand in (t, LIXO_PREFIXO.sub("", t, count=1)):
            nome = expandir(cand, tags).strip().strip(".")
            k = chave(nome)
            if not k:
                continue
            if k in self.idx.classe:
                return {"class_level": {self.idx.classe[k]: {">=": 1}}}
            ref = self.idx.resolver(nome)
            if ref:
                return {"has": ref}
            if k in self.idx.arquetipo:
                return {"has": "wb:archetype/" + self.idx.arquetipo[k]}
            if k in self.idx.ancestralidades:
                return {"trait": slug(k)}
            if k in self.idx.tracos:
                return {"trait": slug(k)}

        self._falhar(t, tags)
        return None

    # -- entidades marcadas ------------------------------------------------
    def _tag(self, tag):
        tipo, partes = tag
        nome = partes[0]
        if tipo == "skill":
            return None  # so faz sentido dentro de clausula de rank
        if tipo == "feat":
            ref = self.idx.resolver(nome)
            return {"has": ref or ("wb:feat/" + slug(nome))}
        if tipo == "class":
            k = chave(nome)
            cls = self.idx.classe.get(k)
            if not cls:
                return None
            base = {"class_level": {cls: {">=": 1}}}
            # {@class bard|crb|Enigma muse|enigma} -> classe + subclasse
            sub = ""
            if len(partes) >= 4 and partes[3]:
                sub = partes[2] if len(partes) >= 3 and partes[2] else partes[3]
            if sub:
                ref = self.idx.resolver(sub)
                if ref is None:
                    ref = "wb:class-feature/" + slug(sub)
                return {"all": [base, {"has": ref}]}
            return base
        if tipo in ("action", "classFeature"):
            ref = self.idx.resolver(nome)
            if ref:
                return {"has": ref}
            return None
        if tipo == "archetype":
            k = chave(nome)
            if k in self.idx.arquetipo:
                return {"has": "wb:archetype/" + self.idx.arquetipo[k]}
            ded = self.idx.resolver(nome)  # "X Dedication" ja vem como feat
            if ded:
                return {"has": ded}
            return None
        if tipo == "trait":
            return {"trait": slug(nome)}
        if tipo == "ancestry":
            base = {"trait": slug(nome)}
            if len(partes) >= 4 and partes[3]:
                her = partes[2] if partes[2] else partes[3]
                return {"all": [base, {"has": "wb:heritage/" + slug(her)}]}
            return base
        if tipo == "spell":
            return {"has": "wb:spell/" + slug(nome)}
        if tipo == "deity":
            return {"has": "wb:deity/" + slug(nome)}
        if tipo == "item":
            return {"has": "wb:equipment/" + slug(nome)}
        if tipo == "background":
            return {"has": "wb:background/" + slug(nome)}
        return None

    def _falhar(self, texto, tags):
        self.falhas.append(assinatura(texto, tags))


# --------------------------------------------------------------------------
# Rule elements -> grants
# --------------------------------------------------------------------------

AEL_PERICIA = re.compile(r"^system\.skills\.([a-z\-]+)\.rank$")
AEL_PERICIA_ESCOLHA = re.compile(r"^system\.skills\.\{item\|.*\}\.rank$")
AEL_PROF = re.compile(r"^system\.proficiencies\.([a-z]+)\.([a-z\-]+)\.rank$")
AEL_PROF2 = re.compile(r"^system\.(martial|attributes\.classDC)\.([a-z\-]+)\.rank$")
AEL_PROF3 = re.compile(r"^system\.proficiencies\.([a-z\-]+)\.rank$")
AEL_FOCO = re.compile(r"^system\.resources\.focus\.(max|value)$")
AEL_HP = re.compile(r"^system\.attributes\.hp\.(max|value)$")
AEL_SENTIDO = re.compile(r"^system\.perception\.rank$")

# Caminhos de ficha que o construtor sabe representar sem interpretar o Foundry.
AEL_NOMEADO = {
    "system.attributes.dying.max": "dying_max",
    "system.attributes.dying.recoveryDC": "dying_recovery_dc",
    "system.attributes.hp.recoveryMultiplier": "hp_recovery_multiplier",
    "system.attributes.reach.base": "reach",
    "system.attributes.familiarAbilities.value": "familiar_abilities",
    "system.build.languages.granted": "languages",
    "system.build.languages.max": "languages_max",
    "inventory.bulk.maxAddend": "bulk_max",
    "inventory.bulk.encumberedAfterAddend": "bulk_encumbered",
    "system.initiative.tiebreakPriority": "initiative_tiebreak",
    "system.attributes.flanking.canGangUp": "flanking_gang_up",
    "system.attributes.flanking.offGuardable": "flanking_off_guardable",
    "system.resources.versatileVials.max": "versatile_vials",
    "system.crafting.entries.advancedAlchemy.maxSlots": "advanced_alchemy_slots",
    "system.attributes.speed.value": "speed_land",
}


def _rank_palavra(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return RANK_NUM.get(v)
    if isinstance(v, str) and v.lower() in RANKS:
        return v.lower()
    return None


def converter_grants(regras, contagem_ignoradas):
    """Traduz `system.rules` do Foundry para a linguagem de efeito.

    Devolve (grants, perdeu_mecanica). `perdeu_mecanica` marca rule element
    relevante para a ficha que nao coube na linguagem -- e o que derruba
    `mechanized`.
    """
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

        elif k == "ActiveEffectLike":
            path = r.get("path") or ""
            val = r.get("value")
            m = AEL_PERICIA.match(path)
            if m:
                rk = _rank_palavra(val)
                if rk:
                    grants.append({"proficiency": {m.group(1): rk}})
                else:
                    grants.append({"skill_training": {"auto": [m.group(1)]}})
                continue
            if AEL_PERICIA_ESCOLHA.match(path):
                rk = _rank_palavra(val)
                grants.append({"skill_training": {"free": 1, "rank": rk or val}})
                continue
            m = AEL_PROF.match(path) or AEL_PROF2.match(path)
            if m:
                rk = _rank_palavra(val)
                grants.append({"proficiency": {m.group(2): rk or val}})
                continue
            m = AEL_PROF3.match(path)
            if m:
                rk = _rank_palavra(val)
                grants.append({"proficiency": {m.group(1): rk or val}})
                continue
            if path in AEL_NOMEADO:
                grants.append({AEL_NOMEADO[path]: val})
                continue
            if AEL_FOCO.match(path):
                grants.append({"focus_pool": val})
                continue
            if AEL_HP.match(path):
                grants.append({"hp": val})
                continue
            if AEL_SENTIDO.match(path):
                rk = _rank_palavra(val)
                grants.append({"proficiency": {"perception": rk or val}})
                continue
            # caminho de flag interna do Foundry: contador de arquetipo etc.
            if path.startswith("flags."):
                contagem_ignoradas["ActiveEffectLike:flags"] += 1
                continue
            contagem_ignoradas["ActiveEffectLike:" + path] += 1
            perdeu = True

        elif k == "MartialProficiency":
            grants.append({"weapon_proficiency": {
                "definicao": r.get("definition"),
                "igual_a": r.get("sameAs"),
                "rank": _rank_palavra(r.get("value")),
            }})

        elif k == "Resistance":
            grants.append({"resistance": {"tipo": r.get("type"), "valor": r.get("value")}})
        elif k == "Immunity":
            grants.append({"immunity": r.get("type")})
        elif k == "Weakness":
            grants.append({"weakness": {"tipo": r.get("type"), "valor": r.get("value")}})
        elif k == "BaseSpeed":
            grants.append({"speed": {"tipo": r.get("selector"), "valor": r.get("value")}})
        elif k == "Sense":
            grants.append({"sense": {"tipo": r.get("selector"),
                                     "acuidade": r.get("acuity"),
                                     "alcance": r.get("range")}})
        elif k == "FastHealing":
            grants.append({"fast_healing": r.get("value")})
        elif k == "TempHP":
            grants.append({"temp_hp": r.get("value")})
        elif k == "CreatureSize":
            grants.append({"size": r.get("value")})
        elif k == "DexterityModifierCap":
            grants.append({"dex_cap": r.get("value")})
        elif k == "CriticalSpecialization":
            grants.append({"critical_specialization": True})
        elif k == "ActorTraits":
            grants.append({"actor_traits": r.get("add")})
        elif k == "GrantItem":
            grants.append({"grant_item": {"uuid": r.get("uuid")}})
        elif k == "ChoiceSet":
            esc = r.get("choices")
            resumo = {"flag": r.get("flag")}
            if isinstance(esc, list):
                resumo["opcoes"] = len(esc)
            elif isinstance(esc, dict):
                resumo["filtro"] = True
                if esc.get("itemType"):
                    resumo["tipo"] = esc["itemType"]
            elif isinstance(esc, str):
                resumo["referencia"] = esc
            grants.append({"choice": resumo})
        elif k == "CraftingAbility":
            grants.append({"crafting_ability": {"slug": r.get("slug"),
                                                "slots": r.get("maxSlots")}})
        elif k == "SpecialResource":
            grants.append({"special_resource": {"slug": r.get("slug"),
                                                "max": r.get("max")}})
        elif k == "SpecialStatistic":
            grants.append({"special_statistic": {"slug": r.get("slug")}})
        elif k == "DamageDice":
            grants.append({"damage_dice": {"selector": r.get("selector"),
                                           "quantidade": r.get("diceNumber")}})
        elif k == "MultipleAttackPenalty":
            grants.append({"map_modifier": r.get("value")})

    return grants, perdeu


# --------------------------------------------------------------------------
# Carga das fontes
# --------------------------------------------------------------------------

def carregar_foundry(packs):
    """Feats do Foundry + indice de class-features + classes + arquetipos."""
    feats = []
    raiz_feats = os.path.join(packs, "feats")
    for caminho in _andar(raiz_feats):
        try:
            d = _ler_json(caminho)
        except Exception:
            continue
        if not isinstance(d, dict) or d.get("type") != "feat":
            continue
        rel = os.path.relpath(caminho, raiz_feats)
        partes = rel.split(os.sep)
        arqt = partes[1] if partes[0] == "archetype" and len(partes) > 2 else None
        classe = partes[1] if partes[0] == "class" and len(partes) > 2 else None
        d["_rel"] = rel
        d["_archetype_dir"] = arqt
        d["_class_dir"] = classe
        feats.append(d)

    class_features = {}
    raiz_cf = os.path.join(packs, "class-features")
    if os.path.isdir(raiz_cf):
        for caminho in _andar(raiz_cf):
            try:
                d = _ler_json(caminho)
            except Exception:
                continue
            n = d.get("name")
            if n:
                class_features.setdefault(chave(n), slug(n))

    classes = {}
    raiz_cls = os.path.join(packs, "classes")
    if os.path.isdir(raiz_cls):
        for caminho in _andar(raiz_cls):
            try:
                d = _ler_json(caminho)
            except Exception:
                continue
            n = d.get("name")
            if n:
                classes[chave(n)] = slug(n)

    return feats, class_features, classes


def carregar_pf2etools():
    dirp = os.path.join(BRUTOS, "pf2etools")
    feats = []
    if not os.path.isdir(dirp):
        return feats
    for a in sorted(os.listdir(dirp)):
        if not (a.startswith("feats-") and a.endswith(".json")):
            continue
        try:
            d = _ler_json(os.path.join(dirp, a))
        except Exception:
            continue
        for f in d.get("feat", []) or []:
            f["_arquivo"] = a
            feats.append(f)
    return feats


def carregar_aon(nome):
    for cand in (os.path.join(BRUTOS, nome),
                 os.path.join(BRUTOS, "aon", nome)):
        if os.path.exists(cand):
            return _ler_json(cand)
    return []


# --------------------------------------------------------------------------
# Normalizacao por fonte
# --------------------------------------------------------------------------

LICENCA_LIVRO = {}


def _licenca(livro, remaster):
    if remaster:
        return "ORC"
    return "OGL"


def norm_foundry(d):
    s = d["system"]
    pub = s.get("publication", {}) or {}
    traits = (s.get("traits", {}) or {}).get("value", []) or []
    pre = [p.get("value") for p in (s.get("prerequisites", {}) or {}).get("value", [])
           if isinstance(p, dict) and p.get("value")]
    return {
        "nome": d.get("name"),
        "level": (s.get("level", {}) or {}).get("value"),
        "traits": [slug(t) for t in traits],
        "rarity": (s.get("traits", {}) or {}).get("rarity"),
        "categoria": s.get("category"),
        "prereq": ", ".join(pre) if pre else None,
        "prereq_lista": pre,
        "rules": s.get("rules", []) or [],
        "descricao": (s.get("description", {}) or {}).get("value"),
        "livro": pub.get("title"),
        "licenca": pub.get("license"),
        "remaster": pub.get("remaster"),
        "id": d.get("_id"),
        "archetype_dir": d.get("_archetype_dir"),
        "class_dir": d.get("_class_dir"),
        "max_takable": s.get("maxTakable"),
        "only_level_1": s.get("onlyLevel1"),
    }


def norm_pf2etools(f):
    return {
        "nome": f.get("name"),
        "level": f.get("level"),
        "traits": [slug(t) for t in (f.get("traits") or [])],
        "prereq": f.get("prerequisites"),
        "fonte": f.get("source"),
        "pagina": f.get("page"),
        "remaster": f.get("remaster"),
        "featType": f.get("featType"),
        "leadsTo": f.get("leadsTo"),
    }


RARIDADES = {"common", "uncommon", "rare", "unique"}


def norm_aon(a):
    src = a.get("primary_source_raw") or ""
    m = re.search(r"pg\.\s*(\d+)", src)
    # o AoN mistura raridade dentro de `trait`; raridade tem campo proprio
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
        "archetype": a.get("archetype") or [],
        "remaster_id": a.get("remaster_id") or [],
        "legacy_id": a.get("legacy_id") or [],
        "prereq": a.get("prerequisite"),
        "pfs": a.get("pfs"),
        "excluir": a.get("exclude_from_search"),
    }


# --------------------------------------------------------------------------
# Extracao
# --------------------------------------------------------------------------

ESTATISTICAS = {}


def extrair():
    packs = _packs_foundry()

    f_brutos, idx_class_feature, idx_classes = carregar_foundry(packs)
    t_brutos = carregar_pf2etools()
    a_feats = carregar_aon("aon_feats.json")
    a_arqs = carregar_aon("aon_archetypes.json")

    foundry = [norm_foundry(d) for d in f_brutos]
    tools = [norm_pf2etools(f) for f in t_brutos]
    aon = [norm_aon(a) for a in a_feats]
    aon_arq = [norm_aon(a) for a in a_arqs]

    # ---- indices de nome ------------------------------------------------
    idx = Indices()
    idx.class_feature = idx_class_feature
    idx.classe = idx_classes

    def registrar_feat(nome):
        k = chave(nome)
        if k and k not in idx.feat:
            idx.feat[k] = slug(nome)

    for r in foundry:
        registrar_feat(r["nome"])
    for r in tools:
        registrar_feat(r["nome"])
    for r in aon:
        registrar_feat(r["nome"])
    # variantes sem sufixo entre parenteses
    for k in list(idx.feat):
        base = re.sub(r"\s*\([^)]*\)\s*$", "", k).strip()
        if base and base not in idx.feat:
            idx.feat[base] = idx.feat[k]

    for r in aon_arq:
        k = chave(r["nome"])
        if k:
            idx.arquetipo[k] = slug(r["nome"])
    dirs_arq = set()
    raiz_arq = os.path.join(packs, "feats", "archetype")
    if os.path.isdir(raiz_arq):
        for d in sorted(os.listdir(raiz_arq)):
            if os.path.isdir(os.path.join(raiz_arq, d)):
                dirs_arq.add(d)
                idx.arquetipo.setdefault(chave(d.replace("-", " ")), d)

    for r in foundry:
        for t in r["traits"]:
            idx.tracos.add(chave(t))
    for r in aon:
        for t in r["traits"]:
            idx.tracos.add(chave(t))

    # ---- agrupamento por chave de nome ----------------------------------
    #    Nomes se repetem entre linha legada e remaster. Preferimos sempre o
    #    registro remaster: e a linha viva e o schema deriva o slug dele.
    porchave = defaultdict(lambda: {"foundry": None, "pf2etools": None, "aon": None})
    est_dup = Counter()

    def melhor(atual, novo, remaster_novo):
        if atual is None:
            return novo
        est_dup["homonimos"] += 1
        return novo if remaster_novo and not atual.get("_remaster") else atual

    for r in foundry:
        k = chave(r["nome"])
        r["_remaster"] = bool(r["remaster"])
        porchave[k]["foundry"] = melhor(porchave[k]["foundry"], r, r["_remaster"])
    for r in tools:
        k = chave(r["nome"])
        r["_remaster"] = bool(r.get("remaster"))
        porchave[k]["pf2etools"] = melhor(porchave[k]["pf2etools"], r, r["_remaster"])
    for r in aon:
        if r.get("excluir"):
            continue
        k = chave(r["nome"])
        # sem `remaster_id` = nao foi substituido, logo e a versao corrente
        r["_remaster"] = not r["remaster_id"]
        porchave[k]["aon"] = melhor(porchave[k]["aon"], r, r["_remaster"])

    # ---- vinculo feat -> arquetipo (fonte exata: diretorio do Foundry) ---
    arq_por_chave = {}
    for r in foundry:
        if r["archetype_dir"]:
            arq_por_chave[chave(r["nome"])] = r["archetype_dir"]

    # ---- parsing --------------------------------------------------------
    parser = Parser(idx)
    ignoradas = Counter()

    # tabela livro -> (licenca, remaster), observada no Foundry. Serve para
    # completar registros cuja fonte vencedora nao carrega licenca.
    licenca_por_livro = {}
    for rf in foundry:
        if rf["livro"] and rf["licenca"]:
            licenca_por_livro.setdefault(chave(rf["livro"]),
                                         (rf["licenca"], bool(rf["remaster"])))
    # e a mesma tabela indexada pela sigla do pf2etools, deduzida por cruzamento
    # (mesmo feat presente nas duas fontes) -- nao por lista escrita a mao
    votos = defaultdict(Counter)
    _f_por_chave = {}
    for rf in foundry:
        _f_por_chave.setdefault(chave(rf["nome"]), rf)
    for rt in tools:
        rf = _f_por_chave.get(chave(rt["nome"]))
        if rf and rf["licenca"] and rt.get("fonte"):
            votos[chave(rt["fonte"])][(rf["licenca"], bool(rf["remaster"]))] += 1
    for sigla, cnt in votos.items():
        licenca_por_livro.setdefault(sigla, cnt.most_common(1)[0][0])

    def completar_licenca(src, prov_dict):
        if not src or src.get("license"):
            return
        info = licenca_por_livro.get(chave(src.get("book") or ""))
        if info:
            src["license"], src["remaster"] = info[0], info[1]
            prov_dict["source"] = (prov_dict.get("source") or "aon") + "+foundry(licenca)"

    est = {
        "foundry_total": len(foundry),
        "pf2etools_total": len(tools),
        "aon_total": len(aon),
        "aon_arquetipos": len(a_arqs),
        "registros": 0,
        "com_prereq": 0,
        "prereq_ok": 0,
        "prereq_falha": 0,
        "prereq_por_fonte": Counter(),
        "falhas_por_padrao": Counter(),
        "falhas_exemplos": {},
        "mechanized_true": 0,
        "mechanized_false": 0,
        "motivo_nao_mechanized": Counter(),
        "rules_ignoradas": ignoradas,
        "conflitos_por_campo": Counter(),
        "cobertura_fontes": Counter(),
        "homonimos": est_dup,
        "arquetipos_emitidos": 0,
        "feats_com_arquetipo": 0,
        "aon_arch_contaminacao": Counter(),
    }

    registros = []
    for k, grupo in sorted(porchave.items()):
        f, t, a = grupo["foundry"], grupo["pf2etools"], grupo["aon"]
        nome = (a or f or t)["nome"]
        sl = slug(nome)
        if not sl:
            continue

        combo = "".join(c for c, v in (("F", f), ("T", t), ("A", a)) if v)
        est["cobertura_fontes"][combo] += 1

        prov = {}
        conflitos = []

        # nome / texto
        prov["name"] = "aon" if a else ("foundry" if f else "pf2etools")
        prov["text"] = "aon" if (a and a["texto"]) else ("foundry" if f else None)
        if prov["text"] is None:
            del prov["text"]

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
        if f and a and f["rarity"] and a["rarity"] and f["rarity"] != a["rarity"]:
            conflitos.append({"campo": "rarity", "foundry": f["rarity"],
                              "aon": a["rarity"], "escolhido": "aon"})
            est["conflitos_por_campo"]["rarity"] += 1

        # source
        source = None
        if a and a["livro"]:
            source = {"book": a["livro"], "page": a["pagina"]}
            prov["source"] = "aon"
            if f and f["licenca"]:
                source["license"] = f["licenca"]
                source["remaster"] = bool(f["remaster"])
            else:
                source["license"] = _licenca(a["livro"], False)
                source["remaster"] = False
        elif f and f["livro"]:
            source = {"book": f["livro"], "license": f["licenca"],
                      "remaster": bool(f["remaster"])}
            prov["source"] = "foundry"
        elif t and t["fonte"]:
            source = {"book": t["fonte"], "page": t["pagina"],
                      "license": None, "remaster": bool(t["remaster"])}
            prov["source"] = "pf2etools"

        completar_licenca(source, prov)

        # ---- requires ---------------------------------------------------
        bruto_pre = None
        fonte_pre = None
        if t and t["prereq"]:
            bruto_pre, fonte_pre = t["prereq"], "pf2etools"
        elif a and a["prereq"]:
            bruto_pre, fonte_pre = a["prereq"], "aon"
        elif f and f["prereq"]:
            bruto_pre, fonte_pre = f["prereq"], "foundry"

        requires = None
        requires_ok = True
        if bruto_pre:
            est["com_prereq"] += 1
            est["prereq_por_fonte"][fonte_pre] += 1
            res = parser.parse(bruto_pre)
            if res.pred is not None:
                requires = res.pred
                prov["requires"] = fonte_pre
                est["prereq_ok"] += 1
            else:
                requires_ok = False
                est["prereq_falha"] += 1
                for pad in (res.falhas or ["<sem atomo>"]):
                    est["falhas_por_padrao"][pad] += 1
                    est["falhas_exemplos"].setdefault(pad, bruto_pre)

        # ---- grants -----------------------------------------------------
        grants = []
        perdeu = False
        if f:
            grants, perdeu = converter_grants(f["rules"], ignoradas)
            if grants:
                prov["grants"] = "foundry"

        mechanized = requires_ok and not perdeu
        if mechanized:
            est["mechanized_true"] += 1
        else:
            est["mechanized_false"] += 1
            if not requires_ok:
                est["motivo_nao_mechanized"]["requires-nao-parseado"] += 1
            if perdeu:
                est["motivo_nao_mechanized"]["rule-element-nao-modelado"] += 1

        # ---- arquetipo --------------------------------------------------
        arq = arq_por_chave.get(k)
        if arq:
            prov["archetype"] = "foundry"
            est["feats_com_arquetipo"] += 1
        if a and a["archetype"]:
            aon_arch = {slug(x) for x in a["archetype"]}
            if arq and arq not in aon_arch:
                est["aon_arch_contaminacao"]["aon-nao-tem-o-do-foundry"] += 1
            if arq and len(aon_arch) > 1:
                est["aon_arch_contaminacao"]["aon-multivalorado"] += 1
            if not arq and aon_arch:
                est["aon_arch_contaminacao"]["so-aon-afirma-arquetipo"] += 1

        reg = {
            "id": "wb:feat/" + sl,
            "kind": "feat",
            "name": nome,
            "level": level,
            "traits": traits or [],
            "rarity": rarity,
            "source": source,
            "requires": requires,
            "grants": grants,
            "text": ("wb:text/feat/" + sl) if "text" in prov else None,
            "mechanized": mechanized,
            "xref": {},
            "prov": prov,
        }
        if bruto_pre:
            reg["requires_texto"] = bruto_pre
        if arq:
            reg["archetype"] = "wb:archetype/" + arq
        if f:
            reg["xref"]["foundry"] = "Compendium.pf2e.feats-srd.Item." + f["id"]
            if f["categoria"]:
                reg["feat_category"] = f["categoria"]
        if a:
            reg["xref"]["aon"] = a["id"]
            if a["remaster_id"]:
                reg["remaster_de"] = a["remaster_id"]
            if a["legacy_id"]:
                reg["legado_de"] = a["legacy_id"]
        if t:
            reg["xref"]["pf2etools"] = (t["fonte"] or "?") + "#" + sl
        if conflitos:
            reg["conflitos"] = conflitos
        registros.append(reg)
        est["registros"] += 1

    # ---- arquetipos ------------------------------------------------------
    arq_por_slug = {}
    for r in aon_arq:
        if r.get("excluir"):
            continue
        sl = slug(r["nome"])
        arq_por_slug[sl] = r
    for d in sorted(dirs_arq):
        arq_por_slug.setdefault(d, None)

    contagem_feats = Counter(v for v in arq_por_chave.values())

    # licenca/edicao do arquetipo herdada do feat de Dedication (tem publication)
    licenca_dedicacao = {}
    for rf in foundry:
        if rf["archetype_dir"] and rf["nome"].lower().endswith("dedication"):
            if rf["licenca"]:
                licenca_dedicacao.setdefault(
                    rf["archetype_dir"], (rf["licenca"], rf["remaster"], rf["livro"]))

    for sl in sorted(arq_por_slug):
        r = arq_por_slug[sl]
        prov = {}
        conflitos = []
        nome = r["nome"] if r else sl.replace("-", " ").title()
        prov["name"] = "aon" if r else "foundry"
        if r and r["texto"]:
            prov["text"] = "aon"
        if r and r["rarity"]:
            prov["rarity"] = "aon"
        if r and r["traits"]:
            prov["traits"] = "aon"
        # Licenca do arquetipo: sai do feat de Dedication, que tem `publication`
        ded = licenca_dedicacao.get(sl)
        source = None
        if r and r["livro"]:
            source = {"book": r["livro"], "page": r["pagina"],
                      "license": ded[0] if ded else None,
                      "remaster": bool(ded[1]) if ded else False}
            prov["source"] = "aon" if not ded else "aon+foundry"
        elif ded:
            source = {"book": ded[2], "license": ded[0], "remaster": bool(ded[1])}
            prov["source"] = "foundry"
        completar_licenca(source, prov)
        requires = None
        bruto_pre = r["prereq"] if r else None
        if bruto_pre:
            est["com_prereq"] += 1
            est["prereq_por_fonte"]["aon(arquetipo)"] += 1
            res = parser.parse(bruto_pre)
            if res.pred is not None:
                requires = res.pred
                prov["requires"] = "aon"
                est["prereq_ok"] += 1
            else:
                est["prereq_falha"] += 1
                for pad in (res.falhas or ["<sem atomo>"]):
                    est["falhas_por_padrao"][pad] += 1
                    est["falhas_exemplos"].setdefault(pad, bruto_pre)
        reg = {
            "id": "wb:archetype/" + sl,
            "kind": "archetype",
            "name": nome,
            "level": r["level"] if r else None,
            "traits": r["traits"] if r else [],
            "rarity": (r["rarity"] if r else None),
            "source": source,
            "requires": requires,
            "grants": [],
            "text": ("wb:text/archetype/" + sl) if "text" in prov else None,
            "mechanized": requires is not None or not bruto_pre,
            "xref": {},
            "prov": prov,
            "feats": contagem_feats.get(sl, 0),
            "no_foundry": sl in dirs_arq,
        }
        if bruto_pre:
            reg["requires_texto"] = bruto_pre
        if r:
            reg["xref"]["aon"] = r["id"]
            if r["remaster_id"]:
                reg["remaster_de"] = r["remaster_id"]
        if r and r["level"] is not None:
            prov["level"] = "aon"
        if conflitos:
            reg["conflitos"] = conflitos
        registros.append(reg)
        est["arquetipos_emitidos"] += 1

    ESTATISTICAS.clear()
    ESTATISTICAS.update(est)
    return registros


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    registros = extrair()
    saida = os.path.join(PIPELINE, "saida", "feats.json")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", encoding="utf-8") as fh:
        json.dump(registros, fh, ensure_ascii=False, indent=1)

    est = ESTATISTICAS
    ser = {}
    for k, v in est.items():
        ser[k] = dict(v) if isinstance(v, Counter) else v
    with open(os.path.join(PIPELINE, "saida", "_feats_estatisticas.json"),
              "w", encoding="utf-8") as fh:
        json.dump(ser, fh, ensure_ascii=False, indent=1)

    tot = est["com_prereq"]
    ok = est["prereq_ok"]
    print("registros ............ %d (feats %d + arquetipos %d)" % (
        est["registros"] + est["arquetipos_emitidos"], est["registros"],
        est["arquetipos_emitidos"]))
    print("com pre-requisito .... %d" % tot)
    print("predicado parseado ... %d (%.1f%%)" % (ok, 100.0 * ok / tot if tot else 0))
    print("predicado falhou ..... %d" % est["prereq_falha"])
    print("mechanized true/false  %d / %d" % (est["mechanized_true"],
                                              est["mechanized_false"]))
    print()
    print("top 15 padroes nao cobertos:")
    for pad, n in est["falhas_por_padrao"].most_common(15):
        print("  %4d  %s" % (n, pad[:88]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
