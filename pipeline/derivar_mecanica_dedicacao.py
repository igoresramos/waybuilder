#!/usr/bin/env python3
"""
Deriva a mecanica das dedicacoes a partir da PROSA OFICIAL.

61 das 226 dedicacoes chegam com `grants` vazio -- o Foundry nao escreveu rule
element para elas, e o AoN nunca traz mecanica estruturada. A leitura anterior
era que so o Pathbuilder resolveria isso. Nao e: a prosa que ja temos DIZ o que
a dedicacao concede, e a Paizo escreve isso em formula quase fixa.

    "You become trained in Occultism; if you were already trained, you instead
     become an expert."
    "You gain the Blessed One's Lay on Hands devotion spell."

O que este passo NAO faz, de proposito: adivinhar. Ele so emite quando (a) o
sujeito da frase e VOCE, e (b) o alvo resolve para um registro que existe na
base. As duas guardas nasceram de falsos positivos reais:

  - `Animal Trainer Dedication` diz "This trained animal is trained in
    Performance" -- sujeito e o COMPANHEIRO, nao o personagem. Sem a ancora em
    "you", o passo dava Performance ao jogador.
  - o cabecalho traz "Prerequisites Trained in Nature". E requisito, nao
    concessao. Por isso a leitura comeca depois do separador `---`.

Categorias medidas nas 61 (uma dedicacao pode cair em mais de uma):
    proficiencia 17 | modificador 17 | companheiro 16 | spellcasting 14 |
    concede item nomeado 9 | nenhuma 10

Este passo cobre as DUAS primeiras colunas em que o motor ja sabe agir:
proficiencia/treino de pericia e feat concedido nomeado. Companheiro,
spellcasting de arquetipo e modificador numerico exigem modelo que o motor
ainda nao tem, e continuam na divida -- listados no relatorio, nao inventados
aqui.

ORDEM: roda depois de `emitir_textos.py` (precisa da prosa) e depois da fusao
(nao enriquece registro que vai ser absorvido). Ver a licao em LESSONS.md sobre
passo que conserta rodando antes do passo que quebra.

Entrada: pipeline/base/index.json + pipeline/base/text/*.json
Saida:   index.json enriquecido + base/relatorio_mecanica_dedicacao.md
"""
import glob
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

RANKS = ("trained", "expert", "master", "legendary")

# Defesas e sentidos entram em `proficiency`; pericia entra em `skill_training`.
# A distincao e do motor, nao da prosa.
DEFESAS = {"perception", "fortitude", "reflex", "will", "class dc"}

# "You become trained in X", "You're trained in X", "You gain the trained
# proficiency rank in X". A ancora inicial em `you` e o que impede a frase do
# companheiro ("This trained animal is trained in Performance") de entrar.
P_PROF = re.compile(
    r"\byou(?:'re| are| become| becomes| gain)\b[^.;]{0,40}?"
    r"\b(" + "|".join(RANKS) + r")\b"
    r"(?: proficiency)?(?: rank)? in ([^.;]{2,80})", re.I)

# "You gain the Lay on Hands devotion spell", "You gain the Cast Down feat".
P_ITEM = re.compile(
    r"\byou gain the ([A-Z][A-Za-z'’\- ]{2,40}?) "
    r"(feat|action|activity|spell|cantrip|focus spell|devotion spell)\b")

# Presenca destas marca a dedicacao como divida declarada, nunca derivada.
P_COMPANHEIRO = re.compile(
    r"\b(?:young )?(?:animal companion|eidolon|familiar|construct companion|"
    r"drake|minion)\b", re.I)
P_SPELLCASTING = re.compile(
    r"\b(?:spell slots?|spell repertoire|spellcasting benefits)\b", re.I)


def corpo(texto: str) -> str:
    """So o que vem depois do separador -- antes dele mora o PREREQUISITO."""
    return texto.split("---", 1)[1] if "---" in texto else texto


def limpar_alvo(bruto: str):
    """`Nature and Survival` -> ['nature', 'survival']. Corta a subordinada.

    Devolve `None` quando a frase oferece ESCOLHA. `You become trained in
    Deception or Diplomacy` concede UMA das duas, e emitir as duas daria ao
    jogador uma pericia que a regra nao deu. Escolha nao e derivavel aqui --
    o motor precisa de um grant que ofereca opcoes, e o vocabulario nao tem.
    """
    bruto = re.split(r"\b(?:if|unless|instead|when|and you|as well as)\b",
                     bruto, 1, re.I)[0]
    if re.search(r"\bor\b", bruto, re.I):
        return None
    partes = re.split(r",| and ", bruto, flags=re.I)
    return [" ".join(p.split()).strip(" .;:").casefold()
            for p in partes if p.strip()]


