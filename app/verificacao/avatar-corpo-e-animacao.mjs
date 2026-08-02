/**
 * Seis corpos, cinco animacoes -- e o picker so oferece o que existe.
 *
 * Duas exigencias do dono:
 *  - "limitar a cada tipo de corpo os assets possiveis, nem todos encaixam em
 *    todos". Medido: `child` tem 98 das 627 pecas. O picker filtra, como o
 *    gerador faz (`components/tree/TreeNode.ts:163`).
 *  - todas as animacoes selecionaveis, com o boneco andando de fato.
 */
import { chromium } from "playwright";

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1100, height: 950 } });
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));
await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(1500);

const corpos = await p.locator(".avatar-corpos button").allTextContents();
const animacoes = await p.locator(".avatar-animacoes button").allTextContents();

// quantas pecas o picker de `hair` oferece em cada corpo
const porCorpo = {};
for (const c of ["male", "female", "teen", "child", "muscular", "pregnant"]) {
  const botao = p.locator(`.avatar-corpos button[data-corpo="${c}"]`);
  if (!(await botao.count())) continue;
  await botao.click();
  await p.waitForTimeout(800);
  await p.locator('.avatar-casa[data-slot="hair"]').first().click();
  await p.waitForTimeout(1500);
  const conta = await p.locator(".avatar-picker-conta").textContent();
  porCorpo[c] = Number(conta.split("/")[1].trim());
  await p.keyboard.press("Escape");
  await p.waitForTimeout(300);
}

await p.locator('.avatar-corpos button[data-corpo="male"]').click();
await p.waitForTimeout(600);

/** O palco anda sozinho? Duas leituras separadas por mais de um frame. */
const quadro = () =>
  p.evaluate(() => {
    const cv = document.querySelector(".avatar-palco canvas");
    const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
    let h = 0;
    for (let i = 0; i < d.length; i += 4) h = (h * 31 + d[i] + d[i + 3]) | 0;
    return h;
  });

const anda = {};
for (const anim of ["idle", "walk", "run"]) {
  await p.locator(`.avatar-animacoes button[data-animacao="${anim}"]`).click();
  await p.waitForTimeout(400);
  // amostra varias vezes: o ciclo do `idle` e [0,0,1] e duas leituras podem
  // cair no mesmo frame
  const vistos = new Set();
  for (let k = 0; k < 8; k++) {
    vistos.add(await quadro());
    await p.waitForTimeout(140);
  }
  anda[anim] = vistos.size > 1;
}

// as casas NAO animam: duas leituras iguais
const casa = () =>
  p.evaluate(() => {
    const cv = document.querySelector('.avatar-casa[data-slot="body"] canvas');
    if (!cv) return null;
    const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
    let h = 0;
    for (let i = 0; i < d.length; i += 4) h = (h * 31 + d[i] + d[i + 3]) | 0;
    return h;
  });
const c1 = await casa();
await p.waitForTimeout(600);
const c2 = await casa();

console.log(JSON.stringify({
  corpos, animacoes,
  pecasDeCabeloPorCorpo: porCorpo,
  palcoAnima: anda,
  casaFicaParada: c1 === c2,
  erros,
}, null, 1));
await b.close();
