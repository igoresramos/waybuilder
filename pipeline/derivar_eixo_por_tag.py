#!/usr/bin/env python3
"""
`otherTags` entra na base, e com ela nascem os eixos do Kineticist e do Commander.

O item 99 achava que faltava um avaliador de query. Ele JA EXISTE
(`_casa_filtro`, nos dois motores, com or/and/not/nor/xor/lte). O que faltava
era o VOCABULARIO: `_atomo_de_filtro` entende `trait`, `level`, `category` e
`rarity`, e os filtros da base usam `item:tag` 54 vezes -- ignorado, e atomo
ignorado CONTA COMO SATISFEITO.

Esse default e certo para ESTREITAR slot de feat (o principio zero manda nao
esvaziar em silencio) e DESTRUTIVO para DEFINIR eixo, porque o eixo sairia com
os 19.604 registros dentro. Por isso a ordem importa: a tag entra na base, o
motor aprende o atomo, e SO ENTAO o filtro vira eixo.

Kineticist e Commander sao as duas unicas classes com ZERO bloco de subclasse,
e as duas dependem de tag:

    Kinetic Gate   filter: ["item:tag:kineticist-kinetic-gate"]
    Tactics        filter: ["item:trait:tactic",
                            {"or": ["item:tag:commander-mobility-tactic",
                                    "item:tag:commander-offensive-tactic"]}]

O bloco guarda o FILTRO, nunca a lista: congelar a lista no build
dessincroniza na primeira mudanca de fonte, e `candidatos()` ja sabe avaliar.

Spec: specs/2026-07-31-tag-e-eixo-por-query.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_eixo_por_tag.md
"""
import collections
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

# O eixo NAO e mais lista escrita a mao. Ele e derivado: toda class-feature que
# a progressao de uma classe concede e que tem `ChoiceSet` com `filter` e um
# eixo declarado pela FONTE. Sao 41 na base.
#
# A lista a mao ja tinha cobrado o preco: ela cobria `Tactics` (nivel 1) e
# deixava de fora `Expert`, `Master` e `Legendary Tactician`, que sao os outros
# tres momentos em que o Commander escolhe tatica -- e por isso 23 das 37
# taticas seguiam inalcancaveis depois do passo que deveria alcanca-las.
#
# A GUARDA que impede duplicata: o eixo so nasce se as opcoes do filtro estiverem
# hoje INALCANCAVEIS. O eidolon do Summoner tem `ChoiceSet` com filtro e ja entra
# pelo slot de ator; criar eixo para ele duplicaria a escolha na tela.
JA_ALCANCAVEL_POR_KIND = {
    "animal-companion", "familiar-specific", "eidolon", "skill", "class",
    "equipment", "weapon", "armor", "shield", "feat", "spell", "ritual",
    "ancestry", "heritage", "background", "archetype", "deity", "domain",
}


