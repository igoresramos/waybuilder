/**
 * Roda o Pathbuilder 2e local, para automatizar a comparacao.
 *
 * Pelo site nao da: `pathbuilder2e.com/app.html` responde 403 "Just a moment"
 * para Chromium headless (Cloudflare). Mas so a PAGINA esta atras do
 * Cloudflare -- o CDN de assets responde 200 a `curl` sem verificacao, entao
 * da para baixar o app inteiro (`docs/referencia-pathbuilder/app-local/`).
 *
 * O que travou a primeira tentativa, e a resposta: servido em `127.0.0.1` o
 * app fica no spinner "Loading" para sempre. A causa esta no proprio bundle:
 *
 *     "www.pathbuilder2e.com" == window.location.hostname
 *       ? segue
 *       : pede permissao de storage e espera resposta
 *     window.isLive = hostname.includes("pathbuilder2e.com")
 *
 * Duas hipoteses anteriores (asset faltando, POST recusado) eram falsas -- o
 * app so nao gosta do hostname. A saida NAO e mexer em `/etc/hosts`: navega-se
 * para a URL REAL e o Playwright serve tudo do disco por `page.route()`. O
 * hostname passa a ser `www.pathbuilder2e.com` sem que um byte saia da maquina,
 * e o Cloudflare nunca e contatado.
 *
 * Uso: node verificacao/pathbuilder-local.mjs
 */
import { chromium } from "playwright";
import { readFileSync, existsSync } from "node:fs";

const LOCAL = "../docs/referencia-pathbuilder/app-local/";
const RAIZ = `${LOCAL}assets/`;
const TIPO = { js: "application/javascript", css: "text/css", txt: "text/plain",
               png: "image/png", wav: "audio/wav", html: "text/html" };

const tipoDe = (nome) =>
  TIPO[nome.split(".").pop()] ?? "application/octet-stream";

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1600, height: 1100 } });
pagina.on("console", (m) => console.log(`  [console.${m.type()}] ${m.text().slice(0, 200)}`));
pagina.on("pageerror", (e) => console.log(`  [pageerror] ${String(e).slice(0, 200)}`));
pagina.on("requestfailed", (r) => console.log(`  [falhou] ${r.url().slice(0, 120)}`));

/** Serve do disco, sem rede. `null` = deixa passar (nao existe aqui). */
function servir(rota, caminho) {
  if (!existsSync(caminho)) return rota.abort();
  return rota.fulfill({ status: 200, body: readFileSync(caminho),
                        contentType: tipoDe(caminho) });
}

// ORDEM IMPORTA: no Playwright a rota registrada por ULTIMO ganha. Com o
// catch-all no fim, ele engolia a navegacao e a pagina saia pela rede -- e
// voltava o desafio do Cloudflare, com a interceptacao no lugar.
// o app faz POST de telemetria/salvamento; sem resposta ele nao trava, mas o
// console enche de erro e atrapalha a leitura
await pagina.route("**/*", (rota) => {
  if (rota.request().method() === "POST") {
    return rota.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  }
  return rota.continue();
});

// a pagina e os assets, TUDO do disco -- a URL real existe so para o hostname
// regex, e nao glob: o Cloudflare redireciona `www` para o apex, e o glob com
// `www.` deixava a SEGUNDA requisicao passar pela rede -- era ela que trazia o
// desafio de volta, com a interceptacao aparentemente no lugar.
await pagina.route(/https?:\/\/(www\.)?pathbuilder2e\.com\//, (rota) => {
  const caminho = new URL(rota.request().url()).pathname;
  console.log("  servindo do disco:", caminho);
  if (caminho === "/app.html" || caminho === "/") return servir(rota, `${LOCAL}app.html`);
  return servir(rota, LOCAL + caminho.replace(/^\//, ""));
});
// preserva o CAMINHO do CDN (`img/character_new.png`), nao so o nome: achatar
// jogava as imagens todas na raiz e elas falhavam em silencio
await pagina.route("**://pathbuilder2e-data.b-cdn.net/**", (rota) => {
  const caminho = new URL(rota.request().url()).pathname.replace(/^\//, "");
  return servir(rota, RAIZ + caminho);
});
await pagina.goto("https://pathbuilder2e.com/app.html",
                  { waitUntil: "load", timeout: 60_000 });
await pagina.waitForTimeout(4000);
console.log("hostname:", await pagina.evaluate(() => location.hostname),
            "| isLive:", await pagina.evaluate(() => window.isLive));
// o app pede permissao de storage antes de montar
// No apex o app pede permissao de storage antes de montar ("...save character
// information and 3mb+ of data to your browser cache. Continue?"). O botao nao
// e <button>, entao locator por texto exato -- e ele so aparece DEPOIS do
// `location.replace` de www para o apex, que era o que fazia o clique anterior
// cair no vazio.
await pagina.locator('text="Accept"').first().click({ timeout: 10_000 })
            .catch(() => console.log("  (sem dialogo de permissao)"));

let carregou = false;
for (let i = 0; i < 9; i++) {
  await pagina.waitForTimeout(5000);
  const t = await pagina.locator("body").innerText();
  if (!/Loading/i.test(t)) {
    console.log(`CARREGOU em t+${(i + 1) * 5}s`);
    carregou = true;
    break;
  }
  console.log(`t+${(i + 1) * 5}s ainda carregando`);
}

console.log("TELA:",
            (await pagina.locator("body").innerText()).slice(0, 600).replace(/\n+/g, " | "));
await pagina.screenshot({ path: "../docs/screenshots/2026-07-29_pathbuilder-local.png" });
await navegador.close();
process.exit(carregou ? 0 : 1);
