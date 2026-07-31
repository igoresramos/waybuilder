/**
 * Prova, no navegador, que o dano chega DECOMPOSTO na ficha.
 *
 * Spec: specs/2026-07-30-dano-de-furia.md
 *
 * A ponta que nenhum teste de motor alcanca: ate 30/07 a aba de Ataques
 * mostrava so a string ja somada (`"1d12+4"`), e ela estava INCOMPLETA --
 * faltavam Weapon Specialization (26 das 27 classes, `grants: []` na base) e o
 * dano de furia (nove instintos, tambem `grants: []`). Aqui se prova que as
 * parcelas aparecem com a origem escrita, e que o condicional aparece SEM
 * entrar no total.
 *
 * Uso: node app/verificacao/verificar-dano.mjs [url]
 *      (precisa do dev server de pe: npx vite --port 5175)
 */
import { chromium } from "playwright";
import { docs } from "./caminhos.mjs";

const URL = process.argv[2] ?? "http://localhost:5175/";
const NIVEL1 = ".bloco.nivel";

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1440, height: 1200 } });
const erros = [];
pagina.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });

await pagina.goto(URL);
await pagina.waitForSelector(".slot-linha", { timeout: 30_000 });

async function abrirSlot(rotulo) {
  const alvo = pagina.locator(`${NIVEL1} .slot-linha`, { hasText: rotulo }).first();
  await alvo.scrollIntoViewIfNeeded();
  await alvo.click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
}

async function escolher(rotulo, nome) {
  await abrirSlot(rotulo);
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(250);
  const exato = new RegExp(`^${nome.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`, "i");
  await pagina.locator(".modal-lista .nome", { hasText: exato }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

/** O texto da aba de Ataques, achatado. */
async function abaDeAtaques() {
  await pagina.locator(".menu-abas button", { hasText: /ataques/i }).first().click();
  await pagina.waitForTimeout(150);
  const txt = await pagina.locator(".lista-simples").first().textContent() ?? "";
  return txt.replace(/\s+/g, " ").trim();
}

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${ok ? "" : `   ${detalhe}`}`);
};

console.log("\ndano decomposto -- Barbaro de instinto Dragon");

await escolher("Classe deste nivel", "Barbarian");
await escolher("instinct", "Dragon");

const vazio = await abaDeAtaques();
checar(/nenhuma arma equipada/i.test(vazio),
       "sem arma equipada a aba diz isso, e nao quebra", vazio.slice(0, 120));

// equipar pela aba de Equipamento e o unico caminho de TELA para ter ataque.
// `weapon` ja e a categoria default do select, e `adicionarItem` grava
// `equipado: true` -- entao basta escolher no slot "Adicionar Arma".
await pagina.locator(".menu-abas button", { hasText: /equipamento/i }).first().click();
await pagina.waitForSelector(".equipamento", { timeout: 10_000 });
await pagina.locator(".equip-add .slot-linha").first().click();
await pagina.waitForSelector(".modal", { timeout: 10_000 });
await pagina.locator(".modal .busca").fill("Greataxe");
await pagina.waitForTimeout(300);
await pagina.locator(".modal-lista .nome", { hasText: /^Greataxe$/i }).first().click();
await pagina.locator(".modal footer .aceitar").click();
await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
const estado = (await pagina.locator(".inventario li", { hasText: /Greataxe/ })
  .first().textContent() ?? "").replace(/\s+/g, " ").trim();
checar(/equipado/.test(estado), "a arma entra ja equipada no inventario", estado);

const texto = await abaDeAtaques();
console.log(`  [aba] ${texto.slice(0, 260)}`);

checar(/Greataxe/.test(texto), "a arma equipada aparece", texto.slice(0, 160));
checar(/1d12/.test(texto), "com o dado de dano", texto.slice(0, 160));

// as parcelas: a soma sozinha nao diz de onde veio, e era essa a lacuna
const parcelas = (await pagina.locator(".parcelas-de-dano .parcela")
  .allTextContents()).map((s) => s.replace(/\s+/g, " ").trim());
console.log(`  [parcelas] ${parcelas.join(" | ")}`);
checar(parcelas.length >= 2, "o dano vem DECOMPOSTO em parcelas, nao so somado",
       `parcelas=${parcelas.length}`);
checar(parcelas.some((p) => /1d12/.test(p)),
       "uma parcela e o dado da arma, com a origem escrita", parcelas.join(" | "));
checar(parcelas.some((p) => /FOR/.test(p)),
       "e outra e o atributo, nomeado", parcelas.join(" | "));
checar(parcelas.some((p) => /Rage|Dragon/i.test(p)),
       "e o dano de furia entra com a origem", parcelas.join(" | "));

// o condicional: aparece com a condicao escrita e NAO entra no total
const cond = (await pagina.locator(".parcela.condicional").allTextContents())
  .map((s) => s.replace(/\s+/g, " ").trim());
console.log(`  [condicional] ${cond.join(" | ") || "nenhum"}`);
checar(cond.length === 1, "o instinto Dragon rende UM condicional", cond.join(" | "));
checar(/draconic rage/i.test(cond.join(" ")),
       "com a condicao NOMEADA -- marca, nunca esconde", cond.join(" | "));

const total = (await pagina.locator(".lista-simples .dado").first().textContent() ?? "")
  .trim();
console.log(`  [total] ${total}`);
checar(!/\+1[0-9]/.test(total),
       "e o condicional NAO entrou no total", `total=${total}`);

await pagina.screenshot({ path: docs("screenshots/2026-07-30_dano-decomposto.png"),
                          fullPage: false });

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `\ndano: ${falhas} FALHA(S)` : "\ndano: ponta a ponta ok");
await navegador.close();
process.exit(falhas ? 1 : 0);