def main() -> int:
    with open(f"{BASE}/index.json", encoding="utf-8") as fh:
        base = json.load(fh)

    prosa = {}
    for f in glob.glob(f"{BASE}/text/*.json"):
        with open(f, encoding="utf-8") as fh:
            prosa.update(json.load(fh))

    # nome -> id, para os dois kinds que este passo sabe resolver
    pericias, feats = {}, {}
    for r in base:
        chave = " ".join((r.get("name") or "").split()).casefold()
        # so as 17 canonicas. O kind `skill` tem 33 registros: as 16 restantes
        # sao Kingdom Skills do Kingmaker (`Agriculture`, `Defense`,
        # `Engineering`...), que nao sao pericia de personagem. `attribute` e o
        # que separa os dois grupos -- so a pericia de personagem tem atributo.
        if r.get("kind") == "skill" and r.get("attribute"):
            pericias[chave] = r["id"]
        elif r.get("kind") in ("feat", "action"):
            feats.setdefault(chave, r["id"])

    dedicacoes = [r for r in base
                  if "dedication" in {t.lower() for t in (r.get("traits") or [])}
                  and not (r.get("grants") or [])]

    derivadas, divida, sem_nada = [], [], []
    for r in dedicacoes:
        texto = corpo(prosa.get(r.get("text") or "", ""))
        grants, provas = [], []

        # Um rank por alvo, o PRIMEIRO que a prosa cita. `Vehicle Mechanic` diz
        # "become an expert in Crafting" e mais adiante fala de master; o
        # segundo e condicional a nivel, e emitir os dois daria mestria de
        # graca. O condicional vai para a divida, nao para o dado.
        ja_concedido, condicionais = set(), []
        for rank, alvo_bruto in P_PROF.findall(texto):
            rank = rank.casefold()
            alvos = limpar_alvo(alvo_bruto)
            if alvos is None:
                condicionais.append(f"escolha: {' '.join(alvo_bruto.split())[:50]}")
                continue
            for alvo in alvos:
                if alvo in ja_concedido:
                    condicionais.append(f"{rank} in {alvo} (rank posterior)")
                    continue
                if alvo in DEFESAS or alvo in pericias:
                    ja_concedido.add(alvo)
                if alvo in DEFESAS:
                    grants.append({"proficiency": {alvo.replace(" ", "_"): rank}})
                    provas.append(f"{rank} in {alvo}")
                elif alvo in pericias:
                    # `skill_training` so fala de treino; rank maior vira
                    # `proficiency` nomeada, que e o que o motor consome
                    if rank == "trained":
                        grants.append({"skill_training": {"auto": [alvo]}})
                    else:
                        grants.append({"proficiency": {alvo: rank}})
                    provas.append(f"{rank} in {alvo}")

        for nome, especie in P_ITEM.findall(texto):
            chave = " ".join(nome.split()).casefold()
            if chave in feats:
                grants.append({"grant_feat": [feats[chave]]})
                provas.append(f"gain the {nome} {especie}")

        # deduplica preservando ordem -- a prosa repete a concessao no resumo
        vistos, limpo = set(), []
        for g in grants:
            chave = json.dumps(g, sort_keys=True)
            if chave not in vistos:
                vistos.add(chave)
                limpo.append(g)
        provas = list(dict.fromkeys(provas))

        if limpo:
            r["grants"] = limpo
            r.setdefault("prov", {})["grants"] = "derivado:prosa-dedicacao"
            # mesma razao do passo 7f: `mechanized == bool(grants)` e derivado
            # pelo reconciliador, que rodou muito antes deste enriquecimento.
            # Sem isto, 7 dedicacoes saem com `grants` cheio e `mechanized:
            # false` -- o campo vira declaracao solta, que e o que o teste de
            # invariante existe para pegar.
            r["mechanized"] = True
            derivadas.append((r, provas, condicionais))
        else:
            marcas = list(condicionais)
            if P_COMPANHEIRO.search(texto):
                marcas.append("companheiro")
            if P_SPELLCASTING.search(texto):
                marcas.append("spellcasting")
            (divida if marcas else sem_nada).append((r, marcas))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = [
        "# Mecanica de dedicacao derivada da prosa", "",
        f"- dedicacoes sem `grants` na entrada: **{len(dedicacoes)}**",
        f"- mecanizadas aqui: **{len(derivadas)}**",
        f"- divida declarada (modelo que o motor nao tem): **{len(divida)}**",
        f"- sem padrao reconhecido: **{len(sem_nada)}**", "",
        "Cada linha traz a FRASE que justifica a concessao. Divergencia entre a "
        "frase e o `grants` e defeito deste passo, nao do dado.", "",
        "## Derivadas", "",
        "| dedicacao | concede | frase na prosa | nao derivado |",
        "|---|---|---|---|",
    ]
    for r, provas, cond in sorted(derivadas, key=lambda x: x[0]["name"]):
        resumo = "; ".join(json.dumps(g, ensure_ascii=False) for g in r["grants"])
        rel.append(f"| {r['name']} | `{resumo}` | {'; '.join(provas)} | "
                   f"{'; '.join(cond) or '-'} |")

    rel += ["", "## Divida declarada -- exige modelo novo no motor", "",
            "| dedicacao | o que a prosa concede |", "|---|---|"]
    for r, marcas in sorted(divida, key=lambda x: x[0]["name"]):
        rel.append(f"| {r['name']} | {', '.join(marcas)} |")

    rel += ["", "## Sem padrao reconhecido -- revisar a mao", ""]
    rel += [f"- {r['name']}" for r, _ in sorted(sem_nada, key=lambda x: x[0]["name"])]

    with open(f"{BASE}/relatorio_mecanica_dedicacao.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    print(f"mecanica de dedicacao: {len(derivadas)} derivadas da prosa, "
          f"{len(divida)} divida declarada, {len(sem_nada)} sem padrao "
          f"(de {len(dedicacoes)})")
    print(f"-> {BASE}/relatorio_mecanica_dedicacao.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
