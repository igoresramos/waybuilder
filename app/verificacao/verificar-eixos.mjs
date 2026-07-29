/**
 * Prova, no navegador, que cada eixo de sub-escolha oferece uma opcao por nome.
 *
 * O defeito que este script vigia: o Campeao oferecia `Justice` DUAS VEZES no
 * slot de causa, porque a mesma causa existia como `wb:cause/justice` e como
 * `wb:class-feature/justice`. A base ja e verificada pelo portao 3, mas quem
 * enxerga a duplicata e o jogador -- entao a checagem final e na tela.
 *
 * A lista do modal e VIRTUALIZADA: contar o que esta no DOM subconta. Por isso
 * o script rola ate o fim acumulando nomes, e so entao conta.
 *
 * Uso: node docs/verificacao/verificar-eixos.mjs [url]
 */
import { chromium } from "playwright";

const URL = process.argv[2] ?? "http://localhost:5175/";
const CLASSES = ["Champion", "Witch", "Wizard", "Barbarian"];

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1440, height: 1200 } });
const erros = [];
pagina.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });

await pagina.goto(URL);
await pagina.waitForSelector(".slot-linha", { timeout: 30_000 });

/**
 * Abre o modal de um slot pelo rotulo, SEMPRE no nivel 1.
 *
 * O escopo nao e detalhe: `Classe deste nivel` existe uma vez por nivel, e os
 * blocos de nivel futuro ficam sobrepostos -- o clique no primeiro era
 * interceptado pelo bloco do nivel seguinte e o script travava em retry.
 */
// `.futuro` marca nivel ainda sem classe -- vale para o nivel 1 tambem
const NIVEL1 = ".bloco.nivel";

async function abrirSlot(rotulo) {
  const alvo = pagina.locator(`${NIVEL1} .slot-linha`, { hasText: rotulo }).first();
  await alvo.scrollIntoViewIfNeeded();
  await alvo.click();
  await pagina.waitForSelector(".modal", { timeout: 10_000 });
}

async function fecharModal() {
  await pagina.locator(".modal-fundo").click({ position: { x: 5, y: 5 } });
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
}

/**
 * Varre a lista inteira e devolve `{ distintos, repetidos }`.
 *
 * Duas armadilhas da lista virtualizada, as duas ja cometidas aqui:
 *  - contar so o que esta no DOM SUBCONTA, entao e preciso rolar;
 *  - acumular cada leitura num array faz o total crescer para sempre (o mesmo
 *    item e relido a cada rolada) e o laco nunca converge. Por isso o acumulado
 *    e um Set, e a REPETICAO e medida dentro de cada leitura -- opcao repetida
 *    aparece duas vezes na MESMA tela, nao entre roladas.
 */
async function varrerLista() {
  const distintos = new Set();
  const repetidos = new Map();
  let paradas = 0;
  while (paradas < 3) {
    const lote = (await pagina.locator(".modal-lista .nome").allTextContents())
                   .map((n) => n.trim());
    const antes = distintos.size;
    const naTela = new Map();
    for (const n of lote) {
      distintos.add(n);
      naTela.set(n, (naTela.get(n) ?? 0) + 1);
    }
    for (const [n, q] of naTela) {
      if (q > 1) repetidos.set(n, Math.max(repetidos.get(n) ?? 0, q));
    }
    const rolou = await pagina.locator(".modal-lista").evaluate((e) => {
      const topo = e.scrollTop;
      e.scrollTop += 400;
      return e.scrollTop !== topo;
    });
    await pagina.waitForTimeout(60);
    paradas = (distintos.size === antes && !rolou) ? paradas + 1 : 0;
  }
  return { distintos, repetidos };
}

let falhas = 0;

for (const classe of CLASSES) {
  await abrirSlot("Classe deste nivel");
  await pagina.locator(".modal .busca").fill(classe);
  await pagina.waitForTimeout(200);
  await pagina.locator(".modal-lista .nome", { hasText: new RegExp(`^${classe}$`) })
              .first().click();
  await pagina.locator(".modal footer .aceitar").click();
  await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });

  const rotulos = (await pagina.locator(`${NIVEL1} .slot-rotulo`).allTextContents())
                    .map((r) => r.trim());
  const eixos = rotulos.filter((r) => r.toLowerCase()
                                       .startsWith(classe.toLowerCase() + " /"));

  console.log(`\n${classe}`);
  // Sem esta guarda o script "passa" quando nao encontra eixo nenhum -- que e
  // o pior resultado possivel: verde sem ter verificado nada. Aconteceu.
  if (!eixos.length) {
    falhas++;
    console.log(`  FALHA nenhum eixo encontrado. slots na tela: ` +
                `${rotulos.join(" | ")}`);
    continue;
  }
  for (const rotulo of eixos) {
    await abrirSlot(rotulo);
    const { distintos, repetidos } = await varrerLista();
    await fecharModal();

    if (repetidos.size) falhas++;
    console.log(`  ${repetidos.size ? "FALHA" : "ok   "} ` +
                `${rotulo.padEnd(34)} ${distintos.size} opcoes distintas` +
                (repetidos.size ? `  REPETIDAS: ${JSON.stringify([...repetidos])}` : ""));
  }
}

console.log(`\nerros de console: ${erros.length ? erros.join(" | ") : "nenhum"}`);
console.log(falhas ? `FALHOU -- ${falhas} slot(s) com opcao repetida`
                   : "todos os eixos com uma opcao por nome");
await navegador.close();
process.exit(falhas ? 1 : 0);
