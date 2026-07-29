#!/usr/bin/env python3
"""
Compara o que o Waybuilder OFERECE num slot com o que o Pathbuilder oferece.

A tese, do review adversarial: o Pathbuilder vale como oraculo de
COMPORTAMENTO. Ele nao e fonte de regra -- a fonte e o livro --, mas e um
segundo implementador do mesmo RAW, e onde os dois discordam ha o que olhar.

Entrada: o JSON colhido por `app/verificacao/sonda-pathbuilder.mjs`, que le a
lista real da tela do Pathbuilder rodando local.

O que o relatorio separa, e por que a separacao importa mais que o placar:

  - **so no Pathbuilder** -- candidato que o Waybuilder nao oferece. Suspeita de
    buraco na base ou de elegibilidade de slot estreita demais.
  - **so no Waybuilder** -- pode ser acerto NOSSO (a houserule muda o que cabe
    no slot) ou ruido de fonte. Nao e defeito automatico.
  - **divergencia de disponibilidade** -- os dois oferecem, mas discordam se o
    personagem atende. Aqui mora o defeito de PREDICADO, que e o mais caro de
    achar por leitura.

Uso: python3 motor/comparar_pathbuilder.py docs/comparacao/pathbuilder-*.json
"""
import glob
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from motor import Base, Personagem   # noqa: E402

# a sonda so sabe montar o default do Pathbuilder: Human / Barkeep / Fighter
DEFAULT = {
    "Fighter": ("wb:class/fighter", "wb:ancestry/human", "wb:background/barkeep"),
}


def personagem_equivalente(base: Base, classe: str, nivel: int) -> Personagem:
    cid, ancestria, background = DEFAULT[classe]
    escolhas = [
        {"em": "criacao", "slot": "ancestralidade", "pega": ancestria},
        {"em": "criacao", "slot": "background", "pega": background},
    ]
    for n in range(1, nivel + 1):
        escolhas.append({"em": n, "slot": "nivel_de_classe", "pega": cid})
    return Personagem({"esquema": "waybuilder/personagem@1", "escolhas": escolhas}, base)


def norm(nome: str) -> str:
    """Nome comparavel entre os dois apps.

    Tres fontes de ruido, todas medidas no primeiro relatorio e nenhuma delas
    divergencia de regra:

      - o sufixo de desambiguacao que NOS colocamos ao desmembrar colisao de
        identidade: `Guardian's Deflection (Fighter)` e o mesmo feat que o
        `Guardian's Deflection` deles;
      - apostrofo tipografico e caixa: `Needle In The God's Eyes` x
        `Needle in the Gods' Eyes`;
      - pontuacao solta.

    Sem isto o relatorio enche de falso positivo e esconde o achado real.
    """
    texto = re.sub(r"\s*\([^)]*\)\s*$", "", str(nome or ""))
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.replace("\u2019", "").replace("'", "")
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", texto.casefold()).split())


# O modal do Pathbuilder tem abas, e cada uma recorta um pedaco do MESMO slot.
# Comparar a lista inteira contra a nossa mente nos dois sentidos, entao cada
# aba e comparada com o subconjunto equivalente dos nossos candidatos.
#
# `Archetype Class Feats` fica VAZIA enquanto o personagem nao tem dedicacao --
# e ai esta a diferenca de design, nao um defeito: pelo principio zero nos
# mostramos esses feats marcados, e o Pathbuilder os esconde ate a dedicacao
# existir. Por isso ela nao entra na comparacao com placar.
ABAS = {
    "Class Feats": lambda base, p, r: bool(
        {t.lower() for t in (r.get("traits") or [])}
        & {str(base.get(c).get("name") or "").lower() for c in p.ordem_de_classe}),
    "Dedication Feats": lambda base, p, r: "dedication" in
        {t.lower() for t in (r.get("traits") or [])},
}


