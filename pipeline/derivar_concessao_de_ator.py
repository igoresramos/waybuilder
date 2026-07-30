#!/usr/bin/env python3
"""
Deriva `grant_actor` -- quem concede COMPANHEIRO ANIMAL -- da prosa oficial.

O motor ja sabe montar a ficha do companheiro inteira (cap de nivel, maturidade,
Specialized, HP, AC, ataques). O que faltava era ANTES disso: nenhum feat da
base dizia "eu concedo um companheiro", entao o ator so entrava por
`doc["atores"]` escrito a mao e pegar `Animal Companion` no nivel 1 nao mudava
nada na ficha.

Regra de emissao, a mesma do passo de dedicacao: **so com o sujeito ancorado em
"you"**. Uma busca crua por "animal companion" traz 23 registros; a ancora
derruba para 12, e as 11 quedas sao todas legitimas:

  - `Captain Dedication` e `Necrologist Dedication` citam companheiro para
    PROIBI-LO ("you can never take a feat ... that grants an animal companion")
  - `Reincarnated Companion`, `Heal Companion`, `Fell Rider`, `Swift Paragon`,
    `Storied Companion` falam do companheiro que voce JA tem
  - `Dragon Grip` da ACESSO a especie Riding Drake, nao um companheiro -- outro
    modelo, que nao existe no vocabulario; vai para a divida

ORDEM: roda em 7f, depois da prosa (5) e depois da fusao (7), ao lado do
`derivar_mecanica_dedicacao.py`. Ver a licao em LESSONS.md sobre passo que
enriquece rodando antes do passo que reescreve.

Spec: specs/2026-07-29-companheiro-concedido.md
Entrada: pipeline/base/index.json + pipeline/base/text/*.json
Saida:   index.json enriquecido + base/relatorio_concessao_de_ator.md
"""
import glob
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = f"{AQUI}/base"

# "You gain the service of a young animal companion", "You gain a young animal
# companion", "you gain a wolf as an animal companion". O sujeito e VOCE e o
# verbo e de aquisicao -- e isso que separa concessao de mencao.
P_CONCEDE = re.compile(
    r"\byou\s+(?:gain|get|acquire)\b[^.;]{0,90}?\banimal companion\b", re.I)

# Frase que PROIBE. Aparece dentro de uma sentenca que tambem casaria o padrao
# de cima ("...you can never take a feat or class feature that grants an animal
# companion"), entao precisa vetar o registro inteiro.
P_PROIBE = re.compile(r"\b(?:never|can't|cannot|precludes|instead of)\b"
                      r"[^.;]{0,90}?\banimal companion\b", re.I)

# Concessao de ACESSO, nao de companheiro: "You gain access to the Riding Drake
# animal companion" (Dragon Grip) libera a especie para quem ja tem companheiro.
# `access` nao existe no vocabulario de `grants`; vai para a divida.
P_ACESSO = re.compile(r"\byou\s+gain\s+access\s+to\b", re.I)

# Divida: concede companheiro que NAO e animal. Cada um tem stat block proprio
# e nenhum deles esta na base -- inventar seria pior que declarar a falta.
P_OUTRO_ATOR = re.compile(
    r"\byou\s+(?:gain|get|acquire)\b[^.;]{0,60}?"
    r"\b(construct companion|undead companion)\b", re.I)


# Familiar e eidolon. O ARTIGO INDEFINIDO e o que separa conceder de mencionar:
# as 18 `lesson` e as 16 `patron` dizem "You gain the X hex, and your familiar
# learns Y", que pressupoe o familiar em vez de dar um. Sem o artigo o padrao
# traz 68 registros e a maioria e ruido; com ele, 15 e todos legitimos.
P_FAMILIAR = re.compile(
    r"\byou\s+(?:also\s+)?(?:gain|get|acquire)\s+(?:the\s+service\s+of\s+)?"
    r"an?\s+(?:[a-z\- ]{0,30}\s)?familiar\b", re.I)

# "You gain an eidolon". Derruba os dois falsos positivos, que dizem "You gain
# an EVOLUTION FEAT for your eidolon" -- concedem feat, nao ator.
P_EIDOLON = re.compile(
    r"\byou\s+(?:also\s+)?(?:gain|get|acquire)\s+an?\s+"
    r"(?:[a-z\- ]{0,30}\s)?eidolon\b", re.I)

# A rota da CLASSE nao passa por prosa. Bruxa e Invocador nao dizem "you gain a
# familiar" em lugar nenhum: concedem uma class-feature que se chama Familiar e
# Eidolon, e a progressao ja esta estruturada. Dado estruturado tem precedencia
# sobre prosa no resto do pipeline, e aqui tambem.
FEATURE_DE_ATOR = {
    "wb:class-feature/familiar-witch": ("familiar", "familiar-specific"),
    "wb:class-feature/eidolon": ("eidolon", "eidolon"),
}


