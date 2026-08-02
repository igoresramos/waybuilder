/**
 * Prova visual da rota do avatar -- abre `#/avatar`, conta o que renderizou e
 * grava um print. Existe porque tipo e teste de unidade nao provam a cadeia
 * canvas: drawImage sobre o atlas consolidado, recolor em PNG real e zPos na
 * tela so aparecem aqui.
 *
 * Rode com o dev server no ar:
 *   node verificacao/avatar-prova.mjs ../docs/screenshots/avatar.png
 */
import { chromium } from "playwright";

const alvo = process.argv[2] ?? "avatar.png";
const url = process.env.URL ?? "http://127.0.0.1:5181/#/avatar";

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1280, height: 900 } });
const erros = [];
pagina.on("console", (m) => m.type() === "error" && erros.push(m.text()));
pagina.on("pageerror", (e) => erros.push(String(e)));

await pagina.goto(url, { waitUntil: "networkidle" });
await pagina.waitForTimeout(2500);

const relatorio = {
  casas: await pagina.locator(".avatar-casa").count(),
  bonecos: await pagina.locator("canvas.avatar-boneco").count(),
  secoes: await pagina.locator(".avatar-casas section h3").allTextContents(),
  erros: erros.slice(0, 6),
};
await pagina.screenshot({ path: alvo, fullPage: true });
console.log(JSON.stringify(relatorio, null, 1));
await navegador.close();
