/**
 * Prova, no navegador, os dois defeitos que o Igor relatou testando o app:
 *
 *   "nos boosts tu so pode clicar em cada status uma vez, ou seja, n tem como
 *    colocar +2 em nada"
 *   "alem disso n tem como upar pericias"
 *
 * Spec: specs/2026-07-31-slots-de-criacao-na-tela.md
 *
 * Por que esta camada, e nao o gabarito: os dois defeitos eram da TELA, nao do
 * motor. O motor somava boost repetido certo (duas entradas `["str"]` dao
 * `str 14`, medido) e abria `pericias_livres` desde 29/07 -- as fixtures
 * passavam verdes o tempo todo. So o navegador ve o que o jogador ve.
 *
 * Uso: node app/verificacao/verificar-slots-de-criacao.mjs [url]
 *      (precisa do dev server de pe)
 */
import { chromium } from "playwright";

const URL = process.argv[2] ?? "http://localhost:5173/";

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

console.log("\nslots de criacao -- Guerreiro humano nivel 1");

await escolher("Classe deste nivel", "Fighter");
await escolher("Ancestralidade", "Human");

// -- 1. boosts: uma linha por FONTE, nao uma fileira so --------------------
await pagina.locator(".cog", { hasText: "Boosts" }).first().click();
await pagina.waitForSelector(".boost-picker", { timeout: 10_000 });

const fontes = pagina.locator(".boost-fonte");
const nFontes = await fontes.count();
checar(nFontes >= 4,
       "o boost mostra uma linha por FONTE (Human, Human, chave, 4 livres)",
       `contei ${nFontes}`);

const origens = (await pagina.locator(".boost-origem").allInnerTexts()).join(" | ");
console.log(`  [fontes] ${origens}`);
checar(/habilidade-chave/i.test(origens),
       "e a linha da habilidade-chave da classe aparece nomeada", origens);

// a linha da chave do Guerreiro so oferece dex|str -- a fonte declara `opcoes`
const linhaChave = pagina.locator(".boost-fonte").filter({ hasText: "habilidade-chave" });
const botoesChave = await linhaChave.locator(".boost-linha button").count();
checar(botoesChave === 2,
       "a linha da chave oferece 2 atributos, nao 6 (a fonte declara `opcoes`)",
       `contei ${botoesChave}`);

// -- 2. O CASO DO IGOR: +2 no mesmo atributo, por fontes diferentes --------
// STR na primeira linha (Human) e STR na linha dos 4 livres
await fontes.nth(0).locator(".boost-linha button", { hasText: "STR" }).first().click();
await pagina.waitForTimeout(150);
const livres = pagina.locator(".boost-fonte").filter({ hasText: "4 livres" });
await livres.locator(".boost-linha").nth(0)
            .locator("button", { hasText: "STR" }).first().click();
await pagina.waitForTimeout(250);

const ficha = (await pagina.locator(".linha-atributos").first().innerText())
  .replace(/\s+/g, " ");
console.log(`  [atributos] ${ficha}`);
checar(/STR \+2/i.test(ficha),
       "STR em duas fontes soma +2 -- o caso reportado como impossivel", ficha);

// -- 3. dentro da MESMA fonte, o atributo nao repete (regra RAW) -----------
const bloqueados = await livres.locator(".boost-linha button:disabled").count();
checar(bloqueados > 0,
       "dentro do bloco de 4 livres, o atributo ja usado fica bloqueado",
       `contei ${bloqueados}`);

// -- 4. pericias treinadas existem na tela --------------------------------
const criacao = pagina.locator("section").nth(0);
const textoCriacao = (await criacao.innerText()).replace(/\s+/g, " ");
checar(/Pericia treinada/i.test(textoCriacao),
       "o slot `Pericia treinada` aparece na criacao",
       textoCriacao.slice(0, 200));

const nPericias = await pagina.locator(".slot-linha", { hasText: "Pericia treinada" }).count();
checar(nPericias === 3,
       "e sao TRES para o Guerreiro (orcamento da classe)", `contei ${nPericias}`);

// -- 5. e o slot oferece PERICIA, nao feat --------------------------------
await pagina.locator(".slot-linha", { hasText: "Pericia treinada" }).first().click();
await pagina.waitForSelector(".modal", { timeout: 10_000 });
const primeiros = (await pagina.locator(".modal-lista .nome").allInnerTexts()).slice(0, 8);
console.log(`  [candidatos] ${primeiros.join(", ")}`);
checar(primeiros.some((n) => /^(Acrobatics|Arcana|Athletics|Crafting)$/i.test(n)),
       "os candidatos sao PERICIAS -- antes o slot caia no `else` e dava feats",
       primeiros.join(", "));

await pagina.locator(".modal .busca").fill("Athletics");
await pagina.waitForTimeout(350);
await pagina.locator(".modal-lista .nome", { hasText: /^Athletics$/i }).first().click();
await pagina.locator(".modal footer .aceitar").click();
await pagina.waitForSelector(".modal", { state: "detached", timeout: 10_000 });
await pagina.waitForTimeout(250);

// -- 6. escolher a pericia muda o rank na ficha ---------------------------
const coluna = (await pagina.locator(".coluna-pericias").first().innerText())
  .replace(/\s+/g, " ");
const linhaAth = coluna.match(/Athletics[^A-Z]*/i)?.[0] ?? "";
console.log(`  [pericia] ${linhaAth.slice(0, 60)}`);
checar(/Athletics/i.test(coluna) && !/Athletics\s*\+0\b/i.test(linhaAth),
       "treinar Athletics muda o rank na coluna da direita", linhaAth);

checar(erros.length === 0, "sem erro de console", erros.slice(0, 3).join(" | "));

await navegador.close();
console.log(falhas ? `\n${falhas} FALHA(S)\n` : "\ntudo passou\n");
process.exit(falhas ? 1 : 0);
