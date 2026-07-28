#!/usr/bin/env python3
"""
Reescreve, dentro de `requires`, o id que o remaster aposentou.

A fusao Legacy<->Remaster faz a coisa certa com o REGISTRO: `Attack of
Opportunity` vira `Reactive Strike`, e o nome antigo fica em `aliases`. O que
ela nao faz e voltar nos OUTROS registros para reescrever quem citava o morto.
Sobram referencias apontando para ids que nao existem mais:

    wb:feat/attack-of-opportunity   -> wb:feat/reactive-strike
    wb:feat/wild-shape              -> wb:feat/untamed-form
    wb:feat/gnoll-weapon-familiarity-> wb:feat/kholo-weapon-familiarity
    wb:feat/drow-shootist-dedication-> wb:feat/crossbow-infiltrator-dedication

Medido: 26 ids orfaos em `requires`, e **24 tem alias registrado** -- o mapa
existe, so nunca foi aplicado.

O motor disfarca parte disso em tempo de execucao (`_termo_has` resolve alias
antes de comparar), mas so no termo `has`. Qualquer outro termo, e qualquer
consumidor que nao seja o motor, ve o id morto. Consertar no dado e mais barato
e vale para todos.

Este passo NAO inventa vinculo: so troca id por id quando a propria base declara
o alias. Orfa sem alias fica como esta e vai para o relatorio.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_aliases_requires.md
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
ID = re.compile(r"wb:[a-z-]+/[a-z0-9-]+")


def mapa_de_alias(base) -> dict:
    """alias -> id canonico, do que a propria base declara.

    `historico[].id_legado` e o vinculo mais forte: a fusao escreve ali o id
    exato que ela aposentou. E o que resolve as causas do Campeao
    (`wb:cause/paladin` -> `wb:cause/justice`) e os patronos da Bruxa
    (`wb:patron/curse` -> `wb:patron/the-resentment`) sem tabela escrita a mao.
    """
    alias = {}
    for r in base:
        for a in r.get("aliases") or []:
            if isinstance(a, str):
                alias[a] = r["id"]
        for h in r.get("historico") or []:
            if isinstance(h, str):
                alias[h] = r["id"]
            elif isinstance(h, dict):
                for v in h.values():
                    if isinstance(v, str) and v.startswith("wb:"):
                        alias[v] = r["id"]
    return alias


def trocar(no, de_para: dict):
    """Percorre o predicado trocando id morto por canonico."""
    if isinstance(no, str):
        return de_para.get(no, no)
    if isinstance(no, list):
        return [trocar(x, de_para) for x in no]
    if isinstance(no, dict):
        return {k: trocar(v, de_para) for k, v in no.items()}
    return no


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    ids = {r["id"] for r in base}
    alias = mapa_de_alias(base)

    # `requires` E `subclasses[].opcoes`. A segunda foi esquecida na primeira
    # versao, e era onde doia mais: as 6 causas do Campeao e os 8 patronos da
    # Bruxa apontavam para ids aposentados, e as duas classes abriam o slot de
    # sub-escolha com ZERO opcao -- parecia conteudo faltando na base, quando o
    # conteudo estava la com o nome novo.
    def referencias(r):
        return json.dumps([r.get("requires") or {}, r.get("subclasses") or []])

    orfas = {}
    for r in base:
        for m in ID.findall(referencias(r)):
            if m not in ids:
                orfas.setdefault(m, []).append(r["id"])

    de_para = {o: alias[o] for o in orfas if o in alias and alias[o] in ids}
    sem_saida = {o: q for o, q in orfas.items() if o not in de_para}

    tocados = 0
    for r in base:
        mudou = False
        for campo in ("requires", "subclasses"):
            atual = r.get(campo)
            if not atual:
                continue
            novo = trocar(atual, de_para)
            if novo != atual:
                r[campo] = novo
                mudou = True
        if mudou:
            tocados += 1

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    linhas = [
        "# Aliases aplicados em referencias", "",
        "A fusao renomeia o registro e guarda o nome antigo em `aliases`, mas "
        "nao reescreve quem citava o id aposentado.", "",
        f"- ids orfaos encontrados: **{len(orfas)}**",
        f"- resolvidos por alias: **{len(de_para)}**",
        f"- registros com `requires` reescrito: **{tocados}**",
        f"- sem alias (intocados): **{len(sem_saida)}**", "",
        "## Trocas", "", "| morto | canonico | citado por |", "|---|---|---|",
    ]
    for morto, vivo in sorted(de_para.items()):
        linhas.append(f"| `{morto}` | `{vivo}` | {len(orfas[morto])} |")
    if sem_saida:
        linhas += ["", "## Sem alias -- ficam como estao", "",
                   "| orfa | citado por |", "|---|---|"]
        for morto, quem in sorted(sem_saida.items()):
            linhas.append(f"| `{morto}` | {len(quem)} |")

    with open(f"{BASE}/relatorio_aliases_requires.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")

    print(f"aliases em requires: {len(de_para)} ids trocados em {tocados} "
          f"registros; {len(sem_saida)} sem alias")
    print(f"-> {BASE}/relatorio_aliases_requires.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
