# Estatisticas de familiar e eidolon

A fonte nunca faltou. `aon_dump/rules.json` tem 3.645 registros e nenhum extrator o abria -- e a decima primeira lacuna de leitura, a primeira que e um ARQUIVO e nao um campo.

- registros de formula criados: **2** (wb:stat-formula/familiar, wb:stat-formula/eidolon)
- eidolons com array: **12**
- eidolons SEM array (marcados, nao escondidos): **1** (Swarm)

## Familiar -- lido do feat `Pet` e de `rules-2122`

| campo | valor |
|---|---|
| `hp_por_nivel` | 5 |
| `pericia_base` | 3 |
| `velocidade` | 25 |
| `tamanho` | tiny |
| `usa_mod_de_conjuracao_se_maior` | True |
| `ac_e_saves_do_mestre` | True |
| `sem_atributo_proprio` | True |

## Eidolon -- lido de `rules-1582` e do pf2etools

| campo | valor |
|---|---|
| `proficiencias` | {"fortitude": "expert", "reflex": "trained", "will": "expert", "perception": "trained"} |
| `hp_proprio` | false |
| `compartilha_pericias_do_invocador` | true |

Ele NAO tem HP proprio: compartilha o pool do invocador. Isso e achado, nao lacuna -- e a razao de `eidolon` so ter velocidade na base ate agora.
