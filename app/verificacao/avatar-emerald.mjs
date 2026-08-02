/** A cor listada tem de pintar no boneco -- caso `emerald`, da paleta all.lpcr. */
import { chromium } from "playwright";
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 900, height: 800 } });
await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(1500);
await p.locator('.avatar-casa[data-slot="hair"]').first().click();
await p.waitForTimeout(2000);
// O cabelo e uma FRACAO dos pixels: as tres cores mais comuns sao pele, e
// comparar so o topo do histograma dava "nao mudou" com o recolor
// funcionando. A prova olha as cores que existem, nao as que dominam.
const px = () => p.evaluate(() => {
  const cv = document.querySelector(".avatar-picker-peca canvas");
  const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
  const c = new Set();
  for (let i = 0; i < d.length; i += 4) if (d[i+3] > 0) c.add(`${d[i]},${d[i+1]},${d[i+2]}`);
  return [...c];
});
const RAMPA_EMERALD = ["15,18,24","23,32,56","25,51,45","28,69,37","37,86,46","48,100,47"];
const antes = await px();
const alvo = p.locator('.avatar-canal button[aria-label*="emerald"]');
const achou = await alvo.count();
if (achou) { await alvo.first().click(); await p.waitForTimeout(1800); }
const depois = await px();
const surgiram = depois.filter((c) => !antes.includes(c));
console.log(JSON.stringify({
  achouEmerald: achou > 0,
  coresQueSurgiram: surgiram.length,
  daRampaEmerald: RAMPA_EMERALD.filter((c) => surgiram.includes(c)).length,
  mudou: surgiram.length > 0,
}, null, 1));
await b.close();
