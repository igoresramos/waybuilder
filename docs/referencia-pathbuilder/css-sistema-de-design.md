# Pathbuilder 2e — Sistema de Design (garimpado dos CSS)

Fonte: arquivos CSS baixados do app web do Pathbuilder 2e, garimpados em 2026-07-28.

Arquivos analisados:
- `pathbuilder-min.css` — tema **dark padrao** ("default"), minificado
- `pathbuilder-lm-minv2.css` — tema **light mode**, minificado
- `pathbuilder-starbuilder-dmv1.css` — tema **dark alternativo "Starbuilder"** (reskin gold/grafite), nao minificado
- `global.css` — CSS de um form de pagamento Stripe (nao faz parte da UI do Pathbuilder, irrelevante pra este garimpo, ignorado abaixo)
- `toggle.css` — componente de toggle switch (usa cores do tema default)
- `ldsring.css` — componente de spinner/loading ring (usa cores do tema default)

O app tem **3 temas** coexistindo via classes/seletores (`:root`, `:root.light`, `:root.starbuilderdark`), todos reaproveitando o mesmo HTML/classes — so trocam variaveis de cor. Isso e o padrao mais util pro Waybuilder: layout unico, paleta trocavel.

---

## 1. Paleta

Nao ha custom properties (`--var`) em nenhum arquivo — cores sao hardcoded por seletor em cada tema. Tabela por funcao:

### Tema Dark padrao (`pathbuilder-min.css`) — o "canonico"

| Funcao | Cor | Onde aparece |
|---|---|---|
| Fundo de pagina | `#171a1e` | `html,body`, `.tabbed-area`, `.modal-content` |
| Fundo de card/painel principal | `#222831` | `.rounded-rectangle`, `.sidenav`, `.content-listview`, `.dice-tray` |
| Fundo de painel secundario/input | `#2a323d` | `.layout-tabbed-armor`, `.edittext-dark`, `.div-spell-level` |
| Borda / elemento neutro | `#2d4059` | `.div-button` (borda), `.item-level-box`, `.trait-common`, scrollbar thumb |
| Texto primario | `white` | corpo geral |
| Texto secundario/muted | `#a1a1a1` / `#a8a8a8` | `.weapon-span`, `.abilityTotal`, `.copyright` |
| **Accent (destaque)** | `#ff5722` (laranja) | bordas de tab ativa, hover, links, `.subtitle`, HP bar verde(!) |
| Sucesso | `#78f678` | `.green-text` |
| Erro/aviso | `#ec5f67` | `.warning-text` |
| Neutro apagado | `#5f6671` | `.red-text` (nome engana, e cinza-azulado) |
| Raridade item — uncommon | `#985420` | `.item-uncommon` |
| Raridade item — rare | `#151a4b` | `.item-rare` |
| Raridade item — unique | `purple` | `.item-unique` |
| Raridade item — custom | `#702963` | `.item-custom` |
| Raridade item — third-party | `#315e24` | `.item-third` |

### Tema Light (`pathbuilder-lm-minv2.css`)

| Funcao | Cor | Onde aparece |
|---|---|---|
| Fundo de pagina | imagem `parchment.jpg` (pergaminho) | `html,body` |
| Fundo de card | `#f9f7ec` (creme) | `.rounded-rectangle`, `.sidenav`, `.layout-item` |
| **Accent (destaque)** | `#500000` (vinho/maroon) | tabs, headers, bordas, links — substitui o laranja 1:1 |
| Texto primario | `#000` | — |
| Texto secundario | `#606060` / `#303030` | `.weapon-span`, `.listview-title` |
| Transparente | `#fff0` (shorthand p/ alpha 0) | fundos "invisiveis" sobre o pergaminho |

### Tema Dark "Starbuilder" (`pathbuilder-starbuilder-dmv1.css`) — reskin alternativo

Comentario no topo do proprio arquivo documenta a paleta:
```
starbuilder_gold = #ffb903 highlight
starbuilder_grey = #363636 eg buttons
starbuilder_background = #464646 eg rounded rectangles
page_background = #1d1a1a
dialog_background = #2a2a2a
```
Confirma o padrao: fundo de pagina mais escuro que o fundo de card, e um unico accent que colore tabs/bordas/links/hover.

### Cores de estado compartilhadas entre os 3 temas (praticamente fixas)

| Estado | Cor |
|---|---|
| HP/vida baixa (progress-bar-red) | `#c54546` |
| HP/vida alta (progress-bar-green) | `#539a5e` |
| Stamina/mana | `#0b7db3` |
| Dano fogo | `#e0502b` |
| Dano frio | `#53e8ec` |
| Dano eletrico | `#6859dd` |
| Dano acido | `#80d146` |
| Dano precisao | `#d7d948` |

