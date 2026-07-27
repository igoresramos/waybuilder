# Gate de nivel derivado

No PF2e o pre-requisito de um feat nunca menciona nivel -- o nivel do
feat **e** o gate. Sob a houserule isso se parte em dois numeros, e e
onde a regra caseira inteira mora.

- gates derivados: **6432**
- registros usando `class_level`: **2007** (eram 79)
- registros usando `character_level`: **4427**

## Por grupo

- `archetype`: 2154
- `classe`: 2005
- `ancestria`: 1235
- `geral`: 1038

## Exemplo de cada grupo

- **ancestria** -- `wb:feat/aberration-kinship` (Aberration Kinship, nivel 1)
  ```json
  {"all": [{"character_level": {">=": 1}}, {"has": "wb:ancestry/fleshwarp"}]}
  ```
- **archetype** -- `wb:feat/a-little-bird-told-me` (A Little Bird Told Me..., nivel 8)
  ```json
  {"character_level": {">=": 8}}
  ```
- **classe** -- `wb:feat/abundant-step` (Abundant Step, nivel 6)
  ```json
  {"class_level": {"monk": {">=": 6}}}
  ```
- **geral** -- `wb:feat/a-home-in-every-port` (A Home in Every Port, nivel 11)
  ```json
  {"character_level": {">=": 11}}
  ```
