import { useState } from "react";
import { colorPorTono, enlaceYoutube, minutoLegible } from "../lib/datos";

export interface MarcaRegleta {
  inicioS: number;
  tono: string;
  cita: string;
}

interface Props {
  duracionS: number;
  codigo: string;
  videoId: string;
  marcas: MarcaRegleta[];
  /** version en miniatura para las tarjetas de episodio del buscador */
  compacta?: boolean;
}

export default function Regleta({ duracionS, codigo, videoId, marcas, compacta = false }: Props) {
  const [copiado, setCopiado] = useState<number | null>(null);

  async function activar(marca: MarcaRegleta) {
    const enlace = enlaceYoutube(videoId, marca.inicioS);
    if (enlace) {
      window.open(enlace, "_blank", "noopener,noreferrer");
      return;
    }
    const texto = `${codigo || "?"} · ${minutoLegible(marca.inicioS)}`;
    try {
      await navigator.clipboard.writeText(texto);
      setCopiado(marca.inicioS);
      setTimeout(() => setCopiado((actual) => (actual === marca.inicioS ? null : actual)), 1500);
    } catch {
      // portapapeles no disponible (contexto no seguro, permiso denegado...):
      // no hay nada mas que hacer, la marca sigue siendo visible e informativa.
    }
  }

  return (
    <div
      role="group"
      aria-label={`Línea de tiempo del episodio${codigo ? " " + codigo : ""}, ${marcas.length} menciones`}
      style={{
        position: "relative",
        width: "100%",
        height: compacta ? "0.75rem" : "2.5rem",
        background: "var(--color-superficie-alta)",
        borderRadius: "var(--radio)",
        border: "1px solid var(--color-borde)",
      }}
    >
      {marcas.map((marca, i) => {
        const posicion = duracionS ? (marca.inicioS / duracionS) * 100 : 0;
        const esCopiado = copiado === marca.inicioS;
        return (
          <button
            key={`${marca.inicioS}-${i}`}
            type="button"
            onClick={() => activar(marca)}
            title={marca.cita}
            aria-label={`${minutoLegible(marca.inicioS)} — ${marca.cita}`}
            style={{
              all: "unset",
              cursor: "pointer",
              position: "absolute",
              left: `${posicion}%`,
              top: 0,
              bottom: 0,
              width: compacta ? "2px" : "3px",
              background: esCopiado ? "var(--color-acento)" : colorPorTono(marca.tono),
              opacity: 0.85,
            }}
          />
        );
      })}
      {copiado != null && !compacta && (
        <span
          aria-live="polite"
          style={{
            position: "absolute",
            right: "0.5rem",
            top: "-1.4rem",
            fontSize: "0.75em",
            color: "var(--color-texto-tenue)",
          }}
        >
          copiado al portapapeles
        </span>
      )}
    </div>
  );
}
