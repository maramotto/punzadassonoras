# universopunzadas.com — build reproducible de tres etapas:
#   1) datos:  Python puro, genera web/public/data/*.json desde podcast-data/
#   2) build:  Node + Astro, construye el sitio estatico en web/dist/
#   3) nginx:  sirve web/dist/ tal cual, sin Node ni Python en la imagen final
#
# Contexto de build: la raiz del repo (necesita podcast-data/ Y web/ a la vez).

FROM python:3.12-alpine AS datos
WORKDIR /repo
COPY podcast-data/scripts/14_build_web_data.py podcast-data/scripts/14_build_web_data.py
COPY podcast-data/data/manifiesto_audio.json podcast-data/data/refs_all.json podcast-data/data/
COPY podcast-data/data/cache_openlibrary.json podcast-data/data/cache_mcu.json podcast-data/data/cache_dialnet.json podcast-data/data/
COPY podcast-data/extraccion/ podcast-data/extraccion/
RUN mkdir -p web/public/data && python3 podcast-data/scripts/14_build_web_data.py

FROM node:22-alpine AS build
WORKDIR /repo/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
COPY --from=datos /repo/web/public/data ./public/data
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/web/dist /usr/share/nginx/html
EXPOSE 80
