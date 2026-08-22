// Carga de datos en tiempo de build (Node), para getStaticPaths y el
// frontmatter de las paginas .astro. No usar desde codigo de cliente: ahi va
// datos.ts, que carga /data/*.json por fetch.
//
// OJO: no calcular la ruta a partir de import.meta.url de este fichero. Astro
// empaqueta este modulo dentro de dist/.prerender/chunks/ al hacer build, asi
// que en ese momento import.meta.url apunta ahi, no a src/lib/ -- una ruta
// relativa a el se habria ido a dist/public/data, que no existe. process.cwd()
// es estable: astro build y astro dev siempre se invocan desde la raiz de
// web/.
import fs from "node:fs";
import path from "node:path";
import type { Autor, Dialogo, FichaEpisodio, Figura, Index, Obra } from "./tipos";

const DIR_DATOS = path.join(process.cwd(), "public", "data");

function leer<T>(nombre: string): T {
  const ruta = path.join(DIR_DATOS, nombre);
  return JSON.parse(fs.readFileSync(ruta, "utf-8")) as T;
}

export function indexBuild(): Index {
  return leer<Index>("index.json");
}

export function obrasBuild(): Obra[] {
  return leer<Obra[]>("obras.json");
}

export function autoresBuild(): Autor[] {
  return leer<Autor[]>("autores.json");
}

export function dialogoBuild(): Dialogo {
  return leer<Dialogo>("dialogo.json");
}

export function figurasBuild(): Figura[] {
  return leer<Figura[]>("figuras.json");
}

export function fichaEpisodioBuild(id: string): FichaEpisodio {
  return leer<FichaEpisodio>(path.join("episodios", `${id}.json`));
}

export function idsEpisodiosBuild(): string[] {
  return fs
    .readdirSync(path.join(DIR_DATOS, "episodios"))
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.slice(0, -5));
}

/** slug de URL seguro para autor/obra/figura: mismo criterio que usa el resto
 * del proyecto (podcast-data/scripts/13_reconciliar_ids.py), para que autor y
 * obra generen slugs con el mismo aspecto que los "id" de episodio. */
export { slugificar, slugObra } from "./slugs";
