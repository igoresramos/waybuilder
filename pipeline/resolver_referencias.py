#!/usr/bin/env python3
"""
Resolve referencia `wb:` orfa dentro de `requires`, por nome.

A spec fecha o ciclo com "toda referencia no documento e um id `wb:` da base --
as tres fontes tinham tres vocabularios, a base normalizou para um". O portao 3
mostrava 80 citacoes a 61 ids inexistentes, e a leitura obvia ("falta conteudo")
estava errada: **as entidades existem**, com outro slug.

  `requires` cita  wb:class-feature/enigma-muse   (slug do nome no AoN)
  a base guarda    wb:class-feature/enigma        (nome no Foundry)
                   wb:muse/enigma-muse-5          (catalogo do AoN)

O extrator que escreveu o predicado derivou o id do nome que ELE tinha em maos,
antes de a reconciliacao decidir qual nome seria canonico. Nao e falta de dado,
e vocabulario nao unificado -- exatamente o que a base existe para eliminar.

Preferencia ao resolver: quem tem `grants` vence, porque o predicado aponta para
a entidade que o motor precisa avaliar, nao para a ficha de catalogo.

Entrada: pipeline/base/index.json
Saida:   index.json reescrito + base/relatorio_referencias.md
"""
import json, os, re, sys, unicodedata, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
sys.path.insert(0, os.path.join(AQUI, "extratores"))
from aon_kinds import SUBESCOLHAS as SUBESCOLHAS_KINDS   # noqa: E402


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def variantes(slug):
    """'enigma-muse' -> {'enigma muse', 'enigma'}; 'universalist-wizard' -> +'universalist'.

    O sufixo com o eixo (`-muse`, `-racket`, `-wizard`, `-instinct`) e como o AoN
    desambigua no titulo; o Foundry usa o nome curto.
    """
    base = norm(slug.replace("-", " "))
    saida = {base}
    for sufixo in ("muse", "racket", "wizard", "instinct", "doctrine", "bloodline",
                   "mystery", "patron", "way", "style", "cause", "order", "school",
                   "thesis", "edge", "field", "study", "implement", "lesson"):
        if base.endswith(" " + sufixo):
            saida.add(base[: -len(sufixo) - 1].strip())
    return {v for v in saida if v}


def referencias(obj):
    """Caminha o predicado devolvendo (container, chave) de cada `has`."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "has" and isinstance(v, str):
                yield obj, k
            else:
                yield from referencias(v)
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            if isinstance(x, str):
                continue
            yield from referencias(x)


def main():
    base = json.load(open(f"{BASE}/index.json"))
    ids = {r["id"] for r in base}

    # nome normalizado -> ids, com quem tem `grants` na frente
    por_nome = collections.defaultdict(list)
    for r in base:
        por_nome[norm(r.get("name"))].append(r)
    for nome in por_nome:
        por_nome[nome].sort(key=lambda r: (0 if r.get("grants") else 1,
                                           0 if r.get("kind") == "class-feature" else 1))

    resolvidas, nao_resolvidas = [], collections.Counter()
    for r in base:
        for container, chave in referencias(r.get("requires")):
            alvo = container[chave]
            if not alvo.startswith("wb:") or alvo in ids:
                continue
            kind, _, slug = alvo[3:].partition("/")
            # o kind citado e parte da referencia, nao ruido: resolver
            # `wb:heritage/versatile` para `wb:trait/versatile` troca uma
            # referencia quebrada por uma silenciosamente errada, que e pior.
            # Sub-escolha e excecao declarada: o predicado cita `class-feature`
            # e a entidade pode ter virado kind proprio (`muse`, `racket`...).
            candidatos = []
            for v in variantes(slug):
                candidatos.extend(por_nome.get(v, []))
            escolhido = next((c for c in candidatos if c.get("kind") == kind), None)
            if escolhido is None and kind == "class-feature":
                escolhido = next((c for c in candidatos
                                  if c.get("kind") in SUBESCOLHAS_KINDS), None)
            if escolhido is None:
                nao_resolvidas[alvo] += 1
                continue
            container[chave] = escolhido["id"]
            r.setdefault("prov", {})["requires"] = (
                (r.get("prov") or {}).get("requires", "pf2etools") + "+resolvido-por-nome")
            resolvidas.append((alvo, escolhido["id"], escolhido.get("name")))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    print(f"referencias orfas resolvidas: {len(resolvidas)}")
    print(f"nao resolvidas: {sum(nao_resolvidas.values())} "
          f"({len(nao_resolvidas)} ids distintos)")

    linhas = ["# Referencias resolvidas por nome", "",
              "`requires` citava ids que a base nao tem -- mas as entidades existem,",
              "com outro slug. O extrator derivou o id do nome que tinha em maos,",
              "antes de a reconciliacao decidir o nome canonico.", "",
              f"- resolvidas: **{len(resolvidas)}**",
              f"- nao resolvidas: **{sum(nao_resolvidas.values())}**", "",
              "## Resolvidas", ""]
    vistos = set()
    for antigo, novo, nome in resolvidas:
        if antigo in vistos:
            continue
        vistos.add(antigo)
        linhas.append(f"- `{antigo}` -> `{novo}`  ({nome})")
    if nao_resolvidas:
        linhas += ["", "## Nao resolvidas", ""]
        linhas += [f"- `{i}` citado {n}x" for i, n in nao_resolvidas.most_common(40)]
    open(f"{BASE}/relatorio_referencias.md", "w").write("\n".join(linhas) + "\n")
    print("-> base/relatorio_referencias.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
