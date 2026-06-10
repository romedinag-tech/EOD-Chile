# 🚍 EOD Chile — Dashboard de Encuestas Origen-Destino

Dashboard interactivo (Streamlit) para explorar y comparar las **Encuestas
Origen-Destino (EOD)** de las ciudades de Chile, homologadas a un esquema común y
expandidas con sus factores de expansión corregidos por sesgo.

## Qué incluye

- **Menú lateral**: selección de región / ciudad / año de la encuesta.
- **Menú superior** (herramientas):
  - **Resumen** — panorama nacional: KPIs país, mapa de ciudades (tamaño ∝ viajes,
    color ∝ % público), partición modal promedio y tabla comparada por ciudad.
  - **Ciudad** — comportamiento de viajes de una ciudad, en pestañas:
    *Resumen · Modos y propósitos · Distancia · Demografía · Ingreso · Mapas*.
    Incluye partición modal, propósito, distribución horaria, **histograma por distancia**
    (tramos 0-1…6+ km), tendencias por grupo etario y tipo de usuario, **segmentación por
    quintil de ingreso**, y mapas de **generación/atracción**, **líneas de deseo** y
    **matriz O/D interactiva** (zona origen → destinos). Filtros de segmentación globales.
  - **Comparador** — partición modal/propósito, indicadores y dispersión entre ciudades.
  - **Ranking** — ordena las ciudades por indicador (viajes por persona, % público, etc.).

## Datos

18 ciudades con viajes validados (factor de expansión ≈ catálogo oficial), homologadas
desde bases Access/xlsx del MTT. Columnas canónicas de modo (`modo_pp`), propósito
(`proposito_agregado_h`), grupo etario, tipo de usuario y hora del día.

Los datos viven en `data/` (Parquet). Detalle metodológico de la homologación y la
depuración en el repositorio de análisis.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud

1. Entra a https://share.streamlit.io y conecta tu cuenta de GitHub.
2. "New app" → repo `romedinag-tech/EOD-Chile`, branch `main`, archivo `app.py`.
3. Deploy. (Los Parquet ya están en el repo, no requiere configuración extra.)

## Estructura

```
app.py                # entrypoint: sidebar + menú superior
views/                # Ciudad, Comparador, Ranking
eodlib/               # data (carga), metrics (ponderadas), viz (Plotly)
data/                 # viajes_analiticos / hogar / persona (Parquet) + índice
```

## Roadmap

- [x] Distancias de viaje + histograma por tramos (0-1, 1-2, … 6+ km), segmentable.
- [x] Mapas: generación / atracción por zona y **líneas de deseo** (20 ciudades).
- [x] Matriz O/D interactiva (seleccionar zona origen → destinos).
- [x] Segmentación por ingreso del hogar (quintiles, 10 ciudades con dato).
- [x] Resumen nacional + rediseño profesional (tema, KPIs, pestañas).
- [ ] Ingreso del hogar para EOD 2010-13 (derivar desde ingreso de personas).
- [ ] Exportar gráficos/tablas y descargar datos filtrados.
