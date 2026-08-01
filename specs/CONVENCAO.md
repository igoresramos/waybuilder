# Convencao de spec

O frontmatter de uma spec e um **contrato**, e `pipeline/verificar_specs.py`
cobra. Contrato sem portao vira decoracao -- foi a licao do portao 3, que varria
`requires` e nunca `subclasses[].opcoes`, justamente o campo que o passo 7c
existe para consertar.

```yaml
---
spec: fusao-de-duplicata-de-nome    # o assunto, em kebab-case
req: WB-075                         # identificador proprio, estavel, unico
project: waybuilder
version: 1
status: implementada
created: 2026-08-01
prova: exemplar-root-epithet        # so quando a deteccao automatica erra
altera: [WB-002]                    # contratos grandes que esta spec muda
atualizada_em: 2026-08-01           # quando o texto mudou depois de aprovado
issue: 1                            # issue do GitHub, quando houver
todo: 84                            # legado -- o TODO.md vive no Tartarus
---
```

## `req` -- por que ele existe

Ate 2026-08-01 a unica chave de rastreio era `todo: NN`, apontando para o
`TODO.md`, que **saiu do repo** no commit `58658db`. Setenta e cinco ponteiros
para um arquivo que nao viaja junto: sem ele nao dava para saber se `todo: 84`
em quatro specs diferentes era a mesma tarefa ou renumeracao.

`req` mora dentro da spec e vai junto com ela. Numerado em ordem de `created`,
`WB-001` a `WB-075`. **Nao renumere:** o id e citado por outras specs no campo
`altera` e pelas tabelas de referencia cruzada.

`todo` fica, como ponteiro secundario para quem tem o Tartarus a mao. Spec nova
usa **`issue: N`**, apontando para o board do GitHub -- convencao que apareceu
sozinha em `persistencia-e-identidade-de-build` (2026-08-01) e que e melhor que
as duas anteriores: o alvo e publico, versionado fora do repo e nao se perde numa
mudanca de pasta. `req` continua sendo a identidade da SPEC; `issue` e o
ponteiro para o TRABALHO. Sao coisas diferentes e convivem.

> Ideia emprestada do Fusion (`REQ-<PREFIXO>-NNN`, 1.383 deles). O que **nao**
> foi copiado de la e a marca `[MVP]`/`[V2]`: o Waybuilder nao tem essa divisao,
> e inventar uma taxonomia que o projeto nao usa e fabricar disputa que o dado
> nao tem -- o mesmo erro que a spec da base ja nomeou a proposito de `grants`.

## `status` -- quatro valores, e um deles se prova

| valor | significado |
|---|---|
| `rascunho` | ainda em discussao. Declaracao humana -- nenhum script promove |
| `aprovada` | decidida, ainda nao construida |
| `implementada` | esta no ar, **e o portao confere** |
| `substituida` | vencida por outra spec; exige `substituida_por: WB-NNN` |

O problema que isto resolve: 73 das 75 specs diziam `aprovada`, incluindo as que
estavam no ar havia uma semana e as que eram so intencao. Uma delas
(`slots-e-candidatos`) precisou de um paragrafo no CORPO para avisar que o
proprio campo estava errado.

### O que conta como prova

`status: implementada` so passa no portao com pelo menos uma destas:

1. **script proprio ligado ao `build.sh`** -- existe no disco E aparece no build;
2. **verificacao de navegador** em `app/verificacao/*.mjs`;
3. **script nomeado a partir do assunto da spec** -- duas palavras em comum
   entre o slug e o nome do script, ambos no build;
4. **identificador com `_`** citado entre crases e presente no codigo
   (`grant_actor`, `_avaliando_em`, `_orcamento_de_pericia`);
5. **campo `prova:`** -- escape para spec de DADO, que nao produz script nem
   simbolo. O portao confere que o valor existe no codigo ou em
   `base/index.json`; declarar algo inexistente falha igual a nao declarar.

A regra foi calibrada duas vezes, e vale registrar as duas para nao voltarem:

