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
    # dump completo do indice (dump_aon.py) -- 43.686 docs, a fonte principal
    for f in glob.glob(f"{BRUTO}/aon_dump/*.json"):
        if os.path.basename(f).startswith("_"):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for r in (d if isinstance(d, list) else []):
            if isinstance(r, dict) and r.get("id"):
                t = limpar(r.get("text") or r.get("summary") or "")
                if t:
                    idx[str(r["id"])] = t
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


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comum                                          # noqa: E402

CLONE = comum.packs_foundry(BRUTO) or f"{BRUTO}/foundry_repo/packs/pf2e"


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
    for f in glob.glob(f"{BRUTO}/aon_dump/*.json") + glob.glob(f"{BRUTO}/aon_*.json"):
        if os.path.basename(f).startswith("_"): continue
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
            # 907 registros mono-fonte nunca ganharam referencia do extrator
            # (768 equipment, 87 weapon, 16 feat). Sem referencia eles ficavam
            # fora ate do denominador da metrica -- invisiveis duas vezes. Se ha
            # prosa recuperavel pelo nome, a referencia nasce aqui.
            slug = r["id"].split("/", 1)[-1]
            ref = f"wb:text/{r.get('kind')}/{slug}"
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
            # quem resolve a prosa sabe de onde ela veio -- registrar aqui e o
            # que faltava para o portao 1 (2.694 registros com `text` preenchido
            # e sem `prov.text`). A prov e do texto de fato emitido, nao do que
            # o extrator supos.
            r.setdefault("prov", {})["text"] = de
        else:
            faltando.append(r["id"])
            r.pop("text", None)          # referencia sem prosa e referencia pendurada

    # A prosa vive no sidecar; o indice guarda o PONTEIRO. Quatro extratores
    # (magias, rituais, equipamento, relicos_idiomas) tambem gravam a prosa
    # INLINE num campo `texto`, e os dois conviviam: 1.858 registros carregavam
    # a mesma prosa duas vezes, somando 1,77 MB -- 12,7% do indice. Nao e so
    # peso: sao duas copias que podem divergir, e a partir dai ninguem sabe qual
    # vale. Aqui, depois de o sidecar estar gravado com a prosa, a copia inline
    # sai. Removida SO quando o ponteiro resolve de fato -- senao seria perder
    # a unica prosa que o registro tem.
    # OS SIDECARS PRIMEIRO. A remocao da copia inline (abaixo) so pode
    # acontecer depois que a prosa estiver em disco -- na ordem inversa, uma
    # falha entre as duas escritas apagaria a unica prosa do registro.
    os.makedirs(f"{BASE}/text", exist_ok=True)
    total_bytes = 0
    for kind, mapa in textos.items():
        caminho = f"{BASE}/text/{kind}.json"
        json.dump(mapa, open(caminho, "w"), ensure_ascii=False, separators=(",", ":"))
        total_bytes += os.path.getsize(caminho)
        print(f"  {kind:14} {len(mapa):>5} textos  {os.path.getsize(caminho)/1e6:.2f} MB")

    # Quatro extratores (magias, rituais, equipamento, relicos_idiomas) gravam
    # a prosa INLINE num campo `texto`, e ela convivia com o ponteiro: 1.858
    # registros carregavam a mesma prosa duas vezes, 1,77 MB -- 12,7% do
    # indice. Nao e so peso: sao duas copias que podem divergir, e a partir dai
    # ninguem sabe qual vale. Sai a copia, fica o ponteiro -- e so quando o
    # ponteiro resolve DE FATO no arquivo recem-gravado.
    escritos = {kind: json.load(open(f"{BASE}/text/{kind}.json"))
                for kind in textos}
    inline_removido = 0
    for r in base:
        if not r.get("texto"):
            continue
        ref, kind = r.get("text"), r.get("kind")
        if isinstance(ref, str) and escritos.get(kind, {}).get(ref):
            r.pop("texto", None)
            inline_removido += 1

    # o index passa a carregar as referencias criadas nesta passada
    json.dump(base, open(f"{BASE}/index.json", "w"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"referencias de texto criadas para registros que nao tinham: {criadas}")
    if inline_removido:
        print(f"prosa inline duplicada removida do indice: {inline_removido} "
              f"registros (a prosa fica no sidecar)")

    # portao: nenhuma referencia pendurada.
    # O denominador e a BASE INTEIRA, nao as referencias existentes. Dividir por
    # `esperadas` reportava 100% enquanto 907 registros nao tinham prosa: quem
    # nao tem referencia nenhuma nunca entrava na conta e por isso nunca
    # aparecia como falta. A metrica mentia exatamente sobre o buraco que
    # deveria denunciar.
    resolvidas = sum(len(m) for m in textos.values())
    esperadas = sum(1 for r in base if isinstance(r.get("text"), str)
                    and r["text"].startswith("wb:text/"))
    sem_referencia = len(base) - esperadas
    cobertura = resolvidas / max(1, len(base))
    print(f"\nreferencias resolvidas: {resolvidas}/{esperadas}")
    print(f"cobertura sobre a base: {resolvidas}/{len(base)} ({cobertura:.1%})")
    print(f"registros sem referencia de texto: {sem_referencia}")
    print(f"origem: {dict(origem)}")
    print(f"prosa total: {total_bytes/1e6:.1f} MB")
    if faltando:
        print(f"SEM PROSA ({len(faltando)}): {faltando[:12]}")

    open(f"{BASE}/relatorio_textos.md", "w").write(
        "# Emissao de prosa\n\n"
        f"- cobertura sobre a base: **{resolvidas}/{len(base)}** ({cobertura:.1%})\n"
        f"- referencias resolvidas: {resolvidas}/{esperadas}\n"
        f"- registros sem referencia de texto: {sem_referencia}\n"
        f"- origem: {dict(origem)}\n"
        f"- prosa total: {total_bytes/1e6:.1f} MB\n"
        f"- sem prosa: {len(faltando)}\n\n"
        + ("## Sem prosa\n\n" + "\n".join(f"- `{i}`" for i in faltando) if faltando else "")
    )
    return 0 if cobertura > 0.98 else 1


if __name__ == "__main__":
    sys.exit(main())
