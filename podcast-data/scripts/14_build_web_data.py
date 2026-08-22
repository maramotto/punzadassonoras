#!/usr/bin/env python3
"""Genera los JSON que consume la web en web/public/data/.

Lee podcast-data/extraccion/*.json (menciones), podcast-data/data/refs_all.json
(temas), podcast-data/data/manifiesto_audio.json (metadatos canonicos: id, codigo,
video_id, duracion) y los caches de enriquecimiento (openlibrary, mcu, dialnet).

No toca nada fuera de web/public/data/. Idempotente: escribe siempre el estado
completo, no acumula.

Salidas:
  index.json          - todo lo que necesita el cliente para filtrar y navegar
  busqueda.json        - documentos para el indice de Orama (con "contexto",
                        que index.json no lleva a proposito por tamano)
  obras.json           - una entrada por par autor+obra
  autores.json         - una entrada por autoria
  dialogo.json         - grafo de "en_dialogo_con"
  figuras.json         - partes de "Fragmentos de un discurso amoroso"
  episodios/<id>.json  - ficha completa por episodio

Uso: python3 14_build_web_data.py [--test]
  --test  corre solo los tests de consistencia sobre la salida ya escrita, sin
          regenerar nada (util tras tocar los JSON a mano).
"""
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
EXTRACCION = os.path.join(BASE, "extraccion")
WEB_DATA = os.path.join(os.path.dirname(BASE), "web", "public", "data")

# Autoria que no representa una persona real: se excluye de autores.json y de
# obras.json (sigue estando en index.json/episodios, solo no genera pagina propia).
AUTORIA_NO_REAL = {"sin determinar"}

FRAGMENTOS = "Fragmentos de un discurso amoroso"


# --------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------

