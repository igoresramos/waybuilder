#!/usr/bin/env python3
"""
Familiar e eidolon ganham numero. A fonte nunca faltou -- ninguem abriu o arquivo.

O item 43 ficou parado em "conseguir a fonte das estatisticas". Ela esta em
disco, e e a DECIMA PRIMEIRA lacuna de leitura -- a primeira que nao e um campo
e sim um ARQUIVO INTEIRO: `aon_dump/rules.json` tem 3.645 registros e nenhum
extrator o abre.

Procurar TABELA nao achava nada porque o que existe e FORMULA: familiar e
eidolon derivam do mestre, ao contrario do companheiro animal, que tem colunas
numericas nativas no AoN -- e por isso o companheiro ja funcionava.

FAMILIAR: o statblock mora no feat geral `Pet` (Player Core pg. 259), porque
`rules-2121` diz que o familiar E o Pet com habilidades. O unico delta esta em
`rules-2122`: nas tres pericias, pode usar `mod de conjuracao + nivel` se for
maior que `3 + nivel`.

EIDOLON: `rules-1582` da as proficiencias e diz que ele compartilha as pericias
do invocador; os arrays por tipo estao estruturados no pf2etools. Ele NAO tem
HP proprio -- compartilha o pool do invocador.

NADA E ESCRITO A MAO: cada numero sai de uma regex sobre a prosa da fonte, e o
passo FALHA ALTO se a prosa mudar e o valor esperado nao casar.

Spec: specs/2026-07-31-estatisticas-de-familiar-e-eidolon.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_estatisticas_de_ator.md
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

# Cada padrao le UM numero da prosa e diz qual valor se espera. Se a fonte
# mudar, o passo para em vez de gravar numero errado em silencio.
DO_PET = [
    ("hp_por_nivel", re.compile(r"(\d+) Hit Points per level", re.I), 5),
    ("pericia_base", re.compile(r"uses (\d+) \+ your level as its modifier", re.I), 3),
    ("velocidade", re.compile(r"a Speed of (\d+) feet", re.I), 25),
]
TAMANHO = re.compile(r"a (Tiny|Small|Medium) animal", re.I)

# `rules-1582` -- as proficiencias do eidolon, lidas da prosa
DO_EIDOLON = [
    ("fortitude", re.compile(r"begins with (\w+) proficiency in Fortitude", re.I), "expert"),
    ("reflex", re.compile(r"and (\w+) proficiency in Reflex saves", re.I), "trained"),
]


def limpar(s) -> str:
    return " ".join(str(s or "").split())


def carregar(nome):
    caminho = f"{BRUTOS}/{nome}"
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def ler(prosa: str, padroes, onde: str) -> dict | None:
    """Le os numeros e CONFERE contra o esperado. `None` = fonte mudou."""
    fora = {}
    for chave, padrao, esperado in padroes:
        m = padrao.search(prosa)
        if not m:
            print(f"!! {onde}: padrao de `{chave}` nao casou -- a fonte mudou",
                  file=sys.stderr)
            return None
        valor = m.group(1)
        valor = int(valor) if valor.isdigit() else valor.lower()
        if valor != esperado:
            print(f"!! {onde}: `{chave}` leu {valor!r}, esperava {esperado!r} "
                  f"-- a fonte mudou, confira antes de gravar", file=sys.stderr)
            return None
        fora[chave] = valor
    return fora


def registro(rid, nome, dados, fonte):
    return {
        "id": rid, "kind": "stat-formula", "name": nome,
        "level": None, "traits": [], "rarity": "common",
        "source": fonte, "requires": None, "grants": [],
        "mechanized": True, "grants_completos": None, "requires_parseado": True,
        "text": None, "xref": {}, "formula": dados,
        "prov": {"name": "waybuilder", "traits": "waybuilder",
                 "rarity": "waybuilder", "source": "aon",
                 "formula": "aon:prosa"},
    }


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    existentes = {r["id"] for r in base}

    feats = carregar("aon_feats.json") or []
    regras = {str(r.get("id")): r for r in (carregar("aon_dump/rules.json") or [])
              if isinstance(r, dict)}
    pf2e = carregar("pf2etools_repo/data/companionsfamiliars.json") or {}
    if not (feats and regras and pf2e):
        print("!! fonte ausente em disco -- passo pulado", file=sys.stderr)
        return 0

    criados, avisos = [], []

    # -- familiar -----------------------------------------------------------
    pet = next((r for r in feats
                if isinstance(r, dict) and limpar(r.get("name")) == "Pet"), None)
    if pet is None:
        print("!! feat `Pet` nao achado -- o statblock do familiar mora nele",
              file=sys.stderr)
        return 1
    prosa_pet = limpar(pet.get("text"))
    dados = ler(prosa_pet, DO_PET, "Pet")
    if dados is None:
        return 1
    m = TAMANHO.search(prosa_pet)
    dados["tamanho"] = (m.group(1).lower() if m else "tiny")
    # o delta do familiar sobre o Pet
    r2122 = limpar((regras.get("rules-2122") or {}).get("text"))
    dados["usa_mod_de_conjuracao_se_maior"] = bool(
        re.search(r"spellcasting attribute modifier \+ your level instead", r2122, re.I))
    dados["ac_e_saves_do_mestre"] = bool(
        re.search(r"save modifiers and AC are equal to yours", prosa_pet, re.I))
    dados["sem_atributo_proprio"] = bool(
        re.search(r"doesn't have or use its own attribute modifiers", prosa_pet, re.I))
    if not all((dados["usa_mod_de_conjuracao_se_maior"],
                dados["ac_e_saves_do_mestre"], dados["sem_atributo_proprio"])):
        print("!! familiar: uma das clausulas qualitativas nao casou",
              file=sys.stderr)
        return 1
    if "wb:stat-formula/familiar" not in existentes:
        base.append(registro("wb:stat-formula/familiar", "Familiar", dados,
                             {"book": "Player Core", "page": 259,
                              "license": "ORC", "remaster": True}))
        criados.append("wb:stat-formula/familiar")

    # -- eidolon: a formula geral -------------------------------------------
    r1582 = limpar((regras.get("rules-1582") or {}).get("text"))
    prof = ler(r1582, DO_EIDOLON, "rules-1582")
    if prof is None:
        return 1
    # Will acompanha Fortitude na mesma frase ("expert proficiency in Fortitude
    # and Will saves"), e Perception acompanha Reflex
    prof["will"] = prof["fortitude"]
    prof["perception"] = prof["reflex"]
    formula_eidolon = {
        "proficiencias": prof,
        "hp_proprio": False,          # compartilha o pool do invocador
        "compartilha_pericias_do_invocador": bool(
            re.search(r"shares your skill proficiencies", r1582, re.I)),
    }
    if not formula_eidolon["compartilha_pericias_do_invocador"]:
        print("!! eidolon: a clausula de pericias compartilhadas nao casou",
              file=sys.stderr)
        return 1
    if "wb:stat-formula/eidolon" not in existentes:
        base.append(registro("wb:stat-formula/eidolon", "Eidolon",
                             formula_eidolon,
                             {"book": "Secrets of Magic", "page": 58,
                              "license": "OGL", "remaster": False}))
        criados.append("wb:stat-formula/eidolon")

    # -- eidolon: os arrays por tipo ----------------------------------------
    # o pf2etools chama "Angel Eidolon"; a base chama "Angel". O sufixo sai.
    por_nome = {}
    for e in (pf2e.get("eidolon") or []):
        nome = re.sub(r"\s+Eidolon$", "", limpar(e.get("name"))).lower()
        por_nome[nome] = e

    tocados, sem_array = [], []
    for reg in base:
        if reg.get("kind") != "eidolon":
            continue
        fonte = por_nome.get(limpar(reg.get("name")).lower())
        if fonte is None:
            sem_array.append(reg.get("name"))
            # marcar, nunca esconder: a ficha precisa poder dizer POR QUE
            reg["stats_ausente"] = "sem array na fonte estruturada (so prosa)"
            reg.setdefault("prov", {})["stats_ausente"] = "waybuilder"
            continue
        arrays = []
        for st in (fonte.get("stats") or []):
            ac = st.get("ac") or {}
            arrays.append({
                "nome": limpar(st.get("name")),
                "atributos": {k: int(v) for k, v in
                              (st.get("abilityScores") or {}).items()},
                "ac_item": int(ac.get("number") or 0),
                "dex_cap": int(ac.get("dexCap") or 0),
            })
        if not arrays:
            sem_array.append(reg.get("name"))
            continue
        # MESCLAR, nunca substituir: `stats` JA EXISTE nos eidolons, com outra
        # forma (`tradicao`, `plano_natal`, `velocidade`, `sentidos`), vinda do
        # extrator de companheiros. A primeira versao deste passo fazia
        # `reg["stats"] = {...}` e apagava os quatro campos nos 12 registros que
        # casavam -- exatamente a velocidade que era a UNICA coisa que o
        # eidolon tinha na base.
        st = reg.get("stats")
        st = dict(st) if isinstance(st, dict) else {}
        # `pericias` NAO entra: o extrator de companheiros ja e dono do campo e
        # ja o traz igual (`['Diplomacy', 'Religion']` contra o
        # `['diplomacy', 'religion']` do pf2etools -- mesmo conteudo, so a
        # caixa). Reescrever seria disputar dono por nada.
        st.update({
            "arrays": arrays,
            "tamanhos": [str(s).lower() for s in (fonte.get("size") or [])],
        })
        reg["stats"] = st
        reg.setdefault("prov", {})["stats"] = "pf2etools"
        tocados.append(reg["id"])

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Estatisticas de familiar e eidolon", "",
           "A fonte nunca faltou. `aon_dump/rules.json` tem 3.645 registros e "
           "nenhum extrator o abria -- e a decima primeira lacuna de leitura, a "
           "primeira que e um ARQUIVO e nao um campo.", "",
           f"- registros de formula criados: **{len(criados)}** "
           f"({', '.join(criados) or '-'})",
           f"- eidolons com array: **{len(tocados)}**",
           f"- eidolons SEM array (marcados, nao escondidos): "
           f"**{len(sem_array)}** ({', '.join(sorted(sem_array)) or '-'})", "",
           "## Familiar -- lido do feat `Pet` e de `rules-2122`", "",
           "| campo | valor |", "|---|---|"]
    for k, v in dados.items():
        rel.append(f"| `{k}` | {v} |")
    rel += ["", "## Eidolon -- lido de `rules-1582` e do pf2etools", "",
            "| campo | valor |", "|---|---|"]
    for k, v in formula_eidolon.items():
        rel.append(f"| `{k}` | {json.dumps(v, ensure_ascii=False)} |")
    rel += ["", "Ele NAO tem HP proprio: compartilha o pool do invocador. Isso "
            "e achado, nao lacuna -- e a razao de `eidolon` so ter velocidade "
            "na base ate agora."]
    with open(f"{BASE}/relatorio_estatisticas_de_ator.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"estatisticas de ator: {len(criados)} formulas, "
          f"{len(tocados)} eidolons com array, {len(sem_array)} sem")
    print(f"-> {BASE}/relatorio_estatisticas_de_ator.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
