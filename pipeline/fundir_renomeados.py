#!/usr/bin/env python3
"""
Fusao de conteudo renomeado entre Legacy e Remaster.

Politica de conteudo (Igor, inalterada): nome nao importa, regra e conteudo
importam. `Power Attack` e `Vicious Swing` sao a mesma coisa e viram um
registro so, com todos os nomes em `aliases`.

O QUE MUDOU NA v2 -- o criterio de decidir se sao a mesma coisa.

  A versao anterior decidia por similaridade de prosa (Jaccard >= 0,62). Medido
  contra o `remaster_id` do AoN: so 35% das 597 fusoes estavam certas. 393
  uniram registros com `level`, `price_cp` ou `damage` diferentes -- o dado ja
  dizia que eram entidades distintas. `wb:equipment/aeon-stone` engoliu 24
  pedras; `Tonfa` virou `Shuan Ji`, do mesmo livro. A causa e estrutural: itens
  de uma familia compartilham quase todo o texto e diferem numa linha de efeito.

Agora: funde SO com vinculo declarado pela fonte (`remaster_id` / `legacy_id`
do AoN). Prosa nao decide nada -- entra so como confirmacao no relatorio.
Guardas vetam a fusao mesmo com chave. E NADA e deletado: o absorvido fica na
base com `superseded_by`.

Entrada: pipeline/base/index.json (+ base/text/), pipeline/dados_brutos/aon*
Saida:   pipeline/base/index.json reescrito + relatorio_fusao.md
"""
import collections
import glob
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import comum  # noqa: E402

BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

# O Remaster comeca no Player Core (novembro/2023). Legado que sai de livro
# posterior nao pode ser nome antigo de nada -- na v1, varios "legados" vinham
# de Tian Xia CG (2024), Battlecry! (2025) e Monster Core 2.
CORTE_REMASTER = "2023-11-01"

STOP = set("a an the you your of to and or with in on for is are that this it as by from at "
           "be can if when have has gain gains use uses make makes than then not no".split())


