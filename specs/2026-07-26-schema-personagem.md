---
spec: schema-personagem
project: waybuilder
version: 1
status: aprovada
created: 2026-07-26
---

# Schema do documento de personagem

A ficha e um JSON. O front edita esse JSON. E so isso -- nao ha servidor, nao ha
mecanica de jogo rodando. O documento **e** o personagem.

Referencia real do formato concorrente:
`docs/referencia/pathbuilder_export_exemplo.json`

## A decisao central: guardar DECISAO, nao RESULTADO

O Pathbuilder guarda o resultado do calculo:

```json
"proficiencies": { "martial": 2, "perception": 4 },
"weapons": [{ "name": "Combat Lure", "attack": 9 }],
"acTotal": { "acProfBonus": 5, "acAbilityBonus": 3, "acTotal": 20 }
```

Funciona, e e por isso que 20+ ferramentas conseguem ler. Mas tem tres defeitos
que importam **neste** projeto especificamente:

1. **Regra que muda invalida ficha salva.** O Waybuilder existe justamente para
   mexer nas regras. Um `martial: 2` gravado nao sabe de onde veio, entao nao da
   para recalcular quando a regra de proficiencia mudar. Toda ficha antiga vira
   lixo silencioso a cada ajuste de houserule.
2. **Nao da para auditar.** `martial: 2` veio da classe, de um feat, de um item?
   O documento nao diz. Quando o numero sair errado, nao ha o que inspecionar.
3. **Nao da para desfazer.** Sem o historico de escolhas, "tira o feat do nivel
   4" exige recalcular tudo na mao.

Entao o documento guarda **as escolhas**, e o resto e derivado:

```json
{
  "esquema": "waybuilder/personagem@1",
  "base": { "versao": "2026-07-26", "pin_foundry": "87f9e502" },

  "identidade": { "nome": "Tuco Ranger", "jogador": "Igor", "notas": "" },

  "escolhas": [
    { "em": "criacao", "slot": "ancestralidade", "pega": "wb:ancestry/tanuki" },
    { "em": "criacao", "slot": "heranca",        "pega": "wb:heritage/custom-mixed" },
    { "em": "criacao", "slot": "background",     "pega": "wb:background/eagle-hunter" },
    { "em": 1, "slot": "nivel_de_classe", "pega": "wb:class/ranger" },
    { "em": 1, "slot": "boosts_livres",   "pega": ["dex","cha","con","wis"] },
    { "em": 1, "slot": "class_feat",      "pega": "wb:feat/monster-hunter" },
    { "em": 1, "slot": "ancestry_feat",   "pega": "wb:feat/natural-ambition" },
    { "em": 1, "slot": "class_feat",      "pega": "wb:feat/animal-companion",
      "concedido_por": "wb:feat/natural-ambition" },
    { "em": 2, "slot": "nivel_de_classe", "pega": "wb:class/ranger" },
    { "em": 2, "slot": "skill_feat",      "pega": "wb:feat/intimidating-glare" },
    { "em": 2, "slot": "free_archetype",  "pega": "wb:feat/summoner-dedication" },
    { "em": 3, "slot": "nivel_de_classe", "pega": "wb:class/ranger" },
    { "em": 3, "slot": "general_feat",    "pega": "wb:feat/act-together" }
  ],

  "atores": [
    { "tipo": "companheiro", "nome": "Princesa",
      "escolhas": [{ "slot": "animal", "pega": "wb:animal-companion/dromaeosaur" }] },
    { "tipo": "companheiro", "nome": "Enguia",
      "escolhas": [{ "slot": "animal", "pega": "wb:animal-companion/giant-eel" }] },
    { "tipo": "familiar", "nome": "Monstro",
      "escolhas": [{ "slot": "habilidades",
                     "pega": ["wb:familiar-ability/flier",
                              "wb:familiar-ability/manual-dexterity"] }] },
    { "tipo": "eidolon", "nome": "", "concedido_por": "wb:feat/summoner-dedication",
      "escolhas": [{ "slot": "tipo", "pega": "wb:eidolon/beast" }] }
  ],

  "inventario": [
    { "item": "wb:equipment/demon-mask", "qtd": 1, "investido": true }
  ],

  "manual": {
    "nota": "tudo aqui e escrito pelo jogador e nunca sobrescrito pelo motor",
    "hp_bonus": 0,
    "proficiencias_forcadas": {},
    "itens_caseiros": []
  }
}
```

`nivel_de_classe` repetido por nivel e o que faz o multiclasse por divisao de
niveis cair natural: `Barbaro 3 / Ladino 1` sao quatro entradas.

## Consequencias

| | Guardar decisao | Guardar resultado |
|---|---|---|
| Regra muda | re-deriva, ficha continua certa | ficha vira lixo silencioso |
| "de onde veio esse +2?" | rastreavel ate a escolha | impossivel |
| Desfazer nivel 4 | remove as entradas de `em: 4` | recalcular na mao |
| Tamanho do arquivo | ~2 KB | ~8 KB |
| Ler sem o motor | precisa derivar | direto |

