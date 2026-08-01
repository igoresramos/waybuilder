/**
 * O NAVEGADOR DE QUEM JA USOU O APP COM O DEFEITO.
 *
 * As duas provas anteriores partem de um `localStorage` limpo. Ninguem que
 * jogou esta semana tem isso: a issue #1 deixou uma pilha de entradas `@1`
 * duplicadas, cada uma com o id de um mount diferente e NENHUMA com `id` dentro
 * do documento. Se a correcao tropecar nesse disco, ela troca um defeito por
 * outro pior -- perda em vez de acumulo.
 *
 * O disco e semeado AQUI, no formato exato de antes de 2026-08-01
 * (`{id, nome, atualizado, doc}` com `doc.esquema = "waybuilder/personagem@1"`,
 * `doc.id` ausente, `doc.base` ausente), e mais:
 *
 *   L. cinco duplicatas do defeito -- todas tem de aparecer e nenhuma sumir;
 *   M. a migracao `@1 -> @2` nao pode inventar berco (`nascida_em_pin` de ficha
 *      migrada tem de ficar nulo -- carimbar a base de hoje seria mentira);
 *   N. lista ILEGIVEL (JSON quebrado) nao pode ser sobrescrita em silencio.
 *
 * Uso: node docs/_verificacao/prova-legado-issue-1.mjs <url>
 */
import { chromium } from "/home/igor0/waybuilder/app/node_modules/playwright/index.mjs";

const URL_APP = process.argv[2] ?? "http://localhost:5199/";
const CHAVE = "waybuilder:personagens";

let falhas = 0;
const checar = (ok, descricao, detalhe = "") => {
  if (!ok) falhas++;
  console.log(`  ${ok ? "ok   " : "FALHA"} ${descricao}${detalhe ? `   ${detalhe}` : ""}`);
};
const pronto = (p) => p.waitForSelector("input.nome", { timeout: 60_000 });
const naTela = (p) => p.inputValue("input.nome");

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1400, height: 1000 } });
const erros = [];
pagina.on("pageerror", (e) => erros.push(String(e)));
pagina.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });
pagina.on("dialog", (d) => d.accept());

console.log(`\nDISCO LEGADO DA ISSUE #1 -- ${URL_APP}`);
await pagina.goto(URL_APP);
await pronto(pagina);

// == L: as cinco duplicatas que o defeito deixou ===========================
console.log("\nL -- cinco entradas `@1` duplicadas, como o defeito deixava");
await pagina.evaluate((chave) => {
  localStorage.clear();
  const lista = [];
  for (let i = 1; i <= 5; i++) {
    lista.push({
      id: `p-legado-${i}`,
      nome: "Valeros",
      atualizado: `2026-07-2${i}T10:00:00.000Z`,
      doc: {
        esquema: "waybuilder/personagem@1",   // sem `id`, sem `base`
        identidade: { nome: "Valeros", jogador: "" },
        escolhas: [{ slot: "ancestry", id: "wb:ancestry/human", nivel: 1 }],
        atores: [], inventario: [], anotacoes: {},
      },
    });
  }
  localStorage.setItem(chave, JSON.stringify(lista));
}, CHAVE);

await pagina.reload();
await pronto(pagina);
await pagina.waitForTimeout(1200);

const apos = await pagina.evaluate((chave) => {
  const l = JSON.parse(localStorage.getItem(chave) ?? "[]");
  return { n: l.length, ids: l.map((e) => e.id), esquemas: l.map((e) => e.doc?.esquema) };
}, CHAVE);
console.log(`  disco: ${apos.n} entrada(s), ids=${JSON.stringify(apos.ids)}`);
checar(apos.n === 5, "nenhuma das cinco e descartada na carga (principio 4)", `n=${apos.n}`);
checar(await naTela(pagina) === "Valeros", "e o app abre uma delas, sem tela em branco",
       `tela=${JSON.stringify(await naTela(pagina))}`);

await pagina.click("button:has-text('fichas')");
await pagina.waitForSelector(".fichas", { timeout: 10_000 });
const listadas = await pagina.locator(".fichas li").count();
console.log(`  o seletor mostra ${listadas} ficha(s)`);
checar(listadas === 5, "as cinco ficam VISIVEIS -- o jogador pode enfim apagar o lixo",
       `li=${listadas}`);