Nota: no tema dark padrao, `.progress-bar-green` usa `#ff5722` (o accent laranja, nao um verde de fato) — inconsistencia do proprio Pathbuilder, so o light/starbuilder usam verde real (`#539a5e`).

---

## 2. Tipografia

| Aspecto | Valor |
|---|---|
| `font-family` | `'Inter', sans-serif`, com fallback para `'Inter var'` via `@supports(font-variation-settings:normal)` — unica fonte usada na UI |
| Tamanho base | `14px` (desktop) → `12px` em `@media (max-width:1400px)` — **escala pra baixo** em telas menores pra caber mais dado, nao pra cima |
| Escala (em `em`, relativa aos 14px base) | `.7em`/`.8em`/`.9em` (labels pequenos, detalhes) · `1em` (padrao) · `1.2em`/`1.3em` (subtitulos, tabs) · `1.5em` (dialog title) · `1.8em`/`2em` (AC, titulo de menu) |
| `font-weight` | so `normal`, `600` (`.label-header`) e `bold` (`.dialog-title`, `.ac-text`, `.abilityMod`, `.cogText`) — sem escala de pesos, binario |
| `text-transform` | **nao usado em lugar nenhum** dos 3 arquivos de tema — rotulos ficam em caixa normal, nao caixa alta |
| `letter-spacing` | **nao usado** — nenhuma ocorrencia |

---

## 3. Espacamento e forma

| Aspecto | Padrao |
|---|---|
| Padding/margin | quase tudo em `em` (`.2em`/`.3em`/`.5em`/`1em`), raramente `px` — escala junto com o font-size responsivo |
| `border-radius` — cards grandes | `10px` (`.rounded-rectangle`, `.dm-skill_background`) |
| `border-radius` — cards/paineis menores | `8px` (`.layout-tabbed-line`, `.layout-item`, `.div-spell-level`) |
| `border-radius` — botoes | `4px`–`5px` (`.div-button`, `.spell-button-row`) ou `8px` (`.modal-button`) |
| `border-radius` — badges/traits | **0** — `.trait`, `.item-level-box` sao retangulos de canto reto, nao pilulas |
| `border-radius` — circular | `50%` (`.item-nolevel` dot, spinner do ldsring) |
| Espessura de borda | `1px` (tooltip, modal-button) ou `2px` (div-button, selected-item, tabs) — nunca mais que 2px |
| `box-shadow` | quase ausente — so `inset 0 0 1px .5px white` (hover de modal-button) e `0 0 0 1px black` (moldura do modal-content). Em vez de shadow, botoes usam **`filter: drop-shadow(...)`** pra dar efeito de profundidade (`.div-button`, `.new-load-buttons`) — tecnica pouco comum, vale considerar |

---

## 4. Componentes (nomes de classe reais)