O ultimo item e a unica vantagem real do outro lado, e ela se resolve emitindo
a visao calculada -- ver interoperabilidade.

## O bloco `manual` e sagrado

O motor **nunca** escreve dentro de `manual`. E onde mora o que o jogador
decidiu na marra: item caseiro, proficiencia forcada, HP extra combinado com o
mestre.

Isso e o Principio zero aplicado ao documento: o app nao arbitra. Se o jogador
quer um personagem que quebra a regra, o documento aceita, o app mostra que
esta fora do padrao, e a mesa resolve.

## Todo companheiro e um Ator, e isso e uma correcao real

O exemplo de referencia foi escolhido por ser dos mais complexos que existem:
Ranger com Summoner Dedication, carregando **dois** animal companions, **um**
familiar e **um** eidolon.

Achado ao cruzar o export com a tela do app (`docs/referencia/`): o Pathbuilder
modela companion e familiar com estrutura propria (`pets[]`, `familiars[]`), e
**o eidolon existe no app** -- tem aba propria ao lado de companion e familiar,
e o painel de plano mostra a escolha "Summoner Archetype Eidolon -> Beast
Eidolon".

Mas **o eidolon nao sobrevive ao export.** No JSON ele vira texto solto em
`specials`: `"Manifest Eidolon"`, `"Beast Eidolon"`. Sem stats, sem escolhas.

Isso e pior que uma lacuna de modelagem: **o formato de interoperabilidade
perde dado.** Quem importa aquele JSON reconstroi um personagem incompleto sem
receber nenhum aviso. Reforca a decisao de o documento proprio ser a fonte de
verdade e o export Pathbuilder ser apenas uma projecao, declaradamente com
perda.

O Foundry tem o mesmo buraco por outro caminho: `familiar` e Actor de primeira
classe, mas animal companion e eidolon tem `"rules": []` -- statblock montado na
mao, fora do sistema de regras.

Aqui os quatro sao o **mesmo tipo**: um Ator, com o mesmo motor e menos slots.
`tipo` diz qual, `concedido_por` diz de onde veio. Nao ha caso especial, nao ha
array por especie, e um eidolon nao e menos cidadao que um familiar.

**Decisao do Igor: eidolon e tratado como companheiro.** Mesmo comportamento,
mesma ficha, mesmos slots. O que muda e so o dado -- o eidolon escolhe um tipo
(Beast, Construct, Dragon...) onde o companheiro animal escolhe uma especie.
Nao ha ramo de codigo separado.

Consequencia pratica: quando entrar `tipo: "montaria"` ou qualquer coisa que a
Paizo publique depois, nao ha codigo novo -- so dado.

## Slots reconhecidos

`ancestralidade`, `heranca`, `background`, `nivel_de_classe`, `boosts_livres`,
`class_feat`, `ancestry_feat`, `skill_feat`, `general_feat`, `free_archetype`,
`skill_increase`, `lore`, `magia_preparada`, `repertorio`, `subclasse`

Slot desconhecido nao quebra o carregamento -- vira aviso e o valor e
preservado. Documento de versao futura tem que abrir numa versao velha do app.

## `concedido_por`: a arvore de escolhas

O Pathbuilder resolve isso com `childChoice` + `parentChoice` e um rotulo
concatenado (`"Natural Ambition Class FeatTanuki Feat 1"`). Funciona mas e
fragil, porque a ligacao e por string montada.

Aqui e um id: `"concedido_por": "wb:feat/natural-ambition"`. Remover o pai
identifica o filho orfao na hora.

## Visao calculada e interoperabilidade

O motor deriva, sob demanda, a **visao calculada** -- proficiencias finais,
ataque, AC decomposta, HP, DCs. Ela nunca e persistida como fonte de verdade;
e cache.

E dessa visao que sai o **export no formato Pathbuilder**, para interoperar com
os 20+ parsers que ja existem. Limitacao conhecida e aceita: `class` e `level`
la sao valor unico e nao expressam multiclasse por divisao. O export emite a
classe majoritaria e carrega o resto num bloco de extensao
`waybuilder`, ignorado por quem nao conhece.

Importar do Pathbuilder e o caminho inverso e e **melhor esforco**: resultado
nao vira decisao sem ambiguidade. O importador reconstroi o que consegue,
marca o que nao conseguiu, e joga o resto em `manual` em vez de descartar.

## Unificacao de vocabulario

Toda referencia no documento e um id `wb:` da base canonica. Nao existe nome
solto, nao existe id de Foundry nem de AoN dentro da ficha.

E o que fecha o ciclo: as tres fontes tinham tres vocabularios, a base
normalizou para um, e o personagem so fala esse.
