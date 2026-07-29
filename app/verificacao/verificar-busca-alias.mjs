/**
 * Prova que o NOME ANTIGO acha o registro.
 *
 * Decisao do Igor em 2026-07-29: manter todo o conteudo legado. A base ja o
 * mantinha -- as tres pilhas da triagem (971 removidos, 339 renomeados, 5.690
 * intocados) estao todas dentro dela --, mas o legado RENOMEADO so existia sob
 * o nome novo: a fusao guarda o antigo em `aliases`, e a busca do modal olhava
 * so `nome` e `id`. Quem digitasse o nome que aprendeu na mesa nao achava nada,
 * com o conteudo na base o tempo todo.
 *
 * Uso: node verificacao/verificar-busca-alias.mjs [url]
 *      (precisa do dev server: npx vite --port 5175)
 */
import { chromium } from "playwright";

const URL = process.argv[2] ?? "http://localhost:5175/";
const NIVEL1 = ".bloco.nivel";

// nome antigo -> nome que a Paizo deu no remaster
const PARES = [
  ["Power Attack", "Vicious Swing"],
  ["Sudden Charge", "Sudden Charge"],   // nao renomeado: tem de achar igual
];

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1440, height: 1200 } });
const erros = [];
pagina.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });

await pagina.goto(URL);
await pagina.waitForSelector(".slot-linha", { timeout: 30_000 });

async function escolher(rotulo, nome) {
  await pagina.locator(`${NIVEL1} .slot-linha`, { hasText: rotulo }).first().click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
  await pagina.locator(".modal .busca").fill(nome);
  await pagina.waitForTimeout(300);
  await pagina.locator(".modal-lista .nome", { hasText: new RegExp(`^${nome}$`) })
              .first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${ok ? "" : `   ${detalhe}`}`);
};

console.log("\nbusca pelo nome antigo (legado renomeado)");

await escolher("Classe deste nivel", "Fighter");
await pagina.locator(`${NIVEL1} .slot-linha`, { hasText: "Feat de classe" })
            .first().click();
await pagina.waitForSelector(".modal", { timeout: 10_000 });

for (const [antigo, novo] of PARES) {
  await pagina.locator(".modal .busca").fill(antigo);
  await pagina.waitForTimeout(400);
  const linhas = (await pagina.locator(".modal-lista li").allTextContents())
                   .map((t) => t.trim()).filter(Boolean);
  checar(linhas.some((l) => l.includes(novo)),
         `"${antigo}" acha ${novo}`, JSON.stringify(linhas.slice(0, 3)));
  if (antigo !== novo) {
    checar(linhas.some((l) => l.includes(antigo)),
           `e a linha mostra o nome antigo, para o resultado nao parecer errado`,
           JSON.stringify(linhas.slice(0, 3)));
  }
}

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `FALHOU -- ${falhas} verificacao(oes)`
                   : "busca por alias: nome antigo acha o registro");
await navegador.close();
process.exit(falhas ? 1 : 0);
