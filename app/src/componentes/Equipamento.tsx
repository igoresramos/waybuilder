/**
 * Arma, armadura e escudo -- a aba que faltava para o motor poder trabalhar.
 *
 * O motor sempre soube calcular ataque e dano por arma e CA com cap de DEX,
 * escudo e penalidade de armadura; ele le tudo de `doc.inventario` e conta so o
 * que esta `equipado`. Como nenhuma tela escrevia ali, todo personagem saia
 * pelado: CA 10 + DEX e a aba de Ataques dizendo "nenhuma arma equipada" para
 * sempre. Nao era defeito de calculo, era falta de porta de entrada.
 *
 * Guardar (`equipado: false`) e diferente de remover: o item continua na ficha
 * e sai da conta -- que e o que se faz com a besta quando se saca a espada.
 */
import { useMemo, useState } from "react";
import type { Base } from "../motor/base";
import type { Candidato, Documento, Registro } from "../motor/tipos";
import { Slot } from "./Slot";
import { adicionarItem as adicionar, removerItem as remover,
         alternarEquipado as alternar } from "../doc";

const CATEGORIAS = [
  { kind: "weapon", rotulo: "Arma" },
  { kind: "armor", rotulo: "Armadura" },
  { kind: "shield", rotulo: "Escudo" },
  { kind: "equipment", rotulo: "Item" },
] as const;

/** Candidato cru: equipar nao tem requisito de regra, so de mao livre. */
const cru = (rs: Registro[]): Candidato[] =>
  rs.map((r) => ({
    id: r.id, nome: r.name ?? null, level: r.level ?? null,
    atende: true, motivos: [], ja_pego: false,
  })).sort((a, b) => (a.nome ?? "").localeCompare(b.nome ?? ""));

export function Equipamento({
  base, d, setD,
}: {
  base: Base;
  d: Documento;
  setD: (x: Documento) => void;
}) {
  const [cat, setCat] = useState<string>("weapon");

  const porKind = useMemo(() => {
    const m = new Map<string, Registro[]>();
    for (const r of base.por_id.values()) {
      if (!r.kind) continue;
      if (!m.has(r.kind)) m.set(r.kind, []);
      m.get(r.kind)!.push(r);
    }
    return m;
  }, [base]);

  const inventario = d.inventario ?? [];

  return (
    <div className="equipamento">
      <div className="equip-add">
        <select value={cat} onChange={(e) => setCat(e.target.value)}
                aria-label="categoria do item a adicionar">
          {CATEGORIAS.map((c) => (
            <option key={c.kind} value={c.kind}>
              {c.rotulo} ({(porKind.get(c.kind) ?? []).length})
            </option>
          ))}
        </select>
        <Slot
          base={base} tipo="class"
          rotulo={`Adicionar ${CATEGORIAS.find((c) => c.kind === cat)?.rotulo ?? ""}`}
          candidatos={cru(porKind.get(cat) ?? [])}
          escolhido={null}
          aoEscolher={(id) => setD(adicionar(d, id))}
        />
      </div>

      <ul className="lista-simples inventario">
        {inventario.map((i) => {
          const reg = base.opcional(i.item);
          return (
            <li key={i.item} className={i.equipado ? "" : "guardado"}>
              <span className="nome">{reg?.name ?? i.item}</span>
              <span className="dado">{reg?.kind ?? ""}</span>
              <button onClick={() => setD(alternar(d, i.item))}
                      aria-pressed={!!i.equipado}
                      title={i.equipado ? "guardar (sai da conta)" : "equipar"}>
                {i.equipado ? "equipado" : "guardado"}
              </button>
              <button className="link" onClick={() => setD(remover(d, i.item))}
                      aria-label={`remover ${reg?.name ?? i.item}`}>
                x
              </button>
            </li>
          );
        })}
        {!inventario.length && (
          <li className="vazio">
            nada no inventario -- sem arma nao ha ataque, e sem armadura a CA e
            so 10 + DEX
          </li>
        )}
      </ul>
    </div>
  );
}
