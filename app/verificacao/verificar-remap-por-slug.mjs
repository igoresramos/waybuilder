/**
 * Prova, no navegador, que o remap de arma por SLUG NOMEADO chega a ficha.
 *
 * Spec: specs/2026-07-31-atomo-slug.md
 *
 * A ponta que o gabarito nao alcanca: a fixture roda contra a base de BUILD, e
 * o app carrega o payload ENXUTO de `emitir_app.py`. Se aquele passo cortasse
 * `weapon_proficiency` -- ele corta `prov`, `xref` e prosa --, o motor no
 * navegador leria untrained onde o Python le trained, e nenhum teste dos dois
 * lados veria a divergencia.
 *
 * O caso: `Sister of the Golden Erinys Dedication` trata `asp-coil` e
 * `scourge` (as duas MARCIAIS) como simples. Um Clerigo e trained em simples e
 * untrained em marciais. A espada longa entra como CONTROLE -- e marcial e nao
 * esta no `or`, entao tem de continuar untrained.
 *
 * Uso: node app/verificacao/verificar-remap-por-slug.mjs [url]
 *      (precisa do dev server de pe: npx vite --port 5175)
 */
import { chromium } from "playwright";
import { docs } from "./caminhos.mjs";

const URL = process.argv[2] ?? "http://localhost:5175/";

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1440, height: 1200 } });
const erros = [];
pagina.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });

await pagina.goto(URL);
await pagina.waitForSelector(".slot-linha", { timeout: 30_000 });

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${ok ? "" : `   ${detalhe}`}`);
};

async function escolherNoNivel(nivel, rotulo, nome, aba = null) {
  const bloco = pagina.locator(".bloco.nivel").nth(nivel - 1);
  const alvo = bloco.locator(".slot-linha", { hasText: rotulo }).first();
  await alvo.scrollIntoViewIfNeeded();
  await alvo.click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  // o modal de feat abre na aba `De classe`, que EXCLUI quem tem o trait
  // `archetype` -- uma dedicacao so aparece em `Dedicacoes` ou `Todos`.
  if (aba) {
    await pagina.locator(".modal button", { hasText: new RegExp(`^${aba}$`, "i") })
      .first().click();
    await pagina.waitForTimeout(250);
  }
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(300);
  const exato = new RegExp(`^${nome.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`, "i");
  await pagina.locator(".modal-lista .nome", { hasText: exato }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

async function equipar(nome) {
  await pagina.locator(".menu-abas button", { hasText: /equipamento/i }).first().click();
  await pagina.waitForSelector(".equipamento", { timeout: 10_000 });
  await pagina.locator(".equip-add .slot-linha").first().click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(350);
  const exato = new RegExp(`^${nome}$`, "i");
  await pagina.locator(".modal-lista .nome", { hasText: exato }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

/** A linha da aba de Ataques daquela arma, achatada. */
async function linhaDeAtaque(arma) {
  await pagina.locator(".menu-abas button", { hasText: /ataques/i }).first().click();
  await pagina.waitForTimeout(200);
  const li = pagina.locator(".lista-simples li", { hasText: new RegExp(arma, "i") })
    .first();
  return ((await li.textContent()) ?? "").replace(/\s+/g, " ").trim();
}

console.log("\nremap por slug -- Clerigo com Sister of the Golden Erinys");

// nivel 2: a dedicacao exige `character_level >= 2` e o slot de class feat do
// Clerigo nasce no nivel 2. O botao `.subir` repete a classe do nivel anterior,
// entao basta escolher Cleric uma vez.
await escolherNoNivel(1, "Classe deste nivel", "Cleric");
await pagina.locator("button.subir").first().click();
await pagina.waitForTimeout(400);

await equipar("Asp Coil");
await equipar("Scourge");
await equipar("Longsword");

const antes = await linhaDeAtaque("Asp Coil");
console.log(`  [antes] ${antes.slice(0, 160)}`);
checar(/untrained/i.test(antes),
       "sem a dedicacao a asp-coil marcial sai untrained (premissa)", antes.slice(0, 160));

await escolherNoNivel(2, "Feat de classe", "Sister of the Golden Erinys Dedication",
                      "Dedicacoes");

const asp = await linhaDeAtaque("Asp Coil");
const scourge = await linhaDeAtaque("Scourge");
const espada = await linhaDeAtaque("Longsword");
console.log(`  [asp]     ${asp.slice(0, 160)}`);
console.log(`  [scourge] ${scourge.slice(0, 160)}`);
console.log(`  [espada]  ${espada.slice(0, 160)}`);

checar(/trained/i.test(asp) && !/untrained/i.test(asp),
       "com a dedicacao a asp-coil passa a contar como SIMPLES -- trained", asp.slice(0, 160));
checar(/trained/i.test(scourge) && !/untrained/i.test(scourge),
       "e o scourge junto -- os dois slugs do mesmo `or`", scourge.slice(0, 160));
checar(/untrained/i.test(espada),
       "e a espada longa, marcial fora do `or`, CONTINUA untrained -- nao vaza",
       espada.slice(0, 160));

await pagina.screenshot({ path: docs("screenshots/2026-07-31_remap-por-slug.png"),
                          fullPage: false });

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
if (erros.length) falhas++;
await navegador.close();
console.log(falhas ? `\nremap por slug: ${falhas} falha(s)` : "\nremap por slug: ponta a ponta ok");
process.exit(falhas ? 1 : 0);
