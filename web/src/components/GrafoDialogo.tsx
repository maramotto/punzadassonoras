import { useEffect, useMemo, useRef, useState } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import Sigma from "sigma";
import { actualizarFiltro } from "../lib/store";
import { cargarIndex, colorPorEntidadResuelto, resolverColorFinal } from "../lib/datos";
import { slugObra } from "../lib/slugs";
import type { Dialogo, NodoDialogo } from "../lib/tipos";

const TAMANIO_MINIMO_COMPONENTE = 4;

function comoRgbTupla(colorRgb: string): [number, number, number] {
  const m = colorRgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
  return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : [200, 200, 200];
}

/** Aclara un color hacia otro (mezcla lineal en sRGB), para atenuar lo que
 * no forma parte del camino resaltado sin tener que mantener una segunda
 * paleta. cantidad 0 = sin cambio, 1 = el color de destino entero. */
function atenuar(colorRgb: string, hacia: [number, number, number], cantidad: number): string {
  const [r, g, b] = comoRgbTupla(colorRgb);
  const mezcla = (c: number, h: number) => Math.round(c + (h - c) * cantidad);
  return `rgb(${mezcla(r, hacia[0])}, ${mezcla(g, hacia[1])}, ${mezcla(b, hacia[2])})`;
}

interface Vecino {
  id: string;
  titulo: string;
  peso: number;
}

