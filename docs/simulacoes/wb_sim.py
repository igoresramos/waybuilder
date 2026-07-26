#!/usr/bin/env python3
"""
Waybuilder -- simulador de balanceamento.

Compara tres regimes:
  RAW      classe unica (Pathfinder 2e oficial)
  RAW_FA   classe unica + dedicacao de multiclasse via Free Archetype
  HOUSE    niveis de classe divididos (as 22 regras do waybuilder)

Fontes de dado (nao inventadas):
  classes.json         progressao exata extraida de foundryvtt/pf2e
  bench_monstros.json  mediana de AC/HP/save/ataque/dano de 3.624 criaturas do AoN

Premissas explicitas estao em ASSUNCOES no fim do arquivo.
"""
import json, random, statistics as st, itertools, collections, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
CLASSES = json.load(open(f"{HERE}/classes.json"))
for _c in CLASSES.values():                      # chaves de JSON voltam string
    _c["prog"] = {int(k): v for k, v in _c["prog"].items()}
BENCH   = {int(k): v for k, v in json.load(open(f"{HERE}/bench_monstros.json")).items()}

RANK_BONUS = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8}      # untrained/trained/expert/master/legendary

# DC padrao por nivel (PF2e Core, tabela 10-5)
DC_POR_NIVEL = {1:15,2:16,3:18,4:19,5:20,6:22,7:23,8:24,9:26,10:27,
                11:28,12:30,13:31,14:32,15:34,16:35,17:36,18:38,19:39,20:40}

# curva de itens assumida (progressao de riqueza padrao)
def potencia_arma(lv):   return 3 if lv>=16 else 2 if lv>=10 else 1 if lv>=2 else 0
def dados_striking(lv):  return 4 if lv>=19 else 3 if lv>=12 else 2 if lv>=4 else 1
def potencia_armadura(lv): return 3 if lv>=18 else 2 if lv>=11 else 1 if lv>=5 else 0
def resiliente(lv):      return 3 if lv>=20 else 2 if lv>=14 else 1 if lv>=8 else 0

def mod_chave(lv):
    "habilidade-chave partindo de 18, com boosts em 5/10/15/20"
    return 4 if lv<10 else 5 if lv<20 else 6
def mod_secundario(lv):
    return 2 if lv<10 else 3

# slots de conjurador pleno por nivel de classe: {rank: n}
def slots_conjurador(nc):
    if nc < 1: return {}
    s = {}
    for rank in range(1, 11):
        primeiro = 2*rank - 1
        if nc >= primeiro:
            s[rank] = 2 if nc == primeiro else 3
    if nc >= 19: s[10] = 1
    if 10 in s and nc < 19: del s[10]
    return s

# Weapon Specialization: marciais no 7 (greater 15), casters no 13
MARCIAIS = {"fighter","barbarian","rogue","monk","champion","ranger","alchemist"}
def weapon_spec(cls, nc, rank):
    if nc < (7 if cls in MARCIAIS else 13): return 0
    base = {2:2, 3:3, 4:4}.get(rank, 0)
    if cls in MARCIAIS and nc >= 15: base *= 2
    return base


