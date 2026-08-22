// Carga y cachea index.json en el cliente, y resuelve los indices de cadena a
// texto. Cero peticiones fuera de /data/*.json (que vive en el propio dominio).
import type { Index, MencionResuelta } from "./tipos";

let promesaIndex: Promise<Index> | null = null;

/** Carga index.json una sola vez por sesion de pagina; llamadas repetidas
 * reciben la misma promesa en curso o ya resuelta. */
export function cargarIndex(): Promise<Index> {
  if (!promesaIndex) {
    promesaIndex = fetch("/data/index.json").then((r) => {
      if (!r.ok) throw new Error(`No se pudo cargar index.json: ${r.status}`);
      return r.json() as Promise<Index>;
    });
  }
  return promesaIndex;
}

export function resolverMencion(index: Index, refIdx: number): MencionResuelta {
  const fila = index.refs[refIdx];
  const [epIdx, autIdx, obrIdx, parIdx, tipIdx, funIdx, tonIdx, sopIdx, alcIdx, conIdx, inicioS, cita] = fila;
  return {
    refIdx,
    episodio: index.eps[epIdx],
    epIdx,
    autor: index.aut[autIdx],
    obra: index.obr[obrIdx],
    parte: index.par[parIdx],
    tipo: index.tip[tipIdx],
    funcion: index.fun[funIdx],
    tono: index.ton[tonIdx],
    soporte: index.sop[sopIdx],
    alcance: index.alc[alcIdx],
    confianza: index.con[conIdx],
    inicioS,
    cita,
  };
}

/** Resuelve una lista de posiciones en index.refs (tipicamente el resultado de
 * filtrarIndices() del store) a menciones con texto legible. */
export function resolverIndices(index: Index, refIdxs: number[]): MencionResuelta[] {
  return refIdxs.map((i) => resolverMencion(index, i));
}

export function episodioPorId(index: Index, id: string) {
  return index.eps.find((e) => e[0] === id);
}

export function minutoLegible(segundos: number | null): string {
  if (segundos == null) return "";
  const h = Math.floor(segundos / 3600);
  const m = Math.floor((segundos % 3600) / 60);
  const s = Math.floor(segundos % 60);
  const mm = String(m).padStart(h ? 2 : 1, "0");
  const ss = String(s).padStart(2, "0");
  return h ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

export function enlaceYoutube(videoId: string, inicioS: number | null): string | null {
  if (!videoId) return null;
  const t = inicioS != null ? `&t=${Math.round(inicioS)}s` : "";
  return `https://www.youtube.com/watch?v=${videoId}${t}`;
}

/** Colores fijos por entidad, no por posicion en el ranking: filtrar nunca
 * repinta a las supervivientes. Maximo 8 tonos categoricos. */
const PALETA_CATEGORICA = [
  "var(--color-cat-1)",
  "var(--color-cat-2)",
  "var(--color-cat-3)",
  "var(--color-cat-4)",
  "var(--color-cat-5)",
  "var(--color-cat-6)",
  "var(--color-cat-7)",
  "var(--color-cat-8)",
];

const cacheColor = new Map<string, string>();

export function colorPorEntidad(clave: string): string {
  let color = cacheColor.get(clave);
  if (!color) {
    // hash estable, no orden de aparicion: el color no cambia si el ranking cambia
    let h = 0;
    for (let i = 0; i < clave.length; i++) h = (h * 31 + clave.charCodeAt(i)) >>> 0;
    color = PALETA_CATEGORICA[h % PALETA_CATEGORICA.length];
    cacheColor.set(clave, color);
  }
  return color;
}

const COLOR_TONO: Record<string, string> = {
  entusiasta: "var(--color-tono-entusiasta)",
  neutro: "var(--color-tono-neutro)",
  crítico: "var(--color-tono-critico)",
  ambivalente: "var(--color-tono-ambivalente)",
};

export function colorPorTono(tono: string): string {
  return COLOR_TONO[tono] ?? "var(--color-tono-neutro)";
}

const cacheColorResuelto = new Map<string, string>();

/** Resuelve una variable CSS ("var(--x)") a su valor computado real (p. ej.
 * "oklch(74% 0.14 55)"). Hace falta para canvas/WebGL (sigma.js): esos
 * contextos no forman parte del DOM con cascada CSS, así que "var(--x)" no
 * se resuelve solo ahi como sí ocurre en SVG. Solo funciona en cliente. */
export function resolverColorCSS(valor: string): string {
  if (!valor.startsWith("var(")) return valor;
  let resuelto = cacheColorResuelto.get(valor);
  if (resuelto) return resuelto;
  const nombre = valor.slice(4, -1).trim();
  resuelto = getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
  cacheColorResuelto.set(valor, resuelto || "#888888");
  return resuelto || "#888888";
}

export function colorPorEntidadResuelto(clave: string): string {
  return resolverColorFinal(colorPorEntidad(clave));
}

/** oklch(L C H) -> [r,g,b] 0-255, algoritmo de referencia de Bjorn Ottosson
 * (https://bottosson.github.io/posts/oklab/#converting-from-linear-srgb-to-oklab). */
function oklchASrgb(l: number, c: number, hGrados: number): [number, number, number] {
  const h = (hGrados * Math.PI) / 180;
  const a = c * Math.cos(h);
  const b = c * Math.sin(h);
  const l_ = l + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = l - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = l - 0.0894841775 * a - 1.2914855480 * b;
  const l3 = l_ ** 3;
  const m3 = m_ ** 3;
  const s3 = s_ ** 3;
  const r = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3;
  const g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3;
  const bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3;
  const gamma = (x: number) => {
    const v = Math.max(0, Math.min(1, x));
    return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055;
  };
  const a8 = (x: number) => Math.round(Math.max(0, Math.min(1, gamma(x))) * 255);
  return [a8(r), a8(g), a8(bl)];
}

const cacheColorFinal = new Map<string, string>();

/** A diferencia de resolverColorCSS (que devuelve el valor bruto del custom
 * property, "oklch(...)" tal cual esta escrito), esto lo convierte a
 * "rgb(r, g, b)" de verdad. Hace falta para escalas continuas de Observable
 * Plot (interpolate: "hcl"): usan d3-color por debajo, que no entiende la
 * funcion oklch() -- ni siquiera pasando por canvas o getComputedStyle sobre
 * un elemento de prueba, porque los navegadores actuales conservan oklch()
 * tal cual en vez de normalizarlo a rgb() como hacian antes. Sin esto la
 * escala interpola entre dos colores no reconocidos y el resultado se pinta
 * negro solido: justo el bug que esto arregla. */
export function resolverColorFinal(valor: string): string {
  let resuelto = cacheColorFinal.get(valor);
  if (resuelto) return resuelto;
  const crudo = resolverColorCSS(valor);
  const m = crudo.match(/oklch\(\s*([\d.]+)(%)?\s+([\d.]+)\s+([\d.]+)/);
  if (!m) {
    resuelto = crudo;
  } else {
    const l = m[2] ? Number(m[1]) / 100 : Number(m[1]);
    const [r, g, b] = oklchASrgb(l, Number(m[3]), Number(m[4]));
    resuelto = `rgb(${r}, ${g}, ${b})`;
  }
  cacheColorFinal.set(valor, resuelto);
  return resuelto;
}
