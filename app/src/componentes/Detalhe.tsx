/**
 * O que um item CONCEDIDO e -- em leitura, sem escolha.
 *
 * `Blessed Armament`, `Devotion Spells`, `Shield Block` chegam pela progressao
 * da classe, nao por escolha, e por isso nao passam pelo picker. Mas o jogador
 * precisa saber o que ganhou tanto quanto precisa saber o que escolhe: no
 * Pathbuilder da para clicar em qualquer um deles e ler a regra.
 *
 * Reusa a mesma faixa de traits e a mesma prosa em partes do picker -- e o
 * mesmo conteudo, so falta o botao de aceitar.
 */
import { useEffect, useState } from "react";
import type { Base } from "../motor/base";
import { prosa } from "../carregarBase";
import { limparMarcacao } from "../marcacao";
import { Traits } from "./Traits";
import { Prosa } from "./Prosa";

export function Detalhe({
  base, id, aoFechar,
}: {
  base: Base;
  id: string;
  aoFechar: () => void;
}) {
  const reg = base.opcional(id);
  const [texto, setTexto] = useState<string | null>(null);

  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === "Escape") aoFechar(); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [aoFechar]);

  useEffect(() => {
    setTexto(null);
    if (!reg) return;
    let vivo = true;
    prosa(reg.text as string | undefined).then((t) => { if (vivo) setTexto(t); });
    return () => { vivo = false; };
  }, [reg]);

  return (
    <div className="modal-fundo" onClick={aoFechar}>
      <div className="modal modal-leitura" onClick={(e) => e.stopPropagation()}>
        <header>
          <h3>{reg?.name ?? id}</h3>
          {reg?.level != null && <span className="nv">{reg.level}</span>}
        </header>
        <div className="modal-detalhe">
          {!reg && (
            <p className="vazio">
              este item nao esta na base carregada (<code>{id}</code>)
            </p>
          )}
          {reg && (
            <>
              <Traits base={base} reg={reg} />
              {texto
                ? <Prosa texto={texto} nome={reg.name}
                         prerequisito={typeof reg.requires_texto === "string"
                           ? limparMarcacao(reg.requires_texto) : null} />
                : <p className="vazio">sem texto para este registro</p>}
            </>
          )}
        </div>
        <footer>
          <button onClick={aoFechar}>Fechar</button>
        </footer>
      </div>
    </div>
  );
}
