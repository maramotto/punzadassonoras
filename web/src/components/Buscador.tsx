import { useEffect, useMemo, useRef, useState } from "react";
import { useStore } from "@nanostores/react";
import { filtro$, filtrarIndices, normalizarBusqueda, conectarUrl } from "../lib/store";
import { cargarIndex, minutoLegible, resolverMencion } from "../lib/datos";
import { slugObra, slugificar } from "../lib/slugs";
import { buscadorListo, crearBusquedaConDebounce, suscribirseEstadoBuscador, type HitBusqueda } from "../lib/buscador";
import type { Index, MencionResuelta } from "../lib/tipos";
import AreaPorTipo from "./AreaPorTipo";

type Pestana = "autoras" | "obras" | "menciones" | "episodios";
const PESTANAS: { id: Pestana; etiqueta: string }[] = [
  { id: "autoras", etiqueta: "Autoras" },
  { id: "obras", etiqueta: "Obras" },
  { id: "menciones", etiqueta: "Menciones" },
  { id: "episodios", etiqueta: "Episodios" },
];

const buscarConDebounce = crearBusquedaConDebounce(150);

// Resumenes por autor/obra calculados a partir de index.json, que ya esta
// cargado en toda la web. Deliberadamente NO se hace fetch de autores.json ni
// obras.json aqui: llevan "citas" para las fichas estaticas (ficha de autor u
// obra completa) y pesan varios MB -- bien para una pagina que se genera una
// vez en build, mal para descargarlos enteros en cada visita a /buscar.
interface ResumenAutor {
  autor: string;
  menciones: number;
  obras: number;
  episodios: number;
  primeraAparicion: string | null;
}
interface ResumenObra {
  autor: string;
  obra: string;
  tipo: string;
  menciones: number;
}

function calcularResumenes(index: Index) {
  const porAutor = new Map<string, { menciones: number; obras: Set<string>; episodios: Set<number>; fechas: string[] }>();
  const porObra = new Map<string, { autor: string; obra: string; tipo: string; menciones: number }>();

  for (const fila of index.refs) {
    const [epIdx, autIdx, obrIdx, , tipIdx] = fila;
    const autor = index.aut[autIdx];
    const obra = index.obr[obrIdx];
    const ep = index.eps[epIdx];

    if (autor && autor !== "sin determinar") {
      let a = porAutor.get(autor);
      if (!a) {
        a = { menciones: 0, obras: new Set(), episodios: new Set(), fechas: [] };
        porAutor.set(autor, a);
      }
      a.menciones++;
      if (obra) a.obras.add(obra);
      a.episodios.add(epIdx);
      a.fechas.push(ep[3]);

      if (obra) {
        const clave = `${autor}||${obra}`;
        let o = porObra.get(clave);
        if (!o) {
          o = { autor, obra, tipo: index.tip[tipIdx], menciones: 0 };
          porObra.set(clave, o);
        }
        o.menciones++;
      }
    }
  }

  const resumenAutores: ResumenAutor[] = [...porAutor.entries()].map(([autor, a]) => ({
    autor,
    menciones: a.menciones,
    obras: a.obras.size,
    episodios: a.episodios.size,
    primeraAparicion: a.fechas.length ? a.fechas.sort()[0] : null,
  }));
  const resumenObras: ResumenObra[] = [...porObra.values()];

  return { resumenAutores, resumenObras };
}

function leerPestanaDeUrl(): Pestana {
  if (typeof window === "undefined") return "menciones";
  const p = new URLSearchParams(window.location.search).get("tab");
  return PESTANAS.some((t) => t.id === p) ? (p as Pestana) : "menciones";
}

function resaltar(texto: string, consulta: string) {
  if (!consulta.trim()) return texto;
  const idx = normalizarBusqueda(texto).indexOf(normalizarBusqueda(consulta));
  if (idx === -1) return texto;
  return (
    <>
      {texto.slice(0, idx)}
      <mark>{texto.slice(idx, idx + consulta.length)}</mark>
      {texto.slice(idx + consulta.length)}
    </>
  );
}

