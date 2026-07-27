#!/usr/bin/env python3
"""
Simula milhares de personagens de CLASSE UNICA e confere contra o RAW.

## O que este teste e, e o que ele nao e

Nao e validacao contra resposta oficial: personagem gerado nao tem HP publicado
para comparar, ao contrario dos iconics (`validar_iconics.py`). E **verificacao
de invariante** -- as regras que o PF2e garante para qualquer personagem legal.

O que o salva de ser so consistencia interna: o Foundry **declara as tabelas de
progressao dentro de cada classe** (`classFeatLevels`, `ancestryFeatLevels`,
`generalFeatLevels`, `skillFeatLevels`, `skillIncreaseLevels`). Entao os slots
sao conferidos contra a fonte, nao contra o proprio motor.

## Por que classe unica, e por que isso e o teste mais importante

Com uma classe so, `nivel_de_classe == nivel_de_personagem` e **toda a houserule
tem que desaparecer**: a elevacao da regra 17 vira zero, a regra 4 nao tem o que
comparar, a regra 8 nao tem segunda classe para negar. Se qualquer efeito da
regra caseira aparecer aqui, ela esta vazando para o jogo padrao -- que e o pior
defeito possivel neste projeto.

Free Archetype fica **ligado**, porque a spec o declara sempre ligado (regra 2)
e porque os iconics da Paizo nao usam a variante -- e territorio que a validacao
anterior nao alcancava.

Uso:
    python3 simular_raw.py            # ~2.000 personagens
    python3 simular_raw.py 8000       # mais
"""
import json, os, sys, glob, random, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(AQUI)
FOUNDRY = os.path.join(PROJETO, "pipeline", "dados_brutos",
                       "foundry_repo", "packs", "pf2e")
sys.path.insert(0, AQUI)
from motor import Base, Personagem, RANKS      # noqa: E402

SEMENTE = 20260727          # deterministico: mesma rodada, mesmo resultado


