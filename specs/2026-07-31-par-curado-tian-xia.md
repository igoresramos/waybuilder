---
spec: par-curado-tian-xia
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 85
---

# Spec -- as duas armas Tian Xia nao faltavam; faltava o NOME

> Esta spec foi escrita depois do codigo, e o **portao 8** pegou -- pela
> segunda vez em 31/07, pelo mesmo motivo. O passo citava este arquivo e ele
> nao existia. A regra do projeto e spec primeiro; o portao existe porque a
> regra e violavel.

## A premissa do item 85 estava errada

Ele dizia: "Nine-Ring Sword e Wind and Fire Wheel (Tian Xia) nao tem fonte em
disco nenhuma -- precisa de dump novo do AoN ou entrada curada".

**Nao precisa de dump.** As duas estao no dump que ja existe, sob os nomes
chineses, e a nossa base ja tem os dois registros COMPLETOS:

| registro vazio (pf2etools) | registro completo (Foundry) | dano |
|---|---|---|
| `wb:weapon/nine-ring-sword` | `wb:weapon/jiu-huan-dao` | 1d8 S, martial, sword |
| `wb:weapon/wind-and-fire-wheel` | `wb:weapon/feng-huo-lun` | 1d4 S, advanced, knife |

O nome em ingles aparece so na PROSA do AoN ("Also known as wind and fire
wheels"), e por isso nenhuma busca por nome achava.

## Por que nenhum mecanismo existente os junta

- **`derivar_alias_legado.py`** le `legacy_id` do AoN, e o vinculo esta la
  (`weapon-623` -> `weapon-288`). Mas o AoN renomeou os **dois** lados: os dois
  registros se chamam "Jiu Huan Dao". A guarda `velho.lower() == novo.lower()`
  pula, **corretamente** -- nao ha renomeacao a registrar.
- **`colapsar_opcoes_irmas.py`** casa por NOME, e `Nine-Ring Sword` nao se
  parece com `Jiu Huan Dao`.

O nome antigo sobrevive so no **pf2etools**, que nao tem ponte de remaster
nenhuma. Nao ha regra derivavel: e par curado, e sao dois.

## O desenho, e por que `equivale_a` sozinho nao bastou

Primeira versao: alias no completo + `equivale_a` no vazio. **Nao resolveu a
ficha.** `resolver()` segue `aliases`, nao `equivale_a`, entao a arma equipada
pelo id antigo continuava saindo com dano `1` na aba de Ataques.

O que fecha e PREENCHER o que falta a partir do gemeo -- so campo ausente,
nunca sobrescrita, para nao apagar o que a fonte antiga trouxe de proprio
(`nine-ring-sword` carrega `disarm`, que o gemeo nao tem). Os tres mecanismos
convivem: alias para a busca, `equivale_a` para quem citar o id, e os campos
mecanicos para a ficha.

Apagar o registro vazio nao entra: o id ficaria inalcancavel, familia do item
97.

## O que esta spec NAO resolve, e declara

`wb:weapon/jiu-huan-dao-disarm` e uma TERCEIRA variante, com os mesmos numeros
e trait `disarm` em vez de `sweep`, vinda de `weapon-99` -- um AoN id sem
`remaster_id` nem `legacy_id`. Sao tres registros do AoN para a mesma arma
(99, 288, 623). Fica registrado, nao tocado: mexer nela e triagem de homonimo,
outra familia.

## Como se prova que funciona

1. Um Guerreiro 1 com `wb:weapon/nine-ring-sword` equipada le **1d8** na ficha;
   com `wind-and-fire-wheel`, **1d4**. Antes as duas liam `1`, sem dado.
2. Os registros completos ganham o nome antigo em `aliases`, entao buscar
   "Nine-Ring Sword" acha a arma.
3. Nenhum campo do registro vazio e sobrescrito -- `disarm` continua la.
4. Nenhuma outra arma muda.
5. 10 portoes, oraculo, paridade, navegador.
