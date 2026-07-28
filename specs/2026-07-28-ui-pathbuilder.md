# Spec -- UI no padrao Pathbuilder

Status: aprovada por instrucao direta do Igor em 2026-07-28 ("disseca o maximo
que tu puder e faz o mais semelhante a isso se possivel").

Deriva da dissecacao do Pathbuilder 2e Web v108 feita no mesmo dia, registrada em
`docs/referencia-pathbuilder/` (sistema de design, arquitetura de UI, abas da
ficha e 28 capturas de tela do app ao vivo).

## Por que

O app ja tinha a arquitetura certa -- duas colunas, slot generico, picker
master-detail -- mas com pele propria: paleta azul-acinzentada, raio de 6px,
fonte de sistema, botoes preenchidos. O Pathbuilder e o app que o Igor usa de
fato na mesa, e a familiaridade de relance vale mais que originalidade visual
num construtor que se usa com 20 niveis abertos.

Escopo: **pele e shell**. O motor, o documento e as 22 regras nao mudam.

## Nao copiar

- Nenhum asset do Pathbuilder (PNG de icone, arte de fundo, favicon). Icone e
  desenho proprio em SVG inline.
- Nenhum bloco de CSS ou JS literal. O que se replica e o **sistema**: valores de
  cor, escala, forma e disposicao -- nao o arquivo.
- Nada de Stripe/PayPal/login/GM Mode/dice tray. Fora do escopo do projeto.

## Sistema de design

### Cor (tema escuro, unico por ora)

| Papel | Valor | Onde |
|---|---|---|
| Fundo de pagina | `#171a1e` | `body`, area de abas, fundo do modal |
| Fundo de card | `#222831` | `.bloco`, sidenav, secoes da ficha |
| Painel secundario | `#2a323d` | `select`, campo de entrada, faixa de barra |
| Borda neutra | `#2d4059` | divisoria, contorno de card |
| Texto primario | `#ffffff` | valor, numero, nome |
| Texto secundario | `#a1a1a1` | rotulo, origem, fonte da regra |
| **Accent** | **`#ff5722`** | aba ativa, cabecalho de nivel, item selecionado, borda inferior da top bar |
| Vazio / pendente | `#d9695f` | "Nao escolhido" |

Regra de uso do accent: ele **nunca preenche fundo**. Marca por cor de texto,
por borda ou por sublinhado. Preenchimento laranja so no badge de nivel em
destaque do picker.

### Tipografia

- Fonte unica: **Inter**, servida do proprio `public/` (o app e offline; nao
  pode depender de `rsms.me`). Fallback `system-ui, sans-serif`.
- Base **14px**; cai para 12px abaixo de 1400px de largura -- encolhe, nunca cresce.
- Titulo de dialogo 21px/700. Rotulo pequeno 12,6px. Rotulo de slot 11px.
- **Sem caixa alta e sem letter-spacing.** O Pathbuilder nao usa em lugar nenhum,
  e a versao atual do Waybuilder usa em rotulo de slot e cabecalho de nivel --
  sai.

### Forma

- Raio: **10px** em card, 8px em painel menor e botao de modal, 5px em botao de
  filtro, **0** em chip de trait.
- Espacamento na malha de 7px: `padding: 7px 14px`, `margin: 0 7px 7px`.
- Botao e **outline-only**: borda 1px, fundo transparente. Hover troca a cor da
  borda para o accent. Nao existe botao primario preenchido.
- Profundidade por `filter: drop-shadow(...)`, nao `box-shadow`.

## Shell

```
top-bar (44px, border-bottom 2px accent)
  hamburguer/titulo | nome do personagem - Classe Nivel

main-container  (flex)
├── coluna esquerda  371px fixa, scroll proprio
│     card de identidade   (Ancestralidade / Heranca / Background)
│     build-section por nivel
└── coluna direita   resto
      linha 0:  section-top (identidade + atributos) | section-conditions
      linha 0:  section-defenses (CA + HP + saves)
      linha 2:  coluna de pericias 194px | area de abas
```

Larguras vem medidas do app real em viewport de 1600px. Abaixo de 1100px as
colunas empilham.

## Coluna esquerda -- a construcao

**Card de identidade** (topo, fixo): tres linhas `ancestralidade`, `heranca`,
`background`. Cada linha e `icone 40x43 | rotulo pequeno cinza / valor`.

**Um card por nivel**, do 1 ate o alvo:
- Cabecalho centralizado `Nivel N` em accent, 14px.
- **Botao-cog** para escolha agregada (boost de atributo, treino de pericia):
  quadrado ~88x69 com engrenagem de 48px, **numero do que falta sobreposto ao
  centro** e rotulo minusculo embaixo. Quando zera, o botao apaga.
- **Linha de slot**: `icone | rotulo cinza / valor`. Vazio e `Nao escolhido` em
  vermelho. E o que faz o olho achar o buraco sem ler.
- **Concedido** vem como `listview-item`: linha simples com o nome e, quando
  houver, o icone de custo de acao. Nao e botao -- nao e escolha.
- Nivel acima do alcancado aparece esmaecido, com o rotulo `nao alcancado`.

## Coluna direita -- a ficha

**section-top**: `Nivel | XP | Nome` como campos-botao, depois `SIZE`, `SPEED` e
os seis atributos como `rotulo cinza / modificador`.

**section-defenses**: CA num escudo desenhado a esquerda (numero grande dentro),
e a direita a barra de HP, a barra de escudo e os tres saves em linha
`rank | total | nome`.

A barra de vida empilha faixa, preenchimento e texto em **grid** (`grid-area`
unica para os tres), nao em `position: absolute`.

**Coluna de pericias** (194px): Pontos de Heroi, CD de classe, Percepcao e
Iniciativa em cards separados, depois a lista de pericias. Cada linha e
`rank | total | nome`. O rank e uma pastilha de uma letra.

**Area de abas**: barra de abas em texto puro, ativa em accent com sublinhado
accent de 2px. Abas atuais do Waybuilder ficam (`Pericias`, `Ataques`, `Feats`,
`Concedido`, `Sinais`) -- as do Pathbuilder que dependem de dado que o projeto
ainda nao tem (Gear, Spells, Pets) nao entram agora.

## Picker

Um so componente, como hoje. Muda a forma:

- Modal de **1250x800 fixo**, fundo `#171a1e`, overlay `rgba(0,0,0,.6)`.
- **Filtros viram abas** no topo, em texto, ativa em accent com sublinhado.
  Botao de filtro fino (funil) alinhado a direita, 31x31, raio 5px.
- Corpo master-detail: lista a esquerda (~340px), detalhe a direita.
- **Linha da lista**: nome a esquerda, icone de custo de acao logo apos o nome,
  **badge de nivel a direita** -- retangulo pequeno, fundo `#2a323d`.
- **Inelegivel nao some**: aparece em cinza, na mesma lista, depois dos
  elegiveis, com o badge de nivel indicando por que. E o principio zero do
  projeto, e o Pathbuilder faz igual.
- **Detalhe**: nome + icone de acao, badge de nivel a direita, chips de trait
  (retangulares, sem raio), a prosa inteira, e a fonte em italico cinza.
- Rodape: `Aceitar | Cancelar | Limpar`, outline, a esquerda.

## Fora desta spec

Dice tray, multiplos personagens abertos, modo Play, condicoes, PDF, GM mode,
IndexedDB. Ficam registrados em `docs/referencia-pathbuilder/ui-arquitetura.md`
como material para decidir depois.

## Como verificar

1. `npm run build` e `npx vitest run` limpos (77 testes).
2. Captura da tela do Waybuilder ao lado de
   `docs/referencia-pathbuilder/capturas/05-builder-limpo.png`: mesma disposicao
   de blocos, mesma paleta, mesma densidade.
3. Nenhum asset do Pathbuilder no repo.
