# Referencias resolvidas

`requires` citava ids que a base nao tem -- mas as entidades existem,
com outro slug. O extrator derivou o id do nome que tinha em maos,
antes de a reconciliacao decidir o nome canonico. Quando nem o nome
sobreviveu (o Remaster renomeou dos dois lados), quem liga e o
`remaster_id` publicado pelo proprio AoN.

- resolvidas por nome: **45**
- resolvidas por curadoria (`aliases_referencias.json`): **10**
- resolvidas pela ponte legado->remaster do AoN: **13**
- removidas por nao serem entidade: **3**
- nao resolvidas: **1**

## Pela ponte do AoN (nome mudou dos dois lados)

- `wb:spell/mage-hand` -> `wb:spell/telekinetic-hand`
- `wb:heritage/sweetbreath-gnoll` -> `wb:heritage/sweetbreath-kholo`
- `wb:spell/cloudkill` -> `wb:spell/toxic-cloud`
- `wb:spell/floating-disk` -> `wb:spell/carryall`
- `wb:heritage/witch-gnoll` -> `wb:heritage/witch-kholo`
- `wb:spell/obscuring-mist` -> `wb:spell/mist`
- `wb:spell/ki-strike` -> `wb:spell/inner-upheaval`
- `wb:spell/vampiric-touch` -> `wb:spell/vampiric-feast`
- `wb:spell/black-tentacles` -> `wb:spell/slither`
- `wb:spell/dancing-lights` -> `wb:spell/light`

## Por curadoria conferida a mao

- `wb:feat/dual-weapon-dedication` -> `wb:feat/dual-weapon-warrior-dedication` -- a base tem `wb:feat/dual-weapon-warrior-dedication` e `wb:archetype/dual-weapon-warrior`; a dedicacao citada e a do arquetipo, com o nome abreviado na
- `wb:heritage/cataphract` -> `wb:heritage/cataphract-fleshwarp` -- a base tem `wb:heritage/cataphract-fleshwarp`; o parser cortou o nome da ancestria do fim do nome da heranca
- `wb:class-feature/redeemer-cause` -> `wb:class-feature/redemption` -- idem; redemption.json, PC2: 'Yearning for all to live in harmony, you make every attempt to redeem those others might slay'
- `wb:class-feature/liberator-cause` -> `wb:class-feature/liberation` -- idem; liberation.json, PC2: 'You will see all people free from bondage and prohibitions'
- `wb:class-feature/paladin-cause` -> `wb:class-feature/justice` -- as causes do Champion foram renomeadas no Player Core 2. O Foundry no pin tem justice.json/redemption.json/liberation.json/obedience.json/avenger.json
- `wb:class-feature/wild-order` -> `wb:class-feature/untamed-order` -- o Foundry no pin tem untamed-order.json ao lado de animal/leaf/storm/flame-order; 'Wild' e o nome Legacy da ordem, do mesmo jeito que Wild Shape virou

## Removidas: o parser virou frase em id

- `wb:heritage/versatile` -- mesmo caso do irmao you-have-a-versatile: o parser transformou a expressao "versatile heritage" em id. A linguagem de predicado ainda nao tem termo para trait de heranca versatil
- `wb:heritage/you-have-a-versatile` -- nao e entidade: o parser transformou a frase 'You have a versatile heritage.' em id. O predicado correto seria um termo sobre TRAIT de heranca versatil, que a linguagem ainda nao t

## Resolvidas por nome

- `wb:class-feature/alchemical-sciences` -> `wb:methodology/alchemical-sciences`  (Alchemical Sciences)
- `wb:class-feature/enigma-muse` -> `wb:class-feature/enigma`  (Enigma)
- `wb:class-feature/ruffian-racket` -> `wb:class-feature/ruffian`  (Ruffian)
- `wb:class-feature/mastermind-racket` -> `wb:class-feature/mastermind`  (Mastermind)
- `wb:class-feature/warrior-muse` -> `wb:class-feature/warrior`  (Warrior)
- `wb:class-feature/scoundrel-racket` -> `wb:class-feature/scoundrel`  (Scoundrel)
- `wb:class-feature/polymath-muse` -> `wb:class-feature/polymath`  (Polymath)
- `wb:class-feature/maestro-muse` -> `wb:class-feature/maestro`  (Maestro)
- `wb:class-feature/universalist-wizard` -> `wb:arcane-school/universalist`  (Universalist)
- `wb:class-feature/empiricism` -> `wb:methodology/empiricism`  (Empiricism)
- `wb:class-feature/interrogation` -> `wb:methodology/interrogation`  (Interrogation)
- `wb:class-feature/thief-racket` -> `wb:class-feature/thief`  (Thief)
- `wb:class-feature/forensic-medicine` -> `wb:methodology/forensic-medicine`  (Forensic Medicine)
- `wb:class-feature/warpriest-doctrine` -> `wb:class-feature/warpriest`  (Warpriest)

## Nao resolvidas

- `wb:feat/underworld-connections` citado 1x
