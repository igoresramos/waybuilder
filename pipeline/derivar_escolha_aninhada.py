#!/usr/bin/env python3
"""
O balaio do Inventor era escolha ANINHADA, nao lista solta.

O Inventor e a unica classe sem eixo nenhum: tres blocos `outras-opcoes` (22,
15 e 15 opcoes). Lido o conteudo, o nivel 1 mistura DUAS naturezas -- 4
INOVACOES (a escolha de identidade) e 18 MODIFICACOES da inovacao. Os niveis 7
e 15 sao tiers de modificacao.

O Foundry declara isso em `ChoiceSet` de lista literal, e cada dono diz quais
sao as suas:

    Weapon Innovation        initialModification        11
    Armor Innovation         armorInnovation             2
    Breakthrough Innovation  breakthroughModification   32
    Revolutionary Innovation revolutionaryModification  46
    School of Thassilonian Rune Magic  sin               7   (Mago)
    School of Rooted Wisdom            branch            5   (Mago)

DESENHO: nao ha bloco condicional. A OPCAO carrega o proprio `requires` e
`candidatos()` ja o avalia -- mesmo desenho da santificacao, ja provado.
Filtrar e MARCAR: um Inventor de armadura ve as modificacoes de arma na lista,
com o motivo escrito.

RESOLUCAO POR NOME, e so porque e inequivoca: 395 referencias distintas no
Foundry, 362 resolvem na base e ZERO sao ambiguas.

O RUIDO FICA DE FORA: 7 das 66 opcoes "explicadas" tem como dono um registro
`Effect:` do VTT (Instinct Crown, Bracers of Devotion). Efeito nao e escolha de
construcao, e mover a opcao por causa dele seria confundir os dois.

Spec: specs/2026-07-31-escolha-aninhada-do-inventor.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_escolha_aninhada.md
"""
import collections
import glob
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

REF = re.compile(r"Compendium\.[^.]+\.[^.]+\.Item\.(.+)$")

# dono -> (eixo, nivel). O dono e o nome no Foundry; o eixo e nosso.
# `Manifold Modifications` fica FORA: e feat de nivel 8, nao progressao de
# classe -- entra pela familia de slot concedido por feat, que e outra.
DONOS = {
    "Weapon Innovation":                 ("initial-modification", 1),
    "Armor Innovation":                  ("initial-modification", 1),
    "Construct Innovation":              ("initial-modification", 1),
    "Light Mortar Innovation":           ("initial-modification", 1),
    "Breakthrough Innovation":           ("breakthrough-modification", 7),
    "Revolutionary Innovation":          ("revolutionary-modification", 15),
    "School of Thassilonian Rune Magic": ("thassilonian-sin", 1),
    "School of Rooted Wisdom":           ("rooted-branch", 1),
    "Dragon Instinct":                   ("dragon-instinct-type", 1),
    "Bloodline: Draconic":               ("draconic-bloodline-type", 1),
    "Bloodline: Wyrmblessed":            ("wyrmblessed-bloodline-type", 1),
}

# o eixo de identidade do Inventor, que nao existe hoje
INOVACOES = ("Weapon Innovation", "Armor Innovation", "Construct Innovation",
             "Light Mortar Innovation")

# TERCEIRA FORMA de ChoiceSet, e a que faltava para os 44 `draconic-exemplar`:
# o Foundry nao referencia o compendio, ele escreve o dragao INLINE, com
# `label: "PF2E.Dragon.<Nome>"` e `value` sendo um objeto (damageType,
# dragonType, tradition). Os 44 registros vem do AoN por outro caminho, e as
# duas fontes nunca se encontraram -- por isso os 44 estavam inalcancaveis.
#
# Os rotulos que NAO casam sao os dragoes PRE-REMASTER (Black, Blue, Brass,
# Bronze, Copper, Gold, Green, Red). A base tem so os 44 do remaster, e esta
# certa: nao casar aqui e a fonte legada falando, nao lacuna nossa.
ROTULO_DE_DRAGAO = "PF2E.Dragon."
DONOS_DE_DRAGAO = {
    "Dragon Instinct":     "dragon-instinct-type",
    "Bloodline: Draconic": "draconic-bloodline-type",
    "Bloodline: Wyrmblessed": "wyrmblessed-bloodline-type",
}


