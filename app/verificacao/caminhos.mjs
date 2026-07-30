/**
 * Onde os artefatos de verificacao nascem -- ancorado no ARQUIVO, nao no cwd.
 *
 * Todo script daqui escrevia em `"../docs/..."`, que so acerta o alvo se o
 * comando for dado de dentro de `app/`. Rodando da raiz do projeto (que e o
 * natural, porque `build.sh` e o oraculo rodam de la), `../docs` vira
 * `Tartarus/Projetos/pessoal/docs/` -- FORA do projeto. Foi o que aconteceu
 * com `2026-07-29_companheiro.png` em 30/07.
 *
 * Artefato orfao fora do projeto e exatamente o que a regra do Tartarus proibe,
 * e ja custou a perda do HTML da home do nimbulus-web em 21/04.
 */
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { mkdirSync } from "node:fs";

// este arquivo mora em <projeto>/app/verificacao/, entao a raiz sobe dois
export const PROJETO = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");

/** Caminho absoluto dentro de `<projeto>/docs/`, com a pasta ja criada. */
export function docs(...partes) {
  const alvo = resolve(PROJETO, "docs", ...partes);
  mkdirSync(dirname(alvo), { recursive: true });
  return alvo;
}
