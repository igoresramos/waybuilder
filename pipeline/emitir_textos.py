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
sys.path.insert(0, AQUI)
import comum  # noqa: E402

BASE = f"{AQUI}/base"
BRUTO = f"{AQUI}/dados_brutos"

# origem da prosa -> valor de prov, no vocabulario fechado da spec v2
PROV_POR_ORIGEM = {
    "aon":              lambda: comum.prov_lido("aon"),
    "foundry":          lambda: comum.prov_lido("foundry"),
    "pf2etools":        lambda: comum.prov_lido("pf2etools"),
    "aon:nome":         lambda: comum.prov_inferido("aon", "nome-aproximado"),
    "aon:alias":        lambda: comum.prov_inferido("aon", "nome-aproximado"),
    "pf2etools:alias":  lambda: comum.prov_inferido("pf2etools", "nome-aproximado"),
}


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


CLONE = os.environ.get("WB_FOUNDRY_PACKS") or os.path.join(
    AQUI, "dados_brutos", "foundry", "packs", "pf2e")


def indexar_foundry():
    """nome normalizado -> descricao. Le o cache e, se existir, o clone completo."""
    idx = {}
    fontes = glob.glob(f"{BRUTO}/foundry/**/*.json", recursive=True)
    if os.path.isdir(CLONE):
        fontes += glob.glob(f"{CLONE}/**/*.json", recursive=True)
    for f in fontes:
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


def entries_para_prosa(e, prof=0):
    """`entries` do pf2etools -> prosa legivel."""
    out = []
    if isinstance(e, str):
        out.append(e)
    elif isinstance(e, list):
        for x in e:
            out.append(entries_para_prosa(x, prof))
    elif isinstance(e, dict):
        if e.get("name"):
            out.append(f"**{e['name']}**")
        for chave in ("entries", "items", "entry"):
            if chave in e:
                out.append(entries_para_prosa(e[chave], prof + 1))
    return limpar("\n".join(x for x in out if x))


