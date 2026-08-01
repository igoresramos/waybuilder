---
spec: concessao-do-mestre
req: WB-074
project: waybuilder
version: 1
status: rascunho
created: 2026-08-01
todo: 117
---

# Spec -- o que o mestre da de graca

## O problema, medido

O mestre quer dar alguma coisa fora das regras: um feat extra, um bicho, um
item. Hoje, num Mago 2:

| o mestre quer | o que o motor faz |
|---|---|
| um feat **a mais** (2 escolhas para 1 slot de `class_feat`) | funciona -- os dois entram em `gastos`, a ficha deriva, e sai o sinal `2 escolha(s) para 1 slot(s) disponivel(is) em [2]` |
| um feat num slot inventado (`presente_do_mestre`) | **desaparece em silencio** -- nao entra em lugar nenhum, nao gera aviso |
| um companheiro avulso, sem feat que o conceda | **desaparece em silencio** -- `atores: []`, zero avisos |
| uma classe a mais | **ja funciona** -- e a houserule central do projeto |

Duas conclusoes. A primeira e boa: o caso do feat extra ja obedece ao principio
zero de `_higiene_de_slot` ("isto SINALIZA, nunca recusa"). A segunda e o
defeito: **o vocabulario de slot e fechado**, e o que ele nao conhece some sem
rastro -- o pior comportamento possivel para um construtor cujo principio 4 e
"nada e descartado".

```python
SLOT_PARA_CADENCIA = {
    "class_feat": "class", "skill_feat": "skill", "general_feat": "general",
    "ancestry_feat": "ancestry", "free_archetype": "free_archetype",
}
```

Nao existe caminho para "toma, um lobo": ator so nasce se um feat o conceder.

## O que esta spec adiciona

Um slot novo, `concessao`, que aceita **qualquer** `pega` e nao e confrontado
com slot nenhum -- porque nao gastou slot.

```json
{ "em": 3, "slot": "concessao", "pega": "wb:feat/reactive-shield",
  "motivo": "recompensa da sessao 12" }
```

`motivo` e livre e opcional. Ele existe porque a diferenca entre "excesso" e
"presente" nao esta no dado, esta na intencao -- e o unico jeito de o app nao
adivinhar e o mestre escrever.

### Roteamento por kind do alvo

O motor NAO ganha uma lista de kinds aceitos. Ele olha o `kind` do registro
apontado e roteia para o mesmo lugar que a concessao por feat ja usa:

| kind do alvo | vai para |
|---|---|
| `feat`, `class-feature`, `action` | `concedidos`, como se um feat o tivesse concedido |
| kinds de ator (`animal-companion`, `familiar`, `eidolon`, ...) | `atores`, mesma rota de `concessoes_de_ator` |
| `equipment`, `weapon`, `armor` | inventario |
| qualquer outro | `concedidos`, com o kind registrado |

Lista a mao ja errou tres vezes neste projeto. Os kinds de ator saem de onde
`derivar_concessao_de_ator.py` ja os declara, nao de um literal novo.

### O que a concessao NAO faz

- **Nao gasta slot.** `_higiene_de_slot` ignora `concessao` inteiramente. Um
  feat de presente nao pode fazer o jogador parecer que estourou o orcamento.
- **Nao pula o requisito.** O requisito continua sendo avaliado e MARCADO em
  `fora_do_requisito` -- principio 1: sugere e ordena, nunca bloqueia. Um Mago
  que ganhou `Reactive Shield` de presente ve o feat na ficha E ve que ele
  normalmente exigiria Fighter. Essa informacao e util para o mestre, nao ruido.
- **Nao inventa mecanica.** O `grants` do registro concedido e aplicado pela
  cadeia que ja existe (`_grants_em_cadeia`), com as mesmas guardas de
  profundidade.

## Onde encosta no codigo

Tres lugares, e os tres precisam concordar:

| arquivo | mudanca |
|---|---|
| `motor/motor.py` | ler `_escolhas("concessao")`, rotear por kind, marcar origem |
| `app/src/motor/personagem.ts` | o mesmo, identico -- o porte tem de derivar igual |
| `app/src/componentes/PainelDireito.tsx` | a aba **Concedido** ja existe e ja le `concedidos`; a concessao entra la com o `motivo` visivel |

A aba "Concedido" hoje filtra `c.nome !== c.por`. Concessao do mestre nao tem
`por` -- a origem e o `motivo`, ou "mestre" quando ele nao escreveu nada.

## O que esta spec NAO resolve

- **Item com runa / customizacao** entra como o registro que existe na base; a
  spec nao cria vocabulario para "espada +1 do mestre".
- **Retirar** uma concessao e editar o documento, nao ha operacao de "tomar de
  volta".
- **Classe a mais** nao entra aqui: ja funciona por `nivel_de_classe`.
- **Ator com estatistica customizada** (o lobo do mestre com HP diferente) fica
  fora: o ator sai derivado do registro, como hoje.

## Como se prova que funciona

1. Um Mago 2 com `{"slot": "concessao", "pega": "wb:feat/reactive-shield"}`
   tem o feat em `concedidos`, com origem legivel.
2. O mesmo Mago **nao** ganha aviso de estouro de slot -- `_higiene_de_slot`
   nao ve a concessao.
3. O mesmo Mago ganha `fora_do_requisito` dizendo que o feat exige Fighter.
4. Um personagem sem feat de companheiro, com
   `{"slot": "concessao", "pega": "wb:animal-companion/wolf"}`, tem um ator
   derivado na ficha.
5. Concessao de um registro com `grants` aplica a cadeia (teste: um feat que
   concede proficiencia muda a proficiencia).
6. Slot desconhecido (`presente_do_mestre`) **continua** nao existindo, mas
   agora **avisa** em vez de sumir -- fim do silencio.
7. Python e TS derivam a MESMA ficha para um documento com concessao.
8. As 20 fichas de exemplo (nenhuma tem concessao) derivam identicas ao de
   antes -- a mudanca e aditiva.
