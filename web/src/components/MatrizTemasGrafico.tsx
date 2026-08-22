import { useEffect, useMemo, useState } from "react";
import { useStore } from "@nanostores/react";
import { cargarIndex } from "../lib/datos";
import { etiquetaTemporada, filtrarIndices, filtro$ } from "../lib/store";
import { slugificar } from "../lib/slugs";
import type { Index } from "../lib/tipos";

/** Igual que MatrizTemasEpisodios.astro (la de portada), pero reactiva al
 * store de filtros: en /explorar hay barra de filtros y este grafico tiene
 * que recalcularse contra la misma porcion de datos que el resto, nunca
 * contra el index.json completo. La version de portada no lo necesita --
 * ahi no hay filtros -- por eso sigue siendo la .astro estatica. */
export default function MatrizTemasGrafico() {
  const filtro = useStore(filtro$);
  const [index, setIndex] = useState<Index | null>(null);

  useEffect(() => {
    cargarIndex().then(setIndex);
  }, []);

  const { temasOrdenados, mencionesPorEpisodioYTema, maxMenciones, total } = useMemo(() => {
    if (!index)
      return { temasOrdenados: [] as number[], mencionesPorEpisodioYTema: new Map<string, number>(), maxMenciones: 1, total: 0 };

    const primeraAparicion = new Map<number, string>();
    for (const ep of index.eps) {
      for (const t of ep[7]) {
        if (!primeraAparicion.has(t)) primeraAparicion.set(t, ep[3]);
      }
    }
    const temasOrdenados = index.temas
      .map((_, i) => i)
      .sort((a, b) => (primeraAparicion.get(a) ?? "").localeCompare(primeraAparicion.get(b) ?? ""));

    const idxsFiltrados = filtrarIndices(index, filtro);
    const mencionesPorEpisodioYTema = new Map<string, number>();
    for (const i of idxsFiltrados) {
      const fila = index.refs[i];
      const ep = index.eps[fila[0]];
      for (const t of ep[7]) {
        const clave = `${fila[0]}|${t}`;
        mencionesPorEpisodioYTema.set(clave, (mencionesPorEpisodioYTema.get(clave) ?? 0) + 1);
      }
    }
    const maxMenciones = Math.max(1, ...mencionesPorEpisodioYTema.values());

    return { temasOrdenados, mencionesPorEpisodioYTema, maxMenciones, total: idxsFiltrados.length };
  }, [index, filtro]);

  function intensidad(n: number): number {
    return n ? Math.sqrt(n / maxMenciones) : 0;
  }

  return (
    <div className="tarjeta-grafico">
      <div className="cabecera-grafico">
        <div>
          <h2>Matriz de temas</h2>
          <p className="nota-grafico">
            {index?.temas.length ?? 0} temas × {index?.eps.length ?? 0} episodios, en orden cronológico. Filas
            ordenadas por primera aparición. {total.toLocaleString("es")} mención(es) con los filtros activos.
          </p>
        </div>
      </div>

      <div className="contenedor-grafico-scroll">
        <table style={{ borderCollapse: "collapse", fontSize: "0.7rem", tableLayout: "fixed" }}>
          <thead>
            <tr>
              <th
                style={{
                  position: "sticky",
                  left: 0,
                  background: "var(--color-fondo)",
                  textAlign: "left",
                  padding: "0.2rem 0.6rem",
                  width: "12rem",
                }}
              >
                Tema
              </th>
              {(index?.eps ?? []).map((ep) => (
                <th key={ep[0]} style={{ padding: 0, width: "0.6rem", overflow: "hidden" }} title={`${ep[2]} — ${ep[3]}`}>
                  <a
                    href={`/episodio/${ep[0]}`}
                    aria-label={ep[2]}
                    style={{
                      display: "block",
                      writingMode: "vertical-rl",
                      height: "5rem",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {ep[1] || etiquetaTemporada(ep[5], ep[1])}
                  </a>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {temasOrdenados.map((temaIdx) => (
              <tr key={temaIdx}>
                <th
                  scope="row"
                  style={{
                    position: "sticky",
                    left: 0,
                    background: "var(--color-fondo)",
                    textAlign: "left",
                    padding: "0.15rem 0.6rem",
                    fontWeight: 400,
                  }}
                >
                  <a href={`/tema/${slugificar(index!.temas[temaIdx])}`}>{index!.temas[temaIdx]}</a>
                </th>
                {(index?.eps ?? []).map((ep, epIdx) => {
                  const n = mencionesPorEpisodioYTema.get(`${epIdx}|${temaIdx}`) ?? 0;
                  const alpha = intensidad(n);
                  return (
                    <td key={ep[0]} style={{ padding: 0, width: "0.6rem", height: "0.9rem" }}>
                      {n > 0 ? (
                        <a
                          href={`/episodio/${ep[0]}`}
                          title={`${ep[2]} · ${ep[3]} · ${n} mención(es) de «${index!.temas[temaIdx]}»`}
                          style={{
                            display: "block",
                            width: "100%",
                            height: "0.9rem",
                            background: `color-mix(in oklch, var(--color-acento) ${Math.round(alpha * 100)}%, var(--color-superficie-alta))`,
                          }}
                        ></a>
                      ) : (
                        <span style={{ display: "block", width: "100%", height: "0.9rem" }}></span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
