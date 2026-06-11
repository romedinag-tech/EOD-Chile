# -*- coding: utf-8 -*-
"""Comparador entre ciudades."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from eodlib import data as D, metrics as M, viz, ui


def render():
    cat = D.catalogo_ciudades()
    todas = cat['ciudad'].tolist()
    sel = st.multiselect('Ciudades a comparar', todas, default=todas[:min(6, len(todas))])
    if len(sel) < 2:
        st.info('Selecciona al menos 2 ciudades.')
        return

    t = D.tabla_resumen()
    t = t[t['ciudad'].isin(sel)].set_index('ciudad').reindex(sel)

    tab1, tab2, tab3 = st.tabs(['Partición modal', 'Indicadores', 'Dispersión'])

    with tab1:
        dim = ui.seg('Variable', ['Partición modal', 'Propósito'], key='cmp_dim')
        filas = {}
        for c in sel:
            d = D.viajes_ciudad(c)
            if d.empty:
                continue
            if dim == 'Partición modal':
                filas[c] = M.particion(d, 'modo_pp', M.ORDEN_MODO)
            else:
                filas[c] = M.particion(d, 'proposito_agregado_h', M.ORDEN_PROP)
        tab = pd.DataFrame(filas).T.fillna(0)
        colores = viz.COLOR_MODO if dim == 'Partición modal' else viz.COLOR_PROP
        orden = M.ORDEN_MODO if dim == 'Partición modal' else M.ORDEN_PROP
        tab = tab[[c for c in orden if c in tab.columns]]
        st.plotly_chart(viz.barras_apiladas(tab, f'{dim} por ciudad', colores, '% de viajes'),
                        use_container_width=True, key='cmp_modal')
        st.dataframe(tab.style.format('{:.1f}%'), use_container_width=True)

    with tab2:
        ind = {'Viajes por persona': 'viajes_persona', 'Distancia mediana (km)': 'dist_mediana',
               '% Transporte privado': 'pct_privado', '% Transporte público': 'pct_publico',
               '% No motorizado': 'pct_no_motor'}
        elegidos = st.multiselect('Indicadores', list(ind), default=list(ind)[:3])
        fig = go.Figure()
        for nombre in elegidos:
            fig.add_bar(name=nombre, x=t.index, y=t[ind[nombre]])
        fig.update_layout(barmode='group', height=420, margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation='h', y=-0.2), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, key='cmp_ind')

    with tab3:
        ui.section('Motorización vs. transporte público',
                   'Cada punto es una ciudad. Tamaño ∝ viajes/día.')
        fig = go.Figure(go.Scatter(
            x=t['pct_publico'], y=t['pct_privado'], mode='markers+text', text=t.index,
            textposition='top center',
            marker=dict(size=10 + 30 * (t['viajes_dia'] / t['viajes_dia'].max()),
                        color=t['viajes_persona'], colorscale='Viridis', showscale=True,
                        colorbar=dict(title='v/pers'))))
        fig.update_xaxes(title='% Transporte público', ticksuffix='%')
        fig.update_yaxes(title='% Transporte privado', ticksuffix='%')
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, key='cmp_disp')
