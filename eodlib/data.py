# -*- coding: utf-8 -*-
"""Carga y acceso a los datos EOD homologados para el dashboard."""
import os
import numpy as np
import pandas as pd
import streamlit as st

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Ciudades con factor de viajes validado (ratio ~1.0). Para otras se avisa.
RATIO_NOTA = {
    'Gran Santiago': 'Factor de viajes 0.80 (sub-reporte propio de la EOD 2012).',
    'Curicó': 'Sobre-expande ~1.2× (diferencia de definición del catálogo).',
    'Linares': 'Factores de hogar/persona ~2× (incluyen laboral+finde); viajes laboral OK.',
}
MULTIDIA = {'Curicó', 'Linares'}  # el viaje mezcla laboral+finde -> filtrar tipo_dia=1


@st.cache_data(show_spinner=False)
def cargar_viajes():
    df = pd.read_parquet(os.path.join(DATA, 'viajes_analiticos.parquet'))
    df['factor'] = pd.to_numeric(df['factor'], errors='coerce')
    df['tiempo_viaje'] = pd.to_numeric(df['tiempo_viaje'], errors='coerce')
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
    df['anio'] = pd.to_numeric(df['anio'], errors='coerce').astype('Int64')
    return df


@st.cache_data(show_spinner=False)
def cargar_hogar():
    return pd.read_parquet(os.path.join(DATA, 'hogar.parquet'))


@st.cache_data(show_spinner=False)
def cargar_persona():
    df = pd.read_parquet(os.path.join(DATA, 'persona.parquet'))
    df['factor'] = pd.to_numeric(df['factor'], errors='coerce')
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
    return df


@st.cache_data(show_spinner=False)
def indice():
    return pd.read_csv(os.path.join(DATA, 'indice_eod.csv'))


@st.cache_data(show_spinner=False)
def catalogo_ciudades():
    """Lista (region, ciudad, anio) de ciudades con viajes disponibles, ordenada."""
    df = cargar_viajes()
    cat = (df[['region', 'ciudad', 'anio']].drop_duplicates()
           .sort_values(['region', 'ciudad']).reset_index(drop=True))
    return cat


def viajes_ciudad(ciudad, solo_laboral=True, solo_completos=True):
    """Devuelve los viajes de una ciudad, filtrando a día laboral expandible."""
    df = cargar_viajes()
    d = df[df['ciudad'] == ciudad].copy()
    if solo_completos:
        d = d[d['factor'] > 0]
    if solo_laboral and ciudad in MULTIDIA:
        d = d[d['tipo_dia'].astype('string').isin(['1', '1.0'])]
    return d


def total_expandido(d):
    return float(pd.to_numeric(d['factor'], errors='coerce').sum())


@st.cache_data(show_spinner=False)
def conteos(ciudad):
    """(poblacion, hogares) expandidos de la ciudad."""
    per = cargar_persona(); hog = cargar_hogar()
    pob = float(per[per['ciudad'] == ciudad]['factor'].sum())
    h = pd.to_numeric(hog[hog['ciudad'] == ciudad]['factor'], errors='coerce').sum()
    return pob, float(h)


@st.cache_data(show_spinner=False)
def tabla_resumen():
    """Tabla de indicadores por ciudad (para Resumen, Ranking y Comparador)."""
    from eodlib import metrics as M
    v = cargar_viajes(); per = cargar_persona()
    rows = []
    for c, d0 in v.groupby('ciudad'):
        d = d0[d0['factor'] > 0]
        if c in MULTIDIA:
            d = d[d['tipo_dia'].astype('string').isin(['1', '1.0'])]
        if d.empty:
            continue
        pm = M.particion(d, 'modo_pp', M.ORDEN_MODO)
        pp = M.particion(d, 'proposito_agregado_h', M.ORDEN_PROP)
        pob = float(per[per['ciudad'] == c]['factor'].sum())
        dist = pd.to_numeric(d['distancia_km'], errors='coerce')
        rows.append({
            'ciudad': c, 'region': d['region'].iloc[0], 'anio': int(d['anio'].iloc[0]),
            'viajes_dia': float(d['factor'].sum()),
            'poblacion': pob,
            'viajes_persona': float(d['factor'].sum()) / pob if pob else None,
            'dist_mediana': float(dist.median()),
            'pct_privado': float(pm.get('Privado', 0)),
            'pct_publico': float(pm.get('Público', 0)),
            'pct_no_motor': float(pm.get('No motorizado', 0)),
            'pct_trabajo': float(pp.get('Trabajo', 0)),
            'pct_estudio': float(pp.get('Estudio', 0)),
        })
    return pd.DataFrame(rows).sort_values('ciudad').reset_index(drop=True)