class Personagem:
    def __init__(self, regime, splits, nivel, dedicacao=None, nome=None):
        self.regime = regime
        self.splits = dict(splits)              # {classe: nivel_de_classe}
        self.nivel  = nivel
        self.dedicacao = dedicacao
        self.nome = nome or self._nome()
        assert sum(self.splits.values()) == nivel, (self.splits, nivel)
        self.principal = max(self.splits, key=lambda c: self.splits[c])
        self._derivar()

    def _nome(self):
        s = " / ".join(f"{c.capitalize()} {n}" for c, n in
                       sorted(self.splits.items(), key=lambda kv: -kv[1]))
        return s + (f" +{self.dedicacao.capitalize()}Ded" if self.dedicacao else "")

    def rank(self, categoria):
        """Regra 3/4: rank vem do nivel da classe que concede; melhor entre as classes."""
        melhor = 0
        for cls, nc in self.splits.items():
            d = CLASSES[cls]
            r = 0
            if categoria in d["attacks"]:    r = d["attacks"][categoria]
            elif categoria in d["defenses"]: r = d["defenses"][categoria]
            elif categoria in d["saves"]:    r = d["saves"][categoria]
            elif categoria == "perception":  r = d["perception"]
            elif categoria == "spellcasting": r = 1 if cls in CASTERS else 0
            for lv, ups in d["prog"].items():
                if lv <= nc and categoria in ups:
                    r = max(r, ups[categoria])
            melhor = max(melhor, r)
        # dedicacao de arquetipo: RAW, checada contra nivel de personagem
        if self.dedicacao and categoria == "spellcasting":
            arq = 1
            if self.nivel >= 12: arq = 2
            if self.nivel >= 18: arq = 3
            melhor = max(melhor, arq)
        return melhor

    def _derivar(self):
        lv = self.nivel
        self.hp = 8 + sum(CLASSES[c]["hp"]*n for c, n in self.splits.items()) + 3*lv

        # MAD: so a classe PRINCIPAL sustenta habilidade-chave maxima.
        # As demais ficam em atributo secundario -- custo real de multiclassar.
        principal_marcial = self.principal in MARCIAIS
        principal_caster  = self.principal in CASTERS
        tem_marcial = any(c in MARCIAIS for c in self.splits)
        tem_caster  = any(c in CASTERS  for c in self.splits)
        self.mod_atk = mod_chave(lv) if principal_marcial else (mod_secundario(lv) if tem_marcial else mod_secundario(lv))
        self.mod_mag = mod_chave(lv) if principal_caster  else mod_secundario(lv)

        rk_arma = max(self.rank("martial"), self.rank("simple"), self.rank("unarmed"))
        self.rank_arma = rk_arma
        self.ataque = (lv + RANK_BONUS[rk_arma] + self.mod_atk + potencia_arma(lv)) if rk_arma else 0

        marciais = [c for c in self.splits if c in MARCIAIS]
        cls_arma = max(marciais, key=lambda c: self.splits[c]) if marciais else self.principal
        self.dano_spec = weapon_spec(cls_arma, self.splits.get(cls_arma, 0), rk_arma)
        self.dados_dano = dados_striking(lv)

        rk_arm = max(self.rank("light"), self.rank("medium"), self.rank("heavy"), self.rank("unarmored"))
        # Dex util limitada pela armadura: pesada/media capam o bonus
        dex_ac = 4 if principal_caster or self.rank("unarmored") >= rk_arm else 3
        self.ac = 10 + dex_ac + RANK_BONUS[rk_arm] + lv + potencia_armadura(lv)

        self.saves = {}
        for sv in ("fortitude", "reflex", "will"):
            r = self.rank(sv)
            self.saves[sv] = lv + RANK_BONUS[r] + mod_secundario(lv) + resiliente(lv) if r else 0

        rk_mag = self.rank("spellcasting")
        self.rank_magia = rk_mag
        self.dc_magia = 10 + lv + RANK_BONUS[rk_mag] + self.mod_mag if rk_mag else 0

        self.slots = collections.Counter()
        for c, n in self.splits.items():
            if c in CASTERS:
                for rank, qtd in slots_conjurador(n).items(): self.slots[rank] += qtd
        if self.dedicacao in CASTERS:
            for gate, rank in ((4,1),(6,2),(8,3),(12,4),(14,5),(16,6),(18,7),(20,8)):
                if lv >= gate: self.slots[rank] += 1

        # regra 17: elevacao ate metade do nivel de PERSONAGEM (slots de classe)
        # regra 18: slots vindos de dedicacao ficam no RAW -> rank do proprio slot
        self.rank_efetivo = (lv + 1)//2 if tem_caster else 0
        self.rank_classe_max = max((max(slots_conjurador(n)) if slots_conjurador(n) else 0)
                                    for c, n in self.splits.items() if c in CASTERS) if tem_caster else 0

        # regras 9/10: automaticas sempre; livres so o delta
        ordem = sorted(self.splits.items(), key=lambda kv: -kv[1])
        livres, automaticas = 0, 0
        for i, (c, n) in enumerate(ordem):
            orc = CLASSES[c]["skills"] + 3           # +Int
            livres = max(livres, orc)                # delta = max()
            automaticas += 1 if i == 0 else 1        # cada classe traz sua assinatura
        self.n_pericias = livres + automaticas
        inc = [l for l in CLASSES[self.principal]["skillInc"] if l <= lv]
        self.rank_pericia_top = min(4, 1 + len(inc)//2)

CASTERS = {"wizard","cleric","druid","sorcerer","bard"}


# ---------------------------------------------------------------- combate
def d20(): return random.randint(1, 20)

def grau(total, dc, nat):
    g = 3 if total >= dc+10 else 2 if total >= dc else 1 if total > dc-10 else 0
    if nat == 20: g = min(3, g+1)
    elif nat == 1: g = max(0, g-1)
    return g                                     # 0 crit-fail 1 fail 2 sucesso 3 crit

def dano_arma(p):
    return sum(random.randint(1,8) for _ in range(p.dados_dano)) + p.mod_atk + p.dano_spec

def turno_marcial(p, ac):
    total = 0
    for i, pen in enumerate((0, -5, -10)):
        if p.ataque == 0: break
        n = d20(); g = grau(n + p.ataque + pen, ac, n)
        if g == 3: total += dano_arma(p)*2
        elif g == 2: total += dano_arma(p)
    return total

def turno_conjurador(p, ref, n_alvos, ac=99):
    """2 acoes: magia de area elevada ao rank efetivo. 1 acao sobra (ignorada)."""
    if not p.slots or p.dc_magia == 0: return turno_marcial(p, ac)
    rank = min(p.rank_efetivo, 10)
    dados = 2*rank                                   # ~2d6 por rank (fireball-like)
    tot = 0
    for _ in range(n_alvos):
        n = d20(); g = grau(n + ref, p.dc_magia, n)
        d = sum(random.randint(1,6) for _ in range(dados))
        tot += [d*2, d, d//2, 0][g]
    return tot

def simular_combate(party, nivel, n_inimigos=3, max_rodadas=6):
    m = BENCH[min(24, max(1, nivel))]
    inimigos = [m["hp"]] * n_inimigos
    hp = {i: p.hp for i, p in enumerate(party)}
    for rodada in range(1, max_rodadas+1):
        # party ataca
        for idx, p in enumerate(party):
            if hp[idx] <= 0: continue
            vivos = [i for i, h in enumerate(inimigos) if h > 0]
            if not vivos: return dict(vitoria=True, rodadas=rodada-1, hp_perdido=sum(p.hp for p in party)-sum(max(0,v) for v in hp.values()))
            if p.rank_magia >= 1 and p.slots:
                d = turno_conjurador(p, m["ref"], min(len(vivos), 3), m["ac"])
                for i in vivos[:3]: inimigos[i] -= d//max(1,min(len(vivos),3))
            else:
                inimigos[vivos[0]] -= turno_marcial(p, m["ac"])
        if all(v <= 0 for v in inimigos):
            return dict(vitoria=True, rodadas=rodada,
                        hp_perdido=sum(p.hp for p in party)-sum(max(0,v) for v in hp.values()))
        # inimigos atacam
        for i, h in enumerate(inimigos):
            if h <= 0: continue
            alvos = [k for k, v in hp.items() if v > 0]
            if not alvos: return dict(vitoria=False, rodadas=rodada, hp_perdido=sum(p.hp for p in party))
            alvo = random.choice(alvos)
            for pen in (0, -5):
                n = d20(); g = grau(n + m["atk"] + pen, party[alvo].ac, n)
                if g == 3: hp[alvo] -= m["dmg"]*2
                elif g == 2: hp[alvo] -= m["dmg"]
    return dict(vitoria=all(v <= 0 for v in inimigos), rodadas=max_rodadas,
                hp_perdido=sum(p.hp for p in party)-sum(max(0,v) for v in hp.values()))


# ---------------------------------------------------------------- pericias / aventura
PILARES = ["social","furtividade","ladroagem","atletismo","saber","medicina","natureza","percepcao"]

def prova_pericia(p, dc, treinado):
    if not treinado: return 0.0
    mod = p.nivel + RANK_BONUS[p.rank_pericia_top] + mod_secundario(p.nivel) + (p.nivel//5)
    acertos = sum(1 for _ in range(400) if (lambda n: grau(n+mod, dc, n))(d20()) >= 2)
    return acertos/400

def cobertura_aventura(party, nivel):
    """Aventura padrao: 8 pilares, cada um exigindo pelo menos um personagem treinado."""
    dc = DC_POR_NIVEL[min(20, nivel)]
    random.seed(hash((nivel, tuple(p.nome for p in party))) & 0xffffffff)
    cobertos, taxas = 0, []
    for pilar in PILARES:
        # quem tem pericia sobrando cobre o pilar (proxy: n_pericias vs 8 pilares)
        melhor = 0.0
        for p in party:
            treinado = random.random() < min(1.0, p.n_pericias/10)
            melhor = max(melhor, prova_pericia(p, dc, treinado))
        if melhor > 0: cobertos += 1
        taxas.append(melhor)
    return dict(pilares_cobertos=cobertos, taxa_media=st.mean(taxas))
