# -*- coding: utf-8 -*-
"""Vista por ciudad: comportamiento de viajes, segmentable, con pestañas."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from eodlib import data as D, metrics as M, viz, geo, geomap, ui

Q_LABEL = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4', 5: 'Q5'}
# Mapas interactivos: rueda = zoom, arrastrar = mover (pan), doble-clic = reset.
MAP_CFG = {'scrollZoom': True, 'displaylogo': False,
           'modeBarButtonsToRemove': ['lasso2d', 'select2d']}


def _click_id(ev):
    """Extrae el id (zona/comuna) del punto clickeado en un mapa Plotly."""
    try:
        pts = (ev or {}).get('selection', {}).get('points', [])
        if not pts:
            return None
        p = pts[0]
        cd = p.get('customdata')
        if isinstance(cd, (list, tuple)):
            cd = cd[0] if cd else None
        return str(p.get('location') if p.get('location') is not None else cd) if (p.get('location') is not None or cd is not None) else None
    except Exception:
        return None


def _bar(serie, ytit='% de viajes', color='#1f4e79'):
    fig = go.Figure(go.Bar(x=list(serie.index), y=list(serie.values), marker_color=color,
                    text=[f'{v:.1f}%' for v in serie.values], textposition='outside'))
    fig.update_yaxes(title=ytit, ticksuffix='%'); fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='rgba(0,0,0,0)')
    return fig


def render(ciudad, anio):
    d0 = D.viajes_ciudad(ciudad, anio=anio)
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
        seg = ui.seg('Segmentar por', ['(ninguno)', 'Modo', 'Propósito'], key='seg_hora')
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
            seg_d = ui.seg('Segmentar por', ['(ninguno)', 'Modo', 'Propósito', 'Tipo usuario', 'Quintil ingreso'], key='seg_dist')
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
            b.plotly_chart(_bar(vpq, '% de viajes', '#1a9850'), use_container_width=True, key='c_ing_vpq')
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
            hay_comuna = geo.comuna_disponible(ciudad)
            st.caption('💡 Rueda del mouse = zoom · arrastrar = mover el mapa · '
                       'doble-clic = restablecer vista.')

            # --- Histograma horario y selector de período ------------------
            hora_d = d.dropna(subset=['hora']).copy()
            hora_d['hora'] = hora_d['hora'].astype(int)

            if not hora_d.empty:
                pct_h = (hora_d.groupby('hora')['factor'].sum()
                         .pipe(lambda s: (s / s.sum() * 100)
                               .reindex(range(24), fill_value=0).round(1)))
                am_h = int(pct_h.loc[6:11].idxmax()) if pct_h.loc[6:11].sum() > 0 else 8
                pm_h = int(pct_h.loc[15:22].idxmax()) if pct_h.loc[15:22].sum() > 0 else 18

                st.plotly_chart(
                    viz.histograma_periodos(pct_h, am_h, pm_h),
                    use_container_width=True, key='c_map_hist',
                )
                PERIODO_MAP = {
                    'Todo el día':                   None,
                    f'Punta AM ({am_h}h)':           ['Punta mañana'],
                    'Mediodía (12–14h)':             ['Punta mediodía'],
                    'Fuera de punta':                ['Fuera punta mañana', 'Fuera punta tarde'],
                    f'Punta tarde ({pm_h}h)':        ['Punta tarde'],
                }
                per_lbl = ui.seg('Período', list(PERIODO_MAP.keys()), key='mapa_per')
                per_vals = PERIODO_MAP.get(per_lbl)
                d_geo = d[d['periodo_dia'].isin(per_vals)] if per_vals else d
            else:
                d_geo = d

            if d_geo.empty:
                st.info('Sin viajes con hora registrada para este período.')
            else:
                modo_mapa = ui.seg(
                    'Vista', ['Generación', 'Atracción', 'Líneas de deseo', 'Matriz O/D'], key='mapa')

                if modo_mapa in ('Generación', 'Atracción'):
                    z = geo.generacion_atraccion(d_geo)
                    col = 'generados' if modo_mapa == 'Generación' else 'atraidos'
                    ttl = ('Viajes generados por zona (origen)' if col == 'generados'
                           else 'Viajes atraídos por zona (destino)')
                    st.plotly_chart(geomap.choropleth(gj, z, col, ttl), use_container_width=True,
                                    key='c_map_choro', config=MAP_CFG)

                elif modo_mapa == 'Líneas de deseo':
                    cc1, cc2 = st.columns([1, 2])
                    niv = ui.seg('Nivel', ['Zona'] + (['Comuna'] if hay_comuna else []),
                                 container=cc1, key='deseo_niv')
                    nivel = 'comuna' if niv == 'Comuna' else 'zona'
                    top = cc2.slider('Pares O-D principales', 30, 400, 120, 30, key='deseo_top')
                    pares = geo.lineas_deseo(d_geo, top_n=top, nivel=nivel)
                    if pares.empty:
                        st.info('Sin pares O-D con coordenadas para esta selección.')
                    else:
                        st.plotly_chart(geomap.lineas_deseo(pares, f'Líneas de deseo entre {niv.lower()}s'),
                                        use_container_width=True, key='c_map_deseo', config=MAP_CFG)
                        st.caption(f'Grosor/color ∝ volumen de viajes entre {niv.lower()}s (interzonales).')

                else:  # Matriz O/D
                    niv = ui.seg('Nivel', ['Zona'] + (['Comuna'] if hay_comuna else []), key='od_niv')
                    nivel = 'comuna' if niv == 'Comuna' else 'zona'
                    unidades = geo.unidades_con_viajes(d_geo, nivel)
                    if not unidades:
                        st.info('Sin unidades con viajes para este período.')
                    else:
                        if nivel == 'zona':
                            cents = geo.centroides()
                            cents = cents[cents['ciudad'] == ciudad][['zona', 'lon', 'lat']]
                        else:
                            cents = geo.centroides_comuna(ciudad).rename(columns={'comuna': 'zona'})
                        wkey = f'odsel_{ciudad}_{nivel}'
                        origen = st.session_state.get(wkey, unidades[0])
                        if origen not in unidades:
                            origen = unidades[0]
                        label = (lambda z: f'Zona {z}') if nivel == 'zona' else (lambda z: f'Comuna {z}')
                        dest = geo.destinos_desde(d_geo, origen, nivel)

                        fig_od = geomap.od_2d(gj, origen, dest, nivel, cents)
                        ev = st.plotly_chart(fig_od, use_container_width=True,
                                             key=f'od2d_{ciudad}_{nivel}',
                                             on_select='rerun', config=MAP_CFG)
                        clic = _click_id(ev)
                        if clic is not None and clic in unidades and clic != origen:
                            st.session_state[wkey] = clic
                            st.rerun()
                        st.caption('🖱️ Pincha una zona para fijar el origen (se destaca en azul). '
                                   'Las burbujas son los destinos: tamaño y color proporcional a los viajes.')

                        c1, c2 = st.columns([2, 3])
                        sel2 = c1.selectbox(f'{niv} de origen (o pincha el mapa)', unidades,
                                            index=unidades.index(origen), format_func=label,
                                            key=f'odbox_{ciudad}_{nivel}')
                        if sel2 != origen:
                            st.session_state[wkey] = sel2
                            st.rerun()
                        tt = dest[dest['zona'].astype(str) != str(origen)].head(15)[['zona', 'viajes']].copy()
                        tt['viajes'] = tt['viajes'].round(0).astype(int)
                        c2.markdown(f'**Principales destinos desde {label(origen)}**')
                        c2.dataframe(tt.rename(columns={'zona': niv + ' destino', 'viajes': 'Viajes'}),
                                     hide_index=True, use_container_width=True, height=360)
