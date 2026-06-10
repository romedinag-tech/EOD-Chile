# -*- coding: utf-8 -*-
"""Ranking de ciudades por indicador."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from eodlib import data as D, metrics as M


INDICADORES = {
    '% Transporte público': ('modo_pp', 'Público'),
    '% No motorizado': ('modo_pp', 'No motorizado'),
    '% Transporte privado': ('modo_pp', 'Privado'),
    '% Viajes al trabajo': ('proposito_agregado_h', 'Trabajo'),
    '% Viajes al estudio': ('proposito_agregado_h', 'Estudio'),
}


@st.cache_data(show_spinner=False)
def _tabla_indicadores():
    cat = D.catalogo_ciudades()
    rows = []
    per = D.cargar_persona()
    for c in cat['ciudad']:
        d = D.viajes_ciudad(c)
        if d.empty:
            continue
        pm = M.particion(d, 'modo_pp', M.ORDEN_MODO)
        pp = M.particion(d, 'proposito_agregado_h', M.ORDEN_PROP)
        pob = float(per[per['ciudad'] == c]['factor'].sum())
        rows.append({'ciudad': c, 'anio': int(d['anio'].iloc[0]),
                     'Viajes/día': d['factor'].sum(),
                     'Viajes por persona': d['factor'].sum() / pob if pob else None,
                     '% Transporte público': pm.get('Público', 0),
                     '% No motorizado': pm.get('No motorizado', 0),
                     '% Transporte privado': pm.get('Privado', 0),
                     '% Viajes al trabajo': pp.get('Trabajo', 0),
                     '% Viajes al estudio': pp.get('Estudio', 0)})
    return pd.DataFrame(rows)


def render():
    st.subheader('Ranking de ciudades')
    tab = _tabla_indicadores()
    ind = st.selectbox('Ordenar por', ['Viajes por persona'] + list(INDICADORES.keys()))
    t = tab.sort_values(ind, ascending=False)
    fig = go.Figure(go.Bar(
        x=t[ind], y=t['ciudad'] + ' (' + t['anio'].astype(str) + ')', orientation='h',
        text=[f'{v:.1f}' for v in t[ind]], textposition='outside', marker_color='#4c78a8'))
    fig.update_layout(height=28 * len(t) + 80, margin=dict(l=10, r=30, t=10, b=10),
                      yaxis=dict(autorange='reversed'), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(t.set_index('ciudad').style.format({
        'Viajes/día': '{:,.0f}', 'Viajes por persona': '{:.2f}',
        **{k: '{:.1f}%' for k in INDICADORES}}), use_container_width=True)