def limpar(s) -> str:
    return " ".join(str(s or "").split())


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por = {r["id"]: r for r in base}

    sys.path.insert(0, AQUI)
    import comum
    raiz = comum.packs_foundry(BRUTOS)
    if not raiz:
        print("!! sem repo do Foundry -- passo pulado", file=sys.stderr)
        return 0

    por_nome = collections.defaultdict(list)
    for r in base:
        n = limpar(r.get("name")).lower()
        if n:
            por_nome[n].append(r["id"])

    # dono -> ids das suas opcoes, lido do ChoiceSet literal
    opcoes_de = collections.defaultdict(list)
    ambiguas = []
    for f in glob.glob(f"{raiz}/**/*.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict) or limpar(d.get("name")) not in DONOS:
            continue
        for r in ((d.get("system") or {}).get("rules") or []):
            if not isinstance(r, dict) or r.get("key") != "ChoiceSet":
                continue
            escolhas = r.get("choices")
            if not isinstance(escolhas, list):
                continue
            for o in escolhas:
                v = o.get("value") if isinstance(o, dict) else o
                m = REF.match(v) if isinstance(v, str) else None
                if not m:
                    continue
                achados = por_nome.get(limpar(m.group(1)).lower()) or []
                if len(achados) > 1:
                    # resolucao por nome so vale porque e inequivoca; se um dia
                    # deixar de ser, o registro fica onde esta
                    ambiguas.append(m.group(1))
                    continue
                if achados:
                    opcoes_de[limpar(d.get("name"))].append(achados[0])

    # a terceira forma: dragao inline, casado por ROTULO
    dragoes = {limpar(r.get("name")).lower(): r["id"] for r in base
               if r.get("kind") == "draconic-exemplar"}
    fora_do_remaster = set()
    for f in glob.glob(f"{raiz}/**/*.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict) or limpar(d.get("name")) not in DONOS_DE_DRAGAO:
            continue
        for r in ((d.get("system") or {}).get("rules") or []):
            if not isinstance(r, dict) or r.get("key") != "ChoiceSet":
                continue
            for o in (r.get("choices") or []):
                rot = o.get("label") if isinstance(o, dict) else None
                if not (isinstance(rot, str) and rot.startswith(ROTULO_DE_DRAGAO)):
                    continue
                nome = rot[len(ROTULO_DE_DRAGAO):].lower()
                if nome in dragoes:
                    opcoes_de[limpar(d.get("name"))].append(dragoes[nome])
                else:
                    fora_do_remaster.add(nome)

    if not opcoes_de:
        print("!! nenhum dono com ChoiceSet literal -- a fonte mudou",
              file=sys.stderr)
        return 1

    # -- 1) `requires` nas opcoes cujo dono e ele mesmo uma SUB-ESCOLHA ------
    #
    # A regra e geral, e nao por eixo: se o dono e uma OPCAO de sub-escolha (a
    # inovacao do Inventor, a escola do Mago), as opcoes dele so cabem em quem
    # o escolheu. Se o dono vem da PROGRESSAO (`Breakthrough` e `Revolutionary
    # Innovation`, que a classe da nos niveis 7 e 15), nao ha o que gatear --
    # todo Inventor os recebe.
    #
    # Sem isto os eixos `thassilonian-sin` e `rooted-branch` apareciam para
    # TODO Mago, gerando "falta escolher" em quem nunca pegou aquela escola.
    dono_da_opcao = collections.defaultdict(set)
    slug_da_classe = {}
    gate_do_bloco = collections.defaultdict(set)
    for dono, ids in opcoes_de.items():
        alvo = (por_nome.get(dono.lower()) or [None])[0]
        if not alvo:
            continue
        # o dono pode estar no eixo pelo GEMEO: `Dragon Instinct` e
        # `wb:class-feature/dragon-instinct`, mas o eixo `instinct` do Barbaro
        # lista `wb:instinct/dragon`. Sem olhar `equivale_a`, o gate nao pegava
        # e o eixo de tipo de dragao aparecia para TODO Barbaro.
        gemeo = (por.get(alvo) or {}).get("equivale_a")
        nomes_do_dono = {alvo} | ({gemeo} if gemeo else set())
        classe_dona = next(
            (r for r in base if r.get("kind") == "class"
             and any(nomes_do_dono & set(b.get("opcoes") or [])
                     for b in (r.get("subclasses") or []))), None)
        if classe_dona is None:
            continue                      # veio da progressao: sem gate
        # o gate cita o id que o EIXO oferece, que e o que o jogador escolhe
        no_eixo = next(
            (o for b in (classe_dona.get("subclasses") or [])
             for o in (b.get("opcoes") or []) if o in nomes_do_dono), alvo)
        for i in ids:
            dono_da_opcao[i].add(no_eixo)
            slug_da_classe[no_eixo] = classe_dona["id"].split("/")[-1]
        # o termo de gate DESTA classe para ESTE eixo. A opcao pode ser
        # compartilhada (os 44 dragoes servem ao Barbaro E ao Feiticeiro), e ai
        # o `requires` dela e um `any` das duas -- mas a condicao do BLOCO do
        # Barbaro e so o ramo dele.
        gate_do_bloco[(classe_dona["id"], DONOS[dono][0])].add(no_eixo)

    gateadas = 0
    for oid, donos in dono_da_opcao.items():
        reg = por.get(oid)
        if not reg:
            continue
        termos = [{"subclass": {slug_da_classe[d]: d}} for d in sorted(donos)]
        novo = termos[0] if len(termos) == 1 else {"any": termos}
        atual = reg.get("requires")
        reg["requires"] = novo if atual in (None, {}, []) else {"all": [atual, novo]}
        reg.setdefault("prov", {})["requires"] = \
            reg.get("prov", {}).get("requires") or "derivado:choiceset-do-dono"
        gateadas += 1

    # -- 2) os eixos ---------------------------------------------------------
    # classe -> eixo -> (nivel, ids)
    novos = collections.defaultdict(dict)
    for dono, ids in opcoes_de.items():
        eixo, nivel = DONOS[dono]
        alvo = (por_nome.get(dono.lower()) or [None])[0]
        if not alvo:
            continue
        # o dono pode chegar por DOIS caminhos, e os dois contam: como opcao
        # de sub-escolha (as inovacoes, que o jogador escolhe) ou pela
        # PROGRESSAO (`Breakthrough`/`Revolutionary Innovation`, que a classe
        # da nos niveis 7 e 15). Olhar so o primeiro deixava os dois tiers
        # maiores de fora -- 78 das opcoes.
        classes = [r for r in base if r.get("kind") == "class"
                   and (any(alvo in (b.get("opcoes") or [])
                            for b in (r.get("subclasses") or []))
                        or any(e.get("concede") == alvo
                               for e in (r.get("progressao") or [])))]
        for classe in classes:
            atual = novos[classe["id"]].setdefault(eixo, [nivel, []])
            atual[1] += ids

    # o eixo de identidade do Inventor
    inv = por.get("wb:class/inventor")
    if inv:
        ids = [i for n in INOVACOES for i in (por_nome.get(n.lower()) or [])]
        if ids:
            novos["wb:class/inventor"]["innovation"] = [1, ids]

    tocadas = []
    for cid, eixos in novos.items():
        classe = por.get(cid)
        if not classe:
            continue
        blocos = classe.setdefault("subclasses", [])
        for eixo, (nivel, ids) in eixos.items():
            if any(b.get("eixo") == eixo for b in blocos):
                continue
            unicos = sorted(set(ids))
            # se TODAS as opcoes do eixo pedem o mesmo dono, a condicao e do
            # EIXO e nao de cada opcao: um Mago de Abjuracao nao tem um eixo de
            # pecado thassiloniano com tudo marcado -- ele nao tem o eixo. Sem
            # isto o motor avisava "falta escolher `thassilonian-sin`" para
            # todo Mago, que e ruido, nao pendencia.
            bloco = {
                "eixo": eixo, "nivel": nivel, "slot": "subclasse",
                "escolhe": 1, "opcoes": unicos,
                "com_mecanica": unicos, "so_catalogo": [],
            }
            # a condicao do bloco e o termo DESTA classe, e nao a interseccao
            # dos `requires` das opcoes: elas podem ser compartilhadas entre
            # classes (os 44 dragoes servem ao Barbaro e ao Feiticeiro) e ai
            # cada uma tem um `any` diferente.
            # SO com dono UNICO. `initial-modification` tem quatro donos (as
            # quatro inovacoes), e gatear o bloco num deles faria o eixo sumir
            # para quem escolheu outro -- que foi exatamente o que quebrou na
            # primeira versao. Com mais de um dono, o gate fica na OPCAO, e a
            # lista aparece inteira com o que nao cabe MARCADO.
            donos_do_eixo = gate_do_bloco.get((cid, eixo)) or set()
            if len(donos_do_eixo) == 1:
                bloco["requires"] = {
                    "subclass": {cid.split("/")[-1]: next(iter(donos_do_eixo))}}
            blocos.append(bloco)
            tocadas.append((cid, eixo, len(unicos)))

    # -- 3) o que foi explicado sai do balaio --------------------------------
    explicadas = {i for eixos in novos.values() for _, ids in eixos.values()
                  for i in ids}
    tirados = 0
    for cid in novos:
        classe = por.get(cid)
        for b in (classe.get("subclasses") or []):
            if b.get("eixo") != "outras-opcoes":
                continue
            antes = list(b.get("opcoes") or [])
            b["opcoes"] = [o for o in antes if o not in explicadas]
            b["com_mecanica"] = [o for o in (b.get("com_mecanica") or [])
                                 if o not in explicadas]
            b["so_catalogo"] = [o for o in (b.get("so_catalogo") or [])
                                if o not in explicadas]
            tirados += len(antes) - len(b["opcoes"])

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Escolha aninhada -- o balaio do Inventor", "",
           "O Inventor era a unica classe SEM eixo nenhum. O balaio do nivel 1 "
           "misturava 4 INOVACOES com 18 MODIFICACOES da inovacao, e os niveis "
           "7 e 15 eram tiers de modificacao.", "",
           f"- eixos criados: **{len(tocadas)}**",
           f"- opcoes que sairam do balaio: **{tirados}**",
           f"- opcoes de modificacao inicial com gate por inovacao: **{gateadas}**",
           f"- referencias ambiguas descartadas: **{len(ambiguas)}**", "",
           "| classe | eixo | opcoes |", "|---|---|---:|"]
    for cid, eixo, quantas in sorted(tocadas):
        rel.append(f"| `{cid}` | `{eixo}` | {quantas} |")
    rel += ["", "Filtrar e MARCAR: um Inventor de armadura ve as modificacoes "
            "de arma na lista, com o motivo escrito. Mesmo desenho da "
            "santificacao."]
    with open(f"{BASE}/relatorio_escolha_aninhada.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"escolha aninhada: {len(tocadas)} eixos, {tirados} opcoes fora do "
          f"balaio, {gateadas} com gate")
    print(f"-> {BASE}/relatorio_escolha_aninhada.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