| Componente | Classe | Estilo |
|---|---|---|
| **Abas (tabs)** | `.tabbed-area-menu` + `.section-menu` / `.section-menu-selected` | Faixa com `border-bottom: 2px solid <accent>` na area toda; cada item e so texto cinza (`#a1a1a1`) que vira cor accent no hover/selecionado — **sem** fundo de pilula nem sublinhado individual por aba no tema padrao (o Starbuilder ja adiciona sublinhado por aba: `.section-menu-selected-sb{border-bottom:2px solid #ffb903}`) |
| **Card/painel** | `.rounded-rectangle`, `.rounded-bottom-only`, `.layout-tabbed-line`, `.layout-item` | `padding:.5em 1em`, `border-radius:10px` (ou 8px pros menores), fundo solido da cor de card do tema, sem borda visivel |
| **Botao** | `.div-button` / `.div-button-simple` | **Outline style**: borda 2px cor neutra (`#2d4059`), fundo transparente/escuro, `border-radius:4px`. Hover troca a cor da borda pra accent (nao preenche fundo). `.div-button-disabled` = borda cinza + texto cinza. Nao ha "botao primario preenchido" no sistema |
| **Botao de modal** | `.modal-button` | Outline branco, `border-radius:8px`, hover = `inset box-shadow` sutil de brilho |
| **Linha de lista** | `.listview-item` / `.listview-title` / `.listview-title-selected` / `.selected-item` | Selecionado = `border:2px solid <accent>` no container + texto na cor accent (nao fundo preenchido). Hover so muda cor do texto |
| **Campo de input** | `.edittext-dark`, `.edittext-custom`, `.spinner-dark` | Sem borda (`border:0`), fundo do painel secundario (`#2a323d`), `outline:none` no focus — visual "sunken", contraste vem so do fundo, nao de contorno |
| **Modal/dialog** | `.modal` (overlay `rgba(0,0,0,.6)`) + `.modal-content` | Fundo = cor de pagina (nao de card), **sem border-radius** (cantos retos), moldura fina `box-shadow:0 0 0 1px black`, largura `80vw` max `1250px` |
| **Badge/pill (raridade de item)** | `.item-level-box`, `.item-uncommon/rare/unique/custom/third` | Caixa pequena de canto reto (sem radius), cor de fundo por raridade, numero do nivel dentro |
| **Badge de trait** | `.trait` + `.trait-common/rare/uncommon/unique/size/alignment` | Chip inline `padding:2px 5px`, **canto reto** (nao e pill arredondado), cor de fundo por categoria |
| **Barra de HP/recurso** | `.progress-bar-container` + `.progress-bar` + `.progress-bar-text` | Track cinza, fill colorido (`.progress-bar-red/green/stamina`), ambos empilhados via **CSS grid** (`grid-column:1;grid-row:1` nos dois) em vez de `position:absolute` — texto sobreposto ao fill |
| **Seletor/picker** | `.select-box`, `.button-filter` / `.button-filter-selected` | Filtro = quadrado 1.5em com borda que vira accent quando selecionado |
| **Tooltip** | `.tooltip .tooltiptext` / `.tooltiptextCrit` | Fundo = cor de card, `border:1px solid <accent>`, `border-radius:6px`, seta via `::after` (`border-color` trick), fade por `opacity` + `visibility` |
| **Toggle switch** | `.switch` / `.slider` (toggle.css) | Pill 70x24px, thumb branco circular, trilho off = azul-marinho `#2d4059`, on = accent do tema |
| **Loading ring** | `.lds-ring` (ldsring.css) | Container quadrado arredondado (`10px`) com fundo de card e borda 1px accent; anel giratorio usa o truque `border-color: accent transparent transparent transparent` |
| **Sidebar/drawer** | `.sidenav` | `position:fixed`, largura anima de `0` pra aberta via `transition:.3s`, fundo = cor de card |

---

## 5. Layout

- Shell de app em **duas colunas via flex**, sem grid framework: `#container-row-0{display:flex;flex-direction:row}`.
- `.main-column-left`: largura fixa `26em` (`24em` em telas ≤1400px), colapsavel pra `0` via `.main-column-left-hidden` (drawer retratil).
- `.main-column-right`: `flex:1`, ocupa o resto.
- Uso extensivo de `inline-block` e `flex` misturados; `display:grid` aparece so em pontos pontuais e tecnicos (`.progress-bar-container`/`.ac-holder` pra empilhar camadas, `.grid-container` pra distribuir colunas iguais via `grid-auto-flow:column`).
- **Media queries — so 4 no total, nenhuma "mobile-first":**
  1. `max-width:1400px` → reduz `font-size` pra 12px, encolhe `.main-column-left` pra 24em, esconde `.div-spell-extra`
  2. `-webkit-min-device-pixel-ratio:1.2` → mesmo ajuste (telas de alta densidade)
  3. `max-height:450px` → ajusta padding/font-size da sidenav
  4. `max-width:1300px` → empilha `.pet-column-holder` (colunas de "familiares") de `flex` pra `display:block`
  
  **Nao ha breakpoint classico de mobile (600-768px) tocando o layout principal** — o app e desenhado como ferramenta densa de desktop; a resposta a telas menores e so "encolhe fonte e colunas fixas", nao reflow real de layout.

---

## Achados mais uteis pro Waybuilder

1. **Paleta e trocavel por variavel unica de accent** — os 3 temas do Pathbuilder sao o mesmo CSS com 1-2 cores substituidas (fundo de pagina, fundo de card, accent). Vale desenhar o design system do Waybuilder assim desde o inicio (CSS custom properties ou tokens do Tailwind), mesmo o Pathbuilder nao usando `--var` nativamente.
2. **Sem uppercase, sem letter-spacing** — contraria a suposicao comum de "ficha de RPG usa caixa alta em rotulo". Pathbuilder e todo caixa normal.
3. **Badges/traits sao quadrados, nao pilulas** — `border-radius:0` em `.trait`/`.item-level-box`, junto com botoes outline (sem preenchimento) e selecao por borda colorida (nao fundo preenchido) — e uma linguagem visual consistente de "contorno realca, fundo nao".
4. **Sem mobile real** — se o Waybuilder precisa funcionar bem em celular, isso e uma lacuna do Pathbuilder a corrigir, nao um padrao a copiar.
