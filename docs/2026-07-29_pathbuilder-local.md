# Rodar o Pathbuilder localmente -- ate onde foi, e o que falta

Estado em 2026-07-29. **Parcial**: o app sobe, o menu funciona e os dados estao
no disco; a inicializacao nao conclui.

## Por que tentar isso

A comparacao com o Pathbuilder precisa dele automatizado. Pelo site nao da:
`https://pathbuilder2e.com/app.html` responde **403 "Just a moment..."** para
Chromium headless -- Cloudflare. Contexto persistente ja passou o desafio em
sessao anterior, mas depende de um perfil validado a mao e nao sobrevive a
limpeza.

O caminho local nasce de uma observacao: **so a pagina esta atras do
Cloudflare**. O CDN de assets (`pathbuilder2e-data.b-cdn.net`, BunnyCDN)
responde 200 para `curl` sem nenhuma verificacao.

## O que ja funciona

1. `docs/referencia-pathbuilder/app-local/app.html` -- copia da pagina, com as
   URLs do CDN reescritas para `assets/`
2. `assets/` -- 19 arquivos, 8,7 MB, baixados do CDN:
   - `Pathbuilder2eWebRemastered108b.js` (1,0 MB, o app em Kotlin/JS)
   - **`data131.txt` (4,2 MB, os dados do jogo)** -- so aparece rastreando as
     requisicoes DEPOIS do "Accept"; nao esta citado no HTML
   - CSS, `nouislider`, `wNumb`, `dicecode`, `jwt`, icones
3. `app/verificacao/pathbuilder-local.mjs` -- sobe o Playwright, intercepta
   `**://pathbuilder2e-data.b-cdn.net/**` e serve do disco

Servir com:

    cd docs/referencia-pathbuilder/app-local && python3 -m http.server 8899 --bind 127.0.0.1
    cd app && node verificacao/pathbuilder-local.mjs

Resultado: menu inteiro renderizado (`sidenav-json`, `sidenav-new`,
`sidenav-feat-browser` -- ids estaveis, bons para automacao), dice tray
funcional, `pathbuilder2e_db@3` criado no IndexedDB, **zero erro de JavaScript**.

## O que trava

A tela fica no spinner "Loading" indefinidamente (medido ate t+90s). Nao ha
requisicao pendente ou falha que explique: com a interceptacao ativa, `data131.txt`
e todos os assets chegam com 200.

### Testado e DESCARTADO: o POST

O console acusava `501 Unsupported method ('POST')` do proprio
`python -m http.server`, e a hipotese era que o app travava esperando essa
resposta. `servir.py` foi escrito para responder `200 {}` a qualquer POST
(confirmado por `curl -X POST` -> 200). **Nao mudou nada**: a tela continua no
spinner ate t+90s. O 501 era ruido.

Quem retomar isto comeca do zero na causa -- as duas pistas gastas (asset
faltando, POST recusado) estao ambas descartadas. A proxima suspeita razoavel e
verificacao de origem dentro do bundle (o app conferir `location.hostname`
antes de liberar os dados), que so se resolve lendo Kotlin/JS minificado.

## Alternativas, se isto nao render

1. **Playwright headed sob xvfb com contexto persistente** no site real: passa o
   Cloudflare, mas depende de perfil validado a mao
2. **Export manual**: o Igor monta as sondas no navegador dele e exporta o JSON.
   Perde a automacao, mas o formato de export ja e o que interessa
   (`build.proficiencies` numerica, `build.specials`, `build.feats`), entao
   20-30 sondas exportadas a mao ja sustentam a comparacao

## O que o export entrega (confirmado)

De `docs/referencia/pathbuilder_export_exemplo.json`:

    proficiencies: { athletics: 0, nature: 2, castingPrimal: 2, martial: 2, ... }
    specials:      ["Hunt Prey", "Manifest Eidolon", "Beast Eidolon", ...]
    feats:         [["Monster Hunter", null, "Class Feat", 1, "Ranger Feat 1", ...]]
    pets:          [{ type: "Animal Companion", animal: "Dromaeosaur", ... }]

`0/2/4/6/8` = untrained/trained/expert/master/legendary. E o estado da ficha em
numero -- nao ha necessidade de ler icone de proficiencia na tela, que era o
desenho original da frente 1.
