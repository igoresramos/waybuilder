/**
 * Icones proprios, em SVG inline.
 *
 * O Pathbuilder usa PNG licenciado (icon_ancestry.png, icon_class.png, ...);
 * nada disso entra aqui. Sao desenhos nossos, de traco, herdando `currentColor`
 * -- assim a mesma peca serve no slot cinza e no cog em accent.
 */

const base = {
  viewBox: "0 0 24 24", fill: "none", stroke: "currentColor",
  strokeWidth: 1.5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const,
};

/** Ancestralidade e heranca -- arvore, que e linhagem. */
export const IconeAncestria = () => (
  <svg {...base} className="icone" aria-hidden>
    <path d="M12 21v-6" />
    <path d="M12 15c-3 0-5-2-5-4.5S9 6 12 6s5 2 5 4.5S15 15 12 15z" />
    <path d="M12 6V3M9 9.5 6.5 8M15 9.5 17.5 8" />
  </svg>
);

/** Background -- pergaminho, que e a historia de antes da aventura. */
export const IconeBackground = () => (
  <svg {...base} className="icone" aria-hidden>
    <path d="M6 4h10a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V4z" />
    <path d="M9 8h6M9 12h6M9 16h3" />
  </svg>
);

/** Classe e feat de classe -- espada. */
export const IconeClasse = () => (
  <svg {...base} className="icone" aria-hidden>
    <path d="M14.5 3.5 20 3l-.5 5.5-8 8" />
    <path d="m8 16 0 0-3.5 3.5a1.5 1.5 0 0 0 2 2L10 18" />
    <path d="m6.5 14.5 3 3" />
  </svg>
);

/** Feat de pericia -- cabeca, que e treino. */
export const IconePericia = () => (
  <svg {...base} className="icone" aria-hidden>
    <path d="M9 21v-2.5C6.5 17.5 5 15.4 5 13a7 7 0 0 1 14 0c0 1.6-.6 3-1.6 4.1V21" />
    <path d="M9.5 12a2 2 0 1 1 4 0M12 12v3" />
  </svg>
);

/** Feat geral -- globo, porque nao pertence a nenhuma trilha. */
export const IconeGeral = () => (
  <svg {...base} className="icone" aria-hidden>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M3.5 12h17M12 3.5c2.5 2.5 2.5 14 0 17-2.5-3-2.5-14.5 0-17z" />
  </svg>
);

/** Arquetipo -- estrela dentro de circulo, a trilha paralela. */
export const IconeArquetipo = () => (
  <svg {...base} className="icone" aria-hidden>
    <circle cx="12" cy="12" r="8.5" />
    <path d="m12 7.5 1.4 2.9 3.1.4-2.3 2.2.6 3.1-2.8-1.5-2.8 1.5.6-3.1L7.5 10.8l3.1-.4z" />
  </svg>
);

/** Engrenagem do botao de escolha agregada. */
export const IconeCog = () => (
  <svg viewBox="0 0 24 24" className="icone" aria-hidden
       fill="none" stroke="currentColor" strokeWidth={1.2}>
    <path d="M12 2.6l1.6 1.9 2.4-.7.7 2.4 2.4.8-.8 2.4 1.6 1.9-1.6 1.9.8 2.4-2.4.8-.7 2.4-2.4-.7L12 21.4l-1.6-1.9-2.4.7-.7-2.4-2.4-.8.8-2.4L4.1 12l1.6-1.9-.8-2.4 2.4-.8.7-2.4 2.4.7z" />
    <circle cx="12" cy="12" r="4.6" />
  </svg>
);

/** O escudo que emoldura a CA. */
export const IconeEscudo = () => (
  <svg viewBox="0 0 24 24" className="icone" aria-hidden
       fill="none" stroke="currentColor" strokeWidth={1.4}>
    <path d="M12 2.5 20 5v7c0 4.4-3.3 8.3-8 9.5-4.7-1.2-8-5.1-8-9.5V5z" />
  </svg>
);

/** Escolhe o icone pelo tipo de slot -- um lugar so decide. */
export function iconeDeSlot(slot: string) {
  if (slot.startsWith("ancestr") || slot === "heranca" || slot === "heritage") {
    return <IconeAncestria />;
  }
  if (slot.startsWith("background")) return <IconeBackground />;
  if (slot.startsWith("skill")) return <IconePericia />;
  if (slot.startsWith("general")) return <IconeGeral />;
  if (slot.startsWith("free_archetype") || slot.startsWith("arquetipo")) {
    return <IconeArquetipo />;
  }
  return <IconeClasse />;
}
