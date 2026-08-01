---
spec: recorte-temporal-do-has
req: WB-016
project: waybuilder
version: 1
status: implementada
created: 2026-07-29
altera: [WB-003]
todo: 65
---

# Spec -- o `has` precisa saber QUANDO

## O problema

`_termo_has` responde "o personagem tem X?" olhando o documento INTEIRO, sem
olhar em que nivel cada coisa foi pega. Entao uma ficha com a ordem ILEGAL passa
limpa.

Reproduzido em 2026-07-29, num Guerreiro 12:

| ficha | `fora_do_requisito` |
|---|---|
| `Dueling Parry` no nivel 2, `Dueling Dance` no 12 -- **legal** | `[]` |
| `Dueling Parry` no nivel 12, `Dueling Dance` no 2 -- **ilegal** | `[]` |

`Dueling Dance` exige `Dueling Parry`. Na segunda ficha o jogador pegou a Dance
no nivel 2, dez niveis ANTES de ter o pre-requisito -- e o motor nao viu, porque
no fim das contas o personagem "tem" as duas.

Isso importa mais do que parece: a ficha e um historico, nao uma foto. O
construtor existe para dizer o que era legal escolher em cada nivel, e sem o
recorte temporal ele so sabe dizer o que e legal ter no fim.

## A decisao

**Contexto temporal na avaliacao**, no mesmo desenho de `self._avaliando` -- que
ja existe para o requisito circular (um feat nao pode satisfazer o proprio
pre-requisito).

- `self._avaliando_em` guarda o nivel em que a escolha sob analise foi feita.
- `_checar_requisitos` passa a preencher os dois campos: o id (que ja preenchia)
  e agora o nivel da escolha.
- `_termo_has` desconsidera escolha com `em` MAIOR que `_avaliando_em`.
- Sem contexto (`_avaliando_em is None`), nada muda -- o termo continua olhando
  o documento inteiro, que e o certo para perguntas fora de uma escolha
  especifica.

`em: "criacao"` conta sempre: ancestria, background e heranca antecedem todo
nivel.

## O que esta spec NAO cobre, e declara

O recorte vale para as **escolhas**. Nao vale para:

- **`self.features`** -- class-features carregam `nivel_de_classe`, nao nivel de
  PERSONAGEM. Num multiclasse os dois divergem, e converter um no outro exige
  inverter `classe_do_nivel` com cuidado. E defeito da mesma familia (um feat
  pego no nivel 2 nao deveria ser satisfeito por uma feature ganha no 9), mas
  merece medicao propria antes de mexer.
- **`self.concedidos`** -- o que a cadeia de grants concede herda o nivel da
  raiz, que ja e rastreada por `concedido_por`; usar isso exige o mesmo mapa
  acima.

Declarado aqui para nao virar "resolvido" quando esta pela metade.

## Como se prova que funciona

1. `Dueling Parry` no 2 e `Dueling Dance` no 12 -- continua limpo.
2. `Dueling Parry` no 12 e `Dueling Dance` no 2 -- passa a aparecer em
   `fora_do_requisito`, com o motivo "exige ter Dueling Parry".
3. Uma ficha sem ordem invertida nenhuma nao ganha aviso novo -- o recorte nao
   pode inventar falso positivo nas 22 fichas de exemplo.
4. `avaliar()` chamado de fora (sem contexto) responde como antes.
5. As 22 fichas derivam identicas nas duas linguagens.
