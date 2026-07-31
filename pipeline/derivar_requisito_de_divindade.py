#!/usr/bin/env python3
"""
`divine_skill` -- a decima lacuna de leitura -- e as 11 clausulas que ela abre.

## Metade 1: o campo

`Divine Skill` esta na prosa do AoN de praticamente toda divindade e a base tem
ZERO. Medido: 475 de 488 lidas, e as 13 restantes sao filosofias (Atheism,
Whispering Way, Prophecies of Kalistrade...) que legitimamente nao tem pericia
divina -- ausencia aqui e RESPOSTA, nao falha. Nenhuma tem mais de uma.

Mesmo formato do modal de santificacao: a prosa traz o campo, o extrator
descarta.

## Metade 2: o residuo

Sao 18 clausulas de divindade em `requires_residuo`, e 11 fecham. Quatro delas
com termo que JA EXISTIA desde a spec `divindade-na-ficha` e que ninguem tinha
aplicado ao residuo (`has_deity`, `deity_font_permitido`, `domain`).

As 7 restantes que fecham pedem tres termos novos:
`deity_favored_weapon_category`, `proficiency_favored_weapon` e
`proficiency_divine_skill`.

NAO fecham 7: seis de alinhamento (recusado -- o Remaster aboliu o conceito) e
`versatile-font`, que precisa CONCEDER a segunda fonte.

POR QUE AQUI E NAO NO PARSER: `feats.py` roda na EXTRACAO, e `divine_skill`,
`favored_weapon` e os dominios so existem na base depois. Na hora em que a
clausula e lida nao ha com o que casar.

Spec: specs/2026-07-30-pericia-divina-e-arma-favorita.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_requisito_divindade.md
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

# a prosa lista os campos em sequencia; a pericia vem entre `Divine Skill` e o
# proximo rotulo. Mesma forma do modal de santificacao.
P_PERICIA = re.compile(
    r"Divine Skill\s+(.{0,40}?)\s+"
    r"(?:Favored Weapon|Domains|Cleric Spells|Divine Font|Alignment)", re.S)

RANKS = {"trained": "trained", "expert": "expert",
         "master": "master", "legendary": "legendary"}


def limpar(s) -> str:
    return " ".join(str(s or "").split()).strip().rstrip(".")


# -- os padroes -------------------------------------------------------------
# Cada forma e uma expressao regular sobre o TEXTO da clausula, nunca uma lista
# por registro. O que nao casar continua no residuo, intacto.

def p_adorador(t, _):
    if re.fullmatch(r"worshipp?er of a specific deity", t, re.I):
        return {"has_deity": True}


def p_fonte(t, _):
    m = re.fullmatch(r"worship a deity with a divine font that grants (\w+)",
                     t, re.I)
    if m:
        return {"deity_font_permitido": m.group(1).lower()}


def p_dominio(t, indice):
    m = re.fullmatch(r"deity who grants the (.+?) domains?", t, re.I)
    if not m:
        return None
    nomes = [n.strip() for n in re.split(r",| or ", m.group(1)) if n.strip()]
    alvos = [f"wb:domain/{n.lower().replace(' ', '-')}" for n in nomes]
    alvos = [a for a in alvos if a in indice]
    if len(alvos) != len(nomes):
        return None                     # dominio que nao existe: nao inventa
    if len(alvos) == 1:
        return {"domain": alvos[0]}
    return {"any": [{"domain": a} for a in alvos]}


def p_categoria_da_arma(t, _):
    m = re.fullmatch(r"deity with an? (.+?) (?:attack )?favou?red weapon", t, re.I)
    if not m:
        return None
    cats = [c.strip().lower() for c in re.split(r",| or ", m.group(1)) if c.strip()]
    if len(cats) == 1:
        return {"deity_favored_weapon_category": cats[0]}
    return {"any": [{"deity_favored_weapon_category": c} for c in cats]}


def p_proficiencia_na_arma(t, _):
    m = re.fullmatch(r"(\w+) (?:with|in) your deity.s favou?red weapon", t, re.I)
    if m and m.group(1).lower() in RANKS:
        return {"proficiency_favored_weapon": {">=": RANKS[m.group(1).lower()]}}


def p_pericia_divina(t, _):
    # `Master in master in Religion...` -- o "Master in" duplicado vem da
    # fonte, no registro do arquetipo. Tolerado no padrao, nao consertado a mao.
    m = re.fullmatch(r"(?:\w+ in )?(\w+) in (\w+) or your deity.s divine skill",
                     t, re.I)
    if not m:
        return None
    rank, pericia = m.group(1).lower(), m.group(2).lower()
    if rank not in RANKS:
        return None
    return {"any": [{"proficiency": {pericia: {">=": RANKS[rank]}}},
                    {"proficiency_divine_skill": {">=": RANKS[rank]}}]}


def p_santificacao_da_divindade(t, _):
    m = re.fullmatch(
        r'must worship a deity that lists "(\w+)" or "(\w+)" in their sanctification',
        t, re.I)
    if m:
        return {"any": [{"deity_sanctification": m.group(1).lower()},
                        {"deity_sanctification": m.group(2).lower()}]}


def p_sem_santificacao(t, _):
    # esta e sobre o PERSONAGEM, nao sobre a divindade: e a escolha dele no
    # eixo `sanctification`, e por isso sai em `has` e nao em
    # `deity_sanctification`.
    m = re.fullmatch(
        r"you are not sanctified with the (\w+) or (\w+) trait", t, re.I)
    if m:
        return {"not": {"any": [{"has": f"wb:sanctification/{m.group(1).lower()}"},
                                {"has": f"wb:sanctification/{m.group(2).lower()}"}]}}


PADROES = [
    ("adorador de divindade", p_adorador),
    ("fonte divina permitida", p_fonte),
    ("dominio concedido", p_dominio),
    ("categoria da arma favorita", p_categoria_da_arma),
    ("proficiencia na arma favorita", p_proficiencia_na_arma),
    ("proficiencia na pericia divina", p_pericia_divina),
    ("santificacao da divindade", p_santificacao_da_divindade),
    ("personagem sem santificacao", p_sem_santificacao),
]


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    indice = {r["id"] for r in base}

    # -- metade 1: `divine_skill` ------------------------------------------
    caminho = f"{BRUTOS}/aon_dump/deity.json"
    if not os.path.exists(caminho):
        print(f"!! sem dump de divindade em {caminho}", file=sys.stderr)
        return 1
    prosa = {}
    for d in json.load(open(caminho, encoding="utf-8")):
        if isinstance(d, dict) and d.get("id"):
            prosa[str(d["id"])] = str(d.get("text") or "")

    lidas, sem_pericia = collections.Counter(), []
    for reg in base:
        if reg.get("kind") != "deity":
            continue
        m = P_PERICIA.search(prosa.get(str((reg.get("xref") or {}).get("aon")), ""))
        if not m:
            sem_pericia.append(reg.get("name"))
            continue
        pericia = limpar(m.group(1)).lower()
        # so pericia que EXISTE na base -- nada de campo inventado
        if f"wb:skill/{pericia}" not in indice:
            sem_pericia.append(reg.get("name"))
            continue
        reg["divine_skill"] = pericia
        reg.setdefault("prov", {})["divine_skill"] = "aon:prosa"
        lidas[pericia] += 1

    # -- metade 2: o residuo ------------------------------------------------
    convertidas, por_padrao = [], collections.Counter()
    for reg in base:
        residuo = reg.get("requires_residuo") or []
        if not residuo:
            continue
        sobra, novos = [], []
        for clausula in residuo:
            if not isinstance(clausula, str):
                sobra.append(clausula)
                continue
            texto = limpar(clausula)
            achou = None
            for nome, padrao in PADROES:
                achou = padrao(texto, indice)
                if achou is not None:
                    por_padrao[nome] += 1
                    convertidas.append((reg["id"], texto, nome, achou))
                    break
            if achou is None:
                sobra.append(clausula)
            else:
                novos.append(achou)
        if not novos:
            continue
        atual = reg.get("requires")
        partes = ([atual] if atual not in (None, {}, []) else []) + novos
        reg["requires"] = partes[0] if len(partes) == 1 else {"all": partes}
        reg.setdefault("prov", {})["requires"] = \
            reg.get("prov", {}).get("requires") or "derivado:clausula-de-divindade"
        if sobra:
            reg["requires_residuo"] = sobra
        else:
            reg.pop("requires_residuo", None)

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Pericia divina e clausulas de divindade", "",
           "## `divine_skill` -- a decima lacuna de leitura", "",
           f"- divindades com o campo: **{sum(lidas.values())}**  (era **0**)",
           f"- sem a frase na prosa: **{len(sem_pericia)}** "
           f"({', '.join(sorted(sem_pericia)[:8])}{'...' if len(sem_pericia) > 8 else ''})",
           "", "Sao filosofias e afins. Nao ter pericia divina e RESPOSTA, nao "
           "falha.", "", "| pericia | divindades |", "|---|---:|"]
    for k, v in lidas.most_common():
        rel.append(f"| {k} | {v} |")
    rel += ["", "## Clausulas convertidas", "",
            f"- convertidas: **{len(convertidas)}**", "",
            "| padrao | quantas |", "|---|---:|"]
    for k, v in por_padrao.most_common():
        rel.append(f"| {k} | {v} |")
    rel += ["", "| registro | clausula | vira |", "|---|---|---|"]
    for rid, texto, _, virou in sorted(convertidas):
        rel.append(f"| `{rid}` | {texto} | `{json.dumps(virou, ensure_ascii=False)}` |")
    with open(f"{BASE}/relatorio_requisito_divindade.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"requisito de divindade: divine_skill em {sum(lidas.values())} "
          f"divindades ({len(sem_pericia)} sem), "
          f"{len(convertidas)} clausulas convertidas")
    print(f"-> {BASE}/relatorio_requisito_divindade.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
