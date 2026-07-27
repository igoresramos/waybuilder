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
    arquivos = [f for f in glob.glob(f"{AON_DUMP}/*.json")
                if not os.path.basename(f).startswith("_")]
    if not arquivos:
        # os apelidos versionados sao copias das mesmas categorias do dump; sem
        # eles uma maquina que nunca rodou dump_aon.py gera mapa vazio e toda
        # obra sai na grafia de entrada
        arquivos = sorted(glob.glob(f"{os.path.dirname(AON_DUMP)}/aon_*.json"))
    if not arquivos:
        print(f"sem dump do AoN em {AON_DUMP} -- rode dump_aon.py antes", file=sys.stderr)
        return 1

    freq = collections.defaultdict(collections.Counter)
    for f in arquivos:
        try:
            docs = json.load(open(f))
        except Exception:
            continue
        if not isinstance(docs, list):
            continue
        for d in docs:
            if not isinstance(d, dict):
                continue
            for campo in CAMPOS:
                v = d.get(campo)
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, str) and x.strip():
                        titulo = limpar(x)
                        if titulo:
                            freq[normalizar_livro(titulo)][titulo] += 1

    mapa = {chave: contagem.most_common(1)[0][0] for chave, contagem in freq.items()}
    ambiguos = {k: dict(c.most_common(3)) for k, c in freq.items() if len(c) > 1}

    # Obra que o AoN nao indexa fica sem entrada, e `canonizar_livro` devolve a
    # grafia de entrada -- entao a mesma obra sai com duas grafias. Foi o caso
    # de `Lost Omens: Pathfinder Society Guide` x `Pathfinder Lost Omens
    # Pathfinder Society Guide` e de `The Grand Bazaar`. Para essas, e so para
    # essas, a grafia mais frequente nas outras fontes decide.
    resto = collections.defaultdict(collections.Counter)
    for f in sorted(glob.glob(f"{os.path.dirname(AON_DUMP)}/../saida/*.json")):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        lista = d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list)), [])
        for r in lista:
            if not isinstance(r, dict):
                continue
            livro = (r.get("source") or {}).get("book") if isinstance(
                r.get("source"), dict) else None
            if isinstance(livro, str) and livro.strip():
                titulo = limpar(livro)
                chave = normalizar_livro(titulo)
                if titulo and chave not in mapa:
                    resto[chave][titulo] += 1
    def preferida(contagem):
        """Segue a convencao do AoN: sem o prefixo editorial `Pathfinder`.

        Escolher so pela frequencia entregaria a grafia do Foundry, que e a
        maioria dos registros -- e as 46 obras fora do AoN sairiam num estilo
        e as 243 dele em outro.
        """
        variantes = sorted(contagem, key=lambda t: (-contagem[t], t))
        sem_prefixo = [t for t in variantes if not t.startswith("Pathfinder ")]
        return (sem_prefixo or variantes)[0]

    fora_do_aon = {k: preferida(c) for k, c in resto.items()}
    mapa.update(fora_do_aon)

    json.dump({
        "_prov": "grafia mais frequente no dump do AoN; `source` vem do aon por "
                 "precedencia da spec (specs/2026-07-26-schema-base.md). Obra que "
                 "o AoN nao indexa e decidida pela grafia mais frequente nas "
                 "outras fontes -- ver `fora_do_aon`",
        "_gerado_por": "pipeline/gerar_canonico_livros.py",
        "canonico": mapa,
        "ambiguos_no_aon": ambiguos,
        "fora_do_aon": fora_do_aon,
    }, open(DESTINO, "w"), ensure_ascii=False, indent=1, sort_keys=True)

    print(f"obras so nas outras fontes: {len(fora_do_aon)}")
    print(f"obras canonizadas: {len(mapa)}")
    print(f"ambiguas dentro do proprio AoN: {len(ambiguos)}")
    for k, v in list(ambiguos.items())[:5]:
        print(f"   {k} -> {v}")
    print(f"-> {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
