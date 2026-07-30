# Normalizacao de `traits` no fim do build

- conflitos de traits resolvidos: **15** de 15 (em 0 deles o valor emitido mudou; nos outros as fontes ja concordavam e so o registro de conflito sobrava)
- registros com `traits` normalizados: **905**
- conflitos de traits restantes: **0**

## Termos substituidos

- `evocation` em 185 registro(s)
- `necromancy` em 130 registro(s)
- `transmutation` em 118 registro(s)
- `conjuration` em 102 registro(s)
- `divination` em 97 registro(s)
- `abjuration` em 83 registro(s)
- `enchantment` em 80 registro(s)
- `positive` em 64 registro(s)
- `negative` em 62 registro(s)
- `good` em 26 registro(s)
- `evil` em 14 registro(s)
- `metamagic` em 10 registro(s)
- `grippli` em 5 registro(s)
- `lawful` em 5 registro(s)
- `aasimar` em 3 registro(s)
- `gnoll` em 3 registro(s)
- `ifrit` em 2 registro(s)
- `chaotic` em 2 registro(s)
- `true name` em 2 registro(s)
- `locathah` em 1 registro(s)

## Amostra

- `wb:feat/azata-magic`: ['aasimar'] -> ['nephilim']
- `wb:feat/corrupted-shield`: ['champion', 'divine', 'necromancy', 'negative', 'void'] -> ['champion', 'divine', 'void']
- `wb:feat/enforced-order`: ['aasimar'] -> ['nephilim']
- `wb:feat/festering-wound`: ['archetype', 'disease', 'divine', 'necromancy'] -> ['archetype', 'disease', 'divine']
- `wb:feat/gnoll-weapon-expertise`: ['gnoll', 'kholo'] -> ['kholo']
- `wb:feat/gnoll-weapon-practicality`: ['gnoll', 'kholo'] -> ['kholo']
- `wb:feat/grippli-glide`: ['grippli'] -> ['tripkee']
- `wb:feat/grippli-lore`: ['grippli'] -> ['tripkee']
- `wb:feat/grippli-weapon-expertise`: ['grippli'] -> ['tripkee']
- `wb:feat/grippli-weapon-innovator`: ['grippli'] -> ['tripkee']
- `wb:feat/heatwave`: ['ifrit'] -> ['naari']
- `wb:feat/inner-fire`: ['ifrit'] -> ['naari']
- `wb:feat/necrotic-infusion`: ['cleric', 'concentrate', 'metamagic', 'spellshape'] -> ['cleric', 'concentrate', 'spellshape']
- `wb:feat/nocturnal-grippli`: ['grippli'] -> ['tripkee']
- `wb:feat/peri-magic`: ['aasimar'] -> ['nephilim']
- `wb:feat/safeguarded-spell`: ['concentrate', 'metamagic', 'sorcerer', 'spellshape'] -> ['concentrate', 'sorcerer', 'spellshape']
- `wb:feat/silent-spell`: ['concentrate', 'metamagic', 'wizard', 'spellshape'] -> ['concentrate', 'spellshape', 'wizard']
- `wb:feat/terraforming-spell`: ['concentrate', 'earth', 'metamagic', 'sorcerer', 'transmutation', 'spellshape'] -> ['concentrate', 'earth', 'sorcerer', 'spellshape']
- `wb:feat/whispering-steps`: ['amp', 'mental', 'mental', 'occult', 'psychic'] -> ['amp', 'mental', 'occult', 'psychic']
- `wb:spell/aberrant-form`: ['polymorph', 'transmutation'] -> ['polymorph']
- `wb:spell/abyssal-plague`: ['chaotic', 'disease', 'evil', 'necromancy'] -> ['disease', 'unholy']
- `wb:spell/accelerated-decomposition`: ['concentrate', 'manipulate', 'oracle', 'uncommon', 'void', 'focus', 'negative'] -> ['concentrate', 'focus', 'manipulate', 'oracle', 'uncommon', 'void']
- `wb:spell/admonishing-ray`: ['attack', 'necromancy', 'nonlethal'] -> ['attack', 'nonlethal']
- `wb:spell/agonizing-despair`: ['emotion', 'enchantment', 'fear', 'mental'] -> ['emotion', 'fear', 'mental']
- `wb:spell/air-walk`: ['air', 'transmutation'] -> ['air']
- `wb:spell/airburst`: ['air', 'evocation', 'uncommon'] -> ['air', 'uncommon']
- `wb:spell/all-is-one-one-is-all`: ['necromancy', 'rare'] -> ['rare']
- `wb:spell/all-encompassing-hunger`: ['death', 'focus', 'manipulate', 'uncommon', 'void', 'wizard', 'negative'] -> ['death', 'focus', 'manipulate', 'uncommon', 'void', 'wizard']
- `wb:spell/allfood`: ['transmutation', 'uncommon'] -> ['uncommon']
- `wb:spell/anathematic-reprisal`: ['enchantment', 'mental'] -> ['mental']
- `wb:spell/ancestral-winds`: ['concentrate', 'emotion', 'fear', 'manipulate', 'mental', 'uncommon', 'void', 'negative'] -> ['concentrate', 'emotion', 'fear', 'manipulate', 'mental', 'uncommon', 'void']
- `wb:spell/ancient-dust`: ['cantrip', 'necromancy', 'negative', 'uncommon', 'void'] -> ['cantrip', 'uncommon', 'void']
- `wb:spell/angel-form`: ['holy', 'polymorph', 'transmutation'] -> ['holy', 'polymorph']
- `wb:spell/animal-allies`: ['conjuration'] -> []
- `wb:spell/animate-rope`: ['transmutation'] -> []
- `wb:spell/antimagic-field`: ['abjuration', 'rare'] -> ['rare']
- `wb:spell/apex-companion`: ['druid', 'polymorph', 'transmutation', 'uncommon', 'focus'] -> ['druid', 'focus', 'polymorph', 'uncommon']
- `wb:spell/approximate`: ['cantrip', 'detection', 'divination'] -> ['cantrip', 'detection']
- `wb:spell/aqueous-blast`: ['evocation', 'rare', 'water'] -> ['rare', 'water']
- `wb:spell/aromatic-lure`: ['emotion', 'enchantment', 'incapacitation', 'mental', 'rare'] -> ['emotion', 'incapacitation', 'mental', 'rare']
