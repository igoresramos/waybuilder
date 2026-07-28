# Pathbuilder 2e Web (Remastered 108b) — Arquitetura de Interface

Garimpado a partir de:
- `Pathbuilder2eWebRemastered108b.js` (3.8MB, bundle Kotlin/JS minificado — identificadores de funcao ilegiveis, mas strings de UI e nomes de classe/id preservados)
- `view-source_https___pathbuilder2e.com_app.html_v=108b.html` (shell HTML real, servido pelo app)
- `pathbuilder-min.css` (26KB, CSS principal do app — fonte mais rica de estrutura)
- `dicecode-min2.js` (three.js + rolador de dados fisico em canvas)
- `longpress.js` (biblioteca generica de long-press, 1000ms)

Nota tecnica: o bundle JS e Kotlin Multiplatform compilado (`kotlin`, sufixos `$_$` nos imports), entao nomes de funcao/variavel sao letras minificadas (`dI`, `RI`, `Su(...)`). Nao da para citar nomes de funcao "legiveis" — a evidencia usada abaixo e string literal (labels, ids de DOM, chaves de localStorage/IndexedDB, nomes de classe CSS), que sobrevivem a minificacao.

---

## 1. Telas / Abas

Layout de duas colunas fixas dentro de `#main-container`:

- **Coluna esquerda** (`#divBuild`, classe `main-column-left`, 26em fixo, colapsa para 24em em telas <1400px): a "construcao" do personagem.
  - `#divTopButtons`: barra de botoes de topo (Print, etc).
  - `#divBuildLevels`: lista dos niveis do personagem, um bloco por nivel — e aqui que aparecem as escolhas (feat, boost, skill increase) de cada nivel, em ordem.
- **Coluna direita** (`main-column-right`, flex): a "ficha" propriamente dita.
  - `#container-row-0` → `#container-row-0-col-0` (estatisticas: AC/HP/saves/percepcao, ver secao 4) + `#section-conditions` (condicoes ativas).
  - `#container-row-2` → `#container-section-skills` (lista de pericias, coluna fixa a esquerda) + `#tabbed-area` (abas com o resto da ficha).

Dentro de `#tabbed-area` (classe `.tabbed-area-menu`, itens `.section-menu` / `.section-menu-selected`, sublinhado laranja `#ff5722` no item ativo), as abas confirmadas por string literal no bundle: **Actions, Feats, Spellbook/Spells, Inventory (Gear), Companion/Animal Companion/Familiar, Details, Notes**. Cada aba e uma view separada renderizada dentro de `.tabbed-area-display` — nao ha SPA-router, e troca de painel via show/hide.

Barra superior (`.top-bar`, escondida ate carregar): hamburguer (`#menu`, classe `.hamburger`) abre o menu lateral; `#active-builds` mostra **abas de builds ativas** (`.active-build-section`, `.button-active-build`) — o app permite ter **varios personagens abertos simultaneamente em memoria**, trocando entre eles sem sair da tela, como abas de navegador.

Menu lateral (`#mySidenav`, slide-in, `.sidenav`) organizado em grupos (`.menu-group-header` + `.menu-group`):
- **Signin**: login/upgrade.
- **Character**: Convert to Remaster Rules, Character Options, New Character, Save Character, Open Character.
- **Connect**: Connect to GM, Launch GM Mode.
- **Export**: Character Sheet PDF, Stat Block PDF, Export JSON, Share Copy of Character.
- **Data**: Backup/Restore, Campaign Management, Feat Browser, Remaster Information.
- **Custom**: Custom Pack, Custom Ability Increases, Custom Feat Choice, Custom Skill Increases.
- **Help**: Help, Licenses, Patch Notes, Report Error.

## 2. Fluxo de construcao

A esquerda (`#divBuildLevels`) e organizada **por nivel**, nao por categoria. Cada nivel do personagem e um bloco expansivel que mostra so as escolhas daquele nivel (feat de classe, feat geral, boost de atributo, skill increase, etc., conforme a progressao da classe). Isso e a decisao de UX central do app: em vez de "monte tudo de uma vez" (ancestry -> background -> classe -> atributos -> feats -> pericias -> equipamento em telas separadas), o Pathbuilder trata o personagem como uma timeline de niveis, e cada escolha pendente aparece "encaixada" no nivel correto, incluindo retroativamente (nivel 1 tem ancestry/background/classe como "escolhas de nivel 1").

Cada escolha individual (feat, boost, skill training, etc.) dispara um picker modal cujo titulo e gerado dinamicamente como **"Select {NomeDaEscolha}"** (ex.: `"Select Ancestry Trait"`, `"Select Arcane School"`, `"Select Advanced Weapon Group"` — centenas de variantes encontradas no bundle, uma por tipo de escolha do jogo). Isso indica um sistema generico de "choice slot" reaproveitado para toda decisao de nivel, e nao uma tela dedicada por categoria.

