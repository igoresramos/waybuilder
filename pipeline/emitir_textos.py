#!/usr/bin/env python3
"""
Camada de emissao de prosa.

O `index.json` guarda so o que serve para filtrar, e aponta a prosa por
referencia (`wb:text/<kind>/<slug>`). Este passo resolve essas referencias e
escreve os arquivos de texto, um por kind, carregados sob demanda pelo cliente.

Regra que motiva este passo: **o flavor nao se perde.** Texto narrativo,
pre-requisito em prosa que o parser nao entendeu, condicao de ficcao
("you died and returned as a ghost") -- tudo fica. O que o parser nao mecaniza
vira leitura, nunca descarte. Nada disso e usado como filtro.

Entrada: pipeline/base/index.json + pipeline/dados_brutos/
Saida:   pipeline/base/text/<kind>.json + relatorio de cobertura
"""
import json, os, re, glob, collections, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTO = f"{AQUI}/dados_brutos"


def limpar(t):
    """Remove marcacao de exibicao do AoN, preserva a prosa."""
    if not t:
        return ""
    t = re.sub(r"<[^>]+>", " ", t)                    # tags de layout
    t = re.sub(r"\{@\w+\s+([^}|]+)(\|[^}]*)?\}", r"\1", t)   # {@feat X|SRC} -> X
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)    # links markdown
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def indexar_aon():
    """id do AoN -> prosa."""
    idx = {}
    for f in glob.glob(f"{BRUTO}/aon_*.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        regs = d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list)), [])
        for r in regs:
            if isinstance(r, dict) and r.get("id"):
                t = limpar(r.get("text") or r.get("summary") or "")
                if t:
                    idx[r["id"]] = t
    # dumps por arquivo (class-feature__*.json etc.)
    for f in glob.glob(f"{BRUTO}/aon/*.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for r in (d if isinstance(d, list) else [d]):
            if isinstance(r, dict) and r.get("id"):
                t = limpar(r.get("text") or r.get("summary") or "")
                if t:
                    idx.setdefault(r["id"], t)
    return idx


def indexar_foundry():
    """nome normalizado -> descricao, como plano B."""
    idx = {}
    for f in glob.glob(f"{BRUTO}/foundry/**/*.json", recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for r in (d if isinstance(d, list) else [d]):
            if not isinstance(r, dict) or not r.get("name"):
                continue
            desc = (((r.get("system") or {}).get("description") or {}).get("value")) or ""
            t = limpar(desc)
            if t:
                idx.setdefault(re.sub(r"[^a-z0-9]+", "", r["name"].lower()), t)
    return idx


def main():
    base = json.load(open(f"{BASE}/index.json"))
    aon = indexar_aon()
    foundry = indexar_foundry()
    print(f"indice de prosa: {len(aon)} do AoN, {len(foundry)} do Foundry")

    textos = collections.defaultdict(dict)
    origem = collections.Counter()
    faltando = []

    for r in base:
        ref = r.get("text")
        if not isinstance(ref, str) or not ref.startswith("wb:text/"):
            continue
        kind = r.get("kind")
        t = ""
        aid = (r.get("xref") or {}).get("aon")
        if aid and aid in aon:
            t, de = aon[aid], "aon"
        if not t:
            chave = re.sub(r"[^a-z0-9]+", "", (r.get("name") or "").lower())
            if chave in foundry:
                t, de = foundry[chave], "foundry"
        if not t:
            t, de = (r.get("summary") or ""), "summary"
        if t:
            textos[kind][ref] = t
            origem[de] += 1
        else:
            faltando.append(r["id"])

    os.makedirs(f"{BASE}/text", exist_ok=True)
    total_bytes = 0
    for kind, mapa in textos.items():
        caminho = f"{BASE}/text/{kind}.json"
        json.dump(mapa, open(caminho, "w"), ensure_ascii=False, separators=(",", ":"))
        total_bytes += os.path.getsize(caminho)
        print(f"  {kind:14} {len(mapa):>5} textos  {os.path.getsize(caminho)/1e6:.2f} MB")

    # portao: nenhuma referencia pendurada
    resolvidas = sum(len(m) for m in textos.values())
    esperadas = sum(1 for r in base if isinstance(r.get("text"), str)
                    and r["text"].startswith("wb:text/"))
    print(f"\nreferencias resolvidas: {resolvidas}/{esperadas} ({resolvidas/max(1,esperadas):.1%})")
    print(f"origem: {dict(origem)}")
    print(f"prosa total: {total_bytes/1e6:.1f} MB")
    if faltando:
        print(f"SEM PROSA ({len(faltando)}): {faltando[:12]}")

    open(f"{BASE}/relatorio_textos.md", "w").write(
        "# Emissao de prosa\n\n"
        f"- referencias resolvidas: **{resolvidas}/{esperadas}** "
        f"({resolvidas/max(1,esperadas):.1%})\n"
        f"- origem: {dict(origem)}\n"
        f"- prosa total: {total_bytes/1e6:.1f} MB\n"
        f"- sem prosa: {len(faltando)}\n\n"
        + ("## Sem prosa\n\n" + "\n".join(f"- `{i}`" for i in faltando) if faltando else "")
    )
    return 0 if resolvidas / max(1, esperadas) > 0.98 else 1


if __name__ == "__main__":
    sys.exit(main())
