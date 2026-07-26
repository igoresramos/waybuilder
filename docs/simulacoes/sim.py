import random
random.seed(7)
N=200_000
def d(n,s): return sum(random.randint(1,s) for _ in range(n))

def basic_save(dc, mod, dmg):
    t=random.randint(1,20)+mod
    if t>=dc+10: return 0
    if t>=dc:    return dmg//2
    if t<=dc-10: return dmg*2
    return dmg

def cone(dc, dice, ntargets, ref):
    """dano total do cone contra ntargets"""
    return sum(basic_save(dc, ref, d(dice,6)) for _ in range(ntargets))

def strike(atk, ac, dice_n, dice_s, bonus):
    t=random.randint(1,20); tot=t+atk
    if t==20: tot+=0
    crit = tot>=ac+10 or (t==20 and tot>=ac)
    hit  = tot>=ac or (t==20)
    if not hit: return 0
    dmg=d(dice_n,dice_s)+bonus
    return dmg*2 if crit else dmg

# ---------- cenarios nivel 10 ----------
MOOK =dict(nome="4 mooks nv7", ac=25, ref=16, hp=115, n=4)
BOSS =dict(nome="2 bosses nv10",ac=27, ref=19, hp=165, n=2)

DC_DIP=24   # Guerreiro 9/Mago 1: 10+10+trained 2+Int 2
DC_MAGO=29  # Mago 10: 10+10+expert 4+Int 5

print("="*74)
print("BREATHE FIRE — dano medio por conjuracao (cone 15ft)")
print("="*74)
for cen in (MOOK,BOSS):
    for alvos in (1,2,3):
        if alvos>cen["n"]: continue
        r3=sum(cone(DC_DIP,6,alvos,cen["ref"]) for _ in range(N))/N
        r5=sum(cone(DC_DIP,10,alvos,cen["ref"]) for _ in range(N))/N
        print(f"  {cen['nome']:15} {alvos} alvo(s):  rank3={r3:6.1f}   rank5={r5:6.1f}   ganho={r5-r3:+5.1f} ({r5/r3-1:+.0%})")

print()
print("  referencia: Mago 10 puro, Fireball rank 5, DC 29")
for cen in (MOOK,BOSS):
    for alvos in (2,3):
        if alvos>cen["n"]: continue
        f=sum(cone(DC_MAGO,10,alvos,cen["ref"]) for _ in range(N))/N
        print(f"    {cen['nome']:15} {alvos} alvos: {f:6.1f}")

# ---------- combate completo 4 rodadas ----------
print()
print("="*74)
print("COMBATE DE 4 RODADAS — Guerreiro 9/Mago 1 (dano total acumulado)")
print("="*74)
ATK,MAP1,MAP2 = 22,17,12
def rodada_ataques(ac, n=3):
    tot=strike(ATK,ac,2,12,8)
    if n>1: tot+=strike(MAP1,ac,2,12,8)
    if n>2: tot+=strike(MAP2,ac,2,12,8)
    return tot

for cen in (MOOK,BOSS):
    alvos=min(3,cen["n"])
    so_ataque=cast3=cast5=0
    for _ in range(N//4):
        so_ataque += sum(rodada_ataques(cen["ac"]) for _ in range(4))
        # R1: cone (2 acoes) + 1 ataque; R2-4: 3 ataques
        cast3 += cone(DC_DIP,6, alvos,cen["ref"]) + rodada_ataques(cen["ac"],1) + sum(rodada_ataques(cen["ac"]) for _ in range(3))
        cast5 += cone(DC_DIP,10,alvos,cen["ref"]) + rodada_ataques(cen["ac"],1) + sum(rodada_ataques(cen["ac"]) for _ in range(3))
    k=N//4
    print(f"  {cen['nome']} (cone pega {alvos}):")
    print(f"     so atacando .............. {so_ataque/k:6.1f}")
    print(f"     1 Breathe Fire rank 3 .... {cast3/k:6.1f}  ({cast3/so_ataque-1:+.1%})")
    print(f"     1 Breathe Fire rank 5 .... {cast5/k:6.1f}  ({cast5/so_ataque-1:+.1%})")