export default function Buscador() {
  const filtro = useStore(filtro$);
  const [index, setIndex] = useState<Index | null>(null);
  const [listo, setListo] = useState(buscadorListo());
  const [hits, setHits] = useState<HitBusqueda[]>([]);
  const [pestana, setPestana] = useState<Pestana>("menciones");
  const primerRender = useRef(true);

  useEffect(() => {
    conectarUrl();
    setPestana(leerPestanaDeUrl());
    cargarIndex().then(setIndex);
    return suscribirseEstadoBuscador(setListo);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    params.set("tab", pestana);
    const nueva = `${window.location.pathname}?${params.toString()}${window.location.hash}`;
    if (nueva !== `${window.location.pathname}${window.location.search}${window.location.hash}`) {
      window.history.replaceState(null, "", nueva);
    }
  }, [pestana]);

  const { resumenAutores, resumenObras } = useMemo(
    () => (index ? calcularResumenes(index) : { resumenAutores: [], resumenObras: [] }),
    [index],
  );

  // Mientras el worker no esta listo, filtrado por subcadena sobre index (lo
  // que ya hace filtrarIndices con "q") en vez de quedarse bloqueado.
  useEffect(() => {
    if (!index) return;
    if (!filtro.q.trim()) {
      setHits([]);
      return;
    }
    if (!listo) {
      const idxs = filtrarIndices(index, { ...filtro, tipo: [], funcion: [], alcance: [], confianza: [], temporada: [], tema: [] });
      setHits(idxs.map((refIdx) => ({ refIdx, score: 1 })));
      return;
    }
    buscarConDebounce(filtro.q, setHits);
  }, [filtro.q, listo, index]);

  const mencionesResueltas: MencionResuelta[] = useMemo(() => {
    if (!index) return [];
    return hits.map((h) => resolverMencion(index, h.refIdx));
  }, [hits, index]);

  const autoresResultado = useMemo(() => {
    const desdeMenciones = new Set(mencionesResueltas.map((m) => m.autor));
    const qNorm = normalizarBusqueda(filtro.q);
    const directos = qNorm ? resumenAutores.filter((a) => normalizarBusqueda(a.autor).includes(qNorm)) : [];
    const claves = new Set<string>();
    const salida: ResumenAutor[] = [];
    for (const a of [...directos, ...resumenAutores.filter((a) => desdeMenciones.has(a.autor))]) {
      if (claves.has(a.autor)) continue;
      claves.add(a.autor);
      salida.push(a);
    }
    return salida.sort((a, b) => b.menciones - a.menciones);
  }, [resumenAutores, mencionesResueltas, filtro.q]);

  const obrasResultado = useMemo(() => {
    const desdeMenciones = new Set(mencionesResueltas.filter((m) => m.obra).map((m) => `${m.autor}||${m.obra}`));
    const qNorm = normalizarBusqueda(filtro.q);
    const directas = qNorm ? resumenObras.filter((o) => normalizarBusqueda(o.obra).includes(qNorm)) : [];
    const claves = new Set<string>();
    const salida: ResumenObra[] = [];
    for (const o of [...directas, ...resumenObras.filter((o) => desdeMenciones.has(`${o.autor}||${o.obra}`))]) {
      const clave = `${o.autor}||${o.obra}`;
      if (claves.has(clave)) continue;
      claves.add(clave);
      salida.push(o);
    }
    return salida.sort((a, b) => b.menciones - a.menciones);
  }, [resumenObras, mencionesResueltas, filtro.q]);

  const episodiosResultado = useMemo(() => {
    if (!index) return [];
    const conteoDesdeMenciones = new Map<number, number>();
    for (const m of mencionesResueltas) conteoDesdeMenciones.set(m.epIdx, (conteoDesdeMenciones.get(m.epIdx) ?? 0) + 1);
    const qNorm = normalizarBusqueda(filtro.q);
    const epIdxs = new Set(conteoDesdeMenciones.keys());
    if (qNorm) {
      index.eps.forEach((ep, i) => {
        if (normalizarBusqueda(ep[2]).includes(qNorm)) epIdxs.add(i);
      });
    }
    return [...epIdxs]
      .map((i) => ({ ep: index.eps[i], epIdx: i, coincidencias: conteoDesdeMenciones.get(i) ?? 0 }))
      .sort((a, b) => b.coincidencias - a.coincidencias);
  }, [index, mencionesResueltas, filtro.q]);

  if (primerRender.current) primerRender.current = false;

  if (!filtro.q.trim()) {
    return (
      <div className="envoltura" style={{ padding: "1rem 1.25rem 2rem" }}>
        <p style={{ color: "var(--color-texto-tenue)" }}>
          Escribe algo en el buscador de la barra de arriba: autoras, obras, un fragmento de cita… Mientras tanto,
          esto es lo que hay en el archivo.
        </p>
        <AreaPorTipo />
      </div>
    );
  }

  const recuentos: Record<Pestana, number> = {
    autoras: autoresResultado.length,
    obras: obrasResultado.length,
    menciones: mencionesResueltas.length,
    episodios: episodiosResultado.length,
  };

  return (
    <div className="envoltura" style={{ padding: "1rem 1.25rem 3rem" }}>
      {!listo && <p className="nota-grafico">Buscando por coincidencia simple mientras se prepara el índice con tolerancia a erratas…</p>}
      <div role="tablist" aria-label="Resultados de búsqueda" style={{ display: "flex", gap: "0.4rem", borderBottom: "1px solid var(--color-borde)", marginBottom: "1rem" }}>
        {PESTANAS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={pestana === t.id}
            className="pestana-buscador"
            onClick={() => setPestana(t.id)}
          >
            {t.etiqueta} ({recuentos[t.id]})
          </button>
        ))}
      </div>

      {pestana === "autoras" && (
        <ul className="lista-resultados">
          {autoresResultado.slice(0, 100).map((a) => (
            <li key={a.autor} className="tarjeta-resultado">
              <a href={`/autor/${slugificar(a.autor)}`} className="titulo-resultado">
                {resaltar(a.autor, filtro.q)}
              </a>
              <p className="nota-grafico">
                {a.menciones} menciones · {a.obras} obras · {a.episodios} episodios
                {a.primeraAparicion && ` · desde ${a.primeraAparicion}`}
              </p>
            </li>
          ))}
          {autoresResultado.length === 0 && <p className="nota-grafico">Sin autorías que coincidan.</p>}
        </ul>
      )}

      {pestana === "obras" && (
        <ul className="lista-resultados">
          {obrasResultado.slice(0, 100).map((o) => (
            <li key={`${o.autor}||${o.obra}`} className="tarjeta-resultado">
              <a href={`/obra/${slugObra(o.autor, o.obra)}`} className="titulo-resultado">
                {resaltar(o.obra, filtro.q)}
              </a>
              <p className="nota-grafico">
                {o.autor} · {o.tipo} · {o.menciones} menciones
              </p>
            </li>
          ))}
          {obrasResultado.length === 0 && <p className="nota-grafico">Sin obras que coincidan.</p>}
        </ul>
      )}

      {pestana === "menciones" && (
        <ul className="lista-resultados">
          {mencionesResueltas.slice(0, 200).map((m) => (
            <li key={m.refIdx} className="tarjeta-resultado">
              <p style={{ margin: "0 0 0.3rem" }}>«{resaltar(m.cita, filtro.q)}»</p>
              <p className="nota-grafico">
                <a href={`/autor/${slugificar(m.autor)}`}>{m.autor}</a>
                {m.obra && <> — <a href={`/obra/${slugObra(m.autor, m.obra)}`}>{m.obra}</a></>}
                {" · "}
                <a href={`/episodio/${m.episodio[0]}`}>{m.episodio[2]}</a>
                {m.inicioS != null && ` · ${minutoLegible(m.inicioS)}`}
                {" · "}
                {m.tono}
              </p>
            </li>
          ))}
          {mencionesResueltas.length === 0 && <p className="nota-grafico">Sin menciones que coincidan.</p>}
        </ul>
      )}

      {pestana === "episodios" && (
        <ul className="lista-resultados">
          {episodiosResultado.slice(0, 100).map(({ ep, coincidencias }) => (
            <li key={ep[0]} className="tarjeta-resultado">
              <a href={`/episodio/${ep[0]}`} className="titulo-resultado">
                {resaltar(ep[2], filtro.q)}
              </a>
              <p className="nota-grafico">
                {ep[3]} · {coincidencias > 0 ? `${coincidencias} mención(es) que casan` : "coincide en el título"}
              </p>
            </li>
          ))}
          {episodiosResultado.length === 0 && <p className="nota-grafico">Sin episodios que coincidan.</p>}
        </ul>
      )}
    </div>
  );
}
