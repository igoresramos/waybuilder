#!/usr/bin/env python3
"""
Desmembra `weapon-expertise` por classe, a partir da prosa oficial do AoN.

`wb:class-feature/weapon-expertise` e UM registro compartilhado por 14 classes,
concedendo `simple: expert` e `unarmed: expert`. Entre as 14 ha marciais e
nao-marciais, e uma feature so nao serve as duas progressoes: o Campeao 5 saia
com `martial: trained` onde o livro diz expert -- dois pontos a menos em todo
ataque com arma marcial.

A resposta esta na PROSA, e nao na tabela de progressao: o AoN publica 53
documentos de Weapon Expertise com texto, cada um com o campo `class` e a frase
"Your proficiency ranks for simple weapons, martial weapons, and unarmed attacks
increase to expert". Nao ha HTML a raspar.

IRMAO POR CLASSE, e nao editar a compartilhada: dar marcial ao registro
compartilhado daria marcial ao Druida tambem. Mesmo desmembramento que
`desmembrar_colisoes.py` faz quando um id serve a duas entidades.

ORDEM: roda depois da fusao (7) e depois do 7d, que decide qual irmao e a opcao
viva. Antes dos portoes.

Spec: specs/2026-07-30-weapon-expertise-por-classe.md
Entrada: pipeline/base/index.json + pipeline/dados_brutos/aon*.json
Saida:   index.json enriquecido + base/relatorio_weapon_expertise.md
"""
import glob
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

COMPARTILHADA = "wb:class-feature/weapon-expertise"

# O vocabulario da frase e fechado. `alchemical bombs` e outros nomes de arma
# aparecem, mas nao sao CATEGORIA -- quem os modela e o registro proprio da
# classe (`alchemical-weapon-expertise` ja traz `weapon-base-alchemical-bomb`).
CATEGORIA_NA_PROSA = {
    "simple weapons": "simple",
    "martial weapons": "martial",
    "unarmed attacks": "unarmed",
}

# "Your proficiency ranks for X, Y, and Z increase to expert" -- e a variante no
# singular ("rank ... increases"). O que vem depois de `to` importa: so `expert`
# entra aqui, porque Weapon Mastery e Legendary sao outros degraus e outra
# medicao.
P_FRASE = re.compile(
    r"proficienc(?:y|ies)\s+ranks?\s+for\s+(.{0,200}?)\s+increases?\s+to\s+expert",
    re.I | re.S)


