# Gate de nivel derivado

No PF2e o pre-requisito de um feat nunca menciona nivel -- o nivel do
feat **e** o gate. Sob a houserule isso se parte em dois numeros, e e
onde a regra caseira inteira mora.

- gates derivados: **6424**
- registros usando `class_level`: **2002** (eram 79)
- registros usando `character_level`: **4424**

## Por grupo

- `archetype`: 2152
- `classe`: 1875
- `ancestria`: 1227
- `geral`: 1037
- `classe (varias)`: 125
- `ancestria (varias)`: 8

## Exemplo de cada grupo

- **ancestria** -- `wb:feat/aberration-kinship` (Aberration Kinship, nivel 1)
  ```json
  {"all": [{"character_level": {">=": 1}}, {"has": "wb:ancestry/fleshwarp"}]}
  ```
- **ancestria (varias)** -- `wb:feat/caustic-nectar` (Caustic Nectar, nivel 1)
  ```json
  {"all": [{"character_level": {">=": 1}}, {"any": [{"has": "wb:ancestry/conrasu"}, {"has": "wb:ancestry/ghoran"}, {"has": "wb:ancestry/leshy"}]}]}
  ```
- **archetype** -- `wb:feat/a-little-bird-told-me` (A Little Bird Told Me..., nivel 8)
  ```json
  {"character_level": {">=": 8}}
  ```
- **classe** -- `wb:feat/abundant-step` (Abundant Step, nivel 6)
  ```json
  {"class_level": {"monk": {">=": 6}}}
  ```
- **classe (varias)** -- `wb:feat/aggressive-block` (Aggressive Block, nivel 2)
  ```json
  {"any": [{"class_level": {"fighter": {">=": 2}}}, {"class_level": {"guardian": {">=": 2}}}]}
  ```
- **geral** -- `wb:feat/a-home-in-every-port` (A Home in Every Port, nivel 11)
  ```json
  {"character_level": {">=": 11}}
  ```
