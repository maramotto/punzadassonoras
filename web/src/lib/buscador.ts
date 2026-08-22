// Gestiona el worker de Orama desde el hilo principal: lo arranca una vez,
// expone su estado de "listo" y resuelve busquedas por promesa. Mientras el
// indice no esta listo, quien use esto debe usar el filtrado por subcadena de
// filtrarIndices() (store.ts) como alternativa -- ver useBuscador() en
// componentes/Buscador.tsx, que hace exactamente eso.

export interface HitBusqueda {
  refIdx: number;
  score: number;
}

type Suscriptor = (listo: boolean) => void;

let worker: Worker | null = null;
let listo = false;
let siguienteId = 1;
const pendientes = new Map<number, (hits: HitBusqueda[]) => void>();
const suscriptores = new Set<Suscriptor>();

function avisarListo(valor: boolean) {
  listo = valor;
  for (const s of suscriptores) s(valor);
}

export function iniciarBuscador(): Worker {
  if (worker) return worker;
  worker = new Worker(new URL("../workers/busqueda.worker.ts", import.meta.url), { type: "module" });

  worker.addEventListener("message", (evento: MessageEvent) => {
    const msg = evento.data;
    if (msg.tipo === "listo") {
      avisarListo(true);
    } else if (msg.tipo === "resultado") {
      const resolver = pendientes.get(msg.id);
      if (resolver) {
        resolver(msg.hits);
        pendientes.delete(msg.id);
      }
    } else if (msg.tipo === "error") {
      console.error("[buscador]", msg.mensaje);
    }
  });

  return worker;
}

export function buscadorListo(): boolean {
  return listo;
}

export function suscribirseEstadoBuscador(fn: Suscriptor): () => void {
  suscriptores.add(fn);
  return () => suscriptores.delete(fn);
}

export function buscar(consulta: string): Promise<HitBusqueda[]> {
  const w = iniciarBuscador();
  const id = siguienteId++;
  return new Promise((resolve) => {
    pendientes.set(id, resolve);
    w.postMessage({ tipo: "buscar", id, consulta });
  });
}

/** Debounce de 150 ms pedido por el plan: agrupa pulsaciones seguidas en una
 * sola consulta al worker, cancelando las intermedias. */
export function crearBusquedaConDebounce(esperaMs = 150) {
  let manejador: ReturnType<typeof setTimeout> | null = null;
  let ultimaConsulta = 0;

  return function buscarConDebounce(consulta: string, alTerminar: (hits: HitBusqueda[]) => void) {
    if (manejador) clearTimeout(manejador);
    const miTurno = ++ultimaConsulta;
    manejador = setTimeout(() => {
      buscar(consulta).then((hits) => {
        if (miTurno === ultimaConsulta) alTerminar(hits);
      });
    }, esperaMs);
  };
}
