#!/usr/bin/env python3
"""
Gera `canonico_livros.json`: grafia normalizada -> grafia canonica de cada obra.

Motivo: `source.book` saia com duas grafias para 26 obras, afetando 11.116
registros ("Player Core" vs "Pathfinder Player Core"), mais 161 registros com
`\\r\\n` literal dentro do nome. A funcao normalizar_livro() ja existia mas so
rodava na COMPARACAO -- o valor emitido continuava nas duas formas.

Quem decide a grafia e o AoN, por precedencia da spec (`source` vem do aon).
Medido: o AoN e internamente consistente e nunca usa o prefixo "Pathfinder";
essa forma vem do Foundry.

Uso: python3 gerar_canonico_livros.py
"""
import json, glob, os, collections, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from reconciliar import normalizar_livro          # noqa: E402

AON_DUMP = f"{AQUI}/dados_brutos/aon_dump"
DESTINO = f"{AQUI}/canonico_livros.json"
CAMPOS = ("primary_source", "primary_source_raw", "source", "source_raw")


def limpar(s):
    """Tira ' pg. 12' e quebra de linha literal que vem colada no titulo."""
    s = str(s).replace("\\r", " ").replace("\\n", " ").replace("\r", " ").replace("\n", " ")
    return " ".join(s.split(" pg.")[0].split()).strip()


def main():
    if not os.path.isdir(AON_DUMP):
        print(f"sem dump do AoN em {AON_DUMP} -- rode dump_aon.py antes", file=sys.stderr)
        return 1

    freq = collections.defaultdict(collections.Counter)
    for f in glob.glob(f"{AON_DUMP}/*.json"):
        if os.path.basename(f).startswith("_"):
            continue
        try:
            docs = json.load(open(f))
        except Exception:
            continue
        for d in docs:
            for campo in CAMPOS:
                v = d.get(campo)
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, str) and x.strip():
                        titulo = limpar(x)
                        if titulo:
                            freq[normalizar_livro(titulo)][titulo] += 1

    mapa = {chave: contagem.most_common(1)[0][0] for chave, contagem in freq.items()}
    ambiguos = {k: dict(c.most_common(3)) for k, c in freq.items() if len(c) > 1}

    json.dump({
        "_prov": "grafia mais frequente no dump do AoN; `source` vem do aon por "
                 "precedencia da spec (specs/2026-07-26-schema-base.md)",
        "_gerado_por": "pipeline/gerar_canonico_livros.py",
        "canonico": mapa,
        "ambiguos_no_aon": ambiguos,
    }, open(DESTINO, "w"), ensure_ascii=False, indent=1, sort_keys=True)

    print(f"obras canonizadas: {len(mapa)}")
    print(f"ambiguas dentro do proprio AoN: {len(ambiguos)}")
    for k, v in list(ambiguos.items())[:5]:
        print(f"   {k} -> {v}")
    print(f"-> {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
