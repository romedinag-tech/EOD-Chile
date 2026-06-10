# -*- coding: utf-8 -*-
"""Resumen nacional: panorama de todas las ciudades."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from eodlib import data as D, geo, ui, viz


def _mapa_ciudades(t):
    cen = geo.centroides()
    cc = cen.groupby('ciudad')[['lon', 'lat']].mean().reset_index()
    m = t.merge(cc, on='ciudad', how='left').dropna(subset=['lon', 'lat'])
    fig = go.Figure(go.Scattermapbox(
        lon=m['lon'], lat=m['lat'], mode='markers',
        marker=dict(size=8 + 26 * (m['viajes_dia'] / m['viajes_dia'].max()),
                    color=m['pct_publico'], colorscale='Viridis', showscale=True,
                    colorbar=dict(title='% público')),
        text=[f"{r.ciudad} ({r.anio})<br>{r.viajes_dia:,.0f} viajes/día<br>"
              f"{r.pct_publico:.0f}% público · {r.viajes_persona:.2f} v/pers"
              .replace(',', '.') for r in m.itertuples()],
        hoverinfo='text'))
    fig.update_layout(mapbox=dict(style='open-street-map',
                      center=dict(lat=-37, lon=-71.5), zoom=3.4),
                      height=620, margin=dict(l=0, r=0, t=0, b=0))
    return fig


def render():
    t = D.tabla_resumen()
    ui.section('Panorama nacional', f'{len(t)} ciudades con Encuesta Origen-Destino homologada.')
    ui.kpis([
        ('Ciudades', f'{len(t)}'),
        ('Viajes/día (suma)', ui.fmt_miles(t['viajes_dia'].sum())),
        ('Población cubierta', ui.fmt_miles(t['poblacion'].sum())),
        ('Viajes/persona (prom.)', f"{t['viajes_persona'].mean():.2f}"),
        ('% público (prom.)', f"{t['pct_publico'].mean():.0f}%"),
        ('% no motorizado (prom.)', f"{t['pct_no_motor'].mean():.0f}%"),
    ])

    a, b = st.columns([3, 2])
    with a:
        ui.section('Mapa de ciudades', 'Tamaño ∝ viajes/día · color ∝ % transporte público.')
        st.plotly_chart(_mapa_ciudades(t), use_container_width=True)
    with b:
        ui.section('Partición modal promedio')
        prom = t[['pct_privado', 'pct_publico', 'pct_no_motor']].mean()
        s = pd.Series({'Privado': prom['pct_privado'], 'Público': prom['pct_publico'],
                       'No motorizado': prom['pct_no_motor']})
        st.plotly_chart(viz.dona(s.round(1), None, viz.COLOR_MODO), use_container_width=True)
        st.caption('Promedio simple entre ciudades (no ponderado).')

    ui.section('Indicadores por ciudad')
    show = t[['ciudad', 'anio', 'viajes_dia', 'viajes_persona', 'dist_mediana',
              'pct_privado', 'pct_publico', 'pct_no_motor', 'pct_trabajo', 'pct_estudio']].copy()
    show.columns = ['Ciudad', 'Año', 'Viajes/día', 'Viajes/pers.', 'Dist. mediana (km)',
                    '% Privado', '% Público', '% No motor.', '% Trabajo', '% Estudio']
    st.dataframe(show.style.format({
        'Viajes/día': '{:,.0f}', 'Viajes/pers.': '{:.2f}', 'Dist. mediana (km)': '{:.1f}',
        '% Privado': '{:.1f}', '% Público': '{:.1f}', '% No motor.': '{:.1f}',
        '% Trabajo': '{:.1f}', '% Estudio': '{:.1f}'}).background_gradient(
        subset=['% Público'], cmap='Blues'), hide_index=True, use_container_width=True, height=560)
