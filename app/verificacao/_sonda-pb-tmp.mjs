/** Sonda descartavel: como o Pathbuilder trata escolha CONCEDIDA que nao e feat. */
import { abrirPathbuilder } from "./pathbuilder-comum.mjs";
const { navegador, pagina } = await abrirPathbuilder();
await pagina.locator("img[src*='character_new']").first().click({ timeout: 10_000 });
await pagina.waitForTimeout(2500);
await pagina.evaluate(() => {
  for (const c of document.querySelectorAll(".checkbox-container"))
    if (/outdated/i.test(c.textContent || "")) c.querySelector("label.switch")?.click();
});
await pagina.waitForTimeout(600);
await pagina.locator(".modal-button", { hasText: "Get Started" }).first().click();
await pagina.waitForTimeout(3500);
await pagina.keyboard.press("Escape").catch(() => {});
await pagina.waitForTimeout(800);

// as abas do topo -- a pergunta "onde mora a escolha de magia"
const abas = await pagina.locator("#id_tab_bar, .tab-bar, nav").first()
  .innerText().catch(() => "");
console.log("ABAS:", abas.replace(/\n+/g, " | ").slice(0, 300));

// bloco de identidade: Ancestry
const ident = pagina.locator(".build-section").nth(0);
console.log("IDENTIDADE:", (await ident.innerText()).replace(/\n+/g, " | ").slice(0, 300));
const btnAnc = ident.locator('.div-button:has-text("Ancestry")').first();
await btnAnc.click(); await pagina.waitForTimeout(1500);
await pagina.locator(".listview-title", { hasText: /^Lizardfolk$/ }).first()
  .click({ timeout: 8000 }).catch((e) => console.log("  ancestry falhou:", String(e).slice(0,80)));
await pagina.waitForTimeout(2000);
console.log("APOS ANCESTRY:", (await pagina.locator(".build-section").nth(0).innerText())
  .replace(/\n+/g, " | ").slice(0, 300));
const btnHer = pagina.locator(".build-section").nth(0)
  .locator('.div-button:has-text("Heritage")').first();
await btnHer.click(); await pagina.waitForTimeout(1500);
const lista = await pagina.locator(".listview-title").allTextContents();
console.log("HERANCAS:", lista.slice(0, 14).join(" | "));
await pagina.locator(".listview-title", { hasText: /Makari/ }).first()
  .click({ timeout: 8000 }).catch((e) => console.log("  heritage falhou:", String(e).slice(0,80)));
await pagina.waitForTimeout(2500);
console.log("NIVEL 1 APOS HERANCA:", (await pagina.locator(".build-section").nth(1).innerText())
  .replace(/\n+/g, " | ").slice(0, 500));
console.log("TELA TODA:", (await pagina.locator("body").innerText())
  .replace(/\n+/g, " | ").slice(0, 700));
await navegador.close();
