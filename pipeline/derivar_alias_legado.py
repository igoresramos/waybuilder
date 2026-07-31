#!/usr/bin/env python3
"""
Emite o NOME antigo como alias, para o que o Remaster renomeou fora de magia.

Achado na 4a rodada de comparacao com o Pathbuilder: `Desperate Wrath` nao
carregava `Reckless Abandon` como alias, entao quem digitasse o nome antigo
achava apenas o feat GOBLIN homonimo. Em 30/07 esse buraco foi fechado para
MAGIA (159 renomeacoes); fora de magia continuava aberto.

TRES GUARDAS, cada uma achada olhando o resultado da anterior. A regra crua
("o doc legado tem outro nome, logo e alias") pega 1.606 e a maioria e lixo:

  1. categoria do legado IGUAL a do canonico -- sem isso
     `wb:class-feature/panache` ganha o alias "Swashbuckler", que e o nome da
     CLASSE e nao o nome antigo;
  2. nome legado nao pode ser nome de classe -- mesma causa;
  3. um nome nao pode ser PREFIXO do outro -- `Ablative Armor Plating (Lesser)`
     aponta para `Ablative Armor Plating`, que e o doc de grau apontando para a
     base, nao renomeacao.

Sobram 335: equipment 217, weapon 57, feat 31, heritage 12, ritual 9, armor 7,
ancestry 2. `Gnoll -> Kholo`, `Grippli -> Tripkee`, `Choker-Arm Mutagen ->
Bendy-Arm Mutagen` -- o mesmo padrao de Product Identity das renomeacoes do
Pathbuilder ja mapeadas.

Spec: specs/2026-07-30-alias-legado-fora-de-magia.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_alias_legado.md
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


def norm(s) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def docs_do_aon() -> dict:
    saida = {}
    for caminho in glob.glob(f"{BRUTOS}/aon*.json") + glob.glob(f"{BRUTOS}/aon_dump/*.json"):
        try:
            with open(caminho, encoding="utf-8") as fh:
                dados = json.load(fh)
        except Exception:
            continue
        for doc in (dados if isinstance(dados, list) else dados.get("docs") or []):
            if isinstance(doc, dict) and doc.get("id"):
                saida[doc["id"]] = doc
    return saida


# Pares que a fonte NAO liga sozinha, e por que cada um esta aqui.
#
# `legacy_id` do AoN so registra renomeacao DENTRO do AoN, e nos dois casos
# abaixo o AoN renomeou os dois lados (weapon-623 "Jiu Huan Dao" ->
# weapon-288 "Jiu Huan Dao"), entao a regra que exige nome diferente pula --
# corretamente. O nome antigo em ingles sobrevive so no pf2etools, que nao tem
# ponte de remaster nenhuma.
#
# Resultado sem isto: dois registros VAZIOS (`nine-ring-sword`,
# `wind-and-fire-wheel`, sem dano, categoria nem grupo, so com xref de
# pf2etools) ao lado dos completos vindos do Foundry. O colapso de irmaos nao
# os junta porque casa por NOME, e os nomes nao se parecem.
#
# Cada par foi conferido no dump: mesmo livro-fonte na cadeia (Gods & Magic /
# Fists of the Ruby Phoenix, OGL, `remaster: false`) apontando para o
# equivalente do Tian Xia Character Guide (ORC, `remaster: true`).
# Spec: specs/2026-07-31-par-curado-tian-xia.md
PARES_CURADOS = [
    ("wb:weapon/nine-ring-sword", "wb:weapon/jiu-huan-dao"),
    ("wb:weapon/wind-and-fire-wheel", "wb:weapon/feng-huo-lun"),
]

# GEMEO class-feature x feat de MESMO NOME. Desde 31/07 o pack do UUID do
# Foundry manda na resolucao do `GrantItem`, entao `Alchemy` concede
# `wb:class-feature/advanced-alchemy` e nao mais o feat homonimo -- o certo. Mas
# `efficient-alchemy` cita o FEAT, e sem esta ponte deixou de ser atendido: e
# exatamente a quebra que o item 100 previa ao trocar o alvo do `grants`.
#
# Os dois ids passam a resolver, como ja acontece com os gemeos de instinto.
# Sao os 4 pares em que a correcao do pack trocou o lado concedido.
# Spec: specs/2026-07-31-gemeo-do-grant-item.md
GEMEOS_DO_GRANT = [
    ("wb:class-feature/advanced-alchemy", "wb:feat/advanced-alchemy"),
    ("wb:class-feature/quick-alchemy", "wb:feat/quick-alchemy"),
    ("wb:class-feature/surprise-attack", "wb:feat/surprise-attack"),
    ("wb:class-feature/keen-recollection", "wb:feat/keen-recollection"),
]


def aplicar_curados(base: list) -> list:
    """O registro vazio vira GEMEO do completo -- nunca se apaga.

    `equivale_a` e o mesmo mecanismo dos gemeos de instinto: os dois ids
    resolvem, e quem citar o nome antigo continua achando. Apagar tornaria o
    id inalcancavel, que e a familia do item 97.
    """
    por_id = {r["id"]: r for r in base}
    feitos = []
    for a, b in GEMEOS_DO_GRANT:
        ra, rb = por_id.get(a), por_id.get(b)
        if ra is None or rb is None or ra.get("equivale_a"):
            continue
        ra["equivale_a"] = b
        ra.setdefault("prov", {})["equivale_a"] = "curado:gemeo-do-grant"
        feitos.append((a, b, "gemeo"))
    for vazio, completo in PARES_CURADOS:
        a, b = por_id.get(vazio), por_id.get(completo)
        if a is None or b is None:
            continue
        nome_antigo = str(a.get("name") or "").strip()
        aliases = b.setdefault("aliases", [])
        if nome_antigo and nome_antigo not in aliases:
            aliases.append(nome_antigo)
            b.setdefault("prov", {}).setdefault("aliases", "curado:par-tian-xia")
        if not a.get("equivale_a"):
            a["equivale_a"] = completo
            a.setdefault("prov", {})["equivale_a"] = "curado:par-tian-xia"
        # `equivale_a` sozinho NAO basta: `resolver()` segue `aliases`, nao ele,
        # entao a arma equipada pelo id antigo continuava saindo sem dano na
        # ficha. Preenche o que FALTA a partir do gemeo -- so campo ausente,
        # nunca sobrescrita, para nao apagar o que a fonte antiga trouxe de
        # proprio (`nine-ring-sword` tem `disarm` que o gemeo nao tem).
        for campo in ("damage", "weapon_category", "group", "bulk", "hands",
                      "range", "reload"):
            if a.get(campo) in (None, "", [], {}) and b.get(campo) not in (None, "", [], {}):
                a[campo] = b[campo]
                a.setdefault("prov", {})[campo] = "curado:par-tian-xia"
        feitos.append((vazio, completo, nome_antigo))
    return feitos


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    docs = docs_do_aon()

    por_aon = {}
    for r in base:
        aon = (r.get("xref") or {}).get("aon")
        if aon:
            por_aon[aon] = r
    nomes_de_classe = {str(r.get("name") or "").strip().lower()
                       for r in base if r.get("kind") == "class"}

    postos = collections.Counter()
    exemplos = []
    for doc in docs.values():
        legados = doc.get("legacy_id") or []
        if isinstance(legados, str):
            legados = [legados]
        alvo = por_aon.get(doc.get("id"))
        if alvo is None:
            continue
        novo = str(alvo.get("name") or "").strip()
        for lid in legados:
            antigo_doc = docs.get(lid)
            if not antigo_doc:
                continue
            velho = str(antigo_doc.get("name") or "").strip()
            if not velho or velho.lower() == novo.lower():
                continue
            if antigo_doc.get("category") != doc.get("category"):
                continue
            if velho.lower() in nomes_de_classe:
                continue
            if norm(novo).startswith(norm(velho)) or norm(velho).startswith(norm(novo)):
                continue
            aliases = alvo.setdefault("aliases", [])
            if velho in aliases:
                continue
            aliases.append(velho)
            alvo.setdefault("prov", {}).setdefault("aliases", "aon:legacy_id")
            postos[alvo.get("kind")] += 1
            if len(exemplos) < 20:
                exemplos.append((alvo.get("kind"), novo, velho))

    curados = aplicar_curados(base)

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Alias legado fora de magia", "",
           f"- pares CURADOS aplicados: **{len(curados)}**",
           *[f"  - `{v}` -> `{c}` (alias `{n}`)" for v, c, n in curados], "",]
    rel += [""]
    rel += ["", "# (derivados abaixo)", "",
           f"- aliases acrescentados: **{sum(postos.values())}**", "",
           "A regra crua pega 1.606 e a maioria e lixo. Tres guardas: categoria "
           "igual, nome legado nao e nome de classe, e um nome nao e prefixo do "
           "outro (isso ultimo derruba os pares de GRAU).", "",
           "| kind | aliases |", "|---|---:|"]
    for k, v in postos.most_common():
        rel.append(f"| {k} | {v} |")
    rel += ["", "## Amostra", "", "| kind | nome atual | alias |", "|---|---|---|"]
    for k, novo, velho in exemplos:
        rel.append(f"| {k} | {novo} | {velho} |")
    with open(f"{BASE}/relatorio_alias_legado.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"alias legado: {sum(postos.values())} acrescentados")
    print(f"-> {BASE}/relatorio_alias_legado.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