def slug(nome: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", nome.strip().lower()).strip("-")


def categorias_da_prosa(texto: str) -> set:
    m = P_FRASE.search(" ".join(str(texto).split()))
    if not m:
        return set()
    trecho = m.group(1).lower()
    return {chave for frase, chave in CATEGORIA_NA_PROSA.items()
            if frase in trecho}


def prosa_por_classe() -> dict:
    """classe -> categorias que a prosa manda. Uniao quando ha mais de um doc
    (legacy e remaster convivem no dump, e as vezes com redacao diferente:
    'all simple weapons' num, 'simple weapons' no outro -- mesma regra)."""
    saida = {}
    for caminho in glob.glob(f"{BRUTOS}/aon*.json") + glob.glob(f"{BRUTOS}/aon_dump/*.json"):
        try:
            with open(caminho, encoding="utf-8") as fh:
                dados = json.load(fh)
        except Exception:
            continue
        docs = dados if isinstance(dados, list) else dados.get("docs") or []
        for doc in docs:
            if not isinstance(doc, dict):
                continue
            if "weapon expertise" not in str(doc.get("name", "")).strip().lower():
                continue
            classe = doc.get("class")
            if not classe:
                continue
            cats = categorias_da_prosa(doc.get("text") or "")
            if cats:
                saida.setdefault(str(classe), set()).update(cats)
    return saida


def concedidas(reg: dict) -> set:
    """As categorias que um registro concede como `expert`."""
    saida = set()
    for g in (reg.get("grants") or []):
        if not isinstance(g, dict):
            continue
        prof = g.get("proficiency")
        if isinstance(prof, dict):
            saida |= {k for k, v in prof.items() if v == "expert"}
    return saida


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por_id = {r["id"]: r for r in base}

    quer = prosa_por_classe()
    partilhada = por_id.get(COMPARTILHADA)
    if partilhada is None:
        print(f"{COMPARTILHADA} nao esta na base -- nada a fazer")
        return 0

    criados, ja_ok, sem_prosa = [], [], []
    novos = []
    for reg in base:
        if reg.get("kind") != "class":
            continue
        entradas = [p for p in (reg.get("progressao") or [])
                    if p.get("concede") == COMPARTILHADA]
        if not entradas:
            continue
        nome = reg.get("name") or ""
        pedido = quer.get(nome)
        if not pedido:
            sem_prosa.append(nome)
            continue

        # o que a classe JA recebe, somando TODAS as suas features de weapon
        # expertise: Druida e Swashbuckler apontam para a compartilhada E para a
        # variante propria, e a uniao delas ja pode estar certa.
        tem = set()
        for p in (reg.get("progressao") or []):
            alvo = por_id.get(str(p.get("concede") or ""))
            if alvo and "weapon-expertise" in alvo["id"]:
                tem |= concedidas(alvo)
        if pedido <= tem:
            ja_ok.append((nome, sorted(pedido)))
            continue

        novo_id = f"wb:class-feature/weapon-expertise-{slug(nome)}"
        if novo_id not in por_id:
            irmao = {
                "id": novo_id,
                "kind": "class-feature",
                "name": partilhada.get("name"),
                "traits": list(partilhada.get("traits") or []),
                "rarity": partilhada.get("rarity"),
                "source": dict(partilhada.get("source") or {}),
                "grants": [{"proficiency": {c: "expert" for c in sorted(pedido)}}],
                "text": partilhada.get("text"),
                "grants_completos": True,
                "requires_parseado": True,
                "desmembrado_de": COMPARTILHADA,
                # `prov` HERDADA da compartilhada, e nao inventada: `traits`,
                # `rarity`, `source` e `text` do irmao sao copia dela e vieram
                # da mesma fonte. So `grants` muda de dono, porque so ele foi
                # derivado aqui. Sem isto o portao 1 acusa 24 campos sem prov --
                # e acusa com razao.
                "prov": {**(partilhada.get("prov") or {}),
                         "grants": "derivado:prosa-weapon-expertise"},
            }
            if partilhada.get("xref"):
                irmao["xref"] = dict(partilhada["xref"])
            novos.append(irmao)
            por_id[novo_id] = irmao
        for p in entradas:
            p["concede"] = novo_id
        criados.append((nome, sorted(pedido), sorted(tem)))

    base.extend(novos)
    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = [
        "# Weapon Expertise desmembrada por classe", "",
        f"- irmaos criados: **{len(criados)}**",
        f"- classes que ja recebiam o certo: **{len(ja_ok)}**",
        f"- classes sem prosa no AoN: **{len(sem_prosa)}**", "",
        "A compartilhada NAO e editada: dar marcial a ela daria marcial ao "
        "Druida tambem.", "",
        "## Irmaos criados", "",
        "| classe | a prosa manda | ja recebia |", "|---|---|---|",
    ]
    for nome, pedido, tem in sorted(criados):
        rel.append(f"| {nome} | {', '.join(pedido)} | {', '.join(tem) or '-'} |")
    rel += ["", "## Ja estavam certas", "", "| classe | prosa |", "|---|---|"]
    for nome, pedido in sorted(ja_ok):
        rel.append(f"| {nome} | {', '.join(pedido)} |")
    if sem_prosa:
        rel += ["", "## Sem prosa no AoN (nao mexidas)", "",
                ", ".join(sorted(sem_prosa))]
    with open(f"{BASE}/relatorio_weapon_expertise.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"weapon expertise: {len(criados)} irmaos criados, "
          f"{len(ja_ok)} ja corretas, {len(sem_prosa)} sem prosa")
    print(f"-> {BASE}/relatorio_weapon_expertise.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
