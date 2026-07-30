---
spec: velocidade
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: [43, 72]
---

# Spec -- a ficha nao tem Velocidade

## O problema

`visao` nao tem `velocidade`. A ficha do COMPANHEIRO tem (`PainelDireito.tsx:254`
le `a.velocidade`), a do personagem nao. Toda ficha de PF2e mostra Velocidade
no topo, ao lado de CA e Percepcao.

O dado esta todo la:

| fonte | quantidade |
|---|---:|
| ancestria com `speed: {land: N}` | **50 de 50** |
| feat com `speed: {tipo, valor}` | 112 |
| `flat_modifier` de velocidade, incondicional | **32** |
| `flat_modifier` de velocidade, condicional | 30 |
| armadura com `speed_penalty` | **109 de 216** |

E os 18 `land-speed` que a fatia anterior contou como "selector nao modelado"
sao exatamente estes.

## As formas que a base usa

Duas, e elas nao sao intercambiaveis:

- **`{"speed": {"land": 25}}`** -- a ancestria DEFINE a velocidade base.
- **`{"speed": {"tipo": "fly", "valor": 25}}`** -- o feat CONCEDE um modo novo,
  ou define o valor daquele modo (112 feats, 7 familiar-ability).

Mais `flat_modifier` com selector `land-speed`, `swim-speed`, `fly-speed`,
`climb-speed`, `all-speeds` e `speed` -- este ultimo sinonimo de `land-speed`.

## A penalidade de armadura, que e regra e nao subtracao

109 armaduras tem `speed_penalty` (-5 ou -10) e `strength`. O RAW:

> If you meet the armor's Strength requirement, reduce the Speed penalty by 5
> (to a minimum of 0).

Ignorar a segunda metade poria um Guerreiro de FOR 18 em cota de malha 5 pes
mais lento do que ele e. A regra entra inteira ou nao entra.

## As decisoes

1. **`visao.velocidade` e um dict por modo** -- `{"land": 25, "fly": 30}` --,
   mais `velocidade_detalhe` com as parcelas nomeadas, no mesmo desenho do `ac`.

2. **Ordem de composicao**: base da ancestria -> modo concedido por feat (o
   MAIOR vence, nao soma: dois feats que dao "fly 25" e "fly 30" dao 30) ->
   bonus incondicional (com a regra de tipo, igual aos outros) -> penalidade de
   armadura, com a reducao por Forca.

3. **`all-speeds` aplica em todo modo existente**, e nao cria modo novo. Criar
   modo a partir de bonus daria voo a quem nao voa.

4. **`speed` (sem sufixo) e sinonimo de `land-speed`** -- sao 11 ocorrencias e
   e o que o Foundry usa quando so ha um modo.

5. **Condicional continua fora**, como no resto: 30 dos 62. E velocidade que
   depende de acao ou estado que a ficha nao tem.

6. **Sem ancestria escolhida, `land` sai 25** -- o valor medio das 50, e o que
   o PF2e usa como padrao. Com aviso, nao em silencio.

## O que esta spec NAO resolve, e declara

- **Os 30 modificadores condicionais.**
- **Penalidade por carga (Bulk).** O motor nao modela carga (item 79j).
- **Velocidade do familiar e do eidolon.** Elas vem do modelo de ator, que ainda
  nao existe para os dois (item 43).

## Como se prova que funciona

1. Um humano sem armadura sai com `velocidade: {"land": 25}`.
2. Um anao sai com 20; um elfo, com 30 -- vem da ancestria, nao de um default.
3. Com cota de malha (`speed_penalty: -10`, `strength: 16`) e FOR 14, sai 15.
4. Com a mesma armadura e FOR 16, sai 20 -- a reducao de 5 por atender o
   requisito de Forca.
5. Um feat que concede `fly 25` cria o modo `fly` na ficha.
6. `all-speeds +5` soma nos modos que existem e NAO cria modo novo.
7. Dois bonus de +5 de status na mesma velocidade dao +5, nao +10.
8. `velocidade_detalhe` nomeia cada parcela.
9. As oito valem identicas no porte TypeScript.
10. Quatro camadas verdes; fixtures regenerados e o diff LIDO.
