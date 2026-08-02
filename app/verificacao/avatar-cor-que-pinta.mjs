/**
 * Toda cor oferecida tem de PINTAR -- pedido literal do dono.
 *
 * "as cores que aparecem para selecao devem ser todas reais e possiveis de
 * serem pareadas com o asset". A prova clica em cores espalhadas pela lista de
 * varios slots e exige que o boneco mude de verdade: cor que nao muda pixel
 * nenhum e cor que mente.
 *
 * O boneco do picker mostra o personagem inteiro, entao a comparacao e por
 * CONJUNTO de cores presentes, nao pelo topo do histograma -- a peca costuma
 * ser uma fracao dos pixels e o topo e sempre pele.
 */
import { chromium } from "playwright";

const SLOTS = ["hair", "hat", "clothes", "legs", "shoes", "shield", "head", "cape"];
const AMOSTRAS = 4;

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 900, height: 900 } });
const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));
await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(1500);

const cores = () =>
  p.evaluate(() => {
    const cv = document.querySelector(".avatar-picker-peca canvas");
    const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
    const s = new Set();
    for (let i = 0; i < d.length; i += 4)
      if (d[i + 3] > 0) s.add(`${d[i]},${d[i + 1]},${d[i + 2]}`);
    return [...s];
  });

const fora = [];
for (const slot of SLOTS) {
  const casa = p.locator(`.avatar-casa[data-slot="${slot}"]`).first();
  if (!(await casa.count())) { fora.push({ slot, erro: "sem casa" }); continue; }
  await casa.click();
  await p.waitForTimeout(2000);
  // peca que nao desenha nesta animacao (ou neste corpo) nao pode mudar de
  // cor: anda ate achar uma que apareca, em vez de acusar cor muda
  let pulos = 0;
  while (await p.locator(".avatar-sem-arte").count() && pulos < 8) {
    await p.locator('.avatar-seta[aria-label="proxima peca"]').click();
    await p.waitForTimeout(900);
    pulos++;
  }
  const peca = await p.locator(".avatar-picker-peca strong").textContent();
  const botoes = p.locator(".avatar-canal button");
  const n = await botoes.count();
  if (n === 0) { fora.push({ slot, oferecidas: 0 }); await p.keyboard.press("Escape"); continue; }

  const mudas = [];
  let testadas = 0;
  const passo = Math.max(1, Math.floor(n / AMOSTRAS));
  for (let i = passo; i < n; i += passo) {
    const antes = await cores();
    const alvo = botoes.nth(i);
    const rotulo = await alvo.getAttribute("aria-label") ?? String(i);
    await alvo.click();
    await p.waitForTimeout(900);
    const depois = await cores();
    testadas++;
    if (depois.filter((c) => !antes.includes(c)).length === 0) mudas.push(rotulo);
  }
  fora.push({ slot, peca, oferecidas: n, testadas, mudas });
  await p.keyboard.press("Escape");
  await p.waitForTimeout(300);
}

const falhou = fora.filter((f) => f.mudas?.length);
console.log(JSON.stringify({ porSlot: fora, slotsComCorMuda: falhou.length, erros }, null, 1));
await b.close();
process.exit(falhou.length === 0 && erros.length === 0 ? 0 : 1);
