---
spec: grau-legado-nao-fundido
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 79
---

# Spec -- o Remaster renomeou o item, e o grau maior ficou com o nome antigo

## O problema

O Remaster renomeou `Cloak of Elvenkind` para `Cloak of Illusions`, e a fusao
fez o trabalho dela: `wb:equipment/cloak-of-illusions` existe, nivel 7, com
`aliases: ["Cloak of Elvenkind"]`.

Mas o GRAU MAIOR nao foi junto. A base tem os dois:

| id | nivel |
|---|---:|
| `wb:equipment/cloak-of-elvenkind-greater` | 12 |
| `wb:equipment/cloak-of-illusions-greater` | 12 |

Mesmo item, duas vezes, e quem procurar pelo nome novo nao acha o antigo nem
vice-versa no grau maior.

## A causa

`fundir_renomeados.py` usa `remaster_id`/`legacy_id` do AoN. O AoN declara o par
no doc BASE (`equipment-424` -> `equipment-3069`) e **nao declara nos docs de
grau** (`equipment-424-514`). Sem par declarado, a fusao nao tem o que fundir --
e ela esta certa em nao inventar par.

## O tamanho, medido

Variantes de grau cujo nome-base e alias de outro registro: **10**. Destas, o
canonico tem o grau correspondente, no MESMO nivel, em **8**:

| legado | nivel | canonico |
|---|---:|---|
| `cloak-of-elvenkind-greater` | 12 | `cloak-of-illusions-greater` |
| `goggles-of-night-greater` | 11 | `obsidian-goggles-greater` |
| `goggles-of-night-major` | 18 | `obsidian-goggles-major` |
| `hat-of-disguise-greater` | 7 | `masquerade-scarf-greater` |
| `judgment-thurible-greater` | 17 | `judgement-thurible-greater` |
| `judgment-thurible-major` | 20 | `judgement-thurible-major` |
| `wyrm-claw-greater` | 15 | `wyrm-spindle-greater` |
| `wyrm-claw-major` | 19 | `wyrm-spindle-major` |

As 2 restantes sao `vigilant-eye-greater/major`, que casaram com
`wb:spell/rune-of-observation` -- alias de KIND DIFERENTE, e portanto ruido da
medicao, nao par. Ficam de fora.

## As decisoes

1. **O grau legado vira alias do canonico**, e o registro sai -- exatamente o
   que a fusao faz com o grau base. Quem digitar "Cloak of Elvenkind (Greater)"
   acha `Cloak of Illusions (Greater)`.
2. **So funde com as tres condicoes juntas**: o nome-base do legado e alias do
   canonico; o canonico tem o mesmo sufixo de grau; e os dois estao no MESMO
   nivel. Nivel diferente veta -- e o mesmo criterio de "divergencia estrutural
   veta a fusao" que `fundir_renomeados.py` ja aplica em 392 pares.
3. **Kind diferente veta.** O par tem de ser equipamento com equipamento; foi o
   que descartou `vigilant-eye`.

## O que esta spec NAO resolve, e declara

- **`vigilant-eye-greater/major`**: o nome-base casa com o alias de uma MAGIA.
  Ou e homonimo, ou e um par que ninguem declarou. Nao ha o que fundir sem
  arbitrar, e fica contado no relatorio.
- **Graus cujo canonico NAO tem o grau correspondente.** Nenhum caso hoje, mas
  se aparecer, o legado e o unico portador daquele grau e remove-lo perderia
  conteudo.

## Como se prova que funciona

1. `wb:equipment/cloak-of-elvenkind-greater` deixa de existir e
   `wb:equipment/cloak-of-illusions-greater` responde
   `aliases: ["Cloak of Elvenkind (Greater)"]`.
2. `Base.resolver("wb:equipment/cloak-of-elvenkind-greater")` devolve o
   canonico.
3. Os 8 somem; os 2 de `vigilant-eye` ficam, com o motivo no relatorio.
4. Nenhuma referencia quebra -- portao 3 em zero.
5. Nenhum nivel muda de valor: a condicao de fusao exige nivel igual.
6. Quatro camadas verdes.
