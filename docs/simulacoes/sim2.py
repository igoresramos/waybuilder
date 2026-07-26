import random
random.seed(11)
N=100_000
def d(n,s): return sum(random.randint(1,s) for _ in range(n))
def basic(dc,mod,dmg):
    t=random.randint(1,20)+mod
    if t>=dc+10: return 0
    if t>=dc:    return dmg//2
    if t<=dc-10: return dmg*2
    return dmg
def strike(atk,ac,bonus):
    t=random.randint(1,20); tot=t+atk
    crit=(tot>=ac+10) or (t==20 and tot>=ac); hit=(tot>=ac) or t==20
    if not hit: return 0
    dm=d(4,12)+bonus
    return dm*2 if crit else dm

AC,REF,HP_PC = 45,32,270
ATK,DMGB = 38,15                    # Guerreiro nv20 (nivel de personagem entra no ataque)
DC_DIP, DC_CLERIGO = 34, 45         # Trained+Wis2  vs  Legendary+Wis7

def rodada(n=3):
    t=strike(ATK,AC,DMGB)
    if n>1: t+=strike(ATK-5,AC,DMGB)
    if n>2: t+=strike(ATK-10,AC,DMGB)
    return t

# ---- dia de aventura: 4 encontros x 4 rodadas = 16 rodadas ----
print("="*72); print("DIA DE AVENTURA — nivel 20, 4 encontros de 4 rodadas"); print("="*72)

# Guerreiro 20 puro
g=sum(sum(rodada() for _ in range(16)) for _ in range(N//100))/(N//100)
print(f"\nGuerreiro 20 puro")
print(f"   dano/dia ......... {g:7.0f}")
print(f"   cura/dia ......... {0:7.0f}")

# Guerreiro 19 / Clerigo 1, SEM TETO (Heal rank 10)
heal10=sum(d(10,8)+80 for _ in range(N))/N
cura=6*heal10
# 6 curas x 2 acoes = 12 acoes; cada 2 acoes ~ ataques 1+2
perda=sum(strike(ATK,AC,DMGB)+strike(ATK-5,AC,DMGB) for _ in range(N//10))/(N//10)*6
print(f"\nGuerreiro 19 / Clerigo 1  (SEM TETO, Heal rank 10)")
print(f"   dano/dia ......... {g-perda:7.0f}   (perdeu {perda:.0f} conjurando)")
print(f"   cura/dia ......... {cura:7.0f}   (6 casts x {heal10:.0f})")
print(f"   slots totais ..... {6:7d}   so magias de rank 1 na lista")
print(f"   DC magico ........ {DC_DIP:7d}")

# Guerreiro 19 / Clerigo 1, font no rank do slot
heal1=sum(d(1,8)+8 for _ in range(N))/N
cura_b=2*heal10+4*heal1
print(f"\nGuerreiro 19 / Clerigo 1  (font conjura no rank do slot)")
print(f"   cura/dia ......... {cura_b:7.0f}   (2x{heal10:.0f} + 4x{heal1:.0f})")

# Clerigo 20 puro
heal_p=6*heal10
# ~18 slots: metade ofensiva rank alto (2 acoes, area 3 alvos), DC 45
ofensiva=0
for _ in range(N//10):
    ofensiva+=sum(basic(DC_CLERIGO,REF,d(20,6)) for _ in range(3))
ofensiva/= (N//10)
print(f"\nClerigo 20 puro")
print(f"   cura/dia ......... {heal_p:7.0f}   (6 font x {heal10:.0f}; + pode preparar mais nos slots normais)")
print(f"   dano/dia ......... {9*ofensiva:7.0f}   (9 magias de area rank 10 x 3 alvos)")
print(f"      por magia de area .. {ofensiva:6.0f}")
print(f"   slots totais ..... {18:7d}   lista divina inteira, ranks 1-10")
print(f"   DC magico ........ {DC_CLERIGO:7d}")

# quao uteis sao as magias de SAVE do dip
print("\n"+"="*72); print("MAGIA DE SAVE: dip vs clerigo (mesma magia, rank 10)"); print("="*72)
for nome,dc in (("dip     ",DC_DIP),("clerigo ",DC_CLERIGO)):
    v=sum(basic(dc,REF,d(20,6)) for _ in range(N))/N
    print(f"   {nome} DC {dc}:  {v:6.1f} por alvo   (multiplicador {v/70:.2f})")
