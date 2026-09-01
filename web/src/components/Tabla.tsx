import { useEffect, useMemo, useRef, useState } from "react";
import { useStore } from "@nanostores/react";
import { getCoreRowModel, useReactTable, createColumnHelper, flexRender } from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { filtro$, filtrarIndices, conectarUrl } from "../lib/store";
import { cargarIndex, colorPorTono, enlaceYoutube, minutoLegible, resolverIndices } from "../lib/datos";
import { slugObra, slugificar } from "../lib/slugs";
import type { Index, MencionResuelta } from "../lib/tipos";

const ALTURA_FILA = 108;

const columnHelper = createColumnHelper<MencionResuelta>();

const columnas = [
  columnHelper.accessor("cita", {
    header: "Cita",
    size: 34,
    cell: (info) => (
      <span lang="es" className="celda-cita">
        «{info.getValue()}»
      </span>
    ),
  }),
  columnHelper.accessor("autor", {
    header: "Autoría",
    size: 15,
    cell: (info) => <a href={`/autor/${slugificar(info.getValue())}`}>{info.getValue()}</a>,
  }),
  columnHelper.accessor("obra", {
    header: "Obra",
    size: 15,
    cell: (info) => {
      const obra = info.getValue();
      if (!obra) return <span className="celda-vacia">—</span>;
      return (
        <a href={`/obra/${slugObra(info.row.original.autor, obra)}`}>
          <em>{obra}</em>
        </a>
      );
    },
  }),
  columnHelper.accessor((m) => m.episodio[2], {
    id: "episodio",
    header: "Episodio",
    size: 15,
    cell: (info) => <a href={`/episodio/${info.row.original.episodio[0]}`}>{info.getValue()}</a>,
  }),
  columnHelper.accessor("funcion", { header: "Función", size: 9 }),
  columnHelper.accessor("tono", {
    header: "Tono",
    size: 6,
    cell: (info) => {
      const tono = info.getValue();
      return (
        <span className="celda-tono">
          <span
            aria-hidden="true"
            className="punto-tono"
            data-tono={tono}
            style={{ "--color-punto": colorPorTono(tono) } as React.CSSProperties}
          />
          {tono}
        </span>
      );
    },
  }),
  columnHelper.accessor((m) => minutoLegible(m.inicioS), {
    id: "minuto",
    header: "Minuto",
    size: 6,
    cell: (info) => {
      const m = info.row.original;
      const enlace = enlaceYoutube(m.episodio[6], m.inicioS);
      return enlace ? (
        <a href={enlace} target="_blank" rel="noopener noreferrer">
          {info.getValue()}
        </a>
      ) : (
        <span>{info.getValue()}</span>
      );
    },
  }),
];

export default function Tabla() {
  const filtro = useStore(filtro$);
  const [index, setIndex] = useState<Index | null>(null);
  const contenedorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    conectarUrl();
    cargarIndex().then(setIndex);
  }, []);

  const filas: MencionResuelta[] = useMemo(() => {
    if (!index) return [];
    return resolverIndices(index, filtrarIndices(index, filtro));
  }, [index, filtro]);

  const tabla = useReactTable({
    data: filas,
    columns: columnas,
    getCoreRowModel: getCoreRowModel(),
  });

  const filasTabla = tabla.getRowModel().rows;
  const virtualizador = useVirtualizer({
    count: filasTabla.length,
    getScrollElement: () => contenedorRef.current,
    estimateSize: () => ALTURA_FILA,
    overscan: 10,
  });

  if (!index) {
    return <p aria-live="polite">Cargando menciones…</p>;
  }

  return (
    <div
      ref={contenedorRef}
      className="envoltorio-tabla"
      style={{
        overflow: "auto",
        maxHeight: "72vh",
        border: "1px solid var(--color-borde)",
        borderRadius: "var(--radio)",
        background: "var(--color-superficie)",
      }}
    >
      <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: 0, tableLayout: "fixed" }}>
        <colgroup>
          {tabla.getFlatHeaders().map((h) => (
            <col key={h.id} style={{ width: `${h.column.columnDef.size}%` }} />
          ))}
        </colgroup>
        <thead style={{ position: "sticky", top: 0, zIndex: 1 }}>
          {tabla.getHeaderGroups().map((grupo) => (
            <tr key={grupo.id}>
              {grupo.headers.map((header) => (
                <th key={header.id} className="cabecera-tabla">
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody style={{ height: `${virtualizador.getTotalSize()}px`, position: "relative", display: "block" }}>
          {virtualizador.getVirtualItems().map((filaVirtual) => {
            const fila = filasTabla[filaVirtual.index];
            return (
              <tr
                key={fila.id}
                className="fila-tabla"
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: `${filaVirtual.size}px`,
                  transform: `translateY(${filaVirtual.start}px)`,
                  display: "table",
                  tableLayout: "fixed",
                }}
              >
                {fila.getVisibleCells().map((celda) => (
                  <td key={celda.id} className="celda-tabla">
                    {flexRender(celda.column.columnDef.cell, celda.getContext())}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
      {filasTabla.length === 0 && <p style={{ padding: "1.5rem" }}>Ninguna mención con estos filtros.</p>}
    </div>
  );
}
