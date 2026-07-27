#!/usr/bin/env python3
"""
Motor do Waybuilder: documento de personagem -> visao calculada.

Fatia vertical 1. Implementa as regras de `specs/2026-07-26-regras-multiclasse.md`
que cabem em niveis 1-5, consumindo `pipeline/base/index.json` e um documento no
formato de `specs/2026-07-26-schema-personagem.md`.

O documento guarda **decisao**, nunca resultado. Tudo aqui e derivado e
descartavel: some o motor, o personagem continua intacto no JSON.

Regras implementadas (numeracao da spec):
  1  nivel_de_personagem = SOMA(niveis_de_classe)
  3  bonus total = nivel_de_personagem + rank
  4  duas classes com a mesma proficiencia: vale o melhor rank
  5  class DC e por classe, com rank pelo nivel daquela classe
  7  nivel 1 de classe da o pacote cheio, de qualquer classe
  8  key ability boost e class feat de nivel 1 so da PRIMEIRA classe
  9  pericias automaticas da classe nova sao sempre concedidas
  10 escolhas livres por delta = max(0, orcamento(C) - livres_ja_concedidas)
  11 HP por nivel da classe que recebeu aquele nivel; ancestria no nivel 1
  12 class feat a cada nivel PAR de personagem
  14 cadencia basica segue o nivel de personagem
  16 slots e rank base vem do nivel de CLASSE cru
  17 elevacao: rank_efetivo = ceil(nivel_de_personagem / 2)
  18 elevacao nao vale para slots de arquetipo
  22 focus pool unico do personagem, teto 3

Principio zero: `requires` sugere, nunca bloqueia. O motor calcula e SINALIZA o
que esta fora do requisito -- nunca recusa.
"""
from __future__ import annotations

import json
import math
import os
import re
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(AQUI)
INDEX = os.path.join(PROJETO, "pipeline", "base", "index.json")

RANKS = ["untrained", "trained", "expert", "master", "legendary"]
RANK_BONUS = {"untrained": 0, "trained": 2, "expert": 4, "master": 6, "legendary": 8}
ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"]


def _comparar(tenho, operador: str, alvo) -> bool:
    if operador == ">=":
        return tenho >= alvo
    if operador == "<=":
        return tenho <= alvo
    if operador == "==":
        return tenho == alvo
    return True          # operador desconhecido nao reprova: o app nao arbitra


def norm_slug(s: str) -> str:
    """'cloistered_cleric' e 'cloistered-cleric' sao a mesma chave."""
    return re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")


def norm_chave(registro: dict) -> str:
    return norm_slug(registro.get("name") or registro.get("id", "").split("/")[-1])


def melhor_rank(a: str | None, b: str | None) -> str:
    """Regra 4: entre duas classes que concedem a mesma proficiencia, vale o melhor."""
    ia = RANKS.index(a) if a in RANKS else 0
    ib = RANKS.index(b) if b in RANKS else 0
    return RANKS[max(ia, ib)]


class Base:
    """A base canonica, carregada uma vez."""

    def __init__(self, caminho: str = INDEX):
        with open(caminho, encoding="utf-8") as fh:
            registros = json.load(fh)
        self.por_id = {r["id"]: r for r in registros}

    def get(self, wb_id: str) -> dict:
        r = self.por_id.get(wb_id)
        if r is None:
            raise KeyError(f"id ausente da base: {wb_id}")
        return r

    def opcional(self, wb_id: str) -> dict | None:
        return self.por_id.get(wb_id)