> **Primeira versao: permissiva demais.** Aceitava qualquer palavra entre crases,
> e marcou **as 75 specs** como implementadas -- reintroduzindo exatamente o
> defeito que o campo existe para matar. `requires`, `trained` e `eidolon`
> casavam por serem vocabulario do jogo, nao por serem prova. Dai a exigencia de
> `_` no simbolo e a lista de arquivos genericos que nao contam
> (`motor.py`, `build.sh`, `doc.ts`...).
>
> **Segunda versao: um falso negativo.** `variante-por-subclasse` saiu
> `aprovada` porque a spec nao escreve o nome de `derivar_variante_por_subclasse.py`
> em lugar nenhum -- o script existe e roda no passo 7d3. Dai a prova 3.
> `nomear-o-balaio-por-tag` escapou das quatro e foi confirmada a mao (o eixo
> `exemplar-root-epithet` existe na base) -- dai a prova 5.

## `version` e `atualizada_em`

Spec editada depois de aprovada sobe `version` e ganha `atualizada_em`. A
convencao **nao foi decidida aqui** -- ela apareceu na `main` em 2026-08-01,
quando `slots-e-candidatos` virou v2 depois de descobrir que descrevia um motor
que nao existia havia 4 dias. Esta pagina so registra o que o projeto ja fez.

O portao nao cobra os dois campos: a maioria das specs nunca foi editada, e
exigir `atualizada_em` de quem nao mudou seria pedir ruido.

## `altera` -- a referencia nos dois sentidos

Spec pequena que muda um contrato grande declara qual:

```yaml
altera: [WB-002]      # schema-base
```

E o contrato grande **responde**, numa tabela ao fim do arquivo, entre
`<!-- specs-que-alteram:start -->` e `:end`. A tabela e **gerada**:

```bash
python3 pipeline/verificar_specs.py --tabelas
```

Nunca escrita a mao -- lista a mao ja errou tres vezes neste projeto (as classes
que dao class feat no nivel 1 foram 3 -> 6 -> 16). O portao falha se uma spec
declarar `altera: WB-002` e o `schema-base` nao a citar de volta.

O problema que isto resolve: a linguagem de `grants` ganhou cinco termos novos
(`grant_actor`, `grant_spellcasting`, `grant_item`, `grant_feat`, grant
condicional) em specs separadas, e o `schema-base` seguia mostrando a lista de
26/07. Quem entrava no projeto lia o contrato desatualizado e implementava
contra ele. Hoje sao **37 specs** alterando o `schema-base`, 5 as regras de
multiclasse e 2 o schema de personagem.

A tabela nao substitui atualizar o texto do contrato quando o termo novo importa
-- ela garante que da para **descobrir** que ele existe.

## Como rodar

```bash
python3 pipeline/verificar_specs.py             # portao: exit 1 se algo falhar
python3 pipeline/verificar_specs.py --listar    # estado spec a spec
python3 pipeline/verificar_specs.py --tabelas   # regenera a referencia cruzada
```

Esta ligado ao `./verificar.sh` como **mecanismo 8 de 8**, e roda em ~1 segundo.
Nao entra no `build.sh` porque nao e portao de dado -- ele nao olha a base, olha
as specs.

> Este paragrafo dizia, ate a revisao deste PR, que o portao "nao esta ligado a
> nada, porque o comando de teste do projeto nao existe". O `verificar.sh`
> nasceu na `main` no meio do caminho, e a divida virou uma linha de codigo.

## O que esta convencao NAO resolve

- **`version` so sobe quando alguem lembra.** O portao nao cobra, e a spec do
  app segue dizendo "atualizada em 28/07" com uma secao "estado em 29/07".
  Cobrar exigiria comparar o texto com a versao anterior no git -- da para
  fazer, nao esta feito.
- **A defasagem ja existente nos contratos grandes.** O `schema-base` fala em 8
  portoes (sao 11) e 22 kinds (sao 58); o `schema-personagem` lista 15 slots e
  faltam 4. A tabela de referencia cruzada torna a defasagem **descobrivel**,
  nao a conserta.
- **Nao ha indice das specs.** Decisao registrada: ficou fora do escopo.
