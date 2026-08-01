/**
 * O seletor de fichas -- a tela que faltava para `listar()` e `apagar()`.
 *
 * As duas funcoes existiam em `doc.ts` desde o inicio e NUNCA tinham chamador:
 * `grep -rn "doc.listar\|doc.apagar" app/src` dava zero (issue #1). O efeito
 * pratico nao era so codigo morto -- sem uma lista na tela, a ficha salva era
 * inalcancavel, e o jogador nao tinha como saber que existiam vinte copias dela.
 *
 * Tres acoes, e as tres sao do jogador:
 *
 *  - ABRIR: carrega aquela ficha e escreve o ponteiro `waybuilder:ultima`;
 *  - APAGAR: um por vez, com confirmacao. Nenhum caminho de codigo apaga
 *    sozinho -- nem a migracao, nem o tratamento de cota;
 *  - NOVA FICHA: o substituto do habito antigo. Ate 2026-08-01 recarregar a
 *    pagina era o unico jeito de comecar outra ficha (`App.tsx:54` cunhava id
 *    novo a cada mount); com a retomada, F5 volta na mesma ficha, e sem este
 *    botao o jogador acabaria editando a primeira por cima.
 *
 * Spec: `specs/2026-08-01-persistencia-e-identidade-de-build.md` (Decisao 2).
 */
import type { Salvo } from "../doc";
import { nivelDoPersonagem } from "../doc";

/** `atualizado` e ISO; na lista o que importa e a data legivel, nao o fuso. */
function quando(iso: string): string {
  if (!iso) return "sem data";
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? "sem data"
    : d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

/**
 * Ficha migrada de `@1` tem `pin: null` -- ela nasceu sob uma base que ninguem
 * registrou. Mostrar vazio se leria como bug; o texto diz o que e.
 */
function base(s: Salvo): string {
  const pin = s.doc.base?.pin;
  return pin ? pin.slice(0, 8) : "base nao registrada";
}

export function Fichas({
  fichas, atual, aoAbrir, aoApagar, aoNova, aoFechar,
}: {
  fichas: Salvo[];
  atual?: string;
  aoAbrir: (id: string) => void;
  aoApagar: (id: string) => void;
  aoNova: () => void;
  aoFechar: () => void;
}) {
  return (
    <div className="fichas-fundo" onClick={aoFechar}>
      <div className="fichas" onClick={(e) => e.stopPropagation()}>
        <header>
          <h2>fichas neste navegador ({fichas.length})</h2>
          <button className="fechar" onClick={aoFechar}>fechar</button>
        </header>

        {fichas.length === 0 && (
          <p className="nota">
            nenhuma ficha gravada ainda -- ela entra na lista na primeira escolha
          </p>
        )}

        <ul>
          {fichas.map((s) => (
            <li key={s.id} className={s.id === atual ? "atual" : ""}>
              <button className="abrir" onClick={() => aoAbrir(s.id)}>
                <strong>{s.nome || "Sem nome"}</strong>
                <span className="meta">
                  nivel {nivelDoPersonagem(s.doc)} &middot; {quando(s.atualizado)}
                  {" "}&middot; base {base(s)}
                </span>
              </button>
              <button
                className="apagar"
                onClick={() => {
                  // confirmacao aqui, e nao no chamador: apagar e irreversivel e
                  // nao ha backend de onde restaurar
                  if (confirm(`apagar "${s.nome || "Sem nome"}" para sempre?`)) {
                    aoApagar(s.id);
                  }
                }}
              >
                apagar
              </button>
            </li>
          ))}
        </ul>

        <button className="nova" onClick={aoNova}>+ nova ficha</button>
      </div>
    </div>
  );
}
