import { useEffect, useMemo, useRef, useState } from "react";
import * as Plot from "@observablehq/plot";
import { useStore } from "@nanostores/react";
import { etiquetaTemporada, filtrarIndices, filtro$ } from "../lib/store";
import { cargarIndex } from "../lib/datos";
import { slugObra } from "../lib/slugs";
import { comoTablaPorDefecto } from "../lib/movil";
import type { Index } from "../lib/tipos";

const MAX_TIPOS = 5; // + "otros" = 6, el maximo de colores categoricos que permite el plan
const PALETA_REALES = [
  "var(--color-cat-1)", "var(--color-cat-2)", "var(--color-cat-3)", "var(--color-cat-4)", "var(--color-cat-5)",
];
const COLOR_OTROS = "var(--color-cat-otros)";
const TEMPORADAS = ["1", "2", "3", "4", "5", "6", "Glosas", "Especial"];
const NOMBRE_TEMPORADA: Record<string, string> = {
  "1": "Temporada 1", "2": "Temporada 2", "3": "Temporada 3", "4": "Temporada 4", "5": "Temporada 5",
  "6": "Temporada 6", Glosas: "Las Glosas", Especial: "Especiales",
};

interface Segmento {
  temporada: string;
  tipo: string;
  n: number;
}
interface ObraDelSegmento {
  autor: string;
  obra: string;
  tipoReal: string;
  n: number;
}