def toks(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return {w for w in re.findall(r"[a-z]{3,}", s) if w not in STOP}


def como_lista(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def anotacoes(legado, alvo, doc_legado, n_legados_no_alvo):
    """O que muda entre legado e alvo, para o registro nao esconder.

    NAO sao vetos. Medido na ponte do AoN antes de decidir: os tres sinais que
    a auditoria propos como guarda barram 77,8% dos pares que a propria fonte
    declara, e por motivo legitimo.

      - N->1 e o caso NORMAL da consolidacao do remaster: 351 alvos recebem 2+
        legados so na mesma categoria (`Magic Wand` <- as 10 varas por rank,
        `Bewitching Bloom` <- as 10 flores). Vetar N->1 desfaz o dedupe.
      - `level`/`price_cp` divergentes sao errata de remaster:
        `Hand of the Mage` nv2 -> `Charlatan's Gloves` nv3.
      - a fronteira de data de publicacao e falsa: Rage of Elements e de
        2023-08-02 e ha legado declarado publicado em 2024.

    O que protegia contra o dano da auditoria A1 (`aeon-stone` engolindo 24
    pedras) nao era o guarda: das 24 pedras, so 5 declaram `remaster_id`. Era a
    chave -- e o fato de nada ser deletado.
    """
    notas = []
    for campo in ("level", "price_cp", "damage"):
        a, b = legado.get(campo), alvo.get(campo)
        if a is not None and b is not None and a != b:
            notas.append(f"{campo}: {a} -> {b}")
    if n_legados_no_alvo > 1:
        notas.append(f"consolidacao: o alvo recebe {n_legados_no_alvo} legados")
    data = str(doc_legado.get("release_date") or "")[:10]
    if data and data >= CORTE_REMASTER:
        notas.append(f"legado publicado em {data}, depois do corte do Remaster")
    return notas


def veto(legado, alvo, doc_legado, doc_alvo):
    """O unico veto que sobra: fundir entidades de categorias diferentes.

    Medido: 351 de 351 class-features com `remaster_id` apontam para um doc de
    categoria `class` -- `Evasion` (class-feature-25) aponta para `class-56`,
    que e o Alchemist. Sem este guarda, a feature seria absorvida pela classe.
    Renomeacao real de class-feature fica sem chave e tem de sair da progressao
    da classe no Foundry, nao daqui.
    """
    ca = (doc_legado or {}).get("category")
    cb = (doc_alvo or {}).get("category")
    if ca and cb and ca != cb:
        return f"categoria diferente: {ca} -> {cb}"
    if legado.get("kind") and alvo.get("kind") and legado["kind"] != alvo["kind"]:
        return f"kind diferente: {legado['kind']} -> {alvo['kind']}"
    return None


def main():
    base = json.load(open(f"{BASE}/index.json"))
    textos = {}
    for f in os.listdir(f"{BASE}/text"):
        textos.update(json.load(open(f"{BASE}/text/{f}")))

    ponte = comum.carregar_ponte(BRUTOS)
    por_aon = {}
    for r in base:
        aon = (r.get("xref") or {}).get("aon")
        if aon:
            por_aon.setdefault(aon, r)

    def prosa(r):
        t = textos.get(r.get("text") or "", "")
        return toks(re.sub(r"^\s*\S.{0,80}?Source .{0,60}?pg\.\s*\d+", "", t)[:900])

    # --- 1. levantar os pares que a FONTE declara -------------------------
    declarados = []          # (legado, alvo, doc_legado)
    alvo_sem_registro = []   # a fonte aponta para algo que a base nao extraiu
    for r in base:
        aon = (r.get("xref") or {}).get("aon")
        doc = ponte.get(aon) if aon else None
        if not doc:
            continue
        for alvo_id in como_lista(doc.get("remaster_id")):
            alvo = por_aon.get(alvo_id)
            if alvo is None:
                alvo_sem_registro.append((r["id"], alvo_id))
            elif alvo["id"] != r["id"]:
                declarados.append((r, alvo, doc))

    contagem_alvo = collections.Counter(alvo["id"] for _, alvo, _ in declarados)

    # --- 2. veto de categoria; o resto vira anotacao ----------------------
    fundidos, vetados = [], []
    for legado, alvo, doc in declarados:
        doc_alvo = ponte.get((alvo.get("xref") or {}).get("aon")) or \
            {"category": (doc or {}).get("category")}
        motivo = veto(legado, alvo, doc, doc_alvo)
        p_leg, p_alvo = prosa(legado), prosa(alvo)
        sim = (len(p_leg & p_alvo) / len(p_leg | p_alvo)) if (p_leg and p_alvo) else 0.0
        if motivo:
            vetados.append((legado, alvo, [motivo], sim))
        else:
            fundidos.append((legado, alvo, sim,
                             anotacoes(legado, alvo, doc, contagem_alvo[alvo["id"]])))

    # --- 3. aplicar a fusao, sem deletar ninguem --------------------------
    por_id = {r["id"]: r for r in base}
    for legado, alvo, sim, notas in fundidos:
        a = por_id[alvo["id"]]
        aliases = set(a.get("aliases") or [])
        aliases.add(legado.get("name"))
        aliases.update(legado.get("aliases") or [])
        aliases.discard(a.get("name"))
        a["aliases"] = sorted(x for x in aliases if x)
        a.setdefault("xref", {}).update(
            {f"legado_{k}": v for k, v in (legado.get("xref") or {}).items()})
        a.setdefault("historico", []).append({
            "nome_legado": legado.get("name"),
            "livro_legado": (legado.get("source") or {}).get("book"),
            "vinculo": "aon:remaster_id",
            "similaridade_prosa": round(sim, 3),
            "mudou": notas,          # errata e consolidacao ficam visiveis
        })
        a.setdefault("prov", {})["aliases"] = comum.prov_inferido("aon", "remaster_id")

        l = por_id[legado["id"]]
        # 1->N declarado existe (14 casos: `Wish` -> [`Wish`, `Manifestation`]),
        # entao o campo e lista.
        sup = list(l.get("superseded_by") or [])
        if alvo["id"] not in sup:
            sup.append(alvo["id"])
        l["superseded_by"] = sup
        l.setdefault("prov", {})["superseded_by"] = comum.prov_lido("aon")

    # vetado: o vinculo declarado fica registrado, mas os dois seguem vivos
    for legado, alvo, motivos, _ in vetados:
        l = por_id[legado["id"]]
        l["substituto_declarado"] = alvo["id"]
        l["fusao_vetada"] = motivos
        l.setdefault("prov", {})["substituto_declarado"] = comum.prov_lido("aon")

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    # --- 4. relatorio: os dois lados da metrica ---------------------------
    #
    # "zero par nao unido" e recall sem precisao -- fundir tudo com tudo tambem
    # daria zero. O relatorio reporta unidos, vetados e sem chave.
    sem_chave = [r for r in base
                 if (r.get("source") or {}).get("license") == "OGL"
                 and not r.get("superseded_by") and not r.get("substituto_declarado")]

    com_alias = sum(1 for r in base if r.get("aliases"))
    com_nota = sum(1 for *_, notas in fundidos if notas)
    linhas = [
        "# Fusao de renomeados (v2 -- chave da fonte)", "",
        "Criterio: funde so com `remaster_id`/`legacy_id` declarado pelo AoN.",
        "Prosa nao decide; aparece so como confirmacao. Nada e deletado -- o",
        "absorvido fica na base com `superseded_by`.", "",
        f"- registros na base: **{len(base)}** (nenhum deletado)",
        f"- pares declarados pela fonte: **{len(declarados)}**",
        f"- fundidos: **{len(fundidos)}** (destes, {com_nota} com mudanca anotada"
        " -- errata de level/preco ou consolidacao)",
        f"- vetados (categoria/kind diferente): **{len(vetados)}**",
        f"- alvo declarado que a base nao tem: **{len(alvo_sem_registro)}**",
        f"- registros OGL sem vinculo nenhum declarado: **{len(sem_chave)}**",
        f"- registros com alias: **{com_alias}**", "",
        "## Vetados (chave declarada, mas nao sao a mesma coisa)", "",
        "Quase todos sao `class-feature` cujo `remaster_id` aponta para a CLASSE,",
        "nao para outra feature. Renomeacao real de feature nao tem chave e sai",
        "da progressao da classe no Foundry.", "",
    ]
    for legado, alvo, motivos, sim in sorted(vetados, key=lambda x: x[0]["id"])[:120]:
        linhas.append(f"- `{legado['id']}` -> `{alvo['id']}` — {'; '.join(motivos)} "
                      f"(prosa {sim:.2f})")
    linhas += ["", "## Fundidos com mudanca anotada", ""]
    for legado, alvo, sim, notas in sorted(fundidos, key=lambda x: -len(x[3])):
        if not notas:
            continue
        linhas.append(f"- **{legado.get('name')}** -> **{alvo.get('name')}** "
                      f"_({legado.get('kind')})_: {'; '.join(notas)}")
    linhas += ["", "## Fundidos", ""]
    for legado, alvo, sim, _ in sorted(fundidos, key=lambda x: -x[2]):
        linhas.append(f"- `{sim:.2f}` **{legado.get('name')}** -> **{alvo.get('name')}** "
                      f"_({legado.get('kind')})_")
    if alvo_sem_registro:
        linhas += ["", "## Alvo declarado ausente da base (buraco de cobertura)", ""]
        for origem, alvo_id in sorted(alvo_sem_registro)[:200]:
            linhas.append(f"- `{origem}` aponta para `{alvo_id}`, que nao foi extraido")
    open(f"{BASE}/relatorio_fusao.md", "w").write("\n".join(linhas) + "\n")

    print(f"pares declarados pela fonte: {len(declarados)}")
    print(f"  fundidos: {len(fundidos)} ({com_nota} com mudanca anotada)")
    print(f"  vetados (categoria/kind diferente): {len(vetados)}")
    print(f"  alvo ausente da base: {len(alvo_sem_registro)}")
    print(f"base: {len(base)} registros (nenhum deletado), com alias: {com_alias}")
    print("-> base/relatorio_fusao.md")


if __name__ == "__main__":
    main()
