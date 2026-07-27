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


def carregar_curadoria():
    """`aliases_referencias.json`: o que o nome sozinho nao resolve.

    Tres secoes, cada entrada com `verificado` dizendo contra o que foi
    conferida. O arquivo existia desde 2026-07-27 e NENHUM script o lia -- era
    o terceiro caso do mesmo padrao (ver `colisoes_identidade.json`).
    """
    caminho = f"{AQUI}/aliases_referencias.json"
    if not os.path.exists(caminho):
        return {}, {}, {}
    d = json.load(open(caminho))
    return (d.get("mapear") or {}, d.get("ignorar") or {},
            d.get("sem_sucessor_conhecido") or {})


def ponte_remaster(por_aon):
    """nome normalizado do doc LEGADO -> id `wb:` do sucessor na base.

    O Remaster renomeou em massa e o predicado guardou o nome antigo: `Attack
    of Opportunity` virou `Reactive Strike`, `Wild Shape` virou `Untamed Form`,
    `Mage Hand` virou `Telekinetic Hand`, toda ancestria `gnoll` virou `kholo`.
    Resolver por nome nao acha nada disso -- o nome mudou dos dois lados. Quem
    liga um ao outro e o `remaster_id` que o proprio AoN publica, e essa e
    evidencia declarada pela fonte, nao heuristica.
    """
    sys.path.insert(0, AQUI)
    import portoes
    aon = portoes.indice_aon()
    if not aon:
        return {}
    mapa = {}
    for d in aon.values():
        if not d.get("name"):
            continue
        sucessores = d.get("remaster_id")
        for s in (sucessores if isinstance(sucessores, list) else [sucessores]):
            # `remaster_id: ['0']` e "removido no remaster", nao renomeado
            if not s or str(s) == "0" or str(s) not in por_aon:
                continue
            mapa.setdefault(norm(d["name"]), por_aon[str(s)]["id"])
    return mapa


def main():
    base = json.load(open(f"{BASE}/index.json"))
    ids = {r["id"] for r in base}
    mapear, ignorar, sem_sucessor = carregar_curadoria()
    por_aon = {str((r.get("xref") or {}).get("aon")): r
               for r in base if (r.get("xref") or {}).get("aon")}
    legado = ponte_remaster(por_aon)

    # nome normalizado -> ids, com quem tem `grants` na frente
    por_nome = collections.defaultdict(list)
    for r in base:
        por_nome[norm(r.get("name"))].append(r)
    for nome in por_nome:
        por_nome[nome].sort(key=lambda r: (0 if r.get("grants") else 1,
                                           0 if r.get("kind") == "class-feature" else 1))

    resolvidas, nao_resolvidas = [], collections.Counter()
    por_curadoria, por_ponte, removidas = [], [], []
    for r in base:
        # materializa antes: o laco troca chave de container (`has` ->
        # `nao_modelavel`) e mutar durante a travessia estoura o gerador
        for container, chave in list(referencias(r.get("requires"))):
            alvo = container.get(chave)
            if not isinstance(alvo, str):
                continue
            if not alvo.startswith("wb:") or alvo in ids:
                continue

            # 1. curadoria: mapeamento conferido a mao vence qualquer heuristica
            if alvo in mapear:
                destino = mapear[alvo].get("para")
                if destino in ids:
                    container[chave] = destino
                    por_curadoria.append((alvo, destino))
                    continue
            if alvo in ignorar:
                # nao e entidade: o parser virou frase em id ("You have a
                # versatile heritage."). Vira termo `nao_modelavel`, que o
                # avaliador do motor ignora por ser termo desconhecido -- e o
                # contrario de `has: None`, que ele tentaria avaliar. O texto
                # original continua legivel em `requires_texto`.
                container.pop(chave, None)
                container["nao_modelavel"] = alvo
                removidas.append((alvo, ignorar[alvo].get("motivo", "")))
                continue
            # `sem_sucessor_conhecido` NAO curto-circuita: a entidade pode ter
            # entrado depois de o arquivo ser escrito. Foi o caso de
            # `universalist-wizard`, declarado sem sucessor enquanto
            # `wb:arcane-school/universalist` ja estava na base. So conta como
            # nao resolvida se as tentativas abaixo falharem.
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
                # 3. ultimo recurso: o nome mudou dos dois lados no Remaster.
                # A ponte do AoN e quem liga, e ela pode cruzar o kind citado
                # (`wb:spell/ki-strike` -> `wb:feat/qi-spells`): aqui isso e
                # aceitavel porque quem une e a FONTE declarando sucessao, nao
                # semelhanca de nome -- o risco que o guarda de kind evita e
                # justamente o do palpite por nome.
                destino = None
                for v in variantes(slug):
                    if v in legado:
                        destino = legado[v]
                        break
                if destino:
                    container[chave] = destino
                    por_ponte.append((alvo, destino))
                    continue
                nao_resolvidas[alvo] += 1
                continue
            container[chave] = escolhido["id"]
            r.setdefault("prov", {})["requires"] = (
                (r.get("prov") or {}).get("requires", "pf2etools") + "+resolvido-por-nome")
            resolvidas.append((alvo, escolhido["id"], escolhido.get("name")))

    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    print(f"referencias orfas resolvidas: {len(resolvidas)} por nome, "
          f"{len(por_curadoria)} por curadoria, {len(por_ponte)} pela ponte do AoN")
    print(f"removidas (nao eram entidade): {len(removidas)}")
    print(f"nao resolvidas: {sum(nao_resolvidas.values())} "
          f"({len(nao_resolvidas)} ids distintos)")

    linhas = ["# Referencias resolvidas", "",
              "`requires` citava ids que a base nao tem -- mas as entidades existem,",
              "com outro slug. O extrator derivou o id do nome que tinha em maos,",
              "antes de a reconciliacao decidir o nome canonico. Quando nem o nome",
              "sobreviveu (o Remaster renomeou dos dois lados), quem liga e o",
              "`remaster_id` publicado pelo proprio AoN.", "",
              f"- resolvidas por nome: **{len(resolvidas)}**",
              f"- resolvidas por curadoria (`aliases_referencias.json`): **{len(por_curadoria)}**",
              f"- resolvidas pela ponte legado->remaster do AoN: **{len(por_ponte)}**",
              f"- removidas por nao serem entidade: **{len(removidas)}**",
              f"- nao resolvidas: **{sum(nao_resolvidas.values())}**", ""]
    if por_ponte:
        linhas += ["## Pela ponte do AoN (nome mudou dos dois lados)", ""]
        vistos_p = set()
        for antigo, novo in por_ponte:
            if antigo not in vistos_p:
                vistos_p.add(antigo)
                linhas.append(f"- `{antigo}` -> `{novo}`")
        linhas.append("")
    if por_curadoria:
        linhas += ["## Por curadoria conferida a mao", ""]
        vistos_c = set()
        for antigo, novo in por_curadoria:
            if antigo not in vistos_c:
                vistos_c.add(antigo)
                linhas.append(f"- `{antigo}` -> `{novo}` -- "
                              f"{mapear[antigo].get('verificado', '')[:150]}")
        linhas.append("")
    if removidas:
        linhas += ["## Removidas: o parser virou frase em id", ""]
        vistos_r = set()
        for antigo, motivo in removidas:
            if antigo not in vistos_r:
                vistos_r.add(antigo)
                linhas.append(f"- `{antigo}` -- {motivo[:180]}")
        linhas.append("")
    linhas += ["## Resolvidas por nome", ""]
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
