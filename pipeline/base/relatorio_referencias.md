# Referencias resolvidas

`requires` citava ids que a base nao tem -- mas as entidades existem,
com outro slug. O extrator derivou o id do nome que tinha em maos,
antes de a reconciliacao decidir o nome canonico. Quando nem o nome
sobreviveu (o Remaster renomeou dos dois lados), quem liga e o
`remaster_id` publicado pelo proprio AoN.

- resolvidas por nome: **4**
- resolvidas por curadoria (`aliases_referencias.json`): **3**
- resolvidas pela ponte legado->remaster do AoN: **52**
- removidas por nao serem entidade: **3**
- nao resolvidas: **0**

## Pela ponte do AoN (nome mudou dos dois lados)

- `wb:feat/hellknight-armiger-dedication` -> `wb:feat/hellknight-dedication`
- `wb:feat/hellknight-signifer-dedication` -> `wb:feat/hellknight-signifer-preferment`
- `wb:spell/mage-hand` -> `wb:spell/telekinetic-hand`
- `wb:feat/crystalline-dust` -> `wb:feat/extraplanar-haze`
- `wb:feat/shining-oath` -> `wb:feat/oath-of-the-slayer`
- `wb:feat/esoteric-oath` -> `wb:feat/oath-of-the-slayer`
- `wb:feat/divine-ally` -> `wb:feat/devout-blessing`
- `wb:feat/fiendsbane-oath` -> `wb:feat/oath-of-the-slayer`
- `wb:feat/wild-shape` -> `wb:feat/untamed-form`
- `wb:heritage/sweetbreath-gnoll` -> `wb:heritage/sweetbreath-kholo`
- `wb:spell/cloudkill` -> `wb:spell/toxic-cloud`
- `wb:spell/floating-disk` -> `wb:spell/carryall`
- `wb:heritage/witch-gnoll` -> `wb:heritage/witch-kholo`
- `wb:spell/obscuring-mist` -> `wb:spell/mist`
- `wb:feat/dueling-parry-swashbuckler` -> `wb:feat/extravagant-parry`
- `wb:feat/ki-strike` -> `wb:feat/qi-spells`
- `wb:feat/wholeness-of-body` -> `wb:feat/harmonize-self`
- `wb:feat/sharp-fangs` -> `wb:feat/iruxi-armaments`
- `wb:feat/gnoll-weapon-familiarity` -> `wb:feat/kholo-weapon-familiarity`
- `wb:feat/grippli-weapon-familiarity` -> `wb:feat/tripkee-weapon-familiarity`
- `wb:feat/attack-of-opportunity` -> `wb:feat/reactive-strike`
- `wb:spell/ki-strike` -> `wb:feat/qi-spells`
- `wb:feat/skillful-tail-ganzi` -> `wb:feat/skillful-tail`
- `wb:feat/drow-shootist-dedication` -> `wb:feat/crossbow-infiltrator-dedication`
- `wb:feat/deflect-arrow` -> `wb:feat/deflect-projectile`
- `wb:feat/tail-whip` -> `wb:feat/iruxi-armaments`
- `wb:spell/vampiric-touch` -> `wb:spell/vampiric-feast`
- `wb:spell/black-tentacles` -> `wb:spell/slither`
- `wb:feat/stunning-fist` -> `wb:feat/stunning-blows`
- `wb:feat/vanths-weapon-familiarity` -> `wb:feat/duskwalker-weapon-familiarity`
- `wb:spell/dancing-lights` -> `wb:spell/light`
- `wb:feat/dragonslayer-oath` -> `wb:feat/oath-of-the-slayer`

## Por curadoria conferida a mao

- `wb:feat/dual-weapon-dedication` -> `wb:feat/dual-weapon-warrior-dedication` -- a base tem `wb:feat/dual-weapon-warrior-dedication` e `wb:archetype/dual-weapon-warrior`; a dedicacao citada e a do arquetipo, com o nome abreviado na
- `wb:heritage/cataphract` -> `wb:heritage/cataphract-fleshwarp` -- a base tem `wb:heritage/cataphract-fleshwarp`; o parser cortou o nome da ancestria do fim do nome da heranca

## Removidas: o parser virou frase em id

- `wb:heritage/versatile` -- mesmo caso do irmao you-have-a-versatile: o parser transformou a expressao "versatile heritage" em id. A linguagem de predicado ainda nao tem termo para trait de heranca versatil
- `wb:heritage/you-have-a-versatile` -- nao e entidade: o parser transformou a frase 'You have a versatile heritage.' em id. O predicado correto seria um termo sobre TRAIT de heranca versatil, que a linguagem ainda nao t

## Resolvidas por nome

- `wb:methodology/alchemical-sciences` -> `wb:methodology/alchemical-sciences-methodology-5`  (Alchemical Sciences)
- `wb:methodology/empiricism` -> `wb:methodology/empiricism-methodology-6`  (Empiricism)
- `wb:methodology/interrogation` -> `wb:methodology/interrogation-methodology-8`  (Interrogation)
- `wb:methodology/forensic-medicine` -> `wb:methodology/forensic-medicine-methodology-7`  (Forensic Medicine)
