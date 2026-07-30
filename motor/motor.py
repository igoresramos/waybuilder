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
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.dirname(AQUI)
INDEX = os.path.join(PROJETO, "pipeline", "base", "index.json")

RANKS = ["untrained", "trained", "expert", "master", "legendary"]
RANK_BONUS = {"untrained": 0, "trained": 2, "expert": 4, "master": 6, "legendary": 8}
ATRIBUTOS = ["str", "dex", "con", "int", "wis", "cha"]

# Cinto de seguranca contra dado malformado, NAO contra o jogador. Medido em
# 2026-07-27 (motor/testes_ciclos/medir_grafo_real.py) sobre os 19705
# registros da base inteira: o grafo de `grant_feat`/`grant_item` com alvo
# ESTATICO (sem uuid dinamico `{...}`) nao tem NENHUM ciclo de 2+ nos, e a
# cadeia mais funda encontrada tem 3 nos. O unico padrao "circular" real sao
# 31 registros que concedem A SI MESMOS (ex.: `Rage`, `Hunt Prey`, `Devise a
# Stratagem` -- artefato do Foundry pra reaplicar o proprio efeito, nao um
# erro de dado), e esses ja saem podados no primeiro passo porque a origem
# entra em `visitados` antes de percorrer. Este teto e so a rede: se um dado
# futuro (novo livro, erro de extracao) formar uma cadeia mais funda, o motor
# CORTA e AVISA -- nunca trava, nunca perde em silencio.
MAX_PROFUNDIDADE_GRANTS = 8


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


def melhor_rank_de(ranks) -> str:
    """O melhor de uma lista. Mesma regra 4, para quando as fontes sao N."""
    return RANKS[max((RANKS.index(r) for r in ranks if r in RANKS), default=0)]


