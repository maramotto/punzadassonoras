import { useStore } from "@nanostores/react";
import { filtro$ } from "../lib/store";
import Tabla from "./Tabla";

/** La tabla completa es dificil de navegar sin acotar antes: solo se muestra
 * cuando hay temporada+episodio elegidos, o una autoria elegida. El resto del
 * tiempo, un aviso explica que hace falta acotar. */
export default function TablaCondicional() {
  const filtro = useStore(filtro$);
  const puedeVerse = (filtro.temporada.length > 0 && filtro.episodio !== null) || filtro.autor !== null;

  if (!puedeVerse) {
    return (
      <p className="nota-grafico" style={{ padding: "1rem", border: "1px dashed var(--color-borde)", borderRadius: "var(--radio)" }}>
        Elige una temporada y un episodio, o una autoría, en la barra de arriba para ver la tabla completa de
        menciones.
      </p>
    );
  }

  return <Tabla />;
}
