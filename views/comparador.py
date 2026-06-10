# -*- coding: utf-8 -*-
"""Comparador entre ciudades."""
import pandas as pd
import streamlit as st

from eodlib import data as D, metrics as M, viz


def render():
    st.subheader('Comparador entre ciudades')
    cat = D.catalogo_ciudades()
    todas = cat['ciudad'].tolist()
    sel = st.multiselect('Ciudades a comparar', todas,
                         default=todas[:min(5, len(todas))])
    if len(sel) < 2:
        st.info('Selecciona al menos 2 ciudades.')
        return
    dim = st.radio('Indicador', ['Partición modal', 'Propósito'], horizontal=True)

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
    st.plotly_chart(viz.barras_apiladas(tab, f'{dim} por ciudad', colores),
                    use_container_width=True)
    st.dataframe(tab.style.format('{:.1f}%'), use_container_width=True)
