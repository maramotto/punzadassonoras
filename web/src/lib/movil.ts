const CONSULTA = "(max-width: 640px)";

/** Punto de partida para el estado "ver como tabla" de los graficos densos
 * (matrices, grafo): en pantalla estrecha no caben, mejor arrancar en su
 * tabla gemela. Es solo el valor inicial -- una vez que alguien cambia de
 * vista a mano, ese cambio manda; no se fuerza de vuelta a tabla si gira el
 * telefono o cambia el tamano de la ventana despues. */
export function comoTablaPorDefecto(): boolean {
  return typeof window !== "undefined" && window.matchMedia(CONSULTA).matches;
}
