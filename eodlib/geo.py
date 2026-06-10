# -*- coding: utf-8 -*-
"""Acceso a datos geográficos: centroides de zona, polígonos (GeoJSON),
generación/atracción por zona y líneas de deseo."""
import os, json
import numpy as np
import pandas as pd
import streamlit as st

from eodlib.data import DATA

GEOJSON = os.path.join(DATA, 'geojson')


@st.cache_data(show_spinner=False)
def centroides():
    df = pd.read_parquet(os.path.join(DATA, 'zonas_centroides.parquet'))
    df['zona'] = df['zona'].astype('string')
    return df


@st.cache_data(show_spinner=False)
def geojson(ciudad):
    p = os.path.join(GEOJSON, f'{ciudad}.geojson')
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def tiene_geo(ciudad):
    return os.path.exists(os.path.join(GEOJSON, f'{ciudad}.geojson'))


def _znorm(s):
    return s.astype('string').str.replace(r'\.0$', '', regex=True)


def generacion_atraccion(d):
    """Viajes generados (origen) y atraídos (destino) por zona, con coords."""
    cen = centroides()
    cen = cen[cen['ciudad'] == d['ciudad'].iloc[0]]
    o = d.assign(zona=_znorm(d['zona_origen'])).groupby('zona')['factor'].sum().rename('generados')
    a = d.assign(zona=_znorm(d['zona_destino'])).groupby('zona')['factor'].sum().rename('atraidos')
    z = pd.concat([o, a], axis=1).fillna(0).reset_index()
    z = z.merge(cen, on='zona', how='left')
    return z


def lineas_deseo(d, top_n=150, interzonal=True):
    """Top pares O-D por viajes, con coords de centroide de origen y destino."""
    cen = centroides()
    cen = cen[cen['ciudad'] == d['ciudad'].iloc[0]][['zona', 'lon', 'lat']]
    g = d.assign(zo=_znorm(d['zona_origen']), zd=_znorm(d['zona_destino']))
    if interzonal:
        g = g[g['zo'] != g['zd']]
    pares = g.groupby(['zo', 'zd'])['factor'].sum().reset_index()
    pares = pares.merge(cen.rename(columns={'zona': 'zo', 'lon': 'lon_o', 'lat': 'lat_o'}), on='zo', how='left')
    pares = pares.merge(cen.rename(columns={'zona': 'zd', 'lon': 'lon_d', 'lat': 'lat_d'}), on='zd', how='left')
    pares = pares.dropna(subset=['lon_o', 'lon_d'])
    return pares.sort_values('factor', ascending=False).head(top_n)


def destinos_desde(d, zona_origen, top_n=12):
    """Destinos principales desde una zona origen (tabla + coords)."""
    cen = centroides()
    cen = cen[cen['ciudad'] == d['ciudad'].iloc[0]][['zona', 'lon', 'lat']]
    g = d.assign(zo=_znorm(d['zona_origen']), zd=_znorm(d['zona_destino']))
    g = g[g['zo'] == str(zona_origen)]
    dest = g.groupby('zd')['factor'].sum().reset_index().rename(columns={'zd': 'zona', 'factor': 'viajes'})
    dest = dest.merge(cen, on='zona', how='left').sort_values('viajes', ascending=False)
    return dest


def zonas_con_viajes(d):
    """Lista de zonas origen ordenadas por volumen (para selector)."""
    g = d.assign(zo=_znorm(d['zona_origen'])).groupby('zo')['factor'].sum().sort_values(ascending=False)
    return g.index.tolist()