def indexar_pf2etools():
    """nome normalizado -> prosa, a partir de `entries`."""
    idx = {}
    for f in glob.glob(f"{BRUTO}/pf2etools/**/*.json", recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        for v in d.values():
            if not isinstance(v, list):
                continue
            for r in v:
                if not isinstance(r, dict) or not r.get("name") or not r.get("entries"):
                    continue
                t = entries_para_prosa(r["entries"])
                if t:
                    idx.setdefault(re.sub(r"[^a-z0-9]+", "", r["name"].lower()), t)
    return idx


def chaves_de(nome):
    """Nome cru e sem o sufixo desambiguador: 'Tusks (Orc)' -> tambem 'Tusks'."""
    base = re.sub(r"[^a-z0-9]+", "", (nome or "").lower())
    sem_par = re.sub(r"\s*\([^)]*\)\s*$", "", nome or "")
    alt = re.sub(r"[^a-z0-9]+", "", sem_par.lower())
    return [k for k in dict.fromkeys([base, alt]) if k]


def main():
    base = json.load(open(f"{BASE}/index.json"))
    aon = indexar_aon()
    foundry = indexar_foundry()
    pf2t = indexar_pf2etools()
    aon_por_nome = {}
    for f in glob.glob(f"{BRUTO}/aon_*.json"):
        try: d = json.load(open(f))
        except Exception: continue
        regs = d if isinstance(d, list) else next((v for v in d.values() if isinstance(v, list)), [])
        for r in regs:
            if isinstance(r, dict) and r.get("name"):
                t = limpar(r.get("text") or r.get("summary") or "")
                if t:
                    aon_por_nome.setdefault(re.sub(r"[^a-z0-9]+", "", r["name"].lower()), t)
    print(f"indice de prosa: {len(aon)} AoN(id), {len(aon_por_nome)} AoN(nome), "
          f"{len(foundry)} Foundry, {len(pf2t)} pf2etools")

    textos = collections.defaultdict(dict)
    origem = collections.Counter()
    faltando = []

    criadas = 0
    for r in base:
        ref = r.get("text")
        if not isinstance(ref, str) or not ref.startswith("wb:text/"):
            # Registro sem referencia nenhuma era invisivel para a metrica
            # antiga: nao entrava no denominador e por isso "prosa em 100%"
            # convivia com 907 registros sem prosa. Agora todo registro ganha
            # referencia e a busca pela prosa acontece para todos.
            ref = "wb:text/" + r["id"].split("wb:", 1)[-1]
            r["text"] = ref
            criadas += 1
        kind = r.get("kind")
        t = ""
        aid = (r.get("xref") or {}).get("aon")
        if aid and aid in aon:
            t, de = aon[aid], "aon"
        if not t:
            for chave in chaves_de(r.get("name")):
                for mapa, rotulo in ((foundry, "foundry"), (aon_por_nome, "aon:nome"),
                                     (pf2t, "pf2etools")):
                    if chave in mapa:
                        t, de = mapa[chave], rotulo
                        break
                if t: break
        if not t:
            for alias in (r.get("aliases") or []):
                for chave in chaves_de(alias):
                    for mapa, rotulo in ((aon_por_nome, "aon:alias"), (pf2t, "pf2etools:alias")):
                        if chave in mapa:
                            t, de = mapa[chave], rotulo
                            break
                    if t: break
                if t: break
        if not t:
            t, de = (r.get("summary") or ""), "summary"
        if t:
            textos[kind][ref] = t
            origem[de] += 1
            fabrica = PROV_POR_ORIGEM.get(de)
            if fabrica:
                r.setdefault("prov", {})["text"] = fabrica()
            elif not comum.prov_valido((r.get("prov") or {}).get("text") or ""):
                # `summary` ja veio de alguma fonte: herda a prov do proprio campo
                p = (r.get("prov") or {}).get("summary")
                fontes = [k for k in (r.get("xref") or {})
                          if k in ("aon", "foundry", "pf2etools")]
                r.setdefault("prov", {})["text"] = (
                    p if comum.prov_valido(p or "")
                    else comum.prov_lido(fontes[0]) if len(fontes) == 1
                    else comum.prov_lido("waybuilder"))
        else:
            faltando.append(r["id"])
            r.pop("text", None)
            (r.get("prov") or {}).pop("text", None)

    os.makedirs(f"{BASE}/text", exist_ok=True)
    total_bytes = 0
    for kind, mapa in textos.items():
        caminho = f"{BASE}/text/{kind}.json"
        json.dump(mapa, open(caminho, "w"), ensure_ascii=False, separators=(",", ":"))
        total_bytes += os.path.getsize(caminho)
        print(f"  {kind:14} {len(mapa):>5} textos  {os.path.getsize(caminho)/1e6:.2f} MB")

    # O index guarda as referencias criadas aqui e a prov de cada prosa.
    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))

    # Metrica: o denominador e a BASE INTEIRA, nao o subconjunto que ja tinha
    # referencia. Dividir pelo subconjunto processado foi o que fez "prosa em
    # 100% (17.866/17.866)" conviver com 907 registros sem prosa nenhuma.
    resolvidas = sum(len(m) for m in textos.values())
    total = len(base)
    orfas = resolvidas - sum(1 for r in base if r.get("text"))
    print(f"\nprosa: {resolvidas}/{total} da base ({resolvidas/max(1,total):.1%})")
    print(f"referencias criadas neste passo: {criadas}")
    print(f"origem: {dict(origem)}")
    print(f"prosa total: {total_bytes/1e6:.1f} MB")
    if faltando:
        print(f"SEM PROSA ({len(faltando)}): {faltando[:12]}")

    open(f"{BASE}/relatorio_textos.md", "w").write(
        "# Emissao de prosa\n\n"
        f"- registros com prosa: **{resolvidas}/{total}** "
        f"({resolvidas/max(1,total):.1%} da base)\n"
        f"- referencias criadas neste passo: {criadas}\n"
        f"- chaves de prosa sem registro apontando (orfas): {max(0, orfas)}\n"
        f"- origem: {dict(origem)}\n"
        f"- prosa total: {total_bytes/1e6:.1f} MB\n"
        f"- sem prosa: {len(faltando)}\n\n"
        + ("## Sem prosa\n\n" + "\n".join(f"- `{i}`" for i in faltando) if faltando else "")
    )
    return 0 if resolvidas / max(1, total) > 0.98 else 1


if __name__ == "__main__":
    sys.exit(main())
