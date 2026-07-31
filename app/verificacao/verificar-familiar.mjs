/**
 * Prova, no navegador, que familiar e eidolon chegam com NUMERO na ficha.
 *
 * Spec: specs/2026-07-31-estatisticas-de-familiar-e-eidolon.md
 *
 * A ponta que nenhum teste de motor alcanca, e ela tinha DOIS defeitos de tela
 * que so aparecem aqui: o cartao de ator so renderizava quando `hp != null`, e
 * o eidolon nao tem HP proprio -- ele sumia inteiro; e a linha de atributos
 * saia zerada para o familiar, AFIRMANDO +0 em tudo, quando a regra diz que ele
 * nao tem atributos.
 *
 * Uso: node app/verificacao/verificar-familiar.mjs [url]
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

async function escolher(rotulo, nome) {
  // sem escopo de bloco: o slot do familiar e `em: "criacao"`, entao vive no
  // bloco de CRIACAO e nao no de nivel 1 -- procurar so em `.bloco.nivel`
  // nunca o acha.
  const alvo = pagina.locator(`.slot-linha`, { hasText: rotulo }).first();
  await alvo.scrollIntoViewIfNeeded();
  await alvo.click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(250);
  const exato = new RegExp(`^${nome.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`, "i");
  await pagina.locator(".modal-lista .nome", { hasText: exato }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

async function abaDeAtores() {
  await pagina.locator(".menu-abas button", { hasText: /ator|companheiro/i })
    .first().click();
  await pagina.waitForTimeout(200);
  return (await pagina.locator(".cartao-ator").first().textContent() ?? "")
    .replace(/\s+/g, " ").trim();
}

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${ok ? "" : `   ${detalhe}`}`);
};

console.log("\nfamiliar da Bruxa -- numero na ficha");

await escolher("Classe deste nivel", "Witch");

// a Bruxa CONCEDE o familiar, mas o ator so entra na ficha depois de escolher
// a especie -- o slot `familiar -- Familiar (Witch)` e a porta.
await escolher("familiar", "Pipefox");

const cartao = await abaDeAtores();
console.log(`  [cartao] ${cartao.slice(0, 220)}`);

checar(/familiar/i.test(cartao), "o familiar aparece na aba de atores", cartao.slice(0, 160));
checar(/\b5\s*HP\b/.test(cartao) || /HP/.test(cartao),
       "com a linha de HP", cartao.slice(0, 160));
// 5 HP por nivel: um Bruxo 1 tem 5
checar(/5\s*HP/.test(cartao), "e o numero e 5 (5 por nivel, Bruxo 1)",
       cartao.slice(0, 160));
checar(/25 ft/.test(cartao), "velocidade 25 ft, lida do feat `Pet`",
       cartao.slice(0, 160));
checar(/tiny/i.test(cartao), "e tamanho Tiny", cartao.slice(0, 160));

// o familiar NAO tem atributos: a ficha diz isso em vez de mostrar +0 em tudo
checar(/sem atributos proprios/i.test(cartao),
       "e a ficha DIZ que ele nao tem atributos, em vez de mostrar +0 em tudo",
       cartao.slice(0, 200));
const zerado = await pagina.locator(".cartao-ator .linha-atributos").count();
checar(zerado === 0, "nenhuma linha de atributo zerada no cartao do familiar",
       `linhas=${zerado}`);

// os saves do familiar sao os do MESTRE, mas o cartao mostra NUMERO -- copiar
// a linha inteira punha `[object Object]` na ficha
checar(!/\[object Object\]/.test(cartao),
       "e as salvaguardas saem como numero, nao como `[object Object]`",
       cartao.slice(0, 220));

await pagina.screenshot({ path: docs("screenshots/2026-07-31_familiar.png"),
                          fullPage: false });

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `\nfamiliar: ${falhas} FALHA(S)` : "\nfamiliar: ponta a ponta ok");
await navegador.close();
process.exit(falhas ? 1 : 0);
