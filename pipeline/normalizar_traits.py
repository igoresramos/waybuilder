#!/usr/bin/env python3
"""
Passa `traits` de TODO registro pela uniao/normalizacao, no fim do build.

Existe por causa de dois residuos que a auditoria de 2026-07-27 mediu na base
emitida, com a mesma raiz -- ORDEM, nao regra:

  1. 113 registros ainda tinham conflito de `traits`. A reparacao
     (`traits_uniao.unir_do_conflito`) roda dentro de `reconciliar.main`, mas
     quem CRIA conflito de traits depois dela -- `auditar_conflitos.py` e
     `desmembrar_colisoes.py`, passos 3 e 4 do build -- nunca passava por ela.

  2. 13 registros carregavam nome legado de ancestria (`grippli`, `aasimar`,
     `gnoll`, `ifrit`) embora `normalizacao_traits.json` tenha os mapeamentos:
     `unir()` so era chamado quando havia conflito ENTRE FONTES, e registro de
     fonte unica nunca passava por ele.

Roda depois do ultimo escritor de `index.json` (`fundir_renomeados.py`) e antes
dos portoes, que e o unico lugar onde a garantia vale para a base inteira.

Idempotente: rodar duas vezes nao muda nada.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_normalizacao_traits.md
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import traits_uniao                                   # noqa: E402

BASE = f"{AQUI}/base"


def main():
    base = json.load(open(f"{BASE}/index.json"))

    def conflitos_de_traits(regs):
        return sum(1 for r in regs
                   for c in (r.get("conflitos") or []) if c.get("campo") == "traits")

    antes_conflitos = conflitos_de_traits(base)
    # `unir_do_conflito` devolve True so quando o VALOR mudou; o conflito pode
    # ser resolvido sem mudar nada (as fontes concordavam). Contar o retorno
    # como "reparados" mediria a coisa errada.
    mudou_valor = sum(1 for r in base if traits_uniao.unir_do_conflito(r))
    resolvidos = antes_conflitos - conflitos_de_traits(base)

    renomeados, mudados = collections.Counter(), []
    for r in base:
        atuais = r.get("traits")
        if not atuais:
            continue
        # a uniao de UMA fonte so aplica mapa legado->remaster, absorcao por
        # granularidade e ordenacao. `prov` nao muda: a fonte do campo continua
        # sendo a mesma, so o vocabulario foi normalizado.
        finais, aliases, _ = traits_uniao.unir({"_base": list(atuais)})
        if finais != sorted(atuais):
            for t in set(atuais) - set(finais):
                renomeados[t] += 1
            mudados.append((r["id"], list(atuais), finais))
            r["traits"] = finais
        if aliases:
            r["aliases_traits"] = sorted(set(r.get("aliases_traits") or []) | set(aliases))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    restantes = conflitos_de_traits(base)
    print(f"conflitos de traits resolvidos: {resolvidos} de {antes_conflitos} "
          f"({mudou_valor} mudaram o valor emitido)")
    print(f"registros com traits normalizados: {len(mudados)}")
    print(f"conflitos de traits restantes: {restantes}")

    linhas = ["# Normalizacao de `traits` no fim do build", "",
              f"- conflitos de traits resolvidos: **{resolvidos}** de {antes_conflitos} "
              f"(em {mudou_valor} deles o valor emitido mudou; nos outros as fontes "
              f"ja concordavam e so o registro de conflito sobrava)",
              f"- registros com `traits` normalizados: **{len(mudados)}**",
              f"- conflitos de traits restantes: **{restantes}**", "",
              "## Termos substituidos", ""]
    linhas += [f"- `{t}` em {n} registro(s)" for t, n in renomeados.most_common()]
    linhas += ["", "## Amostra", ""]
    linhas += [f"- `{i}`: {antes} -> {depois}" for i, antes, depois in mudados[:40]]
    open(f"{BASE}/relatorio_normalizacao_traits.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_normalizacao_traits.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