Builds incompletos ficam navegaveis: da pra pular entre niveis e o app deve sinalizar (via cor/highlight, nao confirmado em detalhe) quais escolhas faltam.

## 3. Picker / Seletor

Confirmado via CSS que e um **modal com layout master-detail (lista + painel de detalhe)**, nao um dropdown simples:

- `.modal` / `.modal-content` (80vw, max 1250px, max-height 80vh) — dialog central com fundo escurecido (`.backdrop`, `rgba(0,0,0,0.6)`).
- `.modal-content-listview` variante fixa em 80vh especifica para pickers de lista.
- `.content-listview` = flex row de dois paineis:
  - `.div-listview-scroller` (24em fixo, scroll vertical) — lista de opcoes, itens `.listview-item` / `.listview-title` com `.listview-title-selected` e `.selected-item` (borda laranja) pro item escolhido.
  - `.div-listview-info` (flex:1, scroll vertical, padding 2em) — painel de detalhe com **texto completo da regra** da opcao selecionada (nao e so um tooltip curto).
- `.filter-controls` + `.button-filter` / `.button-filter-selected`: botoes de filtro toggle (icones, nao dropdown) acima da lista — usados no Feat Browser (`sidenav-feat-browser`) e nos pickers de feat/spell para filtrar por trait/nivel/fonte.
- `.listview-traits` mostra os trait-pills (ver secao 4) direto na lista, permitindo filtrar visualmente sem abrir o detalhe.
- Botoes de acao do modal ficam fixos embaixo em `.modal-buttons` (fora da area de scroll).

Ou seja: e busca/filtro + lista com preview ao vivo do texto da regra, sempre no mesmo padrao de modal para qualquer tipo de escolha (feat, spell, item, ancestry trait, etc.) — um componente picker reutilizado, nao uma tela por tipo.

## 4. Ficha

Numeros/agrupamentos confirmados (labels e classes CSS):

- **AC**: `.ac-holder` — icone de escudo (`.ac-image`) com o numero sobreposto (`.ac-text`, grid stack) e o label embaixo (`.ac-label`), nao uma linha de texto simples.
- **HP / Shield / Stamina**: barras de progresso visuais, nao so numero — `.healthbar`, `.shield-healthbar`, `.progress-bar` com variantes de cor `.progress-bar-red` / `.progress-bar-green` / `.progress-bar-stamina` / `.progress-bar-shield` (Stamina = variante Remaster/regras de resistencia).
- **Saves e Perception**: strings `"Fortitude"`, `"Reflex"`, `"Will"`, `"Perception"` confirmadas, layout em `.defense-lines` / `.defense-top-line` / `.defense-second-line`.
- **Pericias** (`#container-section-skills`, classe `.section-skills`): lista compacta, cada linha `.section-skill` com nome (`.section-skill-name`, trunca com ellipsis) e total (`.section-skill-total`), cursor pointer com hover laranja — clique provavelmente rola o dado direto na pericia.
- **Condicoes ativas** (`#section-conditions` / `.div-conditions`): linha de icones `.condition` com nome clicavel (`.condition-name`) e imagem (`.condition-image`).
- **Ataques/armas** (`.weapon-bar`): linha por arma com nome (`.weapon-name`), bonus de acerto (`.weapon-hit`), **MAP explicito** (`.mapspan` — multiple attack penalty, mostrado sempre visivel na propria linha do ataque em vez de calculado mentalmente), traits (`.weapon-traits`) e icone de toggle 1H/2H (`.icon-2h`).
- **Magias**: organizadas por nivel de slot em colunas horizontais scrollaveis (`.div-spell-scroller` + `.div-spell-level`, 18em cada, uma coluna por nivel de spell), cada magia numa linha (`.spell-button-row`) com botao de cast dedicado (`.button-cast`) separado do nome.
- **Atributos**: `.ability-container` com label/total/modificador separados (`.abilityLabel`, `.abilityTotal`, `.abilityMod`) e **input de override manual** (`.override-ability-input`) — permite forcar um valor de atributo sem refazer a matematica de boosts.
- **Traits/raridade**: pills coloridas e consistentes entre feats, spells e itens — `.trait-common` (azul), `.trait-rare` (azul escuro), `.trait-uncommon` (laranja escuro), `.trait-unique` (roxo), `.trait-third` (verde) — o mesmo esquema de cor aparece em `.item-level-box` pra raridade de item, e em `.trait-size` / `.trait-alignment` como cores dedicadas.

## 5. Interacoes distintivas

