/**
 * Prova que a conjuracao aparece na ficha -- as DUAS rotas.
 *
 * Spec: specs/2026-07-29-spellcasting-de-arquetipo.md.
 *
 * O defeito que este script vigia e duplo, e o segundo e o pior:
 *  - a dedicacao de conjurador entrava na ficha sem entregar slot nenhum
 *    (13 dedicacoes, corrigido pelo passo 7g do pipeline);
 *  - e a conjuracao NUNCA aparecia na tela, nem a de classe. O bloco existia
 *    so em `src/telas/Ficha.tsx`, que nao e usado por ninguem -- o motor
 *    calculava desde sempre e o jogador nunca via.
 *
 * Uso: node verificacao/verificar-magia.mjs [url]
 *      (precisa do dev server: npx vite --port 5175)
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

const escapar = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

async function escolher(rotulo, nome, nivel = 1) {
  const bloco = pagina.locator(NIVEL1).nth(nivel - 1);
  await bloco.locator(".slot-linha", { hasText: rotulo }).first().click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  // o modal abre no filtro "De classe", e dedicacao nao tem trait de classe --
  // sem trocar para "Todos", buscar `Wizard Dedication` nao acha nada
  await pagina.locator(".modal .filtros button", { hasText: /^Todos$/ })
              .first().click({ timeout: 3000 }).catch(() => {});
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(350);
  await pagina.locator(".modal-lista .nome", { hasText: new RegExp(`^${escapar(nome)}$`) })
              .first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${ok ? "" : `   ${detalhe}`}`);
};

console.log("\nconjuracao na ficha -- classe e arquetipo");

await escolher("Classe deste nivel", "Fighter");
checar(await pagina.locator(".menu-abas button", { hasText: "Magia" }).count() === 0,
       "Guerreiro puro nao tem aba de Magia -- ela some quando nao ha conjuracao");

// sobe ate o nivel 4 e entra na rota gratuita: dedicacao no 2, Basic no 4
for (let i = 0; i < 3; i++) {
  await pagina.locator(".subir").first().click();
  await pagina.waitForTimeout(250);
}
for (const n of [2, 3, 4]) {
  await pagina.locator(NIVEL1).nth(n - 1)
              .locator(".slot-linha", { hasText: "Classe deste nivel" }).first().click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  await pagina.locator(".modal .busca").fill("Fighter");
  await pagina.waitForTimeout(300);
  await pagina.locator(".modal-lista .nome", { hasText: /^Fighter$/ }).first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

await escolher("Free Archetype", "Wizard Dedication", 2);
const aba = pagina.locator(".menu-abas button", { hasText: "Magia" });
checar(await aba.count() > 0, "a dedicacao de conjurador FAZ a aba de Magia aparecer");

if (await aba.count()) {
  await aba.first().click();
  const cartao = pagina.locator(".cartao-ator").first();
  const so_ded = (await cartao.textContent()) ?? "";
  checar(/sem slot/.test(so_ded),
         "so com a dedicacao: truques, e nenhum slot", so_ded.slice(0, 90));

  await escolher("Free Archetype", "Basic Wizard Spellcasting", 4);
  await pagina.locator(".menu-abas button", { hasText: "Magia" }).first().click();
  const texto = (await pagina.locator(".cartao-ator").first().textContent()) ?? "";
  // No nivel 4 a rota gratuita da rank 1 -- rank 2 vem no 6 e rank 3 no 8,
  // pela tabela RAW. Esperar 1..3 aqui seria testar a expectativa errada: o
  // teto do degrau Basic e 3, mas quem entrega o rank e o NIVEL.
  checar(/slots de rank 1/.test(texto) && !/slots de rank 2/.test(texto),
         "com Basic Spellcasting no nivel 4: um slot de rank 1, e so",
         texto.slice(0, 120));
  checar(/nao eleva/.test(texto),
         "e marcada como de arquetipo, que pela regra 18 NAO eleva");
  console.log(`         ${texto.replace(/\s+/g, " ").slice(0, 170)}`);
}

await pagina.screenshot({ path: docs("screenshots/2026-07-29_magia.png") });
console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `FALHOU -- ${falhas} verificacao(oes)`
                   : "conjuracao na ficha: ponta a ponta ok");
await navegador.close();
process.exit(falhas ? 1 : 0);
