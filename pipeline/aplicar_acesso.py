#!/usr/bin/env python3
"""
Le `access` do AoN e emite `acesso` na base.

Centenas de registros incomuns so estao disponiveis para quem tem certa
filiacao -- "Member of the Pathfinder Society", "Knights of Lastwall have access
to this feat", "Tian Xia origin" --, e e isso que torna a raridade `uncommon`.
A base nao carregava nada disso.

NAO E PROSA. O item 22 propunha varrer o texto atras da linha `Access`, e a
varredura e ruim: a palavra `access` aparece em 716 registros, e boa parte e
ruido (`wb:class/oracle` casa por "Your mystery offers you strange ACCESS to
spells"). O AoN publica `access` como CAMPO, em 1.010 documentos -- lacuna de
leitura, a mesma classe do `alvos`/`salvaguarda` do item 79.

TEXTO VERBATIM, sem parse: o campo e para LER na ficha. Transformar em estrutura
e outra decisao, e ela precisa de um consumidor -- hoje nada no motor pergunta
"de que organizacao voce e".

NAO VIRA REQUISITO. Principio zero: filiacao sugere, nunca bloqueia -- quem joga
numa mesa de Golarion pode ser da Pathfinder Society, e o construtor nao tem como
saber.

ORDEM: depois da reconciliacao, porque o join e por `xref.aon`.

Spec: specs/2026-07-30-acesso-por-filiacao.md
Entrada: pipeline/base/index.json + pipeline/dados_brutos/aon*.json
Saida:   index.json enriquecido + base/relatorio_acesso.md
"""
import collections
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"
BRUTOS = f"{AQUI}/dados_brutos"


def acesso_do_aon() -> dict:
    """id do doc -> texto de `access`, ja normalizado em espaco."""
    saida = {}
    for caminho in glob.glob(f"{BRUTOS}/aon*.json") + glob.glob(f"{BRUTOS}/aon_dump/*.json"):
        try:
            with open(caminho, encoding="utf-8") as fh:
                dados = json.load(fh)
        except Exception:
            continue
        docs = dados if isinstance(dados, list) else dados.get("docs") or []
        for doc in docs:
            if not isinstance(doc, dict) or not doc.get("access"):
                continue
            texto = " ".join(str(doc["access"]).split())
            if texto:
                saida[doc.get("id")] = texto
    return saida


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    tabela = acesso_do_aon()
    por_kind = collections.Counter()
    formas = collections.Counter()
    for reg in base:
        aon = (reg.get("xref") or {}).get("aon")
        texto = tabela.get(aon) if aon else None
        if not texto or reg.get("acesso") == texto:
            continue
        reg["acesso"] = texto
        reg.setdefault("prov", {})["acesso"] = "aon"
        por_kind[reg.get("kind")] += 1
        formas[texto[:60]] += 1

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = [
        "# Condicao de acesso, lida do campo `access` do AoN", "",
        f"- docs do AoN com `access`: **{len(tabela)}**",
        f"- registros da base que ganharam `acesso`: **{sum(por_kind.values())}**",
        "",
        "Filiacao SUGERE, nunca bloqueia: o campo informa e nao entra em "
        "`requires`. Quem joga numa mesa de Golarion pode ser da Pathfinder "
        "Society, e o construtor nao tem como saber.", "",
        "## Por kind", "", "| kind | registros |", "|---|---:|",
    ]
    for kind, n in por_kind.most_common():
        rel.append(f"| {kind} | {n} |")
    rel += ["", "## Formas mais comuns", "", "| inicio do texto | registros |",
            "|---|---:|"]
    for forma, n in formas.most_common(15):
        rel.append(f"| {forma} | {n} |")
    with open(f"{BASE}/relatorio_acesso.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"acesso: {sum(por_kind.values())} registros de {len(tabela)} docs "
          f"do AoN com o campo")
    print(f"-> {BASE}/relatorio_acesso.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
