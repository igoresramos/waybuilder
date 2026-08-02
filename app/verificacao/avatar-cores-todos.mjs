/** Confere que TODO slot com cor oferece as cores, nao so `hair`. */
import { chromium } from "playwright";
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 900, height: 800 } });
await p.goto(process.env.URL ?? "http://127.0.0.1:5182/#/avatar", { waitUntil: "networkidle" });
await p.waitForTimeout(1500);
const fora = [];
for (const slot of ["hair", "hat", "clothes", "head", "legs", "shoes", "weapon", "shield"]) {
  const casa = p.locator(`.avatar-casa[data-slot="${slot}"]`).first();
  if (!(await casa.count())) { fora.push([slot, "sem casa"]); continue; }
  await casa.click();
  await p.waitForTimeout(1800);
  const n = await p.locator(".avatar-canal button").count();
  const nome = await p.locator(".avatar-picker-peca strong").textContent();
  const etiqueta = await p.locator(".avatar-etiqueta").textContent().catch(() => null);
  fora.push([slot, n, nome, etiqueta]);
  await p.keyboard.press("Escape");
  await p.waitForTimeout(400);
}
console.log(fora.map((f) => JSON.stringify(f)).join("\n"));
await b.close();
