#!/usr/bin/env python3
"""
Emite o payload que o APP consome -- que nao e o mesmo artefato que o pipeline
produz.

`base/index.json` e o artefato de BUILD: carrega proveniencia por campo,
referencia cruzada para as tres fontes e o registro de conflito entre elas.
Isso existe para auditar a base e re-sincronizar so o que mudou; o construtor
nunca le nada disso. Medido no build de 2026-07-27, dos 13,9 MB de conteudo:

    prov        3,29 MB  (23,7%)   metadado de build
    xref        1,72 MB  (12,4%)   id nas tres fontes
    conflitos   0,31 MB   (2,2%)   divergencia entre fontes
    texto       1,77 MB  (12,7%)   prosa INLINE em 1.858 registros -- vazamento:
                                   a prosa vive em base/text/ e o indice ja
                                   aponta para ela pelo campo `text`

Nada disso vai para o cliente. O que sobra e o que monta ficha.

O corte e por LISTA NEGRA, nao por lista branca: campo novo que um extrator
passe a emitir entra no payload por padrao. O contrario -- lista branca --
faria o app perder dado novo em silencio, que e exatamente a classe de erro que
os portoes existem para impedir.

Entrada: pipeline/base/index.json + base/text/*.json
Saida:   base/app/index.json        indice enxuto, tudo num arquivo
         base/app/por-kind/*.json   o mesmo, fatiado (carga sob demanda)
         base/app/_manifesto.json   tamanhos e contagens
"""
import collections
import gzip
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
SAIDA = f"{BASE}/app"

# metadado de build: existe para auditar a base, nunca para montar ficha
DESCARTAR = ("prov", "xref", "conflitos", "texto", "mechanized",
             "desmembrado_de", "aliases_traits", "antes")

# Campos em que `None` E RESPOSTA, e nao vazio. `grants_completos` tem TRES
# estados por desenho (`comum.py::mecanizacao`): true = converti tudo, false =
# perdi mecanica, **null = a fonte nao declarou mecanica nenhuma**. O terceiro
# obriga quem le a tratar o caso em vez de concluir que `grants: []` representa
# o registro -- foi o que custou as 61 dedicacoes com grants vazio e
# `completos: true`. O filtro de vazio abaixo apagava justamente o null, e o app
# recebia 14.247 registros sem resposta em vez de 9.043.
TRI_ESTADO = ("grants_completos", "requires_parseado")


def compactar(r: dict) -> dict:
    saida = {k: v for k, v in r.items()
             if k not in DESCARTAR
             and (k in TRI_ESTADO or v not in (None, "", [], {}))}
    # `source` inteiro custa 1,34 MB e o app so precisa de atribuicao legivel.
    # Licenca fica: e exigencia da OGL/ORC, nao enfeite.
    s = r.get("source") or {}
    if s:
        saida["source"] = {k: v for k, v in
                           (("book", s.get("book")), ("page", s.get("page")),
                            ("license", s.get("license")))
                           if v not in (None, "")}
    return saida


def escrever(caminho: str, dado) -> int:
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    bruto = json.dumps(dado, ensure_ascii=False, separators=(",", ":"))
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(bruto)
    return len(gzip.compress(bruto.encode("utf-8")))


def main() -> int:
    base = json.load(open(f"{BASE}/index.json", encoding="utf-8"))
    enxuto = [compactar(r) for r in base]

    antes = len(gzip.compress(
        json.dumps(base, ensure_ascii=False, separators=(",", ":")).encode()))
    depois = escrever(f"{SAIDA}/index.json", enxuto)

    por_kind = collections.defaultdict(list)
    for r in enxuto:
        por_kind[r.get("kind") or "sem-kind"].append(r)

    fatias = {}
    for kind, itens in sorted(por_kind.items()):
        fatias[kind] = {
            "registros": len(itens),
            "gzip_bytes": escrever(f"{SAIDA}/por-kind/{kind}.json", itens),
        }

    # a prosa continua separada, e e MAIOR que o indice inteiro: e por isso que
    # ela nao pode viajar junto. O app busca o texto de um registro so quando o
    # jogador abre aquele registro.
    prosa = 0
    for nome in sorted(os.listdir(f"{BASE}/text")):
        if nome.endswith(".json"):
            prosa += os.path.getsize(f"{BASE}/text/{nome}")

    manifesto = {
        "registros": len(enxuto),
        "kinds": len(fatias),
        "gzip_indice_completo": depois,
        "gzip_indice_de_build": antes,
        "prosa_bytes_em_disco": prosa,
        "campos_descartados": list(DESCARTAR),
        "por_kind": fatias,
    }
    escrever(f"{SAIDA}/_manifesto.json", manifesto)

    mb = 1048576
    print(f"registros: {len(enxuto)}  em {len(fatias)} kinds")
    print(f"indice de build:  {antes / mb:5.2f} MB gzip")
    print(f"indice do app:    {depois / mb:5.2f} MB gzip   "
          f"({100 * (antes - depois) / antes:.0f}% menor)")
    print(f"prosa (separada): {prosa / mb:5.2f} MB em disco, carregada sob demanda")
    print("\nmaiores fatias (gzip):")
    for kind, d in sorted(fatias.items(), key=lambda kv: -kv[1]["gzip_bytes"])[:8]:
        print(f"  {kind:<16} {d['gzip_bytes'] / 1024:7.0f} KB  "
              f"{d['registros']:>5} registros")

    # o que o construtor precisa para a PRIMEIRA tela: sem equipamento, sem
    # magia, sem catalogo de referencia
    # `action` entra no nucleo: a deed do Gunslinger e a reacao do Campeao sao
# concedidas no nivel 1 e precisam estar la na PRIMEIRA tela. Custo medido:
# ~45 B/registro gzip, abaixo de 5% do nucleo.
    montar_ficha = ("class", "class-feature", "feat", "ancestry", "heritage",
                    "background", "archetype", "skill", "action")
    nucleo = sum(fatias[k]["gzip_bytes"] for k in montar_ficha if k in fatias)
    print(f"\nnucleo para montar ficha ({', '.join(montar_ficha)}): "
          f"{nucleo / mb:.2f} MB gzip")
    print(f"-> {SAIDA}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
