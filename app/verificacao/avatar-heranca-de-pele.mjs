/**
 * A cabeca segue o tom de pele do corpo -- inclusive as nao-humanas.
 *
 * Relato do dono: "quando eu coloco uma cabeca [...] como cabeca de orc, porco,
 * ele ta indo com uma cor so, [...] n herda a cor do corpo".
 *
 * As 79 pecas com `match_body_color` tem de nascer na cor do corpo, e nao na
 * rampa em que a arte foi pintada. O orc e o caso limite: a arte dele nasce em
 * `ulpc.green` -- se a heranca falhar, a rampa verde continua na tela e o
 * defeito e visivel a olho nu. Medimos os dois lugares onde o boneco aparece,
 * o PALCO e a CASA, porque eles montam a selecao de formas diferentes.
 */
import { chromium } from "playwright";

/** A rampa `green` de `body_ulpc` -- a cor CRUA da arte do orc. */
const VERDE = ["#140C09", "#09320B", "#19541D", "#228236", "#39AA4E", "#53BF71"]
  .map((h) => h.slice(1).match(/../g).map((x) => parseInt(x, 16)).join(","));

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));
await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(1500);

const coresDe = (sel) =>
  p.evaluate((s) => {
    const cv = document.querySelector(s);
    if (!cv) return null;
    const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
    const m = new Map();
    for (let i = 0; i < d.length; i += 4)
      if (d[i + 3] > 0) {
        const k = `${d[i]},${d[i + 1]},${d[i + 2]}`;
        m.set(k, (m.get(k) ?? 0) + 1);
      }
    return [...m].sort((a, c) => c[1] - a[1]);
  }, sel);

// equipar a cabeca de orc: abrir a casa `head` e andar ate achar
await p.locator('.avatar-casa[data-slot="head"]').first().click();
await p.waitForTimeout(1200);
let achou = false;
for (let i = 0; i < 60 && !achou; i++) {
  const nome = await p.locator(".avatar-picker-peca strong").innerText();
  if (/orc/i.test(nome)) achou = true;
  else {
    await p.locator('.avatar-seta[aria-label="proxima peca"]').click();
    await p.waitForTimeout(220);
  }
}
if (!achou) { console.error("FALHA: nao achei a cabeca de orc no picker"); await b.close(); process.exit(1); }

const noPicker = await coresDe(".avatar-picker-peca canvas");
await p.locator(".avatar-picker footer .primario").click();
await p.waitForTimeout(1500);

const noPalco = await coresDe(".avatar-palco canvas");
const naCasa = await coresDe('.avatar-casa[data-slot="head"] canvas');

const falhas = [];
for (const [onde, cores] of [["picker", noPicker], ["palco", noPalco], ["casa", naCasa]]) {
  if (!cores) { falhas.push(`${onde}: canvas ausente`); continue; }
  const presentes = cores.filter(([k]) => VERDE.includes(k));
  const total = cores.reduce((s, [, n]) => s + n, 0);
  const verdes = presentes.reduce((s, [, n]) => s + n, 0);
  console.log(`${onde}: ${verdes}/${total} px na rampa crua do orc`
    + (presentes.length ? ` -> ${presentes.map(([k, n]) => `${k}(${n})`).join(" ")}` : ""));
  if (verdes > 0) falhas.push(`${onde}: ${verdes} px ficaram na cor crua da arte`);
}

if (erros.length) falhas.push(`erros de pagina: ${erros.join(" | ")}`);
console.log(falhas.length ? `\nFALHA\n- ${falhas.join("\n- ")}` : "\nOK: a cabeca de orc herdou o tom de pele nos tres lugares");
await b.close();
process.exit(falhas.length ? 1 : 0);
