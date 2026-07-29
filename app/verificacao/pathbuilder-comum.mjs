/**
 * Abre o Pathbuilder 2e servido do disco, pronto para automacao.
 *
 * A receita inteira (e por que ela e assim) esta em
 * `docs/2026-07-29_pathbuilder-local.md`. Resumo do que NAO pode mudar:
 *
 *  - navega para a URL REAL: o bundle so monta em `pathbuilder2e.com`, e o
 *    conteudo vem todo do disco por `page.route()` -- o Cloudflare nunca e
 *    contatado;
 *  - APEX, nao `www`: entrando por `www` o app faz `location.replace` para o
 *    apex, e um glob com `www.` deixa a segunda requisicao vazar para a rede;
 *  - a rota registrada por ULTIMO ganha: o catch-all de POST vai PRIMEIRO;
 *  - o dialogo de permissao de storage aparece so depois do redirect, e o
 *    botao nao e um `<button>`.
 */
import { chromium } from "playwright";
import { readFileSync, existsSync } from "node:fs";

const LOCAL = "../docs/referencia-pathbuilder/app-local/";
const RAIZ = `${LOCAL}assets/`;
const TIPO = { js: "application/javascript", css: "text/css", txt: "text/plain",
               png: "image/png", wav: "audio/wav", html: "text/html" };

const tipoDe = (nome) => TIPO[nome.split(".").pop()] ?? "application/octet-stream";

function servir(rota, caminho) {
  if (!existsSync(caminho)) return rota.abort();
  return rota.fulfill({ status: 200, body: readFileSync(caminho),
                        contentType: tipoDe(caminho) });
}

/** Devolve `{ navegador, pagina }` com o app ja montado. */
export async function abrirPathbuilder({ viewport = { width: 1600, height: 1100 },
                                         verboso = false } = {}) {
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({ viewport });
  if (verboso) {
    pagina.on("console", (m) => console.log(`  [${m.type()}] ${m.text().slice(0, 160)}`));
    pagina.on("requestfailed", (r) => console.log(`  [falhou] ${r.url().slice(0, 110)}`));
  }

  await pagina.route("**/*", (rota) => (
    rota.request().method() === "POST"
      ? rota.fulfill({ status: 200, contentType: "application/json", body: "{}" })
      : rota.continue()));

  await pagina.route(/https?:\/\/(www\.)?pathbuilder2e\.com\//, (rota) => {
    const caminho = new URL(rota.request().url()).pathname;
    if (caminho === "/app.html" || caminho === "/") return servir(rota, `${LOCAL}app.html`);
    return servir(rota, LOCAL + caminho.replace(/^\//, ""));
  });

  await pagina.route("**://pathbuilder2e-data.b-cdn.net/**", (rota) =>
    servir(rota, RAIZ + new URL(rota.request().url()).pathname.replace(/^\//, "")));

  await pagina.goto("https://pathbuilder2e.com/app.html",
                    { waitUntil: "load", timeout: 60_000 });
  await pagina.waitForTimeout(4000);
  await pagina.locator('text="Accept"').first().click({ timeout: 10_000 }).catch(() => {});

  for (let i = 0; i < 12; i++) {
    await pagina.waitForTimeout(2500);
    if (!/Loading/i.test(await pagina.locator("body").innerText())) {
      return { navegador, pagina };
    }
  }
  throw new Error("o Pathbuilder nao saiu do 'Loading' -- ver docs/2026-07-29_pathbuilder-local.md");
}
