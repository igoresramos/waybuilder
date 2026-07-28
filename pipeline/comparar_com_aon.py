#!/usr/bin/env python3
"""
Cruza a base contra o dump do AoN -- o juiz de cobertura, offline.

Por que o AoN e nao o Pathbuilder: o Pathbuilder e oraculo de COMPORTAMENTO
(o que aparece em cada slot, a mecanica curada da dedicacao), nao de dado. Para
saber se falta conteudo, ou se um nivel/raridade esta errado, quem manda e a
fonte -- e ela ja esta no disco, em `dados_brutos/aon_*.json`.

Isso torna as frentes de CATALOGO (ancestralidade, heranca, magia, arma,
equipamento, companheiro, divindade) inteiramente offline: sem browser, sem
Cloudflare, sem coleta serial, e re-executavel a qualquer momento.

Uso:  python3 comparar_com_aon.py [frente ...]
      python3 comparar_com_aon.py --listar
Saida: docs/comparacao/aon/{frente}.json + resumo no terminal
"""
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
BRUTOS = f"{AQUI}/dados_brutos"
SAIDA = f"{RAIZ}/docs/comparacao/aon"

# frente -> (arquivo do AoN, kinds nossos, tipos do AoN que contam)
FRENTES = {
    "ancestralidade": ("aon_ancestries.json", ["ancestry"], {"Ancestry"}),
    "heranca":        ("aon_heritages.json", ["heritage"], {"Heritage"}),
    # os dumps de equipamento nao qualificam o subtipo -- vem todos como `Item`,
    # ja separados por arquivo. O de magias nao traz `type` nenhum. Filtrar por
    # tipo aqui zerava as quatro frentes em silencio.
    "magia":          ("aon_spells.json", ["spell"], None),
    "arma":           ("aon_equipment_weapon.json", ["weapon"], None),
    "armadura":       ("aon_equipment_armor.json", ["armor"], None),
    "escudo":         ("aon_equipment_shield.json", ["shield"], None),
    "companheiro":    ("aon_companheiros.json", ["animal-companion"],
                       {"Animal Companion"}),
    "familiar":       ("aon_companheiros.json",
                       ["familiar-ability", "familiar-specific"],
                       {"Familiar Ability", "Specific Familiar"}),
    "divindade":      ("aon_deities.json", ["deity"], {"Deity"}),
    "background":     ("aon_backgrounds.json", ["background"], {"Background"}),
    "arquetipo":      ("aon_archetypes.json", ["archetype"], {"Archetype"}),
    "feat":           ("aon_feats.json", ["feat"], None),
    "ritual":         ("aon_rituals.json", ["ritual"], None),
}


def norm(s: str) -> str:
    """Nome comparavel: sem acento, sem pontuacao, caixa unica."""
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def campo(doc, *nomes):
    fonte = doc.get("_source", doc)
    for n in nomes:
        if fonte.get(n) not in (None, "", []):
            return fonte[n]
    return None


def carregar_aon(arquivo, tipos):
    """Indexa o dump por nome normalizado, resolvendo rename do Remaster.

    Duas armadilhas que a primeira versao caiu, e as duas produziam falso
    positivo em MASSA -- 158 magias "faltando" que na verdade estavam todas na
    base sob o nome novo:

    1. **Homonimo colide.** 647 dos 2.461 nomes de magia se repetem (reimpressao
       em Adventure Path). Um `dict[norm(nome)]` deixava o ultimo processado
       vencer em silencio e atribuia id errado na comparacao de campo.
    2. **O Remaster renomeia.** 800 dos 2.461 docs trazem `remaster_id`
       apontando para o sucessor. Comparar por nome sem seguir esse ponteiro
       acusa ausencia onde houve troca de nome (Magic Missile -> Force Barrage).

    O dump e a propria fonte do mapa: `remaster_id` e `legacy_id` ligam os dois
    lados. Aqui o doc LEGADO que tem sucessor sai do universo comparavel -- quem
    responde por ele e o sucessor.
    """
    caminho = f"{BRUTOS}/{arquivo}"
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as fh:
        bruto = json.load(fh)
    docs = bruto if isinstance(bruto, list) else (bruto.get("hits") or [])

    crus = []
    por_id = {}
    for d in docs:
        f = d.get("_source", d)
        tipo = campo(d, "type")
        if tipos and tipo not in tipos:
            continue
        nome = campo(d, "name")
        if not nome:
            continue
        item = {
            "id": f.get("id") or d.get("_id"),
            "nome": nome,
            "nivel": campo(d, "level"),
            "raridade": campo(d, "rarity"),
            "traits": campo(d, "trait", "trait_raw") or [],
            "tipo": tipo,
            "remaster_id": f.get("remaster_id") or [],
            "legacy_id": f.get("legacy_id") or [],
        }
        crus.append(item)
        if item["id"]:
            por_id[item["id"]] = item

    # doc legado cujo sucessor esta no proprio dump nao e cobranca: o sucessor
    # ja responde por ele
    aposentados = set()
    for item in crus:
        for alvo in item["remaster_id"]:
            if alvo in por_id and alvo != item["id"]:
                aposentados.add(item["id"])

    saida = {}
    for item in crus:
        if item["id"] in aposentados:
            continue
        chave = norm(item["nome"])
        # homonimo: fica o de nivel definido; empate mantem o primeiro
        anterior = saida.get(chave)
        if anterior is None or (anterior["nivel"] is None
                                and item["nivel"] is not None):
            saida[chave] = item
    return saida


