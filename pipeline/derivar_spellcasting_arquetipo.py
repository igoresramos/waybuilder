#!/usr/bin/env python3
"""
Deriva `grant_spellcasting` -- quem concede CONJURACAO DE ARQUETIPO -- da prosa.

21 dedicacoes prometem conjuracao na propria prosa ("you can cast spells like a
wizard") e nenhuma entrega nada na ficha: `grants` vem vazio de conjuracao em
todas. Sob Free Archetype, que a regra 2 mantem sempre ligada, essa e a rota de
conjuracao mais comum de um personagem nao-conjurador -- e ela era invisivel.

O que este passo NAO faz: inventar a tabela de slots. Ela ja existe no motor
(`RANK_DEDICACAO`), citada verbatim da regra "Spellcasting Archetypes" e usada
desde 2026-07-27 como piso da regra 21. O que faltava era saber QUEM esta na
rota e por qual cadeia.

Regra de emissao, a mesma do 7e e do 7f: **so com o sujeito ancorado em "you"**.
Varredura crua por "spell" nas 226 dedicacoes traz 77; a ancora derruba para as
que realmente conjuram. As quedas sao legitimas -- citam magia para dar
resistencia, para calcular DC, ou para condicionar um feat posterior.

A TRADICAO nao e lista escrita a mao: "cast spells like a wizard" resolve pela
propria base, lendo `spellcasting.tradition` de `wb:class/wizard`.

ORDEM: passo 7g, mesma janela do 7e e 7f -- depois da prosa (5) e depois da
fusao (7).

Spec: specs/2026-07-29-spellcasting-de-arquetipo.md
Entrada: pipeline/base/index.json + pipeline/base/text/*.json
Saida:   index.json enriquecido + base/relatorio_spellcasting_arquetipo.md
"""
import glob
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

TRADICOES = ("arcane", "divine", "occult", "primal")

# "you can cast spells", "you gain a spell repertoire", "you learn to cast
# spontaneous spells". O sujeito e VOCE -- e isso que separa conceder de citar.
#
# O verbo tem de reger SPELLS no plural ou o repertorio/slot: a primeira versao
# aceitava `gain ... spell` e trouxe `Avenger Dedication` ("+1 bonus to saving
# throws against divine spells"), `Blessed One` ("gain the lay on hands devotion
# spell") e `Pure Legion Enforcer` ("gain the Recognize Spell" -- uma acao).
P_CONJURA = re.compile(
    r"\byou\b[^.;]{0,50}?\b(?:cast|casting|learn to cast)\b[^.;]{0,50}?\bspells\b"
    r"|\byou\b[^.;]{0,50}?\bgain\b[^.;]{0,40}?\bspell (?:repertoire|slots?)\b", re.I)

# "bonus to saves against divine spells" fala de magia SOFRIDA, nao conjurada
P_CONTRA = re.compile(r"\bagainst\b[^.;]{0,30}\bspells\b", re.I)

# "cast spells like a wizard" -> a tradicao e a da CLASSE, lida da base
P_COMO_CLASSE = re.compile(r"\blike an? ([a-z][a-z' -]{2,20}?)\b", re.I)
P_TRADICAO = re.compile(r"\b(" + "|".join(TRADICOES) + r")\b", re.I)
P_ESPONTANEO = re.compile(r"\bspontaneous\b|\brepertoire\b", re.I)

# Magia INATA fixa, nao progressao de slots: modelo diferente, fica na divida.
P_INATA = re.compile(r"\binnate\b", re.I)

# Cadeia emprestada: a prosa diz de quem. Sem isto, `spellshot` fica sem cadeia
# apesar de dizer, com todas as letras, que usa a do Wizard.
P_CONTA_COMO = re.compile(
    r"counts? as (?:the |a )?([a-z][a-z' -]{2,24}?) archetype", re.I)