def foundry():
    sys.path.insert(0, AQUI)
    import comum
    raiz = comum.packs_foundry(BRUTOS)
    idx = {}
    for f in glob.glob(f"{raiz}/**/*.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and d.get("_id"):
            idx[d["_id"]] = d
    return idx


def id_foundry(reg) -> str:
    return str((reg.get("xref") or {}).get("foundry") or "").rsplit(".", 1)[-1]


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    fnd = foundry()
    if not fnd:
        print("!! sem repo do Foundry -- passo pulado", file=sys.stderr)
        return 0

    # -- 1) `tags` na base ---------------------------------------------------
    com_tag, por_kind = 0, collections.Counter()
    for reg in base:
        d = fnd.get(id_foundry(reg))
        if not d:
            continue
        ot = ((d.get("system") or {}).get("traits") or {}).get("otherTags") or []
        ot = [str(t) for t in ot if isinstance(t, str)]
        if not ot:
            continue
        reg["tags"] = sorted(set(ot))
        reg.setdefault("prov", {})["tags"] = "foundry"
        com_tag += 1
        por_kind[reg.get("kind")] += 1

    # -- 2) os eixos ---------------------------------------------------------
    # o filtro sai do PROPRIO ChoiceSet do Foundry, verbatim -- nunca a mao
    por_nome = collections.defaultdict(list)
    for d in fnd.values():
        n = str(d.get("name") or "")
        if n:
            por_nome[n].append(d)

    # a feature de progressao que tem `ChoiceSet` com `filter` E um eixo, dito
    # pela fonte. Nao ha lista: sao 41 na base.
    concede_em = collections.defaultdict(list)
    for reg in base:
        if reg.get("kind") != "class":
            continue
        for e in (reg.get("progressao") or []):
            concede_em[e.get("concede")].append((reg, e.get("nivel")))

    # o que JA e alcancavel hoje, para a guarda anti-duplicata
    alcancavel = {r["id"] for r in base
                  if r.get("kind") in JA_ALCANCAVEL_POR_KIND}
    for reg in base:
        for bloco in (reg.get("subclasses") or []):
            alcancavel |= set(bloco.get("opcoes") or [])

    def casa(reg, filtro) -> bool:
        """Avaliacao minima do filtro, so o que o eixo precisa: `and` implicito
        na lista, `or`, e os atomos `item:trait` e `item:tag`. O motor avalia a
        gramatica inteira; aqui basta saber SE o eixo tem opcao inalcancavel."""
        if isinstance(filtro, str):
            partes = filtro.split(":")
            if len(partes) < 3 or partes[0] != "item":
                return False
            campo = {"trait": "traits", "tag": "tags"}.get(partes[1])
            return bool(campo) and ":".join(partes[2:]) in (reg.get(campo) or [])
        if isinstance(filtro, list):
            return all(casa(reg, f) for f in filtro)
        if isinstance(filtro, dict):
            for op, itens in filtro.items():
                if op == "or":
                    return any(casa(reg, i) for i in itens)
                if op == "and":
                    return all(casa(reg, i) for i in itens)
                if op == "not":
                    return not casa(reg, itens)
            return False
        return False

    tocadas, relatorio, pulados = [], [], []
    for feature_id, donas in sorted(concede_em.items()):
        alvo = next((r for r in base if r["id"] == feature_id), None)
        if alvo is None:
            continue
        d = fnd.get(id_foundry(alvo))
        if not d:
            continue
        filtros = [r["choices"]["filter"]
                   for r in ((d.get("system") or {}).get("rules") or [])
                   if isinstance(r, dict) and r.get("key") == "ChoiceSet"
                   and isinstance(r.get("choices"), dict)
                   and r["choices"].get("filter")]
        if not filtros:
            continue
        # todas as `flag` do mesmo registro compartilham o filtro; o numero
        # delas e quantas o eixo pede (o Commander escolhe 5 taticas no nv 1)
        filtro = filtros[0]
        eixo = feature_id.rsplit("/", 1)[-1]
        for classe, nivel in donas:
            blocos = classe.setdefault("subclasses", [])
            if any(b.get("eixo") == eixo for b in blocos):
                continue
            # ja existe eixo de verdade neste nivel? entao o dado veio por
            # outro caminho e criar outro duplicaria a escolha na tela
            if any(b.get("nivel") == nivel and b.get("eixo") != "outras-opcoes"
                   for b in blocos):
                pulados.append((classe["id"], eixo, "ja ha eixo no nivel"))
                continue
            casam = [r["id"] for r in base if casa(r, filtro)]
            novos = [i for i in casam if i not in alcancavel]
            # A GUARDA: sem opcao inalcancavel, o eixo nao acrescenta -- so
            # duplica. E o caso do eidolon do Summoner, que ja entra pelo slot
            # de ator.
            if not novos:
                pulados.append((classe["id"], eixo, "nada inalcancavel"))
                continue
            blocos.append({
                "eixo": eixo, "nivel": nivel, "slot": "subclasse",
                "escolhe": len(filtros),
                # sem `opcoes`: o bloco guarda o FILTRO e o motor resolve por
                # personagem. Congelar aqui dessincroniza na mudanca de fonte.
                "opcoes": [], "com_mecanica": [], "so_catalogo": [],
                "filtro": filtro,
            })
            tocadas.append(f"{classe['id']} / {eixo}")
            relatorio.append((classe["id"], eixo, nivel, len(filtros),
                              len(casam), len(novos)))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Tags e eixos por query", "",
           f"- registros que ganharam `tags`: **{com_tag}** (eram **0**)",
           f"- por kind: {dict(por_kind.most_common(6))}", "",
           "`item:tag` era usado 54 vezes nos filtros da base e o motor o "
           "IGNORAVA -- e atomo ignorado conta como SATISFEITO. Isso e certo "
           "para estreitar slot de feat e destrutivo para definir eixo, que e "
           "por isso que a tag entra antes do eixo.", "",
           f"- eixos criados: **{len(tocadas)}**",
           f"- pulados pela guarda anti-duplicata: **{len(pulados)}**", "",
           "O eixo NAO e lista a mao: sai de toda class-feature de PROGRESSAO "
           "com `ChoiceSet` de `filter`. A guarda so deixa nascer o eixo cujo "
           "filtro alcanca registro hoje INALCANCAVEL -- sem ela, o eidolon do "
           "Summoner ganharia um eixo duplicando o slot de ator.", "",
           "| classe | eixo | nivel | escolhe | casam | inalcancaveis |",
           "|---|---|---:|---:|---:|---:|"]
    for cid, eixo, nivel, quantos, casam, novos in relatorio:
        rel.append(f"| `{cid}` | `{eixo}` | {nivel} | {quantos} | {casam} | {novos} |")
    rel += ["", "### Pulados", "", "| classe | eixo | motivo |", "|---|---|---|"]
    for cid, eixo, motivo in pulados:
        rel.append(f"| `{cid}` | `{eixo}` | {motivo} |")
    rel += ["", "O bloco guarda o FILTRO, nunca a lista: `candidatos()` avalia "
            "com `_casa_filtro`, que ja existia e ja rodava."]
    with open(f"{BASE}/relatorio_eixo_por_tag.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"eixo por tag: {com_tag} registros com `tags`, "
          f"{len(tocadas)} eixo(s) criado(s)")
    print(f"-> {BASE}/relatorio_eixo_por_tag.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
