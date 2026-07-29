# Rodar o Pathbuilder localmente -- RESOLVIDO

Estado em 2026-07-29. **Funciona**: o app sobe, inicializa e chega na tela de
"New Character / Load Character", automatizavel pelo Playwright.

## Por que

A comparacao com o Pathbuilder precisa dele automatizado. Pelo site nao da:
`https://pathbuilder2e.com/app.html` responde **403 "Just a moment..."** para
Chromium headless -- Cloudflare.

O caminho local nasce de uma observacao: **so a pagina esta atras do
Cloudflare**. O CDN de assets (`pathbuilder2e-data.b-cdn.net`, BunnyCDN)
responde 200 para `curl` sem verificacao nenhuma.

## A causa do "Loading" eterno, e a saida

Servido em `127.0.0.1:8899`, o app ficava no spinner para sempre. Duas
hipoteses foram testadas e **descartadas**: asset faltando e POST recusado pelo
`python -m http.server`. Nenhuma era a causa.

A causa esta no proprio bundle, achada por `grep -o "location\.[a-zA-Z]*"`:

    "www.pathbuilder2e.com" == window.location.hostname
      ? (migra o banco e) window.location.replace("https://pathbuilder2e.com/app.html")
      : permissionStorage ? segue : pede permissao e ESPERA resposta
    window.isLive = hostname.includes("pathbuilder2e.com")

O app so monta em `pathbuilder2e.com`. Em qualquer outro host ele para -- e a
espera nao tem timeout, entao a tela fica em "Loading" sem erro nenhum.

**A saida nao e mexer em `/etc/hosts`.** Navega-se para a URL REAL e o
Playwright serve tudo do disco com `page.route()`: o hostname passa a ser
`pathbuilder2e.com` sem que um byte saia da maquina, e o Cloudflare nunca e
contatado.

Tres detalhes que custaram cada um uma rodada:

1. **Ordem das rotas.** No Playwright a rota registrada por ULTIMO ganha. Com o
   catch-all de POST registrado no fim, ele engolia a navegacao, a pagina saia
   pela rede e o desafio do Cloudflare voltava -- com a interceptacao
   aparentemente no lugar.
2. **Apex, nao `www`.** Entrando por `www`, o proprio app faz
   `location.replace` para o apex ("forwarded to the correct domain"). Um glob
   com `www.` deixava a segunda requisicao passar pela rede. Rota por **regex**,
   cobrindo os dois, e `goto` direto no apex.
3. **O dialogo de permissao.** No apex o app pede permissao de storage
   ("...save character information and 3mb+ of data to your browser cache.
   Continue?") e espera. O botao **nao e um `<button>`** -- `locator('text="Accept"')`.
   E ele so aparece depois do redirect, entao clicar antes nao adianta.

## Como rodar

    cd app && node verificacao/pathbuilder-local.mjs

Sem servidor local: o script serve o disco pela propria interceptacao.
Screenshot em `docs/screenshots/2026-07-29_pathbuilder-local.png`.

## O que esta em disco

`docs/referencia-pathbuilder/app-local/`:

- `app.html` -- copia da pagina, com as URLs do CDN reescritas para `assets/`
- `assets/` -- 22 arquivos, ~12 MB:
  - `Pathbuilder2eWebRemastered108b.js` (1,0 MB, o app em Kotlin/JS)
  - `data131.txt` (4,2 MB) -- dados legado
  - **`data_remastered71.txt` (3,4 MB)** -- dados do remaster, que e o que o app
    pede com "Remaster: On"; nao estava na copia e era a ultima peca faltando
  - `dice.wav`, `img/` (5 imagens), CSS, `nouislider`, `wNumb`, `dicecode`, `jwt`

Nenhum desses arquivos e redistribuido -- ficam no repo do projeto so como
copia de trabalho para comparacao, e todos vem do CDN publico do proprio app.

## Proximo passo

Sonda: criar personagem, montar um build igual ao do Waybuilder e exportar o
JSON (`Export > Export JSON`). O formato ja e conhecido, de
`docs/referencia/pathbuilder_export_exemplo.json`:

    proficiencies: { athletics: 0, nature: 2, castingPrimal: 2, martial: 2, ... }
    specials:      ["Hunt Prey", "Manifest Eidolon", "Beast Eidolon", ...]
    feats:         [["Monster Hunter", null, "Class Feat", 1, "Ranger Feat 1", ...]]
    pets:          [{ type: "Animal Companion", animal: "Dromaeosaur", ... }]

`0/2/4/6/8` = untrained/trained/expert/master/legendary. E o estado da ficha em
numero -- nao ha necessidade de ler icone de proficiencia na tela.