- **Rolagem de dados fisica embutida**: `dicecode-min2.js` embarca o three.js completo e renderiza um **d20 (e outros dados) com fisica real num canvas** (`#canvas`, `#canvas-total`) dentro de uma gaveta lateral deslizante (`.dice-tray`, 360px, `position:fixed`, desliza da direita, acionada pelo icone flutuante `#dice-switch`). Resultado final tem cor por tipo de dano (`.color-fire`, `.color-cold`, `.color-elec`, `.color-acid`, `.color-precision`) e historico de rolagens (`#dice-history`, `.dice-history-item`). Isso e bem mais que um RNG com popup — e uma animacao de dado fisico completa, com log persistente na sessao.
- **Long-press como acao destrutiva rapida**: biblioteca `longpress.js` dispara evento customizado `long-press` apos 1000ms parado (tolerancia de 10px de movimento). No bundle, o padrao encontrado em itens de equipamento e: **click = abre detalhe/dialogo do item**; **long-press = confirmacao direta de "Really remove item from your equipment?"** (funcao `Su(true, mensagem, acao)` = dialogo de confirmacao generico). Ou seja, o app usa long-press como atalho de exclusao sem precisar abrir menu de contexto — click curto nunca deleta.
- **Steppers +/- em vez de input livre**: quantidade de item/carga (`.button-adjust-qty`) e ajustada por botoes +/-, nao digitando o numero.
- **Drag and drop de inventario**: classes `.dragged-item` e `.potential-drop` confirmam reordenacao/mover-para-container por arrastar (poucas ocorrencias no bundle — feature real mas pouco usada/pequena).
- **Multiplas builds simultaneas**: barra `#active-builds` no topo permite alternar entre personagens carregados sem navegar pra outra tela (analogo a abas de navegador).
- **GM Mode / Connect to GM em tempo real**: IndexedDB tem object stores dedicados `firebaseCacheGMMode` e `firebaseCacheEncountersMode`, e o app usa `localStorage` com chaves `gmModeID` / `gmModeChar` — confirma que o modo GM sincroniza fichas de jogadores em tempo real via Firebase, nao e so um export estatico.
- **Print/export via handoff por localStorage**: os botoes "Print" (spellbook, statblock) nao geram PDF no cliente diretamente — eles gravam o payload em `localStorage.setItem("spellbook", ...)` / `("statblock", ...)` e abrem `export.html` numa aba nova, que le esse localStorage pra montar a pagina de impressao. Padrao reutilizavel se o app proprio tambem quiser uma view de impressao separada.
- **Tooltip de critico dedicado**: `.tooltiptextCrit` (classe separada do tooltip padrao) sugere que o app tem hover especial pra explicar resultados de critico (sucesso/fracasso critico), nao so texto de ajuda generico.

## 6. Persistencia e export

- **Fichas de personagem**: guardadas em **IndexedDB**, object stores `saves` (dados) e `saveIDs` + `folders` (organizacao — o dialogo "Open Character" suporta pastas, nao so lista plana).
- **Portraits e imagens custom**: IndexedDB, stores `portraits` e `customBGs` (backgrounds customizados) — guardados como blobs locais, nao soh URL.
- **Custom packs** (conteudo homebrew): IndexedDB store `customFiles`.
- **Cache de modo GM/encounters**: IndexedDB stores `firebaseCacheGMMode` / `firebaseCacheEncountersMode`, sincronizado com Firebase quando logado.
- **localStorage** usado so pra flags leves e preferencias, nunca pra dados grandes: `colorMode`/`lastColorMode` (tema), `prefLastCampaign`, `prefLastCharacterID`, `prefLastCharacterModeStarbuilder`, `build` (ponteiro pro ultimo build ativo), `portrait`/`portraitH` (handoff temporario), `gmModeID`/`gmModeChar` (sessao de GM), `pdfObject`, `spellbook`/`statblock` (handoff pro `export.html`, ver secao 5).
- **Export JSON**: item de menu `sidenav-json` dispara rotina dedicada de export (`rh0` no bundle minificado) — serializa o personagem completo pra download, formato nao inspecionado em detalhe (identificadores minificados, precisaria interceptar o output real em runtime pra mapear o schema).
- **Compartilhamento**: "Share Copy of Character" (`sidenav-share`) cria copia compartilhavel, provavel via Firebase/backend (nao um export.html), mas o mecanismo exato nao ficou claro so pelo bundle estatico.

---

## Observacao para o Waybuilder

O ganho de UX mais facil de portar pro React sem reinventar a roda do Pathbuilder inteiro:
1. **Timeline por nivel** em vez de wizard sequencial por categoria (ancestry -> classe -> ...).
2. **Picker generico master-detail** (lista + painel de regra completa + filtros por trait) reaproveitado pra toda escolha (feat/spell/item/trait) — um so componente, parametrizado.
3. **Long-press = delete rapido, click = abrir detalhe** — evita menu de contexto extra.
4. **MAP e outros calculos derivados sempre visiveis na linha**, nao escondidos atras de tooltip.
5. **Multiplas fichas abertas ao mesmo tempo** via abas no topo.
