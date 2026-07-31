# Pericia divina e clausulas de divindade

## `divine_skill` -- a decima lacuna de leitura

- divindades com o campo: **475**  (era **0**)
- sem a frase na prosa: **13** (Alocer, Atheism, Atheists and Free Agents, Chinostes, God Calling, Laws of Mortality, Lissala (The Order of Virtue), Norns...)

Sao filosofias e afins. Nao ter pericia divina e RESPOSTA, nao falha.

| pericia | divindades |
|---|---:|
| athletics | 50 |
| nature | 46 |
| society | 40 |
| survival | 39 |
| intimidation | 38 |
| crafting | 37 |
| diplomacy | 36 |
| occultism | 34 |
| deception | 33 |
| stealth | 28 |
| medicine | 27 |
| arcana | 19 |
| performance | 17 |
| acrobatics | 16 |
| thievery | 11 |
| religion | 3 |
| lore | 1 |

## Clausulas convertidas

- convertidas: **11**

| padrao | quantas |
|---|---:|
| proficiencia na arma favorita | 2 |
| adorador de divindade | 2 |
| proficiencia na pericia divina | 2 |
| categoria da arma favorita | 1 |
| fonte divina permitida | 1 |
| dominio concedido | 1 |
| santificacao da divindade | 1 |
| personagem sem santificacao | 1 |

| registro | clausula | vira |
|---|---|---|
| `wb:archetype/mortal-herald` | Master in master in Religion or your deity’s divine skill | `{"any": [{"proficiency": {"religion": {">=": "master"}}}, {"proficiency_divine_skill": {">=": "master"}}]}` |
| `wb:archetype/mortal-herald` | Worshiper of a specific deity | `{"has_deity": true}` |
| `wb:feat/deadly-simplicity` | deity with a simple or unarmed attack favored weapon | `{"any": [{"deity_favored_weapon_category": "simple"}, {"deity_favored_weapon_category": "unarmed"}]}` |
| `wb:feat/deadly-simplicity` | trained with your deity's favored weapon | `{"proficiency_favored_weapon": {">=": "trained"}}` |
| `wb:feat/divine-healing` | worship a deity with a divine font that grants heal | `{"deity_font_permitido": "heal"}` |
| `wb:feat/environmental-grace` | deity who grants the cold, fire, nature, or travel domain | `{"any": [{"domain": "wb:domain/cold"}, {"domain": "wb:domain/fire"}, {"domain": "wb:domain/nature"}, {"domain": "wb:domain/travel"}]}` |
| `wb:feat/mortal-herald-dedication` | master in Religion or your deity's divine skill | `{"any": [{"proficiency": {"religion": {">=": "master"}}}, {"proficiency_divine_skill": {">=": "master"}}]}` |
| `wb:feat/mortal-herald-dedication` | worshipper of a specific deity | `{"has_deity": true}` |
| `wb:feat/replenishment-of-war` | expert in your deity's favoured weapon | `{"proficiency_favored_weapon": {">=": "expert"}}` |
| `wb:feat/sanctify-water` | must worship a deity that lists "holy" or "unholy" in their sanctification | `{"any": [{"deity_sanctification": "holy"}, {"deity_sanctification": "unholy"}]}` |
| `wb:feat/vow-of-mortal-defiance` | You are not sanctified with the holy or unholy trait | `{"not": {"any": [{"has": "wb:sanctification/holy"}, {"has": "wb:sanctification/unholy"}]}}` |
