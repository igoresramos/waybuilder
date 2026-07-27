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
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(AQUI)
INDEX = os.path.join(PROJETO, "pipeline", "base", "index.json")

RANKS = ["untrained", "trained", "expert", "master", "legendary"]
RANK_BONUS = {"untrained": 0, "trained": 2, "expert": 4, "master": 6, "legendary": 8}
ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"]


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
            for f in (self.ancestria.get("flaw") or []):
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

        # boosts livres declarados no documento
        for e in self._escolhas("boosts_livres"):
            for atributo in (e.get("pega") or []):
                self.boosts[atributo] += 1
                self.origem_boost.append(f"nivel {e.get('em')}: +{atributo} (livre)")

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
        for nivel in sorted(self.classe_do_nivel):
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
        self.hp = total

    # -- regras 12 e 14: slots de feat --------------------------------------

    def _slots_de_feat(self) -> None:
        """Regra 12: class feat a cada nivel PAR de personagem, nao por classe.

        Regra 14: a cadencia basica (ancestry, general, skill) segue o nivel de
        personagem, sem mudanca.

        A conta e por PERSONAGEM. Somar as tabelas das classes multiplicaria os
        slots e quebraria a regra 21 (a rota de nivel nunca pode render mais que
        a de dedicacao... nem menos).
        """
        self.slots: dict[str, list[int]] = {}
        self.slots["class"] = [n for n in range(1, self.nivel + 1) if n % 2 == 0]
        self.slots["skill"] = [n for n in range(1, self.nivel + 1) if n % 2 == 0]
        self.slots["general"] = [n for n in range(1, self.nivel + 1) if n % 4 == 3]
        self.slots["ancestry"] = [n for n in range(1, self.nivel + 1) if n % 4 == 1]
        # regra 2: Free Archetype sempre ligado -- slot em todo nivel par
        self.slots["free_archetype"] = [n for n in range(1, self.nivel + 1) if n % 2 == 0]

        # regra 8: a primeira classe da um class feat no nivel 1, se a classe der
        self.class_feat_nivel_1 = False
        if self.primeira_classe:
            classe = self.base.get(self.primeira_classe)
            for g in classe.get("grants") or []:
                fs = g.get("feat_slot") if isinstance(g, dict) else None
                if fs and fs.get("kind") == "class" and 1 in (fs.get("levels") or []):
                    self.class_feat_nivel_1 = True
        if self.class_feat_nivel_1:
            self.slots["class"] = [1] + self.slots["class"]

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
            exigido = feat.get("level")
            if not isinstance(exigido, int):
                continue

            if e.get("slot") == "free_archetype":
                # regra 13: arquetipo nao pertence a classe nenhuma
                disponivel, contra = self.nivel, "nivel de personagem"
            else:
                classe = self._classe_do_feat(feat)
                if classe:
                    disponivel = self.nivel_de(classe)
                    contra = f"nivel de {self.base.get(classe).get('name')}"
                else:
                    disponivel, contra = self.nivel, "nivel de personagem"

            if disponivel < exigido:
                self.fora_do_requisito.append({
                    "feat": feat.get("name", wb_id),
                    "motivo": f"exige nivel {exigido}, personagem tem "
                              f"{disponivel} ({contra})"})

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
