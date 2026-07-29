import { chromium } from "playwright";
import { readFileSync, existsSync } from "node:fs";
const RAIZ = "../docs/referencia-pathbuilder/app-local/assets/";
const TIPO = { js: "application/javascript", css: "text/css", txt: "text/plain",
               png: "image/png", wav: "audio/wav" };
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1600, height: 1100 } });
await p.route("**://pathbuilder2e-data.b-cdn.net/**", (rota) => {
  const nome = rota.request().url().split("/").pop().split("?")[0];
  const caminho = RAIZ + nome;
  if (!existsSync(caminho)) return rota.abort();
  rota.fulfill({ status: 200, body: readFileSync(caminho),
                 contentType: TIPO[nome.split(".").pop()] ?? "application/octet-stream" });
});
await p.goto("http://127.0.0.1:8899/app.html", { waitUntil: "load", timeout: 60000 });
await p.waitForTimeout(7000);
await p.locator('text="Accept"').first().click({ timeout: 10000 }).catch(() => {});
for (let i = 0; i < 9; i++) {
  await p.waitForTimeout(10000);
  const t = await p.locator("body").innerText();
  if (!/Loading/i.test(t)) { console.log(`CARREGOU em t+${(i+1)*10}s`); break; }
  console.log(`t+${(i+1)*10}s ainda carregando`);
}
console.log("TELA:", (await p.locator("body").innerText()).slice(0, 500).replace(/\n+/g, " | "));
await p.screenshot({ path: "../docs/screenshots/2026-07-29_pathbuilder-local.png" });
await b.close();