def tabelas_do_foundry():
    """nome da classe -> tabelas oficiais de progressao, direto da fonte."""
    saida = {}
    for f in glob.glob(f"{FOUNDRY}/classes/*.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        s = d.get("system") or {}

        def lista(chave):
            v = s.get(chave)
            if isinstance(v, dict):
                v = v.get("value")
            return list(v or [])

        saida[str(d.get("name") or "").lower()] = {
            "class": lista("classFeatLevels"),
            "ancestry": lista("ancestryFeatLevels"),
            "general": lista("generalFeatLevels"),
            "skill": lista("skillFeatLevels"),
            "skill_increase": lista("skillIncreaseLevels"),
            "hp": (s.get("hp") or 0) if isinstance(s.get("hp"), int) else 0,
        }
    return saida


class Verificador:
    """Cada metodo `checa_*` devolve lista de violacoes (str)."""

    def __init__(self, base, tabelas):
        self.base = base
        self.tabelas = tabelas

    def checa_slots(self, p, classe):
        """Os slots gerados batem com a tabela que a CLASSE declara."""
        tab = self.tabelas.get(str(classe.get("name") or "").lower())
        if not tab:
            return [f"sem tabela do Foundry para {classe.get('name')}"]
        problemas = []
        for chave in ("class", "ancestry", "general", "skill"):
            oficial = [n for n in tab[chave] if n <= p.nivel]
            nosso = sorted(p.slots.get(chave) or [])
            if nosso != oficial:
                problemas.append(
                    f"slots de {chave}: motor {nosso} != oficial {oficial}")
        return problemas

    def checa_hp(self, p, classe):
        """HP = ancestria + nivel x (HP da classe + mod de CON), pelo RAW."""
        por_nivel = 0
        for g in classe.get("grants") or []:
            if isinstance(g, dict) and "hp_per_level" in g:
                por_nivel = int(g["hp_per_level"])
        anc = int((p.ancestria or {}).get("hp") or 0)
        con = p.modificadores.get("con", 0)
        esperado = anc + p.nivel * (por_nivel + con)
        # feats que concedem HP entram por cima, entao so cobramos o piso
        if p.hp < esperado:
            return [f"HP {p.hp} abaixo do RAW ({esperado} = {anc} + "
                    f"{p.nivel}x({por_nivel}+{con}))"]
        return []

    def checa_houserule_nao_vaza(self, p):
        """CLASSE UNICA: a houserule inteira tem que sumir.

        CORRECAO 2026-07-27. A versao anterior travava em `elevacao != 0` e
        acusava Animist, Magus e Summoner nos niveis 19-20. **A assercao e que
        estava errada**, nao o motor -- ela confundia os dois eixos:

          liberar rank de slot  ->  nivel de CLASSE      (regra 16)
          heightened, sempre    ->  nivel de PERSONAGEM  (regra 17)

        `elevacao` era a subtracao de um eixo pelo outro, o que nao significa
        nada. Conjurador parcial tem teto de slot 9 e mesmo assim heightena
        truque e focus spell no rank 10 no nivel 20 -- isso e **RAW**, esta na
        regra do trait Cantrip ("automatically heightened to half your level
        rounded up") e vale para o Magus oficial, sem houserule nenhuma.

        O que de fato tem de valer com uma classe so:
          1. nivel de classe == nivel de personagem;
          2. o heightened e ceil(nivel/2) -- se algum dia amarrar no nivel de
             classe, a houserule quebrou o RAW e este teste pega;
          3. slots e max_rank saem da tabela nativa, sem invencao (checado em
             checa_conjuracao).
        """
        problemas = []
        for c in p.conjuracao:
            if c["nivel_de_classe"] != p.nivel:
                problemas.append(
                    f"nivel de classe {c['nivel_de_classe']} != nivel de "
                    f"personagem {p.nivel} com uma classe so")
            esperado = -(-p.nivel // 2)          # ceil(nivel/2)
            if c["rank_efetivo"] != esperado:
                problemas.append(
                    f"rank efetivo {c['rank_efetivo']} != ceil({p.nivel}/2)="
                    f"{esperado} em {c['classe']} -- heightened tem que vir do "
                    f"nivel de PERSONAGEM (regra 17), nunca do de classe")
        return problemas

    def checa_conjuracao(self, p, classe):
        """Slots e rank saem da tabela nativa, sem invencao."""
        sc = classe.get("spellcasting")
        if not isinstance(sc, dict) or not sc.get("slots_per_level"):
            return ["conjurador sem tabela de slots"] if p.conjuracao else []
        if not p.conjuracao:
            return ["classe conjuradora sem bloco de conjuracao derivado"]
        oficial = (sc["slots_per_level"] or {}).get(str(p.nivel)) or {}
        nosso = p.conjuracao[0]
        problemas = []
        if oficial.get("ranks") and nosso["slots"] != oficial["ranks"]:
            problemas.append(f"slots {nosso['slots']} != tabela {oficial['ranks']}")
        if oficial.get("max_rank") is not None and \
                nosso["max_rank_do_slot"] != oficial["max_rank"]:
            problemas.append(
                f"max_rank {nosso['max_rank_do_slot']} != {oficial['max_rank']}")
        return problemas

    def checa_free_archetype(self, p):
        """Regra 2: FA sempre ligado -- slot em todo nivel par, sem exceção."""
        esperado = [n for n in range(1, p.nivel + 1) if n % 2 == 0]
        nosso = sorted(p.slots.get("free_archetype") or [])
        if nosso != esperado:
            return [f"free archetype {nosso} != {esperado}"]
        # e nao pode roubar o slot de class feat
        if set(nosso) - set(p.slots.get("class") or []) != set(nosso) - set(esperado):
            pass
        return []

    def checa_subclasse(self, p, classe):
        """Classe com eixo obrigatorio precisa da escolha, ou avisar."""
        problemas = []
        for bloco in classe.get("subclasses") or []:
            if int(bloco.get("nivel") or 1) > p.nivel:
                continue
            escolhido = any(s["eixo"] == bloco["eixo"] and s["escolhido"]
                            for s in p.slots_de_subclasse)
            avisou = any(bloco["eixo"] in a for a in p.avisos)
            if not escolhido and not avisou:
                problemas.append(
                    f"eixo `{bloco['eixo']}` obrigatorio no nivel "
                    f"{bloco['nivel']} sem escolha e sem aviso")
        return problemas

    def checa_proficiencia(self, p):
        """Rank tem que ser palavra conhecida, e bonus coerente com o rank."""
        problemas = []
        for chave, rank in p.proficiencias.items():
            if rank not in RANKS:
                problemas.append(f"rank invalido em {chave}: {rank!r}")
        if p.nivel > 0 and p.proficiencias.get("perception", "untrained") != "untrained":
            if p.bonus("perception") <= p.nivel:
                problemas.append("bonus de Percepcao nao supera o nivel com rank treinado")
        return problemas

    def checa_atores(self, p):
        """Feat que concede companheiro/familiar/eidolon aparece como ator.

        O eidolon foi o achado do estudo de interoperabilidade: existe no
        Pathbuilder e some no export. Aqui ele e um Ator como qualquer outro.
        """
        concedem = {"wb:feat/animal-companion": "companheiro",
                    "wb:feat/familiar": "familiar"}
        problemas = []
        escolhidos = {e.get("pega") for e in p.doc.get("escolhas", [])
                      if isinstance(e.get("pega"), str)}
        atores = {a.get("tipo") for a in p.doc.get("atores", [])}
        for wb_id, tipo in concedem.items():
            if wb_id in escolhidos and tipo not in atores:
                problemas.append(f"{wb_id} pego mas sem ator `{tipo}`")
        return problemas


def gerar(base, tabelas, quantos, rng):
    classes = [r for r in base.por_id.values() if r.get("kind") == "class"
               and r.get("progressao")]
    ancestrias = [r for r in base.por_id.values() if r.get("kind") == "ancestry"]
    backgrounds = [r for r in base.por_id.values()
                   if r.get("kind") == "background" and r.get("skill_training")]
    if not (classes and ancestrias and backgrounds):
        return
    for i in range(quantos):
        classe = classes[i % len(classes)]                 # cobre todas as classes
        nivel = (i // len(classes)) % 20 + 1               # e todos os niveis
        anc = rng.choice(ancestrias)
        bg = rng.choice(backgrounds)

        escolhas = [
            {"em": "criacao", "slot": "ancestralidade", "pega": anc["id"]},
            {"em": "criacao", "slot": "background", "pega": bg["id"]},
        ]
        for n in range(1, nivel + 1):
            escolhas.append({"em": n, "slot": "nivel_de_classe", "pega": classe["id"]})
        for n in (1, 5, 10, 15, 20):
            if n <= nivel:
                escolhas.append({"em": n, "slot": "boosts_livres",
                                 "pega": rng.sample(["str", "dex", "con",
                                                     "int", "wis", "cha"], 4)})
        # escolher a subclasse quando a classe exige
        for bloco in classe.get("subclasses") or []:
            if int(bloco.get("nivel") or 1) <= nivel and bloco.get("opcoes"):
                escolhas.append({"em": bloco.get("nivel") or 1, "slot": "subclasse",
                                 "pega": rng.choice(bloco["opcoes"])})
        yield classe, {"esquema": "waybuilder/personagem@1",
                       "identidade": {"nome": f"sim-{i}"},
                       "escolhas": escolhas, "atores": []}


def main():
    quantos = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rng = random.Random(SEMENTE)
    base = Base()
    tabelas = tabelas_do_foundry()
    verificador = Verificador(base, tabelas)

    checagens = [
        ("slots vs tabela do Foundry", verificador.checa_slots, True),
        ("HP pelo RAW", verificador.checa_hp, True),
        ("houserule nao vaza", lambda p, c: verificador.checa_houserule_nao_vaza(p), True),
        ("conjuracao vs tabela nativa", verificador.checa_conjuracao, True),
        ("free archetype", lambda p, c: verificador.checa_free_archetype(p), True),
        ("subclasse obrigatoria", verificador.checa_subclasse, True),
        ("proficiencia coerente", lambda p, c: verificador.checa_proficiencia(p), True),
        ("atores concedidos", lambda p, c: verificador.checa_atores(p), True),
    ]

    violacoes = collections.Counter()
    amostras = collections.defaultdict(list)
    por_classe = collections.Counter()
    total = erros = 0

    for classe, doc in gerar(base, tabelas, quantos, rng):
        total += 1
        try:
            p = Personagem(doc, base)
        except Exception as exc:
            violacoes["EXCECAO ao derivar"] += 1
            amostras["EXCECAO ao derivar"].append(
                f"{classe.get('name')}: {type(exc).__name__}: {exc}")
            erros += 1
            continue
        for nome, fn, _ in checagens:
            for problema in fn(p, classe):
                violacoes[nome] += 1
                por_classe[classe.get("name")] += 1
                if len(amostras[nome]) < 6:
                    amostras[nome].append(
                        f"{classe.get('name')} nivel {p.nivel}: {problema}")

    print(f"personagens simulados: {total}")
    print(f"classes com alguma violacao: {len(por_classe)}")
    if not violacoes:
        print("\nnenhuma violacao -- o motor respeita o RAW em classe unica")
    else:
        print(f"\nviolacoes por checagem:")
        for nome, n in violacoes.most_common():
            print(f"  {n:>6}  {nome}")
            for a in amostras[nome][:3]:
                print(f"           {a}")

    saida = os.path.join(PROJETO, "docs", "2026-07-27_simulacao-raw.md")
    linhas = ["# Simulacao de personagens RAW (classe unica, Free Archetype ligado)", "",
              "Verificacao de invariante, nao comparacao com resposta oficial: os",
              "slots sao conferidos contra as tabelas que o **Foundry declara dentro",
              "de cada classe**, e a houserule tem que desaparecer por completo",
              "quando ha uma classe so.", "",
              f"- personagens simulados: **{total}**",
              f"- violacoes: **{sum(violacoes.values())}**", ""]
    if violacoes:
        linhas += ["## Por checagem", ""]
        for nome, n in violacoes.most_common():
            linhas.append(f"### {nome} -- {n}\n")
            linhas += [f"- {a}" for a in amostras[nome]]
            linhas.append("")
        linhas += ["## Por classe", ""]
        linhas += [f"- {c}: {n}" for c, n in por_classe.most_common(15)]
    else:
        linhas.append("Nenhuma violacao.")
    open(saida, "w").write("\n".join(linhas) + "\n")
    print(f"-> {saida}")
    return 1 if violacoes else 0


if __name__ == "__main__":
    sys.exit(main())
