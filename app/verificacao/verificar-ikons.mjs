/**
 * Prova, no navegador, que um eixo de `escolhe: N` deixa escolher as N.
 *
 * Spec: specs/2026-07-30-escolha-multipla-e-ikons.md
 *
 * O caso e novo na tela: ate 30/07 todos os 52 blocos de sub-escolha pediam
 * UMA, e `escolherSubclasse` SUBSTITUI por (nivel, eixo). Num eixo de tres, a
 * segunda escolha apagaria a primeira -- e o motor, do outro lado, nem lia o
 * campo `escolhe`. Aqui se prova a ponta que nenhum teste de motor alcanca: a
 * tela abre uma linha por ikon e as tres sobrevivem.
 *
 * Uso: node app/verificacao/verificar-ikons.mjs [url]
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

const rotulos = async () =>
  (await pagina.locator(`${NIVEL1} .slot-rotulo`).allTextContents()).map((r) => r.trim());

/** O texto de cada linha de ikon, na ordem da tela. */
const linhasDeIkon = async () => {
  const linhas = pagina.locator(`${NIVEL1} .slot-linha`, { hasText: /\/ ikon/ });
  return (await linhas.allTextContents()).map((s) => s.replace(/\s+/g, " ").trim());
};

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${ok ? "" : `   ${detalhe}`}`);
};

console.log("\nescolha multipla -- os tres ikons do Exemplar");

await escolher("Classe deste nivel", "Exemplar");

const comExemplar = await rotulos();
checar(comExemplar.some((r) => /\/ ikon 1\/3/.test(r)),
       "o Exemplar abre a primeira linha de ikon, marcada 1/3",
       comExemplar.join(" | "));

await escolher("/ ikon 1/3", "Gleaming Blade");
let agora = await linhasDeIkon();
checar(agora.some((l) => /Gleaming Blade/.test(l)),
       "escolhido o primeiro, ele fica na linha", agora.join(" | "));
checar(agora.some((l) => /ikon 2\/3/.test(l)),
       "e uma segunda linha abre", agora.join(" | "));

await escolher("/ ikon 2/3", "Barrow's Edge");
agora = await linhasDeIkon();
// e AQUI que a implementacao errada aparece: com `escolherSubclasse` o segundo
// substituiria o primeiro e `Gleaming Blade` sumiria da tela
checar(agora.some((l) => /Gleaming Blade/.test(l)),
       "o PRIMEIRO continua na tela depois do segundo -- nada foi substituido",
       agora.join(" | "));
checar(agora.some((l) => /Barrow/.test(l)), "e o segundo aparece", agora.join(" | "));

await escolher("/ ikon 3/3", "Starshot");
agora = await linhasDeIkon();
const escolhidas = ["Gleaming Blade", "Barrow", "Starshot"]
  .filter((n) => agora.some((l) => l.includes(n)));
checar(escolhidas.length === 3, "os TRES sobrevivem juntos", agora.join(" | "));

// nenhuma linha de ikon pode continuar VAZIA: `escolhe` chegou a zero
const vazias = await pagina.locator(`${NIVEL1} .slot-linha`, { hasText: /\/ ikon/ })
  .locator(".slot-valor", { hasText: /nao escolhid/i }).count();
checar(vazias === 0, "e nao sobra linha de ikon aberta", `vazias=${vazias}`);

// as tres tem de aparecer como FEATURES, que moram na aba `feats`
await pagina.locator(".menu-abas button", { hasText: /feats/i }).first().click();
const lista = (await pagina.locator(".lista-simples").first().textContent() ?? "")
  .replace(/\s+/g, " ");
const naFicha = ["Gleaming Blade", "Barrow", "Starshot"].filter((n) => lista.includes(n));
checar(naFicha.length === 3, "e as tres entram na ficha como features",
       lista.slice(0, 200));

await pagina.screenshot({ path: docs("screenshots/2026-07-30_ikons.png"),
                          fullPage: false });

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `\nikons: ${falhas} FALHA(S)` : "\nikons: ponta a ponta ok");
await navegador.close();
process.exit(falhas ? 1 : 0);
