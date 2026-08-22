// Formas de los JSON generados por podcast-data/scripts/14_build_web_data.py.
// Mantener en sincronia con ese script: es la unica fuente de verdad del esquema.

/** Una fila de eps: [id, codigo, titulo, fecha, duracion_s, temporada, video_id, temaIdx[]] */
export type FilaEpisodio = [
  id: string,
  codigo: string,
  titulo: string,
  fecha: string,
  duracionS: number,
  temporada: number | null,
  videoId: string,
  temaIdx: number[],
];

/** Una fila de refs: [epIdx, autIdx, obrIdx, parIdx, tipIdx, funIdx, tonIdx, sopIdx, alcIdx, conIdx, inicio_s, cita] */
export type FilaMencion = [
  epIdx: number,
  autIdx: number,
  obrIdx: number,
  parIdx: number,
  tipIdx: number,
  funIdx: number,
  tonIdx: number,
  sopIdx: number,
  alcIdx: number,
  conIdx: number,
  inicioS: number | null,
  cita: string,
];

export interface Index {
  eps: FilaEpisodio[];
  aut: string[];
  obr: string[];
  par: string[];
  tip: string[];
  fun: string[];
  ton: string[];
  sop: string[];
  alc: string[];
  con: string[];
  temas: string[];
  refs: FilaMencion[];
}

/** Una mencion ya resuelta a texto, con su posicion original en index.refs. */
export interface MencionResuelta {
  refIdx: number;
  episodio: FilaEpisodio;
  epIdx: number;
  autor: string;
  obra: string;
  parte: string;
  tipo: string;
  funcion: string;
  tono: string;
  soporte: string;
  alcance: string;
  confianza: string;
  inicioS: number | null;
  cita: string;
}

export interface EditorialAudio {
  editorial: string;
  cita: string;
}

export interface CitaResumen {
  cita: string;
  contexto: string;
  episodio_id: string;
  episodio_titulo: string;
  inicio_s: number | null;
  parte: string;
  funcion: string;
  tono: string;
}

export interface CitaResumenAutor extends CitaResumen {
  obra: string;
}

export interface Obra {
  autor: string;
  obra: string;
  tipo: string;
  subtipo: string;
  menciones: number;
  episodios: string[];
  partes: string[];
  anio: number | null;
  editorial: string | null;
  editoriales_mencionadas_en_audio: EditorialAudio[];
  en_dialogo_con: string[];
  citas: CitaResumen[];
}

export interface Autor {
  autor: string;
  menciones: number;
  obras: string[];
  partes: string[];
  episodios: string[];
  primera_aparicion: string | null;
  ultima_aparicion: string | null;
  en_dialogo_con: string[];
  citas: CitaResumenAutor[];
}

export interface NodoDialogo {
  id: string;
  titulo: string;
  menciones: number;
  componente: number;
}

export interface Dialogo {
  nodes: NodoDialogo[];
  edges: [number, number, number][];
}

export interface Figura {
  figura: string;
  menciones: number;
  episodios: string[];
  en_dialogo_con: string[];
  citas: {
    episodio: string;
    cita: string;
    contexto: string;
    inicio_s: number | null;
    en_dialogo_con: string[];
  }[];
}

/** Mencion completa tal como sale de extraccion/*.json, para la ficha de episodio. */
export interface MencionCompleta {
  id: string;
  autor: string;
  obra: string;
  parte: string;
  tipo: string;
  subtipo: string;
  funcion: string;
  alcance: string;
  soporte: string;
  tono: string;
  grado: string;
  via: string | null;
  autores_citados: string[];
  fuente: string;
  inicio_s: number | null;
  segmento_idx?: number;
  hablante: string;
  cita: string;
  contexto: string;
  en_dialogo_con: string[];
  datos_nuevos: { campo: string; valor: string; cita: string; inicio_s: number }[];
  confianza: string;
}

export interface FichaEpisodio {
  id: string;
  codigo: string;
  titulo: string;
  fecha: string;
  duracion_s: number;
  temporada: number | null;
  serie: string;
  video_id: string;
  tags: string[];
  menciones: MencionCompleta[];
}

/** Un documento de busqueda.json (indexado por Orama en el worker). refIdx
 * apunta a la misma posicion en index.refs, para poder cruzar con tono,
 * funcion, temporada, etc. sin duplicar esos campos aqui. */
export interface DocBusqueda {
  refIdx: number;
  autor: string;
  obra: string;
  parte: string;
  cita: string;
  contexto: string;
  episodioTitulo: string;
}
