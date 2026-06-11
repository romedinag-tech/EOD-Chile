# -*- coding: utf-8 -*-
"""Ranking de ciudades por indicador."""
import plotly.graph_objects as go
import streamlit as st

from eodlib import data as D

_FONT = 'Inter,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif'
IND = {
    'Viajes por persona': ('viajes_persona', '{:.2f}', '#1f4e79'),
    'Distancia mediana (km)': ('dist_mediana', '{:.1f}', '#1f8a86'),
    '% Transporte público': ('pct_publico', '{:.1f}%', '#1f4e79'),
    '% No motorizado': ('pct_no_motor', '{:.1f}%', '#1a9850'),
    '% Transporte privado': ('pct_privado', '{:.1f}%', '#d6453a'),
    '% Viajes al trabajo': ('pct_trabajo', '{:.1f}%', '#1f8a86'),
    '% Viajes al estudio': ('pct_estudio', '{:.1f}%', '#d96a1f'),
    'Viajes/día (total)': ('viajes_dia', '{:,.0f}', '#172430'),
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
                      paper_bgcolor='rgba(0,0,0,0)', xaxis_title=ind,
                      font=dict(family=_FONT, color='#172430'))
    fig.update_xaxes(showgrid=True, gridcolor='#eef3f9', linecolor='#e4eaf2',
                     tickfont=dict(size=12, color='#5e6e80'))
    fig.update_yaxes(tickfont=dict(size=12, color='#172430'))
    st.plotly_chart(fig, use_container_width=True, key='rank_bar')
