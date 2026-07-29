# Modelo de efeito unificado

A spec define UMA linguagem de efeito (`grants`) e ela so era
respeitada em `class`. Ancestria usava campos soltos, background
usava outro conjunto. Os campos originais permanecem -- isto
adiciona a projecao canonica, nao substitui.

- registros que ganharam `grants`: **985**
- base com `grants`: **3768** de 20375 (18.5%)

## Por kind

- `background`: 626
- `heritage`: 309
- `ancestry`: 50
- `heritage: sem efeito derivavel`: 37
- `background: sem efeito derivavel`: 11

## Exemplos

### ancestry -- `wb:ancestry/anadi` (Anadi)

```json
[
 {
  "hp_ancestry": 8
 },
 {
  "size": "med"
 },
 {
  "speed": {
   "land": 25
  }
 },
 {
  "ability_boost": {
   "opcoes": [
    "dex"
   ],
   "quantidade": 1
  }
 },
 {
  "ability_boost": {
   "opcoes": [
    "wis"
   ],
   "quantidade": 1
  }
 },
 {
  "ability_boost": {
   "livre": true,
   "quantidade": 1
  }
 },
 {
  "ability_flaw": {
   "opcoes": [
    "con"
   ]
  }
 }
]
```
### background -- `wb:background/abadars-avenger` (Abadar's Avenger)

```json
[
 {
  "ability_boost": {
   "opcoes": [
    "cha",
    "wis"
   ],
   "quantidade": 1
  }
 },
 {
  "ability_boost": {
   "livre": true,
   "quantidade": 1
  }
 },
 {
  "skill_training": {
   "auto": [
    "religion"
   ],
   "lore": [
    "Goka Lore"
   ]
  }
 },
 {
  "grant_feat": [
   "wb:feat/assurance"
  ]
 }
]
```
### heritage -- `wb:heritage/abyssal-merfolk` (Abyssal Merfolk)

```json
[
 {
  "requires_ancestry": "wb:ancestry/merfolk"
 }
]
```
