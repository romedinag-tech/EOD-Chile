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
