#!/usr/bin/env python3
"""
Dump completo do indice `aon` do Archives of Nethys para dados_brutos/aon_dump/.

Por que existe: os extratores consultavam o AoN ao vivo e so alguns gravavam
cache. `carregar_aon()` do extrator de equipamento, por exemplo, cai para lista
vazia **em silencio** quando o dump nao existe -- foi o que fez a re-execucao de
2026-07-26 produzir 5.698 registros de equipamento contra os 7.496 da base, com
cobertura mono-fonte. A spec ja mandava fixar a fonte em disco; isto cumpre.

Um arquivo por categoria, todos os campos (`_source: true`), sem lista fixa --
lista fixa de campos e como se perde `remaster_id` sem perceber.

Uso:
    python3 dump_aon.py              # so o que falta
    python3 dump_aon.py --forcar     # rebaixa tudo
    python3 dump_aon.py spell ritual # so essas categorias
"""
import json, os, sys, time, urllib.request, urllib.error

AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(AQUI, "dados_brutos", "aon_dump")

URL = "https://elasticsearch.aonprd.com/aon/_search"
# Sem User-Agent a resposta trava pendurada -- nao da erro, so nunca volta.
HEADERS = {"Content-Type": "application/json", "User-Agent": "waybuilder-extrator/1"}
TIMEOUT = 45
PAGINA = 200          # respostas grandes sofrem throttling de banda
PAUSA = 0.15          # cortesia entre paginas
TENTATIVAS = 5


def post(payload):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())


def com_retentativa(payload, rotulo):
    """Reduz a pagina pela metade a cada rodada de falhas antes de desistir."""
    tentativa = 0
    while True:
        tentativa += 1
        try:
            return post(payload)
        except urllib.error.HTTPError as exc:
            # 4xx (menos 429) e defeito da consulta: retentar so gasta tempo.
            if 400 <= exc.code < 500 and exc.code != 429:
                print(f"    [{rotulo}] HTTP {exc.code}: {exc.read()[:300]!r}", file=sys.stderr)
                raise
            print(f"    [{rotulo}] tentativa {tentativa}: HTTP {exc.code}", file=sys.stderr)
            if tentativa >= TENTATIVAS:
                raise
            time.sleep(1.0)
        except Exception as exc:
            print(f"    [{rotulo}] tentativa {tentativa}: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            if tentativa >= TENTATIVAS:
                if payload.get("size", 0) > 10:
                    payload["size"] = max(10, payload["size"] // 2)
                    tentativa = 0
                    print(f"    [{rotulo}] reduzindo pagina para {payload['size']}",
                          file=sys.stderr)
                else:
                    raise
            time.sleep(1.0)


def categorias():
    d = post({"size": 0, "aggs": {"c": {"terms": {"field": "category", "size": 200}}}})
    return {b["key"]: b["doc_count"] for b in d["aggregations"]["c"]["buckets"]}


def baixar(cat, esperado):
    """search_after: from/size trava no teto de 10k.

    Sort por `_doc`: o indice desabilita fielddata em `_id` e em `id` (text),
    entao os dois dao HTTP 400. `name.keyword` funciona mas empata em homonimo
    -- e homonimo e exatamente o que este projeto nao pode perder.
    """
    todos, ultimo = [], None
    while True:
        p = {"size": PAGINA, "track_total_hits": True, "_source": True,
             "sort": ["_doc"],
             "query": {"bool": {"must": [{"match_phrase": {"category": cat}}]}}}
        if ultimo is not None:
            p["search_after"] = ultimo
        d = com_retentativa(p, cat)
        hits = d["hits"]["hits"]
        if not hits:
            break
        todos.extend({**h["_source"], "_id": h["_id"]} for h in hits)
        ultimo = hits[-1]["sort"]
        time.sleep(PAUSA)
    if esperado is not None and len(todos) != esperado:
        print(f"    ! {cat}: {len(todos)} baixados, {esperado} esperados", file=sys.stderr)
    return todos


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    forcar = "--forcar" in sys.argv
    os.makedirs(DESTINO, exist_ok=True)

    censo = categorias()
    alvos = args or sorted(censo, key=lambda c: -censo[c])
    print(f"indice aon: {sum(censo.values())} docs em {len(censo)} categorias")

    manifesto, baixados, pulados = {}, 0, 0
    for cat in alvos:
        caminho = os.path.join(DESTINO, f"{cat}.json")
        if os.path.exists(caminho) and not forcar:
            manifesto[cat] = len(json.load(open(caminho)))
            pulados += 1
            continue
        regs = baixar(cat, censo.get(cat))
        json.dump(regs, open(caminho, "w"), ensure_ascii=False, separators=(",", ":"))
        manifesto[cat] = len(regs)
        baixados += len(regs)
        print(f"  {cat:32} {len(regs):>6}")

    manifesto["_censo_remoto"] = censo
    manifesto["_pin"] = time.strftime("%Y-%m-%d")
    json.dump(manifesto, open(os.path.join(DESTINO, "_manifesto.json"), "w"),
              ensure_ascii=False, indent=1)

    total = sum(v for k, v in manifesto.items() if not k.startswith("_"))
    print(f"\ntotal em disco: {total} docs "
          f"({baixados} baixados agora, {pulados} categorias ja em cache)")
    # so cobra as categorias pedidas nesta rodada -- senao um dump parcial de
    # proposito se reporta como falha
    faltando = {c: n for c, n in censo.items()
                if c in alvos and manifesto.get(c, 0) != n}
    if faltando:
        print(f"INCOMPLETO em {len(faltando)} categorias: "
              f"{dict(list(faltando.items())[:8])}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
