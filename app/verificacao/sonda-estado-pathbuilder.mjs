/**
 * Colhe o ESTADO do personagem default (Human / Barkeep / <Classe> no nivel
 * pedido) -- atributos e pericias treinadas -- em vez das opcoes de um slot
 * (isso quem faz e sonda-pathbuilder.mjs). Receita de montagem do default
 * COPIADA de la (character_new -> toggle outdated -> Get Started -> Escape).
 *
 * Nivel real: o Pathbuilder tem um seletor dedicado "Set Character Level"
 * (botao `.div-button` rotulado "Level", no topo da coluna direita) -- so ele
 * muda o nivel EFETIVO do personagem (HP/AC/saves/pericias recalculados).
 * Abrir o bloco de nivel na arvore (`.build-section`) SEM setar o nivel apenas
 * deixa BROWSEAR o slot futuro (o proprio Pathbuilder mostra "Prerequisites
 * not met" nos botoes) -- nao muda a ficha.
 *
 * Troca de classe: a classe entra no bloco de IDENTIDADE (`.build-section`
 * indice 0), nao num nivel -- mesma receita usada em sonda-pathbuilder.mjs
 * (abrir o `.div-button` "Class", clicar o nome exato na lista, "Accept").
 *
 * Pericia TREINADA de verdade: nao e "bonus != +0" -- pericia sem treino
 * ainda mostra o modificador puro do atributo (ex.: Athletics +3 com STR +3 e
 * Prof 0). O sinal correto e o icone de proficiencia por linha
 * (`img[src*='icon_prof_']`, sufixo `untrained`/`trained`/`expert`/...),
 * visivel direto na ficha sem abrir modal. Descoberto investigando por que
 * Fighter nivel 2 parecia ter 4 pericias treinadas alem do background com 3
 * escolhas (Skill Training) + 1 (Class Skill) ainda pendentes: Acrobatics,
 * Athletics, Stealth e Thievery aparecem com bonus != +0 so porque STR/DEX
 * daquele build sao != 0 -- nenhuma das quatro estava de fato treinada
 * (icone `icon_prof_untrained` em todas, inclusive reabrindo os modais de
 * Skill Training e Class Skill depois de subir de nivel).
 *
 * Uso: node verificacao/sonda-estado-pathbuilder.mjs [Classe] [Nivel]
 * Saida: docs/comparacao/estado-pathbuilder-<classe>-nv<N>.json
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { abrirPathbuilder } from "./pathbuilder-comum.mjs";
import { docs } from "./caminhos.mjs";

const [CLASSE = "Fighter", NIVEL_TXT = "2"] = process.argv.slice(2);
const NIVEL = Number(NIVEL_TXT);
const SAIDA = docs("comparacao");
const chave = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");

const { navegador, pagina } = await abrirPathbuilder({ verboso: false });

// tela inicial -> criacao -> construtor (Human / Barkeep / Fighter 1, o default)
await pagina.locator("img[src*='character_new']").first().click({ timeout: 10_000 });
await pagina.waitForTimeout(2500);
await pagina.evaluate(() => {
  for (const c of document.querySelectorAll(".checkbox-container")) {
    if (/outdated/i.test(c.textContent || "")) c.querySelector("label.switch")?.click();
  }
});
await pagina.waitForTimeout(600);

await pagina.locator(".modal-button", { hasText: "Get Started" }).first().click();
await pagina.waitForTimeout(3500);
await pagina.keyboard.press("Escape").catch(() => {});
await pagina.waitForTimeout(800);

// troca de classe (default nasce Fighter) -- mesma receita de sonda-pathbuilder.mjs
if (CLASSE !== "Fighter") {
  const botaoClasse = pagina.locator(".build-section").nth(0)
                            .locator('.div-button:has-text("Class")').first();
  await botaoClasse.click({ timeout: 15_000 });
  await pagina.waitForTimeout(1500);
  await pagina.locator(".modal-content-listview .listview-title",
                       { hasText: new RegExp(`^${CLASSE}$`) }).first().click();
  await pagina.waitForTimeout(800);
  await pagina.locator(".modal-button", { hasText: /^(Select|OK|Accept)$/ }).first()
              .click({ timeout: 4000 }).catch(() => {});
  await pagina.waitForTimeout(2500);
}

// evidencia do estado PENDENTE de nivel 1 antes de subir de nivel (badges
// numericos ao lado de "Set Abilities"/"Skill Training"/"Class Skill" --
// contagem de escolhas ainda nao feitas -- e "Not Selected" nos slots
// singulares: Heritage, Ancestry Feat, Class Feat)
const nivel1AntesDeSubir = await pagina.locator(".build-section").nth(1).innerText();

// subir o personagem para o nivel alvo de fato: botao dedicado "Level" no
// topo da coluna direita, NAO o bloco da arvore (esse so navega, nao muda a
// ficha). Nivel 1 e o default -- nada a fazer.
if (NIVEL !== 1) {
  const botaoLevel = pagina.locator(".div-button",
    { has: pagina.locator(".button-text", { hasText: "Level" }) }).first();
  await botaoLevel.click({ timeout: 10_000 });
  await pagina.waitForTimeout(1000);
  await pagina.locator(".modal:visible", { hasText: "Set Character Level" })
              .locator(`text=/^Level ${NIVEL}$/`).first().click();
  await pagina.waitForTimeout(1500);
  await pagina.keyboard.press("Escape").catch(() => {});
  await pagina.waitForTimeout(500);
}

const nivelAtual = (await pagina.locator(".main-column-right").innerText())
  .match(/Level\n(\d+)/)?.[1];

// atributos: STR/DEX/CON/INT/WIS/CHA, formato "+N" (modificador, nao o score)
const atributos = {};
{
  const texto = await pagina.locator(".main-column-right").innerText();
  for (const sigla of ["STR", "DEX", "CON", "INT", "WIS", "CHA"]) {
    atributos[sigla] = texto.match(new RegExp(`${sigla}\\n([+-]\\d+)`))?.[1] ?? null;
  }
}

// pericias reais da ficha: nome + bonus + PROFICIENCIA pelo icone da linha
// (`.section-skill`, excluindo saves -- essas carregam a classe extra
// `saves-button` -- e as linhas que nao sao pericia de verdade: Perception,
// Initiative, "<Classe> DC")
const periciasDados = await pagina.evaluate(() => {
  const excluir = new Set(["Perception", "Initiative"]);
  return [...document.querySelectorAll(".section-skill")]
    .filter((el) => !el.classList.contains("saves-button"))
    .map((el) => ({
      nome: el.querySelector(".section-skill-name")?.textContent?.trim() ?? null,
      bonus: el.querySelector(".section-skill-total")?.textContent?.trim() ?? null,
      proficiencia: el.querySelector("img[src*='icon_prof_']")?.getAttribute("src")
        ?.match(/icon_prof_(\w+)\.png/)?.[1] ?? null,
    }))
    .filter((s) => s.nome && !excluir.has(s.nome) && !/ DC$/.test(s.nome));
});
const periciasTreinadas = periciasDados.filter((s) => s.proficiencia && s.proficiencia !== "untrained");

// pendencias sinalizadas na tela, nivel a nivel (badge numerico + "Not Selected")
const pendenciasPorNivel = [];
const totalNiveis = await pagina.locator(".build-section").count();
for (let i = 1; i < totalNiveis; i++) {
  const texto = (await pagina.locator(".build-section").nth(i).innerText()).trim();
  if (!texto) continue;
  pendenciasPorNivel.push({ indice: i, texto });
}

// evidencia direta: dentro dos modais de "Skill Training" e "Class Skill" o
// Pathbuilder escreve por extenso a contagem restante ("Remaining Skill
// Selections: N" / "Select Skill") -- procura o primeiro botao de cada rotulo
// entre os blocos ja alcancados (1..NIVEL) SEM escolher nada dentro.
async function textoLiteralDoModal(rotulo) {
  for (let i = 1; i <= NIVEL; i++) {
    const botao = pagina.locator(".build-section").nth(i)
                        .locator(".div-button", { hasText: rotulo }).first();
    if (await botao.count() === 0) continue;
    await botao.click({ timeout: 10_000 });
    await pagina.waitForTimeout(1000);
    const texto = (await pagina.locator(".modal:visible").first().innerText());
    await pagina.keyboard.press("Escape").catch(() => {});
    await pagina.waitForTimeout(500);
    return texto;
  }
  return null;
}
const modalSkillTraining = await textoLiteralDoModal("Skill Training");
const modalClassSkill = await textoLiteralDoModal("Class Skill");

const resultado = {
  fonte: "pathbuilder 2e web 108, remaster on, legado ligado",
  personagem: `Human / Barkeep / ${CLASSE}`,
  nivel_alvo: NIVEL,
  nivel_confirmado_na_tela: nivelAtual,
  atributos_modificador: atributos,
  pericias_treinadas_na_ficha: periciasTreinadas,
  pericias_todas_na_ficha: periciasDados,
  pendencias: {
    bloco_nivel1_antes_de_subir_de_nivel: nivel1AntesDeSubir,
    blocos_apos_atingir_nivel_alvo: pendenciasPorNivel,
    texto_literal_modal_skill_training: modalSkillTraining?.split("\n")[0] ?? null,
    texto_literal_modal_class_skill: modalClassSkill?.split("\n")[0] ?? null,
  },
};

mkdirSync(SAIDA, { recursive: true });
const arquivo = `${SAIDA}/estado-pathbuilder-${chave(CLASSE)}-nv${NIVEL}.json`;
writeFileSync(arquivo, JSON.stringify(resultado, null, 2));
console.log(JSON.stringify(resultado, null, 2));
console.log(`\n-> ${arquivo}`);

await pagina.screenshot({ path: docs(`screenshots/2026-07-29_pathbuilder-estado-${chave(CLASSE)}-nv${NIVEL}.png`),
                         fullPage: true });
await navegador.close();
