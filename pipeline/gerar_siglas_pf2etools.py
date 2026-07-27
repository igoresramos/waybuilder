#!/usr/bin/env python3
"""
Gera `siglas_pf2etools.json`: sigla de livro do pf2etools -> titulo completo.

O pf2etools grava `source` como sigla (`"G&G"`, `"LOGM"`, `"FRP2"`, `"PC1"`).
Sem o mapa, registro que so existe nessa fonte sai com `source` vazio -- foi o
que deixou `Nine-Ring Sword`, `Wind and Fire Wheel` e `Heavy Power Suit` sem
livro e sem licenca, os 3 que seguravam o portao 5.

`data/books.json` cobre 5 livros. O mapa completo esta em `js/parser.js`, nas
linhas `Parser.SOURCE_JSON_TO_FULL[SRC_X] = "Titulo";`, com as constantes
`SRC_X = "sigla"` declaradas no mesmo arquivo. Ler de la e o oposto de chutar:
a fonte declara a propria abreviacao.

Uso: python3 gerar_siglas_pf2etools.py
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PARSER = os.path.join(AQUI, "dados_brutos", "pf2etools_repo", "js", "parser.js")
DESTINO = os.path.join(AQUI, "siglas_pf2etools.json")


def main():
    if not os.path.exists(PARSER):
        print(f"sem {PARSER} -- rode buscar_fontes.sh antes", file=sys.stderr)
        return 1
    texto = open(PARSER, encoding="utf-8", errors="replace").read()

    # const SRC_GnG = "G&G";
    constantes = dict(re.findall(r'\b(SRC_\w+)\s*=\s*"([^"]+)"', texto))
    # Parser.SOURCE_JSON_TO_FULL[SRC_GnG] = "Guns & Gears";
    pares = re.findall(
        r'SOURCE_JSON_TO_FULL\[\s*(SRC_\w+|"[^"]+")\s*\]\s*=\s*"([^"]+)"', texto)

    mapa = {}
    for chave, titulo in pares:
        sigla = chave.strip('"')
        sigla = constantes.get(sigla, sigla)
        if sigla and titulo:
            mapa[sigla] = titulo

    if len(mapa) < 50:
        print(f"mapa suspeito: so {len(mapa)} siglas", file=sys.stderr)
        return 1

    json.dump({
        "_prov": "js/parser.js do Pf2eToolsOrg/Pf2eTools (SOURCE_JSON_TO_FULL), "
                 "pin em buscar_fontes.sh -- a fonte declara a propria sigla",
        "_gerado_por": "pipeline/gerar_siglas_pf2etools.py",
        "siglas": dict(sorted(mapa.items())),
    }, open(DESTINO, "w"), ensure_ascii=False, indent=1)

    print(f"siglas mapeadas: {len(mapa)}")
    for s in ("G&G", "LOGM", "FRP2", "PC1", "PC2", "CRB", "LOCG", "TV"):
        if s in mapa:
            print(f"   {s:6} -> {mapa[s]}")
    print(f"-> {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
