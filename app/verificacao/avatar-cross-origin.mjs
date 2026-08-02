/**
 * O acervo de sprites saiu do proprio deploy e passou a vir do GitHub Pages
 * (`igoresramos.github.io`), outro dominio -- para o recorte deixar de ser
 * regido pelo teto de 100 MB de estaticos do plano Hobby da Vercel e passar a
 * caber no 1 GB do Pages, que e o que permite as 4 direcoes do boneco.
 *
 * Cross-origin sem `crossOrigin="anonymous"` tem dois jeitos de quebrar
 * silenciosamente: o canvas fica "tainted" e o `getImageData` do recolor
 * estoura `SecurityError` em toda peca com cor (o boneco carrega, so nao
 * pinta); e a resposta chega OPACA, que o service worker `CacheFirst` se
 * recusa a guardar (o avatar nunca fica offline, sem erro nenhum na tela).
 * Ninguem verificou isso rodando -- so leu o codigo. Esta prova roda de
 * verdade: intercepta os requests pra confirmar que o acervo sai do dominio
 * certo com a versao certa, e prova que o recolor pinta apesar do cross-origin
 * comparando o CONJUNTO de cores do canvas antes/depois de trocar a cor --
 * pixel a pixel via `getImageData`, que e exatamente o ponto de falha.
 */
import { chromium } from "playwright";

const ORIGEM_ACERVO = "igoresramos.github.io";
const SLOTS = ["hair", "clothes", "shield"];
const falhas = [];

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 900, height: 900 } });

const erros = [];
p.on("pageerror", (e) => erros.push(String(e)));

// Todo request do acervo passa pela funcao `url()` de Avatar.tsx, que sempre
// anexa `?v=` a um .png ou .json. So `?v=` nao basta como marcador: o Vite dev
// tambem versiona os deps pre-bundled (`react.js?v=<hash>`) e isso caiu na
// primeira rodada. Extensao + `?v=` juntos e o par que so o acervo produz.
const doAcervo = [];
p.on("request", (req) => {
  const u = req.url();
  let caminho;
  try { caminho = new URL(u).pathname; } catch { return; }
  if (/\.(png|json)$/i.test(caminho) && /[?&]v=/.test(u)) doAcervo.push(u);
});

await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(1500);

// abrir algumas casas pra garantir trafego de png (sprite) e json (paleta)
for (const slot of SLOTS) {
  const casa = p.locator(`.avatar-casa[data-slot="${slot}"]`).first();
  if (await casa.count()) { await casa.click(); await p.waitForTimeout(1200); await p.keyboard.press("Escape"); }
}
await p.waitForTimeout(500);

// -- 1. origem certa ----------------------------------------------------------
const foraDoPages = doAcervo.filter((u) => !u.includes(ORIGEM_ACERVO));
const pngs = doAcervo.filter((u) => u.includes(".png"));
const jsons = doAcervo.filter((u) => u.includes(".json"));
if (doAcervo.length === 0) falhas.push("nenhum request do acervo foi capturado -- pagina nao carregou asset nenhum");
if (foraDoPages.length > 0) falhas.push(`${foraDoPages.length} request(s) do acervo NAO foram para ${ORIGEM_ACERVO}: ${foraDoPages.slice(0, 3).join(", ")}`);

// -- 3. sufixo de versao -------------------------------------------------------
const semVersao = doAcervo.filter((u) => !/\?v=/.test(u));
if (semVersao.length > 0) falhas.push(`${semVersao.length} request(s) do acervo sem "?v=": ${semVersao.slice(0, 3).join(", ")}`);

// -- 2. recolor pinta cross-origin ---------------------------------------------
// mesma tecnica da avatar-cor-que-pinta.mjs: compara o CONJUNTO de cores do
// canvas, nao o topo do histograma -- a peca costuma ser fracao dos pixels.
const cores = () =>
  p.evaluate(() => {
    const cv = document.querySelector(".avatar-picker-peca canvas");
    if (!cv) return null;
    const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
    const s = new Set();
    for (let i = 0; i < d.length; i += 4)
      if (d[i + 3] > 0) s.add(`${d[i]},${d[i + 1]},${d[i + 2]}`);
    return [...s];
  });

const porSlot = [];
for (const slot of SLOTS) {
  const casa = p.locator(`.avatar-casa[data-slot="${slot}"]`).first();
  if (!(await casa.count())) { porSlot.push({ slot, erro: "sem casa" }); falhas.push(`slot "${slot}": nao achei a casa no picker`); continue; }
  await casa.click();
  await p.waitForTimeout(1500);

  // peca que nao desenha nesta animacao/corpo nao pode provar recolor: anda
  // ate achar uma que apareca, como a avatar-cor-que-pinta.mjs faz
  let pulos = 0;
  while (await p.locator(".avatar-sem-arte").count() && pulos < 8) {
    await p.locator('.avatar-seta[aria-label="proxima peca"]').click();
    await p.waitForTimeout(900);
    pulos++;
  }

  const botoes = p.locator(".avatar-canal button");
  const n = await botoes.count();
  if (n < 2) { porSlot.push({ slot, oferecidas: n }); falhas.push(`slot "${slot}": menos de 2 cores oferecidas, nao da pra provar mudanca`); await p.keyboard.press("Escape"); continue; }

  const antes = await cores();
  if (antes === null) { porSlot.push({ slot, erro: "sem canvas" }); falhas.push(`slot "${slot}": canvas do picker nao encontrado`); await p.keyboard.press("Escape"); continue; }

  // escolhe uma cor diferente da atual (indice no meio da lista)
  const alvo = botoes.nth(Math.floor(n / 2));
  const rotulo = await alvo.getAttribute("aria-label") ?? String(Math.floor(n / 2));
  await alvo.click();
  await p.waitForTimeout(1200);
  const depois = await cores();

  const surgiram = depois.filter((c) => !antes.includes(c));
  const mudou = surgiram.length > 0;
  porSlot.push({ slot, cor: rotulo, coresAntes: antes.length, coresDepois: depois.length, coresNovas: surgiram.length, mudou });
  if (!mudou) falhas.push(`slot "${slot}": trocar para "${rotulo}" NAO mudou nenhuma cor no canvas (recolor nao pintou)`);

  await p.keyboard.press("Escape");
  await p.waitForTimeout(300);
}

const securityErrors = erros.filter((e) => /SecurityError/i.test(e));
if (securityErrors.length > 0) falhas.push(`${securityErrors.length} SecurityError disparado(s): ${securityErrors[0]}`);
if (erros.length > securityErrors.length) {
  // outros pageerror nao sao o alvo desta prova, mas listamos pra nao esconder ruido
  porSlot.push({ outrosErros: erros.filter((e) => !/SecurityError/i.test(e)) });
}

console.log(JSON.stringify({
  origem: {
    totalRequestsAcervo: doAcervo.length,
    pngs: pngs.length,
    jsons: jsons.length,
    foraDoPages: foraDoPages.length,
  },
  versao: {
    comSufixoV: doAcervo.length - semVersao.length,
    semSufixoV: semVersao.length,
  },
  recolor: porSlot,
  securityErrors: securityErrors.length,
  falhas,
}, null, 1));

await b.close();
process.exit(falhas.length === 0 ? 0 : 1);
