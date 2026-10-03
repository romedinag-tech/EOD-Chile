# 🚍 EOD Chile — Movilidad Urbana en Chile

Sitio web que explora y compara las **Encuestas Origen-Destino (EOD)** del MTT/SECTRA de las ciudades
de Chile, homologadas a un esquema común y expandidas con el factor de expansión de cada encuesta.

Es un **sitio estático**: HTML + JavaScript vanilla, sin backend ni dependencias que instalar. Los
indicadores vienen precalculados en JSON desde el repositorio de análisis.

## Qué incluye

Selector de ciudad (19 con microdato de viajes) y siete vistas:

- **Resumen** — KPIs de la ciudad: viajes diarios expandidos, viajes por persona, partición modal.
- **Movilidad** — partición modal, propósito del viaje, distribución horaria y distancia por tramos.
- **Demografía** — comportamiento por grupo etario, sexo y tipo de usuario.
- **Ingreso** — segmentación por quintil del hogar (sólo las ciudades que publican el dato).
- **Mapas** — generación y atracción por zona, líneas de deseo y matriz O-D interactiva (20 capas de
  zonificación, EPSG:4326).
- **Nacional** — panorama país: mapa de ciudades y comparación de indicadores.
- **Comparador** — partición modal, propósito e indicadores entre ciudades.

## Datos

19 ciudades con microdato de viajes homologado desde las bases Access del MTT (Calama no publica
microdato; Antofagasta tiene la base corrupta). Los totales están **expandidos con el factor de
expansión de la encuesta**, día laboral, **sin factor de subreporte** — la expansión es de la encuesta;
el subreporte es calibración del modelo y va aparte.

Cada ciudad declara contra qué cifra oficial se validó. En tres de ellas la partición modal está
contrastada **al entero contra el cuadro del informe de su propio estudio**: Linares (Cuadro N° 11-23),
San Antonio y Gran Valparaíso (Cuadro N° 17.26 de cada estudio), las tres con diferencia 0,00 pp. Donde
una encuesta no separa caminata de bicicleta y no hay cuadro oficial leído, el indicador se publica
como **s/d**, nunca como 0,0.

**Cada cifra es de un año distinto**: una EOD por ciudad, entre 2010 y 2023. Es un corte transversal,
no una serie temporal — no encadenar ciudades como si fueran años.

## Estructura

```
index.html            # el sitio
app.js                # lógica, gráficos y mapas (Leaflet)
theme.css             # tema
version.json          # versión publicada, qué cambió y cómo se validó
data/eod/             # index.json + un JSON de KPIs por ciudad
data/geojson/         # 20 capas de zonificación EOD (EPSG:4326)
```

## Ver en local

Servirlo por HTTP; con `file://` los mapas de Leaflet renderizan a 0 px:

```bash
python -X utf8 -m http.server 8000      # y abrir http://localhost:8000
```

## Fuente

Encuestas Origen-Destino de la Subsecretaría de Transportes / SECTRA, Ministerio de Transportes y
Telecomunicaciones de Chile. La homologación, la expansión y la validación contra las cifras oficiales
de cada estudio se hacen en el repositorio de análisis; acá sólo se muestran.
