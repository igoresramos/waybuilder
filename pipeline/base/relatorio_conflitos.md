# Divergencias detectadas fora dos extratores

Os extratores fundem as fontes por dentro e emitem um valor unico.
Esta passada compara a base contra o AoN e o Foundry em disco, pelo
`xref`, e anota o que discorda -- o contrato da spec e que
divergencia nunca e silenciada.

- registros que ganharam conflito: **427**
- registros com conflito na base: **1830**

## Por campo

- `source.book`: 333
- `rarity`: 55
- `name`: 51

## Por kind

- **equipment**: {'rarity': 26, 'source.book': 92}
- **weapon**: {'source.book': 94, 'rarity': 4}
- **class-feature**: {'source.book': 37, 'name': 51}
- **feat**: {'source.book': 63}
- **spell**: {'rarity': 2, 'source.book': 20}
- **background**: {'rarity': 17}
- **action**: {'source.book': 15, 'rarity': 2}
- **heritage**: {'source.book': 5, 'rarity': 1}
- **armor**: {'source.book': 2, 'rarity': 3}
- **ritual**: {'source.book': 3}
- **ancestry**: {'source.book': 1}
- **shield**: {'source.book': 1}