def comparar(base: Base, sonda: dict, aba: str | None = None) -> dict:
    p = personagem_equivalente(base, sonda["classe"], sonda["nivel"])
    todos = p.candidatos(sonda["slot"], sonda["nivel"])
    if aba:
        cabe = ABAS[aba]
        todos = [c for c in todos if cabe(base, p, base.opcional(c["id"]) or {})]
    nossos = {norm(c["nome"]): c for c in todos}
    deles = {norm(o["nome"]): o for o in (sonda.get("abas", {}).get(aba)
                                          if aba else sonda["opcoes"])}

    so_deles = sorted(deles[k]["nome"] for k in deles.keys() - nossos.keys())
    so_nossos = sorted(nossos[k]["nome"] for k in nossos.keys() - deles.keys())

    divergem = []
    for k in nossos.keys() & deles.keys():
        if nossos[k]["atende"] != deles[k]["atende"]:
            divergem.append({
                "nome": nossos[k]["nome"],
                "waybuilder": nossos[k]["atende"],
                "pathbuilder": deles[k]["atende"],
                "motivos": nossos[k]["motivos"],
            })
    divergem.sort(key=lambda d: d["nome"])

    return {
        "slot": f"{sonda['classe']} {sonda['nivel']} / {sonda['slot']}"
                + (f" [{aba}]" if aba else ""),
        "waybuilder": len(nossos), "pathbuilder": len(deles),
        "em_comum": len(nossos.keys() & deles.keys()),
        "so_no_pathbuilder": so_deles,
        "so_no_waybuilder": so_nossos,
        "divergencia_de_disponibilidade": divergem,
    }


def main() -> int:
    alvos = sys.argv[1:] or sorted(glob.glob(
        os.path.join(AQUI, "..", "docs", "comparacao", "pathbuilder-*.json")))
    if not alvos:
        print("nenhum JSON de sonda -- rode app/verificacao/sonda-pathbuilder.mjs")
        return 1

    base = Base()
    problemas = 0
    for caminho in alvos:
        with open(caminho, encoding="utf-8") as fh:
            sonda = json.load(fh)
        if sonda["classe"] not in DEFAULT:
            print(f"pulado (classe sem equivalente montado): {sonda['classe']}")
            continue

        relatorios = ([comparar(base, sonda, aba) for aba in ABAS
                       if aba in (sonda.get("abas") or {})]
                      or [comparar(base, sonda)])
        for r in relatorios:
            problemas += imprimir(r)

        saida = caminho.replace("pathbuilder-", "comparacao-")
        with open(saida, "w", encoding="utf-8") as fh:
            json.dump(relatorios, fh, ensure_ascii=False, indent=2)
        print(f"   -> {os.path.relpath(saida)}")
    print(f"\ntotal de pontos a olhar: {problemas}")
    return 0


def imprimir(r: dict) -> int:
    """Imprime um relatorio e devolve quantos pontos ele levanta."""
    problemas = 0
    print(f"\n== {r['slot']}")
    print(f"   waybuilder {r['waybuilder']} | pathbuilder {r['pathbuilder']} "
          f"| em comum {r['em_comum']}")
    for chave, rotulo in (("so_no_pathbuilder", "so no Pathbuilder"),
                          ("so_no_waybuilder", "so no Waybuilder")):
        itens = r[chave]
        if itens:
            problemas += len(itens)
            print(f"   {rotulo} ({len(itens)}): {', '.join(itens[:12])}"
                  + (" ..." if len(itens) > 12 else ""))
    if r["divergencia_de_disponibilidade"]:
        problemas += len(r["divergencia_de_disponibilidade"])
        print(f"   discordam se atende ({len(r['divergencia_de_disponibilidade'])}):")
        for d in r["divergencia_de_disponibilidade"][:10]:
            print(f"     {d['nome']}: wb={d['waybuilder']} pb={d['pathbuilder']}"
                  + (f"  -- {d['motivos'][0]}" if d["motivos"] else ""))
    return problemas


if __name__ == "__main__":
    sys.exit(main())
