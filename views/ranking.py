# -*- coding: utf-8 -*-
"""Ranking de ciudades por indicador."""
import plotly.graph_objects as go
import streamlit as st

from eodlib import data as D

IND = {
    'Viajes por persona': ('viajes_persona', '{:.2f}', '#1f6feb'),
    'Distancia mediana (km)': ('dist_mediana', '{:.1f}', '#0891b2'),
    '% Transporte público': ('pct_publico', '{:.1f}%', '#4c78a8'),
    '% No motorizado': ('pct_no_motor', '{:.1f}%', '#16a34a'),
    '% Transporte privado': ('pct_privado', '{:.1f}%', '#e45756'),
    '% Viajes al trabajo': ('pct_trabajo', '{:.1f}%', '#7c3aed'),
    '% Viajes al estudio': ('pct_estudio', '{:.1f}%', '#f58518'),
    'Viajes/día (total)': ('viajes_dia', '{:,.0f}', '#334155'),
}


def render():
    t = D.tabla_resumen()
    c1, c2 = st.columns([2, 1])
    ind = c1.selectbox('Ordenar por', list(IND))
    asc = c2.toggle('Ascendente', value=False)
    col, fmt, color = IND[ind]
    ts = t.sort_values(col, ascending=asc)
    etq = ts['ciudad'] + '  (' + ts['anio'].astype(str) + ')'
    fig = go.Figure(go.Bar(
        x=ts[col], y=etq, orientation='h', marker_color=color,
        text=[fmt.format(v).replace(',', '.') for v in ts[col]], textposition='outside'))
    fig.update_layout(height=34 * len(ts) + 60, margin=dict(l=10, r=40, t=10, b=10),
                      yaxis=dict(autorange='reversed'), plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_title=ind)
    st.plotly_chart(fig, use_container_width=True, key='rank_bar')
