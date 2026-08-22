// Funciones de slug puras (sin fs), compartidas entre el codigo de cliente
// (componentes React) y el frontmatter de build (paginas .astro).

export function slugificar(texto: string): string {
  return texto
    .toLocaleLowerCase("es")
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** slug de /obra/[slug]: autor+obra en un solo segmento, porque el titulo solo
 * no es unico (hay homonimos reales, p. ej. "Historia natural" de Yuszczuk y
 * de Plinio el Viejo). */
export function slugObra(autor: string, obra: string): string {
  return `${slugificar(autor)}--${slugificar(obra)}`;
}
