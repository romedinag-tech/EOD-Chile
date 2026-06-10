# -*- coding: utf-8 -*-
"""Métricas ponderadas por factor de expansión sobre los viajes EOD."""
import numpy as np
import pandas as pd

ORDEN_MODO = ['Privado', 'Público', 'No motorizado', 'Combinado', 'Otro']
ORDEN_PROP = ['Trabajo', 'Estudio', 'Otro']
ORDEN_ETARIO = ['0-5', '6-14', '15-24', '25-44', '45-64', '65+']
ORDEN_USUARIO = ['Niño/a', 'Joven', 'Adulto productivo', 'Adulto mayor']
ORDEN_TRAMO = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6+']
ORDEN_QUINTIL = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']


def particion(d, dim, orden=None, dropna=True):
    """% de viajes (ponderado por factor) por categoría de `dim`."""
    g = d.dropna(subset=[dim]) if dropna else d
    s = g.groupby(dim, observed=True)['factor'].sum()
    if s.sum() == 0:
        return pd.Series(dtype=float)
    s = (s / s.sum() * 100)
    if orden:
        s = s.reindex([o for o in orden if o in s.index]).dropna()
    return s.round(1)


def tabla_cruzada(d, fila, col, normaliza='fila'):
    """Tabla cruzada ponderada (%); normaliza por 'fila', 'col' o None (totales)."""
    t = d.pivot_table(index=fila, columns=col, values='factor', aggfunc='sum', observed=True).fillna(0)
    if normaliza == 'fila':
        t = t.div(t.sum(axis=1), axis=0) * 100
    elif normaliza == 'col':
        t = t.div(t.sum(axis=0), axis=1) * 100
    return t.round(1)


def kpis(d, n_personas=None, n_hogares=None):
    """Indicadores resumen de una ciudad (viajes ya filtrados a laboral/expandibles)."""
    tot = float(d['factor'].sum())
    k = {'viajes_dia': tot}
    if n_personas:
        k['viajes_persona'] = tot / n_personas
    if n_hogares:
        k['viajes_hogar'] = tot / n_hogares
    pm = particion(d, 'modo_pp', ORDEN_MODO)
    k['pct_publico'] = float(pm.get('Público', 0))
    k['pct_no_motor'] = float(pm.get('No motorizado', 0))
    k['pct_privado'] = float(pm.get('Privado', 0))
    return k


def distribucion_horaria(d, segmento=None):
    """Viajes por hora del día (%), opcionalmente segmentado por una columna."""
    g = d.dropna(subset=['hora'])
    g = g.assign(hora=g['hora'].astype(int))
    if segmento:
        t = g.pivot_table(index='hora', columns=segmento, values='factor', aggfunc='sum', observed=True).fillna(0)
        return (t / t.values.sum() * 100).round(2)
    s = g.groupby('hora')['factor'].sum()
    return (s / s.sum() * 100).round(2)
