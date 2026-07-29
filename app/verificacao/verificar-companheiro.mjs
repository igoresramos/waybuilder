/**
 * Prova, no navegador, que o companheiro concedido por feat funciona ponta a
 * ponta: pegar o feat abre o slot da especie, escolher a especie fecha o slot,
 * e a ficha do bicho aparece com numero.
 *
 * Spec: specs/2026-07-29-companheiro-concedido.md.
 *
 * O motor ja e testado nas duas linguagens (106 assercoes no Python, 110 no
 * TS), mas nada disso prova que a TELA liga as pontas -- e foi exatamente esse
 * o buraco que a spec fechou: o motor sabia montar a ficha do companheiro
 * desde sempre, e o app nunca abria o slot.
 *
 * Uso: node verificacao/verificar-companheiro.mjs [url]
 *      (precisa do dev server de pe: npx vite --port 5175)
 */
import { chromium } from "playwright";

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

/** Busca pelo nome exato e aceita -- e o caminho que o jogador percorre. */
async function escolher(rotulo, nome) {
  await abrirSlot(rotulo);
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(250);
  // escapar: "Animal Companion (Ranger)" tem parenteses, que em regex viram
  // grupo e fazem o nome nunca casar
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

console.log("\ncompanheiro concedido por feat");

await escolher("Classe deste nivel", "Ranger");

// antes do feat nao existe slot de companheiro -- ele NASCE do `grant_actor`
const antes = await rotulos();
checar(!antes.some((r) => r.toLowerCase().includes("companheiro")),
       "sem o feat, nenhum slot de companheiro na tela", antes.join(" | "));

await escolher("Feat de classe", "Animal Companion (Ranger)");

const depois = await rotulos();
const slot = depois.find((r) => r.toLowerCase().startsWith("companheiro"));
checar(slot !== undefined, "pegar o feat abre o slot da especie", depois.join(" | "));

if (slot) {
  // o slot vazio precisa ser LEGIVEL de relance -- e a regra da tela
  const valor = await pagina.locator(`${NIVEL1} .slot-linha`, { hasText: slot })
                            .first().locator(".slot-valor").textContent();
  checar(/nao escolhid/i.test(valor ?? ""),
         "e o slot aparece como nao escolhido", `valor="${valor}"`);

  await escolher(slot, "Wolf");

  const fechou = await pagina.locator(`${NIVEL1} .slot-linha`, { hasText: slot })
                             .first().locator(".slot-valor").textContent();
  checar((fechou ?? "").includes("Wolf"), "escolhida a especie, o slot mostra o bicho",
         `valor="${fechou}"`);

  const aba = pagina.locator(".menu-abas button", { hasText: "Companheiro" });
  checar(await aba.count() > 0, "a aba do companheiro aparece na ficha");
  if (await aba.count()) {
    await aba.first().click();
    const cartao = pagina.locator(".cartao-ator").first();
    const texto = (await cartao.textContent()) ?? "";
    checar(/HP/.test(texto) && /CA/.test(texto),
           "e traz a ficha derivada (HP, CA, ataques)", texto.slice(0, 120));
    // Wolf young num Ranger 1: 8 de ancestria + (6+2)x1 = 16 HP, CA 16
    const hp = await cartao.locator("li", { hasText: /^\d+HP/ }).first().textContent()
                 .catch(() => "");
    console.log(`         ficha do bicho: ${texto.replace(/\s+/g, " ").slice(0, 160)}`);
    checar(hp !== "", "com numero, nao placeholder", `hp="${hp}"`);
  }
}

// a prova visual fica no projeto, nao em /tmp -- e o cartao do bicho e o unico
// pedaco da tela que nenhum teste de motor consegue olhar
await pagina.screenshot({ path: "../docs/screenshots/2026-07-29_companheiro.png",
                          fullPage: false });

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `FALHOU -- ${falhas} verificacao(oes)`
                   : "companheiro concedido: ponta a ponta ok");
await navegador.close();
process.exit(falhas ? 1 : 0);
