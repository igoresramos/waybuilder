/**
 * Prova que o avatar abre SEM REDE -- a decisao 4 da spec ("offline de
 * verdade": o uso e mesa de jogo, pode nao ter rede e o app tem de abrir).
 *
 * Carrega uma vez com rede para o service worker instalar o precache, corta a
 * rede, recarrega e exige que o boneco desenhe.
 */
import { chromium } from "playwright";

const url = process.env.URL ?? "http://127.0.0.1:4180/#/avatar";
const b = await chromium.launch();
const ctx = await b.newContext();
const p = await ctx.newPage();
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));

await p.goto(url, { waitUntil: "networkidle" });
await p.waitForFunction(() => navigator.serviceWorker?.controller !== null, null,
                        { timeout: 60000 }).catch(() => {});
await p.waitForTimeout(8000); // o precache baixa 499 entradas

const swAtivo = await p.evaluate(() => !!navigator.serviceWorker.controller);

await ctx.setOffline(true);
await p.reload({ waitUntil: "domcontentloaded" });
await p.waitForTimeout(4000);

const desenhou = await p.evaluate(() => {
  const cv = document.querySelector(".avatar-palco canvas");
  if (!cv) return { erro: "sem canvas" };
  const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
  let opacos = 0;
  for (let i = 3; i < d.length; i += 4) if (d[i] > 0) opacos++;
  return { opacos, casas: document.querySelectorAll(".avatar-casa").length };
});

console.log(JSON.stringify({ swAtivo, offline: desenhou, erros: erros.slice(0, 3) }, null, 1));
await b.close();