# A fonte declara as PROPRIAS excecoes a regra de um ator por vez: "Contrary to
# the usual rules for animal companions, this feat can grant you a SECOND animal
# companion" (Beastmaster). Sao 6 dos 30 concessores -- Beastmaster, Drake
# Rider, Faithful Steed, Mammoth Lord, Emissary Familiar e Familiar (Witch).
# Sem esta marca, uma regra geral de exclusao reprovaria os seis, e com ela a
# regra vale por padrao e cede onde o livro manda.
# Spec: `specs/2026-07-30-segundo-ator.md`
P_ADICIONAL = re.compile(
    r"\b(?:second|additional|another|more than one)\s+"
    r"(?:young\s+)?(?:animal companion|familiar|eidolon)\b", re.I)


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

    # nome da especie -> id, para resolver a citacao nominal
    especies = {}
    for r in base:
        if r.get("kind") == "animal-companion":
            especies[" ".join((r.get("name") or "").split()).casefold()] = r["id"]

    # Nome da especie -> regex de palavra inteira. A citacao nominal na prosa
    # e procurada pelos 113 nomes que a base TEM, e nao por estrutura de frase:
    # "a young riding drake, riding dragonet, or another animal companion" tem
    # duas especies e so uma delas vem depois de "young".
    padrao_especie = [
        (re.compile(r"\b" + re.escape(nome) + r"\b", re.I), ident)
        for nome, ident in sorted(especies.items(), key=lambda kv: -len(kv[0]))]

    concedem, divida, proibem, acesso = [], [], [], []
    outros = []   # familiar e eidolon, que tem relatorio proprio
    for r in base:
        if r.get("kind") not in ("feat", "class-feature"):
            continue
        # idempotente: rodar duas vezes sobre a mesma base nao duplica a
        # concessao (o passo pode ser chamado a mao para conferir o relatorio)
        if any("grant_actor" in g for g in (r.get("grants") or [])
               if isinstance(g, dict)):
            continue
        texto = corpo(prosa.get(r.get("text") or "", ""))
        if not texto:
            continue

        outro = P_OUTRO_ATOR.search(texto)
        if outro:
            divida.append((r, outro.group(1).lower()))
            continue

        # familiar e eidolon antes do companheiro: sao padroes disjuntos, e
        # ordem so importa para nao pagar o regex maior a toa.
        # Spec: `specs/2026-07-30-familiar-e-eidolon-concedidos.md`
        # o preenchedor entre o artigo e o substantivo aceita adjetivo
        # ("a tiny crocodile as a familiar"), mas nao pode engolir OUTRO
        # substantivo: "You gain an evolution FEAT for YOUR eidolon" concede
        # feat, nao ator, e casava porque "evolution feat for your " cabia no
        # preenchedor. `feat` e `your` dentro do trecho reprovam o casamento.
        def _concessao(pad):
            m = pad.search(texto)
            if not m:
                return None
            return None if re.search(r"\b(feat|your)\b", m.group(0), re.I) else m

        outro_tipo, m_outro = None, None
        m_outro = _concessao(P_FAMILIAR)
        if m_outro:
            outro_tipo = ("familiar", "familiar-specific")
        else:
            m_outro = _concessao(P_EIDOLON)
            if m_outro:
                outro_tipo = ("eidolon", "eidolon")
        if outro_tipo:
            tipo, escolhe = outro_tipo
            ga = {"tipo": tipo, "escolhe": escolhe}
            if P_ADICIONAL.search(texto):
                ga["adicional"] = True
            r.setdefault("grants", []).append({"grant_actor": ga})
            prov = r.setdefault("prov", {})
            prov["grants.grant_actor"] = f"derivado:prosa-{tipo}"
            prov.setdefault("grants", f"derivado:prosa-{tipo}")
            outros.append((r, tipo, m_outro))
            continue

        m = P_CONCEDE.search(texto)
        if not m:
            continue
        if P_PROIBE.search(texto):
            proibem.append(r)
            continue
        if P_ACESSO.search(texto):
            acesso.append(r)
            continue

        frase = " ".join(m.group(0).split())

        # Especies citadas nominalmente, na ordem em que a prosa cita: no Drake
        # Rider, riding drake vem antes de riding dragonet.
        achadas = [(p.search(frase).start(), ident)
                   for p, ident in padrao_especie if p.search(frase)]
        opcoes = list(dict.fromkeys(i for _, i in sorted(achadas)))

        g = {"tipo": "companheiro", "escolhe": "animal-companion"}
        if opcoes:
            g["opcoes"] = opcoes
        if P_ADICIONAL.search(texto):
            g["adicional"] = True

        tinha = bool(r.get("grants") or [])
        r.setdefault("grants", []).append({"grant_actor": g})
        # `prov` do que ja existia FICA. Sobrescrever apagaria o rastro de quem
        # escreveu o resto do `grants` (o Beastmaster tem `grant_item` do
        # Foundry); o portao 1 so cobra a chave do campo, nao estranha a extra.
        prov = r.setdefault("prov", {})
        prov["grants.grant_actor"] = "derivado:prosa-companheiro"
        if not tinha:
            prov["grants"] = "derivado:prosa-companheiro"
        # `mechanized == bool(grants)` e invariante da v1, e o reconciliador
        # (que a deriva) roda MUITO antes deste passo. Sem esta linha os 17
        # feats de companheiro saem com `grants` cheio e `mechanized: false` --
        # a mesma correcao que `unificar_efeitos.py` ja faz ao concluir.
        r["mechanized"] = True
        concedem.append((r, frase, opcoes))

    # ROTA DA CLASSE, estruturada: a class-feature Familiar/Eidolon nao tem
    # prosa de concessao, mas esta na `progressao` da classe. Marca a propria
    # feature, e nao a classe: e ela que o motor poe em `self.features`.
    por_id = {r["id"]: r for r in base}
    for fid, (tipo, escolhe) in FEATURE_DE_ATOR.items():
        reg = por_id.get(fid)
        if reg is None:
            continue
        if any("grant_actor" in g for g in (reg.get("grants") or [])
               if isinstance(g, dict)):
            continue
        reg.setdefault("grants", []).append(
            {"grant_actor": {"tipo": tipo, "escolhe": escolhe}})
        prov = reg.setdefault("prov", {})
        prov["grants.grant_actor"] = f"derivado:progressao-{tipo}"
        prov.setdefault("grants", f"derivado:progressao-{tipo}")
        outros.append((reg, tipo, None))

    with open(f"{BASE}/index.json", "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False)

    rel = [
        "# Concessao de companheiro derivada da prosa", "",
        f"- registros que concedem companheiro animal: **{len(concedem)}**",
        f"- divida (companheiro que nao e animal): **{len(divida)}**",
        f"- casaram o padrao e foram vetados: **{len(proibem) + len(acesso)}**",
        "",
        "Cada linha traz a FRASE que justifica. Divergencia entre a frase e o "
        "`grant_actor` e defeito deste passo, nao do dado.", "",
        "## Concedem", "",
        "| registro | frase na prosa | especie citada |", "|---|---|---|",
    ]
    for r, frase, opcoes in sorted(concedem, key=lambda x: x[0].get("name") or ""):
        rel.append(f"| {r.get('name')} | {frase[:90]} | "
                   f"{', '.join(opcoes) if opcoes else 'livre'} |")

    rel += ["", "## Familiar e eidolon", "",
            "Mesma ancora, artigo INDEFINIDO: e ele que separa quem GANHA um "
            "familiar de quem fala do que ja tem (as 18 `lesson` e as 16 "
            "`patron` dizem \"and your familiar learns\"). A rota da classe "
            "sai da `progressao`, nao da prosa.", "",
            "| registro | tipo | frase ou rota |", "|---|---|---|"]
    for r, tipo, m in sorted(outros, key=lambda x: (x[1], x[0].get("name") or "")):
        just = " ".join(m.group(0).split())[:70] if m else "progressao da classe"
        rel.append(f"| {r.get('name')} | {tipo} | {just} |")

    rel += ["", "## Divida -- companheiro sem stat block na base", "",
            "| registro | tipo |", "|---|---|"]
    for r, tipo in sorted(divida, key=lambda x: x[0].get("name") or ""):
        rel.append(f"| {r.get('name')} | {tipo} |")

    rel += ["", "## Casaram o padrao e foram VETADOS", "",
            "| registro | veto |", "|---|---|"]
    for r in sorted(proibem, key=lambda x: x.get("name") or ""):
        rel.append(f"| {r.get('name')} | frase proibe o companheiro |")
    for r in sorted(acesso, key=lambda x: x.get("name") or ""):
        rel.append(f"| {r.get('name')} | da ACESSO a especie, nao companheiro "
                   f"(`access` nao existe no vocabulario) |")

    with open(f"{BASE}/relatorio_concessao_de_ator.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(rel) + "\n")

    n_fam = sum(1 for _, t, _ in outros if t == "familiar")
    print(f"concessao de ator: {n_fam} concedem familiar, "
          f"{len(outros) - n_fam} concedem eidolon")
    print(f"concessao de ator: {len(concedem)} concedem companheiro animal, "
          f"{len(divida)} divida, {len(proibem) + len(acesso)} vetados")
    print(f"-> {BASE}/relatorio_concessao_de_ator.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
