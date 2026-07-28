/**
 * UM componente de escolha, reusado em todo slot.
 *
 * PRINCIPIO ZERO, e e aqui que ele fica visivel ou nao: o que nao atende o
 * requisito **aparece na lista, marcado, com o motivo** -- nunca escondido,
 * nunca bloqueado. O slot ja filtrou por TIPO (so feat de arquetipo entra no
 * slot gratuito); o requisito so ordena e explica.
 *
 * Uma tela que escondesse o que nao atende quebraria a regra central do
 * projeto sem que ninguem percebesse -- o motor continuaria certo e o app
 * estaria mentindo.
 */
import { useMemo, useState } from "react";
import type { Candidato } from "../motor/tipos";

interface Props {
  titulo: string;
  candidatos: Candidato[];
  escolhido?: string | null;
  aoEscolher: (id: string) => void;
  aoLimpar?: () => void;
  /** quantos mostrar antes de "ver mais" -- lista de feat tem centenas */
  janela?: number;
}

export function Picker({
  titulo, candidatos, escolhido, aoEscolher, aoLimpar, janela = 12,
}: Props) {
  const [busca, setBusca] = useState("");
  const [mostrarFora, setMostrarFora] = useState(false);
  const [expandido, setExpandido] = useState(false);

  const { atendem, fora } = useMemo(() => {
    const q = busca.trim().toLowerCase();
    const casa = (c: Candidato) =>
      !q || (c.nome ?? "").toLowerCase().includes(q) || c.id.includes(q);
    const filtrados = candidatos.filter(casa);
    return {
      atendem: filtrados.filter((c) => c.atende),
      fora: filtrados.filter((c) => !c.atende),
    };
  }, [candidatos, busca]);

  const visiveis = expandido ? atendem : atendem.slice(0, janela);

  return (
    <div className="picker">
      <header>
        <h4>{titulo}</h4>
        {escolhido && aoLimpar && (
          <button className="limpar" onClick={aoLimpar} title="desfazer escolha">
            limpar
          </button>
        )}
      </header>

      {escolhido && (
        <div className="escolhido">
          {candidatos.find((c) => c.id === escolhido)?.nome ?? escolhido}
        </div>
      )}

      {!escolhido && (
        <>
          <input
            className="busca"
            placeholder={`buscar entre ${candidatos.length}...`}
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />

          <ul className="opcoes">
            {visiveis.map((c) => (
              <li key={c.id}>
                <button onClick={() => aoEscolher(c.id)}>
                  <span className="nome">{c.nome ?? c.id}</span>
                  {c.level != null && <span className="nivel">nv{c.level}</span>}
                  {c.ja_pego && <span className="marca">ja tem</span>}
                </button>
              </li>
            ))}
            {!visiveis.length && <li className="vazio">nada encontrado</li>}
          </ul>

          {atendem.length > janela && (
            <button className="mais" onClick={() => setExpandido(!expandido)}>
              {expandido
                ? "mostrar menos"
                : `ver os outros ${atendem.length - janela}`}
            </button>
          )}

          {/* O QUE NAO ATENDE. Fica recolhido para nao poluir, mas o botao diz
              quantos sao -- o jogador precisa saber que existem. */}
          {fora.length > 0 && (
            <div className="fora">
              <button onClick={() => setMostrarFora(!mostrarFora)}>
                {mostrarFora ? "esconder" : "mostrar"} {fora.length} fora do
                requisito
              </button>
              {mostrarFora && (
                <ul className="opcoes marcadas">
                  {fora.slice(0, 30).map((c) => (
                    <li key={c.id}>
                      <button onClick={() => aoEscolher(c.id)}>
                        <span className="nome">{c.nome ?? c.id}</span>
                        {c.level != null && (
                          <span className="nivel">nv{c.level}</span>
                        )}
                        <span className="motivo">{c.motivos.join("; ")}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
              {mostrarFora && (
                <p className="nota">
                  o requisito <strong>sugere e ordena</strong>, nunca bloqueia --
                  da para escolher assim mesmo, e a ficha aponta
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
