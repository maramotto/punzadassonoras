import { useEffect, useMemo, useRef, useState } from "react";
import * as Plot from "@observablehq/plot";
import { useStore } from "@nanostores/react";
import { actualizarFiltro, filtrarIndices, filtro$ } from "../lib/store";
import { cargarIndex } from "../lib/datos";
import { slugificar } from "../lib/slugs";
import type { Index } from "../lib/tipos";

const TOP_N = 20;

interface FilaAutor {
  autor: string;
  menciones: number;
  obras: number;
  episodios: number;
}

export default function RankingAutores() {
  const filtro = useStore(filtro$);
  const [index, setIndex] = useState<Index | null>(null);
  const [comoTabla, setComoTabla] = useState(false);
  const contenedorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    cargarIndex().then(setIndex);
  }, []);

  const { top, totalAutorias, total } = useMemo(() => {
    if (!index) return { top: [] as FilaAutor[], totalAutorias: 0, total: 0 };

    const idxsFiltrados = filtrarIndices(index, filtro);
    const porAutor = new Map<string, { menciones: number; obras: Set<string>; episodios: Set<number> }>();
    for (const i of idxsFiltrados) {
      const fila = index.refs[i];
      const autor = index.aut[fila[1]];
      if (!autor || autor === "sin determinar") continue;
      const obra = index.obr[fila[2]];
      let a = porAutor.get(autor);
      if (!a) {
        a = { menciones: 0, obras: new Set(), episodios: new Set() };
        porAutor.set(autor, a);
      }
      a.menciones++;
      if (obra) a.obras.add(obra);
      a.episodios.add(fila[0]);
    }

    const todas: FilaAutor[] = [...porAutor.entries()]
      .map(([autor, a]) => ({ autor, menciones: a.menciones, obras: a.obras.size, episodios: a.episodios.size }))
      .sort((a, b) => b.menciones - a.menciones);

    return { top: todas.slice(0, TOP_N), totalAutorias: todas.length, total: idxsFiltrados.length };
  }, [index, filtro]);

  useEffect(() => {
    if (!index || !contenedorRef.current || comoTabla || top.length === 0) return;
    const contenedor = contenedorRef.current;
    contenedor.replaceChildren();

    const figura = Plot.plot({
      width: Math.max(600, contenedor.clientWidth || 600),
      height: top.length * 24 + 20,
      marginLeft: 190,
      marginBottom: 30,
      style: { background: "transparent", color: "var(--color-texto)" },
      x: { label: "menciones", grid: true },
      y: { domain: top.map((f) => f.autor), label: null },
      marks: [
        Plot.barX(top, {
          x: "menciones",
          y: "autor",
          fill: "var(--color-acento)",
          sort: { y: "-x" },
          title: (d: FilaAutor) => `${d.autor} · ${d.menciones} mención(es) · ${d.obras} obra(s) · ${d.episodios} episodio(s) — clic para filtrar`,
        }),
        Plot.ruleX([0]),
      ],
    });

    // "aria-label=bar" lo lleva el <g> que envuelve todas las barras, no cada
    // rect individual; sus hijos siguen el mismo orden que "top" al no haber
    // pasado "sort" como mark option aparte del propio orden de los datos.
    const grupoBarras = figura.querySelector("[aria-label='bar']");
    if (grupoBarras) {
      Array.from(grupoBarras.children).forEach((nodo, i) => {
        const fila = top[i];
        if (!fila) return;
        (nodo as SVGElement).style.cursor = "pointer";
        nodo.addEventListener("click", () => actualizarFiltro({ autor: fila.autor }));
      });
    }

    contenedor.appendChild(figura);
    return () => figura.remove();
  }, [top, comoTabla, index]);

  return (
    <div className="tarjeta-grafico">
      <div className="cabecera-grafico">
        <div>
          <h3>Ranking de autorías</h3>
          <p className="nota-grafico">
            Las {TOP_N} autorías más citadas, de {totalAutorias.toLocaleString("es")} con los filtros activos ({total.toLocaleString("es")}{" "}
            mención(es)). Clic en una barra: filtra por esa autoría.
          </p>
        </div>
        <button type="button" className="faceta" onClick={() => setComoTabla((v) => !v)}>
          {comoTabla ? "Ver gráfico" : "Ver como tabla"}
        </button>
      </div>

      {!comoTabla ? (
        top.length === 0 ? (
          <p className="nota-grafico">Sin autorías que coincidan con los filtros activos.</p>
        ) : (
          <div ref={contenedorRef} className="contenedor-grafico-scroll" />
        )
      ) : (
        <div className="contenedor-tabla-scroll">
          <table className="tabla-gemela">
            <thead>
              <tr>
                <th>Autoría</th>
                <th>Menciones</th>
                <th>Obras</th>
                <th>Episodios</th>
              </tr>
            </thead>
            <tbody>
              {top.map((f) => (
                <tr key={f.autor}>
                  <td>
                    <a className="enlace-tabla" href={`/autor/${slugificar(f.autor)}`}>
                      {f.autor}
                    </a>
                  </td>
                  <td>{f.menciones}</td>
                  <td>{f.obras}</td>
                  <td>{f.episodios}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
