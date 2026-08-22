import { useEffect, useMemo, useRef, useState } from "react";
import { useStore } from "@nanostores/react";
import {
  actualizarFiltro,
  alternarValor,
  conectarUrl,
  etiquetaTemporada,
  filtro$,
  filtrarIndices,
  hayFiltrosActivos,
  limpiarFiltro,
  normalizarBusqueda,
} from "../lib/store";
import { cargarIndex } from "../lib/datos";
import type { Index } from "../lib/tipos";

type CampoMulti = "temporada" | "tema" | "tipo" | "alcance" | "funcion" | "confianza";

// Orden pedido: Temporada, Episodio, Tema, Autor, Tipo, Alcance, Función,
// Confianza. Episodio y Autor son de seleccion unica con buscador (1.160
// autorias / 118 episodios no caben como checkboxes); el resto son
// multiseleccion de vocabulario cerrado y pequeño.
const ORDEN: ({ tipo: "multi"; campo: CampoMulti; etiqueta: string } | { tipo: "combo"; campo: "episodio" | "autor"; etiqueta: string })[] = [
  { tipo: "multi", campo: "temporada", etiqueta: "Temporada" },
  { tipo: "combo", campo: "episodio", etiqueta: "Episodio" },
  { tipo: "multi", campo: "tema", etiqueta: "Tema" },
  { tipo: "combo", campo: "autor", etiqueta: "Autor" },
  { tipo: "multi", campo: "tipo", etiqueta: "Tipo" },
  { tipo: "multi", campo: "alcance", etiqueta: "Alcance" },
  { tipo: "multi", campo: "funcion", etiqueta: "Función" },
  { tipo: "multi", campo: "confianza", etiqueta: "Confianza" },
];

/** Cuenta en cuántos episodios distintos aparece cada tema, recorriendo el
 * conjunto de todos los episodios disponibles (no las menciones filtradas). */
function episodiosPorTema(index: Index): Map<string, number> {
  const conteo = new Map<string, number>();
  for (const ep of index.eps) {
    for (const temaIdx of ep[7]) {
      const tema = index.temas[temaIdx];
      conteo.set(tema, (conteo.get(tema) ?? 0) + 1);
    }
  }
  return conteo;
}

/** Cuenta en cuántos episodios distintos aparece cada tipo, recorriendo el
 * conjunto de todos los episodios disponibles (no las menciones filtradas). */
function episodiosPorTipo(index: Index): Map<string, number> {
  const vistos = new Map<string, Set<number>>();
  for (const fila of index.refs) {
    const [epIdx, , , , tipIdx] = fila;
    const tipo = index.tip[tipIdx];
    if (!tipo) continue;
    if (!vistos.has(tipo)) vistos.set(tipo, new Set());
    vistos.get(tipo)!.add(epIdx);
  }
  const conteo = new Map<string, number>();
  for (const [tipo, epIdxs] of vistos) conteo.set(tipo, epIdxs.size);
  return conteo;
}

function ordenarPorPresencia(valores: string[], conteo: Map<string, number>): string[] {
  return [...valores].sort((a, b) => (conteo.get(b) ?? 0) - (conteo.get(a) ?? 0) || a.localeCompare(b, "es"));
}

/** Menciones por autoría, para ordenar las sugerencias del buscador de
 * autoría por relevancia en vez de alfabéticamente sobre 1.160 nombres. */
function mencionesPorAutor(index: Index): Map<string, number> {
  const conteo = new Map<string, number>();
  for (const fila of index.refs) {
    const autor = index.aut[fila[1]];
    if (!autor || autor === "sin determinar") continue;
    conteo.set(autor, (conteo.get(autor) ?? 0) + 1);
  }
  return conteo;
}