export default function GrafoDialogo() {
  const contenedorRef = useRef<HTMLDivElement>(null);
  const sigmaRef = useRef<Sigma | undefined>(undefined);
  const grafoRef = useRef<Graph | undefined>(undefined);
  const [dialogo, setDialogo] = useState<Dialogo | null>(null);
  const [comoTabla, setComoTabla] = useState(false);
  const [seleccionado, setSeleccionado] = useState<string | null>(null);
  const [mapaAutorPorObra, setMapaAutorPorObra] = useState<Map<string, string> | null>(null);
  // el reducer de sigma lee la seleccion actual de una ref, no del estado: asi
  // "seleccionado" no tiene que ser dependencia del efecto pesado de abajo, que
  // recalcularia las 200 iteraciones de ForceAtlas2 en cada clic
  const seleccionadoRef = useRef<string | null>(null);
  useEffect(() => {
    seleccionadoRef.current = seleccionado;
    sigmaRef.current?.refresh();
  }, [seleccionado]);

  useEffect(() => {
    fetch("/data/dialogo.json")
      .then((r) => r.json())
      .then(setDialogo);
    // para el enlace "ver ficha de la obra" en el panel: index.json ya trae
    // autor+obra, dialogo.json solo trae el titulo (los nodos no son por
    // autoria). Se queda con la primera autoria vista por titulo.
    cargarIndex().then((index) => {
      const mapa = new Map<string, string>();
      for (const fila of index.refs) {
        const obra = index.obr[fila[2]];
        const autor = index.aut[fila[1]];
        if (obra && autor && autor !== "sin determinar" && !mapa.has(obra)) mapa.set(obra, autor);
      }
      setMapaAutorPorObra(mapa);
    });
  }, []);

  const nodosGrandes = dialogo ? dialogo.nodes.filter((n) => n.componente >= TAMANIO_MINIMO_COMPONENTE) : [];
  const parejasSueltas = dialogo
    ? new Set(dialogo.nodes.filter((n) => n.componente < TAMANIO_MINIMO_COMPONENTE).map((n) => n.id)).size / 2
    : 0;

  // datos del panel de info: independientes del ciclo de vida de sigma (no se
  // pierden al alternar "ver como tabla"), por eso no viven en el grafo de
  // graphology sino en su propia estructura derivada de dialogo.json.
  const { vecinosPorId, nodoPorId } = useMemo(() => {
    const vecinosPorId = new Map<string, Vecino[]>();
    const nodoPorId = new Map<string, NodoDialogo>();
    if (!dialogo) return { vecinosPorId, nodoPorId };
    for (const n of dialogo.nodes) if (n.componente >= TAMANIO_MINIMO_COMPONENTE) nodoPorId.set(n.id, n);
    for (const [a, b, peso] of dialogo.edges) {
      const nodoA = dialogo.nodes[a];
      const nodoB = dialogo.nodes[b];
      if (!nodoA || !nodoB || nodoA.componente < TAMANIO_MINIMO_COMPONENTE || nodoB.componente < TAMANIO_MINIMO_COMPONENTE) continue;
      if (!vecinosPorId.has(nodoA.id)) vecinosPorId.set(nodoA.id, []);
      if (!vecinosPorId.has(nodoB.id)) vecinosPorId.set(nodoB.id, []);
      vecinosPorId.get(nodoA.id)!.push({ id: nodoB.id, titulo: nodoB.titulo, peso });
      vecinosPorId.get(nodoB.id)!.push({ id: nodoA.id, titulo: nodoA.titulo, peso });
    }
    return { vecinosPorId, nodoPorId };
  }, [dialogo]);

  useEffect(() => {
    if (!dialogo || !contenedorRef.current || comoTabla) return;
    const contenedor = contenedorRef.current;
    contenedor.replaceChildren();

    const idxIncluidos = new Map<number, string>();
    dialogo.nodes.forEach((n, i) => {
      if (n.componente >= TAMANIO_MINIMO_COMPONENTE) idxIncluidos.set(i, n.id);
    });

    const grado = new Map<string, number>();
    for (const [a, b] of dialogo.edges) {
      const idA = idxIncluidos.get(a);
      const idB = idxIncluidos.get(b);
      if (!idA || !idB) continue;
      grado.set(idA, (grado.get(idA) ?? 0) + 1);
      grado.set(idB, (grado.get(idB) ?? 0) + 1);
    }

    const colorArista = resolverColorFinal("var(--color-borde)");
    const colorResaltado = resolverColorFinal("var(--color-acento)");
    const colorFondoTarjeta = comoRgbTupla(resolverColorFinal("var(--color-superficie-alta)"));
    const colorAristaTenue = atenuar(colorArista, colorFondoTarjeta, 0.6);

    const grafo = new Graph();
    let angulo = 0;
    const paso = (2 * Math.PI) / Math.max(1, idxIncluidos.size);
    for (const [, id] of idxIncluidos) {
      const nodo = dialogo.nodes.find((n) => n.id === id)!;
      const color = colorPorEntidadResuelto(id);
      grafo.addNode(id, {
        x: Math.cos(angulo) * 10 + Math.random(),
        y: Math.sin(angulo) * 10 + Math.random(),
        size: 2 + Math.sqrt(nodo.menciones) * 1.6,
        label: nodo.titulo,
        color,
        colorTenue: atenuar(color, colorFondoTarjeta, 0.65),
        grado: grado.get(id) ?? 0,
      });
      angulo += paso;
    }
    for (const [a, b, peso] of dialogo.edges) {
      const idA = idxIncluidos.get(a);
      const idB = idxIncluidos.get(b);
      if (!idA || !idB || grafo.hasEdge(idA, idB)) continue;
      grafo.addEdge(idA, idB, { size: Math.min(3, 0.5 + peso * 0.4), color: colorArista, peso });
    }

    forceAtlas2.assign(grafo, {
      iterations: 200,
      settings: { gravity: 1, scalingRatio: 8, barnesHutOptimize: true, adjustSizes: true },
    });

    // etiquetas solo en los nodos de mayor grado, para no saturar el lienzo
    // (el nodo seleccionado y sus vecinos se libran de esta regla mas abajo)
    const grados = [...grafo.nodes()].map((n) => grafo.getNodeAttribute(n, "grado") as number);
    const umbral = grados.length > 20 ? [...grados].sort((a, b) => b - a)[Math.floor(grados.length * 0.15)] : 0;

    const sigma = new Sigma(grafo, contenedor, {
      renderLabels: true,
      labelRenderedSizeThreshold: 6,
      labelDensity: 0.7,
      labelGridCellSize: 80,
      defaultNodeColor: resolverColorFinal("var(--color-cat-1)"),
      defaultEdgeColor: colorArista,
      labelColor: { color: resolverColorFinal("var(--color-texto)") },
      labelWeight: "600",
      zIndex: true,
      // Sin esto se puede seguir haciendo zoom out hasta que los ~400 nodos
      // se amontonen en un borrón ilegible de un par de pixeles; y sin cota
      // de zoom in, un doble clic accidental deja la vista perdida en una
      // esquina vacia. minRatio = mas cerca (zoom in), maxRatio = mas lejos.
      minCameraRatio: 0.1,
      maxCameraRatio: 2.5,
      nodeReducer: (id, attrs) => {
        const sel = seleccionadoRef.current;
        if (!sel) return { ...attrs, label: attrs.grado >= umbral ? attrs.label : "", highlighted: false };
        const esSeleccionado = id === sel;
        const esVecino = !esSeleccionado && grafo.areNeighbors(sel, id);
        if (esSeleccionado) return { ...attrs, highlighted: true, zIndex: 2 };
        if (esVecino) return { ...attrs, highlighted: false, zIndex: 1 };
        return { ...attrs, color: attrs.colorTenue, label: "", highlighted: false, zIndex: 0 };
      },
      edgeReducer: (edge, attrs) => {
        const sel = seleccionadoRef.current;
        if (!sel) return attrs;
        const [a, b] = grafo.extremities(edge);
        if (a === sel || b === sel) return { ...attrs, color: colorResaltado, size: Math.max(attrs.size, 2), zIndex: 1 };
        return { ...attrs, color: colorAristaTenue, zIndex: 0 };
      },
    });

    sigma.getCamera().animatedReset({ duration: 0 });

    sigma.on("clickNode", ({ node }) => {
      const titulo = grafo.getNodeAttribute(node, "label");
      setSeleccionado(node);
      actualizarFiltro({ obra: titulo });
    });
    sigma.on("clickStage", () => setSeleccionado(null));
    sigma.on("doubleClickNode", ({ node, event }) => {
      event.preventSigmaDefault();
      const titulo = grafo.getNodeAttribute(node, "label") as string;
      const autor = mapaAutorPorObra?.get(titulo);
      if (autor) window.location.href = `/obra/${slugObra(autor, titulo)}`;
    });

    grafoRef.current = grafo;
    sigmaRef.current = sigma;
    return () => sigma.kill();
  }, [dialogo, comoTabla, mapaAutorPorObra]);

  if (!dialogo) {
    return (
      <div className="tarjeta-grafico">
        <p aria-live="polite">Cargando grafo de diálogo…</p>
      </div>
    );
  }

  const nodoSeleccion = seleccionado ? nodoPorId.get(seleccionado) : null;
  const vecinosSeleccion = seleccionado ? (vecinosPorId.get(seleccionado) ?? []).sort((a, b) => b.peso - a.peso) : [];
  const autorSeleccion = nodoSeleccion ? mapaAutorPorObra?.get(nodoSeleccion.titulo) : null;

  return (
    <div className="tarjeta-grafico">
      <div className="cabecera-grafico">
        <div>
          <h2>Grafo de obras en diálogo</h2>
          <p className="nota-grafico">
            {nodosGrandes.length} obras en componentes de {TAMANIO_MINIMO_COMPONENTE} o más nodos. Quedan fuera{" "}
            {Math.round(parejasSueltas)} parejas sueltas de dos o tres obras. Clic en un nodo: resalta con quién
            dialoga. Doble clic: abre la ficha de la obra. El propio grafo solo se puede usar con ratón; "Ver como
            tabla" da la misma información completa por teclado o con lector de pantalla.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.4rem" }}>
          {!comoTabla && (
            <button
              type="button"
              className="faceta"
              onClick={() => {
                setSeleccionado(null);
                sigmaRef.current?.getCamera().animatedReset();
              }}
            >
              Restablecer vista
            </button>
          )}
          <button type="button" className="faceta" onClick={() => setComoTabla((v) => !v)}>
            {comoTabla ? "Ver grafo" : "Ver como tabla"}
          </button>
        </div>
      </div>

      {!comoTabla ? (
        <>
          <div
            ref={contenedorRef}
            aria-hidden="true"
            style={{ height: "clamp(280px, 65vw, 480px)", background: "var(--color-superficie-alta)", borderRadius: "var(--radio)" }}
          />
          {nodoSeleccion && (
            <div className="panel-nodo-grafo">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem" }}>
                <div>
                  <strong>{nodoSeleccion.titulo}</strong>
                  <p className="nota-grafico">
                    {nodoSeleccion.menciones} mención(es) · dialoga con {vecinosSeleccion.length} obra(s)
                    {autorSeleccion && <> · {autorSeleccion}</>}
                  </p>
                </div>
                <button type="button" className="faceta" onClick={() => setSeleccionado(null)} aria-label="Cerrar selección">
                  Cerrar
                </button>
              </div>
              {autorSeleccion && (
                <a className="enlace-tabla" href={`/obra/${slugObra(autorSeleccion, nodoSeleccion.titulo)}`}>
                  Ver ficha de la obra →
                </a>
              )}
              {vecinosSeleccion.length > 0 && (
                <div className="lista-vecinos-grafo">
                  {vecinosSeleccion.map((v) => (
                    <button
                      key={v.id}
                      type="button"
                      className="faceta"
                      onClick={() => {
                        setSeleccionado(v.id);
                        actualizarFiltro({ obra: v.titulo });
                      }}
                    >
                      {v.titulo} · {v.peso}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      ) : (
        <div className="contenedor-tabla-scroll">
          <table className="tabla-gemela">
            <thead>
              <tr>
                <th>Obra A</th>
                <th>Obra B</th>
                <th>Coocurrencias</th>
              </tr>
            </thead>
            <tbody>
              {dialogo?.edges
                .filter(([a, b]) => dialogo.nodes[a].componente >= TAMANIO_MINIMO_COMPONENTE && dialogo.nodes[b].componente >= TAMANIO_MINIMO_COMPONENTE)
                .map(([a, b, peso], i) => (
                  <tr key={i}>
                    <td>
                      <button type="button" className="enlace-tabla" onClick={() => actualizarFiltro({ obra: dialogo.nodes[a].titulo })}>
                        {dialogo.nodes[a].titulo}
                      </button>
                    </td>
                    <td>
                      <button type="button" className="enlace-tabla" onClick={() => actualizarFiltro({ obra: dialogo.nodes[b].titulo })}>
                        {dialogo.nodes[b].titulo}
                      </button>
                    </td>
                    <td>{peso}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
