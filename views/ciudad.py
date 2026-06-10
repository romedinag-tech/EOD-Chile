# -*- coding: utf-8 -*-
"""Vista por ciudad: comportamiento de viajes, segmentable."""
import pandas as pd
import streamlit as st

from eodlib import data as D, metrics as M, viz


def _pob_hog(ciudad):
    per = D.cargar_persona(); hog = D.cargar_hogar()
    p = per[per['ciudad'] == ciudad]['factor']
    h = pd.to_numeric(hog[hog['ciudad'] == ciudad]['factor'], errors='coerce')
    return float(p.sum()), float(h.sum())


def render(ciudad, anio):
    st.subheader(f'{ciudad} · {int(anio)}')

    d0 = D.viajes_ciudad(ciudad)
    if d0.empty:
        st.info('Esta ciudad no tiene viajes disponibles (solo hogar/persona).')
        return
    pob, hog = _pob_hog(ciudad)

    # ---------- filtros de segmentación ----------
    with st.expander('🎛️ Segmentar viajes', expanded=False):
        c1, c2, c3 = st.columns(3)
        f_modo = c1.multiselect('Modo', M.ORDEN_MODO, default=[])
        f_prop = c2.multiselect('Propósito', M.ORDEN_PROP, default=[])
        f_eta = c3.multiselect('Grupo etario', M.ORDEN_ETARIO, default=[])
    d = d0.copy()
    if f_modo: d = d[d['modo_pp'].isin(f_modo)]
    if f_prop: d = d[d['proposito_agregado_h'].isin(f_prop)]
    if f_eta: d = d[d['grupo_etario'].isin(f_eta)]

    # ---------- KPIs ----------
    k = M.kpis(d, n_personas=pob, n_hogares=hog)
    c = st.columns(5)
    c[0].metric('Viajes/día (exp.)', f"{k['viajes_dia']:,.0f}".replace(',', '.'))
    c[1].metric('Viajes por persona', f"{k.get('viajes_persona', 0):.2f}")
    c[2].metric('Viajes por hogar', f"{k.get('viajes_hogar', 0):.2f}")
    c[3].metric('% Transporte público', f"{k['pct_publico']:.1f}%")
    c[4].metric('% No motorizado', f"{k['pct_no_motor']:.1f}%")
    st.divider()

    # ---------- partición modal + propósito ----------
    a, b = st.columns(2)
    with a:
        st.plotly_chart(viz.barra_modal(M.particion(d, 'modo_pp', M.ORDEN_MODO),
                        'Partición modal'), use_container_width=True)
    with b:
        st.plotly_chart(viz.dona(M.particion(d, 'proposito_agregado_h', M.ORDEN_PROP),
                        'Propósito del viaje', viz.COLOR_PROP), use_container_width=True)

    # ---------- distribución horaria segmentable ----------
    st.markdown('#### Distribución horaria')
    seg = st.radio('Segmentar por', ['(ninguno)', 'Modo', 'Propósito'],
                   horizontal=True, key='seg_hora')
    if seg == 'Modo':
        tab = M.distribucion_horaria(d, 'modo_pp')[[m for m in M.ORDEN_MODO if m in d['modo_pp'].unique()]]
        st.plotly_chart(viz.lineas_horarias(tab, None, viz.COLOR_MODO), use_container_width=True)
    elif seg == 'Propósito':
        tab = M.distribucion_horaria(d, 'proposito_agregado_h')
        st.plotly_chart(viz.lineas_horarias(tab, None, viz.COLOR_PROP), use_container_width=True)
    else:
        st.plotly_chart(viz.lineas_horarias(M.distribucion_horaria(d)), use_container_width=True)

    # ---------- tendencias por grupo etario ----------
    st.markdown('#### Tendencias por grupo etario')
    a, b = st.columns(2)
    with a:
        t = M.tabla_cruzada(d, 'grupo_etario', 'modo_pp', 'fila').reindex(M.ORDEN_ETARIO).dropna(how='all')
        t = t[[m for m in M.ORDEN_MODO if m in t.columns]]
        st.plotly_chart(viz.barras_apiladas(t, 'Partición modal por edad', viz.COLOR_MODO),
                        use_container_width=True)
    with b:
        t = M.tabla_cruzada(d, 'grupo_etario', 'proposito_agregado_h', 'fila').reindex(M.ORDEN_ETARIO).dropna(how='all')
        t = t[[p for p in M.ORDEN_PROP if p in t.columns]]
        st.plotly_chart(viz.barras_apiladas(t, 'Propósito por edad', viz.COLOR_PROP),
                        use_container_width=True)

    # ---------- comportamiento por tipo de usuario ----------
    st.markdown('#### Comportamiento por tipo de usuario')
    a, b = st.columns(2)
    with a:
        t = M.tabla_cruzada(d, 'tipo_usuario', 'modo_pp', 'fila').reindex(M.ORDEN_USUARIO).dropna(how='all')
        t = t[[m for m in M.ORDEN_MODO if m in t.columns]]
        st.plotly_chart(viz.barras_apiladas(t, 'Partición modal por tipo de usuario', viz.COLOR_MODO),
                        use_container_width=True)
    with b:
        share = (d.dropna(subset=['tipo_usuario']).groupby('tipo_usuario')['factor'].sum())
        share = (share / share.sum() * 100).reindex(M.ORDEN_USUARIO).dropna().round(1)
        st.plotly_chart(viz.dona(share, '% de viajes por tipo de usuario'), use_container_width=True)