class Personagem:
    """Deriva a visao calculada a partir das escolhas.

    Nada aqui e persistido: o documento continua sendo a unica fonte de verdade,
    e por isso mudanca de regra re-deriva em vez de invalidar ficha salva.
    """

    def __init__(self, doc: dict, base: Base):
        self.doc = doc
        self.base = base
        self.avisos: list[str] = []
        self._derivar()

    # -- escolhas -----------------------------------------------------------

    def _escolhas(self, slot: str) -> list[dict]:
        return [e for e in self.doc.get("escolhas", []) if e.get("slot") == slot]

    def _derivar(self) -> None:
        self._niveis_de_classe()
        self._ancestria_e_background()
        self._features_de_classe()
        self._proficiencias()
        self._atributos()
        self._hp()
        self._slots_de_feat()
        self._conjuracao()
        self._focus()
        self._checar_requisitos()

    # -- regra 1: estrutura -------------------------------------------------

    def _niveis_de_classe(self) -> None:
        """Regra 1: nivel de personagem e a SOMA dos niveis de classe."""
        self.niveis_por_classe: dict[str, int] = defaultdict(int)
        self.ordem_de_classe: list[str] = []      # ordem de entrada de cada classe
        self.classe_do_nivel: dict[int, str] = {}  # nivel de personagem -> classe

        for e in self._escolhas("nivel_de_classe"):
            cid = e["pega"]
            nivel_personagem = e.get("em")
            if not isinstance(nivel_personagem, int):
                self.avisos.append(f"nivel_de_classe sem `em` numerico: {e}")
                continue
            self.niveis_por_classe[cid] += 1
            self.classe_do_nivel[nivel_personagem] = cid
            if cid not in self.ordem_de_classe:
                self.ordem_de_classe.append(cid)

        self.nivel = sum(self.niveis_por_classe.values())
        self.primeira_classe = self.ordem_de_classe[0] if self.ordem_de_classe else None

        # sanidade: um nivel de personagem, uma classe
        esperados = set(range(1, self.nivel + 1))
        vistos = set(self.classe_do_nivel)
        if vistos != esperados:
            faltando = sorted(esperados - vistos)
            sobrando = sorted(vistos - esperados)
            if faltando:
                self.avisos.append(f"niveis de personagem sem classe atribuida: {faltando}")
            if sobrando:
                self.avisos.append(f"niveis fora da faixa 1..{self.nivel}: {sobrando}")

    def nivel_de(self, classe_id: str) -> int:
        return self.niveis_por_classe.get(classe_id, 0)

    # -- ancestralidade, heranca, background --------------------------------

    def _ancestria_e_background(self) -> None:
        def um(slot):
            esc = self._escolhas(slot)
            return self.base.opcional(esc[0]["pega"]) if esc else None

        self.ancestria = um("ancestralidade")
        self.heranca = um("heranca")
        self.background = um("background")
        for nome, reg in (("ancestralidade", self.ancestria),
                          ("background", self.background)):
            if reg is None:
                self.avisos.append(f"sem {nome} escolhida")

    # -- regra 7: identidade de classe --------------------------------------

    def _features_de_classe(self) -> None:
        """Regra 7: o nivel de classe compra IDENTIDADE, e ela vem inteira.

        E o argumento central da houserule: gastar nivel de classe vale a pena
        porque compra identidade, e nenhuma dedicacao compra identidade integra.
        Se as features nao aparecem na ficha, a regra fica sem efeito visivel.

        A progressao ja vem separada em concedido vs escolhido
        (`pipeline/aplicar_subclasses.py`): sem isso um Mago 1 receberia as 23
        escolas de magia de uma vez.
        """
        self.features: list[dict] = []
        self.slots_de_subclasse: list[dict] = []

        escolhidas = {e.get("pega") for e in self._escolhas("subclasse")}

        for cid in self.ordem_de_classe:
            classe = self.base.get(cid)
            nivel_classe = self.nivel_de(cid)

            for passo in classe.get("progressao") or []:
                if int(passo.get("nivel") or 0) > nivel_classe:
                    continue          # regra 16/7: a feature vem pelo nivel DA CLASSE
                fid = passo.get("concede")
                feature = self.base.opcional(fid)
                self.features.append({
                    "id": fid,
                    "nome": (feature or {}).get("name", fid),
                    "classe": classe.get("name", cid),
                    "nivel_de_classe": passo.get("nivel"),
                    "grants": (feature or {}).get("grants") or [],
                    "na_base": feature is not None,
                })

            for bloco in classe.get("subclasses") or []:
                if int(bloco.get("nivel") or 1) > nivel_classe:
                    continue
                escolha = next((o for o in bloco.get("opcoes") or [] if o in escolhidas), None)
                self.slots_de_subclasse.append({
                    "classe": classe.get("name", cid),
                    "eixo": bloco.get("eixo"),
                    "nivel": bloco.get("nivel"),
                    "opcoes": len(bloco.get("opcoes") or []),
                    "escolhido": escolha,
                    "nome": (self.base.opcional(escolha) or {}).get("name") if escolha else None,
                })
                if escolha is None:
                    self.avisos.append(
                        f"{classe.get('name')}: falta escolher `{bloco.get('eixo')}` "
                        f"({len(bloco.get('opcoes') or [])} opcoes)")
                else:
                    reg = self.base.opcional(escolha)
                    if reg:
                        self.features.append({
                            "id": escolha, "nome": reg.get("name", escolha),
                            "classe": classe.get("name", cid),
                            "nivel_de_classe": bloco.get("nivel"),
                            "grants": reg.get("grants") or [],
                            "na_base": True, "eixo": bloco.get("eixo"),
                        })

    # -- regras 3, 4, 5, 7, 9: proficiencias --------------------------------

    def _proficiencias(self) -> None:
        """Regras 7 e 4: pacote cheio de cada classe, melhor rank entre elas.

        Regra 7 e deliberada e cara: nivel 1 de QUALQUER classe entrega saves,
        Percepcao, armas e armadura completos. Um Monge 1 / Guerreiro 1 no nivel
        2 tem o melhor perfil defensivo do jogo -- aceito de olho aberto, porque
        o nivel fica gasto para sempre.
        """
        self.proficiencias: dict[str, str] = {}
        self.origem_proficiencia: dict[str, list[str]] = defaultdict(list)

        def aplicar(chave: str, rank: str, origem: str) -> None:
            anterior = self.proficiencias.get(chave)
            novo = melhor_rank(anterior, rank)
            self.proficiencias[chave] = novo
            if novo == rank and rank != anterior:
                self.origem_proficiencia[chave] = [origem]
            elif rank == novo:
                self.origem_proficiencia[chave].append(origem)

        for cid in self.ordem_de_classe:
            classe = self.base.get(cid)
            for g in classe.get("grants") or []:
                if isinstance(g, dict) and "proficiency" in g:
                    for chave, rank in (g["proficiency"] or {}).items():
                        aplicar(chave, rank, classe.get("name", cid))

        # as features de identidade tambem elevam rank (Weapon Mastery,
        # Expert Spellcaster, Reflex Expertise...). Sem isto a regra 7 entrega
        # a feature na lista e nao no numero.
        for f in self.features:
            for g in f.get("grants") or []:
                if isinstance(g, dict) and "proficiency" in g:
                    for chave, rank in (g["proficiency"] or {}).items():
                        aplicar(chave, rank, f"{f['nome']} ({f['classe']})")

        # regra 9: pericia automatica da classe e identidade, sempre concedida
        self.pericias_automaticas: dict[str, str] = {}
        for cid in self.ordem_de_classe:
            classe = self.base.get(cid)
            for g in classe.get("grants") or []:
                for pericia in ((g.get("skill_training") or {}).get("auto") or []):
                    self.pericias_automaticas[pericia] = classe.get("name", cid)
                    aplicar(pericia, "trained", classe.get("name", cid))

        # background treina pericia tambem
        if self.background:
            treino = self.background.get("skill_training") or {}
            for pericia in (treino.get("skills") or []):
                aplicar(pericia, "trained", self.background.get("name", "background"))
            for lore in (treino.get("lore") or []):
                aplicar(f"lore:{lore}", "trained", self.background.get("name", "background"))

        # regra 10: orcamento de pericia livre, por delta
        self._orcamento_de_pericia()

    def _orcamento_de_pericia(self) -> None:
        """Regra 10: delta = max(0, orcamento(C) - livres_ja_concedidas).

        O `max` e o que torna a ordem das classes irrelevante para o total, e o
        que impede o multiclasse de multiplicar orcamento de pericia. As
        automaticas da regra 9 nao entram na conta dos dois lados.
        """
        concedidas = 0
        detalhe = []
        for cid in self.ordem_de_classe:
            classe = self.base.get(cid)
            livre = 0
            for g in classe.get("grants") or []:
                livre = max(livre, int((g.get("skill_training") or {}).get("free") or 0))
            # o INT tambem da pericias livres, mas isso e recurso de personagem
            delta = max(0, livre - concedidas)
            concedidas += delta
            detalhe.append({"classe": classe.get("name", cid),
                            "orcamento": livre, "delta": delta})
        self.pericias_livres = concedidas
        self.pericias_livres_detalhe = detalhe

    # -- regra 8: atributos -------------------------------------------------

    def _atributos(self) -> None:
        """Regra 8: o boost de habilidade-chave vem SO da primeira classe."""
        self.boosts: dict[str, int] = defaultdict(int)
        self.origem_boost: list[str] = []

        def aplicar_boosts(lista, origem):
            for b in lista or []:
                ab = b.get("ability_boost") if isinstance(b, dict) else None
                if not ab:
                    continue
                if ab.get("livre"):
                    self.origem_boost.append(
                        f"{origem}: {ab.get('quantidade', 1)} livre(s)")
                    continue
                opcoes = ab.get("opcoes") or []
                if len(opcoes) == 1:
                    self.boosts[opcoes[0]] += ab.get("quantidade", 1)
                    self.origem_boost.append(f"{origem}: +{opcoes[0]}")
                else:
                    self.origem_boost.append(f"{origem}: escolha entre {opcoes}")

        if self.ancestria:
            aplicar_boosts(self.ancestria.get("boosts"),
                           self.ancestria.get("name", "ancestria"))
            # `flaw` vem como DICT (`{"ability_flaw": {...}}`), nao como lista.
            # Iterar um dict entrega as chaves -- strings --, o isinstance
            # reprovava e o defeito era descartado em silencio. Achado ao
            # comparar com os iconics: todo personagem de ancestria com defeito
            # de CON saia com 1 ponto de modificador a mais, e portanto
            # `nivel` HP a mais.
            defeitos = self.ancestria.get("flaw") or []
            if isinstance(defeitos, dict):
                defeitos = [defeitos]
            for f in defeitos:
                ab = f.get("ability_flaw") if isinstance(f, dict) else None
                for op in ((ab or {}).get("opcoes") or []):
                    self.boosts[op] -= 1
                    self.origem_boost.append(
                        f"{self.ancestria.get('name')}: -{op} (defeito)")
        if self.background:
            aplicar_boosts(self.background.get("boosts"),
                           self.background.get("name", "background"))

        # regra 8: SO a primeira classe da o boost de habilidade-chave
        if self.primeira_classe:
            classe = self.base.get(self.primeira_classe)
            chaves = classe.get("key_ability") or []
            if len(chaves) == 1:
                self.boosts[chaves[0]] += 1
                self.origem_boost.append(f"{classe.get('name')} (1a classe): +{chaves[0]}")
            elif chaves:
                self.origem_boost.append(
                    f"{classe.get('name')} (1a classe): escolha entre {chaves}")
        for cid in self.ordem_de_classe[1:]:
            classe = self.base.get(cid)
            self.origem_boost.append(
                f"{classe.get('name')}: SEM boost de chave (regra 8 -- so a 1a classe)")

        # Boosts livres declarados no documento, **so ate o nivel atual**.
        # O documento pode carregar escolha de nivel futuro -- planejamento de
        # progressao e caso normal, e o schema guarda decisao, nao resultado.
        # Aplicar tudo faz um personagem de nivel 3 andar com os atributos de
        # nivel 5: achado comparando com os iconics, cujo arquivo de nivel 3 ja
        # traz os boosts do 5.
        for e in self._escolhas("boosts_livres"):
            quando = e.get("em")
            if isinstance(quando, int) and quando > self.nivel:
                self.avisos.append(
                    f"boosts de nivel {quando} ignorados -- personagem tem "
                    f"nivel {self.nivel}")
                continue
            for atributo in (e.get("pega") or []):
                self.boosts[atributo] += 1
                self.origem_boost.append(f"nivel {quando}: +{atributo} (livre)")

        self.atributos = {a: 10 + 2 * self.boosts.get(a, 0) for a in ATRIBUTOS}
        self.modificadores = {a: (v - 10) // 2 for a, v in self.atributos.items()}

    # -- regra 11: HP -------------------------------------------------------

    def _hp(self) -> None:
        """Regra 11: HP por nivel vem da classe que recebeu AQUELE nivel."""
        self.hp_detalhe = []
        total = 0
        if self.ancestria:
            hp_anc = int(self.ancestria.get("hp") or 0)
            total += hp_anc
            self.hp_detalhe.append(
                {"origem": self.ancestria.get("name"), "hp": hp_anc, "nota": "ancestria"})

        con = self.modificadores.get("con", 0)
        for nivel in sorted(self.classe_do_nivel):  # noqa: B007 (usado abaixo)
            cid = self.classe_do_nivel[nivel]
            classe = self.base.get(cid)
            por_nivel = 0
            for g in classe.get("grants") or []:
                if isinstance(g, dict) and "hp_per_level" in g:
                    por_nivel = int(g["hp_per_level"])
            ganho = por_nivel + con
            total += ganho
            self.hp_detalhe.append({
                "origem": f"nivel {nivel} ({classe.get('name')})",
                "hp": ganho, "nota": f"{por_nivel} da classe + {con} de CON"})

        # feat que concede HP -- `Toughness` e o caso classico
        # (`flat_modifier` com selector `hp` e valor `@actor.level`). Sem isto o
        # HP fica exatamente `nivel` pontos abaixo do oficial, que foi como a
        # validacao contra os iconics da Paizo achou esta lacuna.
        for wb_id, feat in self._feats_escolhidos():
            for g in feat.get("grants") or []:
                fm = g.get("flat_modifier") if isinstance(g, dict) else None
                if not fm or fm.get("selector") != "hp":
                    continue
                valor = self._resolver_valor(fm.get("value"))
                if valor:
                    total += valor
                    self.hp_detalhe.append({
                        "origem": feat.get("name", wb_id), "hp": valor,
                        "nota": f"feat ({fm.get('value')})"})
        self.hp = total

    def _feats_escolhidos(self):
        for e in self.doc.get("escolhas", []):
            wb_id = e.get("pega")
            if isinstance(wb_id, str) and wb_id.startswith("wb:feat/"):
                feat = self.base.opcional(wb_id)
                if feat is not None:
                    yield wb_id, feat

    def _resolver_valor(self, expressao):
        """Resolve a expressao do Foundry no valor deste personagem.

        Regra 19: em texto de regra impresso, "your level" significa **nivel de
        personagem** -- e `@actor.level` e exatamente isso.
        """
        if isinstance(expressao, (int, float)):
            return int(expressao)
        texto = str(expressao or "").strip()
        if texto in ("@actor.level", "@actor.details.level.value"):
            return self.nivel
        try:
            return int(texto)
        except ValueError:
            return 0

    # -- regras 12 e 14: slots de feat --------------------------------------

    def _slots_de_feat(self) -> None:
        """Regra 12: class feat a cada nivel PAR de personagem, nao por classe.

        Regra 14: a cadencia basica (ancestry, general, skill) segue o nivel de
        personagem, sem mudanca.

        A conta e por PERSONAGEM. Somar as tabelas das classes multiplicaria os
        slots e quebraria a regra 21 (a rota de nivel nunca pode render mais que
        a de dedicacao... nem menos).
        """
        # Cadencia BASICA (regra 14), valida para qualquer personagem
        basica = {
            "class": [n for n in range(1, self.nivel + 1) if n % 2 == 0],
            "skill": [n for n in range(1, self.nivel + 1) if n % 2 == 0],
            "general": [n for n in range(1, self.nivel + 1) if n % 4 == 3],
            "ancestry": [n for n in range(1, self.nivel + 1) if n % 4 == 1],
        }

        # Regra 15: quando uma CLASSE concede cadencia extra, o extra passa a
        # valer a partir do nivel de personagem em que aquela classe entrou.
        # O Ladino concede skill feat todo nivel e o Investigador concede skill
        # increase todo nivel -- usar so a cadencia basica dava a eles metade
        # dos slots. A tabela vem de `feat_slot` da classe, que o Foundry
        # declara em `skillFeatLevels` e afins.
        entrada_da_classe = {}
        for nivel, cid in sorted(self.classe_do_nivel.items()):
            entrada_da_classe.setdefault(cid, nivel)

        extras: dict[str, set[int]] = {k: set(v) for k, v in basica.items()}
        for cid, desde in entrada_da_classe.items():
            classe = self.base.get(cid)
            for g in classe.get("grants") or []:
                fs = g.get("feat_slot") if isinstance(g, dict) else None
                if not fs or not fs.get("kind"):
                    continue
                chave = fs["kind"]
                if chave not in extras:
                    extras[chave] = set(basica.get(chave, []))
                for n in (fs.get("levels") or []):
                    # so conta a partir de quando a classe entrou (regra 15) e
                    # ate o nivel atual
                    if desde <= n <= self.nivel:
                        extras[chave].add(n)

        self.slots = {k: sorted(v) for k, v in extras.items()}
        # regra 2: Free Archetype sempre ligado -- slot em todo nivel par
        self.slots["free_archetype"] = [n for n in range(1, self.nivel + 1) if n % 2 == 0]

        # regra 8: o class feat de nivel 1 so vem da PRIMEIRA classe
        self.class_feat_nivel_1 = 1 in (self.slots.get("class") or [])
        if 1 in (self.slots.get("class") or []) and self.primeira_classe:
            concede = any(
                1 in ((g.get("feat_slot") or {}).get("levels") or [])
                and (g.get("feat_slot") or {}).get("kind") == "class"
                for g in (self.base.get(self.primeira_classe).get("grants") or [])
                if isinstance(g, dict))
            if not concede:
                self.slots["class"] = [n for n in self.slots["class"] if n != 1]
                self.class_feat_nivel_1 = False

        # o que o documento realmente gastou
        self.gastos: dict[str, list[dict]] = defaultdict(list)
        for e in self.doc.get("escolhas", []):
            if e.get("slot") in ("class_feat", "skill_feat", "general_feat",
                                 "ancestry_feat", "free_archetype"):
                self.gastos[e["slot"]].append(e)

    # -- regras 16, 17, 18: conjuracao --------------------------------------

    def _conjuracao(self) -> None:
        """Regra 16: slots pelo nivel de CLASSE cru, tabela nativa do PF2e.
        Regra 17: rank efetivo = ceil(nivel_de_personagem / 2).

        E aqui que a houserule inteira aparece. Um Mago 2 dentro de um
        personagem de nivel 5 tem os SLOTS de um Mago 2 (2 de rank 1) mas
        conjura no rank 3 -- o slot vem da classe, a potencia vem do personagem.
        Sem os dois numeros separados nao ha como expressar isso.
        """
        self.conjuracao = []
        for cid in self.ordem_de_classe:
            classe = self.base.get(cid)
            sc = classe.get("spellcasting")
            if not isinstance(sc, dict) or not sc.get("slots_per_level"):
                continue
            nivel_classe = self.nivel_de(cid)
            tabela = (sc.get("slots_per_level") or {}).get(str(nivel_classe))
            if not tabela:
                self.avisos.append(
                    f"{classe.get('name')}: sem linha de slots para nivel de classe "
                    f"{nivel_classe}")
                continue
            rank_efetivo = math.ceil(self.nivel / 2)          # regra 17
            max_rank_cru = int(tabela.get("max_rank") or 0)   # regra 16
            self.conjuracao.append({
                "classe": classe.get("name", cid),
                "nivel_de_classe": nivel_classe,
                "tradicao": sc.get("tradition"),
                "tipo": sc.get("type"),
                "slots": tabela.get("ranks") or {},
                "truques": tabela.get("cantrips"),
                "max_rank_do_slot": max_rank_cru,
                "rank_efetivo": rank_efetivo,
                "elevacao": max(0, rank_efetivo - max_rank_cru),
                "dc": self._dc_de_conjuracao(classe, nivel_classe, sc),
            })

    def _dc_de_conjuracao(self, classe: dict, nivel_classe: int, sc: dict) -> dict:
        """Regra 3: bonus = nivel_de_PERSONAGEM + rank; o RANK vem do nivel da classe."""
        prog = sc.get("proficiency") or {}

        # A progressao pode depender da SUBCLASSE. O Clerigo e o caso publicado:
        # Cloistered chega a legendary no 19, Warpriest para em master. Ler a
        # progressao "da classe" aqui daria o numero errado para metade dos
        # Clerigos -- e e por isso que `class_level` sozinho nao basta.
        aninhadas = {k: v for k, v in prog.items() if isinstance(v, dict)}
        if aninhadas:
            escolhida = self._subclasse_de(classe["id"])
            chave = None
            if escolhida:
                alvo = norm_chave(self.base.opcional(escolhida) or {})
                chave = next((k for k in aninhadas if norm_slug(k) == alvo), None)
            if chave is None:
                chave = sorted(aninhadas)[0]
                self.avisos.append(
                    f"{classe.get('name')}: progressao de conjuracao depende da "
                    f"subclasse ({', '.join(sorted(aninhadas))}) e nenhuma foi "
                    f"escolhida -- usando `{chave}`")
            prog = aninhadas[chave]

        rank = "untrained"
        for nome in RANKS:
            exigido = prog.get(nome)
            if isinstance(exigido, int) and nivel_classe >= exigido:
                rank = melhor_rank(rank, nome)
        chaves = classe.get("key_ability") or []
        mod = max((self.modificadores.get(k, 0) for k in chaves), default=0)
        bonus = self.nivel + RANK_BONUS[rank] + mod
        return {"rank": rank, "dc": 10 + bonus, "ataque": bonus,
                "nota": f"nivel de personagem {self.nivel} + rank {rank} "
                        f"(pelo nivel de classe {nivel_classe}) + mod {mod}"}

    # -- regra 22: focus ----------------------------------------------------

    def _focus(self) -> None:
        """Regra 22: pool UNICO do personagem, teto 3, independente das classes."""
        pool = 0
        for cid in self.ordem_de_classe:
            sc = self.base.get(cid).get("spellcasting")
            if isinstance(sc, dict):
                pool += int(((sc.get("focus_pool") or {}).get("base") or 0))
        self.focus_pool = min(3, pool)

    # -- regra 3: bonus derivado --------------------------------------------

    def bonus(self, chave: str) -> int:
        """Regra 3: bonus total = nivel_de_personagem + rank. Rank 0 = sem nivel."""
        rank = self.proficiencias.get(chave, "untrained")
        if rank == "untrained":
            return 0
        return self.nivel + RANK_BONUS[rank]

    def _subclasse_de(self, classe_id: str) -> str | None:
        """A sub-escolha que este personagem fez para a classe dada."""
        classe = self.base.opcional(classe_id) or {}
        opcoes = {o for bloco in (classe.get("subclasses") or [])
                  for o in (bloco.get("opcoes") or [])}
        for e in self._escolhas("subclasse"):
            if e.get("pega") in opcoes:
                return e["pega"]
        return None

    # -- avaliacao do predicado ---------------------------------------------

    def avaliar(self, predicado) -> tuple[bool, list[str]]:
        """Avalia o predicado contra este personagem.

        Devolve (atende, motivos). **Nunca** e usado para negar uma escolha --
        o principio zero e explicito: `requires` sugere e ordena, nunca bloqueia.
        Serve para o app dizer "estes combinam com o que voce tem" e para marcar
        o que esta fora.
        """
        if predicado in (None, {}, []):
            return True, []
        if not isinstance(predicado, dict):
            return True, []

        if "all" in predicado:
            motivos = []
            ok = True
            for c in predicado["all"]:
                passou, m = self.avaliar(c)
                ok = ok and passou
                motivos += m
            return ok, motivos
        if "any" in predicado:
            resultados = [self.avaliar(c) for c in predicado["any"]]
            if any(r[0] for r in resultados):
                return True, []
            return False, [m for _, ms in resultados for m in ms]
        if "not" in predicado:
            passou, _ = self.avaliar(predicado["not"])
            return (not passou), ([] if not passou else ["condicao proibida presente"])

        for termo, valor in predicado.items():
            metodo = getattr(self, f"_termo_{termo}", None)
            if metodo is None:
                continue          # termo desconhecido nao reprova: nao arbitra
            passou, motivo = metodo(valor)
            if not passou:
                return False, [motivo]
        return True, []

    def _termo_class_level(self, valor) -> tuple[bool, str]:
        """`class_level` e o termo que so existe por causa da houserule."""
        for slug, exigencia in (valor or {}).items():
            cid = f"wb:class/{slug}"
            tenho = self.nivel_de(cid)
            nome = (self.base.opcional(cid) or {}).get("name", slug)
            for op, alvo in (exigencia or {}).items():
                if not _comparar(tenho, op, alvo):
                    return False, (f"exige {nome} nivel {op} {alvo}; "
                                   f"tem {tenho} (personagem {self.nivel})")
        return True, ""

    def _termo_character_level(self, valor) -> tuple[bool, str]:
        for op, alvo in (valor or {}).items():
            if not _comparar(self.nivel, op, alvo):
                return False, f"exige nivel de personagem {op} {alvo}; tem {self.nivel}"
        return True, ""

    def _termo_ability(self, valor) -> tuple[bool, str]:
        for atributo, exigencia in (valor or {}).items():
            tenho = self.atributos.get(atributo, 10)
            for op, alvo in (exigencia or {}).items():
                if not _comparar(tenho, op, alvo):
                    return False, f"exige {atributo.upper()} {op} {alvo}; tem {tenho}"
        return True, ""

    def _termo_proficiency(self, valor) -> tuple[bool, str]:
        for chave, exigencia in (valor or {}).items():
            tenho = self.proficiencias.get(chave, "untrained")
            for op, alvo in (exigencia or {}).items():
                ia = RANKS.index(tenho) if tenho in RANKS else 0
                ib = RANKS.index(alvo) if alvo in RANKS else 0
                if not _comparar(ia, op, ib):
                    return False, f"exige {chave} {op} {alvo}; tem {tenho}"
        return True, ""

    def _termo_has(self, valor) -> tuple[bool, str]:
        # `pega` nem sempre e um id: `boosts_livres` guarda uma LISTA de
        # atributos. Filtrar por str antes do set, senao estoura no primeiro
        # personagem que distribuiu boosts.
        tudo = {e.get("pega") for e in self.doc.get("escolhas", [])
                if isinstance(e.get("pega"), str)}
        tudo |= {f["id"] for f in self.features}
        tudo |= {c for c in self.ordem_de_classe}
        for reg in (self.ancestria, self.heranca, self.background):
            if reg:
                tudo.add(reg["id"])
        if valor in tudo:
            return True, ""
        nome = (self.base.opcional(valor) or {}).get("name", valor)
        return False, f"exige ter {nome}"

    def _termo_subclass(self, valor) -> tuple[bool, str]:
        """A camada do meio: nem classe, nem personagem."""
        for slug, alvo in (valor or {}).items():
            escolhida = self._subclasse_de(f"wb:class/{slug}")
            if escolhida != alvo:
                nome = (self.base.opcional(alvo) or {}).get("name", alvo)
                atual = (self.base.opcional(escolhida) or {}).get("name", "nenhuma") \
                    if escolhida else "nenhuma"
                return False, f"exige a sub-escolha {nome}; tem {atual}"
        return True, ""

    def _termo_trait(self, valor) -> tuple[bool, str]:
        alvos = valor if isinstance(valor, list) else [valor]
        meus = set()
        for reg in (self.ancestria, self.heranca, self.background):
            if reg:
                meus |= {str(t).lower() for t in (reg.get("traits") or [])}
        for cid in self.ordem_de_classe:
            meus.add(str(self.base.get(cid).get("name") or "").lower())
        faltando = [a for a in alvos if str(a).lower() not in meus]
        return (not faltando), (f"exige o trait {faltando}" if faltando else "")

    def disponiveis(self, kind: str = "feat", limite: int | None = None) -> list[dict]:
        """O que combina com o personagem -- a pergunta central do construtor.

        `requires` ORDENA a lista; nao a filtra. O que esta fora aparece
        marcado, nunca escondido.
        """
        saida = []
        for r in self.base.por_id.values():
            if r.get("kind") != kind:
                continue
            atende, motivos = self.avaliar(r.get("requires"))
            saida.append({"id": r["id"], "nome": r.get("name"),
                          "level": r.get("level"), "atende": atende,
                          "motivos": motivos})
        saida.sort(key=lambda x: (not x["atende"], x["level"] or 0, x["nome"] or ""))
        return saida[:limite] if limite else saida

    # -- principio zero: sinaliza, nunca bloqueia ---------------------------

    def _checar_requisitos(self) -> None:
        """`requires` sugere, NUNCA bloqueia (principio zero da spec).

        Regra 12: o requisito de nivel de um class feat e checado contra o nivel
        DAQUELA CLASSE. Regra 13: feat de arquetipo, contra o nivel de personagem.
        """
        self.fora_do_requisito = []
        for e in self.doc.get("escolhas", []):
            wb_id = e.get("pega")
            if not isinstance(wb_id, str) or not wb_id.startswith("wb:feat/"):
                continue
            feat = self.base.opcional(wb_id)
            if feat is None:
                self.fora_do_requisito.append(
                    {"feat": wb_id, "motivo": "id ausente da base"})
                continue
            # O predicado ja carrega o gate de nivel derivado
            # (`pipeline/derivar_gate_nivel.py`), entao a checagem manual de
            # nivel que existia aqui virou caso particular de avaliar o
            # predicado inteiro -- e agora `proficiency`, `has`, `ability` e
            # `subclass` tambem sao verificados.
            atende, motivos = self.avaliar(feat.get("requires"))
            if not atende:
                self.fora_do_requisito.append({
                    "feat": feat.get("name", wb_id),
                    "motivo": "; ".join(motivos) or "predicado nao atendido"})

    def _classe_do_feat(self, feat: dict) -> str | None:
        """A classe de um feat sai do trait, nao de lista escrita a mao."""
        traits = {str(t).lower() for t in (feat.get("traits") or [])}
        for cid in self.ordem_de_classe:
            nome = str(self.base.get(cid).get("name") or "").lower()
            if nome in traits:
                return cid
        return None

    # -- saida --------------------------------------------------------------

    def visao(self) -> dict:
        """A visao calculada. Cache, nunca fonte de verdade."""
        return {
            "nivel": self.nivel,
            "classes": {self.base.get(c).get("name", c): n
                        for c, n in self.niveis_por_classe.items()},
            "ancestralidade": (self.ancestria or {}).get("name"),
            "heranca": (self.heranca or {}).get("name"),
            "background": (self.background or {}).get("name"),
            "atributos": self.atributos,
            "modificadores": self.modificadores,
            "hp": self.hp,
            "proficiencias": self.proficiencias,
            "pericias_livres": self.pericias_livres,
            "slots": self.slots,
            "conjuracao": self.conjuracao,
            "focus_pool": self.focus_pool,
            "features": self.features,
            "subclasses": self.slots_de_subclasse,
            "fora_do_requisito": self.fora_do_requisito,
            "avisos": self.avisos,
        }


def carregar(caminho_doc: str, base: Base | None = None) -> Personagem:
    with open(caminho_doc, encoding="utf-8") as fh:
        doc = json.load(fh)
    return Personagem(doc, base or Base())
