/**
 * Prova, no navegador, que o slot concedido deixou de ser so de feat.
 *
 * Spec: specs/2026-07-31-slot-concedido-generico.md
 *
 * A ponta que o gabarito nao alcanca: a fixture congela `slots_abertos`, mas
 * nao os CANDIDATOS do slot concedido (`SLOTS_DE_CANDIDATO` do teste de
 * paridade cobre class/skill/general/ancestry/free_archetype). Entao a lista
 * que o jogador ve nesses slots novos so aparece aqui -- e e justamente onde os
 * dois erros possiveis moram: slot que nasce VAZIO e slot que oferece a base
 * inteira.
 *
 * O caso: a heranca `Born of Elements` concede escolha de MAGIA (8 truques
 * elementais). Ate 2026-07-31 o motor filtrava `tipo != "feat"` e essa escolha
 * nunca era perguntada.
 *
 * Uso: node app/verificacao/verificar-slot-concedido-generico.mjs [url]
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

// os slots de criacao (ancestralidade, heranca, background) vivem na PRIMEIRA
// `section`, que nao e um `.bloco.nivel` -- estes comecam no "Nivel 1". O slot
// concedido por heranca tem `em: "criacao"` e cai junto com eles.
const criacao = () => pagina.locator("section").nth(0);

async function escolher(rotulo, nome) {
  const alvo = pagina.locator(".slot-linha", { hasText: rotulo }).first();
  await alvo.scrollIntoViewIfNeeded();
  await alvo.click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(350);
  const exato = new RegExp(`^${nome}$`, "i");
  await pagina.locator(".modal-lista .nome", { hasText: exato }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

console.log("\nslot concedido generico -- Yaoguai `Born of Elements`");

await escolher("Classe deste nivel", "Fighter");
await escolher("Ancestralidade", "Yaoguai");

const antes = (await criacao().innerText()).replace(/\s+/g, " ");
checar(!/Magia de Born of Elements/i.test(antes),
       "sem a heranca nao ha slot de magia (premissa)");

await escolher("Heranca", "Born of Elements");

const depois = (await criacao().innerText()).replace(/\s+/g, " ");
console.log(`  [criacao] ${depois.slice(0, 240)}`);
checar(/de Born of Elements/i.test(depois),
       "a heranca abre um slot NOVO, nomeando quem o concedeu", depois.slice(0, 200));
// o rotulo e pt-BR, nao o `itemType` cru do Foundry: quem le a ficha nao tem
// por que ver `spell`
checar(/Magia de Born of Elements/i.test(depois),
       "e o slot diz que pede MAGIA, nao feat", depois.slice(0, 200));

// a lista: nem vazia nem a base inteira. Os dois erros que este slot pode ter.
// "concedido por", e nao so o nome: a linha da HERANCA tambem passou a conter
// "Born of Elements" como valor escolhido, e casava primeiro.
// `Magia de`, e nao so o nome: a linha da HERANCA tambem contem "Born of
// Elements" como valor escolhido, e casava primeiro.
const linha = criacao().locator(".slot-linha", { hasText: /Magia de Born of Elements/i })
  .first();
await linha.scrollIntoViewIfNeeded();
await linha.click();
await pagina.waitForSelector(".modal", { timeout: 10_000 });
await pagina.waitForTimeout(700);
const nomes = await pagina.locator(".modal-lista .nome").allTextContents();
console.log(`  [lista] ${nomes.length}: ${nomes.slice(0, 10).join(", ")}`);
checar(nomes.length === 8,
       "e oferece os 8 truques elementais -- nem 0, nem as 1.638 da base",
       `${nomes.length} opcoes`);
checar(nomes.some((n) => /^Ignition$/i.test(n)) && nomes.some((n) => /^Frostbite$/i.test(n)),
       "com os nomes REMASTERIZADOS (`Ignition`, `Frostbite`)", nomes.join(", "));

// escolher fecha a pendencia -- e o ciclo completo do slot
await pagina.locator(".modal-lista .nome", { hasText: /^Ignition$/i }).first().click();
await pagina.locator(".modal footer .aceitar").click();
await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
await pagina.waitForTimeout(400);
const final = (await criacao().innerText()).replace(/\s+/g, " ");
checar(/Ignition/.test(final), "a escolha grava no slot", final.slice(0, 240));

await pagina.screenshot({ path: docs("screenshots/2026-07-31_slot-concedido-generico.png"),
                          fullPage: false });

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
if (erros.length) falhas++;
await navegador.close();
console.log(falhas ? `\nslot generico: ${falhas} falha(s)`
                   : "\nslot generico: ponta a ponta ok");
process.exit(falhas ? 1 : 0);