def normalizar(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def clave_cache(autor, obra):
    return f"{normalizar(autor)}||{normalizar(obra)}"


def cargar_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


class TablaIndice:
    """Lista de cadenas distintas con lookup O(1) para construir arrays indexados."""

    def __init__(self):
        self._indices = {}
        self.valores = []

    def idx(self, valor):
        valor = valor or ""
        if valor not in self._indices:
            self._indices[valor] = len(self.valores)
            self.valores.append(valor)
        return self._indices[valor]


# --------------------------------------------------------------------------------
# Carga de datos de origen
# --------------------------------------------------------------------------------

def cargar_episodios():
    """Devuelve {id: {..metadatos fundidos de manifiesto+refs_all..}}, y la lista
    de menciones (dict + id de episodio) de todas las extracciones."""
    manifiesto = cargar_json(os.path.join(DATA, "manifiesto_audio.json"))
    refs_all = cargar_json(os.path.join(DATA, "refs_all.json"))
    refs_por_id = {e["id"]: e for e in refs_all}

    episodios = {}
    for e in manifiesto:
        eid = e["id"]
        r = refs_por_id.get(eid, {})
        episodios[eid] = {
            "id": eid,
            "codigo": e.get("codigo") or "",
            "titulo": e["titulo"],
            "fecha": e["fecha"],
            "duracion_s": e["duracion_s"],
            "temporada": r.get("temporada"),
            "serie": r.get("serie") or "Punzadas Sonoras",
            "video_id": e.get("video_id") or "",
            "tags": r.get("tags") or [],
        }

    menciones = []
    for path in sorted(glob.glob(os.path.join(EXTRACCION, "*.json"))):
        d = cargar_json(path)
        eid = d.get("id")
        if eid not in episodios:
            raise SystemExit(f"extraccion {path} tiene id {eid!r} sin entrada en el manifiesto")
        for m in d["menciones"]:
            menciones.append((eid, m))

    return episodios, menciones


def cargar_caches():
    caches = {}
    for nombre in ("cache_openlibrary", "cache_mcu", "cache_dialnet"):
        path = os.path.join(DATA, f"{nombre}.json")
        caches[nombre] = cargar_json(path) if os.path.exists(path) else {}
    return caches


def enriquecimiento(autor, obra, caches):
    """Devuelve (anio, editorial) desde el primer cache que tenga una coincidencia
    VERIFICADA (titulo y autor coinciden a la vez). No se usan coincidencias
    "inferidas": la politica del proyecto es no mostrar lo que no esta confirmado."""
    k = clave_cache(autor, obra)

    ol = caches["cache_openlibrary"].get(k)
    if ol and ol.get("ol_titulo") and ol.get("coincidencia_titulo") and ol.get("coincidencia_autor"):
        anio = ol.get("anio_primera_edicion")
        editoriales = ol.get("editoriales") or []
        editorial = editoriales[0] if editoriales else None
        return anio, editorial

    mcu = caches["cache_mcu"].get(k)
    if mcu and mcu.get("mcu_titulo") and mcu.get("coincidencia_titulo") and mcu.get("coincidencia_autor"):
        anio = mcu.get("anio")
        return (int(anio) if anio and str(anio).isdigit() else None), mcu.get("editorial")

    dn = caches["cache_dialnet"].get(k)
    if dn and dn.get("dialnet_titulo") and dn.get("coincidencia_titulo") and dn.get("coincidencia_autor"):
        anio = dn.get("anio")
        return (int(anio) if anio and str(anio).isdigit() else None), None

    return None, None


# --------------------------------------------------------------------------------
# index.json
# --------------------------------------------------------------------------------

def construir_index(episodios, menciones):
    orden_eps = sorted(episodios.values(), key=lambda e: e["fecha"])
    idx_ep = {e["id"]: i for i, e in enumerate(orden_eps)}

    tabla_temas = TablaIndice()
    for e in orden_eps:
        for t in e["tags"]:
            tabla_temas.idx(t)

    eps_rows = []
    for e in orden_eps:
        tema_idxs = sorted({tabla_temas.idx(t) for t in e["tags"]})
        eps_rows.append([
            e["id"], e["codigo"], e["titulo"], e["fecha"], e["duracion_s"],
            e["temporada"], e["video_id"], tema_idxs,
        ])

    tabla_aut = TablaIndice()
    tabla_obr = TablaIndice()
    tabla_par = TablaIndice()
    tabla_tip = TablaIndice()
    tabla_fun = TablaIndice()
    tabla_ton = TablaIndice()
    tabla_sop = TablaIndice()
    tabla_alc = TablaIndice()
    tabla_con = TablaIndice()

    refs_rows = []
    for eid, m in menciones:
        refs_rows.append([
            idx_ep[eid],
            tabla_aut.idx(m.get("autor")),
            tabla_obr.idx(m.get("obra")),
            tabla_par.idx(m.get("parte")),
            tabla_tip.idx(m.get("tipo")),
            tabla_fun.idx(m.get("funcion")),
            tabla_ton.idx(m.get("tono")),
            tabla_sop.idx(m.get("soporte")),
            tabla_alc.idx(m.get("alcance")),
            tabla_con.idx(m.get("confianza")),
            m.get("inicio_s"),
            m.get("cita") or "",
        ])

    index = {
        "eps": eps_rows,
        "aut": tabla_aut.valores,
        "obr": tabla_obr.valores,
        "par": tabla_par.valores,
        "tip": tabla_tip.valores,
        "fun": tabla_fun.valores,
        "ton": tabla_ton.valores,
        "sop": tabla_sop.valores,
        "alc": tabla_alc.valores,
        "con": tabla_con.valores,
        "temas": tabla_temas.valores,
        "refs": refs_rows,
    }
    return index, idx_ep


# --------------------------------------------------------------------------------
# busqueda.json
# --------------------------------------------------------------------------------

def construir_busqueda(episodios, menciones):
    """Documentos para el indice de Orama: obra, autor, parte, cita, contexto y
    titulo de episodio, con su refIdx para poder cruzar con index.json.

    "contexto" no esta en index.json a proposito: son ~1 MB de texto y ese
    fichero se carga siempre, en cada pagina; este solo lo carga el worker de
    /buscar. refIdx es la posicion en "menciones" en el MISMO orden que usa
    construir_index() para "refs" -- si algun dia esa funcion cambia de orden,
    esta tiene que cambiar igual, o los indices dejan de casar."""
    docs = []
    for i, (eid, m) in enumerate(menciones):
        ep = episodios[eid]
        docs.append({
            "refIdx": i,
            "autor": m.get("autor") or "",
            "obra": m.get("obra") or "",
            "parte": m.get("parte") or "",
            "cita": m.get("cita") or "",
            "contexto": m.get("contexto") or "",
            "episodioTitulo": ep["titulo"],
        })
    return docs


# --------------------------------------------------------------------------------
# obras.json / autores.json
# --------------------------------------------------------------------------------

def construir_obras_y_autores(episodios, menciones, caches):
    por_obra = defaultdict(list)   # (autor, obra) -> [ (eid, mencion) ]
    por_autor = defaultdict(list)  # autor -> [ (eid, mencion) ]

    for eid, m in menciones:
        autor = (m.get("autor") or "").strip()
        obra = (m.get("obra") or "").strip()
        if autor and autor not in AUTORIA_NO_REAL:
            por_autor[autor].append((eid, m))
        if autor and obra and autor not in AUTORIA_NO_REAL:
            por_obra[(autor, obra)].append((eid, m))

    obras = []
    for (autor, obra), items in sorted(por_obra.items(), key=lambda kv: -len(kv[1])):
        tipos = Counter(m.get("tipo") for _, m in items)
        subtipos = Counter(m.get("subtipo") for _, m in items if m.get("subtipo"))
        partes = sorted({m.get("parte") for _, m in items if m.get("parte")})
        eps_ids = sorted({eid for eid, _ in items}, key=lambda e: episodios[e]["fecha"])

        editoriales_audio = []
        vistas = set()
        for _, m in items:
            for dn in m.get("datos_nuevos") or []:
                if dn.get("campo") == "editorial_mencionada":
                    v = dn.get("valor")
                    if v and v not in vistas:
                        vistas.add(v)
                        editoriales_audio.append({"editorial": v, "cita": dn.get("cita") or ""})

        anio, editorial = enriquecimiento(autor, obra, caches)

        en_dialogo_con = sorted({
            destino.strip()
            for _, m in items
            for destino in (m.get("en_dialogo_con") or [])
            if destino.strip() and destino.strip() != obra
        })

        citas = [
            {
                "cita": m.get("cita") or "",
                "contexto": m.get("contexto") or "",
                "episodio_id": episodios[eid]["id"],
                "episodio_titulo": episodios[eid]["titulo"],
                "inicio_s": m.get("inicio_s"),
                "parte": m.get("parte") or "",
                "funcion": m.get("funcion") or "",
                "tono": m.get("tono") or "",
            }
            for eid, m in sorted(items, key=lambda em: (episodios[em[0]]["fecha"], em[1].get("inicio_s") or 0))
        ]

        obras.append({
            "autor": autor,
            "obra": obra,
            "tipo": tipos.most_common(1)[0][0] if tipos else "",
            "subtipo": subtipos.most_common(1)[0][0] if subtipos else "",
            "menciones": len(items),
            "episodios": eps_ids,
            "partes": partes,
            "anio": anio,
            "editorial": editorial,
            "editoriales_mencionadas_en_audio": editoriales_audio,
            "en_dialogo_con": en_dialogo_con,
            "citas": citas,
        })

    autores = []
    for autor, items in sorted(por_autor.items(), key=lambda kv: -len(kv[1])):
        obras_autor = sorted({m.get("obra") for _, m in items if m.get("obra")})
        partes_autor = sorted({m.get("parte") for _, m in items if m.get("parte")})
        eps_ids = sorted({eid for eid, _ in items}, key=lambda e: episodios[e]["fecha"])
        fechas = sorted(episodios[e]["fecha"] for e in eps_ids)

        en_dialogo_con = sorted({
            destino.strip()
            for _, m in items
            for destino in (m.get("en_dialogo_con") or [])
            if destino.strip()
        })

        citas = [
            {
                "cita": m.get("cita") or "",
                "contexto": m.get("contexto") or "",
                "obra": m.get("obra") or "",
                "episodio_id": episodios[eid]["id"],
                "episodio_titulo": episodios[eid]["titulo"],
                "inicio_s": m.get("inicio_s"),
                "parte": m.get("parte") or "",
                "funcion": m.get("funcion") or "",
                "tono": m.get("tono") or "",
            }
            for eid, m in sorted(items, key=lambda em: (episodios[em[0]]["fecha"], em[1].get("inicio_s") or 0))
        ]

        autores.append({
            "autor": autor,
            "menciones": len(items),
            "obras": obras_autor,
            "partes": partes_autor,
            "episodios": eps_ids,
            "primera_aparicion": fechas[0] if fechas else None,
            "ultima_aparicion": fechas[-1] if fechas else None,
            "en_dialogo_con": en_dialogo_con,
            "citas": citas,
        })

    return obras, autores


# --------------------------------------------------------------------------------
# dialogo.json
# --------------------------------------------------------------------------------

class UnionFind:
    def __init__(self):
        self.padre = {}

    def find(self, x):
        self.padre.setdefault(x, x)
        while self.padre[x] != x:
            self.padre[x] = self.padre[self.padre[x]]
            x = self.padre[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.padre[ra] = rb


def construir_dialogo(menciones):
    titulos_por_norm = {}   # norm -> titulo "bonito" (el mas frecuente)
    contador_titulo = Counter()
    menciones_por_norm = Counter()
    pesos = Counter()  # (norm_a, norm_b) ordenado -> peso

    for eid, m in menciones:
        obra = (m.get("obra") or "").strip()
        if not obra:
            continue
        norm_obra = normalizar(obra)
        contador_titulo[norm_obra] += 1
        titulos_por_norm.setdefault(norm_obra, obra)
        menciones_por_norm[norm_obra] += 1

        for destino in m.get("en_dialogo_con") or []:
            destino = destino.strip()
            if not destino:
                continue
            norm_destino = normalizar(destino)
            if norm_destino == norm_obra:
                continue
            titulos_por_norm.setdefault(norm_destino, destino)
            par = tuple(sorted((norm_obra, norm_destino)))
            pesos[par] += 1

    # elegir como "titulo bonito" el que mas veces aparece como obra propia,
    # no el primero visto
    mejor_titulo = {}
    conteo_variantes = defaultdict(Counter)
    for eid, m in menciones:
        obra = (m.get("obra") or "").strip()
        if obra:
            conteo_variantes[normalizar(obra)][obra] += 1
    for norm, variantes in conteo_variantes.items():
        mejor_titulo[norm] = variantes.most_common(1)[0][0]
    for norm, titulo in titulos_por_norm.items():
        mejor_titulo.setdefault(norm, titulo)

    uf = UnionFind()
    nodos_norm = set()
    for (a, b) in pesos:
        nodos_norm.add(a)
        nodos_norm.add(b)
        uf.union(a, b)
    for n in nodos_norm:
        uf.find(n)  # asegura que esta en el union-find aunque no tenga aristas

    componentes = defaultdict(list)
    for n in nodos_norm:
        componentes[uf.find(n)].append(n)
    tamanio_componente = {n: len(componentes[uf.find(n)]) for n in nodos_norm}

    orden_nodos = sorted(nodos_norm, key=lambda n: mejor_titulo.get(n, n))
    idx_nodo = {n: i for i, n in enumerate(orden_nodos)}

    nodes = [
        {
            "id": n,
            "titulo": mejor_titulo.get(n, n),
            "menciones": menciones_por_norm.get(n, 0),
            "componente": tamanio_componente[n],
        }
        for n in orden_nodos
    ]
    edges = [
        [idx_nodo[a], idx_nodo[b], peso]
        for (a, b), peso in sorted(pesos.items(), key=lambda kv: -kv[1])
    ]

    return {"nodes": nodes, "edges": edges}


# --------------------------------------------------------------------------------
# figuras.json
# --------------------------------------------------------------------------------

def construir_figuras(episodios, menciones):
    por_parte = defaultdict(list)
    for eid, m in menciones:
        if (m.get("obra") or "").strip() != FRAGMENTOS:
            continue
        parte = (m.get("parte") or "").strip()
        if not parte:
            continue
        por_parte[parte].append((eid, m))

    figuras = []
    for parte, items in sorted(por_parte.items(), key=lambda kv: -len(kv[1])):
        eps_ids = sorted({eid for eid, _ in items}, key=lambda e: episodios[e]["fecha"])
        en_dialogo_con = sorted({
            destino.strip()
            for _, m in items
            for destino in (m.get("en_dialogo_con") or [])
            if destino.strip()
        })
        figuras.append({
            "figura": parte,
            "menciones": len(items),
            "episodios": eps_ids,
            "en_dialogo_con": en_dialogo_con,
            "citas": [
                {
                    "episodio": eid,
                    "cita": m.get("cita") or "",
                    "contexto": m.get("contexto") or "",
                    "inicio_s": m.get("inicio_s"),
                    "en_dialogo_con": [d.strip() for d in (m.get("en_dialogo_con") or []) if d.strip()],
                }
                for eid, m in sorted(items, key=lambda em: (episodios[em[0]]["fecha"], em[1].get("inicio_s") or 0))
            ],
        })
    return figuras


# --------------------------------------------------------------------------------
# episodios/<id>.json
# --------------------------------------------------------------------------------

def construir_fichas_episodio(episodios, menciones):
    menciones_por_ep = defaultdict(list)
    for eid, m in menciones:
        menciones_por_ep[eid].append(m)

    fichas = {}
    for eid, meta in episodios.items():
        ms = sorted(menciones_por_ep.get(eid, []), key=lambda m: (m.get("inicio_s") is None, m.get("inicio_s")))
        fichas[eid] = {**meta, "menciones": ms}
    return fichas


# --------------------------------------------------------------------------------
# Tests de consistencia
# --------------------------------------------------------------------------------

def tests(episodios, menciones, index, busqueda=None):
    errores = []

    total_extraccion = len(menciones)
    total_index = len(index["refs"])
    if total_extraccion != total_index:
        errores.append(f"total de menciones no coincide: extraccion={total_extraccion} index={total_index}")

    for e in index["eps"]:
        eid, codigo, titulo, fecha, dur, temporada, video_id, temas_idx = e
        if not temas_idx:
            errores.append(f"episodio sin tema: {eid}")

    n_eps = len(index["eps"])
    for row in index["refs"]:
        ep_idx = row[0]
        if not (0 <= ep_idx < n_eps):
            errores.append(f"epIdx fuera de rango: {ep_idx}")
        for campo, tabla in zip(row[1:10], ("aut", "obr", "par", "tip", "fun", "ton", "sop", "alc", "con")):
            if not (0 <= campo < len(index[tabla])):
                errores.append(f"{tabla}Idx fuera de rango: {campo}")

    if busqueda is not None:
        if len(busqueda) != total_index:
            errores.append(f"busqueda.json no tiene una fila por mencion: {len(busqueda)} vs {total_index}")
        for i, doc in enumerate(busqueda):
            if doc["refIdx"] != i:
                errores.append(f"busqueda.json desalineado con index.refs en la posicion {i}: refIdx={doc['refIdx']}")
                break

    if errores:
        print(f"TESTS: FALLA ({len(errores)})")
        for e in errores[:30]:
            print(" -", e)
        return False
    print("TESTS: OK")
    return True


# --------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------

def main():
    solo_test = "--test" in sys.argv

    episodios, menciones = cargar_episodios()
    caches = cargar_caches()

    index, idx_ep = construir_index(episodios, menciones)
    busqueda = construir_busqueda(episodios, menciones)

    if solo_test:
        ok = tests(episodios, menciones, index, busqueda)
        sys.exit(0 if ok else 1)

    obras, autores = construir_obras_y_autores(episodios, menciones, caches)
    dialogo = construir_dialogo(menciones)
    figuras = construir_figuras(episodios, menciones)
    fichas = construir_fichas_episodio(episodios, menciones)

    escribir_json(os.path.join(WEB_DATA, "index.json"), index)
    escribir_json(os.path.join(WEB_DATA, "obras.json"), obras)
    escribir_json(os.path.join(WEB_DATA, "autores.json"), autores)
    escribir_json(os.path.join(WEB_DATA, "dialogo.json"), dialogo)
    escribir_json(os.path.join(WEB_DATA, "figuras.json"), figuras)
    escribir_json(os.path.join(WEB_DATA, "busqueda.json"), busqueda)
    for eid, ficha in fichas.items():
        escribir_json(os.path.join(WEB_DATA, "episodios", f"{eid}.json"), ficha)

    ok = tests(episodios, menciones, index, busqueda)

    tam_index = os.path.getsize(os.path.join(WEB_DATA, "index.json"))
    componentes_grandes = len({n["componente"] for n in dialogo["nodes"] if n["componente"] >= 4})
    nodos_en_componentes_grandes = sum(1 for n in dialogo["nodes"] if n["componente"] >= 4)

    print()
    print("=== Resumen ===")
    print(f"Episodios: {len(episodios)}")
    print(f"Menciones: {len(menciones)}")
    print(f"Autores/as distintos (index): {len(index['aut'])}")
    print(f"Obras distintas (index): {len(index['obr'])}")
    print(f"Temas: {len(index['temas'])}")
    print(f"obras.json: {len(obras)} pares autor+obra ({sum(1 for o in obras if o['anio'])} con anio)")
    print(f"autores.json: {len(autores)} autorias")
    print(f"dialogo.json: {len(dialogo['nodes'])} nodos, {len(dialogo['edges'])} aristas, "
          f"{nodos_en_componentes_grandes} nodos en componentes de 4+")
    print(f"figuras.json: {len(figuras)} figuras de Fragmentos de un discurso amoroso")
    print(f"index.json: {tam_index / 1024:.0f} KB")
    if tam_index > 1_000_000:
        print("AVISO: index.json supera 1 MB, avisar antes de recortar nada")
    tam_busqueda = os.path.getsize(os.path.join(WEB_DATA, "busqueda.json"))
    print(f"busqueda.json: {len(busqueda)} documentos, {tam_busqueda / 1024:.0f} KB "
          f"(aparte de index.json a proposito: lleva 'contexto', que solo carga el worker de /buscar)")

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
