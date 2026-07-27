#!/usr/bin/env python3
"""
Converte o subconjunto DECLARATIVO dos Rule Elements do Foundry para `grants`.

## O problema que isto ataca

Medido em 2026-07-27: das **176 opcoes de sub-escolha de classe** (bloodline,
patron, mystery, instinct, racket, doctrine, muse, arcane-school...), **175 nao
tinham efeito estruturado nenhum**. Escolher a subclasse nao mudava um numero
sequer na ficha -- e subclasse e o que mais muda um personagem no PF2e.

O dado existe: 584 das 841 class-features do Foundry tem Rule Elements. O que
faltava era converter, e a spec ja avisava que este e "o item de maior custo do
projeto".

## O que e convertido, e o que deliberadamente NAO e

Rule Element se divide em duas naturezas:

**Declarativo** -- `ActiveEffectLike` com `path` de rank e sem `predicate`:
"Ruffian e treinado em Intimidation". Vira `proficiency` direto, sem perda.
Sao 95 casos.

**Dependente do interpretador** -- `FlatModifier` do Thief usa o predicado
`item:trait:finesse`; `Resistance` do Giant Instinct usa `self:effect:rage`;
`AdjustModifier` consulta `@actor.flags`. Reusar isso exigiria reimplementar o
motor de predicados do Foundry em JS -- 69 casos so entre os de rank, e a maior
parte dos 454 `ActiveEffectLike`.

Esses ficam como prosa, e **isso nao e lacuna**: pelo principio zero da spec,
`mechanized: false` e o caso normal -- o app exibe, o jogador resolve na mesa.
O que nao pode e o app fingir que calculou.

Entrada: pipeline/base/index.json + dados_brutos/foundry_repo/
Saida:   index.json reescrito + base/relatorio_rule_elements.md
"""
import json, os, re, sys, glob, collections, unicodedata