function opcionesDe(index: Index, campo: CampoMulti): string[] {
  if (campo === "temporada") return ["1", "2", "3", "4", "5", "Glosas", "Especial"];
  if (campo === "tema") return ordenarPorPresencia(index.temas, episodiosPorTema(index));
  if (campo === "tipo") return ordenarPorPresencia(index.tip.filter(Boolean), episodiosPorTipo(index));
  const tabla: Record<string, string[]> = {
    funcion: index.fun,
    alcance: index.alc,
    confianza: index.con,
  };
  return [...tabla[campo]].filter(Boolean).sort((a, b) => a.localeCompare(b, "es"));
}

export default function BarraFiltros() {
  const filtro = useStore(filtro$);
  const [index, setIndex] = useState<Index | null>(null);
  const [facetaAbierta, setFacetaAbierta] = useState<string | null>(null);
  const [consultaAutor, setConsultaAutor] = useState("");
  const [consultaEpisodio, setConsultaEpisodio] = useState("");
  // para devolver el foco al boton que abrio el panel, al cerrarlo con Escape
  // o haciendo clic fuera -- si no, un teclado se queda sin saber donde esta
  const botonesRef = useRef<Record<string, HTMLButtonElement | null>>({});
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    conectarUrl();
    cargarIndex().then(setIndex);
  }, []);

  function cerrarFaceta() {
    if (facetaAbierta) botonesRef.current[facetaAbierta]?.focus();
    setFacetaAbierta(null);
  }

  useEffect(() => {
    if (!facetaAbierta) return;
    function alTeclado(e: KeyboardEvent) {
      if (e.key === "Escape") cerrarFaceta();
    }
    function alClicFuera(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) setFacetaAbierta(null);
    }
    document.addEventListener("keydown", alTeclado);
    document.addEventListener("mousedown", alClicFuera);
    return () => {
      document.removeEventListener("keydown", alTeclado);
      document.removeEventListener("mousedown", alClicFuera);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [facetaAbierta]);

  const total = index?.refs.length ?? 0;
  const activos = index ? filtrarIndices(index, filtro).length : total;

  const sugerenciasAutor = useMemo(() => {
    if (!index) return [];
    const conteo = mencionesPorAutor(index);
    const q = normalizarBusqueda(consultaAutor);
    const candidatos = q ? [...conteo.keys()].filter((a) => normalizarBusqueda(a).includes(q)) : [...conteo.keys()];
    return candidatos.sort((a, b) => conteo.get(b)! - conteo.get(a)!).slice(0, 12);
  }, [index, consultaAutor]);

  // Si hay temporada(s) elegidas, acota la lista de episodios a esas
  // temporadas: es justo el flujo que hace falta para ver "todas las
  // menciones" en /explorar (temporada + episodio).
  const sugerenciasEpisodio = useMemo(() => {
    if (!index) return [];
    const temporadaSet = new Set(filtro.temporada);
    const q = normalizarBusqueda(consultaEpisodio);
    let candidatos = index.eps;
    if (temporadaSet.size) {
      candidatos = candidatos.filter((ep) => temporadaSet.has(etiquetaTemporada(ep[5], ep[1])));
    }
    if (q) {
      candidatos = candidatos.filter((ep) => normalizarBusqueda(ep[2]).includes(q) || normalizarBusqueda(ep[1]).includes(q));
    }
    return [...candidatos].sort((a, b) => b[3].localeCompare(a[3])).slice(0, 30);
  }, [index, consultaEpisodio, filtro.temporada]);

  function elegirAutor(autor: string | null) {
    actualizarFiltro({ autor });
    setConsultaAutor("");
    if (facetaAbierta === "autor") botonesRef.current.autor?.focus();
    setFacetaAbierta(null);
  }

  function elegirEpisodio(episodio: string | null) {
    actualizarFiltro({ episodio });
    setConsultaEpisodio("");
    if (facetaAbierta === "episodio") botonesRef.current.episodio?.focus();
    setFacetaAbierta(null);
  }

  const episodioActual = filtro.episodio ? index?.eps.find((e) => e[0] === filtro.episodio) : null;

  return (
    <div className="barra-filtros">
      <div className="envoltura" style={{ display: "flex", flexDirection: "column", gap: "0.6rem", padding: "0.75rem 1.25rem" }}>
        <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", flexWrap: "wrap" }}>
          <input
            type="search"
            aria-label="Buscar en autoras, obras, menciones y episodios"
            placeholder="Buscar…"
            value={filtro.q}
            onChange={(e) => actualizarFiltro({ q: e.target.value })}
            style={{
              flex: "1 1 16rem",
              padding: "0.5rem 0.75rem",
              borderRadius: "var(--radio)",
              border: "1px solid var(--color-borde)",
              background: "var(--color-superficie)",
              color: "var(--color-texto)",
              font: "inherit",
            }}
          />
          {index && (
            <span aria-live="polite" style={{ color: "var(--color-texto-tenue)", fontSize: "0.9em", whiteSpace: "nowrap" }}>
              {`${activos.toLocaleString("es")} de ${total.toLocaleString("es")} menciones`}
            </span>
          )}
          {hayFiltrosActivos(filtro) && (
            <button className="faceta" onClick={limpiarFiltro} type="button">
              Limpiar filtros
            </button>
          )}
        </div>

        <img
          src="/images/marca/filtros-letras.svg"
          alt="Filtros"
          style={{ height: "1.1rem", width: "auto", display: "block", alignSelf: "flex-start", marginTop: "0.5rem" }}
        />

        <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
          {ORDEN.map((entrada) => {
            if (entrada.tipo === "combo") {
              const esAutor = entrada.campo === "autor";
              const valor = esAutor ? filtro.autor : filtro.episodio;
              const etiquetaValor = esAutor ? valor : episodioActual ? `${episodioActual[1] || episodioActual[3]} — ${episodioActual[2]}` : null;
              const consulta = esAutor ? consultaAutor : consultaEpisodio;
              const setConsulta = esAutor ? setConsultaAutor : setConsultaEpisodio;
              const sugerencias = esAutor ? sugerenciasAutor : sugerenciasEpisodio;
              const elegir = esAutor ? elegirAutor : elegirEpisodio;

              return (
                <div key={entrada.campo} style={{ position: "relative" }}>
                  <button
                    ref={(el) => { botonesRef.current[entrada.campo] = el; }}
                    type="button"
                    className="faceta"
                    aria-expanded={facetaAbierta === entrada.campo}
                    aria-pressed={valor != null}
                    onClick={() => setFacetaAbierta(facetaAbierta === entrada.campo ? null : entrada.campo)}
                  >
                    {etiquetaValor ? `${entrada.etiqueta}: ${etiquetaValor}` : entrada.etiqueta}
                  </button>
                  {facetaAbierta === entrada.campo && index && (
                    <div
                      ref={panelRef}
                      role="group"
                      aria-label={entrada.etiqueta}
                      style={{
                        position: "absolute",
                        top: "calc(100% + 0.3rem)",
                        left: 0,
                        background: "var(--color-superficie-alta)",
                        border: "1px solid var(--color-borde)",
                        borderRadius: "var(--radio)",
                        padding: "0.5rem",
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.3rem",
                        minWidth: "18rem",
                        zIndex: 50,
                      }}
                    >
                      <input
                        type="search"
                        autoFocus
                        aria-label={`Buscar ${entrada.etiqueta.toLowerCase()}`}
                        placeholder="Escribe para filtrar…"
                        value={consulta}
                        onChange={(e) => setConsulta(e.target.value)}
                        style={{
                          padding: "0.4rem 0.6rem",
                          borderRadius: "var(--radio)",
                          border: "1px solid var(--color-borde)",
                          background: "var(--color-superficie)",
                          color: "var(--color-texto)",
                          font: "inherit",
                          fontSize: "0.9em",
                        }}
                      />
                      {valor != null && (
                        <button type="button" className="faceta" onClick={() => elegir(null)}>
                          Quitar «{etiquetaValor}»
                        </button>
                      )}
                      <div style={{ display: "flex", flexDirection: "column", gap: "0.1rem", maxHeight: "16rem", overflowY: "auto" }}>
                        {esAutor
                          ? (sugerencias as string[]).map((autor) => (
                              <button
                                key={autor}
                                type="button"
                                onClick={() => elegir(autor)}
                                className="opcion-combo"
                                data-activa={autor === filtro.autor}
                              >
                                {autor}
                              </button>
                            ))
                          : (sugerencias as Index["eps"]).map((ep) => (
                              <button
                                key={ep[0]}
                                type="button"
                                onClick={() => elegir(ep[0])}
                                className="opcion-combo"
                                data-activa={ep[0] === filtro.episodio}
                              >
                                {ep[1] || ep[3]} — {ep[2]}
                              </button>
                            ))}
                        {sugerencias.length === 0 && (
                          <p style={{ margin: 0, fontSize: "0.85em", color: "var(--color-texto-tenue)" }}>Sin resultados.</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            }

            const { campo, etiqueta } = entrada;
            return (
              <div key={campo} style={{ position: "relative" }}>
                <button
                  ref={(el) => { botonesRef.current[campo] = el; }}
                  type="button"
                  className="faceta"
                  aria-expanded={facetaAbierta === campo}
                  onClick={() => setFacetaAbierta(facetaAbierta === campo ? null : campo)}
                >
                  {etiqueta}
                  {filtro[campo].length > 0 ? ` (${filtro[campo].length})` : ""}
                </button>
                {facetaAbierta === campo && index && (
                  <div
                    ref={panelRef}
                    role="group"
                    aria-label={etiqueta}
                    style={{
                      position: "absolute",
                      top: "calc(100% + 0.3rem)",
                      left: 0,
                      background: "var(--color-superficie-alta)",
                      border: "1px solid var(--color-borde)",
                      borderRadius: "var(--radio)",
                      padding: "0.5rem",
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.2rem",
                      maxHeight: "18rem",
                      overflowY: "auto",
                      minWidth: "14rem",
                      zIndex: 50,
                    }}
                  >
                    {opcionesDe(index, campo).map((valor) => (
                      <label key={valor} style={{ display: "flex", gap: "0.4rem", alignItems: "center", fontSize: "0.9em" }}>
                        <input type="checkbox" checked={filtro[campo].includes(valor)} onChange={() => alternarValor(campo, valor)} />
                        {valor}
                      </label>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {hayFiltrosActivos(filtro) && (
          <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
            {filtro.autor && (
              <span className="chip">
                Autor: {filtro.autor}
                <button type="button" onClick={() => elegirAutor(null)} aria-label={`Quitar filtro Autor: ${filtro.autor}`}>
                  ×
                </button>
              </span>
            )}
            {episodioActual && (
              <span className="chip">
                Episodio: {episodioActual[2]}
                <button type="button" onClick={() => elegirEpisodio(null)} aria-label={`Quitar filtro Episodio: ${episodioActual[2]}`}>
                  ×
                </button>
              </span>
            )}
            {ORDEN.filter((e): e is Extract<typeof e, { tipo: "multi" }> => e.tipo === "multi").flatMap(({ campo, etiqueta }) =>
              filtro[campo].map((valor) => (
                <span className="chip" key={`${campo}-${valor}`}>
                  {etiqueta}: {valor}
                  <button type="button" onClick={() => alternarValor(campo, valor)} aria-label={`Quitar filtro ${etiqueta}: ${valor}`}>
                    ×
                  </button>
                </span>
              )),
            )}
            {filtro.q && (
              <span className="chip">
                “{filtro.q}”
                <button type="button" onClick={() => actualizarFiltro({ q: "" })} aria-label="Quitar la búsqueda">
                  ×
                </button>
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
