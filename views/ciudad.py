# -*- coding: utf-8 -*-
"""Vista por ciudad: comportamiento de viajes, segmentable, con pestañas."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from eodlib import data as D, metrics as M, viz, geo, geomap, ui

Q_LABEL = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4', 5: 'Q5'}


def _bar(serie, ytit='% de viajes', color='#1f6feb'):
    fig = go.Figure(go.Bar(x=list(serie.index), y=list(serie.values), marker_color=color,
                    text=[f'{v:.1f}%' for v in serie.values], textposition='outside'))
    fig.update_yaxes(title=ytit, ticksuffix='%'); fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='rgba(0,0,0,0)')
    return fig


def render(ciudad, anio):
    d0 = D.viajes_ciudad(ciudad)
    pob, hog = D.conteos(ciudad)
    reg = d0['region'].iloc[0] if not d0.empty else ''
    ui.chips([reg, f'EOD {int(anio)}', f'{ui.fmt_miles(pob)} hab.', f'{ui.fmt_miles(hog)} hogares'])

    if d0.empty:
        st.info('Esta ciudad solo tiene datos de hogar/persona (sin viajes disponibles).')
        return

    with st.expander('🎛️  Segmentar viajes', expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        f_modo = c1.multiselect('Modo', M.ORDEN_MODO)
        f_prop = c2.multiselect('Propósito', M.ORDEN_PROP)
        f_eta = c3.multiselect('Grupo etario', M.ORDEN_ETARIO)
        f_usu = c4.multiselect('Tipo usuario', M.ORDEN_USUARIO)
    d = d0.copy()
    if f_modo: d = d[d['modo_pp'].isin(f_modo)]
    if f_prop: d = d[d['proposito_agregado_h'].isin(f_prop)]
    if f_eta: d = d[d['grupo_etario'].isin(f_eta)]
    if f_usu: d = d[d['tipo_usuario'].isin(f_usu)]

    k = M.kpis(d, n_personas=pob, n_hogares=hog)
    dist = pd.to_numeric(d['distancia_km'], errors='coerce')
    ui.kpis([
        ('Viajes/día (exp.)', ui.fmt_miles(k['viajes_dia'])),
        ('Viajes por persona', f"{k.get('viajes_persona', 0):.2f}"),
        ('Viajes por hogar', f"{k.get('viajes_hogar', 0):.2f}"),
        ('Distancia mediana', f"{dist.median():.1f} km" if dist.notna().any() else '—'),
        ('% T. público', f"{k['pct_publico']:.1f}%"),
        ('% No motorizado', f"{k['pct_no_motor']:.1f}%"),
    ])

    tabs = st.tabs(['📊 Resumen', '🚦 Modos y propósitos', '📏 Distancia',
                    '👥 Demografía', '💰 Ingreso', '🗺️ Mapas'])

    # ---- Resumen ----
    with tabs[0]:
        a, b = st.columns(2)
        a.plotly_chart(viz.barra_modal(M.particion(d, 'modo_pp', M.ORDEN_MODO), 'Partición modal'),
                       use_container_width=True, key='c_modal')
        b.plotly_chart(viz.dona(M.particion(d, 'proposito_agregado_h', M.ORDEN_PROP),
                       'Propósito del viaje', viz.COLOR_PROP), use_container_width=True, key='c_prop')
        if dist.notna().any():
            ui.section('Distribución por distancia')
            st.plotly_chart(_bar(M.particion(d.dropna(subset=['tramo_dist']), 'tramo_dist', M.ORDEN_TRAMO),
                            'tramo (km) · % de viajes'), use_container_width=True, key='c_dist_res')

    # ---- Modos y propósitos ----
    with tabs[1]:
        ui.section('Distribución horaria', 'Viajes a lo largo del día, segmentable.')
        seg = st.radio('Segmentar por', ['(ninguno)', 'Modo', 'Propósito'], horizontal=True, key='seg_hora')
        if seg == 'Modo':
            tab = M.distribucion_horaria(d, 'modo_pp')
            tab = tab[[m for m in M.ORDEN_MODO if m in tab.columns]]
            st.plotly_chart(viz.lineas_horarias(tab, None, viz.COLOR_MODO), use_container_width=True, key='c_hora_m')
        elif seg == 'Propósito':
            st.plotly_chart(viz.lineas_horarias(M.distribucion_horaria(d, 'proposito_agregado_h'),
                            None, viz.COLOR_PROP), use_container_width=True, key='c_hora_p')
        else:
            st.plotly_chart(viz.lineas_horarias(M.distribucion_horaria(d)), use_container_width=True, key='c_hora_n')
        ui.section('Propósito por modo')
        t = M.tabla_cruzada(d, 'modo_pp', 'proposito_agregado_h', 'fila').reindex(M.ORDEN_MODO).dropna(how='all')
        t = t[[p for p in M.ORDEN_PROP if p in t.columns]]
        st.plotly_chart(viz.barras_apiladas(t, None, viz.COLOR_PROP), use_container_width=True, key='c_prop_modo')

    # ---- Distancia ----
    with tabs[2]:
        if not dist.notna().any():
            st.info('Sin zonificación para calcular distancias en esta ciudad.')
        else:
            ui.section('Distribución por distancia de viaje',
                       'Tramos de 0-1, 1-2, … 6+ km. Segmentable.')
            seg_d = st.radio('Segmentar por', ['(ninguno)', 'Modo', 'Propósito', 'Tipo usuario', 'Quintil ingreso'],
                             horizontal=True, key='seg_dist')
            dd = d.dropna(subset=['tramo_dist'])
            if seg_d == '(ninguno)':
                st.plotly_chart(_bar(M.particion(dd, 'tramo_dist', M.ORDEN_TRAMO), 'tramo (km) · % de viajes'),
                                use_container_width=True, key='c_dist_seg0')
            else:
                cmap = {'Modo': ('modo_pp', M.ORDEN_MODO, viz.COLOR_MODO),
                        'Propósito': ('proposito_agregado_h', M.ORDEN_PROP, viz.COLOR_PROP),
                        'Tipo usuario': ('tipo_usuario', M.ORDEN_USUARIO, None),
                        'Quintil ingreso': ('quintil_label', M.ORDEN_QUINTIL, None)}
                col, orden, colores = cmap[seg_d]
                ddx = dd.assign(quintil_label=dd['quintil_ingreso'].map(Q_LABEL)) if 'quintil' in col else dd
                if col == 'quintil_label' and ddx['quintil_label'].isna().all():
                    st.info('Esta ciudad no tiene datos de ingreso.')
                else:
                    t = M.tabla_cruzada(ddx, 'tramo_dist', col, 'fila').reindex(M.ORDEN_TRAMO).dropna(how='all')
                    t = t[[c for c in orden if c in t.columns]]
                    st.plotly_chart(viz.barras_apiladas(t, None, colores), use_container_width=True, key='c_dist_seg1')

    # ---- Demografía ----
    with tabs[3]:
        ui.section('Tendencias por grupo etario')
        a, b = st.columns(2)
        t = M.tabla_cruzada(d, 'grupo_etario', 'modo_pp', 'fila').reindex(M.ORDEN_ETARIO).dropna(how='all')
        a.plotly_chart(viz.barras_apiladas(t[[m for m in M.ORDEN_MODO if m in t.columns]],
                       'Partición modal por edad', viz.COLOR_MODO), use_container_width=True, key='c_eta_modal')
        t = M.tabla_cruzada(d, 'grupo_etario', 'proposito_agregado_h', 'fila').reindex(M.ORDEN_ETARIO).dropna(how='all')
        b.plotly_chart(viz.barras_apiladas(t[[p for p in M.ORDEN_PROP if p in t.columns]],
                       'Propósito por edad', viz.COLOR_PROP), use_container_width=True, key='c_eta_prop')
        ui.section('Comportamiento por tipo de usuario')
        a, b = st.columns(2)
        t = M.tabla_cruzada(d, 'tipo_usuario', 'modo_pp', 'fila').reindex(M.ORDEN_USUARIO).dropna(how='all')
        a.plotly_chart(viz.barras_apiladas(t[[m for m in M.ORDEN_MODO if m in t.columns]],
                       'Partición modal por tipo de usuario', viz.COLOR_MODO), use_container_width=True, key='c_usu_modal')
        share = d.dropna(subset=['tipo_usuario']).groupby('tipo_usuario')['factor'].sum()
        share = (share / share.sum() * 100).reindex(M.ORDEN_USUARIO).dropna().round(1)
        b.plotly_chart(viz.dona(share, '% de viajes por tipo de usuario'), use_container_width=True, key='c_usu_dona')

    # ---- Ingreso ----
    with tabs[4]:
        if 'quintil_ingreso' not in d.columns or d['quintil_ingreso'].isna().all():
            st.info('Esta ciudad no registra ingreso del hogar (no disponible para segmentar).')
        else:
            ui.section('Comportamiento por quintil de ingreso',
                       'Q1 = 20% de menor ingreso · Q5 = 20% de mayor ingreso (por ciudad).')
            dq = d.dropna(subset=['quintil_ingreso']).assign(q=lambda x: x['quintil_ingreso'].map(Q_LABEL))
            a, b = st.columns(2)
            t = M.tabla_cruzada(dq, 'q', 'modo_pp', 'fila').reindex(M.ORDEN_QUINTIL).dropna(how='all')
            a.plotly_chart(viz.barras_apiladas(t[[m for m in M.ORDEN_MODO if m in t.columns]],
                           'Partición modal por quintil', viz.COLOR_MODO), use_container_width=True, key='c_ing_modal')
            vpq = dq.groupby('q')['factor'].sum().reindex(M.ORDEN_QUINTIL)
            vpq = (vpq / vpq.sum() * 100).round(1).dropna()
            b.plotly_chart(_bar(vpq, '% de viajes', '#16a34a'), use_container_width=True, key='c_ing_vpq')
            if dist.notna().any():
                ui.section('Distancia por quintil')
                t = M.tabla_cruzada(dq.dropna(subset=['tramo_dist']), 'q', 'tramo_dist', 'fila').reindex(M.ORDEN_QUINTIL)
                t = t[[c for c in M.ORDEN_TRAMO if c in t.columns]]
                st.plotly_chart(viz.barras_apiladas(t, None), use_container_width=True, key='c_ing_dist')

    # ---- Mapas ----
    with tabs[5]:
        if not geo.tiene_geo(ciudad):
            st.info('Esta ciudad aún no tiene zonificación geográfica cargada.')
        else:
            gj = geo.geojson(ciudad)
            modo_mapa = st.radio('Vista', ['Generación', 'Atracción', 'Líneas de deseo', 'Matriz O/D'],
                                 horizontal=True, key='mapa')
            if modo_mapa in ('Generación', 'Atracción'):
                z = geo.generacion_atraccion(d)
                col = 'generados' if modo_mapa == 'Generación' else 'atraidos'
                ttl = 'Viajes generados por zona (origen)' if col == 'generados' else 'Viajes atraídos por zona (destino)'
                st.plotly_chart(geomap.choropleth(gj, z, col, ttl), use_container_width=True, key='c_map_choro')
            elif modo_mapa == 'Líneas de deseo':
                top = st.slider('Pares O-D principales', 50, 400, 150, 50)
                pares = geo.lineas_deseo(d, top_n=top)
                if pares.empty:
                    st.info('Sin pares O-D con coordenadas para esta selección.')
                else:
                    st.plotly_chart(geomap.lineas_deseo(pares), use_container_width=True, key='c_map_deseo')
                    st.caption('Grosor/color ∝ volumen de viajes entre zonas (interzonales).')
            else:
                zonas = geo.zonas_con_viajes(d)
                zsel = st.selectbox('Zona de origen', zonas, format_func=lambda z: f'Zona {z}')
                dest = geo.destinos_desde(d, zsel)
                if dest.empty:
                    st.info('Sin destinos para esta zona.')
                else:
                    cmap, ctab = st.columns([3, 2])
                    cmap.plotly_chart(geomap.destinos_map(dest, zsel), use_container_width=True, key='c_map_od')
                    tt = dest.head(12)[['zona', 'viajes']].copy()
                    tt['viajes'] = tt['viajes'].round(0).astype(int)
                    ctab.markdown('**Principales destinos**')
                    ctab.dataframe(tt.rename(columns={'zona': 'Zona destino', 'viajes': 'Viajes'}),
                                   hide_index=True, use_container_width=True)
