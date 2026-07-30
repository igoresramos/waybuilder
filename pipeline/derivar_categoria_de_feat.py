#!/usr/bin/env python3
"""
Preenche `feat_category` a partir dos traits, para o que sobrou vazio.

`extratores/feats.py` ja deriva a categoria e fechou 378 registros em 29/07.
Sobravam 164, por dois motivos diferentes:

  - **a regra la nao olha o trait de CLASSE nem o de ancestria.** Ela pergunta
    ao campo `class`/`ancestry` do doc do AoN, e feat que nao casou com o AoN
    nao tem esse campo -- mas tem o trait. Sao 94 com trait de classe, 51 com
    trait de ancestria e 11 com trait de heranca (`nephilim`, `naari`: heranca
    versatil, e feat de linhagem e feat de ancestria).
  - **os registros criados DEPOIS do extrator nao passam por ela.** Os 8
    restantes nasceram em `desmembrar_colisoes.py`, com o sufixo do
    desmembramento (`know-it-all-archetype`, `rallying-charge-visual`). O
    gemeo deles tem categoria e eles nao -- a mesma prosa, a mesma regra, e um
    caiu fora so por ordem de execucao.

Por isso este passo roda TARDE e sobre a base inteira, em vez de virar mais uma
condicao dentro do extrator: assim ele alcanca todo registro que exista ao
final, venha de onde vier.

NAO SOBRESCREVE categoria que ja existe -- so preenche vazio.

Spec: specs/2026-07-30-categoria-de-feat-por-trait.md
Entrada/Saida: pipeline/base/index.json + base/relatorio_categoria_de_feat.md
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"


def nomes(base, kind) -> set:
    return {str(r.get("name") or "").strip().lower()
            for r in base if r.get("kind") == kind} - {""}


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    classes = nomes(base, "class")
    ancestrias = nomes(base, "ancestry")
    herancas = nomes(base, "heritage")

    postos = collections.Counter()
    sem_resposta = []
    exemplos = []
    for reg in base:
        if reg.get("kind") != "feat" or reg.get("feat_category"):
            continue
        traits = {str(t).lower() for t in (reg.get("traits") or [])}
        # ordem importa: `archetype` ganha de trait de classe porque um feat de
        # arquetipo de multiclasse carrega os dois, e ele e feat de classe pela
        # rota do arquetipo -- o mesmo desempate que o extrator ja usa.
        if "mythic" in traits:
            cat, de = "mythic", "trait"
        elif "skill" in traits:
            cat, de = "skill", "trait"
        elif "general" in traits:
            cat, de = "general", "trait"
        elif "archetype" in traits:
            cat, de = "class", "trait"
        elif traits & classes:
            cat, de = "class", "trait-de-classe"
        elif traits & ancestrias:
            cat, de = "ancestry", "trait-de-ancestria"
        elif traits & herancas:
            # heranca versatil (`nephilim`, `naari`): feat de linhagem e feat
            # de ancestria pelas regras, e e no slot de ancestria que ele cabe.
            cat, de = "ancestry", "trait-de-heranca"
        else:
            sem_resposta.append(reg["id"])
            continue
        reg["feat_category"] = cat
        reg.setdefault("prov", {})["feat_category"] = f"derivado:{de}"
        postos[f"{cat} ({de})"] += 1
        if len(exemplos) < 20:
            exemplos.append((reg["id"], cat, de, sorted(traits)[:4]))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = ["# Categoria de feat derivada do trait", "",
           f"- preenchidos: **{sum(postos.values())}**",
           f"- ainda sem resposta: **{len(sem_resposta)}**", "",
           "| categoria (de onde) | registros |", "|---|---:|"]
    for k, v in postos.most_common():
        rel.append(f"| {k} | {v} |")
    rel += ["", "## Amostra", "", "| id | categoria | de | traits |", "|---|---|---|---|"]
    for i, c, d, t in exemplos:
        rel.append(f"| `{i}` | {c} | {d} | {', '.join(t)} |")
    if sem_resposta:
        rel += ["", "## Sem trait que responda", ""]
        rel += [f"- `{i}`" for i in sorted(sem_resposta)[:40]]
    with open(f"{BASE}/relatorio_categoria_de_feat.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"categoria de feat: {sum(postos.values())} preenchidos, "
          f"{len(sem_resposta)} sem resposta")
    print(f"-> {BASE}/relatorio_categoria_de_feat.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