def main() -> int:
    if "--listar" in sys.argv:
        for f in FRENTES:
            print(f)
        return 0

    pedidas = [a for a in sys.argv[1:] if not a.startswith("-")] or list(FRENTES)
    with open(f"{AQUI}/base/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    os.makedirs(SAIDA, exist_ok=True)
    print(f"{'frente':16} {'nossa':>7} {'aon':>7} {'faltam':>7} {'so nosso':>9} "
          f"{'nivel≠':>7} {'rar≠':>6}")
    print("-" * 66)

    for frente in pedidas:
        if frente not in FRENTES:
            print(f"!! frente desconhecida: {frente}", file=sys.stderr)
            continue
        arquivo, kinds, tipos = FRENTES[frente]
        aon = carregar_aon(arquivo, tipos)
        if aon is None:
            print(f"{frente:16} (dump ausente: {arquivo})")
            continue

        # O nosso lado responde tambem pelos NOMES ANTIGOS que carrega. Sem
        # isto, toda heranca e toda magia renomeada pelo Remaster era acusada
        # de ausente -- 12 de 12 herancas e 158 de 158 magias eram exatamente
        # este falso positivo.
        nossos, por_alias = {}, {}
        for r in base:
            if r.get("kind") not in kinds or not r.get("name"):
                continue
            nossos[norm(r["name"])] = r
            for campo_alias in ("aliases", "historico", "legado_de"):
                for a in r.get(campo_alias) or []:
                    if isinstance(a, str):
                        # tanto `wb:spell/magic-missile` quanto "Magic Missile"
                        por_alias[norm(a.split("/")[-1])] = r
                        por_alias[norm(a)] = r

        def responde(chave):
            return nossos.get(chave) or por_alias.get(chave)

        faltam = sorted(aon[k]["nome"] for k in aon if not responde(k))
        sobram = sorted(nossos[k].get("name") for k in nossos.keys() - aon.keys())

        nivel_dif, rar_dif = [], []
        for k in aon:
            n = responde(k)
            if n is None:
                continue
            a = aon[k]
            if a["nivel"] is not None and n.get("level") is not None \
                    and int(a["nivel"]) != int(n["level"]):
                nivel_dif.append({"nome": a["nome"], "aon": a["nivel"],
                                  "nosso": n["level"], "id": n["id"]})
            ra = (a["raridade"] or "common").lower()
            rn = (n.get("rarity") or "common").lower()
            if ra != rn:
                rar_dif.append({"nome": a["nome"], "aon": ra, "nosso": rn,
                                "id": n["id"]})

        rel = {
            "frente": frente, "kinds": kinds, "fonte_aon": arquivo,
            "nossos": len(nossos), "aon": len(aon),
            "faltam_em_nos": faltam, "so_nosso": sobram,
            "nivel_divergente": nivel_dif, "raridade_divergente": rar_dif,
        }
        with open(f"{SAIDA}/{frente}.json", "w", encoding="utf-8") as fh:
            json.dump(rel, fh, ensure_ascii=False, indent=1)

        print(f"{frente:16} {len(nossos):7} {len(aon):7} {len(faltam):7} "
              f"{len(sobram):9} {len(nivel_dif):7} {len(rar_dif):6}")

    print(f"\n-> {SAIDA}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
