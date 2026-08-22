# UniversoPunzadas

**Proyecto aficionado (no oficial)**, creado por [maramotto](https://github.com/maramotto)
(Mara Crespo), para catalogar todas las obras, autoras y autores que se citan en
**Punzadas Sonoras**, el podcast de **Paula Ducay** e **Inés García** producido por
**Radio Primavera Sound**. Un mapa navegable por autor, obra, tema y temporada de todo lo
que se ha citado, leído, visto y discutido a lo largo del podcast.

**Web pública: <https://universopunzadas.com>**

> Este es un proyecto aficionado, sin relación oficial con Punzadas Sonoras, Paula Ducay,
> Inés García ni Radio Primavera Sound. Todo el contenido citado (títulos, citas,
> transcripciones) pertenece a sus autoras y autores originales; este repositorio solo
> cataloga referencias con fines de documentación y consulta.

---

## Estado actual

| | |
|---|---|
| Episodios en el catálogo | **118 de 118** — extracción completa |
| Transcripciones propias | **118 de 118**, con hablante identificado (mlx-whisper large-v3 + pyannote 3.1) |
| Menciones extraídas desde el audio | **5.874** |
| Autoras y autores distintos citados | **1.160** |
| Web pública | **en producción** en [universopunzadas.com](https://universopunzadas.com) (Astro + React) |

El dato central del proyecto: las descripciones escritas de los episodios solo dan una
fracción de lo que realmente se cita. Comparando ambas fuentes, la transcripción aporta
en torno al **85-90% de las referencias** que no aparecen en ningún otro sitio — nombres
propios, ediciones, citas exactas y matices (leído/visto/escuchado, entusiasta/crítico,
qué figura concreta de un libro, con qué otra obra se pone en diálogo) que solo se oyen
en el propio episodio.

---

## De dónde salen los datos

- **Descripciones oficiales** de la playlist de YouTube y del feed RSS público del
  podcast, usadas para contrastar nombres y fechas — nunca para inventar contenido.
- **Transcripción propia** de los 118 episodios, hecha con `mlx-whisper` (modelo
  large-v3) y diarización con `pyannote` 3.1, corriendo en local.
- **Extracción de referencias** hecha leyendo la transcripción entera de cada episodio,
  con un criterio explícito y verificable: cada dato tiene que poder señalarse con una
  cita literal en el audio. Lo que no se dice, no entra — el enriquecimiento contra
  catálogos externos (editoriales, años, traductores) es una fase aparte, posterior.

El criterio completo de extracción, con ejemplos y su historial de versiones, está en
[`podcast-data/CRITERIO_extraccion.md`](podcast-data/CRITERIO_extraccion.md).

---

## Estructura del repositorio

```
punzadassonoras/
├── Dockerfile                build multi-etapa: datos (Python) -> Astro -> nginx
├── docker-compose.yml        despliegue del contenedor
├── nginx.conf                config de nginx dentro del contenedor
├── web/                      sitio Astro + React
│   ├── src/
│   │   ├── components/        gráficos (Observable Plot, sigma.js), buscador, tablas
│   │   ├── pages/              portada, /buscar, /explorar, fichas de autor/obra/tema/...
│   │   └── lib/                store de filtros, tipos, funciones compartidas
│   └── public/data/          JSON que consume el sitio, generados por 14_build_web_data.py
└── podcast-data/
    ├── data/                 índices, feeds y caches de enriquecimiento
    ├── extraccion/           una ficha .json + .md por episodio, con cada mención
    ├── transcribir/          transcripciones propias (una por episodio)
    ├── scripts/              extracción, validación, datos de la web y entregable
    └── Punzadas_Sonoras_referencias.xlsx   entregable .xlsx (autor, obra, tipo, tag...)
```

---

## Añadir un episodio nuevo

El podcast saca episodios nuevos a partir de septiembre a ritmo de un par al mes.
`podcast-data/scripts/17_nuevo_episodio.py` cubre la parte mecánica del proceso; la
transcripción y la extracción siguen siendo pasos aparte a propósito, porque no son
automatizables sin perder calidad — la extracción en concreto exige leer la transcripción
entera con el criterio de `podcast-data/CRITERIO_extraccion.md`, hoy vía Claude Code.

```bash
# 1. ¿Hay episodios nuevos en el feed que no estén en el manifiesto?
python3 podcast-data/scripts/17_nuevo_episodio.py comprobar

# 2. Dar de alta uno (equivale al bloque A0 de podcast-data/PROMPTS_claude_code.md)
python3 podcast-data/scripts/17_nuevo_episodio.py alta --fecha AAAA-MM-DD --titulo "..." [--codigo 6x01]

# 3. Aparte: transcribir (bloque A1) y extraer (bloque B1) el episodio dado de alta.

# 4. Cuando la extracción esté validada, reconstruir todo lo demás:
python3 podcast-data/scripts/17_nuevo_episodio.py regenerar --codigo-nuevo 6x01
```

El paso 4 encadena la reconciliación de identificadores, el informe de QA, la
regeneración de los datos de la web y `npm run build` en `web/`. No despliega: ese paso es
manual, ver la sección siguiente.

Los bloques de transcripción y extracción, con sus prompts exactos, están documentados
en detalle en [`podcast-data/PROMPTS_claude_code.md`](podcast-data/PROMPTS_claude_code.md);
no se duplican aquí para no desincronizarse.

---

## Despliegue

El sitio corre en un contenedor Docker, detrás de un nginx que hace de proxy inverso y
termina el HTTPS (Let's Encrypt / Certbot), en un servidor propio.

`Dockerfile` en la raíz hace un build de tres etapas, con la raíz del repo como contexto
(necesita `podcast-data/` y `web/` a la vez):

1. **datos** (`python:3.12-alpine`) — corre `14_build_web_data.py` y genera
   `web/public/data/*.json` desde `podcast-data/`.
2. **build** (`node:22-alpine`) — `npm ci && npm run build`, produce `web/dist/`.
3. **nginx** (`nginx:1.27-alpine`) — sirve `web/dist/` con `nginx.conf` (gzip, cache
   larga e inmutable para los assets con hash de Astro, cache corta para `/data/`, que
   cambia en cada despliegue).

Para actualizar el sitio en producción, en el servidor:

```bash
cd /ruta/al/repo
git pull
docker compose build
docker compose up -d
```

El contenedor se publica en un puerto local; un `nginx` a nivel de sistema (no el de
dentro del contenedor) hace de proxy inverso desde `universopunzadas.com` hacia ese
puerto y gestiona el certificado TLS. Esa parte —el vhost del host y las credenciales del
servidor— es específica de la máquina y no vive en este repositorio.

---

## Próximos pasos

- [x] Buscador con Orama (tolerancia a erratas, cuatro pestañas: autoras, obras,
      menciones, episodios).
- [x] Gráficos de `/explorar`: matriz de temas, ranking de autorías, matriz de autoría,
      grafo de obras en diálogo, área por tipo — todos contra la misma barra de filtros.
- [x] Publicación: dominio propio, HTTPS, sitemap y robots.txt, contenedor en producción.
- [ ] Revisión formal de accesibilidad (navegación por teclado, contraste, lectores de
      pantalla).

---

## Licencia y atribución

El código y los datos catalográficos de este repositorio están bajo licencia MIT (ver
[`LICENSE`](LICENSE)). Las transcripciones son un volcado automático del audio original
del podcast, con su propio aviso de atribución en
[`podcast-data/transcribir/README.md`](podcast-data/transcribir/README.md); son
automáticas y pueden contener errores. El contenido original —el podcast en sí— es
propiedad de sus autoras y de Radio Primavera Sound.

---

## Enlaces

- Punzadas Sonoras en Radio Primavera Sound: <https://www.primaverasound.com/es/radio/shows/punzadas-sonoras>
- Playlist de YouTube: <https://www.youtube.com/playlist?list=PLLbN7SMQhMVbsBcHlP9RnBXFjZyPgam6y>
- Spotify: <https://open.spotify.com/show/444xAKuV4A4WUlSXqyl51P>
- Web de las autoras: <https://punzadas.com/punzadas-sonoras/>
- Newsletter: <https://punzadas.substack.com>