def normalizar(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"

RANK_POR_NUMERO = {0: "untrained", 1: "trained", 2: "expert",
                   3: "master", 4: "legendary"}
# `system.proficiencies.defenses.medium.rank` -> chave `medium`
PATH_RANK = re.compile(
    r"^system\.(?:skills|proficiencies|martial|attributes)\.(?:[\w-]+\.)*([\w-]+)\.rank$")


def rules_do_foundry():
    """_id do Foundry -> lista de rule elements."""
    raiz = os.environ.get("WB_FOUNDRY_PACKS", f"{BRUTOS}/foundry_repo/packs/pf2e")
    idx = {}
    for f in glob.glob(f"{raiz}/**/*.json", recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict) or not d.get("_id"):
            continue
        regras = (d.get("system") or {}).get("rules") or []
        if regras:
            idx[d["_id"]] = regras
    return idx


def converter(regras, por_nome=None):
    """Rule elements -> (grants novos, quantos ficaram de fora e por que)."""
    grants, pulados = [], collections.Counter()
    for r in regras:
        if not isinstance(r, dict):
            continue
        chave = r.get("key")

        # GrantItem sem predicado tambem e declarativo: o UUID carrega o nome
        # (`Compendium.pf2e.feats-srd.Item.Bardic Lore`), e resolver nome para
        # id `wb:` e o que a base existe para fazer.
        #
        # E onde mora metade do que a subclasse entrega: a Musa do Bardo concede
        # a composition spell (Maestro -> Lingering Composition, Enigma ->
        # Bardic Lore), a Ordem do Druida concede o focus spell (Flame Order ->
        # Fire Lung). Sem isto, escolher a musa mudava quais feats APARECIAM
        # (o predicado ja fazia isso) mas nao dava nada.
        if chave == "GrantItem" and por_nome is not None:
            if r.get("predicate"):
                pulados["GrantItem com predicate"] += 1
                continue
            uuid = str(r.get("uuid") or "")
            nome = uuid.split(".")[-1].strip()
            alvo = por_nome.get(normalizar(nome))
            if alvo is None:
                pulados["GrantItem sem alvo na base"] += 1
                continue
            campo = "grant_spell" if alvo.get("kind") == "spell" else "grant_feat"
            grants.append({campo: [alvo["id"]]})
            continue

        if chave != "ActiveEffectLike":
            pulados[f"{chave}: precisa do interpretador"] += 1
            continue
        if r.get("predicate"):
            # o predicado do Foundry fala de estado de combate, tag de item e
            # flag de ator -- avaliar isso aqui seria reimplementar o VTT
            pulados["ActiveEffectLike com predicate"] += 1
            continue
        m = PATH_RANK.match(str(r.get("path") or ""))
        if not m:
            pulados["ActiveEffectLike sem path de rank"] += 1
            continue
        valor = r.get("value")
        if not isinstance(valor, int) or valor not in RANK_POR_NUMERO:
            pulados["valor de rank nao literal"] += 1
            continue
        grants.append({"proficiency": {m.group(1): RANK_POR_NUMERO[valor]}})
    return grants, pulados


def main():
    base = json.load(open(f"{BASE}/index.json"))
    rules = rules_do_foundry()
    if not rules:
        print("sem clone do Foundry -- rode buscar_fontes.sh", file=sys.stderr)
        return 1

    # nome normalizado -> registro, para resolver o UUID do GrantItem.
    # Preferencia a quem tem `grants`: o predicado aponta para a entidade que o
    # motor precisa avaliar, nao para a ficha de catalogo.
    por_nome = {}
    for r in sorted(base, key=lambda x: (0 if x.get("grants") else 1,
                                         0 if x.get("kind") in ("feat", "spell") else 1)):
        por_nome.setdefault(normalizar(r.get("name")), r)

    convertidos, novos_grants = 0, 0
    pulados_total = collections.Counter()
    exemplos = []
    por_kind = collections.Counter()

    for r in base:
        fid = str((r.get("xref") or {}).get("foundry") or "").split(".")[-1]
        regras = rules.get(fid)
        if not regras:
            continue
        grants, pulados = converter(regras, por_nome)
        pulados_total.update(pulados)
        if not grants:
            continue
        existentes = list(r.get("grants") or [])
        chaves = {json.dumps(x, sort_keys=True) for x in existentes}
        adicionar = [g for g in grants
                     if json.dumps(g, sort_keys=True) not in chaves]
        if not adicionar:
            continue
        r["grants"] = existentes + adicionar
        r["mechanized"] = True
        r.setdefault("prov", {})["grants"] = (
            (r.get("prov") or {}).get("grants", "") + "+foundry:rule-elements"
        ).lstrip("+")
        convertidos += 1
        novos_grants += len(adicionar)
        por_kind[r.get("kind")] += 1
        if len(exemplos) < 8:
            exemplos.append((r["id"], r.get("name"), adicionar))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    print(f"registros que ganharam efeito: {convertidos}  ({novos_grants} grants)")
    print(f"por kind: {dict(por_kind.most_common(6))}")
    print("\nnao convertidos (ficam como prosa, por decisao):")
    for motivo, n in pulados_total.most_common(8):
        print(f"  {n:>6}  {motivo}")

    linhas = ["# Rule Elements convertidos", "",
              "Das 176 opcoes de sub-escolha de classe, 175 nao tinham efeito",
              "estruturado -- escolher a subclasse nao mudava numero nenhum. O dado",
              "existia nos Rule Elements do Foundry.", "",
              "Convertido apenas o **declarativo**: `ActiveEffectLike` com path de",
              "rank e sem `predicate`. O resto depende do interpretador do Foundry",
              "(`item:trait:finesse`, `self:effect:rage`, `@actor.flags`) e fica como",
              "prosa -- que pelo principio zero **nao e lacuna**.", "",
              f"- registros que ganharam efeito: **{convertidos}**",
              f"- grants adicionados: **{novos_grants}**", "",
              "## Nao convertidos", ""]
    linhas += [f"- {motivo}: {n}" for motivo, n in pulados_total.most_common()]
    linhas += ["", "## Exemplos", ""]
    for wid, nome, gs in exemplos:
        linhas.append(f"- `{wid}` ({nome}): `{json.dumps(gs, ensure_ascii=False)}`")
    open(f"{BASE}/relatorio_rule_elements.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_rule_elements.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