const rotuloBase = await pagina.locator(".fichas li").first().innerText();
checar(/base nao registrada/.test(rotuloBase),
       "e ficha `@1` diz `base nao registrada` em vez de mostrar vazio",
       JSON.stringify(rotuloBase.replace(/\n/g, " | ").slice(0, 90)));

// apagar quatro: e o caminho de saida de quem foi mordido pela issue #1
for (let i = 0; i < 4; i++) {
  await pagina.locator(".fichas li").nth(1).locator("button.apagar").click();
  await pagina.waitForTimeout(350);
}
const sobrou = await pagina.evaluate((c) => JSON.parse(localStorage.getItem(c) ?? "[]").length, CHAVE);
console.log(`  apos apagar quatro: ${sobrou} entrada(s)`);
checar(sobrou === 1, "e apagar limpa o acumulo, uma por vez", `n=${sobrou}`);
await pagina.click(".fichas .fechar").catch(() => {});

// == M: a migracao nao inventa berco ======================================
console.log("\nM -- `@1 -> @2` na primeira gravacao daquela ficha");
await pagina.waitForTimeout(400);
await pagina.fill("input.nome", "Valeros Migrado");
await pagina.waitForTimeout(1200);
const migrado = await pagina.evaluate((c) => {
  const e = JSON.parse(localStorage.getItem(c) ?? "[]")[0];
  return { esquema: e?.doc?.esquema, id: e?.id, docId: e?.doc?.id, base: e?.doc?.base,
           escolhas: (e?.doc?.escolhas ?? []).length };
}, CHAVE);
console.log(`  ${JSON.stringify(migrado)}`);
checar(migrado.esquema === "waybuilder/personagem@2", "o esquema sobe para `@2`", migrado.esquema);
checar(migrado.docId === migrado.id,
       "o id da entrada `@1` e ADOTADO pelo documento (nao se cunha outro)",
       `${migrado.id} / ${migrado.docId}`);
checar(migrado.id.startsWith("p-legado-"), "e e o id que ja estava em disco", migrado.id);
checar(migrado.escolhas === 1, "as escolhas antigas continuam la", `${migrado.escolhas}`);
checar(migrado.base?.nascida_em_pin === null,
       "`nascida_em_pin` fica NULO: a base de hoje nao e o berco dela",
       JSON.stringify(migrado.base?.nascida_em_pin));
checar(typeof migrado.base?.pin === "string" && migrado.base.pin.length > 0,
       "mas a base ATUAL e carimbada", JSON.stringify(migrado.base?.pin));

// == N: lista ilegivel ====================================================
console.log("\nN -- lista ilegivel (JSON quebrado) nao pode ser sobrescrita em silencio");
await pagina.evaluate((chave) => {
  localStorage.clear();
  localStorage.setItem(chave, '[{"id":"p-x","doc":{"escolhas":[  <<< LIXO');
}, CHAVE);
await pagina.reload();
await pronto(pagina);
await pagina.fill("input.nome", "Depois Do Lixo");
await pagina.waitForTimeout(1200);
const resgate = await pagina.evaluate((chave) => {
  const chaves = Object.keys(localStorage);
  const copias = chaves.filter((k) => k.startsWith(`${chave}:corrompido-`));
  return { chaves, copias, copia: copias[0] ? localStorage.getItem(copias[0]) : null,
           atual: localStorage.getItem(chave) };
}, CHAVE);
console.log(`  chaves: ${JSON.stringify(resgate.chaves)}`);
checar(resgate.copias.length === 1, "os bytes ilegiveis sao COPIADOS antes de a chave sumir",
       JSON.stringify(resgate.copias));
checar((resgate.copia ?? "").includes("<<< LIXO"),
       "e a copia tem os bytes originais, na integra",
       JSON.stringify((resgate.copia ?? "").slice(0, 50)));
checar((resgate.atual ?? "").includes("Depois Do Lixo"),
       "e o app volta a gravar normalmente por cima");
checar(erros.length === 0, "e nada disso derruba o app", JSON.stringify(erros.slice(0, 2)));

console.log(`\nerros de console/pagina: ${erros.length}`);
for (const e of erros.slice(0, 6)) console.log(`  [erro] ${e.slice(0, 160)}`);
console.log(`\n${falhas === 0 ? "TUDO VERDE" : `${falhas} FALHA(S)`}\n`);
await navegador.close();
process.exit(falhas === 0 ? 0 : 1);