export default function AreaPorTipo() {
  const filtro = useStore(filtro$);
  const [index, setIndex] = useState<Index | null>(null);
  const [comoTabla, setComoTabla] = useState(false);
  const [seleccion, setSeleccion] = useState<{ temporada: string; tipo: string } | null>(null);
  const contenedorRef = useRef<HTMLDivElement>(null);
  const dialogoRef = useRef<HTMLDivElement>(null);

  // Escape cierra, el foco entra en el dialogo al abrirse y queda atrapado
  // ahi mientras esta abierto (patron estandar de dialogo modal accesible).
  useEffect(() => {
    if (!seleccion) return;
    const nodo = dialogoRef.current;
    const foco = nodo?.querySelector<HTMLElement>("button, a[href]");
    foco?.focus();

    function alTeclado(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setSeleccion(null);
        return;
      }
      if (e.key !== "Tab" || !nodo) return;
      const focosables = Array.from(nodo.querySelectorAll<HTMLElement>("button, a[href]"));
      if (focosables.length === 0) return;
      const primero = focosables[0];
      const ultimo = focosables[focosables.length - 1];
      if (e.shiftKey && document.activeElement === primero) {
        e.preventDefault();
        ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault();
        primero.focus();
      }
    }
    document.addEventListener("keydown", alTeclado);
    return () => document.removeEventListener("keydown", alTeclado);
  }, [seleccion]);

  useEffect(() => {
    cargarIndex().then(setIndex);
  }, []);

  // se calcula en cliente, tras montar: si se metiera en el useState inicial
  // (window.matchMedia) el servidor renderizaria "false" (SSR no ve window) y
  // el cliente "true" en movil, un mismatch que React rompe con el error 418
  useEffect(() => {
    if (comoTablaPorDefecto()) setComoTabla(true);
  }, []);

  // Color fijo por tipo, calculado sobre TODO el corpus (no el subconjunto
  // filtrado): asi ningun tipo cambia de color al filtrar, solo puede dejar
  // de tener barra si su conteo en el filtro actual es cero. Los 5 tipos mas
  // citados en el conjunto completo son los que tienen color propio; el
  // resto siempre cae en "otros".
  const { tiposReales, topSet, colorPorTipo } = useMemo(() => {
    if (!index) return { tiposReales: [] as string[], topSet: new Set<string>(), colorPorTipo: new Map<string, string>() };
    const totalGlobal = new Map<string, number>();
    for (const fila of index.refs) {
      const tipo = index.tip[fila[4]];
      if (!tipo) continue;
      totalGlobal.set(tipo, (totalGlobal.get(tipo) ?? 0) + 1);
    }
    const tiposReales = [...totalGlobal.entries()].sort((a, b) => b[1] - a[1]).slice(0, MAX_TIPOS).map(([t]) => t);
    const colorPorTipo = new Map<string, string>(tiposReales.map((t, i) => [t, PALETA_REALES[i]]));
    return { tiposReales, topSet: new Set(tiposReales), colorPorTipo };
  }, [index]);

  const { segmentos, tiposOrdenados, obrasPorSegmento, total } = useMemo(() => {
    if (!index)
      return { segmentos: [] as Segmento[], tiposOrdenados: [] as string[], obrasPorSegmento: new Map<string, ObraDelSegmento[]>(), total: 0 };

    const idxsFiltrados = filtrarIndices(index, filtro);

    const totalPorTipo = new Map<string, number>();
    for (const i of idxsFiltrados) {
      const tipo = index.tip[index.refs[i][4]];
      if (!tipo) continue;
      totalPorTipo.set(tipo, (totalPorTipo.get(tipo) ?? 0) + 1);
    }
    const presentes = tiposReales.filter((t) => (totalPorTipo.get(t) ?? 0) > 0);
    const hayOtros = [...totalPorTipo.keys()].some((t) => !topSet.has(t));
    const tiposOrdenados = hayOtros ? [...presentes, "otros"] : presentes;

    const conteoSegmento = new Map<string, number>(); // `${temporada}|${tipoAgrupado}` -> n
    const obrasPorSegmento = new Map<string, Map<string, ObraDelSegmento>>(); // `${temporada}|${tipoAgrupado}` -> autor||obra -> detalle

    for (const i of idxsFiltrados) {
      const fila = index.refs[i];
      const ep = index.eps[fila[0]];
      const temporada = etiquetaTemporada(ep[5], ep[1]);
      const tipoReal = index.tip[fila[4]];
      if (!tipoReal) continue;
      const tipoAgrupado = topSet.has(tipoReal) ? tipoReal : "otros";
      const claveSeg = `${temporada}|${tipoAgrupado}`;
      conteoSegmento.set(claveSeg, (conteoSegmento.get(claveSeg) ?? 0) + 1);

      const autor = index.aut[fila[1]];
      const obra = index.obr[fila[2]];
      if (!autor || !obra) continue;
      if (!obrasPorSegmento.has(claveSeg)) obrasPorSegmento.set(claveSeg, new Map());
      const mapaObras = obrasPorSegmento.get(claveSeg)!;
      const claveObra = `${autor}||${obra}`;
      const actual = mapaObras.get(claveObra) ?? { autor, obra, tipoReal, n: 0 };
      actual.n += 1;
      mapaObras.set(claveObra, actual);
    }

    const segmentos: Segmento[] = [];
    for (const [clave, n] of conteoSegmento) {
      const [temporada, tipo] = clave.split("|");
      segmentos.push({ temporada, tipo, n });
    }

    const obrasPorSegmentoOrdenadas = new Map<string, ObraDelSegmento[]>();
    for (const [clave, mapaObras] of obrasPorSegmento) {
      obrasPorSegmentoOrdenadas.set(clave, [...mapaObras.values()].sort((a, b) => b.n - a.n));
    }

    return { segmentos, tiposOrdenados, obrasPorSegmento: obrasPorSegmentoOrdenadas, total: idxsFiltrados.length };
  }, [index, filtro, tiposReales, topSet]);

  useEffect(() => {
    if (!index || !contenedorRef.current || comoTabla) return;
    const contenedor = contenedorRef.current;
    contenedor.replaceChildren();

    if (segmentos.length === 0) return;

    const figura = Plot.plot({
      width: contenedor.clientWidth || 900,
      height: 420,
      marginLeft: 48,
      marginBottom: 40,
      style: { background: "transparent", color: "var(--color-texto)" },
      x: { domain: TEMPORADAS.map((t) => NOMBRE_TEMPORADA[t]), label: null },
      y: { label: "menciones", grid: true },
      color: {
        domain: tiposOrdenados,
        range: tiposOrdenados.map((t) => (t === "otros" ? COLOR_OTROS : colorPorTipo.get(t)!)),
        legend: true,
      },
      marks: [
        Plot.barY(segmentos, {
          x: (d: Segmento) => NOMBRE_TEMPORADA[d.temporada],
          y: "n",
          fill: "tipo",
          order: tiposOrdenados,
          title: (d: Segmento) => `${NOMBRE_TEMPORADA[d.temporada]} · ${d.tipo}: ${d.n} mención(es) — clic para ver la lista`,
        }),
        Plot.ruleY([0], { ariaHidden: "true" }),
      ],
    });

    // "aria-label=bar" lo lleva el <g> que envuelve todas las barras, no cada
    // rect individual; sus hijos siguen el mismo orden que "segmentos".
    const grupoBarras = figura.querySelector("[aria-label='bar']");
    if (grupoBarras) {
      Array.from(grupoBarras.children).forEach((nodo, i) => {
        const seg = segmentos[i];
        if (!seg) return;
        (nodo as SVGElement).style.cursor = "pointer";
        nodo.addEventListener("click", () => setSeleccion({ temporada: seg.temporada, tipo: seg.tipo }));
      });
    }

    contenedor.appendChild(figura);
    return () => figura.remove();
  }, [segmentos, tiposOrdenados, comoTabla, index, colorPorTipo]);

  const claveSeleccion = seleccion ? `${seleccion.temporada}|${seleccion.tipo}` : null;
  const obrasSeleccion = claveSeleccion ? obrasPorSegmento.get(claveSeleccion) ?? [] : [];

  return (
    <div className="tarjeta-grafico">
      <div className="cabecera-grafico">
        <div>
          <h2>Área por tipo</h2>
          <p className="nota-grafico">
            Menciones por tipo de obra, una barra por temporada. Clic en un tramo de color: lista de obras de ese
            tipo en esa temporada. {total.toLocaleString("es")} mención(es) con los filtros activos.
          </p>
        </div>
        <button type="button" className="faceta" onClick={() => setComoTabla((v) => !v)}>
          {comoTabla ? "Ver gráfico" : "Ver como tabla"}
        </button>
      </div>

      {!comoTabla ? (
        segmentos.length === 0 ? (
          <p className="nota-grafico">Sin menciones que coincidan con los filtros activos.</p>
        ) : (
          <div ref={contenedorRef} className="contenedor-grafico-scroll" />
        )
      ) : (
        <div className="contenedor-tabla-scroll">
          <table className="tabla-gemela">
            <thead>
              <tr>
                <th>Temporada</th>
                <th>Tipo</th>
                <th>Menciones</th>
              </tr>
            </thead>
            <tbody>
              {segmentos
                .sort((a, b) => TEMPORADAS.indexOf(a.temporada) - TEMPORADAS.indexOf(b.temporada) || b.n - a.n)
                .map((s, i) => (
                  <tr key={i}>
                    <td>{NOMBRE_TEMPORADA[s.temporada]}</td>
                    <td>
                      <button type="button" className="enlace-tabla" onClick={() => setSeleccion({ temporada: s.temporada, tipo: s.tipo })}>
                        {s.tipo}
                      </button>
                    </td>
                    <td>{s.n}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}

      {seleccion && (
        <div
          ref={dialogoRef}
          role="dialog"
          aria-modal="true"
          aria-label={`Obras de tipo ${seleccion.tipo} en ${NOMBRE_TEMPORADA[seleccion.temporada]}`}
          style={{
            position: "fixed",
            inset: 0,
            background: "color-mix(in oklch, black 55%, transparent)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
            padding: "1.5rem",
          }}
          onClick={(e) => e.target === e.currentTarget && setSeleccion(null)}
        >
          <div
            style={{
              background: "var(--color-superficie)",
              border: "1px solid var(--color-borde)",
              borderRadius: "var(--radio)",
              padding: "1.25rem",
              maxWidth: "32rem",
              width: "100%",
              maxHeight: "80vh",
              overflowY: "auto",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem" }}>
              <h3 style={{ margin: 0 }}>
                {seleccion.tipo} · {NOMBRE_TEMPORADA[seleccion.temporada]}
              </h3>
              <button type="button" className="faceta" onClick={() => setSeleccion(null)} aria-label="Cerrar">
                Cerrar
              </button>
            </div>
            <p className="nota-grafico">{obrasSeleccion.length} obra(s) distinta(s)</p>
            <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {obrasSeleccion.map((o) => (
                <li key={`${o.autor}||${o.obra}`}>
                  <a href={`/obra/${slugObra(o.autor, o.obra)}`}>{o.obra}</a>
                  <span className="nota-grafico"> — {o.autor}{seleccion.tipo === "otros" && ` (${o.tipoReal})`} · {o.n} mención(es)</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