class Base:
    """A base canonica, carregada uma vez."""

    def __init__(self, caminho: str = INDEX):
        with open(caminho, encoding="utf-8") as fh:
            registros = json.load(fh)
        self.por_id = {r["id"]: r for r in registros}
        self._dedicacao_de: dict | None = None
        self._multiclasse: dict | None = None
        self._por_alias: dict | None = None

    def resolver(self, wb_id: str) -> str:
        """Id canonico de uma referencia, seguindo `aliases`.

        A base guarda o nome PRE-REMASTER como alias: `wb:feat/stunning-fist`
        e o mesmo feat que `wb:feat/stunning-blows`, `wild-shape` virou
        `untamed-form`, `divine-ally` virou `devout-blessing`. Sao 348 ids
        alternativos.

        O portao 3 do pipeline sempre aceitou essas referencias -- ele resolve
        por alias antes de reclamar --, mas o motor comparava id cru e por isso
        24 `requires` de feats de classes centrais nunca eram satisfeitos, por
        mais que o personagem tivesse o feat. Portao e motor precisam concordar
        sobre o que e "a mesma coisa"; enquanto discordavam, o portao verde
        escondia o defeito em vez de denunciar.
        """
        if self._por_alias is None:
            self._por_alias = {}
            for r in self.por_id.values():
                kind = r.get("kind")
                for a in (r.get("aliases") or []):
                    if kind and a:
                        self._por_alias[f"wb:{kind}/{norm_slug(a)}"] = r["id"]
        if wb_id in self.por_id:
            return wb_id
        return self._por_alias.get(wb_id, wb_id)

    def multiclasse(self) -> dict[str, str]:
        """nome normalizado -> id da classe, para os arquetipos de multiclasse.

        Derivado: arquetipo cujo nome e nome de classe. Sem lista escrita a
        mao, que ja errou tres vezes neste projeto. Calculado UMA vez por base
        -- ver o comentario em `Personagem._classes_multiclasse`.
        """
        if self._multiclasse is None:
            classes = {norm_slug(r["name"]): r["id"] for r in self.por_id.values()
                       if r.get("kind") == "class" and r.get("name")}
            self._multiclasse = {
                norm_slug(r["name"]): classes[norm_slug(r["name"])]
                for r in self.por_id.values()
                if r.get("kind") == "archetype" and r.get("name")
                and norm_slug(r["name"]) in classes}
        return self._multiclasse

    def dedicacao_do_arquetipo(self, arquetipo_id: str) -> str | None:
        """O feat de dedicacao de um arquetipo, achado pelo dado -- nunca por
        lista escrita a mao. O vinculo e 1:1 na base inteira: 225 arquetipos,
        nenhum com duas dedicacoes (medido 2026-07-27)."""
        if self._dedicacao_de is None:
            self._dedicacao_de = {}
            for r in self.por_id.values():
                if (r["id"].startswith("wb:feat/")
                        and "dedication" in (r.get("traits") or [])
                        and r.get("archetype")):
                    self._dedicacao_de.setdefault(r["archetype"], r["id"])
        return self._dedicacao_de.get(arquetipo_id)

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
        # `_rank_de_arma` e chamado uma vez por arma citada em cada predicado,
        # e `candidatos()` avalia milhares de feats por slot -- varrer classes,
        # features e feats a cada chamada custaria caro por nada.
        self._remaps_cache: list | None = None
        self._bonus_memo: dict | None = None
        self.bonus_ignorados: dict = {}
        # escolhas anotadas para um nivel que o personagem ainda nao tem
        self.escolhas_de_nivel_futuro = 0
        # atomo de filtro de slot concedido que o avaliador nao conhece. Contado
        # e nao silenciado, pela mesma razao de `bonus_ignorados`.
        self.filtro_ignorado: dict = {}
        self.slots_concedidos: list = []
        self._derivar()

    # -- escolhas -----------------------------------------------------------

    def _escolhas(self, slot: str) -> list[dict]:
        return [e for e in self.doc.get("escolhas", []) if e.get("slot") == slot]

    def _derivar(self) -> None:
        self._niveis_de_classe()
        self._ancestria_e_background()
        self._features_de_classe()
        # antes de `_proficiencias`: a cadeia de grants poe class-feature na
        # lista de features e feat na lista de feats efetivos, e as duas coisas
        # sao lidas na derivacao de proficiencia, HP e requisito.
        self._grants_em_cadeia()
        # `_atributos` ANTES de `_proficiencias`: o orcamento de pericia e
        # "N plus your Intelligence modifier", e com a ordem antiga o INT ainda
        # nao existia quando a conta era feita -- um Mago de INT 18 tinha
        # direito a 6 pericias e o motor oferecia 2. Medido nos dois sentidos:
        # `_atributos` nao le nada que `_proficiencias` produz, e
        # `_proficiencias` nao le `atributos` nem `modificadores`.
        # Spec: `specs/2026-07-30-int-no-orcamento-de-pericia.md`
        self._atributos()
        self._proficiencias()
        self._hp()
        self._slots_de_feat()
        self._conjuracao()
        self._atores()
        self._focus()
        self._defesa()
        self._ataques()
        self._pericias_e_salvas()
        self._resistencias()
        self._velocidade()
        self._checar_requisitos()

    # -- regra 1: estrutura -------------------------------------------------

    def _niveis_de_classe(self) -> None:
        """Regra 1: nivel de personagem e a SOMA dos niveis de classe."""
        self.niveis_por_classe: dict[str, int] = defaultdict(int)
        self.ordem_de_classe: list[str] = []      # ordem de entrada de cada classe
        self.classe_do_nivel: dict[int, str] = {}  # nivel de personagem -> classe

        # ORDENAR POR NIVEL, nao pela ordem do array: a "primeira classe" de um
        # personagem e a que recebeu o NIVEL 1, e nao a que o jogador digitou
        # primeiro. Sem isto, reordenar o JSON muda `primeira_classe` e com ela
        # a regra 8 (o class feat de nivel 1 so vem da primeira classe) -- a
        # mesma ficha derivava `slots['class'] = [1,2,4]` ou `[2,4]` conforme a
        # ordem de digitacao. Achado pelo teste de embaralhamento em
        # testes/test_robustez.py, numa ficha multiclasse (com classe unica o
        # defeito e invisivel).
        por_nivel = sorted(self._escolhas("nivel_de_classe"),
                           key=lambda e: e["em"] if isinstance(e.get("em"), int) else 0)
        for e in por_nivel:
            cid = e.get("pega")
            if not isinstance(cid, str):
                self.avisos.append(f"nivel_de_classe sem classe em `pega`: {e}")
                continue
            if self.base.opcional(cid) is None:
                # barrar aqui e o que impede o id invalido de chegar nos passos
                # seguintes, que usam `base.get` e levantariam KeyError
                self.avisos.append(f"nivel_de_classe aponta pra classe ausente "
                                   f"da base: {cid}")
                continue
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

        # nivel de PERSONAGEM em que cada classe entrou -- e o ponto de partida
        # da regra 15 (cadencia extra so vale dali pra frente), usado tanto
        # pelos slots de feat quanto pelos aumentos de pericia
        self.entrada_da_classe: dict[str, int] = {}
        for nivel, cid in sorted(self.classe_do_nivel.items()):
            self.entrada_da_classe.setdefault(cid, nivel)

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
            return self.base.opcional(esc[0].get("pega")) if esc else None

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
                    # a LISTA, alem da contagem: `candidatos("subclasse")`
                    # precisa dos ids, e ate 2026-07-28 iterava `opcoes` -- que
                    # e um int -- e levantava TypeError. Nao explodia so porque
                    # nenhuma ficha de exemplo exercitava esse slot; o porte
                    # para TypeScript e que trouxe o caso a tona.
                    "opcoes_ids": list(bloco.get("opcoes") or []),
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
        # cada aplicacao, com o id de QUEM aplicou. E o que permite perguntar
        # depois "qual seria o rank sem este feat?" -- sem isso, um feat que
        # concede a mesma pericia que exige satisfaz o proprio requisito.
        self.aplicacoes_de_proficiencia: dict[str, list[tuple]] = defaultdict(list)

        self.proficiencia_ignorada: dict[str, int] = {}

        def aplicar(chave: str, rank: str, origem: str, origem_id=None) -> None:
            if rank not in RANKS:
                # 47 dos 1.071 valores de `proficiency` sao expressao do VTT, e
                # `melhor_rank` as rebaixava a `untrained` em silencio -- um
                # Azarketi Guerreiro 13 saia untrained nas armas que o feat
                # existe para elevar a master. `untrained` errado e pior que
                # ausencia, porque e uma AFIRMACAO.
                # Spec: `specs/2026-07-30-proficiencia-por-expressao.md`
                rank = self._rank_de_expressao(rank)
                if rank is None:
                    return
            anterior = self.proficiencias.get(chave)
            novo = melhor_rank(anterior, rank)
            self.proficiencias[chave] = novo
            self.aplicacoes_de_proficiencia[chave].append((rank, origem_id))
            if novo == rank and rank != anterior:
                self.origem_proficiencia[chave] = [origem]
            elif rank == novo:
                self.origem_proficiencia[chave].append(origem)

        for cid in self.ordem_de_classe:
            classe = self.base.get(cid)
            for g in self._grants_de(classe):
                if isinstance(g, dict) and "proficiency" in g:
                    for chave, rank in (g["proficiency"] or {}).items():
                        aplicar(chave, rank, classe.get("name", cid), cid)

        # as features de identidade tambem elevam rank (Weapon Mastery,
        # Expert Spellcaster, Reflex Expertise...). Sem isto a regra 7 entrega
        # a feature na lista e nao no numero.
        for f in self.features:
            for g in self._grants_de(f):
                if isinstance(g, dict) and "proficiency" in g:
                    for chave, rank in (g["proficiency"] or {}).items():
                        aplicar(chave, rank,
                                f"{f['nome']} ({f.get('classe') or f.get('origem')})",
                                f.get("raiz") or f.get("id"))

        # feat tambem eleva rank -- e a lacuna que deixava toda dedicacao
        # inerte. `wizard-dedication` e `{proficiency: {arcana: trained}}`,
        # exatamente a mesma chave plana que classe e feature ja usavam; sao
        # 342 feats com `proficiency`, 72 deles dedicacoes.
        for wb_id, feat, por in self._feats_efetivos():
            rotulo = feat.get("name", wb_id)
            if por:
                rotulo = f"{rotulo} (via {por})"
            # a RAIZ da cadeia, nao o elo: se a dedicacao X concedeu o feat Y,
            # o que Y aplica tem de ser descontado ao avaliar o requisito de X
            raiz = self._raiz_de(wb_id)
            for g in self._grants_de(feat):
                if not isinstance(g, dict):
                    continue
                for chave, rank in (g.get("proficiency") or {}).items():
                    aplicar(chave, rank, rotulo, raiz)
                for pericia in ((g.get("skill_training") or {}).get("auto") or []):
                    aplicar(pericia, "trained", rotulo, raiz)

        # regra 9: pericia automatica da classe e identidade, sempre concedida
        self.pericias_automaticas: dict[str, str] = {}
        for cid in self.ordem_de_classe:
            classe = self.base.get(cid)
            for g in self._grants_de(classe):
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
        self._gastar_pericias_livres(aplicar)
        self._escolhas_de_grant()
        # o aumento de pericia por nivel -- que todo personagem faz e o motor
        # nao implementava
        self._aumentos_de_pericia(aplicar)

    # teto RAW do aumento de pericia, por nivel de PERSONAGEM
    TETO_DE_RANK = ((15, "legendary"), (7, "master"), (1, "expert"))

    def _aumentos_de_pericia(self, aplicar) -> None:
        """Skill increase: sobe UM degrau numa pericia, nos niveis que a classe
        declara.

        O schema declarava `skill_increase` e o motor nao tinha uma linha a
        respeito -- entao a ficha saia com o rank de origem congelado, e a
        comparacao com os iconics media essa lacuna, nao o motor.

        A cadencia vem do dado, nunca de tabela escrita aqui: as 27 classes da
        base declaram `{levels: [...]}` -- 25 no padrao [3,5,..,19] e 2 (Ladino
        e Investigador) em todo nivel de 2 a 20. Vale a regra 15: a cadencia de
        uma classe conta a partir do nivel de personagem em que ela entrou.
        """
        niveis: set[int] = set()
        for cid, desde in self.entrada_da_classe.items():
            for g in self._grants_de(self.base.get(cid)):
                if not isinstance(g, dict) or "skill_increase" not in g:
                    continue
                for n in ((g["skill_increase"] or {}).get("levels") or []):
                    if desde <= int(n) <= self.nivel:
                        niveis.add(int(n))
        self.aumentos_de_pericia = sorted(niveis)

        # o default importa: nivel 0 e o ESTADO INICIAL do construtor (ainda
        # sem classe), e sem ele o `next` estoura StopIteration e o motor
        # inteiro morre antes de derivar qualquer coisa
        teto = next((r for n, r in self.TETO_DE_RANK if self.nivel >= n), "trained")
        # o recorte vale para a CHECAGEM e para a APLICACAO. Medido: um
        # Guerreiro 4 com aumento anotado para o nivel 8 ficava `trained` na
        # pericia -- rank que ele nao tem. `_atributos` ja nao aplicava o boost
        # futuro; aqui aplicava. Spec:
        # `specs/2026-07-30-escolha-de-nivel-futuro.md`
        escolhas = sorted((e for e in self._escolhas("skill_increase")
                           if not self._e_plano(e.get("em"))),
                          key=lambda e: e["em"] if isinstance(e.get("em"), int) else 0)

        if len(escolhas) > len(self.aumentos_de_pericia):
            self.avisos.append(
                f"skill_increase: {len(escolhas)} aumento(s) escolhido(s) para "
                f"{len(self.aumentos_de_pericia)} disponivel(is) em "
                f"{self.aumentos_de_pericia}")

        self.aumentos_detalhe = []
        for e in escolhas:
            em = e.get("em")
            if isinstance(em, int) and em not in self.aumentos_de_pericia:
                self.avisos.append(
                    f"skill_increase: aumento no nivel {em}, que nao tem "
                    f"aumento (niveis validos: {self.aumentos_de_pericia})")
            for pericia in (e["pega"] if isinstance(e.get("pega"), list) else [e.get("pega")]):
                if not isinstance(pericia, str):
                    continue
                # sem esta checagem, um nome errado vira uma linha de
                # proficiencia FANTASMA na ficha, sem nada apontando o erro.
                # `lore:<algo>` e legitimo -- Lore e aberto por definicao.
                if (not pericia.startswith("lore:")
                        and self.base.opcional(f"wb:skill/{norm_slug(pericia)}") is None):
                    self.avisos.append(
                        f"skill_increase: `{pericia}` nao e uma pericia da base "
                        f"-- aumento aplicado assim mesmo, confira o nome")
                atual = self.proficiencias.get(pericia, "untrained")
                proximo = RANKS[min(RANKS.index(atual) + 1, len(RANKS) - 1)]
                if RANKS.index(proximo) > RANKS.index(teto):
                    self.avisos.append(
                        f"skill_increase: {pericia} iria a {proximo}, acima do "
                        f"teto {teto} do nivel {self.nivel}")
                    proximo = teto
                aplicar(pericia, proximo, f"aumento de pericia (nivel {em})")
                self.aumentos_detalhe.append(
                    {"nivel": em, "pericia": pericia, "de": atual, "para": proximo})

    # `@actor.system.proficiencies.<grupo>.<chave>.rank` -> a nossa chave. O
    # Foundry separa por grupo (attacks/defenses); nos temos a chave plana.
    CHAVE_DO_VTT = {
        "attacks.unarmed": "unarmed", "attacks.simple": "simple",
        "attacks.martial": "martial", "attacks.advanced": "advanced",
        "defenses.unarmored": "unarmored", "defenses.light": "light",
        "defenses.medium": "medium", "defenses.heavy": "heavy",
    }

    def _rank_de_expressao(self, valor):
        """Rank vindo de expressao do VTT, ou `None` quando nao da para saber.

        `None` e deliberado e NAO e `untrained`: ausencia faz a tela perguntar,
        `untrained` faz o jogador atacar com o numero errado. Mesma escolha do
        `_resolver_valor` das resistencias, que devolve `None` em vez de zero.

        A expressao le `self.proficiencias`, que esta sendo montada na mesma
        passada. E correto porque `aplicar` roda em tres blocos nesta ordem --
        classes, features, feats -- e os 13 registros com expressao sao todos
        `feat`, lendo chaves que classe ou feature ja gravaram. Se um dia uma
        CLASSE trouxer expressao, ela le chave vazia e isto devolve `None`:
        degrada para ausencia, nunca para valor falso.

        Spec: `specs/2026-07-30-proficiencia-por-expressao.md`
        """
        if isinstance(valor, int) and not isinstance(valor, bool):
            return RANKS[valor] if 0 <= valor < len(RANKS) else None
        if not isinstance(valor, str):
            self.proficiencia_ignorada[str(valor)] = (
                self.proficiencia_ignorada.get(str(valor), 0) + 1)
            return None
        texto = valor.strip()
        if texto in RANKS:
            return texto

        m = re.fullmatch(r"@actor\.system\.proficiencies\.([\w.]+)\.rank", texto)
        if m:
            chave = self.CHAVE_DO_VTT.get(m.group(1))
            return self.proficiencias.get(chave) if chave else None

        m = re.fullmatch(r"max\((.+)\)", texto)
        if m:
            partes = [self._rank_de_expressao(x.strip())
                      for x in m.group(1).split(",")]
            vivos = [x for x in partes if x]
            return melhor_rank_de(vivos) if vivos else None

        # `ternary(gte(@actor.level,19),3,ternary(gte(@actor.level,13),2,1))`
        m = re.fullmatch(r"ternary\(gte\(@actor\.level,(\d+)\),(.+?),(.+)\)", texto)
        if m:
            corte = int(m.group(1))
            ramo = m.group(2) if self.nivel >= corte else m.group(3)
            ramo = ramo.strip()
            return self._rank_de_expressao(
                int(ramo) if ramo.isdigit() else ramo)

        self.proficiencia_ignorada[texto] = (
            self.proficiencia_ignorada.get(texto, 0) + 1)
        return None

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
            for g in self._grants_de(classe):
                livre = max(livre, int((g.get("skill_training") or {}).get("free") or 0))
            # "a number of additional skills equal to N plus your Intelligence
            # modifier" -- a prosa de cada classe. O INT entra UMA vez por
            # personagem e nao uma por classe: somar em cada uma daria a um Mago
            # 3/Ladino 3 o dobro. Entra na primeira, que e quem concede as
            # pericias iniciais. Modificador negativo REDUZ (a prosa nao tem
            # piso); o piso e do total, em zero, que e aritmetica.
            if cid == self.primeira_classe:
                livre = max(0, livre + int(self.modificadores.get("int", 0)))
            delta = max(0, livre - concedidas)
            concedidas += delta
            detalhe.append({"classe": classe.get("name", cid),
                            "orcamento": livre, "delta": delta})

        # feat que treina pericia a escolher SOMA (nao entra no max da regra
        # 10, que existe so pra impedir o multiclasse de multiplicar o
        # orcamento das CLASSES). Sao 37 feats, entre eles dedicacoes como
        # `battle-harbinger`, que da 1 pericia treinada a escolha.
        for wb_id, feat, por in self._feats_efetivos():
            for g in self._grants_de(feat):
                if not isinstance(g, dict):
                    continue
                livre = int((g.get("skill_training") or {}).get("free") or 0)
                if livre:
                    concedidas += livre
                    detalhe.append({"classe": feat.get("name", wb_id),
                                    "orcamento": livre, "delta": livre})

        self.pericias_livres = concedidas
        self.pericias_livres_detalhe = detalhe

    def _gastar_pericias_livres(self, aplicar) -> None:
        """Aplica as pericias que o JOGADOR escolheu, e cobra o que falta.

        Ate 2026-07-29 o orcamento era calculado (`pericias_livres: 3` aparecia
        na ficha) e **nunca gasto**: nao existia `_escolhas("pericias_livres")`
        em lugar nenhum do motor. Todo personagem saia sem nenhuma pericia
        treinada por escolha, nas 27 classes, que dao de 2 a 7.

        Achado ao alinhar a bancada de comparacao com o Pathbuilder, cujo
        personagem default sai com quatro pericias treinadas.

        Spec: `specs/2026-07-29-pericias-livres.md`
        """
        escolhidas: list[str] = []
        for e in self._escolhas("pericias_livres"):
            if isinstance(e.get("em"), int) and e["em"] > self.nivel:
                continue                      # escolha de nivel futuro nao conta
            for p in (e.get("pega") or []):
                if isinstance(p, str):
                    escolhidas.append(p)

        for p in escolhidas:
            # regra 9: pericia que a classe ja da de graca. Aplicar nao rebaixa
            # (a regra 4 mantem o melhor rank), mas a escolha foi jogada fora --
            # e na mesa o mestre manda escolher outra. Avisa, nao reprova.
            if p in self.pericias_automaticas:
                self.avisos.append(
                    f"pericias livres: `{p}` ja vem da classe "
                    f"({self.pericias_automaticas[p]}) -- escolha desperdicada")
            aplicar(p, "trained", "escolha do jogador")

        self.pericias_declaradas = len(escolhidas)
        if self.pericias_declaradas < self.pericias_livres:
            faltam = self.pericias_livres - self.pericias_declaradas
            self.avisos.append(
                f"pericias livres: {self.pericias_declaradas} declarada(s) de "
                f"{self.pericias_livres} a que o personagem tem direito -- "
                f"faltam {faltam}")
        elif self.pericias_declaradas > self.pericias_livres:
            self.avisos.append(
                f"pericias livres: {self.pericias_declaradas} declarada(s) para "
                f"{self.pericias_livres} de direito -- sobra "
                f"{self.pericias_declaradas - self.pericias_livres}")

    def _grants_de(self, reg) -> list:
        """Os grants de um registro, com a escolha do jogador ja resolvida.

        Um `grants` pode conter `{"choice": {"flag": ..., "opcoes": [...]}}`, e
        cada opcao carrega os grants que dependem DELA (spec
        `2026-07-29-choiceset.md`). Antes disso as consequencias ficavam soltas
        na raiz e o personagem recebia TODAS as opcoes -- Marshal Dedication
        dava Diplomacy E Intimidation, trained E expert.

        Aqui a opcao escolhida entra no fluxo como se fosse grant normal, e as
        outras nao entram. O marcador `choice` PERMANECE na lista, porque e ele
        que `slots_abertos` usa para oferecer o picker.

        Sem escolha declarada, NENHUMA opcao e aplicada -- o motor nao arbitra a
        escolha do jogador.
        """
        grants = (reg or {}).get("grants") or []
        if not any(isinstance(g, dict) and "choice" in g for g in grants):
            return grants
        escolhidos = {e["pega"] for e in self._escolhas("escolha_de_grant")
                      if isinstance(e.get("pega"), str)}
        saida = []
        for g in grants:
            saida.append(g)
            if not isinstance(g, dict) or "choice" not in g:
                continue
            escolha = g["choice"] or {}
            opcoes = escolha.get("opcoes")
            if not isinstance(opcoes, list):
                continue
            for o in opcoes:
                if not isinstance(o, dict):
                    continue
                if f"{escolha.get('flag')}:{o.get('valor')}" in escolhidos:
                    saida += [x for x in (o.get("grants") or [])
                              if isinstance(x, dict)]
        return saida

    def _escolhas_de_grant(self) -> None:
        """Escolha embutida em `grants` -- ex: Marshal Dedication, que da UMA
        entre Diplomacy e Intimidation.

        Ate 2026-07-29 o extrator guardava so a CONTAGEM de opcoes e soltava as
        consequencias ao lado, entao o personagem recebia TODAS -- Diplomacy E
        Intimidation, trained E expert. Agora as opcoes vem aninhadas com os
        grants de cada uma (spec `2026-07-29-choiceset.md`).

        ESTA FATIA SO MARCA. O que a opcao concede ainda NAO e aplicado, porque
        `grants` e lido em 14 pontos do motor e a expansao tem de valer em todos
        -- fatia propria. Marcar antes de aplicar e deliberado: sem isso a
        escolha sumiria em silencio, que e pior que o defeito que ela substitui.
        """
        self.escolhas_de_grant: list[dict] = []
        vistos = set()
        fontes = [(f.get("id"), f.get("nome"), f.get("grants") or [])
                  for f in self.features]
        fontes += [(i, feat.get("name", i), feat.get("grants") or [])
                   for i, feat, _ in self._feats_efetivos()]
        for origem_id, nome, grants in fontes:
            for g in grants:
                if not isinstance(g, dict) or "choice" not in g:
                    continue
                opcoes = (g["choice"] or {}).get("opcoes")
                if not isinstance(opcoes, list):
                    continue        # forma resumida: nao ha o que escolher aqui
                flag = (g["choice"] or {}).get("flag")
                chave = f"{origem_id}:{flag}"
                if chave in vistos:
                    continue
                vistos.add(chave)
                escolhido = next(
                    (e.get("pega") for e in self._escolhas("escolha_de_grant")
                     if isinstance(e.get("pega"), str)
                     and e["pega"].startswith(f"{flag}:")), None)
                self.escolhas_de_grant.append({
                    "origem": origem_id, "nome": nome, "flag": flag,
                    "opcoes": opcoes, "escolhido": escolhido})
                if escolhido is None:
                    rotulos = ", ".join(
                        str(o.get("rotulo") or o.get("valor")) for o in opcoes)
                    self.avisos.append(
                        f"{nome}: falta escolher `{flag}` ({rotulos})")

    # -- regra 8: atributos -------------------------------------------------

    # Os boosts livres do PF2e que NAO vem de `grants` -- sao regra fixa do
    # sistema, iguais para toda classe, e por isso nenhum registro os declara.
    #
    # Na CRIACAO sao 4, aplicados depois de ancestria, background e classe
    # ("Step 6: Finish Attribute Modifiers", 2e.aonprd.com/Rules.aspx?ID=2036).
    # Foi a parte que faltou na primeira versao deste orcamento: sem eles o
    # motor acusava "6 declarados de 5 de direito" numa ficha que na verdade
    # tinha direito a 9, e o aviso saia invertido -- apontando excesso onde
    # faltava.
    #
    # Depois, 4 a cada 5 niveis. Isto a base declara, na class-feature
    # `Ability Boosts`: "At 5th level and every 5 levels thereafter, you boost
    # four different ability scores".
    BOOSTS_DE_CRIACAO = 4
    NIVEIS_DE_BOOST = (5, 10, 15, 20)
    BOOSTS_POR_NIVEL = 4

    def _atributos(self) -> None:
        """Regra 8: o boost de habilidade-chave vem SO da primeira classe."""
        self.boosts: dict[str, int] = defaultdict(int)
        self.origem_boost: list[str] = []
        # o que o personagem tem DIREITO de escolher e ainda nao escolheu.
        # Sem esta lista, uma ficha sem `boosts_livres` declarado derivava com
        # todos os atributos em 10, HP menor, e nenhum aviso -- o app nao teria
        # como montar a lista de pendencias.
        self.boosts_pendentes: list[dict] = []

        def aplicar_boosts(lista, origem, origem_id=None):
            for b in lista or []:
                ab = b.get("ability_boost") if isinstance(b, dict) else None
                if not ab:
                    continue
                if ab.get("livre"):
                    qtd = ab.get("quantidade", 1)
                    self.origem_boost.append(f"{origem}: {qtd} livre(s)")
                    self.boosts_pendentes.append(
                        {"origem": origem, "origem_id": origem_id,
                         "quantidade": qtd, "opcoes": None, "em": "criacao"})
                    continue
                opcoes = ab.get("opcoes") or []
                if len(opcoes) == 1:
                    self.boosts[opcoes[0]] += ab.get("quantidade", 1)
                    self.origem_boost.append(f"{origem}: +{opcoes[0]}")
                else:
                    self.origem_boost.append(f"{origem}: escolha entre {opcoes}")
                    self.boosts_pendentes.append(
                        {"origem": origem, "origem_id": origem_id,
                         "quantidade": ab.get("quantidade", 1),
                         "opcoes": opcoes, "em": "criacao"})

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
                self.boosts_pendentes.append(
                    {"origem": f"{classe.get('name')} (habilidade-chave)",
                     "origem_id": self.primeira_classe, "quantidade": 1,
                     "opcoes": chaves, "em": 1})
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

        self._orcamento_de_boost()

        self.atributos = {a: 10 + 2 * self.boosts.get(a, 0) for a in ATRIBUTOS}
        self.modificadores = {a: (v - 10) // 2 for a, v in self.atributos.items()}

    def _orcamento_de_boost(self) -> None:
        """Quantos boosts o personagem tem DIREITO contra quantos declarou.

        Mesma forma da higiene de slot (item 63) e do orcamento de pericia
        (regra 10): o motor ja sabia LER cada fonte de boost, mas nunca somava
        o direito nem confrontava com o gasto. Resultado: ficha sem
        `boosts_livres` saia com tudo 10 e a suite inteira verde.

        Os 4 boosts de nivel (5, 10, 15, 20) sao regra fixa do PF2e e nao
        aparecem em `grants` de lugar nenhum -- por isso entram aqui.
        """
        self.boosts_pendentes.append(
            {"origem": "criacao (4 livres)", "origem_id": None,
             "quantidade": self.BOOSTS_DE_CRIACAO, "opcoes": None, "em": "criacao"})
        for n in self.NIVEIS_DE_BOOST:
            if n <= self.nivel:
                self.boosts_pendentes.append(
                    {"origem": f"nivel {n}", "origem_id": None,
                     "quantidade": self.BOOSTS_POR_NIVEL, "opcoes": None, "em": n})

        direito = sum(b["quantidade"] for b in self.boosts_pendentes)
        declarado = sum(
            len(e.get("pega") or []) for e in self._escolhas("boosts_livres")
            if not (isinstance(e.get("em"), int) and e["em"] > self.nivel))

        self.boosts_direito = direito
        self.boosts_declarados = declarado
        if declarado < direito:
            faltam = direito - declarado
            de_onde = ", ".join(
                f"{b['origem']} ({b['quantidade']})" for b in self.boosts_pendentes)
            self.avisos.append(
                f"boosts de atributo: {declarado} declarado(s) de {direito} a que "
                f"o personagem tem direito -- faltam {faltam}. Fontes: {de_onde}")
        elif declarado > direito:
            self.avisos.append(
                f"boosts de atributo: {declarado} declarado(s) para {direito} "
                f"de direito -- {declarado - direito} a mais")

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
            for g in self._grants_de(classe):
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
        for wb_id, feat, por in self._feats_efetivos():
            for g in self._grants_de(feat):
                fm = g.get("flat_modifier") if isinstance(g, dict) else None
                if not fm or fm.get("selector") != "hp":
                    continue
                valor = self._resolver_valor(fm.get("value"))
                if valor:
                    total += valor
                    self.hp_detalhe.append({
                        "origem": feat.get("name", wb_id), "hp": valor,
                        "nota": f"feat ({fm.get('value')})"
                                + (f" via {por}" if por else "")})
        self.hp = total

    def _feats_escolhidos(self):
        for e in self.doc.get("escolhas", []):
            wb_id = e.get("pega")
            if isinstance(wb_id, str) and wb_id.startswith("wb:feat/"):
                feat = self.base.opcional(wb_id)
                if feat is not None:
                    yield wb_id, feat

    # A gramatica INTEIRA que a base usa em `value`, medida nos 233 `resistance`
    # e nos 1.709 `flat_modifier`: inteiro, as duas variaveis abaixo, `+`, `/`,
    # `floor()` e `max()`. Nao ha multiplicacao, nao ha subtracao e o unico
    # aninhamento e `max(1, floor(...))`. Isto e um mini-avaliador dessa
    # gramatica, e nao um interpretador do Foundry.
    # Spec: `specs/2026-07-30-resistencia-e-formula.md`
    _FORMULA_OK = re.compile(r"^(?:floor|max|[\d\s+/(),])*$")

    def _resolver_valor(self, expressao):
        """Resolve a expressao do Foundry no valor deste personagem.

        Regra 19: em texto de regra impresso, "your level" significa **nivel de
        personagem** -- e `@actor.level` e exatamente isso.

        Devolve `None` para o que estiver FORA da gramatica. Antes devolvia
        zero, e zero e uma resposta: um `resistance` de `@actor.abilities.str.mod`
        saia como "resistencia 0" em vez de "nao sei calcular". Quem chama
        decide o que fazer com o nulo -- o HP, por exemplo, nao soma.
        """
        if isinstance(expressao, bool):
            return None
        if isinstance(expressao, (int, float)):
            return int(expressao)
        texto = str(expressao or "").strip()
        if not texto:
            return None
        texto = texto.replace("@actor.details.level.value", str(self.nivel))
        texto = texto.replace("@actor.level", str(self.nivel))
        if "@armor.system.runes.potency" in texto:
            texto = texto.replace("@armor.system.runes.potency",
                                  str(self._potencia_de_armadura()))
        return self._avaliar_formula(texto)

    def _potencia_de_armadura(self) -> int:
        """A runa de potencia da armadura EQUIPADA, ou 0 sem armadura.

        Mesma leitura do `_defesa`: a runa vem do registro (202 armaduras da
        base tem `runes`) ou da entrada do inventario.
        """
        for entrada in (self.doc.get("inventario") or []):
            if not entrada.get("equipado"):
                continue
            reg = self.base.opcional(str(entrada.get("item") or "")) or {}
            if reg.get("kind") != "armor":
                continue
            return max(int(entrada.get("potencia") or 0),
                       int((reg.get("runes") or {}).get("potency") or 0))
        return 0

    def _avaliar_formula(self, texto: str):
        """`floor()`, `max()`, `+` e `/` inteira. Fora disso, `None`."""
        if not self._FORMULA_OK.match(texto):
            return None
        try:
            return self._reduzir(texto)
        except (ValueError, ZeroDivisionError, IndexError):
            return None

    def _reduzir(self, texto: str):
        texto = texto.strip()
        # reduz a funcao mais INTERNA primeiro, para `max(1, floor(x/2))` sair
        m = re.search(r"(floor|max)\(([^()]*)\)", texto)
        while m:
            args = [self._reduzir(a) for a in m.group(2).split(",")]
            if any(a is None for a in args):
                return None
            valor = args[0] if m.group(1) == "floor" else max(args)
            texto = texto[:m.start()] + str(valor) + texto[m.end():]
            m = re.search(r"(floor|max)\(([^()]*)\)", texto)
        if "(" in texto or ")" in texto:
            return None
        total = 0
        for parcela in texto.split("+"):
            parcela = parcela.strip()
            if not parcela:
                return None
            # divisao INTEIRA para baixo, que e o que `floor(a/b)` significa --
            # e o unico uso de `/` na base esta sempre dentro de um `floor`
            partes = [int(x.strip()) for x in parcela.split("/")]
            valor = partes[0]
            for d in partes[1:]:
                valor //= d
            total += valor
        return total

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
        extras: dict[str, set[int]] = {k: set(v) for k, v in basica.items()}
        for cid, desde in self.entrada_da_classe.items():
            classe = self.base.get(cid)
            for g in self._grants_de(classe):
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

        # Regra do livro que nao vive em `feat_slot`: ha feat e heranca que
        # CONCEDEM outro feat. `Ancient Elf` diz "You gain the multiclass
        # dedication feat for that class" -- e um slot novo, nao uma cadencia.
        # O Foundry escreve isso como ChoiceSet com `itemType: "feat"` e um
        # filtro; sao 101 na fonte. Sem este passo o jogador escolhia
        # `Ancient Elf` e nao era perguntado nada.
        #
        # A familia vizinha ("when you gain an ancestry feat, you can choose
        # from aiuvarin feats") NAO entra aqui: ela alarga o pool de um slot que
        # ja existe, e trata-la como slot daria feat de graca. O Foundry nao
        # escreve ChoiceSet nela, entao a separacao vem da fonte e nao de
        # heuristica de prosa.
        # Spec: `specs/2026-07-30-slot-de-feat-concedido.md`
        self.slots_concedidos = []
        fontes = [(self.heranca, "criacao"), (self.ancestria, "criacao"),
                  (self.background, "criacao")]
        fontes += [(f, self._nivel_do_feat(i)) for i, f, _ in self._feats_efetivos()]
        for reg, em in fontes:
            if not reg:
                continue
            for g in self._grants_de(reg):
                ch = g.get("choice") if isinstance(g, dict) else None
                if not isinstance(ch, dict) or ch.get("tipo") != "feat":
                    continue
                self.slots_concedidos.append({
                    "origem": reg.get("name"), "origem_id": reg.get("id"),
                    "em": em, "flag": ch.get("flag"),
                    "filtro": ch.get("filtro"),
                })
        # regra 2: Free Archetype sempre ligado -- slot em todo nivel par
        self.slots["free_archetype"] = [n for n in range(1, self.nivel + 1) if n % 2 == 0]

        # regra 8: o class feat de nivel 1 so vem da PRIMEIRA classe
        self.class_feat_nivel_1 = 1 in (self.slots.get("class") or [])
        if 1 in (self.slots.get("class") or []) and self.primeira_classe:
            concede = any(
                1 in ((g.get("feat_slot") or {}).get("levels") or [])
                and (g.get("feat_slot") or {}).get("kind") == "class"
                for g in self._grants_de(self.base.get(self.primeira_classe))
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

        self._higiene_de_slot()

    # cada slot do documento e a lista de niveis que o alimenta
    SLOT_PARA_CADENCIA = {
        "class_feat": "class", "skill_feat": "skill", "general_feat": "general",
        "ancestry_feat": "ancestry", "free_archetype": "free_archetype",
    }

    def _e_plano(self, em) -> bool:
        """A escolha esta acima do nivel atual? Entao e plano, nao erro.

        Contado em `escolhas_de_nivel_futuro`: silenciar por decisao e diferente
        de silenciar por descuido, e so o contador distingue os dois depois.
        """
        if isinstance(em, int) and em > self.nivel:
            self.escolhas_de_nivel_futuro += 1
            return True
        return False

    def _higiene_de_slot(self) -> None:
        """Confronta o que foi GASTO com o que existe de slot.

        Ate aqui o motor colecionava `gastos` e `slots` lado a lado sem nunca
        compara-los: um pick de Free Archetype no nivel 3 (onde nao ha slot),
        tres picks para dois slots, ou um class feat puro ocupando o slot
        gratuito passavam os tres em silencio.

        Principio zero: isto SINALIZA, nunca recusa. A escolha continua no
        documento e a ficha continua derivando.
        """
        for slot, cadencia in self.SLOT_PARA_CADENCIA.items():
            niveis = self.slots.get(cadencia) or []
            # escolha ACIMA do nivel atual e PLANO, nao erro: no nivel 8 o
            # personagem vai ter o slot, e a lista `niveis` so enumera os que
            # existem ate o nivel de hoje. Avisar sobre o futuro treina o
            # jogador a ignorar aviso, que e o pior resultado possivel para um
            # mecanismo de aviso. `_atributos` ja tratava assim; aqui e
            # `_aumentos_de_pericia` tratavam como erro -- tres semanticas no
            # mesmo motor. Spec: `specs/2026-07-30-escolha-de-nivel-futuro.md`
            usados = [e for e in (self.gastos.get(slot) or [])
                      if not self._e_plano(e.get("em"))]

            if len(usados) > len(niveis):
                self.avisos.append(
                    f"slot {slot}: {len(usados)} escolha(s) para "
                    f"{len(niveis)} slot(s) disponivel(is) em {niveis}")

            for e in usados:
                em = e.get("em")
                # `em` nao-inteiro DESLIGAVA a checagem: um feat posto em
                # `criacao` por engano passava calado. As cinco cadencias sao
                # todas por NIVEL -- nenhuma delas nasce na criacao --, entao
                # aqui a string e erro, e nao dispensa. (O slot
                # `feat_concedido`, que pode nascer em `criacao`, nao e
                # cadencia e nao passa por este laco.)
                # Item 73(b) do review adversarial de 2026-07-27.
                if not isinstance(em, int):
                    self.avisos.append(
                        f"slot {slot}: escolha com nivel {em!r}, que nao e "
                        f"nivel -- este slot so existe por nivel ({niveis})")
                    continue
                if em not in niveis:
                    self.avisos.append(
                        f"slot {slot}: escolha no nivel {em}, que nao tem "
                        f"slot desse tipo (niveis validos: {niveis})")

        # o slot de Free Archetype (regra 2) so aceita feat de ARQUETIPO --
        # e a unica coisa que o distingue do slot de class feat. Sem esta
        # checagem ele vira um segundo class feat de graca em toda ficha.
        for e in self.gastos.get("free_archetype") or []:
            wb_id = e.get("pega")
            if not isinstance(wb_id, str):
                continue
            feat = self.base.opcional(wb_id)
            if feat is None:
                continue
            if "archetype" not in (feat.get("traits") or []):
                self.avisos.append(
                    f"slot free_archetype: {feat.get('name', wb_id)} nao tem "
                    f"trait `archetype` -- o slot gratuito so aceita feat de "
                    f"arquetipo")

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
            # Feiticeiro, Bruxa e Invocador nao tem tradicao fixa: a classe traz
            # uma FRASE ("variavel (definida pela escolha de bloodline...)") e
            # quem responde e a subclasse. Sem esta resolucao a frase ia crua
            # para a ficha, no campo que decide quais magias ele pode aprender.
            # Spec: `specs/2026-07-30-tradicao-por-subclasse.md`
            tradicao = sc.get("tradition")
            if tradicao not in ("arcane", "divine", "occult", "primal"):
                tradicao = self._tradicao_por_escolha(
                    classe, {"de": "subclasse"}, classe.get("name", cid))
            self.conjuracao.append({
                "classe": classe.get("name", cid),
                "nivel_de_classe": nivel_classe,
                "tradicao": tradicao,
                "tipo": sc.get("type"),
                "slots": tabela.get("ranks") or {},
                "truques": tabela.get("cantrips"),
                "max_rank_do_slot": max_rank_cru,
                "rank_efetivo": rank_efetivo,
                "elevacao": max(0, rank_efetivo - max_rank_cru),
                "rank_de_invocacao": self.cap_invocacao(nivel_classe),  # regra 17b
                "dc": self._dc_de_conjuracao(classe, nivel_classe, sc),
            })
        self._conjuracao_de_arquetipo()

    # teto de rank por degrau da cadeia, RAW ("Spellcasting Archetypes"):
    # Basic vai ate rank 3, Expert ate 6, Master ate 8. So a dedicacao, sem
    # nenhum degrau, da cantrip e nada de slot.
    TETO_DO_DEGRAU = {"basic": 3, "expert": 6, "master": 8}

    def _conjuracao_de_arquetipo(self) -> None:
        """A rota de conjuracao que a dedicacao abre -- ate 2026-07-29, invisivel.

        13 dedicacoes prometem conjuracao na prosa e a ficha nao mostrava nada.
        Sob Free Archetype (regra 2, sempre ligada) essa e a rota mais comum de
        um personagem nao-conjurador.

        O rank vem do FEAT que o personagem pegou, nao do nivel dele: a tabela
        `RANK_DEDICACAO` descreve a rota completa e serve de piso para a regra
        21, mas na ficha real quem so tem Basic para no rank 3 mesmo no nivel
        20. Spec: specs/2026-07-29-spellcasting-de-arquetipo.md.
        """
        for origem_id, reg, _ in self._feats_efetivos():
            for g in self._grants_de(reg):
                if not isinstance(g, dict) or "grant_spellcasting" not in g:
                    continue
                gs = g["grant_spellcasting"] or {}
                degraus = gs.get("degraus") or {}
                tidos = [d for d, fid in degraus.items() if self._tem_feat(fid)]
                teto = max((self.TETO_DO_DEGRAU.get(d, 0) for d in tidos), default=0)
                # a tabela oficial, limitada pelo degrau que ele realmente tem
                rank = min(self.rank_de_dedicacao(), teto)
                tradicao = gs.get("tradicao")
                if tradicao == "escolha":
                    tradicao = self._tradicao_por_escolha(reg, gs)
                self.conjuracao.append({
                    "classe": (self.base.opcional(gs.get("cadeia") or "") or {})
                              .get("name") or reg.get("name"),
                    "de_arquetipo": True,
                    "origem": origem_id,
                    "nivel_de_classe": None,
                    "tradicao": tradicao,
                    "tipo": gs.get("tipo"),
                    # RAW: um slot de cada rank ate o teto vigente
                    "slots": {str(r): 1 for r in range(1, rank + 1)},
                    "truques": gs.get("truques", 2),
                    "max_rank_do_slot": rank,
                    # regra 18: arquetipo roda RAW puro, entao NAO eleva
                    "rank_efetivo": rank,
                    "elevacao": 0,
                    "rank_de_invocacao": rank,
                    "dc": self._dc_de_arquetipo(),
                })

    def _tem_feat(self, feat_id: str | None) -> bool:
        if not feat_id:
            return False
        alvo = self.base.resolver(feat_id)
        return any(self.base.resolver(i) == alvo
                   for i, _, _ in self._feats_efetivos())

    def _tradicao_por_escolha(self, reg: dict, gs: dict,
                              classe: str | None = None) -> str | None:
        """Sorcerer usa a tradicao do bloodline; a Bruxa, a do patron.

        Sem a escolha feita nao da para saber, e ARBITRAR aqui poria uma
        tradicao errada na ficha em silencio -- mesmo tratamento do grau do
        companheiro: avisa e devolve `None`.

        `classe` e o NOME da classe cuja conjuracao esta sendo resolvida, e sem
        ele um Feiticeiro 5 / Bruxa 3 sai com a mesma tradicao nas duas linhas:
        a varredura devolvia a primeira escolha de subclasse que tivesse
        tradicao, qualquer que fosse a classe dona. A rota de arquetipo nao
        passa o filtro porque ali a escolha e unica por cadeia.

        Spec: `specs/2026-07-30-tradicao-por-subclasse.md`
        """
        eixo = gs.get("de")
        for e in self.doc.get("escolhas", []):
            if e.get("slot") != "subclasse":
                continue
            escolhido = self.base.opcional(e.get("pega") or "") or {}
            if classe and classe not in (escolhido.get("class") or [classe]):
                continue
            trad = ((escolhido.get("spellcasting") or {}).get("tradition")
                    or escolhido.get("tradition"))
            if trad in ("arcane", "divine", "occult", "primal"):
                return trad
        self.avisos.append(
            f"{reg.get('name')}: a tradicao vem da escolha de "
            f"{eixo or 'subclasse'}, que ainda nao foi feita -- slots sem "
            f"tradicao ate resolver")
        return None

    def _dc_de_arquetipo(self) -> dict:
        """Regra 3, como todo o resto: nivel de PERSONAGEM + rank.

        A dedicacao concede `trained` na tradicao e nao sobe sozinha -- quem
        sobe e a cadeia, quando a prosa diz. Ate haver dado disso, trained.
        """
        rank = "trained"
        return {"rank": rank, "dc": 10 + self.nivel + RANK_BONUS[rank],
                "ataque": self.nivel + RANK_BONUS[rank],
                "nota": "conjuracao de arquetipo: trained pela dedicacao"}

    # -- regra 17b: teto para o que cria criatura ---------------------------

    # Rank de slot que a dedicacao de conjuracao concede, por nivel de
    # PERSONAGEM. Citado verbatim da regra "Spellcasting Archetypes" (Player
    # Core, dump do AoN category=rules): "Basic Spellcasting Feat: usually
    # available at 4th level, these feats grant a 1st-rank spell slot. At 6th
    # level, a 2nd-rank spell slot. At 8th level, a 3rd-rank spell slot.
    # Expert: 12th -> 4th-rank, 14th -> 5th, 16th -> 6th.
    # Master: 18th -> 7th-rank, 20th -> 8th-rank."
    RANK_DEDICACAO = [(20, 8), (18, 7), (16, 6), (14, 5), (12, 4),
                      (8, 3), (6, 2), (4, 1)]

    def rank_de_dedicacao(self, nivel_personagem: int | None = None) -> int:
        """O que a rota GRATUITA entrega neste nivel de personagem.

        Sob Free Archetype (regra 2, sempre ligada) a dedicacao nao custa nada
        alem do slot gratuito de arquetipo, e pela regra 18 ela roda RAW puro.
        E por isso que ela e o piso: qualquer coisa que custe nivel de classe
        tem de render pelo menos isto.
        """
        n = self.nivel if nivel_personagem is None else nivel_personagem
        return next((r for lvl, r in self.RANK_DEDICACAO if n >= lvl), 0)

    def cap_invocacao(self, nivel_classe: int) -> int:
        """Rank maximo de magia com trait `summon` ou `incarnate` (regra 17b).

            min( max( ceil(class_level/2) + 2 , rank_de_dedicacao ), ceil(nivel/2) )

        Tres termos, cada um com um trabalho:

        - `ceil(class_level/2) + 2` -- a folga que a houserule concede a quem
          gastou nivel de classe;
        - `rank_de_dedicacao` -- o PISO da regra 21: gastar um nivel inteiro de
          personagem tem de render pelo menos o que a dedicacao entrega de
          graca sob Free Archetype. Sem ele a simulacao de 2026-07-27 achou 50
          de 204 pares violando, com o dip chegando a **0%** da dedicacao no
          nivel 20 -- criatura nivel 2 contra AC 45 nao acerta nem com nat 20;
        - `ceil(nivel/2)` -- o teto de heightened, que vale para tudo e faz a
          regra se autoproteger: com classe unica os dois niveis sao iguais,
          nem a folga nem o piso chegam a valer, e o RAW sai intacto sem caso
          especial.
        """
        folga = math.ceil(nivel_classe / 2) + 2
        return min(max(folga, self.rank_de_dedicacao()), math.ceil(self.nivel / 2))

    def cap_ator(self, nivel_classe: int) -> int:
        """Nivel maximo de companheiro, familiar ou eidolon.

        Sem o `/2`, de proposito. Rank de magia ja nasce em escala de metade do
        nivel; nivel de criatura esta na mesma escala do nivel de personagem.
        Dividir por dois faria um Ranger 12 PURO cair para companheiro nivel 6,
        quebrando classe unica == RAW.
        """
        return min(nivel_classe + 2, self.nivel)

    def eleva_por_invocacao(self, magia: dict) -> bool:
        """A magia cria criatura que age sozinha? Deriva so de trait.

        `summon` (14 magias) e `incarnate` (23) nao tem interseccao -- a
        segunda cobre as invocacoes de rank 4 a 10. Spirit Link e Protector
        Tree NAO entram: nao criam nada, sao efeito continuo.
        """
        traits = set(magia.get("traits") or [])
        return bool(traits & {"summon", "incarnate"})

    # Avanco do companheiro, RAW (Player Core p.206 e 211), citado no relatorio
    # docs/2026-07-27_atores.md. `nimble` e `savage` partem de `mature`, entao
    # os ajustes sao cumulativos com ele.
    AVANCO = {
        "young":  {"attr": {}, "dados": 1, "dano_extra": 0, "pericias": {}},
        "mature": {"attr": {"str": 1, "dex": 1, "con": 1, "wis": 1},
                   "dados": 2, "dano_extra": 0,
                   "pericias": {"perception": "expert", "fortitude": "expert",
                                "reflex": "expert", "will": "expert",
                                "intimidation": "trained", "stealth": "trained",
                                "survival": "trained"}},
        "nimble": {"attr": {"str": 2, "dex": 3, "con": 2, "wis": 2},
                   "dados": 2, "dano_extra": 2,
                   "pericias": {"perception": "expert", "fortitude": "expert",
                                "reflex": "expert", "will": "expert",
                                "intimidation": "trained", "stealth": "trained",
                                "survival": "trained", "acrobatics": "expert"}},
        "savage": {"attr": {"str": 3, "dex": 2, "con": 2, "wis": 2},
                   "dados": 2, "dano_extra": 3,
                   "pericias": {"perception": "expert", "fortitude": "expert",
                                "reflex": "expert", "will": "expert",
                                "intimidation": "trained", "stealth": "trained",
                                "survival": "trained", "athletics": "expert"}},
    }
    # RAW: "trained in its unarmed attacks, unarmored defense, barding, all
    # saving throws, Perception, Acrobatics, and Athletics"
    PROF_BASE = ["unarmed", "unarmored", "barding", "fortitude", "reflex",
                 "will", "perception", "acrobatics", "athletics"]

    # Feats reais na base (pipeline/base/index.json, kind=feat) que concedem
    # cada avanco. Usados para DERIVAR o teto de maturidade em vez de ler
    # `ator["maturidade"]` como resultado pronto. Cada lista cobre aliases
    # duplicados que a base carrega para o mesmo feat (ex.: "Mature Animal
    # Companion" e "Mature Animal Companion (Druid)" sao o mesmo texto, mesma
    # fonte, dois ids -- artefato do dump, nao duas regras).
    FEATS_MATURIDADE = {
        "mature": {
            "wb:class/druid": ["wb:feat/mature-animal-companion",
                                "wb:feat/mature-animal-companion-druid"],
            "wb:class/ranger": ["wb:feat/mature-animal-companion-ranger"],
        },
        "incredible": {
            "wb:class/druid": ["wb:feat/incredible-companion",
                                "wb:feat/incredible-companion-druid"],
            "wb:class/ranger": ["wb:feat/incredible-companion-ranger"],
        },
        "specialized": {
            "wb:class/druid": ["wb:feat/specialized-companion-druid"],
            "wb:class/ranger": ["wb:feat/specialized-companion-ranger"],
        },
    }
    # Arquetipo Animal Trainer (Pathfinder #152: Legacy of the Lost God):
    # trilha PROPRIA, gate por character_level -- isso e RAW normal de
    # arquetipo, nao houserule, e essa trilha nao passa pelas feats de
    # Druid/Ranger acima. Mature Trained Companion / Splendid Companion /
    # Specialized Companion (Animal Trainer) equivalem a
    # mature/incredible/specialized dessa trilha independente.
    FEATS_MATURIDADE_ARQUETIPO = {
        "mature": ["wb:feat/mature-trained-companion"],
        "incredible": ["wb:feat/splendid-companion"],
        "specialized": ["wb:feat/specialized-companion-animal-trainer"],
    }
    ORDEM_TIER = ["young", "mature", "incredible"]

    # RAW (rules-2120, Player Core p.211, "Specialized Animal Companions"):
    # "Its proficiency rank for unarmed attacks increases to expert. Its
    # proficiency ranks for saving throws and Perception increase to master.
    # Increase its Dexterity modifier by 1 and its Intelligence modifier by 2.
    # Its unarmed attack damage increases from two dice to three dice, and it
    # increases its additional damage with unarmed attacks from 2 to 4 or from
    # 3 to 6." O dano extra sempre DOBRA (nimble 2->4, savage 3->6) -- por
    # isso o codigo multiplica em vez de gravar os dois numeros na tabela.
    #
    # O "extra benefit" por TIPO de especializacao (Ambusher/Bully/Daredevil/
    # Racer/Tracker/Wrecker) NAO esta aqui: e escolha do jogador sem campo no
    # schema nem na base, entao nao da pra derivar -- ver docs/2026-07-27_atores.md.
    SPECIALIZADO = {
        "attr_delta": {"dex": 1, "int": 2},
        "dados": 3,
        "pericias_upgrade": {"unarmed": "expert", "perception": "master",
                              "fortitude": "master", "reflex": "master",
                              "will": "master"},
    }

    def _maturidade_do_companheiro(self, cid: str | None) -> tuple[str, bool]:
        """Deriva o teto de maturidade dos feats de avanco REALMENTE
        escolhidos (nao so presentes no requisito -- escolhidos de fato),
        conferindo o requisito de cada um contra o nivel de CLASSE que
        concedeu o companheiro. E a houserule central deste ponto: um Ranger
        6 dentro de um personagem 20 so passa disso se tiver 6 niveis de
        Ranger, porque `class_level` no `requires` do feat e comparado com
        `self.nivel_de(cid)`, nunca com `self.nivel`.

        A trilha do arquetipo Animal Trainer usa `character_level` porque
        isso e RAW normal de arquetipo, sem desvio.

        Devolve (tier, especializado). `tier` em young/mature/incredible;
        `especializado` marca se o teto real e specialized, que so existe em
        cima de incredible (Specialized Animal Companions, Player Core p.211)."""
        escolhidos = {wb_id for wb_id, _ in self._feats_escolhidos()}

        def valido(feat_ids) -> bool:
            for fid in feat_ids:
                if fid not in escolhidos:
                    continue
                feat = self.base.opcional(fid)
                if feat is not None and self.avaliar(feat.get("requires"))[0]:
                    return True
            return False

        tier = "young"
        if cid and valido(self.FEATS_MATURIDADE["mature"].get(cid, [])):
            tier = "mature"
            if valido(self.FEATS_MATURIDADE["incredible"].get(cid, [])):
                tier = "incredible"
        if valido(self.FEATS_MATURIDADE_ARQUETIPO["mature"]):
            tier = max(tier, "mature", key=self.ORDEM_TIER.index)
            if valido(self.FEATS_MATURIDADE_ARQUETIPO["incredible"]):
                tier = max(tier, "incredible", key=self.ORDEM_TIER.index)

        especializado = False
        if tier == "incredible":
            if cid and valido(self.FEATS_MATURIDADE["specialized"].get(cid, [])):
                especializado = True
            if valido(self.FEATS_MATURIDADE_ARQUETIPO["specialized"]):
                especializado = True
        return tier, especializado

    # Feats que ABREM ESCOLHA (nimble ou savage) em vez de decidir sozinhos --
    # o mesmo padrao de `ChoiceSet` que o Foundry usa em ~243 dos 6.044 feats
    # (medido no pin atual, ver docs/2026-07-27_atores.md). A base ainda nao
    # extrai esse tipo de escolha PARA FEATS (so para eixo de subclasse, em
    # `classe["subclasses"]`), entao aqui o feat e citado a mao. Splendid
    # Companion (arquetipo Animal Trainer) tambem abre a mesma escolha --
    # texto do feat, Pathfinder #152 p.76: "It becomes a nimble or savage
    # animal companion (your choice)".
    FEATS_QUE_ABREM_ESCOLHA = {
        "wb:feat/incredible-companion": ["nimble", "savage"],
        "wb:feat/incredible-companion-druid": ["nimble", "savage"],
        "wb:feat/incredible-companion-ranger": ["nimble", "savage"],
        "wb:feat/splendid-companion": ["nimble", "savage"],
    }

    def _resolver_grau_incredible(self, ator: dict, tier: str) -> tuple[str | None, dict | None]:
        """`tier` (young/mature/incredible) ja vem derivado dos feats. Incredible
        Companion (e Splendid Companion) nao dizem sozinhos se o companheiro
        fica nimble ou savage -- e escolha do jogador, aberta pelo feat.

        Registrada com o MESMO vocabulario que o eixo de subclasse ja usa
        (`eixo`/`nivel`/`slot`/`escolhe`/`opcoes`, ver `classe["subclasses"]`
        e `self.slots_de_subclasse`), para o front poder reusar o mesmo
        componente de picker -- e nao um campo ad-hoc feito so pra isso. A
        escolha do jogador mora no `escolhas` do proprio ator (mesmo lugar
        onde `{"slot": "animal", "pega": ...}` ja vive), no slot novo
        `grau_avancado`.

        Devolve (grau_resolvido_ou_None, entrada_do_picker_ou_None). SEM
        escolha feita, `grau` vem None -- nao ha default silencioso para
        nimble nem para young. Escolha nao feita e estado legitimo; quem
        chamar decide como exibir a ficha enquanto isso (aqui: capada no
        ultimo grau CERTO, `mature`)."""
        if tier != "incredible":
            return tier, None

        escolhidos = {wb_id for wb_id, _ in self._feats_escolhidos()}
        feat_id = next((fid for fid in self.FEATS_QUE_ABREM_ESCOLHA if fid in escolhidos), None)
        feat = self.base.opcional(feat_id) if feat_id else None
        opcoes = self.FEATS_QUE_ABREM_ESCOLHA.get(feat_id, ["nimble", "savage"])

        declarado = next((e.get("pega") for e in (ator.get("escolhas") or [])
                          if e.get("slot") == "grau_avancado"), None)
        escolhido = declarado if declarado in opcoes else None

        entrada = {
            "origem": "feat",
            "feat": feat_id,
            "nome_do_feat": (feat or {}).get("name", feat_id),
            "ator": ator.get("nome") or "",
            "eixo": "grau-incredible-companion",
            "nivel": (feat or {}).get("level"),
            "slot": "grau_avancado",
            "escolhe": 1,
            "opcoes": opcoes,
            "escolhido": escolhido,
        }
        if escolhido is None:
            self.avisos.append(
                f"companheiro {ator.get('nome') or ''}: {entrada['nome_do_feat']} "
                f"aberto, falta escolher entre {'/'.join(opcoes)} (slot "
                f"`grau_avancado` no `escolhas` do ator)")
        return escolhido, entrada

    def _concessoes_de_ator(self) -> None:
        """Quem, nesta ficha, CONCEDE um ator -- e em que nivel.

        Sem isto o companheiro so entrava por `doc["atores"]` escrito a mao:
        pegar `Animal Companion` no nivel 1 nao mudava nada na ficha e nao
        gerava aviso. O termo `grant_actor` vem do passo 7f do pipeline
        (`derivar_concessao_de_ator.py`), derivado da prosa oficial.

        A `classe` sai do NIVEL em que o feat foi pego, e nao de casar nome de
        classe com o id do feat -- `wb:feat/animal-companion` nao carrega a
        classe no nome, e o cap da regra 17b depende dela.
        """
        self.concessoes_de_ator: list[dict] = []
        em_de = {}
        for e in self.doc.get("escolhas", []):
            pega = e.get("pega")
            if isinstance(pega, str) and isinstance(e.get("em"), int):
                em_de.setdefault(pega, e["em"])

        vistos = set()
        for origem_id, reg, _ in self._feats_efetivos():
            vistos.add(origem_id)
            self._coletar_grant_actor(origem_id, reg, em_de.get(origem_id))
        for f in self.features:
            if f.get("id") and f["id"] not in vistos:
                vistos.add(f["id"])
                self._coletar_grant_actor(f["id"], self.base.opcional(f["id"]) or f,
                                          em_de.get(f["id"]))

    def _coletar_grant_actor(self, origem_id: str, reg: dict, em) -> None:
        for g in self._grants_de(reg):
            if not isinstance(g, dict) or "grant_actor" not in g:
                continue
            ga = g["grant_actor"] or {}
            self.concessoes_de_ator.append({
                "origem": origem_id,
                "origem_nome": reg.get("name") or origem_id,
                "em": em,
                "tipo": ga.get("tipo") or "companheiro",
                "escolhe": ga.get("escolhe") or "animal-companion",
                "opcoes": list(ga.get("opcoes") or []),
                "classe": self.classe_do_nivel.get(em) if isinstance(em, int) else None,
                "preenchida": False,
                "escolhido": None,
                # a fonte declara as PROPRIAS excecoes a regra de um ator por
                # vez: "Contrary to the usual rules for animal companions, this
                # feat can grant you a SECOND animal companion". Sao 6 dos 30
                # concessores, e sem esta marca uma regra geral de exclusao
                # reprovaria justo o que o livro autoriza por escrito.
                # Spec: `specs/2026-07-30-segundo-ator.md`
                "adicional": bool(ga.get("adicional")),
            })

    def _avisar_ator_duplicado(self) -> None:
        """Mais de um ator do mesmo tipo sem nenhuma fonte que autorize.

        AVISO e nao bloqueio: bloquear apagaria escolha ja feita pelo jogador, e
        este projeto marca em vez de sumir -- a mesma postura de
        `fora_do_requisito`. A regra geral esta na fonte (`Familiars`, AoN: "You
        can have only one familiar at a time"); a excecao tambem.
        """
        por_tipo: dict[str, list] = defaultdict(list)
        for c in self.concessoes_de_ator:
            por_tipo[str(c.get("tipo"))].append(c)
        for tipo, lista in sorted(por_tipo.items()):
            if len(lista) < 2 or any(c.get("adicional") for c in lista):
                continue
            origens = ", ".join(sorted(c.get("origem_nome") or "?" for c in lista))
            self.avisos.append(
                f"{len(lista)} fontes de {tipo} na ficha ({origens}) e nenhuma "
                f"delas declara conceder um adicional -- pelo livro vale um por "
                f"vez")

    def _casar_ator_com_concessao(self, ator: dict) -> dict | None:
        """`concedido_por` + `em`. O `em` desempata quando o mesmo feat concede
        duas vezes (Mammoth Lord da um segundo companheiro) e e opcional: ator
        antigo, sem `em`, casa com a primeira concessao daquela origem."""
        origem = ator.get("concedido_por")
        if not origem:
            return None
        candidatas = [c for c in self.concessoes_de_ator
                      if c["origem"] == origem and id(c) not in self._casadas]
        if ator.get("em") is not None:
            exatas = [c for c in candidatas if c["em"] == ator["em"]]
            candidatas = exatas or candidatas
        if not candidatas:
            return None
        escolhida = candidatas[0]
        self._casadas.add(id(escolhida))
        escolhida["preenchida"] = True
        escolhida["escolhido"] = next(
            (e.get("pega") for e in (ator.get("escolhas") or [])
             if e.get("slot") == "animal"), None)
        return escolhida

    def _atores(self) -> None:
        """Ficha do companheiro, familiar e eidolon.

        Nivel pela regra 17b; o resto e RAW puro -- "animal companions
        calculate their modifiers and DCs just as you do", entao bonus =
        nivel + rank + atributo, exatamente como o personagem.
        """
        self._concessoes_de_ator()
        self._avisar_ator_duplicado()
        self.atores = []
        self.escolhas_de_feat: list[dict] = []
        self._casadas: set[int] = set()
        for a in self.doc.get("atores") or []:
            concessao = self._casar_ator_com_concessao(a)
            if a.get("concedido_por") and concessao is None:
                self.avisos.append(
                    f"ator {a.get('nome') or ''}: `concedido_por` aponta para "
                    f"{a['concedido_por']}, que nao esta na ficha ou nao concede "
                    f"ator -- o feat pode ter sido removido depois")
            cid, nota = self._classe_do_ator(a, concessao)
            nivel_classe = self.nivel_de(cid) if cid else self.nivel
            ator = {
                "tipo": a.get("tipo"),
                "nome": a.get("nome") or "",
                "concedido_por": a.get("concedido_por"),
                "em": a.get("em"),
                "classe": (self.base.opcional(cid) or {}).get("name") if cid else None,
                "nivel_de_classe": nivel_classe,
                "nivel": self.cap_ator(nivel_classe),
                "nota": nota,
                "escolhas": a.get("escolhas") or [],
            }
            if a.get("tipo") == "companheiro":
                tier, especializado = self._maturidade_do_companheiro(cid)
                grau, pendente = self._resolver_grau_incredible(a, tier)
                if pendente:
                    self.escolhas_de_feat.append(pendente)
                if grau is None and especializado:
                    self.avisos.append(
                        f"companheiro {a.get('nome') or ''}: Specialized "
                        f"Companion detectado, mas o grau nimble/savage ainda "
                        f"nao foi escolhido -- specialized nao aplicado ate "
                        f"resolver")
                if grau is None:
                    especializado = False
                ator["grau_pendente"] = grau is None
                ator.update(self._ficha_de_companheiro(a, ator["nivel"],
                                                        grau or "mature", especializado))
            self.atores.append(ator)

    def _ficha_de_companheiro(self, ator: dict, nivel: int, grau: str,
                              especializado: bool) -> dict:
        """RAW, Player Core p.206: atributos do stat block com os ajustes de
        avanco; HP de ancestria mais (6 + CON) por nivel; proficiencia treinada
        na lista base, elevada pelo avanco. `grau` e `especializado` ja vem
        DERIVADOS dos feats (`_maturidade_do_companheiro` /
        `_resolver_grau_incredible`) -- aqui e so aplicar os numeros."""
        pega = next((e.get("pega") for e in (ator.get("escolhas") or [])
                     if e.get("slot") == "animal"), None)
        especie = self.base.opcional(pega or "") or {}
        st = especie.get("stats") or {}
        if not st:
            return {"aviso": f"especie do companheiro nao encontrada: {pega}"}

        av = self.AVANCO.get(grau) or self.AVANCO["young"]
        attr = dict(st.get("atributos") or {})
        for k, v in av["attr"].items():
            attr[k] = attr.get(k, 0) + v
        dados = av["dados"]
        dano_extra = av["dano_extra"]
        pericias_av = dict(av["pericias"])

        # Specialized Animal Companions (Player Core p.211, rules-2120): delta
        # por cima do nimble/savage ja acumulado -- ver SPECIALIZADO.
        if especializado:
            for k, v in self.SPECIALIZADO["attr_delta"].items():
                attr[k] = attr.get(k, 0) + v
            dados = self.SPECIALIZADO["dados"]
            dano_extra *= 2
            pericias_av.update(self.SPECIALIZADO["pericias_upgrade"])

        # RAW: "ancestry Hit Points from its type, plus a number of Hit Points
        # equal to 6 plus its Constitution modifier for each level you have"
        hp = int(st.get("hp") or 0) + (6 + attr.get("con", 0)) * nivel

        prof = {k: "trained" for k in self.PROF_BASE}
        for p in (st.get("pericia_inicial") or []):
            prof[p.lower()] = "trained"
        for k, v in pericias_av.items():
            # "if it was already trained in one of those skills from its type,
            # increase its proficiency rank in that skill to expert"
            if v == "trained" and prof.get(k) == "trained":
                prof[k] = "expert"
            else:
                prof[k] = v

        def bonus(chave, atributo):
            return nivel + RANK_BONUS[prof.get(chave, "untrained")] + attr.get(atributo, 0)

        ataques = []
        for atk in (st.get("ataques") or []):
            dado = str(atk.get("dano") or "")
            face = dado.split("d")[-1] if "d" in dado else None
            agil = "agile" in (atk.get("traits") or [])
            # finesse usa DEX quando compensa; o resto e STR, como no personagem
            usa = "dex" if ("finesse" in (atk.get("traits") or [])
                            and attr.get("dex", 0) > attr.get("str", 0)) else "str"
            dano = (f"{dados}d{face}" if face else "?")
            mod = attr.get("str", 0) + dano_extra
            ataques.append({
                "nome": atk.get("nome"),
                "ataque": bonus("unarmed", usa),
                "dano": f"{dano}{mod:+d}" if mod else dano,
                "tipo": atk.get("tipo"),
                "traits": atk.get("traits") or [],
                "agil": agil,
            })

        return {
            "especie": especie.get("name"),
            "maturidade": grau,
            "especializado": especializado,
            "tamanho": st.get("tamanho"),
            "velocidade": st.get("velocidade"),
            "sentidos": st.get("sentidos"),
            "atributos": attr,
            "hp": hp,
            "hp_detalhe": f"{st.get('hp')} de ancestria + (6 {attr.get('con',0):+d}) x {nivel}",
            "ac": 10 + attr.get("dex", 0) + nivel + RANK_BONUS[prof["unarmored"]],
            "proficiencias": prof,
            "saves": {s: bonus(s, {"fortitude": "con", "reflex": "dex",
                                   "will": "wis"}[s])
                      for s in ("fortitude", "reflex", "will")},
            "percepcao": bonus("perception", "wis"),
            "ataques": ataques,
            "support": st.get("support_benefit"),
            "manobra_avancada": st.get("advanced_maneuver") if grau in ("nimble", "savage") else None,
        }

    def _classe_do_ator(self, ator: dict,
                        concessao: dict | None = None) -> tuple[str | None, str | None]:
        """De qual classe veio o ator. `classe` explicito ganha; depois a
        CONCESSAO que criou o ator; depois o `concedido_por` por nome; senao
        assume a classe de maior nivel e AVISA -- chutar em silencio daria o
        cap errado sem ninguem perceber."""
        if ator.get("classe"):
            return ator["classe"], None
        # a concessao sabe em que NIVEL o feat foi pego, e o nivel diz a classe.
        # E o unico caminho que acerta num `wb:feat/animal-companion`, cujo id
        # nao carrega classe nenhuma.
        if concessao and concessao.get("classe"):
            return concessao["classe"], None
        origem = ator.get("concedido_por")
        if origem:
            for cid in self.ordem_de_classe:
                nome = (self.base.opcional(cid) or {}).get("name", "")
                if nome and nome.lower().replace(" ", "-") in origem:
                    return cid, None
        if not self.ordem_de_classe:
            return None, "sem classe para ancorar o nivel do ator"
        maior = max(self.ordem_de_classe, key=self.nivel_de)
        return maior, (f"classe de origem nao declarada; usei "
                       f"{(self.base.opcional(maior) or {}).get('name')} "
                       f"(a de maior nivel). Declare `classe` no ator para "
                       f"travar o cap da regra 17b")

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

    # -- AC e ataque: a ficha tem que trazer os numeros ---------------------

    def _equipados(self, kind: str) -> list[dict]:
        saida = []
        for item in self.doc.get("inventario", []):
            if not item.get("equipado") and not item.get("investido"):
                continue
            reg = self.base.opcional(item.get("item", ""))
            if reg is not None and reg.get("kind") == kind:
                saida.append({"registro": reg, "entrada": item})
        return saida

    def _defesa(self) -> None:
        """AC = 10 + DEX (limitado pelo cap da armadura) + proficiencia + item.

        Regra 3 vale aqui como em tudo: o bonus de proficiencia e
        `nivel_de_personagem + rank`, e o rank sai da categoria da armadura que
        esta sendo usada -- que pode ter vindo de qualquer classe (regra 4).
        """
        dex = self.modificadores.get("dex", 0)
        armaduras = self._equipados("armor")
        escudos = self._equipados("shield")

        if armaduras:
            arm = armaduras[0]["registro"]
            categoria = arm.get("armor_category") or "unarmored"
            cap = arm.get("dex_cap")
            dex_usada = min(dex, cap) if isinstance(cap, int) else dex
            item_bonus = int(arm.get("ac_bonus") or 0)
            # mesma regra da arma: a runa vem do registro (armadura magica da
            # base, 202 tem `runes`) OU da entrada do inventario (o jogador
            # gravou numa armadura comum). Antes so a segunda era lida.
            runas_arm = arm.get("runes") or {}
            potencia = max(int(armaduras[0]["entrada"].get("potencia") or 0),
                           int(runas_arm.get("potency") or 0))
            nome = arm.get("name")
            penalidade = arm.get("check_penalty")
            forca = arm.get("strength")
        else:
            categoria, dex_usada, item_bonus, potencia = "unarmored", dex, 0, 0
            nome, penalidade, forca = "sem armadura", None, None

        rank = self.proficiencias.get(categoria, "untrained")
        prof = (self.nivel + RANK_BONUS[rank]) if rank != "untrained" else 0

        # o `item_bonus` da armadura E um bonus de item, e os 6 grants
        # incondicionais de `ac` da base tambem sao (Bands of Force, Assassin's
        # Bracers). Somar um sobre o outro daria +2 a quem veste Couro e Bands
        # of Force, onde o RAW da +1 -- bonus do mesmo tipo nao empilham. Por
        # isso a armadura entra como CONTENDOR, e nao como parcela.
        # A runa de potencia soma ao bonus da armadura ANTES da disputa: pelo
        # RAW ela aumenta o bonus de item, nao e um segundo bonus de item.
        contendores = []
        if item_bonus or potencia:
            contendores.append(("item", item_bonus + potencia, nome))
        extras = self._bonus_incondicionais().get("ac", [])
        contendores += list(extras)
        bonus_de_item = self._melhor_por_tipo(contendores)
        total = 10 + dex_usada + prof + bonus_de_item

        # a penalidade de armadura so vale se a FOR nao alcanca o minimo
        aplica_penalidade = (isinstance(forca, int)
                             and self.atributos.get("str", 10) < forca)

        self.ac = {
            "total": total,
            "armadura": nome,
            "categoria": categoria,
            "rank": rank,
            "detalhe": f"10 + DEX {dex_usada:+d} + prof {prof} "
                       f"({rank}, nivel {self.nivel}) + item {bonus_de_item}",
            # de onde veio cada contendor, para a ficha poder explicar por que
            # dois itens de +1 nao viraram +2
            "bonus": [{"tipo": t, "valor": v, "origem": o}
                      for t, v, o in contendores],
            "dex_perdida": max(0, dex - dex_usada),
            "check_penalty": penalidade if aplica_penalidade else 0,
            "escudo": ({"nome": escudos[0]["registro"].get("name"),
                        "ac": int(escudos[0]["registro"].get("ac_bonus") or 0)}
                       if escudos else None),
        }

    def _ataques(self) -> None:
        """Ataque = nivel + rank da categoria + atributo + item; dano = dados + atributo.

        `finesse` deixa usar DEX no ataque; o dano continua em FOR, salvo
        excecao que depende de feature (Thief usa DEX, e isso vem de rule
        element com predicado -- por isso nao esta aqui).
        """
        self.ataques = []
        for equipado in self._equipados("weapon"):
            arma = equipado["registro"]
            entrada = equipado["entrada"]
            traits = {str(t).lower() for t in (arma.get("traits") or [])}
            categoria = arma.get("weapon_category") or "simple"
            # pelo `weapon:<slug>`, e nao pela categoria crua: e por aqui que o
            # remap de `weapon_proficiency` chega ao BONUS DE ATAQUE. Sem isto o
            # conserto do item 75 ficaria so no predicado, e o numero na ficha
            # -- que e o que o jogador olha -- continuaria errado.
            # Spec: `specs/2026-07-30-proficiencia-de-arma-nomeada.md`
            rank = (self._rank_de_arma("weapon:" + arma["id"].split("/")[-1], None)
                    or self.proficiencias.get(categoria, "untrained"))
            prof = (self.nivel + RANK_BONUS[rank]) if rank != "untrained" else 0

            forca = self.modificadores.get("str", 0)
            destreza = self.modificadores.get("dex", 0)
            usa_dex = "finesse" in traits and destreza > forca
            atributo = destreza if usa_dex else forca
            # arma a distancia usa DEX no ataque e nao soma atributo no dano
            distancia = bool(arma.get("range")) and "thrown" not in traits
            if distancia:
                atributo, usa_dex = destreza, True

            # RUNAS: vem de dois lugares e os dois contam. O registro da base
            # traz as runas EMBUTIDAS no item magico (974 armas tem
            # `runes: {potency, striking, property}`), e a entrada do inventario
            # traz o que o jogador gravou numa arma comum. Ate 2026-07-29 o
            # motor lia so `entrada.potencia` -- entao equipar uma arma magica
            # da base nao somava nada, e `striking` era ignorado em qualquer
            # caso: um `+1 striking longsword` saia com 1d8 no lugar de 2d8.
            runas = arma.get("runes") or {}
            potencia = max(int(entrada.get("potencia") or 0),
                           int(runas.get("potency") or 0))
            striking = max(int(entrada.get("striking") or 0),
                           int(runas.get("striking") or 0))
            propriedade = sorted({str(p) for p in (runas.get("property") or [])}
                                 | {str(p) for p in (entrada.get("property") or [])})

            dano = arma.get("damage") or {}
            # cada grau de striking soma UM dado do mesmo tamanho
            dados = int(dano.get("dados", 1) or 1) + striking
            mod_dano = 0 if distancia else forca

            self.ataques.append({
                "arma": arma.get("name"),
                "categoria": categoria,
                "rank": rank,
                "ataque": self.nivel + RANK_BONUS[rank] + atributo + potencia
                          if rank != "untrained" else atributo + potencia,
                "atributo_do_ataque": "dex" if usa_dex else "str",
                "dano": f"{dados}{dano.get('dado', '')}"
                        f"{mod_dano:+d}" if mod_dano else
                        f"{dados}{dano.get('dado', '')}",
                "tipo_de_dano": dano.get("tipo") or dano.get("type"),
                "potencia": potencia,
                "striking": striking,
                "runas_de_propriedade": propriedade,
                "traits": sorted(traits),
                "detalhe": f"nivel {self.nivel} + prof {prof} ({rank}) + "
                           f"{'DEX' if usa_dex else 'FOR'} {atributo:+d}",
            })

    # -- regra 3: bonus derivado --------------------------------------------

    def bonus(self, chave: str) -> int:
        """Regra 3: bonus total = nivel_de_personagem + rank. Rank 0 = sem nivel."""
        rank = self.proficiencias.get(chave, "untrained")
        if rank == "untrained":
            return 0
        return self.nivel + RANK_BONUS[rank]

    def _subclasse_de(self, classe_id: str) -> str | None:
        """A sub-escolha que este personagem fez para a classe dada.

        A ordem e a da FONTE, e nao a do documento. Uma classe tem VARIOS
        eixos (o Mago tem `arcane-school`, `arcane-thesis` e `outras-opcoes`), e
        percorrer as escolhas do jogador fazia a resposta depender de qual delas
        vinha antes no array -- mesma ficha, resposta diferente. Era a ultima
        dependencia de ordem que sobrou depois do conserto de `ordem_de_classe`.

        Spec: `specs/2026-07-30-pendencias-do-review.md`
        """
        classe = self.base.opcional(classe_id) or {}
        escolhidas = {e.get("pega") for e in self._escolhas("subclasse")}
        for bloco in (classe.get("subclasses") or []):
            for o in (bloco.get("opcoes") or []):
                if o in escolhidas:
                    return o
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

    def _rank_sem(self, chave: str, excluir: str | None) -> str:
        """O rank que a pericia teria se `excluir` nao estivesse na ficha.

        Existe por causa do requisito circular: `acrobat-dedication` EXIGE
        acrobatics trained e CONCEDE acrobatics. Desde que o motor passou a
        aplicar grants de feat, o requisito passou a ser satisfeito pelo
        proprio feat, e a ficha saia limpa onde antes sinalizava. Medido: 25
        termos auto-satisfeitos entre os 6.273 feats com `requires`.
        """
        atual = self.proficiencias.get(chave, "untrained")
        if not excluir:
            return atual
        restante = "untrained"
        for rank, origem_id in self.aplicacoes_de_proficiencia.get(chave, []):
            if origem_id != excluir:
                restante = melhor_rank(restante, rank)
        return restante

    def _rank_de_arma(self, chave: str, excluir: str | None) -> str | None:
        """`weapon:aldori-dueling-sword` cai na CATEGORIA da arma.

        Ninguem preenche uma proficiencia por arma nomeada -- a ficha guarda
        rank por categoria (simple/martial/advanced). Sem esta ponte, um
        Guerreiro 6, que e TREINADO em advanced desde o nivel 1, aparecia
        untrained na Aldori Dueling Sword e a `Aldori Duelist Dedication` saia
        como fora do requisito. Achado comparando com o Pathbuilder, que libera
        as duas -- e ali ele esta certo.

        Rank NOMEADO ganha quando existe: feat que treina uma arma especifica
        (`weapon_proficiency`) escreve a chave propria, e ela e mais precisa que
        a categoria.
        """
        if not chave.startswith("weapon:"):
            return None
        if chave in self.proficiencias:
            return None
        pedido = chave.split(":", 1)[1]

        # `weapon:*` pergunta "voce e expert em ALGUMA arma?", e era letra
        # morta: `wb:weapon/*` nao resolve, a chave literal caia em `_rank_sem`
        # e voltava untrained SEMPRE. Cinco feats ficavam inalcancaveis
        # (`reaper-of-repose`, `diverse-weapon-expert`...). Mesmo tratamento do
        # `lore:*`, que ja responde o melhor rank.
        if pedido == "*":
            return melhor_rank_de(
                [self._rank_sem(c, excluir) for c in self.CATEGORIAS_DE_ARMA])

        arma = self.base.opcional("wb:weapon/" + pedido)
        if not arma:
            return None
        ranks = []
        categoria = arma.get("weapon_category")
        if categoria:
            ranks.append(self._rank_sem(str(categoria), excluir))
        # Feat de familiaridade nao concede treino: REMAPEIA categoria ("trate
        # arco marcial como simples"). O melhor entre nativa e remapeada, nunca
        # so a remapeada -- ler o RAW ao pe da letra faria um Guerreiro expert
        # em marcial CAIR para trained ao pegar `Archer Dedication`.
        # Spec: `specs/2026-07-30-proficiencia-de-arma-nomeada.md`
        for igual_a, definicao in self._remaps_de_arma():
            if igual_a and self._arma_casa(arma, definicao):
                ranks.append(self._rank_sem(str(igual_a), excluir))
        return melhor_rank_de(ranks) if ranks else None

    # as quatro categorias que `weapon:*` varre. `unarmed` entra porque o RAW
    # trata ataque desarmado como proficiencia de arma.
    CATEGORIAS_DE_ARMA = ("simple", "martial", "advanced", "unarmed")

    def _remaps_de_arma(self) -> list[tuple]:
        """Todos os `weapon_proficiency` ativos na ficha, como (igual_a, definicao).

        91 ocorrencias em 54 registros, e ate agora nenhuma era lida: um `grep`
        por `weapon_proficiency` no motor dava um unico hit, dentro de um
        docstring.
        """
        if self._remaps_cache is not None:
            return self._remaps_cache
        saida = []
        fontes = [self.base.get(cid) for cid in self.ordem_de_classe]
        fontes += [f for f in self.features]
        fontes += [feat for _, feat, _ in self._feats_efetivos()]
        for reg in fontes:
            for g in self._grants_de(reg):
                if not isinstance(g, dict):
                    continue
                wp = g.get("weapon_proficiency")
                if isinstance(wp, dict):
                    saida.append((wp.get("igual_a"), wp.get("definicao")))
        self._remaps_cache = saida
        return saida

    def _arma_casa(self, arma: dict, no) -> bool:
        """A arma satisfaz este `definicao`?

        Gramatica medida: 28 formas estruturais, mas so quatro seletores
        importam -- `base`, `category`, `trait` e `group` cobrem 76 das 91
        ocorrencias inteiras. Seletor que o motor nao conhece, ou valor
        dinamico (`{item|flags...}`), NAO CASA -- e como o remap so ADICIONA
        rank, o principio zero fica intacto por construcao: o que o motor nao
        entende nunca vira reprovacao, so deixa de conceder.
        """
        if isinstance(no, list):
            return all(self._arma_casa(arma, x) for x in no)
        if isinstance(no, dict):
            if "or" in no:
                alvo = no["or"]
                itens = alvo if isinstance(alvo, list) else [alvo]
                return any(self._arma_casa(arma, x) for x in itens)
            if "and" in no:
                alvo = no["and"]
                itens = alvo if isinstance(alvo, list) else [alvo]
                return all(self._arma_casa(arma, x) for x in itens)
            if "not" in no:
                return not self._arma_casa(arma, no["not"])
            return False
        if not isinstance(no, str) or not no.startswith("item:"):
            return False
        partes = no.split(":", 2)
        if len(partes) < 3 or "{" in partes[2]:
            return False                      # sem valor, ou placeholder do VTT
        seletor, valor = partes[1], norm_slug(partes[2])
        if seletor == "category":
            return norm_slug(str(arma.get("weapon_category") or "")) == valor
        if seletor == "group":
            return norm_slug(str(arma.get("group") or "")) == valor
        if seletor == "trait":
            return valor in {norm_slug(t) for t in (arma.get("traits") or [])}
        if seletor == "base":
            return norm_slug(arma.get("id", "").split("/")[-1]) == valor
        return False

    def _slug_de_lore(self, bruto: str) -> str:
        """`Alcohol Lore` e `alcohol` sao a mesma pericia.

        O sufixo ` Lore` sai antes do slug porque e assim que o parser escreve
        (`extratores/feats.py`), e o apostrofo some antes de hifenizar pelo
        mesmo motivo -- `slug()` de la remove, `norm_slug()` daqui nao.
        """
        s = re.sub(r"\s+lore$", "", str(bruto or "").strip(), flags=re.I)
        return norm_slug(s.replace("'", "").replace("’", ""))

    def _rank_de_lore(self, chave: str, excluir: str | None) -> str | None:
        """`lore:alcohol` cai na Lore da ficha chamada `Alcohol Lore`.

        Duas convencoes para a mesma pericia: o predicado escreve o slug sem o
        sufixo, a ficha guarda o nome humano com ele. Sem esta ponte, requisito
        de Lore NOMEADA e insatisfazivel por construcao -- em 35 registros,
        nenhum personagem atendia com nenhuma escolha. Achado comparando com o
        Pathbuilder: um Barkeep, que tem Alcohol Lore em RAW, aparecia untrained
        para o `Seasoned`.

        `lore:*` le-se "alguma Lore" e devolve o MELHOR rank da ficha, porque o
        requisito pode pedir mais que trained (`Scrollmaster` pede expert).
        """
        if not chave.startswith("lore:"):
            return None
        pedido = chave.split(":", 1)[1]
        melhor: str | None = None
        for k in self.proficiencias:
            if not k.startswith("lore:"):
                continue
            if pedido != "*" and self._slug_de_lore(k.split(":", 1)[1]) != pedido:
                continue
            melhor = melhor_rank(melhor, self._rank_sem(k, excluir))
        return melhor

    def _termo_proficiency(self, valor) -> tuple[bool, str]:
        excluir = getattr(self, "_avaliando", None)
        for chave, exigencia in (valor or {}).items():
            tenho = (self._rank_de_arma(chave, excluir)
                     or self._rank_de_lore(chave, excluir)
                     or self._rank_sem(chave, excluir))
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
        # RECORTE TEMPORAL: escolha feita DEPOIS da que esta sendo avaliada nao
        # pode satisfazer o pre-requisito dela. Sem isto, pegar `Dueling Dance`
        # no nivel 2 e `Dueling Parry` no 12 -- ordem ilegal -- passava limpo,
        # porque no fim das contas o personagem "tem" as duas. A ficha e
        # historico, nao foto.
        # Spec: `specs/2026-07-29-recorte-temporal-do-has.md`
        ate = getattr(self, "_avaliando_em", None)

        def no_tempo(e) -> bool:
            if not isinstance(ate, int):
                return True                    # sem contexto, olha tudo
            em = e.get("em")
            # `criacao` antecede todo nivel; `em` nao numerico nao recorta
            return not isinstance(em, int) or em <= ate

        tudo = {e.get("pega") for e in self.doc.get("escolhas", [])
                if isinstance(e.get("pega"), str) and no_tempo(e)}
        # `excluir is None or ...`, e nao so a comparacao: feature vinda da
        # PROGRESSAO da classe nao tem `raiz` (e None), e `_avaliando` tambem e
        # None fora de `_checar_requisitos` -- entao `None != None` dava False e
        # a feature era DESCARTADA. Em `candidatos()`, que e a pergunta central
        # do app, `_avaliando` nunca e setado: toda class-feature ficava
        # invisivel para o `has`. Sao 139 clausulas em 135 registros
        # (`spellstrike` 21, `arcane-cascade` 12, `ki-spells` 12), ou seja um
        # Magus nunca podia pegar feat de Spellstrike. Achado pela comparacao
        # com o Pathbuilder (Cleric 20 / `Martyr`).
        excluir = getattr(self, "_avaliando", None)
        tudo |= {f["id"] for f in self.features
                 if excluir is None or f.get("raiz") != excluir}
        # o que a cadeia concedeu conta como "tenho": no jogo nao ha diferenca
        # entre o Streetwise que voce pegou e o que a dedicacao te deu. Mas o
        # que o PROPRIO feat concedeu nao pode satisfazer o requisito dele.
        tudo |= {c["id"] for c in self.concedidos
                 if excluir is None or c["raiz"] != excluir}
        tudo |= {c for c in self.ordem_de_classe}
        for reg in (self.ancestria, self.heranca, self.background):
            if reg:
                tudo.add(reg["id"])
        # comparar pelo id CANONICO dos dois lados: `requires` de 24 feats cita
        # o nome pre-remaster (`stunning-fist` pelo `stunning-blows`), e sem
        # resolver o alias o requisito nunca era satisfeito
        canonico = self.base.resolver(valor)
        if canonico in {self.base.resolver(t) for t in tudo}:
            return True, ""
        nome = (self.base.opcional(canonico) or {}).get("name", valor)
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

    def _sentidos(self) -> dict:
        """Todo `grants.sense` que a ficha carrega, por tipo.

        81 registros da base concedem sentido e **ninguem lia** -- mesmo padrao
        do companheiro: o dado existia, o consumidor nao. Isso deixava
        `low-light vision` (11 ocorrencias) e `darkvision` sem como serem
        respondidos no pre-requisito, e a ficha sem dizer o que o personagem
        enxerga.
        """
        if getattr(self, "_cache_sentidos", None) is not None:
            return self._cache_sentidos
        achados: dict[str, dict] = {}
        origens = [(i, self.base.opcional(i) or {}) for i, _, _ in self._feats_efetivos()]
        origens += [(f["id"], self.base.opcional(f["id"]) or {})
                    for f in self.features if f.get("id")]
        for reg in (self.ancestria, self.heranca, self.background):
            if reg and reg.get("id"):
                origens.append((reg["id"], reg))
        # `senses` no TOPO do registro, so em ancestria (37): `{"low_light": true}`.
        # Sem isto, um Elfo (que declara so assim) nao atendia `low-light vision`.
        for origem_id, reg in origens:
            for chave, ligado in (reg.get("senses") or {}).items():
                if ligado:
                    achados.setdefault(self._slug_de_sentido(chave), {
                        "tipo": chave, "acuidade": None, "alcance": None,
                        "origem": reg.get("name") or origem_id})
            for g in self._grants_de(reg):
                if not isinstance(g, dict) or "sense" not in g:
                    continue
                # `sense` vem como dict (`{tipo, acuidade, alcance}`) na maioria
                # e como STRING crua em parte dos registros -- as duas formas
                # existem na base, e tratar so a primeira estourava na segunda
                sense = g["sense"]
                sense = sense if isinstance(sense, dict) else {"tipo": sense}
                tipo = self._slug_de_sentido(sense.get("tipo") or "")
                if not tipo:
                    continue
                achados.setdefault(tipo, {
                    "tipo": sense.get("tipo"),
                    "acuidade": sense.get("acuidade"),
                    "alcance": sense.get("alcance"),
                    "origem": (reg.get("name") or origem_id),
                })
        self._cache_sentidos = achados
        return achados

    # a fonte escreve `low_light` e o pre-requisito diz `low-light vision`:
    # sem o alias, a mesma coisa vira duas chaves e o termo nunca casa
    ALIAS_DE_SENTIDO = {"low-light": "low-light-vision",
                        "lowlight": "low-light-vision",
                        "low-light-vision": "low-light-vision"}

    def _slug_de_sentido(self, bruto) -> str:
        s = norm_slug(str(bruto or ""))
        return self.ALIAS_DE_SENTIDO.get(s, s)

    def _termo_sense(self, valor) -> tuple[bool, str]:
        """`{"sense": "darkvision"}` -- o personagem enxerga assim?

        Termo novo de 2026-07-29 (spec `2026-07-29-termos-de-predicado.md`).
        Antes dele, `low-light vision` caia inteiro em `requires_residuo`.
        """
        alvo = self._slug_de_sentido(valor)
        if alvo in self._sentidos():
            return True, ""
        return False, f"exige o sentido {valor}"

    def _termo_focus_pool(self, valor) -> tuple[bool, str]:
        """`{"focus_pool": {">=": 1}}` -- o personagem tem pontos de foco?

        O motor ja calculava o pool (regra 22: unico, teto 3); faltava expor
        como termo, e por isso `focus pool` (10 ocorrencias) e `ability to cast
        focus spells` (6) caiam inteiros em `requires_residuo`.
        """
        for op, alvo in (valor or {}).items():
            if not _comparar(self.focus_pool, op, alvo):
                return False, (f"exige focus pool {op} {alvo}; "
                               f"tem {self.focus_pool}")
        return True, ""

    # as quatro do Remaster. Serve para separar tradicao RESOLVIDA de prosa:
    # Sorcerer, Summoner e Witch guardam a frase "variavel (definida pela
    # escolha de ...)" no lugar do valor -- item 78.
    TRADICOES = ("arcane", "divine", "occult", "primal")

    def _termo_spellcasting_tradition(self, valor) -> tuple[bool, str]:
        """`{"spellcasting_tradition": "arcane"}` -- conjura dessa tradicao?

        99 clausulas em 27 arquetipos, e ate 2026-07-29 nenhum dos dois motores
        tinha o metodo. Termo sem handler nao reprova (principio zero), entao o
        `any` de `cathartic-mage-dedication` passava a vacuo e um Guerreiro 6
        recebia seis dedicacoes de conjuracao. Achado comparando com o
        Pathbuilder, que barra as seis -- e ali ele esta certo.

        Le `self.conjuracao`, que ja inclui a de CLASSE e a de ARQUETIPO: um
        Guerreiro com Cleric Dedication + Basic Cleric Spellcasting conjura
        divine de verdade e atende.

        Spec: `specs/2026-07-29-termo-spellcasting-tradition.md`
        """
        alvo = norm_slug(str(valor or ""))
        if not self.conjuracao:
            return False, f"exige conjurar {valor}; o personagem nao conjura"
        indefinida = False
        for c in self.conjuracao:
            bruta = c.get("tradicao")
            if not bruta:
                # `None` e "varia com a subclasse e ela nao foi escolhida", e
                # NAO "nao tem tradicao" -- desde que `_conjuracao` passou a
                # resolver (item 78), a frase em prosa virou nulo. Tratar como
                # ausencia faria o Feiticeiro sem bloodline ser REPROVADO, que
                # e o oposto do principio zero: o motor nao sabe qual e.
                indefinida = True
                continue
            if norm_slug(str(bruta)) == alvo:
                return True, ""
            if norm_slug(str(bruta)) not in self.TRADICOES:
                indefinida = True
        if indefinida:
            # principio zero: a tradicao esta em prosa (item 78) -- o motor nao
            # sabe qual e e nao reprova sobre o que nao sabe. A ficha JA mostra
            # a string, entao a marca existe e nao precisa virar aviso aqui:
            # `candidatos()` avalia milhares de feats por slot e o log afogaria.
            return True, ""
        tem = ", ".join(sorted({str(c.get("tradicao")) for c in self.conjuracao
                                if c.get("tradicao")})) or "nenhuma"
        return False, f"exige conjurar {valor}; tem {tem}"

    def _termo_has_actor(self, valor) -> tuple[bool, str]:
        """`{"has_actor": "companheiro"}` -- alguma coisa na ficha concede um?

        A pergunta e sobre ter DIREITO ao bicho, nao sobre ja ter escolhido a
        especie: o pre-requisito de `Mature Animal Companion` fala do primeiro.
        """
        tipo = str(valor or "").lower()
        if any(c["tipo"] == tipo for c in self.concessoes_de_ator):
            return True, ""
        return False, f"exige ter {tipo}"

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

    # -- o que o app pergunta: slots abertos e candidatos por slot -----------

    def slots_abertos(self) -> list[dict]:
        """Tudo que esta por preencher, no estado atual.

        A terceira pergunta do construtor. O motor ja sabia responder "o que eu
        tenho" (`visao`) e "o que esta errado" (`fora_do_requisito`, `avisos`);
        faltava "o que falta escolher", que e o que guia a tela.
        """
        abertos = []
        gasto_em = defaultdict(list)
        for e in self.doc.get("escolhas", []):
            gasto_em[e.get("slot")].append(e.get("em"))

        for slot, cadencia in self.SLOT_PARA_CADENCIA.items():
            usados = list(gasto_em.get(slot) or [])
            for nivel in (self.slots.get(cadencia) or []):
                if nivel in usados:
                    usados.remove(nivel)
                    continue
                abertos.append({
                    "slot": slot, "em": nivel, "kind": "feat", "escolhe": 1,
                    "rotulo": f"{slot.replace('_', ' ')} (nivel {nivel})"})

        usados = list(gasto_em.get("skill_increase") or [])
        for nivel in self.aumentos_de_pericia:
            if nivel in usados:
                usados.remove(nivel)
                continue
            abertos.append({
                "slot": "skill_increase", "em": nivel, "kind": "skill",
                "escolhe": 1, "rotulo": f"aumento de pericia (nivel {nivel})"})

        # o slot que um feat ou heranca CONCEDEU. Identidade pela `flag` do
        # ChoiceSet e nao pelo nivel: `Ancient Elf` e um `basic-arcana` podem
        # cair no mesmo nivel, e dois slots com a mesma chave viravam um so.
        usados_conc = {e.get("flag") for e in self.doc.get("escolhas", [])
                       if e.get("slot") == "feat_concedido"}
        for bloco in self.slots_concedidos:
            if bloco.get("flag") in usados_conc:
                continue
            abertos.append({
                "slot": "feat_concedido", "em": bloco.get("em"), "kind": "feat",
                "escolhe": 1, "flag": bloco.get("flag"),
                "rotulo": f"feat concedido por {bloco.get('origem')}"})

        for bloco in self.slots_de_subclasse:
            if bloco.get("escolhido") is None:
                abertos.append({
                    "slot": "subclasse", "em": bloco.get("nivel"),
                    "kind": bloco.get("eixo"), "escolhe": 1,
                    "opcoes": bloco.get("opcoes"),
                    "rotulo": f"{bloco.get('classe')} / {bloco.get('eixo')}"})

        faltam = self.boosts_direito - self.boosts_declarados
        if faltam > 0:
            abertos.append({
                "slot": "boosts_livres", "em": "criacao", "kind": "ability",
                "escolhe": faltam, "fontes": self.boosts_pendentes,
                "rotulo": f"boosts de atributo ({faltam} a escolher)"})

        for e in getattr(self, "escolhas_de_grant", []):
            if e["escolhido"] is None:
                abertos.append({
                    "slot": "escolha_de_grant", "em": "criacao", "kind": "grant",
                    "escolhe": 1, "opcoes": e["opcoes"],
                    "flag": e["flag"], "origem": e["origem"],
                    "rotulo": f"{e['nome']} / {e['flag']}"})

        # sem esta entrada a tela nunca oferece o picker de pericia, e o
        # orcamento continua sendo um numero que ninguem gasta
        faltam_pericias = self.pericias_livres - self.pericias_declaradas
        if faltam_pericias > 0:
            abertos.append({
                "slot": "pericias_livres", "em": "criacao", "kind": "skill",
                "escolhe": faltam_pericias,
                "fontes": self.pericias_livres_detalhe,
                "rotulo": f"pericias treinadas ({faltam_pericias} a escolher)"})

        # concessao de ator sem ator: o feat foi pego e a especie nao foi
        # escolhida. `_casadas` e preenchido em `_atores`, que ja rodou.
        for c in self.concessoes_de_ator:
            if c["preenchida"]:
                continue
            abertos.append({
                "slot": c["tipo"], "em": c.get("em") or "criacao",
                "kind": c["escolhe"], "escolhe": 1, "origem": c["origem"],
                # `opcoes_ids`, e nao `opcoes`: no slot de subclasse `opcoes` e
                # a CONTAGEM, e o mesmo nome com dois tipos ja quebrou este
                # campo uma vez (TypeError ao iterar um int)
                "opcoes_ids": c["opcoes"],
                "rotulo": f"{c['tipo']} -- {c['origem_nome']}"})

        for slot in ("ancestralidade", "heranca", "background"):
            atributo = {"ancestralidade": self.ancestria, "heranca": self.heranca,
                        "background": self.background}[slot]
            if atributo is None:
                abertos.append({
                    "slot": slot, "em": "criacao",
                    "kind": {"ancestralidade": "ancestry", "heranca": "heritage",
                             "background": "background"}[slot],
                    "escolhe": 1, "rotulo": slot})

        abertos.sort(key=lambda s: (s["em"] if isinstance(s["em"], int) else 0,
                                    s["slot"]))
        return abertos

    # -- o filtro do slot concedido (ChoiceSet do Foundry) -------------------

    # `item:X:Y` -> onde X vive no nosso registro. Medido nos 101 ChoiceSet com
    # `itemType: "feat"`: trait 291, level 94, category 56, rarity 8.
    CAMPO_DO_ATOMO = {"trait": "traits", "level": "level",
                      "category": "feat_category", "rarity": "rarity"}

    def _sem_gate_de_nivel(self, requires):
        """O mesmo `requires` sem a clausula de nivel de personagem.

        A prosa do `Ancient Elf` e explicita e e ela que manda: "You gain the
        multiclass dedication feat for that class, **even though you don't meet
        its level prerequisite**. You must still meet its **other**
        prerequisites." Entao o slot concedido dispensa o nivel e mantem todo o
        resto -- CHA >= 14 continua valendo.

        Vale para os outros concessores sem risco: `Basic Arcana` e companhia
        ja trazem o teto de nivel dentro do proprio filtro
        (`{"lte": ["item:level", 2]}`), e quem os pega esta acima desse nivel de
        qualquer jeito. Aqui a clausula sai por decisao da fonte, nao por
        conveniencia.
        """
        if not isinstance(requires, dict):
            return requires
        if "character_level" in requires:
            return None
        saida = {}
        for chave, valor in requires.items():
            if chave in ("all", "any", "none") and isinstance(valor, list):
                limpo = [c for c in (self._sem_gate_de_nivel(v) for v in valor)
                         if c is not None]
                if limpo:
                    saida[chave] = limpo
            else:
                saida[chave] = valor
        return saida or None

    def _atomo_de_filtro(self, reg: dict, atomo: str):
        """Um atomo do filtro contra um registro. `None` = nao sei avaliar.

        `None` nao e `False`: 153 dos atomos carregam referencia dinamica
        (`item:trait:{actor|system.details.ancestry.trait}`), e tratar o que nao
        se avalia como reprovacao esvaziaria o slot em silencio -- o oposto do
        principio zero.
        """
        if "{" in atomo:
            return None
        partes = atomo.split(":")
        if len(partes) < 3 or partes[0] != "item":
            return None
        campo = self.CAMPO_DO_ATOMO.get(partes[1])
        if campo is None:
            return None
        alvo = ":".join(partes[2:])
        valor = reg.get(campo)
        if campo == "traits":
            return alvo in (valor or [])
        if campo == "level":
            return isinstance(valor, int) and str(valor) == alvo
        return str(valor or "") == alvo

    def _casa_filtro(self, reg: dict, filtro) -> bool:
        """O filtro RECORTA o slot, como `_aceita_no_slot` -- nao ordena.

        Gramatica medida na fonte: lista no topo e AND; operadores `or` 28,
        `and` 16, `not` 37, `nor` 2, `xor` 8, e `lte` 59 (`{"lte": ["item:level",
        2]}`, que le "de nivel 2 ou menos").

        Atomo desconhecido NAO reprova: conta em `self.filtro_ignorado` e vale
        como satisfeito, para o slot estreitar pelo que se sabe em vez de
        esvaziar pelo que nao se sabe.
        """
        if filtro is None or filtro is True:
            return True
        if isinstance(filtro, str):
            r = self._atomo_de_filtro(reg, filtro)
            if r is None:
                self.filtro_ignorado[filtro] = self.filtro_ignorado.get(filtro, 0) + 1
                return True
            return r
        if isinstance(filtro, list):
            return all(self._casa_filtro(reg, f) for f in filtro)
        if not isinstance(filtro, dict):
            return True
        for op, arg in filtro.items():
            itens = arg if isinstance(arg, list) else [arg]
            if op == "or":
                if not any(self._casa_filtro(reg, i) for i in itens):
                    return False
            elif op == "and":
                if not all(self._casa_filtro(reg, i) for i in itens):
                    return False
            elif op == "not":
                if all(self._casa_filtro(reg, i) for i in itens):
                    return False
            elif op == "nor":
                if any(self._casa_filtro(reg, i) for i in itens):
                    return False
            elif op == "xor":
                if sum(1 for i in itens if self._casa_filtro(reg, i)) != 1:
                    return False
            elif op in ("lte", "lt", "gte", "gt"):
                # `{"lte": ["item:level", 2]}` -- campo de um lado, numero do
                # outro. So `item:level` aparece assim nos 101 medidos.
                if len(itens) != 2 or not str(itens[0]).endswith(":level"):
                    self.filtro_ignorado[op] = self.filtro_ignorado.get(op, 0) + 1
                    continue
                nivel = reg.get("level")
                # o lado direito e inteiro em 32 dos 34, e `self:level` em um --
                # `Rogue Dedication` concede "um feat de pericia de nivel ate o
                # seu". Tratar a referencia como nao-inteiro reprovava TODOS os
                # feats de pericia e esvaziava o slot em silencio, que e o
                # oposto do que o principio zero manda.
                teto_f = self.nivel if itens[1] == "self:level" else itens[1]
                if not isinstance(teto_f, int):
                    self.filtro_ignorado[str(itens[1])] = (
                        self.filtro_ignorado.get(str(itens[1]), 0) + 1)
                    continue
                if not isinstance(nivel, int):
                    return False
                itens = [itens[0], teto_f]
                if not {"lte": nivel <= itens[1], "lt": nivel < itens[1],
                        "gte": nivel >= itens[1], "gt": nivel > itens[1]}[op]:
                    return False
            else:
                self.filtro_ignorado[op] = self.filtro_ignorado.get(op, 0) + 1
        return True

    def _aceita_no_slot(self, slot: str, r: dict) -> bool:
        """Elegibilidade de SLOT -- que e coisa diferente de requisito.

        O slot FILTRA por tipo; `requires` so ORDENA (principio zero). Um feat
        sem trait `archetype` nao e candidato ao slot gratuito -- isso nao e
        bloquear escolha, e a definicao do slot. Ja um feat de arquetipo cujo
        requisito o personagem nao atende APARECE, marcado.
        """
        traits = {str(t).lower() for t in (r.get("traits") or [])}
        if slot == "free_archetype":
            return "archetype" in traits
        if slot == "skill_feat":
            return "skill" in traits
        if slot == "general_feat":
            return "general" in traits
        if slot == "ancestry_feat":
            nomes = {str((self.ancestria or {}).get("name") or "").lower()}
            nomes |= {str((self.heranca or {}).get("name") or "").lower()}
            return bool(traits & (nomes - {""}))
        if slot == "class_feat":
            # feat de classe do personagem. Um feat pode servir a varias
            # classes, e basta pertencer a UMA das que ele tem.
            minhas = {str(self.base.get(c).get("name") or "").lower()
                      for c in self.ordem_de_classe}
            if traits & minhas:
                return True
            # RAW: feat de ARQUETIPO pode ser gasto num slot de feat de classe --
            # e literalmente assim que se entra num arquetipo no PF2e oficial.
            # Nenhuma das 226 dedicacoes carrega trait de classe, entao exigir a
            # trait tornava todas inalcancaveis por este slot, e a unica porta
            # para dedicacao virava o slot de Free Archetype. Num projeto cuja
            # regra da casa SUBSTITUI a dedicacao, o caminho RAW tem de continuar
            # existindo para poder ser comparado com ela.
            #
            # A regra 23 continua valendo: `_veto_dedicacao_da_propria_classe`
            # marca a dedicacao do proprio Guerreiro como fora-do-requisito, sem
            # esconde-la.
            return "archetype" in traits
        return True

    def candidatos(self, slot: str, em: int | None = None,
                   limite: int | None = None, flag: str | None = None) -> list[dict]:
        """O que cabe NESTE slot, ordenado -- nunca filtrado por requisito.

        `disponiveis(kind=...)` devolve os 6.273 feats da base; uma tela de
        escolha nao pode receber isso. Aqui o conjunto de entrada e recortado
        pela elegibilidade do slot, e o `requires` continua so ordenando.
        """
        if slot == "boosts_livres":
            return [{"id": a, "nome": a.upper(), "level": None,
                     "atende": True, "motivos": [], "ja_pego": False}
                    for a in ATRIBUTOS]

        if slot in ("companheiro", "familiar", "eidolon"):
            # As `opcoes` do concessor ORDENAM, nao filtram: Drake Rider diz
            # "riding drake, riding dragonet, or another animal companion", e
            # mesmo o Rough Rider, que fixa o lobo, nao some com o resto -- e o
            # principio zero aplicado a especie.
            preferidas = [o for c in self.concessoes_de_ator
                          if c["tipo"] == slot
                          and (em is None or c.get("em") == em)
                          for o in c["opcoes"]]
            kinds = {c["escolhe"] for c in self.concessoes_de_ator
                     if c["tipo"] == slot} or {"animal-companion"}
            # `stats` separa ESPECIE de ESPECIALIZACAO: dos 113 registros do
            # kind, 17 sao Ambusher, Nimble, Savage, Wrecker e companhia --
            # graus e especializacoes que nao tem stat block e nao cabem neste
            # slot. Elegibilidade de slot, nao requisito: nao ha o que ordenar.
            # `stats` so discrimina no companheiro: la ele separa ESPECIE de
            # especializacao (17 dos 113 sao Ambusher, Nimble, Savage...). Os 39
            # `familiar-specific` nao tem `stats` -- a fonte nao publica numero
            # para eles --, entao exigir o campo esvaziaria a lista inteira.
            # Spec: `specs/2026-07-30-familiar-e-eidolon-concedidos.md`
            registros = [r for r in self.base.por_id.values()
                         if r.get("kind") in kinds
                         and (slot != "companheiro" or r.get("stats"))]
            saida = []
            for r in registros:
                atende, motivos = self.avaliar(r.get("requires"))
                saida.append({"id": r["id"], "nome": r.get("name"),
                              "level": r.get("level"), "atende": atende,
                              "motivos": motivos, "ja_pego": False,
                              "sugerida": r["id"] in preferidas})
            saida.sort(key=lambda x: (not x["sugerida"], not x["atende"],
                                      x["nome"] or ""))
            return saida[:limite] if limite else saida

        if slot == "subclasse":
            ids = [o for b in self.slots_de_subclasse
                   if em is None or b.get("nivel") == em
                   for o in (b.get("opcoes_ids") or [])]
            registros = [self.base.opcional(i) for i in ids]
        elif slot == "skill_increase":
            registros = [r for r in self.base.por_id.values()
                         if r.get("kind") == "skill"]
        elif slot == "nivel_de_classe":
            registros = [r for r in self.base.por_id.values()
                         if r.get("kind") == "class"]
        elif slot == "feat_concedido":
            # o filtro do ChoiceSet RECORTA, como qualquer elegibilidade de
            # slot. Um slot de `Ancient Elf` que aceitasse feat qualquer seria
            # pior que nao existir: entregaria escolha ilegal com cara de legal.
            blocos = [b for b in self.slots_concedidos
                      if em is None or b.get("em") == em]
            if flag is not None:
                blocos = [b for b in blocos if b.get("flag") == flag]
            registros = [r for r in self.base.por_id.values()
                         if r.get("kind") == "feat"
                         and any(self._casa_filtro(r, b.get("filtro"))
                                 for b in blocos)] if blocos else []
        else:
            registros = [r for r in self.base.por_id.values()
                         if r.get("kind") == "feat" and self._aceita_no_slot(slot, r)]

        ja = self._ids_de_feat_escolhidos()
        saida = []
        for r in registros:
            if r is None:
                continue
            exigencia = (self._sem_gate_de_nivel(r.get("requires"))
                         if slot == "feat_concedido" else r.get("requires"))
            atende, motivos = self.avaliar(exigencia)
            veto = self._veto_dedicacao_da_propria_classe(r)
            if veto:
                atende, motivos = False, motivos + [veto]
            # `em` e int nos slots de cadencia e a string `criacao` no que
            # nasce na criacao do personagem (heranca, background). Comparar os
            # dois estourava; na criacao o teto de nivel e 1.
            # slot concedido nao tem teto de nivel proprio: o filtro da fonte ja
            # diz quais niveis ele aceita, e o `Ancient Elf` dispensa o
            # pre-requisito de nivel por escrito.
            teto = None if slot == "feat_concedido" else (1 if em == "criacao" else em)
            if isinstance(teto, int) and isinstance(r.get("level"), int) and r["level"] > teto:
                atende = False
                motivos = motivos + [f"feat de nivel {r['level']} num slot de nivel {em}"]
            saida.append({"id": r["id"], "nome": r.get("name"),
                          "level": r.get("level"), "atende": atende,
                          "motivos": motivos, "ja_pego": r["id"] in ja})
        saida.sort(key=lambda x: (not x["atende"], x["ja_pego"],
                                  x["level"] or 0, x["nome"] or ""))
        return saida[:limite] if limite else saida

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
            extra = self._veto_dedicacao_da_propria_classe(r)
            if extra:
                atende, motivos = False, motivos + [extra]
            saida.append({"id": r["id"], "nome": r.get("name"),
                          "level": r.get("level"), "atende": atende,
                          "motivos": motivos})
        saida.sort(key=lambda x: (not x["atende"], x["level"] or 0, x["nome"] or ""))
        return saida[:limite] if limite else saida

    def _classes_multiclasse(self) -> dict[str, str]:
        """nome normalizado -> id da classe, para os 27 arquetipos de
        multiclasse. Derivado: arquetipo cujo nome e nome de classe. Nao ha
        lista escrita a mao, que ja errou tres vezes neste projeto."""
        # O cache vive na BASE, nao no personagem: o resultado depende so do
        # catalogo, e a base e compartilhada por todas as fichas. Com cache de
        # instancia, cada `Personagem` novo varria os 19.705 registros -- o
        # profile de um teste de carga com 285 fichas mostrou ~90% do tempo
        # total de derivacao aqui dentro. Era o unico ponto medido cujo custo
        # escalava com o tamanho da BASE em vez do tamanho da FICHA, que e
        # exatamente o que nao pode acontecer num app client-side.
        return self.base.multiclasse()

    def _veto_dedicacao_da_propria_classe(self, feat: dict) -> str | None:
        """Regra 23: dedicacao de multiclasse da propria classe.

        RAW (Advanced Player's Guide, "Multiclass Archetypes"): *"You can't
        select a multiclass archetype's dedication feat if you are a member of
        the class of the same name."* Nada na base modelava isso -- um Mago 20
        puro recebia `atende: True` para Wizard Dedication.

        DECISAO DO IGOR (2026-07-27): a exclusao vale sempre que o personagem
        tem QUALQUER nivel da classe, e e MUTUA -- ver
        `_veto_classe_de_dedicacao_ja_pega` para a ordem inversa.

        Eu havia argumentado por liberar no caso multiclasse, alegando que
        bloquear custaria ao Mago 2 os 8 slots que o Guerreiro 20 leva de graca
        sob Free Archetype. **O argumento estava inflado**: o personagem
        continua podendo pegar qualquer uma das outras 26 dedicacoes e levar os
        mesmos 8 slots. O que a exclusao tira e a ESCOLHA DA TRADICAO, nao os
        slots -- entao a regra 21 nao e violada.

        E a exclusao resolve uma incoerencia real: com as duas rotas na mesma
        classe, a mesma magia sairia em DOIS ranks na mesma ficha, o do slot de
        classe elevado pela regra 17 e o do slot de arquetipo, que pela regra 18
        roda RAW puro.

        Principio zero continua valendo: isto marca `fora do requisito`, com o
        motivo escrito. Nunca esconde nem impede.
        """
        nome = norm_slug(feat.get("name") or "")
        if not nome.endswith("-dedication"):
            return None
        cid = self._classes_multiclasse().get(nome[:-len("-dedication")])
        if not cid:
            return None
        nc = self.nivel_de(cid)
        if nc == 0:
            return None
        return (f"regra 23: o personagem ja tem {nc} nivel(is) de "
                f"{self.base.get(cid).get('name')}; as duas rotas se excluem")

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
            # o requisito de um feat e avaliado contra o estado SEM o efeito
            # dele mesmo -- ver `_rank_sem`
            self._avaliando = wb_id
            # o nivel DESTA escolha: sem ele o `has` olha o documento inteiro e
            # a ordem ilegal passa limpa -- ver `_termo_has`
            self._avaliando_em = e.get("em")
            atende, motivos = self.avaliar(feat.get("requires"))
            self._avaliando = None
            self._avaliando_em = None
            for veto in (self._veto_dedicacao_da_propria_classe(feat),
                         self._exige_a_dedicacao_do_arquetipo(feat, motivos)):
                if veto:
                    atende, motivos = False, motivos + [veto]
            if not atende:
                self.fora_do_requisito.append({
                    "feat": feat.get("name", wb_id),
                    "motivo": "; ".join(motivos) or "predicado nao atendido"})
        self._veto_classe_de_dedicacao_ja_pega()
        self._nova_dedicacao_exige_dois_feats()

    # -- as duas regras do trait `dedication` (RAW) -------------------------

    def _ids_de_feat_escolhidos(self) -> set:
        """Escolhidos MAIS concedidos. `gray-corsair-training` concede
        `pirate-dedication`: sem contar o concedido, um feat Pirate na mesma
        ficha era acusado de nao ter a dedicacao (falso positivo) e uma segunda
        dedicacao passava batido (falso negativo)."""
        ids = {e["pega"] for e in self.doc.get("escolhas", [])
               if isinstance(e.get("pega"), str) and e["pega"].startswith("wb:feat/")}
        return ids | {c["id"] for c in self.concedidos if c["id"].startswith("wb:feat/")}

    def _exige_a_dedicacao_do_arquetipo(self, feat: dict, motivos: list) -> str | None:
        """RAW do trait `archetype`: um feat de arquetipo exige a Dedication
        daquele arquetipo.

        A base nao escreve isso no `requires` -- 181 feats de arquetipo trazem
        so `character_level >= N` --, e por isso Barbarian Resiliency entrava
        numa ficha sem Barbarian Dedication em silencio. O vinculo nao precisa
        de lista: `feat["archetype"]` aponta o arquetipo e a dedicacao dele e
        achavel por trait.
        """
        traits = feat.get("traits") or []
        if "archetype" not in traits or "dedication" in traits:
            return None
        arq = feat.get("archetype")
        if not arq:
            return None
        ded = self.base.dedicacao_do_arquetipo(arq)
        if not ded or ded in self._ids_de_feat_escolhidos():
            return None
        nome = self.base.get(ded).get("name", ded)
        # se o `requires` ja reprovou por causa da MESMA dedicacao, nao repetir
        if any(nome in m for m in motivos):
            return None
        return (f"feat do arquetipo {self.base.opcional(arq).get('name', arq) if self.base.opcional(arq) else arq}"
                f" exige {nome} (RAW do trait archetype), que a ficha nao tem")

    def _nova_dedicacao_exige_dois_feats(self) -> None:
        """RAW do trait `dedication`, conferido no texto da propria base (76
        dedicacoes repetem a clausula): "You can't select another dedication
        feat until you've gained two other feats from the <X> archetype".

        A contagem e NO TEMPO: vale o que o personagem tinha ate o nivel em que
        a nova dedicacao entrou, nao o que ele tem no fim da ficha.
        """
        picks = [e for e in self.doc.get("escolhas", [])
                 if isinstance(e.get("pega"), str) and e["pega"].startswith("wb:feat/")]
        # `criacao` vem antes de qualquer nivel numerado
        picks.sort(key=lambda e: e["em"] if isinstance(e.get("em"), int) else 0)
        # feat de arquetipo CONCEDIDO conta na cota tanto quanto o escolhido --
        # entra no nivel da escolha que o originou, que e quando ele apareceu
        nivel_da_raiz = {e["pega"]: e.get("em") for e in picks}
        for c in self.concedidos:
            if c["id"].startswith("wb:feat/"):
                picks.append({"pega": c["id"], "em": nivel_da_raiz.get(c["raiz"])})
        picks.sort(key=lambda e: e["em"] if isinstance(e.get("em"), int) else 0)

        contagem: dict[str, int] = defaultdict(int)   # arquetipo -> feats nao-dedicacao
        dedicados: list[str] = []                     # arquetipos ja dedicados, em ordem
        for e in picks:
            feat = self.base.opcional(e["pega"])
            if feat is None:
                continue
            traits = feat.get("traits") or []
            arq = feat.get("archetype")
            if "dedication" in traits and arq:
                faltando = [a for a in dedicados if contagem[a] < 2]
                if faltando:
                    nomes = ", ".join(
                        (self.base.opcional(a) or {}).get("name", a) for a in faltando)
                    self.fora_do_requisito.append({
                        "feat": feat.get("name", e["pega"]),
                        "motivo": (f"nova dedicacao no nivel {e.get('em')} sem os 2 "
                                   f"feats exigidos de: {nomes} (RAW do trait "
                                   f"dedication)")})
                dedicados.append(arq)
            elif arq:
                contagem[arq] += 1

    def _veto_classe_de_dedicacao_ja_pega(self) -> None:
        """Regra 23, o outro sentido: nivel de classe X com dedicacao de X.

        A exclusao e MUTUA. O primeiro sentido (pegar a dedicacao tendo a
        classe) e barrado em `_veto_dedicacao_da_propria_classe`; este barra a
        ordem inversa, que produz exatamente a mesma ficha e passaria batido se
        so um lado fosse checado.

        O que a exclusao resolve: sem ela, a mesma magia sai em DOIS ranks na
        mesma ficha -- o slot de classe elevado pela regra 17 e o slot de
        arquetipo, que pela regra 18 roda RAW puro.
        """
        pegos = {norm_slug((self.base.opcional(e.get("pega")) or {}).get("name") or "")
                 for e in self.doc.get("escolhas", [])
                 if isinstance(e.get("pega"), str)
                 and e["pega"].startswith("wb:feat/")}
        for nome, cid in self._classes_multiclasse().items():
            nc = self.nivel_de(cid)
            if nc and f"{nome}-dedication" in pegos:
                self.fora_do_requisito.append({
                    "feat": f"{self.base.get(cid).get('name')} (nivel de classe)",
                    "motivo": (f"regra 23: o personagem tem {nc} nivel(is) de "
                               f"{self.base.get(cid).get('name')} E a dedicacao "
                               f"da mesma classe. As duas rotas se excluem")})

    def _classe_do_feat(self, feat: dict) -> str | None:
        """A classe de um feat sai do trait, nao de lista escrita a mao."""
        traits = {str(t).lower() for t in (feat.get("traits") or [])}
        for cid in self.ordem_de_classe:
            nome = str(self.base.get(cid).get("name") or "").lower()
            if nome in traits:
                return cid
        return None

    # -- cadeia de grant_feat/grant_item: aplica o estatico, sinaliza o resto -

    def _grants_em_cadeia(self) -> None:
        """Percorre `grant_feat`/`grant_item` de tudo que o personagem tem
        (feats escolhidos + features de classe/subclasse), com guarda de
        profundidade e visitados -- ver `MAX_PROFUNDIDADE_GRANTS` e
        `_resolver_cadeia_de_grants`.

        O que a cadeia entrega com ALVO ESTATICO e aplicado: no PF2e isso nao
        e escolha nenhuma, e efeito automatico (Barbarian Dedication da Rage,
        ponto final). O principio zero fala de `requires` -- sugerir em vez de
        bloquear a ESCOLHA do jogador --, nao de esconder o efeito de uma
        escolha ja feita. Alvo DINAMICO (`{item|flags...}`) e que depende de
        escolha ainda nao feita: esse continua so sinalizado, e o app precisa
        distinguir "pendente" de "ausente".

        Antes desta passada, uma dedicacao entrava na ficha como linha e nao
        entregava nada -- medido: 52 HP contra 56 (`battle-harbinger`),
        `society` untrained (`shieldmarshal`), Rage sumido (`barbarian`).
        """
        self.concedidos: list[dict] = []
        self._raizes: dict[str, str] = {}
        # o que o personagem ja tem por escolha propria nao pode ser concedido
        # de novo: senao Toughness pego a mao + Toughness da dedicacao somaria
        # HP duas vezes.
        self._ja_tenho = {f["id"] for f in self.features if f.get("id")}
        self._ja_tenho |= {wb_id for wb_id, _ in self._feats_escolhidos()}

        origens = [(wb_id, feat.get("grants") or [])
                   for wb_id, feat in self._feats_escolhidos()]
        # snapshot: a recursao percorre os grants do proprio alvo concedido,
        # entao features novas nao precisam ser revisitadas por este laco
        origens += [(f["id"], f.get("grants") or [])
                    for f in list(self.features) if f.get("id")]
        # ancestria, heranca e background TAMBEM concedem -- sao 496 registros
        # com `grant_feat` que ficavam inertes porque a cadeia so olhava feat e
        # feature (`shielded-fortune` -> Toughness, `ambitious-human` -> Fleet)
        for reg in (self.ancestria, self.heranca, self.background):
            if reg and reg.get("id"):
                origens.append((reg["id"], reg.get("grants") or []))
        for origem_id, grants in origens:
            self._resolver_cadeia_de_grants(origem_id, grants, {origem_id})

    def _raiz_de(self, wb_id: str) -> str:
        """Quem ORIGINOU este item na ficha. Para o que o jogador escolheu, e
        ele mesmo; para o que veio de cadeia, e a escolha la no comeco dela."""
        return getattr(self, "_raizes", {}).get(wb_id, wb_id)

    def _aplicar_concessao(self, origem_id: str, alvo: str, alvo_reg: dict) -> None:
        """Poe na ficha o que a cadeia concedeu. Class-feature vira linha de
        feature (e por isso entra em `_proficiencias`, em `_termo_has` e na
        visao); feat vira feat efetivo, que e o que `_hp` e `_proficiencias`
        percorrem."""
        origem_nome = (self.base.opcional(origem_id) or {}).get("name", origem_id)
        raiz = self._raiz_de(origem_id)
        self._raizes[alvo] = raiz
        registro = {
            "id": alvo,
            "nome": alvo_reg.get("name", alvo),
            "classe": None,
            "origem": origem_nome,
            "nivel_de_classe": None,
            "grants": alvo_reg.get("grants") or [],
            "na_base": True,
            "concedido_por": origem_id,
            "raiz": raiz,
        }
        self.concedidos.append(registro)
        if alvo.startswith("wb:class-feature/"):
            self.features.append(registro)

    def _nivel_do_feat(self, wb_id: str):
        """Em que nivel o feat entrou. `criacao` quando veio pela cadeia (ele
        chega junto com quem o concedeu, e nao por escolha do jogador)."""
        for e in self.doc.get("escolhas", []):
            if e.get("pega") == wb_id or e.get("valor") == wb_id:
                return e.get("em", "criacao")
        return "criacao"

    def _feats_efetivos(self):
        """Feats escolhidos MAIS os concedidos pela cadeia, sem repetir.

        E a lista que vale para efeito: o jogo nao distingue o Toughness que
        voce pegou do Toughness que a dedicacao te deu.
        """
        vistos = set()
        for wb_id, feat in self._feats_escolhidos():
            if wb_id not in vistos:
                vistos.add(wb_id)
                yield wb_id, feat, None
        for c in getattr(self, "concedidos", []):
            if c["id"].startswith("wb:feat/") and c["id"] not in vistos:
                vistos.add(c["id"])
                yield c["id"], self.base.get(c["id"]), c["origem"]

    def _resolver_cadeia_de_grants(self, origem_id: str, grants: list,
                                    visitados: set, profundidade: int = 0) -> None:
        """Um passo da cadeia. `visitados` e compartilhado entre as chamadas
        recursivas de uma mesma origem -- e o que poda auto-referencia (A
        concede A mesma) sem gerar aviso: o alvo ja esta em `visitados` desde
        o primeiro passo, entao e tratado como "ja tenho", nao como perda.
        """
        if profundidade > MAX_PROFUNDIDADE_GRANTS:
            self.avisos.append(
                f"{origem_id}: cadeia de grants cortada em profundidade "
                f"{MAX_PROFUNDIDADE_GRANTS} (possivel ciclo ou dado malformado)")
            return
        for g in grants or []:
            if not isinstance(g, dict):
                continue
            if "grant_feat" in g:
                alvos = g["grant_feat"]
                alvos = alvos if isinstance(alvos, list) else [alvos]
                for alvo in alvos:
                    if not isinstance(alvo, str) or not alvo.startswith("wb:"):
                        # 476 alvos da base sao nome cru ou dict serializado em
                        # vez de id -- TODOS de background (medido 2026-07-27).
                        # Nao e "ausente da base", e referencia nao resolvida
                        # pelo pipeline, e o aviso precisa dizer isso.
                        self.avisos.append(
                            f"{origem_id}: grant_feat com alvo nao resolvido "
                            f"pelo pipeline ({str(alvo)[:60]}) -- nao aplicado")
                        continue
                    if "{" in alvo:
                        self.avisos.append(
                            f"{origem_id}: grant_feat depende de escolha do "
                            f"jogador ({alvo}) -- nao resolvivel automaticamente")
                        continue
                    if alvo in visitados:
                        continue      # ja concedido nesta cadeia -- poda sem avisar
                    alvo_reg = self.base.opcional(alvo)
                    if alvo_reg is None:
                        self.avisos.append(
                            f"{origem_id}: grant_feat aponta pra id ausente "
                            f"da base: {alvo}")
                        continue
                    visitados.add(alvo)
                    if alvo not in self._ja_tenho:
                        self._ja_tenho.add(alvo)
                        self._aplicar_concessao(origem_id, alvo, alvo_reg)
                    self._resolver_cadeia_de_grants(
                        alvo, alvo_reg.get("grants") or [], visitados, profundidade + 1)
            if "grant_item" in g:
                gi = g["grant_item"]
                uuid = gi.get("uuid") if isinstance(gi, dict) else gi
                # `wb` e o id que o pipeline resolveu a partir do NOME no fim do
                # uuid (spec `2026-07-29-grant-item-por-nome.md`). Ate 2026-07-29
                # o motor nao aplicava grant_item NENHUM -- so avisava do uuid
                # dinamico --, entao 619 concessoes ficavam inertes.
                alvo = gi.get("wb") if isinstance(gi, dict) else None
                if isinstance(alvo, str) and alvo.startswith("wb:"):
                    if alvo in visitados:
                        continue      # ja concedido nesta cadeia -- poda sem avisar
                    alvo_reg = self.base.opcional(alvo)
                    if alvo_reg is None:
                        self.avisos.append(
                            f"{origem_id}: grant_item aponta pra id ausente "
                            f"da base: {alvo}")
                        continue
                    visitados.add(alvo)
                    if alvo not in self._ja_tenho:
                        self._ja_tenho.add(alvo)
                        self._aplicar_concessao(origem_id, alvo, alvo_reg)
                    self._resolver_cadeia_de_grants(
                        alvo, self._grants_de(alvo_reg), visitados,
                        profundidade + 1)
                    continue
                if isinstance(uuid, str) and "{" in uuid:
                    # uuid dinamico: so a escolha do jogador fecha isto. NAO e
                    # "alvo nao encontrado" -- e "pendente", e o app tem que
                    # distinguir os dois casos.
                    self.avisos.append(
                        f"{origem_id}: grant_item depende de escolha do "
                        f"jogador (uuid dinamico `{uuid}`) -- pendente, nao "
                        f"e alvo ausente")

    # -- saida --------------------------------------------------------------


    # -- bonus incondicional e o total de pericia/salva ----------------------

    def _melhor_por_tipo(self, bonus) -> int:
        """Soma respeitando a regra de tipo do PF2e.

        Bonus do MESMO tipo nao empilham -- vale o maior. Tipos diferentes
        somam. Bonus sem tipo (`untyped`) empilha com tudo, inclusive com outro
        untyped, e por isso ele e somado inteiro em vez de disputar.

        Sem isto, um personagem com tres itens de +1 de circunstancia sairia com
        +3 onde o RAW da +1 -- e a ficha parada inflaria sozinha.

        Spec: `specs/2026-07-30-bonus-de-pericia-e-salva.md`
        """
        melhor: dict[str, int] = {}
        solto = 0
        for tipo, valor, _origem in bonus:
            if not tipo or str(tipo).lower() == "untyped":
                solto += int(valor)
                continue
            chave = str(tipo).lower()
            melhor[chave] = max(melhor.get(chave, 0), int(valor))
        return solto + sum(melhor.values())

    # selectors que o motor sabe onde somar. O resto e contado e ignorado:
    # `initiative` e `perception-dc` nao existem como numero na ficha, e
    # `skill-check` generico nao diz QUAL pericia.
    SELETORES_DE_SALVA = {"fortitude", "reflex", "will", "saving-throw",
                          "perception"}

    def _bonus_incondicionais(self) -> dict:
        """`flat_modifier` sem `condicional`, agrupado por selector.

        Sao 462 de 1.709 -- os outros 1.247 sao condicionais ("+2 em Atletismo
        so para Empurrar") e dependem de contexto de acao que a ficha nao tem.
        Aplicar o grupo inteiro inflaria a ficha parada.

        `value` nao-inteiro (41 formulas do VTT e 1 nulo) e ignorado: avaliar
        formula do Foundry e o interpretador inteiro, outro item.

        MEMOIZADO, e nao por desempenho. A ultima linha atribui
        `self.bonus_ignorados` em vez de acumular, e ha tres chamadores em
        ordem: `_defesa`, `_pericias_e_salvas` e `_velocidade`. Os dois do meio
        GRAVAM as chaves `selector nao modelado: X` depois de chamar, e o
        terceiro reatribuia e apagava as duas -- nenhum personagem tinha uma
        unica chave dessas. O contador que existe para tornar a perda silenciosa
        impossivel estava ele proprio silenciado, e foi assim que o bonus de
        `ac` sumiu sem aparecer nem como ignorado.

        Spec: `specs/2026-07-30-bonus-de-item-equipado.md`
        """
        if self._bonus_memo is not None:
            return self._bonus_memo
        fora = Counter()
        por_selector: dict[str, list] = defaultdict(list)
        fontes = [(self.base.get(c).get("name", c), self.base.get(c))
                  for c in self.ordem_de_classe]
        for reg in (self.ancestria, self.heranca, self.background):
            if reg:
                fontes.append((reg.get("name"), reg))
        fontes += [(f.get("nome"), f) for f in self.features]
        fontes += [(feat.get("name", i), feat)
                   for i, feat, _ in self._feats_efetivos()]
        # o inventario equipado, que faltava: sao 293 grants incondicionais e
        # aplicaveis em `equipment` (261), `armor` (11), `shield` (11) e
        # `weapon` (10) -- religion 26, intimidation 25, diplomacy 22,
        # athletics 20, e o `ac` 6. Todos em selectors que o motor ja soma. A
        # resistencia vinda de item chegou na ficha porque `_resistencias` monta
        # esta mesma lista COM o inventario; aqui a linha nao existia, e por
        # isso vestir um item de +1 em Furtividade nao mudava Furtividade.
        # `equipado` e a condicao: espada na mochila nao ajuda ninguem.
        for entrada in (self.doc.get("inventario") or []):
            if entrada.get("equipado"):
                reg = self.base.opcional(str(entrada.get("item") or ""))
                if reg:
                    fontes.append((reg.get("name"), reg))
        for nome, reg in fontes:
            for g in self._grants_de(reg):
                if not isinstance(g, dict):
                    continue
                fm = g.get("flat_modifier")
                if not isinstance(fm, dict) or fm.get("condicional"):
                    continue
                valor = fm.get("value")
                if not isinstance(valor, int) or isinstance(valor, bool):
                    fora["valor nao inteiro"] += 1
                    continue
                bruto = fm.get("selector")
                # lista de selectors e a mesma declaracao escrita compacta:
                # `["ac", "saving-throw"]` aplica nos dois
                alvos = bruto if isinstance(bruto, list) else [bruto]
                for alvo in alvos:
                    chave = str(alvo)
                    if "{" in chave:
                        fora["selector dinamico"] += 1
                        continue
                    por_selector[chave].append((fm.get("type"), valor, nome))
        self.bonus_ignorados = dict(fora)
        self._bonus_memo = por_selector
        return por_selector

    def _pericias_e_salvas(self) -> None:
        """O total que a TELA calculava (`PainelDireito.tsx:94`).

        Numero que nasce no componente React nao tem oraculo, nao tem paridade e
        nao tem onde receber `flat_modifier`. AC e ataque ja moravam aqui; a
        pericia e a salva ficaram para tras.

        Nesta primeira passada o valor e IDENTICO ao que a tela mostrava --
        muda o lugar, nao o numero -- exceto onde ha bonus incondicional.
        """
        bonus = self._bonus_incondicionais()
        consumidos: set[str] = set()

        def total(chave: str, atributo: str, extras: list) -> dict:
            rank = self.proficiencias.get(chave, "untrained")
            mod = self.modificadores.get(atributo, 0)
            aplicados = []
            for sel in extras:
                aplicados += bonus.get(sel, [])
                consumidos.add(sel)
            extra = self._melhor_por_tipo(aplicados)
            # RAW: destreinado NAO soma o nivel, so o atributo
            base = (self.nivel + RANK_BONUS[rank]) if rank != "untrained" else 0
            # `nome` sai daqui com o default, e a pericia sobrescreve: sem
            # isto a salva ficava SEM a chave e o porte TS, que sempre a
            # preenche, divergia do gabarito em 23 fichas.
            linha = {"chave": chave, "nome": chave,
                     "rank": rank, "atributo": atributo,
                     "mod_atributo": mod, "bonus_total": extra,
                     "total": base + mod + extra,
                     "detalhe": (f"{'nivel ' + str(self.nivel) + ' + prof ' if rank != 'untrained' else ''}"
                                 f"{RANK_BONUS[rank] if rank != 'untrained' else 0} ({rank})"
                                 f" + {atributo.upper()} {mod:+d}"
                                 + (f" + bonus {extra:+d}" if extra else ""))}
            if aplicados:
                linha["bonus"] = [{"tipo": t, "valor": v, "origem": o}
                                  for t, v, o in aplicados]
            return linha

        self.pericias = []
        for reg in self.base.por_id.values():
            if reg.get("kind") != "skill" or reg.get("lore") or reg["id"] == "wb:skill/lore":
                continue
            chave = reg["id"].split("/")[-1]
            attr = (reg.get("attribute") or ["int"])[0]
            linha = total(chave, str(attr), [chave])
            linha["nome"] = reg.get("name") or chave
            self.pericias.append(linha)
        # as Lore que o personagem TEM entram junto, com a mesma conta
        for chave in self.proficiencias:
            if not str(chave).startswith("lore:"):
                continue
            linha = total(str(chave), "int", [str(chave)])
            # a chave as vezes ja carrega o sufixo "Lore" (vem assim da fonte),
            # e prefixar cegamente produzia `Lore: Alcohol Lore` na ficha. A
            # regra estava em `PainelDireito.tsx` e veio junto com a conta.
            bruto = re.sub(r"\s*\blore\b\s*$", "", str(chave)[5:], flags=re.I).strip()
            linha["nome"] = "Lore: " + bruto.title()
            self.pericias.append(linha)
        self.pericias.sort(key=lambda p: p["nome"])

        # `saving-throw` vale para as tres salvas; `fortitude` so para a dela
        ATRIBUTO_DA_SALVA = {"fortitude": "con", "reflex": "dex", "will": "wis",
                             "perception": "wis"}
        self.salvas = {}
        for chave, attr in ATRIBUTO_DA_SALVA.items():
            extras = [chave] if chave == "perception" else [chave, "saving-throw"]
            self.salvas[chave] = total(chave, attr, extras)
            consumidos.add(chave)
        consumidos.add("saving-throw")

        # o que sobrou nao e "ignorado" indistintamente: `hp` e `ac` tem passo
        # proprio (`_hp`, `_defesa`), e o resto (`initiative`, `perception-dc`,
        # `skill-check` generico, `strike-damage`) o motor nao modela. Contar e
        # o que impede a perda silenciosa -- foi ela que deixou 462 bonus fora
        # da ficha sem ninguem ver.
        #
        # ATE 30/07 ESTE COMENTARIO MENTIA sobre o `ac`: `_hp` de fato lia
        # `flat_modifier`, mas `_defesa` terminava em
        # `10 + dex + prof + item_bonus + potencia` e nao lia nada. O bonus era
        # coletado, excluido do contador por esta linha, e sumia sem aparecer
        # nem como ignorado -- a pior forma da perda, porque o proprio mecanismo
        # anti-perda a autorizava. Agora `_defesa` disputa de verdade.
        OUTRO_PASSO = {"hp", "ac"}
        for sel, lista in bonus.items():
            if sel in consumidos or sel in OUTRO_PASSO:
                continue
            self.bonus_ignorados[f"selector nao modelado: {sel}"] = len(lista)


    # -- resistencia, fraqueza e imunidade -----------------------------------

    def _melhor_resistencia(self, lista: list) -> list:
        """Duas fontes do MESMO tipo nao somam -- vale a maior (regra do livro).

        Mesma forma do `_melhor_por_tipo` dos bonus, mas aqui o resultado e a
        LISTA de linhas sobreviventes, porque a ficha mostra a origem.
        """
        melhor: dict[str, dict] = {}
        for linha in lista:
            t = str(linha.get("tipo"))
            if t not in melhor or int(linha.get("valor") or 0) > int(melhor[t].get("valor") or 0):
                melhor[t] = linha
        return sorted(melhor.values(), key=lambda x: str(x.get("tipo")))

    def _somar_resistencia(self, crus, chave, tipo, bruto, nome) -> None:
        """Uma linha por TIPO. Separado porque `tipo` pode ser lista."""
        def ignorar(motivo: str) -> None:
            k = f"{chave} {motivo}"
            self.bonus_ignorados[k] = self.bonus_ignorados.get(k, 0) + 1

        if "{" in tipo:
            return ignorar("de tipo dinamico")
        if tipo == "custom":
            return ignorar("custom")
        if chave == "immunity":
            crus[chave].append({"tipo": tipo, "origem": nome})
            return
        valor = self._resolver_valor((bruto or {}).get("valor"))
        if valor is None:
            return ignorar("com formula fora da gramatica")
        crus[chave].append({"tipo": tipo, "valor": valor, "origem": nome})

    def _resistencias(self) -> None:
        """233 `resistance`, 14 `immunity` e 11 `weakness` que a ficha ignorava.

        Fatia 3.2 do plano. Spec:
        `specs/2026-07-30-resistencia-e-formula.md`
        """
        crus = {"resistance": [], "weakness": [], "immunity": []}
        fontes = [(self.base.get(c).get("name", c), self.base.get(c))
                  for c in self.ordem_de_classe]
        for reg in (self.ancestria, self.heranca, self.background):
            if reg:
                fontes.append((reg.get("name"), reg))
        fontes += [(f.get("nome"), f) for f in self.features]
        fontes += [(feat.get("name", i), feat)
                   for i, feat, _ in self._feats_efetivos()]
        for entrada in (self.doc.get("inventario") or []):
            if entrada.get("equipado"):
                reg = self.base.opcional(str(entrada.get("item") or ""))
                if reg:
                    fontes.append((reg.get("name"), reg))
        for nome, reg in fontes:
            for g in self._grants_de(reg):
                if not isinstance(g, dict):
                    continue
                for chave in ("resistance", "weakness", "immunity"):
                    bruto = g.get(chave)
                    if bruto is None:
                        continue
                    # `tipo` e LISTA em 19 dos 258 (`Blast Resistance` protege
                    # de fire E sonic). Uma resistencia a N tipos sao N linhas;
                    # `str()` cego escrevia `"['fire', 'sonic']"` na ficha, e
                    # foi o diff do fixture que pegou.
                    alvo = bruto if chave == "immunity" else (bruto or {}).get("tipo")
                    tipos = [str(x) for x in alvo] if isinstance(alvo, list) else [str(alvo)]
                    for tipo in tipos:
                        self._somar_resistencia(crus, chave, tipo, bruto, nome)
                    continue
        self.resistencias = self._melhor_resistencia(crus["resistance"])
        self.fraquezas = self._melhor_resistencia(crus["weakness"])
        # imunidade nao tem valor: basta uma por tipo
        vistas, self.imunidades = set(), []
        for linha in crus["immunity"]:
            if linha["tipo"] in vistas:
                continue
            vistas.add(linha["tipo"])
            self.imunidades.append(linha)
        self.imunidades.sort(key=lambda x: x["tipo"])


    # -- velocidade ----------------------------------------------------------

    # `speed` sem sufixo e o que o Foundry usa quando so ha um modo -- 11
    # ocorrencias, todas de deslocamento terrestre.
    SELECTOR_DE_MODO = {"land-speed": "land", "speed": "land",
                        "fly-speed": "fly", "swim-speed": "swim",
                        "climb-speed": "climb", "burrow-speed": "burrow"}

    def _compor_velocidade(self, base: dict, concedidos: list,
                           bonus: dict, penalidade: int) -> dict:
        """base da ancestria -> modo concedido -> bonus -> penalidade de armadura.

        Modo concedido NAO soma: dois feats que dao `fly 25` e `fly 30` dao 30.
        `all-speeds` aplica so nos modos que EXISTEM -- criar modo a partir de
        bonus daria voo a quem nao voa.

        Spec: `specs/2026-07-30-velocidade.md`
        """
        vel = dict(base)
        for modo, valor in concedidos:
            vel[modo] = max(int(vel.get(modo, 0)), int(valor))
        for selector, lista in bonus.items():
            modo = self.SELECTOR_DE_MODO.get(selector)
            alvos = list(vel) if selector == "all-speeds" else ([modo] if modo else [])
            for alvo in alvos:
                if alvo in vel:
                    vel[alvo] += self._melhor_por_tipo(lista)
        if penalidade:
            for modo in vel:
                vel[modo] = max(0, vel[modo] + penalidade)
        return vel

    def _velocidade(self) -> None:
        """A ficha do COMPANHEIRO ja mostrava velocidade; a do personagem, nao."""
        base, detalhe = {}, []
        if self.ancestria:
            for g in self._grants_de(self.ancestria):
                sp = g.get("speed") if isinstance(g, dict) else None
                if isinstance(sp, dict) and "tipo" not in sp:
                    for modo, valor in sp.items():
                        base[str(modo)] = int(valor)
                    detalhe.append({"origem": self.ancestria.get("name"),
                                    "efeito": dict(base)})
        if not base:
            base = {"land": 25}
            self.avisos.append(
                "sem ancestria escolhida: velocidade base assumida em 25 pes")

        concedidos = []
        fontes = [(f.get("nome"), f) for f in self.features]
        fontes += [(feat.get("name", i), feat)
                   for i, feat, _ in self._feats_efetivos()]
        for nome, reg in fontes:
            for g in self._grants_de(reg):
                sp = g.get("speed") if isinstance(g, dict) else None
                if isinstance(sp, dict) and "tipo" in sp:
                    valor = self._resolver_valor(sp.get("valor"))
                    if valor is None:
                        continue
                    concedidos.append((str(sp.get("tipo")), valor))
                    detalhe.append({"origem": nome,
                                    "efeito": {str(sp.get("tipo")): valor}})

        bonus_todos = self._bonus_incondicionais()
        bonus = {sel: lista for sel, lista in bonus_todos.items()
                 if sel in self.SELECTOR_DE_MODO or sel == "all-speeds"}
        for sel, lista in bonus.items():
            for _tipo, valor, origem in lista:
                detalhe.append({"origem": origem, "efeito": {sel: valor}})

        # RAW: a penalidade cai 5 (minimo 0) quando a FOR atende o requisito da
        # armadura. Ignorar a segunda metade poria um Guerreiro de FOR alta 5
        # pes mais lento do que ele e.
        penalidade = 0
        for entrada in (self.doc.get("inventario") or []):
            if not entrada.get("equipado"):
                continue
            arm = self.base.opcional(str(entrada.get("item") or "")) or {}
            if arm.get("kind") != "armor" or not arm.get("speed_penalty"):
                continue
            bruta = int(arm["speed_penalty"])
            exigida = arm.get("strength")
            if isinstance(exigida, int) and self.modificadores.get("str", 0) >= exigida:
                bruta = min(0, bruta + 5)
            penalidade += bruta
            if bruta:
                detalhe.append({"origem": arm.get("name"),
                                "efeito": {"penalidade": bruta}})

        self.velocidade = self._compor_velocidade(base, concedidos, bonus, penalidade)
        self.velocidade_detalhe = detalhe

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
            "pericias": self.pericias,
            "salvas": self.salvas,
            "pericias_livres": self.pericias_livres,
            "aumentos_de_pericia": {"niveis": self.aumentos_de_pericia,
                                    "gastos": self.aumentos_detalhe},
            "boosts": {"direito": self.boosts_direito,
                       "declarados": self.boosts_declarados,
                       "fontes": self.boosts_pendentes},
            # a terceira pergunta do construtor: o que falta escolher
            "slots_abertos": self.slots_abertos(),
            "slots": self.slots,
            "conjuracao": self.conjuracao,
            "sentidos": list(self._sentidos().values()),
            "atores": self.atores,
            "concessoes_de_ator": self.concessoes_de_ator,
            "escolhas_de_feat": self.escolhas_de_feat,
            "focus_pool": self.focus_pool,
            "ac": self.ac,
            "velocidade": self.velocidade,
            "velocidade_detalhe": self.velocidade_detalhe,
            "resistencias": self.resistencias,
            "fraquezas": self.fraquezas,
            "imunidades": self.imunidades,
            "ataques": self.ataques,
            "features": self.features,
            # o que a cadeia de grants entregou sem o jogador escolher. Fica em
            # lista propria (e nao misturado em `escolhas`) porque a origem
            # importa: a ficha precisa poder dizer "Streetwise veio da
            # dedicacao", e o documento continua com so o que foi escolhido.
            "concedidos": [{"id": c["id"], "nome": c["nome"],
                            "por": c["origem"], "por_id": c["concedido_por"]}
                           for c in self.concedidos],
            "subclasses": self.slots_de_subclasse,
            "fora_do_requisito": self.fora_do_requisito,
            "avisos": self.avisos,
        }


def carregar(caminho_doc: str, base: Base | None = None) -> Personagem:
    with open(caminho_doc, encoding="utf-8") as fh:
        doc = json.load(fh)
    return Personagem(doc, base or Base())
