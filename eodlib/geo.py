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


SENT_COM = {'-1', 'nan', '', 'none', '0', 'sin informacion'}


@st.cache_data(show_spinner=False)
def zona_comuna(ciudad):
    """Mapeo zona -> comuna (moda de la comuna observada en los viajes de esa zona)."""
    from eodlib.data import cargar_viajes
    d = cargar_viajes(); d = d[d['ciudad'] == ciudad]
    o = d[['zona_origen', 'comuna_origen']].rename(columns={'zona_origen': 'zona', 'comuna_origen': 'comuna'})
    de = d[['zona_destino', 'comuna_destino']].rename(columns={'zona_destino': 'zona', 'comuna_destino': 'comuna'})
    z = pd.concat([o, de], ignore_index=True)
    z['zona'] = _znorm(z['zona']); z['comuna'] = _znorm(z['comuna'])
    z = z[z['comuna'].str.lower().fillna('nan').isin(SENT_COM) == False].dropna(subset=['zona', 'comuna'])
    if z.empty:
        return {}
    m = z.groupby('zona')['comuna'].agg(lambda s: s.mode().iloc[0] if len(s.mode()) else None)
    return m.dropna().to_dict()


@st.cache_data(show_spinner=False)
def centroides_comuna(ciudad):
    """Centroide de cada comuna = promedio de los centroides de sus zonas."""
    cen = centroides()
    cen = cen[cen['ciudad'] == ciudad].copy()
    zc = zona_comuna(ciudad)
    cen['comuna'] = cen['zona'].map(zc)
    cc = cen.dropna(subset=['comuna']).groupby('comuna')[['lon', 'lat']].mean().reset_index()
    return cc


def n_comunas(ciudad):
    return len(centroides_comuna(ciudad))


@st.cache_data(show_spinner=False)
def comuna_disponible(ciudad):
    """True si la ciudad tiene un campo de comuna utilizable (no texto libre).
    Excluye casos como Talca/Curicó/Linares donde 'comuna' trae texto con muchos valores."""
    from eodlib.data import cargar_viajes
    d = cargar_viajes(); d = d[d['ciudad'] == ciudad]
    co = _znorm(d['comuna_origen'])
    raw = co[~co.str.lower().fillna('nan').isin(SENT_COM)].nunique()
    nz = _znorm(d['zona_origen']).nunique()
    interno = len(centroides_comuna(ciudad))
    return interno >= 2 and raw <= max(40, nz * 0.5)


def generacion_atraccion(d, nivel='zona'):
    """Viajes generados (origen) y atraídos (destino) por zona/comuna, con coords."""
    co, cd, cen = _unidades(d, nivel)
    cen = cen.rename(columns={'u': 'zona'})
    o = d.assign(zona=_znorm(d[co])).groupby('zona')['factor'].sum().rename('generados')
    a = d.assign(zona=_znorm(d[cd])).groupby('zona')['factor'].sum().rename('atraidos')
    z = pd.concat([o, a], axis=1).fillna(0).reset_index()
    z = z.merge(cen, on='zona', how='left')
    return z


def _unidades(d, nivel):
    """(columna_origen, columna_destino, centroides) según nivel zona|comuna."""
    ciudad = d['ciudad'].iloc[0]
    if nivel == 'comuna':
        cc = centroides_comuna(ciudad).rename(columns={'comuna': 'u'})
        return 'comuna_origen', 'comuna_destino', cc
    cen = centroides()
    cen = cen[cen['ciudad'] == ciudad][['zona', 'lon', 'lat']].rename(columns={'zona': 'u'})
    return 'zona_origen', 'zona_destino', cen


def lineas_deseo(d, top_n=150, interzonal=True, nivel='zona'):
    """Top pares O-D por viajes, con coords de centroide de origen y destino."""
    co, cd, cen = _unidades(d, nivel)
    g = d.assign(o=_znorm(d[co]), dd=_znorm(d[cd]))
    if interzonal:
        g = g[g['o'] != g['dd']]
    pares = g.groupby(['o', 'dd'])['factor'].sum().reset_index()
    pares = pares.merge(cen.rename(columns={'u': 'o', 'lon': 'lon_o', 'lat': 'lat_o'}), on='o', how='left')
    pares = pares.merge(cen.rename(columns={'u': 'dd', 'lon': 'lon_d', 'lat': 'lat_d'}), on='dd', how='left')
    pares = pares.dropna(subset=['lon_o', 'lon_d']).rename(columns={'o': 'zo', 'dd': 'zd'})
    return pares.sort_values('factor', ascending=False).head(top_n)


def destinos_desde(d, origen, nivel='zona', top_n=12):
    """Destinos principales desde una zona/comuna origen (tabla + coords)."""
    co, cd, cen = _unidades(d, nivel)
    cen = cen.rename(columns={'u': 'zona'})
    g = d.assign(o=_znorm(d[co]), dd=_znorm(d[cd]))
    g = g[g['o'] == str(origen)]
    dest = g.groupby('dd')['factor'].sum().reset_index().rename(columns={'dd': 'zona', 'factor': 'viajes'})
    dest = dest.merge(cen, on='zona', how='left').sort_values('viajes', ascending=False)
    return dest


def unidades_con_viajes(d, nivel='zona'):
    """Lista de zonas/comunas origen ordenadas por volumen (para selector).
    En nivel comuna se restringe a las que tienen centroide (comunas internas)."""
    co, _, _ = _unidades(d, nivel)
    g = d.assign(o=_znorm(d[co])).groupby('o')['factor'].sum().sort_values(ascending=False)
    units = [u for u in g.index.tolist() if u and u.lower() not in SENT_COM]
    if nivel == 'comuna':
        validas = set(centroides_comuna(d['ciudad'].iloc[0])['comuna'].astype(str))
        units = [u for u in units if u in validas]
    return units


# alias retro-compatible
def zonas_con_viajes(d):
    return unidades_con_viajes(d, 'zona')
