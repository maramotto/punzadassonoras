import { useEffect, useMemo, useRef, useState } from "react";
import * as Plot from "@observablehq/plot";
import { useStore } from "@nanostores/react";
import { actualizarFiltro, filtrarIndices, filtro$ } from "../lib/store";
import { cargarIndex, resolverColorFinal } from "../lib/datos";
import type { Index } from "../lib/tipos";

const TOP_N = 24;

interface Celda {
  autor: string;
  epIdx: number;
  fecha: Date;
  episodioTitulo: string;
  episodioId: string;
  menciones: number;
}

export default function MatrizAutorEpisodio() {
  const filtro = useStore(filtro$);
  const [index, setIndex] = useState<Index | null>(null);
  const [comoTabla, setComoTabla] = useState(false);
  const contenedorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    cargarIndex().then(setIndex);
  }, []);

  const { celdas, autoresOrdenados, total } = useMemo(() => {
    if (!index) return { celdas: [] as Celda[], autoresOrdenados: [] as string[], total: 0 };

    const idxsFiltrados = filtrarIndices(index, filtro);

    const totalPorAutor = new Map<string, number>();
    for (const i of idxsFiltrados) {
      const autor = index.aut[index.refs[i][1]];
      if (!autor || autor === "sin determinar") continue;
      totalPorAutor.set(autor, (totalPorAutor.get(autor) ?? 0) + 1);
    }
    const top = [...totalPorAutor.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, TOP_N)
      .map(([autor]) => autor);
    const topSet = new Set(top);

    const conteo = new Map<string, number>(); // `${autor}|${epIdx}` -> n
    for (const i of idxsFiltrados) {
      const fila = index.refs[i];
      const autor = index.aut[fila[1]];
      if (!topSet.has(autor)) continue;
      const clave = `${autor}|${fila[0]}`;
      conteo.set(clave, (conteo.get(clave) ?? 0) + 1);
    }

    const salida: Celda[] = [];
    for (const [clave, n] of conteo) {
      const [autor, epIdxStr] = clave.split("|");
      const epIdx = Number(epIdxStr);
      const ep = index.eps[epIdx];
      salida.push({ autor, epIdx, fecha: new Date(ep[3]), episodioTitulo: ep[2], episodioId: ep[0], menciones: n });
    }
    return { celdas: salida, autoresOrdenados: top, total: idxsFiltrados.length };
  }, [index, filtro]);

  useEffect(() => {
    if (!index || !contenedorRef.current || comoTabla || celdas.length === 0) return;
    const contenedor = contenedorRef.current;
    contenedor.replaceChildren();

    const figura = Plot.plot({
      width: Math.max(900, contenedor.clientWidth || 900),
      height: 560,
      marginLeft: 190,
      marginBottom: 10,
      padding: 0,
      style: { background: "transparent", color: "var(--color-texto)", fontSize: "10px" },
      x: { axis: null, domain: index.eps.map((_, i) => i) },
      y: { domain: autoresOrdenados, label: null },
      color: {
        type: "sqrt",
        range: [resolverColorFinal("var(--color-secuencial-1)"), resolverColorFinal("var(--color-secuencial-5)")],
        interpolate: "hcl",
        label: "menciones",
        legend: true,
      },
      marks: [
        Plot.cell(celdas, {
          x: "epIdx",
          y: "autor",
          fill: "menciones",
          inset: 0.5,
          title: (d: Celda) => `${d.autor}\n${d.episodioTitulo} (${d.fecha.toISOString().slice(0, 10)})\n${d.menciones} mención(es)`,
        }),
      ],
    });

    // "aria-label=cell" lo lleva el <g> que envuelve todas las celdas, no
    // cada rect individual; sus hijos siguen el mismo orden que "celdas"
    // porque no se pasa ninguna opcion de "sort" al mark.
    const grupoCeldas = figura.querySelector("[aria-label='cell']");
    if (grupoCeldas) {
      Array.from(grupoCeldas.children).forEach((nodo, i) => {
        const celda = celdas[i];
        if (!celda) return;
        (nodo as SVGElement).style.cursor = "pointer";
        nodo.addEventListener("click", () => {
          actualizarFiltro({ autor: celda.autor, episodio: celda.episodioId });
        });
      });
    }

    contenedor.appendChild(figura);
    return () => figura.remove();
  }, [celdas, autoresOrdenados, comoTabla, index]);

  return (
    <div className="tarjeta-grafico">
      <div className="cabecera-grafico">
        <div>
          <h2>Matriz de autoría</h2>
          <p className="nota-grafico">
            Las {TOP_N} autorías más citadas × {index?.eps.length ?? 0} episodios. Intensidad en escala raíz.
            Clic en una celda: filtra por esa autoría en ese episodio. {total.toLocaleString("es")} mención(es) con
            los filtros activos.
          </p>
        </div>
        <button type="button" className="faceta" onClick={() => setComoTabla((v) => !v)}>
          {comoTabla ? "Ver matriz" : "Ver como tabla"}
        </button>
      </div>

      {!comoTabla ? (
        celdas.length === 0 ? (
          <p className="nota-grafico">Sin menciones que coincidan con los filtros activos.</p>
        ) : (
          <div ref={contenedorRef} className="contenedor-grafico-scroll" />
        )
      ) : (
        <div className="contenedor-tabla-scroll">
          <table className="tabla-gemela">
            <thead>
              <tr>
                <th>Autoría</th>
                <th>Episodio</th>
                <th>Fecha</th>
                <th>Menciones</th>
              </tr>
            </thead>
            <tbody>
              {celdas
                .sort((a, b) => b.menciones - a.menciones)
                .map((c, i) => (
                  <tr key={i}>
                    <td>
                      <button type="button" className="enlace-tabla" onClick={() => actualizarFiltro({ autor: c.autor })}>
                        {c.autor}
                      </button>
                    </td>
                    <td>{c.episodioTitulo}</td>
                    <td>{c.fecha.toISOString().slice(0, 10)}</td>
                    <td>{c.menciones}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
