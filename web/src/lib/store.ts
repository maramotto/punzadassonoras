// Estado global de filtros, compartido entre todas las islas de React de una
// misma pagina. Una sola barra de filtros pegajosa arriba controla esto; nunca
// hay un filtro dentro de la tarjeta de un grafico. Sincronizado en ambos
// sentidos con la query string, asi que cualquier vista filtrada es un enlace.
import { atom } from "nanostores";
import type { Index } from "./tipos";

export interface Filtro {
  q: string;
  temporada: string[];
  tema: string[];
  tipo: string[];
  funcion: string[];
  alcance: string[];
  confianza: string[];
  episodio: string | null;
  autor: string | null;
  obra: string | null;
  figura: string | null;
}

export const FILTRO_VACIO: Filtro = {
  q: "",
  temporada: [],
  tema: [],
  tipo: [],
  funcion: [],
  alcance: [],
  confianza: [],
  episodio: null,
  autor: null,
  obra: null,
  figura: null,
};

export const filtro$ = atom<Filtro>(FILTRO_VACIO);

export function actualizarFiltro(cambios: Partial<Filtro>) {
  filtro$.set({ ...filtro$.get(), ...cambios });
}

export function alternarValor(campo: "temporada" | "tema" | "tipo" | "funcion" | "alcance" | "confianza", valor: string) {
  const actual = filtro$.get();
  const lista = actual[campo];
  const nueva = lista.includes(valor) ? lista.filter((v) => v !== valor) : [...lista, valor];
  actualizarFiltro({ [campo]: nueva } as Partial<Filtro>);
}

export function limpiarFiltro() {
  filtro$.set(FILTRO_VACIO);
}

export function hayFiltrosActivos(f: Filtro): boolean {
  return (
    f.q !== "" ||
    f.temporada.length > 0 ||
    f.tema.length > 0 ||
    f.tipo.length > 0 ||
    f.funcion.length > 0 ||
    f.alcance.length > 0 ||
    f.confianza.length > 0 ||
    f.episodio !== null ||
    f.autor !== null ||
    f.obra !== null ||
    f.figura !== null
  );
}

export function normalizarBusqueda(s: string): string {
  return s
    .toLocaleLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "");
}

/** Aplica el filtro activo sobre index.refs y devuelve las posiciones que
 * sobreviven. O(n) sobre ~5900 filas: no hace falta indexar para esto, el
 * indexado con tolerancia a erratas es cosa del buscador (Orama, /buscar). */
export function filtrarIndices(index: Index, f: Filtro): number[] {
  const temporadaSet = new Set(f.temporada);
  const temaIdxSet = f.tema.length ? new Set(f.tema.map((t) => index.temas.indexOf(t))) : null;
  const qNorm = f.q ? normalizarBusqueda(f.q) : null;
  const episodioIdx = f.episodio ? index.eps.findIndex((e) => e[0] === f.episodio) : -1;

  const resultado: number[] = [];
  for (let i = 0; i < index.refs.length; i++) {
    const [epIdx, autIdx, obrIdx, parIdx, tipIdx, funIdx, , , alcIdx, conIdx] = index.refs[i];
    const ep = index.eps[epIdx];

    if (f.episodio && epIdx !== episodioIdx) continue;
    if (f.autor && index.aut[autIdx] !== f.autor) continue;
    if (f.obra && index.obr[obrIdx] !== f.obra) continue;
    if (f.figura && index.par[parIdx] !== f.figura) continue;

    if (temporadaSet.size) {
      const etiqueta = etiquetaTemporada(ep[5], ep[1]);
      if (!temporadaSet.has(etiqueta)) continue;
    }
    if (temaIdxSet && !ep[7].some((t) => temaIdxSet.has(t))) continue;
    if (f.tipo.length && !f.tipo.includes(index.tip[tipIdx])) continue;
    if (f.funcion.length && !f.funcion.includes(index.fun[funIdx])) continue;
    if (f.alcance.length && !f.alcance.includes(index.alc[alcIdx])) continue;
    if (f.confianza.length && !f.confianza.includes(index.con[conIdx])) continue;

    if (qNorm) {
      const cita = index.refs[i][11];
      const hay =
        normalizarBusqueda(index.aut[autIdx]).includes(qNorm) ||
        normalizarBusqueda(index.obr[obrIdx]).includes(qNorm) ||
        normalizarBusqueda(cita).includes(qNorm);
      if (!hay) continue;
    }

    resultado.push(i);
  }
  return resultado;
}

/** "1".."6" para temporadas numeradas, "Especial" para sueltos sin numerar
 * y sin "Glosas" en el codigo, "Glosas" para los episodios de Las Glosas. */
export function etiquetaTemporada(temporada: number | null, codigo: string): string {
  if (codigo.startsWith("Glosas")) return "Glosas";
  if (temporada == null) return "Especial";
  return String(temporada);
}

// --- sincronizacion con la query string -----------------------------------

const CAMPOS_LISTA = ["temporada", "tema", "tipo", "funcion", "alcance", "confianza"] as const;
const CAMPOS_TEXTO = ["episodio", "autor", "obra", "figura"] as const;

export function filtroDesdeQueryString(qs: string): Filtro {
  const params = new URLSearchParams(qs);
  const f: Filtro = { ...FILTRO_VACIO };
  f.q = params.get("q") ?? "";
  for (const campo of CAMPOS_LISTA) {
    const valor = params.get(campo);
    f[campo] = valor ? valor.split(",") : [];
  }
  for (const campo of CAMPOS_TEXTO) {
    f[campo] = params.get(campo);
  }
  return f;
}

export function queryStringDesdeFiltro(f: Filtro): string {
  const params = new URLSearchParams();
  if (f.q) params.set("q", f.q);
  for (const campo of CAMPOS_LISTA) {
    if (f[campo].length) params.set(campo, f[campo].join(","));
  }
  for (const campo of CAMPOS_TEXTO) {
    const valor = f[campo];
    if (valor) params.set(campo, valor);
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

let sincronizado = false;

/** Conecta el store con la URL: la lee al arrancar y la reescribe (sin apilar
 * historial) en cada cambio. Idempotente, solo se conecta una vez por carga
 * de pagina aunque varias islas la invoquen. */
export function conectarUrl() {
  if (sincronizado || typeof window === "undefined") return;
  sincronizado = true;

  filtro$.set(filtroDesdeQueryString(window.location.search));

  filtro$.subscribe((f) => {
    const qs = queryStringDesdeFiltro(f);
    const nueva = `${window.location.pathname}${qs}${window.location.hash}`;
    if (nueva !== `${window.location.pathname}${window.location.search}${window.location.hash}`) {
      window.history.replaceState(null, "", nueva);
    }
  });

  window.addEventListener("popstate", () => {
    filtro$.set(filtroDesdeQueryString(window.location.search));
  });
}
