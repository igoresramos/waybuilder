/**
 * Colhe o ESTADO do personagem default (Human / Barkeep / Fighter nivel 2) --
 * atributos e pericias treinadas -- em vez das opcoes de um slot (isso quem
 * faz e sonda-pathbuilder.mjs). Receita de montagem do default COPIADA de la
 * (character_new -> toggle outdated -> Get Started -> Escape).
 *
 * Nivel 2 real: o Pathbuilder tem um seletor dedicado "Set Character Level"
 * (botao `.div-button` rotulado "Level", no topo da coluna direita) -- so ele
 * muda o nivel EFETIVO do personagem (HP/AC/saves/pericias recalculados).
 * Abrir o bloco de nivel 2 na arvore (`.build-section` indice 2) SEM setar o
 * nivel apenas deixa BROWSEAR o slot futuro (o proprio Pathbuilder mostra
 * "Prerequisites not met" nos botoes) -- nao muda a ficha. Descoberto por
 * exploracao: sonda-pathbuilder.mjs, ao contrario do que se supunha, NAO tem
 * um passo de "subir de nivel" -- ele so indexa o bloco futuro para ler as
 * OPCOES oferecidas, o que basta pra aquele proposito mas nao para este.
 *
 * Uso: node verificacao/sonda-estado-pathbuilder.mjs
 * Saida: docs/comparacao/estado-pathbuilder-fighter-nv2.json
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { abrirPathbuilder } from "./pathbuilder-comum.mjs";

const SAIDA = "../docs/comparacao";

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

// evidencia do estado PENDENTE de nivel 1 antes de subir de nivel (badges
// numericos "4"/"3"/"1" ao lado de "Set Abilities"/"Skill Training"/"Class
// Skill" -- contagem de escolhas ainda nao feitas -- e "Not Selected" nos
// slots singulares: Heritage, Ancestry Feat, Class Feat)
const nivel1AntesDeSubir = await pagina.locator(".build-section").nth(1).innerText();

// subir o personagem para nivel 2 de fato: botao dedicado "Level" no topo da
// coluna direita, NAO o bloco da arvore (esse so navega, nao muda a ficha)
const botaoLevel = pagina.locator(".div-button",
  { has: pagina.locator(".button-text", { hasText: "Level" }) }).first();
await botaoLevel.click({ timeout: 10_000 });
await pagina.waitForTimeout(1000);
await pagina.locator(".modal:visible", { hasText: "Set Character Level" })
            .locator("text=/^Level 2$/").first().click();
await pagina.waitForTimeout(1500);
await pagina.keyboard.press("Escape").catch(() => {});
await pagina.waitForTimeout(500);

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

// pericias: nome + bonus total exibido na coluna de pericias da ficha
const periciasTexto = (await pagina.locator(".section-skill").allTextContents())
  .map((t) => t.trim());

// pendencias sinalizadas na tela, nivel a nivel (badge numerico + "Not Selected")
const pendenciasPorNivel = [];
const totalNiveis = await pagina.locator(".build-section").count();
for (let i = 1; i < totalNiveis; i++) {
  const texto = (await pagina.locator(".build-section").nth(i).innerText()).trim();
  if (!texto) continue;
  pendenciasPorNivel.push({ indice: i, texto });
}

// evidencia direta: dentro do modal de "Skill Training" o Pathbuilder escreve
// por extenso "Remaining Skill Selections: N"
const nivel1Bloco = pagina.locator(".build-section").nth(1);
await nivel1Bloco.locator(".div-button", { hasText: "Skill Training" }).first()
                 .click({ timeout: 10_000 });
await pagina.waitForTimeout(1000);
const remanescenteSkillTraining = (await pagina.locator(".modal:visible").first().innerText())
  .split("\n")[0];
await pagina.keyboard.press("Escape").catch(() => {});
await pagina.waitForTimeout(500);

const resultado = {
  fonte: "pathbuilder 2e web 108, remaster on, legado ligado",
  personagem: "Human / Barkeep / Fighter",
  nivel_alvo: 2,
  nivel_confirmado_na_tela: nivelAtual,
  atributos_modificador: atributos,
  pericias_treinadas_na_ficha: periciasTexto.filter((p) => !p.startsWith("+0")),
  pericias_todas_na_ficha: periciasTexto,
  pendencias: {
    bloco_nivel1_antes_de_subir_de_nivel: nivel1AntesDeSubir,
    bloco_nivel1_depois_de_subir_de_nivel: pendenciasPorNivel.find((p) => p.indice === 1)?.texto,
    bloco_nivel2_depois_de_subir_de_nivel: pendenciasPorNivel.find((p) => p.indice === 2)?.texto,
    texto_literal_modal_skill_training: remanescenteSkillTraining,
  },
};

mkdirSync(SAIDA, { recursive: true });
const arquivo = `${SAIDA}/estado-pathbuilder-fighter-nv2.json`;
writeFileSync(arquivo, JSON.stringify(resultado, null, 2));
console.log(JSON.stringify(resultado, null, 2));
console.log(`\n-> ${arquivo}`);

await pagina.screenshot({ path: "../docs/screenshots/2026-07-29_pathbuilder-estado-fighter-nv2.png",
                         fullPage: true });
await navegador.close();
