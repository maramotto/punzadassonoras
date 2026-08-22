// Worker de busqueda: construye el indice de Orama a partir de busqueda.json
// (no de index.json -- lleva "contexto", que solo hace falta aqui) y responde
// a mensajes de busqueda sin bloquear el hilo principal. Orama ya normaliza
// acentos y aplica tolerancia a erratas por su cuenta; no hace falta que este
// worker lo haga a mano.
import { create, insertMultiple, search } from "@orama/orama";
import type { DocBusqueda } from "../lib/tipos";

type MensajeEntrada = { tipo: "buscar"; id: number; consulta: string };
type MensajeSalida =
  | { tipo: "listo"; documentos: number }
  | { tipo: "resultado"; id: number; hits: { refIdx: number; score: number }[] }
  | { tipo: "error"; mensaje: string };

const PROPIEDADES = ["autor", "obra", "parte", "cita", "contexto", "episodioTitulo"] as const;

let indice: Awaited<ReturnType<typeof create>> | null = null;
const promesaIndice = construir();

async function construir() {
  try {
    const esquema = {
      refIdx: "number",
      autor: "string",
      obra: "string",
      parte: "string",
      cita: "string",
      contexto: "string",
      episodioTitulo: "string",
    } as const;

    const db = create({ schema: esquema });
    const r = await fetch("/data/busqueda.json");
    const docs: DocBusqueda[] = await r.json();
    await insertMultiple(db, docs, 1000);

    indice = db;
    postMessage({ tipo: "listo", documentos: docs.length } satisfies MensajeSalida);
    return db;
  } catch (e) {
    postMessage({ tipo: "error", mensaje: e instanceof Error ? e.message : String(e) } satisfies MensajeSalida);
    throw e;
  }
}

self.addEventListener("message", async (evento: MessageEvent<MensajeEntrada>) => {
  const msg = evento.data;
  if (msg.tipo !== "buscar") return;

  const db = indice ?? (await promesaIndice.catch(() => null));
  if (!db) {
    postMessage({ tipo: "resultado", id: msg.id, hits: [] } satisfies MensajeSalida);
    return;
  }

  if (!msg.consulta.trim()) {
    postMessage({ tipo: "resultado", id: msg.id, hits: [] } satisfies MensajeSalida);
    return;
  }

  const resultados = await search(db, {
    term: msg.consulta,
    properties: [...PROPIEDADES],
    tolerance: 1,
    limit: 500,
  });

  const hits = resultados.hits.map((h) => ({
    refIdx: (h.document as unknown as DocBusqueda).refIdx,
    score: h.score,
  }));

  postMessage({ tipo: "resultado", id: msg.id, hits } satisfies MensajeSalida);
});