def corpo(texto: str) -> str:
    """So o que vem depois do separador -- antes dele mora o PREREQUISITO."""
    return texto.split("---", 1)[1] if "---" in texto else texto


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    prosa = {}
    for f in glob.glob(f"{BASE}/text/*.json"):
        with open(f, encoding="utf-8") as fh:
            prosa.update(json.load(fh))

    def texto(r):
        t = r.get("text")
        return prosa.get(t, "") if isinstance(t, str) and t.startswith("wb:text/") else ""

    # tradicao por nome de classe, direto da base -- nada escrito a mao
    tradicao_da_classe = {}
    for r in base:
        if r.get("kind") == "class" and isinstance(r.get("spellcasting"), dict):
            nome = " ".join((r.get("name") or "").split()).casefold()
            trad = r["spellcasting"].get("tradition")
            tipo = r["spellcasting"].get("type")
            if nome and trad:
                tradicao_da_classe[nome] = (trad, tipo)

    # cadeia Basic/Expert/Master por arquetipo. O nome varia ("Red Mantis
    # Magic", "Snowcasting"), entao o vinculo e o campo `archetype`, e o padrao
    # de nome so serve para reconhecer o degrau.
    DEGRAU = re.compile(r"^(basic|expert|master)\b", re.I)
    cadeia = {}
    for r in base:
        if r.get("kind") != "feat":
            continue
        m = DEGRAU.match(str(r.get("name") or ""))
        if not m or "spellcasting" not in (r.get("name") or "").casefold():
            continue
        arq = r.get("archetype")
        if arq:
            cadeia.setdefault(arq, {})[m.group(1).lower()] = r["id"]

    arquetipo_por_nome = {
        " ".join((r.get("name") or "").split()).casefold(): r["id"]
        for r in base if r.get("kind") == "archetype"}

    concedem, inatas, sem_tradicao, sem_cadeia = [], [], [], []
    for r in base:
        if "dedication" not in {str(t).lower() for t in (r.get("traits") or [])}:
            continue
        # idempotente: rodar duas vezes nao duplica
        if any("grant_spellcasting" in g for g in (r.get("grants") or [])
               if isinstance(g, dict)):
            continue
        t = corpo(texto(r))
        m = P_CONJURA.search(t)
        if not m:
            continue
        frase = " ".join(m.group(0).split())
        if P_CONTRA.search(frase):
            continue

        # tradicao: explicita na frase, ou a da classe citada em "like a X"
        trad = tipo = None
        mt = P_TRADICAO.search(frase) or P_TRADICAO.search(t[:400])
        mc = P_COMO_CLASSE.search(t[:400])
        if mc and " ".join(mc.group(1).split()).casefold() in tradicao_da_classe:
            trad, tipo = tradicao_da_classe[" ".join(mc.group(1).split()).casefold()]
        elif mt:
            trad = mt.group(1).lower()

        if P_INATA.search(t[:400]) and not trad:
            inatas.append((r, frase))
            continue
        if not trad:
            # tradicao que depende de outra escolha (bloodline, patron) ou que a
            # prosa nao fixa: declarar em vez de arbitrar
            sem_tradicao.append((r, frase))
            continue

        if tipo is None:
            tipo = "spontaneous" if P_ESPONTANEO.search(t[:400]) else "prepared"

        # A classe pode NAO ter tradicao fixa: o Sorcerer guarda em
        # `spellcasting.tradition` a frase "variavel (definida pela escolha de
        # bloodline...)", e a Bruxa o mesmo com patron. Gravar essa prosa num
        # campo de VALOR seria dado sujo; vira escolha declarada, e o motor
        # resolve pelo eixo de subclasse -- ou avisa, como faz com o grau do
        # companheiro.
        eixo = None
        if trad not in TRADICOES:
            m_eixo = re.search(r"\b(bloodline|patron|muse|instinct|order)\b",
                               str(trad), re.I)
            eixo = m_eixo.group(1).lower() if m_eixo else None
            trad = "escolha"

        # cadeia: a do proprio arquetipo, ou a emprestada que a prosa aponta
        arq = r.get("archetype")
        mb = P_CONTA_COMO.search(t)
        if mb:
            emprestada = arquetipo_por_nome.get(
                " ".join(mb.group(1).split()).casefold())
            if emprestada:
                arq = emprestada

        # SEM CADEIA nao ha progressao de slots: a dedicacao pode dar cantrip,
        # magia de foco ou inata, e isso e outro modelo. A cadeia
        # Basic/Expert/Master e o que caracteriza a rota de conjuracao de
        # arquetipo, e e ela que a tabela `RANK_DEDICACAO` do motor descreve.
        degraus = cadeia.get(arq or "")
        if not degraus or "basic" not in degraus:
            sem_cadeia.append((r, frase, trad))
            continue

        g = {"tradicao": trad, "tipo": tipo, "cadeia": arq, "degraus": degraus}
        if eixo:
            g["de"] = eixo

        tinha = bool(r.get("grants") or [])
        r.setdefault("grants", []).append({"grant_spellcasting": g})
        prov = r.setdefault("prov", {})
        prov["grants.grant_spellcasting"] = "derivado:prosa-spellcasting"
        if not tinha:
            prov["grants"] = "derivado:prosa-spellcasting"
        # TERCEIRA ocorrencia do mesmo esquecimento (7e, 7f e aqui): todo passo
        # que enriquece `grants` depois do reconciliador precisa refazer
        # `mechanized`, que a spec v1 define como `bool(grants)` e que so era
        # derivado no passo 2. Quem guarda a invariante e
        # `test_mechanized_e_derivado_de_grants` -- foi ele que achou as tres.
        r["mechanized"] = True
        concedem.append((r, frase, g))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = [
        "# Spellcasting de arquetipo derivado da prosa", "",
        f"- dedicacoes que concedem conjuracao: **{len(concedem)}**",
        f"- so magia INATA fixa (modelo diferente, divida): **{len(inatas)}**",
        f"- prometem magia mas a tradicao depende de outra escolha: **{len(sem_tradicao)}**",
        f"- prometem magia SEM cadeia Basic/Expert/Master (outro modelo): **{len(sem_cadeia)}**",
        f"- arquetipos com cadeia Basic/Expert/Master mapeada: **{len(cadeia)}**", "",
        "A tabela de slots NAO esta aqui: ela vive no motor (`RANK_DEDICACAO`), "
        "citada verbatim da regra oficial. Este passo diz QUEM esta na rota.", "",
        "## Concedem", "",
        "| dedicacao | tradicao | tipo | cadeia | degraus | frase |",
        "|---|---|---|---|---|---|",
    ]
    for r, frase, g in sorted(concedem, key=lambda x: x[0].get("name") or ""):
        rel.append(f"| {r.get('name')} | {g['tradicao']}"
                   f"{' (' + g['de'] + ')' if g.get('de') else ''} | {g['tipo']} | "
                   f"{g.get('cadeia', '-')} | {len(g.get('degraus') or {})} | "
                   f"{frase[:60]} |")

    rel += ["", "## Magia inata fixa -- divida declarada", "",
            "| dedicacao | frase |", "|---|---|"]
    for r, frase in sorted(inatas, key=lambda x: x[0].get("name") or ""):
        rel.append(f"| {r.get('name')} | {frase[:70]} |")

    rel += ["", "## Sem cadeia Basic/Expert/Master -- cantrip, foco ou inata", "",
            "| dedicacao | tradicao | frase |", "|---|---|---|"]
    for r, frase, trad in sorted(sem_cadeia, key=lambda x: x[0].get("name") or ""):
        rel.append(f"| {r.get('name')} | {trad} | {frase[:60]} |")

    rel += ["", "## Tradicao depende de outra escolha -- nao arbitrado", "",
            "| dedicacao | frase |", "|---|---|"]
    for r, frase in sorted(sem_tradicao, key=lambda x: x[0].get("name") or ""):
        rel.append(f"| {r.get('name')} | {frase[:70]} |")

    with open(f"{BASE}/relatorio_spellcasting_arquetipo.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"spellcasting de arquetipo: {len(concedem)} concedem, "
          f"{len(sem_cadeia)} sem cadeia (outro modelo), "
          f"{len(sem_tradicao)} sem tradicao fixa")
    print(f"-> {BASE}/relatorio_spellcasting_arquetipo.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
