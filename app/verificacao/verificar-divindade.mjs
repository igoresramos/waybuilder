/**
 * Prova, no navegador, que a divindade fecha o circuito: o slot aparece so
 * para quem a exige, e escolher muda a FICHA (fonte, arma favorita, dominios).
 *
 * O EFEITO no predicado (Harming Hands recusado por fonte errada) nao e
 * conferido aqui: um Clerigo 1 nao tem slot de feat de classe no nosso modelo
 * de progressao, e o oraculo e a paridade ja provam os dois sentidos.
 *
 * Spec: specs/2026-07-30-divindade-na-ficha.md
 *
 * O motor ja e testado nas duas linguagens, mas nada disso prova que a tela
 * liga as pontas -- e esse era exatamente o buraco do item 98: a base tinha 488
 * divindades estruturadas (`divine_font`, `domains`, `favored_weapon`) e ZERO
 * consumidores.
 *
 * Uso: node app/verificacao/verificar-divindade.mjs [url]
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
  const exato = new RegExp(`^${nome.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`);
  await pagina.locator(".modal-lista .nome", { hasText: exato }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

const rotulos = async () =>
  (await pagina.locator(`${NIVEL1} .slot-rotulo`).allTextContents())
    .map((r) => r.trim());

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${ok ? "" : `   ${detalhe}`}`);
};

console.log("\ndivindade na ficha");

// um Guerreiro NAO deve ganhar slot de divindade: o eixo so existe nas classes
// que citam `class-feature/deity-*`
await escolher("Classe deste nivel", "Fighter");
checar(!(await rotulos()).some((r) => /deity|divindade/i.test(r)),
       "Guerreiro nao ganha slot de divindade");

await pagina.reload();
await pagina.waitForSelector(".slot-linha", { timeout: 30_000 });
await escolher("Classe deste nivel", "Cleric");

const comClerigo = await rotulos();
const slot = comClerigo.find((r) => /deity|divindade/i.test(r));
checar(slot !== undefined, "Clerigo ganha o slot de divindade",
       comClerigo.join(" | "));

if (slot) {
  const valor = await pagina.locator(`${NIVEL1} .slot-linha`, { hasText: slot })
                            .first().locator(".slot-valor").textContent();
  checar(/nao escolhid/i.test(valor ?? ""), "e ele comeca vazio",
         `valor="${valor}"`);

  await escolher(slot, "Pharasma");

  const fechou = await pagina.locator(`${NIVEL1} .slot-linha`, { hasText: slot })
                             .first().locator(".slot-valor").textContent();
  checar((fechou ?? "").includes("Pharasma"), "escolhida, o slot mostra qual",
         `valor="${fechou}"`);

  // a FICHA -- e nao so o slot -- tem de mudar
  const cartao = pagina.locator(".coluna-pericias .deidade").first();
  checar(await cartao.count() > 0, "a ficha ganha a linha da divindade");
  if (await cartao.count()) {
    const texto = ((await cartao.textContent()) ?? "").replace(/\s+/g, " ");
    console.log(`         linha da ficha: ${texto.slice(0, 140)}`);
    checar(/fonte heal/.test(texto), "com a fonte divina que Pharasma concede",
           texto);
    checar(/Dagger/i.test(texto), "e a arma favorita resolvida por nome", texto);
    checar(/Death|Fate|Healing|Knowledge/.test(texto),
           "e os dominios, tambem por nome", texto);
  }

  // O picker precisa ABRIR com as 488 opcoes: e o unico eixo da base com essa
  // ordem de grandeza, e o resto (predicado, motivo de recusa) ja esta provado
  // pelo oraculo e pela paridade. Um Clerigo 1 nao tem slot de feat de classe
  // no nosso modelo de progressao, entao nao da para conferir a lista por aqui.
  await abrirSlot(slot);
  const quantos = await pagina.locator(".modal-lista li").count();
  checar(quantos > 0, "o picker de divindade abre com opcoes", `n=${quantos}`);
  await pagina.locator(".modal .busca").fill("Sarenrae");
  await pagina.waitForTimeout(250);
  const achou = await pagina.locator(".modal-lista .nome", { hasText: /^Sarenrae$/ })
                            .count();
  checar(achou > 0, "e a busca por nome encontra a divindade");
  await pagina.keyboard.press("Escape");
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 })
              .catch(() => {});
}

await pagina.screenshot({ path: docs("screenshots/2026-07-30_divindade.png"),
                          fullPage: false });

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `\ndivindade: ${falhas} FALHA(S)` : "\ndivindade: ponta a ponta ok");
await navegador.close();
process.exit(falhas ? 1 : 0);
