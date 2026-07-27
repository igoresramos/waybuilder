#!/usr/bin/env python3
"""
Detecta divergencia entre fontes que os extratores nunca registraram.

O contrato da spec e "divergencia e registrada, nunca silenciada". Seis kinds
nao cumpriam: `class-feature`, `background`, `heritage`, `familiar-ability`,
`ancestry` e `class` somavam 1.618 registros com duas ou mais fontes e **zero**
conflitos anotados. Nao era ausencia de divergencia -- era ausencia de
deteccao: cada extrator funde as fontes por dentro e emite um valor unico, sem
comparar. Por isso os 2.299 conflitos da base eram um PISO, nunca o total.

Reescrever seis extratores seria o caminho longo. Este passo faz a comparacao
onde as duas fontes ainda existem: o dump do AoN e o clone do Foundry em disco,
alcancados pelo `xref` de cada registro. O que diverge e anotado em
`conflitos`, no mesmo formato que o reconciliador usa.

Entrada: pipeline/base/index.json (+ dados_brutos/)
Saida:   index.json reescrito + base/relatorio_conflitos.md
"""
import json, os, sys, collections, re, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import portoes                                    # noqa: E402
from reconciliar import normalizar_livro          # noqa: E402

BASE = f"{AQUI}/base"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def chave_livro(b):
    """Chave so para COMPARAR obra entre fontes -- nunca para emitir.

    O AoN e o Foundry descrevem a mesma obra com convencoes editoriais
    diferentes: 'Guns & Gears (Remastered)' x 'Pathfinder Guns & Gears',
    'PFS Guide' x 'Pathfinder Lost Omens Pathfinder Society Guide',
    'Pathfinder #222: Hellbreakers' x 'Pathfinder Adventure Path: Hellbreakers'.
    Tratar isso como divergencia troca silencio por ruido, que e pior: enterra
    as poucas divergencias reais (Player Core 2 x GM Core) em 1.700 falsas.
    """
    n = normalizar_livro(b or "")
    n = re.sub(r"\bremaster(ed)?\b", "", n)
    n = re.sub(r"\bhardcover( compilation)?\b", "", n)
    n = re.sub(r"^adventure( path)? ", "", n)
    n = re.sub(r"^\d+ ", "", n)                    # '#222: Hellbreakers'
    n = re.sub(r"^the ", "", n)
    n = re.sub(r"\bcompanion guide\b", "", n)
    n = n.replace("pathfinder society guide", "pfs guide")
    return re.sub(r"\s+", " ", n).strip()


def livro_de(doc):
    v = doc.get("primary_source_raw") or doc.get("primary_source")
    if isinstance(v, list):
        v = v[0] if v else None
    return str(v).split(" pg.")[0].strip() if v else None


def main():
    base = json.load(open(f"{BASE}/index.json"))
    aon = portoes.indice_aon()
    foundry = portoes.indice_foundry()
    if not aon or not foundry:
        print("ERRO: sem dump do AoN ou clone do Foundry em disco", file=sys.stderr)
        return 1

    achados = collections.Counter()
    por_kind = collections.defaultdict(collections.Counter)
    novos = 0

    for r in base:
        xr = r.get("xref") or {}
        doc_aon = aon.get(str(xr.get("aon", "")))
        doc_fnd = foundry.get(str(xr.get("foundry", "")).split(".")[-1])
        if not doc_aon and not doc_fnd:
            continue
        ja = {c.get("campo") for c in (r.get("conflitos") or [])}
        conflitos = list(r.get("conflitos") or [])

        # name -- so conta divergencia depois de normalizar; grafia nao e conflito
        if doc_aon and doc_fnd and "name" not in ja:
            a, f = doc_aon.get("name"), doc_fnd.get("name")
            if a and f and norm(a) != norm(f):
                conflitos.append({"campo": "name", "aon": a, "foundry": f,
                                  "escolhido": (r.get("prov") or {}).get("name", "aon")})
                achados["name"] += 1
                por_kind[r.get("kind")]["name"] += 1

        # level -- class-feature fica de fora: o nivel vive na progressao da classe
        if (doc_aon and doc_fnd and "level" not in ja
                and r.get("kind") != "class-feature"):
            a, f = doc_aon.get("level"), doc_fnd.get("level")
            if a is not None and f is not None and a != f:
                conflitos.append({"campo": "level", "aon": a, "foundry": f,
                                  "escolhido": (r.get("prov") or {}).get("level", "foundry")})
                achados["level"] += 1
                por_kind[r.get("kind")]["level"] += 1

        # source.book -- comparado ja normalizado, senao 26 obras com duas
        # grafias virariam 10 mil conflitos falsos.
        # O confronto que importa e AoN x FOUNDRY: comparar o AoN com o valor
        # emitido nunca acha nada, porque `source` vem do AoN por precedencia --
        # foi assim que 145 divergencias reais passaram despercebidas.
        if doc_aon and doc_fnd and "source" not in ja and "source.book" not in ja:
            a, f = livro_de(doc_aon), doc_fnd.get("book")
            if a and f and chave_livro(a) != chave_livro(f):
                conflitos.append({"campo": "source.book", "aon": a, "foundry": f,
                                  "escolhido": "aon"})
                achados["source.book"] += 1
                por_kind[r.get("kind")]["source.book"] += 1

        # rarity -- idem: AoN contra Foundry
        if doc_aon and doc_fnd and "rarity" not in ja:
            a = (doc_aon.get("rarity") or "").lower()
            f = (doc_fnd.get("rarity") or "").lower()
            if a and f and a != f:
                conflitos.append({"campo": "rarity", "aon": a, "foundry": f,
                                  "escolhido": "aon"})
                achados["rarity"] += 1
                por_kind[r.get("kind")]["rarity"] += 1

        if len(conflitos) != len(r.get("conflitos") or []):
            r["conflitos"] = conflitos
            novos += 1

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    total = sum(1 for r in base if r.get("conflitos"))
    print(f"registros que ganharam conflito nesta passada: {novos}")
    print(f"divergencias encontradas por campo: {dict(achados)}")
    print(f"registros com conflito registrado na base: {total}")

    linhas = ["# Divergencias detectadas fora dos extratores", "",
              "Os extratores fundem as fontes por dentro e emitem um valor unico.",
              "Esta passada compara a base contra o AoN e o Foundry em disco, pelo",
              "`xref`, e anota o que discorda -- o contrato da spec e que",
              "divergencia nunca e silenciada.", "",
              f"- registros que ganharam conflito: **{novos}**",
              f"- registros com conflito na base: **{total}**", "",
              "## Por campo", ""]
    linhas += [f"- `{c}`: {n}" for c, n in achados.most_common()]
    linhas += ["", "## Por kind", ""]
    for kind, campos in sorted(por_kind.items(), key=lambda x: -sum(x[1].values())):
        linhas.append(f"- **{kind}**: {dict(campos)}")
    open(f"{BASE}/relatorio_conflitos.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_conflitos.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
