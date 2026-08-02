/**
 * Prova que a cabeca acompanha o tom de pele (`match_body_color`).
 *
 * Clica num tom diferente e compara o pixel do rosto com o do torso: sem a
 * heranca, o rosto fica na cor antiga e o torso muda -- o defeito que a flag
 * corrige.
 */
import { chromium } from "playwright";

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 500, height: 500 } });
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));
await p.goto(process.env.URL ?? "http://127.0.0.1:5181/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(2000);

const amostra = () =>
  p.evaluate(() => {
    const ctx = document.querySelector(".avatar-palco canvas").getContext("2d");
    const px = (x, y) => Array.from(ctx.getImageData(x, y, 1, 1).data).slice(0, 3).join(",");
    return { rosto: px(128, 100), torso: px(128, 185) };
  });

const antes = await amostra();
const tons = p.locator(".avatar-tons button");
await tons.nth(6).click();          // um tom bem diferente do padrao
await p.waitForTimeout(1500);
const depois = await amostra();

console.log(JSON.stringify({
  antes, depois,
  rostoMudou: antes.rosto !== depois.rosto,
  torsoMudou: antes.torso !== depois.torso,
  coerente: depois.rosto === depois.torso,
  erros,
}, null, 1));
await b.close();
