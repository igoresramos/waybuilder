#!/usr/bin/env python3
"""
Uma opcao por nome dentro de cada eixo de sub-escolha.

A mesma causa do Campeao entra na base DUAS VEZES, por dois caminhos que nunca
se falaram: o extrator de classes cria um registro no kind dedicado a partir da
lista que a classe publica (`wb:cause/justice`), e o AoN/Foundry publicam a
mesma coisa como caracteristica de classe (`wb:class-feature/justice`). Os dois
sobrevivem a fusao, porque a fusao compara dentro do kind e estes estao em
kinds diferentes.

Enquanto o id legado ficava orfao o app descartava a casca em silencio e o
defeito nao aparecia. Assim que `aplicar_aliases_em_requires.py` passou a rodar
DEPOIS da fusao -- que e a ordem certa -- os dois viraram opcoes vivas, e o
Campeao passou a oferecer `Justice` duas vezes na tela.

Medido: 15 pares em 3 classes (6 causas do Campeao, 8 patronos da Bruxa, a tese
`Experimental Spellshaping` do Mago).

QUEM GANHA: o registro com mais sinal, nesta ordem -- tem `grants`, tem
`traits`, tem prosa, e por ultimo o kind `class-feature`. Na pratica sempre o
irmao `class-feature`: a casca do kind dedicado nunca tem trait nem mecanica.
O criterio e por SINAL e nao por kind de proposito, para que um dia em que a
casca for a mais rica ela ganhe sozinha.

Este passo NAO deleta registro -- so reescreve a REFERENCIA dentro de
`subclasses`. Os kinds dedicados nao sao citados em nenhum outro lugar da base
(verificado: 52 citacoes, todas em `subclasses`), entao o registro perdedor
fica no acervo, buscavel, sem duplicar a tela de escolha.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_opcoes_irmas.md
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"


def chave_de_nome(nome: str) -> str:
    return " ".join((nome or "").split()).casefold()


# chaves que TODO registro tem: nao dizem nada sobre quem sabe mais de si
BOILERPLATE = {"id", "kind", "name", "level", "traits", "rarity", "source",
               "requires", "grants", "text", "xref", "prov", "mechanized",
               "grants_completos", "requires_parseado", "aliases"}


def sinal(r: dict) -> tuple:
    """Quanto o registro sabe sobre si mesmo. Maior ganha.

    O REMASTER vem primeiro desde 2026-07-31, e por um caso concreto: `Ma'at`
    existe como `wb:deity/maat` (Divine Mysteries, com divine_font,
    sanctification, domains e favored_weapon) e como `wb:deity/maat-ln` (Gods &
    Magic, praticamente vazio). O legado GANHAVA, porque o unico sinal que os
    separava era `traits`, e o unico trait dele e `ln` -- o codigo de
    ALINHAMENTO, conceito que o proprio Remaster aboliu. Um resquicio do que foi
    abolido decidia contra o registro rico.

    A contagem de campos ESTRUTURADOS entra em seguida, pelo mesmo motivo: e ela
    que mede o que o registro carrega, enquanto `traits` mede so se ele carrega
    alguma etiqueta.
    """
    estruturados = sum(1 for k, v in r.items()
                       if k not in BOILERPLATE and v not in (None, [], {}, ""))
    return (
        1 if (r.get("source") or {}).get("remaster") else 0,
        1 if (r.get("grants") or []) else 0,
        estruturados,
        1 if (r.get("traits") or []) else 0,
        1 if r.get("text") else 0,
        1 if r.get("kind") == "class-feature" else 0,
    )


def trocar(no, de_para: dict):
    if isinstance(no, str):
        return de_para.get(no, no)
    if isinstance(no, list):
        vistos, saida = set(), []
        for x in no:
            y = trocar(x, de_para)
            if isinstance(y, str):
                if y in vistos:
                    continue
                vistos.add(y)
            saida.append(y)
        return saida
    if isinstance(no, dict):
        return {k: trocar(v, de_para) for k, v in no.items()}
    return no


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    reg = {r["id"]: r for r in base}

    linhas_rel = []
    colapsados = 0
    registros_tocados = 0

    for r in base:
        eixos = r.get("subclasses")
        if not eixos:
            continue
        mudou = False
        for eixo in eixos:
            opcoes = [o for o in (eixo.get("opcoes") or []) if isinstance(o, str)]
            por_nome = {}
            for o in opcoes:
                alvo = reg.get(o)
                if alvo:
                    por_nome.setdefault(chave_de_nome(alvo.get("name")), []).append(o)

            de_para = {}
            for nome, irmaos in por_nome.items():
                if len(irmaos) < 2:
                    continue
                vencedor = max(irmaos, key=lambda i: (sinal(reg[i]), i))
                for perdedor in irmaos:
                    if perdedor != vencedor:
                        de_para[perdedor] = vencedor
                        colapsados += 1
                        linhas_rel.append(
                            f"| `{r['id']}` | {eixo.get('eixo')} | "
                            f"{reg[vencedor].get('name')} | `{perdedor}` | "
                            f"`{vencedor}` |")

            if de_para:
                novo = trocar(eixo, de_para)
                eixo.clear()
                eixo.update(novo)
                mudou = True
        if mudou:
            registros_tocados += 1

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = [
        "# Opcoes irmas colapsadas", "",
        "Mesma opcao publicada em dois kinds -- o dedicado (`cause`, `patron`, "
        "`arcane-thesis`) e `class-feature`. Fica quem tem mais sinal.", "",
        f"- referencias reescritas: **{colapsados}**",
        f"- classes afetadas: **{registros_tocados}**", "",
        "| classe | eixo | opcao | descartado | fica |", "|---|---|---|---|---|",
    ] + sorted(linhas_rel)
    with open(f"{BASE}/relatorio_opcoes_irmas.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"opcoes irmas: {colapsados} referencias colapsadas em "
          f"{registros_tocados} classes")
    print(f"-> {BASE}/relatorio_opcoes_irmas.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
