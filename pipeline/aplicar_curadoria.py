#!/usr/bin/env python3
"""
Aplica as correcoes CURADAS -- as que exigiram leitura da prosa oficial porque
as tres fontes estruturadas estao vazias ou erradas no ponto.

A guarda que faz isto ser seguro: cada entrada declara o `valor_atual` que
espera encontrar. Se a base ja tiver outra coisa, a correcao NAO e aplicada e o
passo falha alto. E o que impede o pior caso deste tipo de arquivo -- a fonte
conserta o dado la na frente, e a curadoria continua sobrescrevendo com o valor
antigo pelo resto da vida do projeto, em silencio.

Entrada: pipeline/base/index.json + dados_derivados/correcoes_curadas.json
Saida:   index.json reescrito
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
CURADORIA = f"{AQUI}/dados_derivados/correcoes_curadas.json"


def main() -> int:
    if not os.path.exists(CURADORIA):
        print("sem arquivo de curadoria -- nada a fazer")
        return 0

    with open(CURADORIA, encoding="utf-8") as fh:
        correcoes = json.load(fh).get("correcoes") or []
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)
    por_id = {r["id"]: r for r in base}

    aplicadas, recusadas = 0, []
    for c in correcoes:
        reg = por_id.get(c["id"])
        if reg is None:
            recusadas.append(f"{c['id']}: id ausente da base")
            continue
        atual = reg.get(c["campo"])
        if atual != c["valor_atual"]:
            recusadas.append(
                f"{c['id']}.{c['campo']}: a base tem {atual!r}, a curadoria "
                f"esperava {c['valor_atual']!r} -- a fonte pode ter consertado; "
                f"revise a entrada antes de seguir")
            continue
        reg[c["campo"]] = c["valor"]
        reg.setdefault("prov", {})[c["campo"]] = "curadoria:prosa-oficial"
        aplicadas += 1
        print(f"  {c['id']}.{c['campo']} = {json.dumps(c['valor'], ensure_ascii=False)}")

    if recusadas:
        print("\ncorrecoes RECUSADAS:")
        for r in recusadas:
            print(f"  - {r}")

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"\ncorrecoes curadas aplicadas: {aplicadas} de {len(correcoes)}")
    return 1 if recusadas else 0


if __name__ == "__main__":
    sys.exit(main())
