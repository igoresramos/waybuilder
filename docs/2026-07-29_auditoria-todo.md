# Auditoria do TODO -- 2026-07-29

Os 54 itens abertos foram medidos contra o codigo e a base **de hoje**, em tres
frentes paralelas (motor, base/pipeline, escopo/decisao). Motivo: 28 dos 54 nao
citavam data de medicao nenhuma, e 18 citavam 27/07 -- varias sessoes de conserto
passaram por cima desde entao.

Tudo que a auditoria marcou como resolvido foi **reconferido a mao** antes de
entrar nesta lista. Um caso (item 3) o agente acertou e a minha primeira e a
segunda sonda erraram -- o rank mora em `conjuracao[0]["dc"]["rank"]`, nao em
`conjuracao[0]["rank"]`.

## Placar

| | itens |
|---|---:|
| abertos antes | 54 |
| **fechados pela auditoria** | **15** |
| fundidos em outro item | 2 |
| abertos depois | **37** |

## Fechados -- resolvidos ou obsoletos

| id | veredito | prova |
|---|---|---|
| 3 | resolvido | `teste_motor.py:241-249`: Cloistered 15 -> master, Warpriest 15 -> expert, mesma classe e nivel. E o companheiro sai no `class_level` de quem concedeu (`Ranger 2` num personagem 12 -> companheiro 4) |
| 7 | resolvido | `docs/simulacoes/2026-07-27_balanceamento.md` cobre niveis 1-15, combate + pericia/social/exploracao, HOUSE vs RAW vs RAW+FA |
| 8 | resolvido | o mesmo relatorio ja usa politica de acao SIMETRICA -- e exatamente a correcao do vies que o Fable apontou |
| 9 | resolvido | o app existe: Vite+React PWA offline, picker modal reusado em todo slot, o JSON e a ficha |
| 16 | obsoleto | o app nao vai ser publicado (decisao de 27/07); licenciamento saiu do escopo |
| 23 | obsoleto | `Triggerbrand Salvo` esta na base (falso alarme); wayfinders do PFS Guide sao limite de fonte declarado |
| 35 | resolvido | os 3 registros tem `source` e `license` hoje, de carona no re-dump do pf2etools |
| 36 | resolvido | 0 linhas `REVISAR` no relatorio de colisoes (eram 13) |
| 37 | resolvido | 0 arquivos `.missing` -- `buscar_fontes.sh` clona e fixa o repo de verdade |
| 44 | resolvido | a tabela de conjuracao saiu do campo `markdown` do AoN; nao depende dos PDFs |
| 54 | resolvido | `tactic` = 37 e `class-kit` = 32, exatamente o esperado |
| 56 | resolvido | 0 registros pre-remaster sem sucessor (eram 69) |
| 66 | resolvido | `_conjuracao_de_arquetipo` entrou hoje 16:06; Cleric Dedication + Basic Spellcasting devolve tradicao `divine` |
| 71 | resolvido | 123 feats com `class_level` dentro de `any` sobre todos os traits de classe (o item falava de 122) |
| 74 | resolvido | ficha sem boost declarado agora avisa: "0 declarado(s) de 9 a que o personagem tem direito -- faltam 9", com as fontes |

## Fundidos

- **41 -> 78.** Mesma tradicao de conjuracao de Feiticeiro/Invocador/Bruxa; o 41
  levantou, o 78 mediu.
- **33 -> 55.** A metrica "3.033 mono-fonte" nao e reproduzivel como buraco de
  conteudo: ela mistura proveniencia com ausencia. O que falta de verdade e o
  que o 55 ja lista.

## Corrigidos -- o item mentia o numero

| id | dizia | e hoje |
|---|---|---|
| 40 | 175 das 176 sub-escolhas sem efeito | **114 de 418 ja tem `grants` que o motor aplica** (27%). O mecanismo parou de ser o problema; a extracao continua sendo -- 304 com `grants: []` |
| 52 | 684 campos com `prov` desconhecida + 128 vazios | **13** |
| 69 | 25 de 27 classes com o balaio `outras-opcoes` | **16 de 27**; Fighter e Monk (os piores exemplos) corrigidos |
| 60 | 679 concessoes de `GrantItem` nao resolvidas | 491 hoje, mas as categorias nao mapeiam 1:1 -- **re-medir com a metodologia original antes de decidir** |
| 78 | 48 subclasses com `grants: []` | so bloodline do Feiticeiro (19/19) esta 100% vazio; patron e eidolon ja tem grants de pericia, **mas nenhum carrega tradicao** -- o defeito central persiste |
| 38 | 160 registros fora do mapa canonico (0,85%) | 176 (0,89%) -- cresceu com a base |
| 34 | varios sub-pontos | licenca inferida zerou; `feat_category` 256 -> 172; `source.page` ausente **piorou** 1.506 -> 1.598 |

## Mudou de natureza

**Item 18** deixa de ser "3 ausencias pontuais". `Life-Saving Yowl` era premissa
errada (existe como `Caterwaul`). O que sobra e a causa: **heritage so e
enumerado a partir do Foundry, nunca do AoN** -- e por isso `Cavern Kobold` e
`Spellscale Kobold` faltam. Titulo novo, escopo novo.

**Item 59** ficou maior do que estava escrito. O item falava de 1.564 registros
que perderam mecanica; os gaps originais foram corrigidos e **outros
apareceram** (724 com `grants_completos == False`, com perfil totalmente
diferente: spell 438, heritage 258, feat 27). Pior: **14.247 registros (72% da
base) nao emitem o campo** -- equipment 6.122, feat 3.849, weapon 1.042,
class-feature 841. A metrica de cobertura e cega em tres quartos da base e
**nenhum portao cobra isso**. Metrica sem contrapartida de erro e propaganda.

## A pergunta do item 91, respondida

O achatamento de "X and either Y or Z" **e falha estrutural de desenho, mas caso
unico hoje**.

Causa: `pipeline/extratores/feats.py::_clausula_rank` escolhe **um conector para
o grupo inteiro** -- `conector = "any" if " or " in resto else "all"` --, olhando
se existe " or " em qualquer lugar do texto, sem posicao estrutural e sem
aninhamento.

Varredura nos 19.706 registros: **4 candidatos, 1 defeito real**. Nos outros 3, um
dos alvos e feat e nao pericia, entao `_clausula_rank` devolve `None` e o parser
geral -- que trata "either...or" corretamente -- assume e produz o aninhamento
certo.

Consequencia para o plano: consertar por ser desenho errado, **sem esperar fila**.
E o mesmo registro (`Marshal Dedication`) tem o defeito irmao no `grants` (da
Diplomacy **e** Intimidation expert quando o RAW e ou-ou, item 75b) -- os dois
saem juntos.

## Seguem validos, sem mudanca

10, 13, 19, 22, 42, 61, 70, 72, 73, 75, 77, 79.

O item 70 foi reconfirmado numero a numero: 926 alvos de `grant_feat`, 450 ids
`wb:` validos, 400 dict stringificado, 76 nome cru = **476 nao resolvidos, 100%
em background**.
