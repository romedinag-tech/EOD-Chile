# -*- coding: utf-8 -*-
"""EOD Chile — Dashboard de Encuestas Origen-Destino homologadas."""
import streamlit as st
from streamlit_option_menu import option_menu

from eodlib import data as D, ui
from views import resumen, ciudad, comparador, ranking

st.set_page_config(page_title='EOD Chile', page_icon='🚍', layout='wide',
                   initial_sidebar_state='collapsed')
ui.inject_css()
ui.hero('EOD Chile', 'Encuestas Origen-Destino · 18 ciudades homologadas y expandidas')

# ── Orden geográfico (Norte → Sur) ──────────────────────────────────────────
ORDEN_GEO = [
    'Arica',
    'Iquique - Alto Hospicio',
    'Copiapó',
    'Coquimbo - La Serena',
    'Gran Valparaíso',
    'San Antonio',
    'Gran Santiago',
    'Rancagua - Machalí',
    'Curicó',
    'Talca',
    'Linares',
    'Chillán',
    'Gran Concepción',
    'Temuco - Padre las Casas',
    'Valdivia',
    'Osorno',
    'Puerto Montt',
    'Punta Arenas',
]

# ── Catálogo: {ciudad: [anios ordenados]} ──────────────────────────────────
cat = D.catalogo_ciudades()
city_years = {}
for _, row in cat.iterrows():
    city_years.setdefault(row['ciudad'], [])
    if row['anio'] not in city_years[row['ciudad']]:
        city_years[row['ciudad']].append(row['anio'])
city_years = {c: sorted(v) for c, v in city_years.items()}
ciudades_disponibles = [c for c in ORDEN_GEO if c in city_years]

# ── Session state inicial ───────────────────────────────────────────────────
if 'ciudad_sel' not in st.session_state or st.session_state['ciudad_sel'] not in city_years:
    primera = ciudades_disponibles[0] if ciudades_disponibles else None
    st.session_state['ciudad_sel'] = primera
    st.session_state['anio_sel'] = city_years[primera][-1] if primera else None
elif 'anio_sel' not in st.session_state:
    c = st.session_state['ciudad_sel']
    st.session_state['anio_sel'] = city_years[c][-1]
ciudad_sel = st.session_state['ciudad_sel']
anio_sel   = st.session_state['anio_sel']

# ── Menú superior ──────────────────────────────────────────────────────────
seccion = option_menu(
    None, ['Resumen', 'Ciudad', 'Comparador', 'Ranking'],
    icons=['globe-americas', 'geo-alt-fill', 'bar-chart-steps', 'trophy-fill'],
    orientation='horizontal', default_index=0,
    styles={
        'container': {'padding': '0', 'background-color': 'transparent',
                      'border-bottom': '2px solid #e4eaf2', 'margin-bottom': '18px'},
        'nav-link': {'font-size': '1rem', 'font-weight': '700', 'color': '#5e6e80',
                     'padding': '13px 22px', 'margin': '0', 'border-radius': '0',
                     'border-bottom': '3px solid transparent', '--hover-color': 'transparent'},
        'nav-link-selected': {'background-color': 'transparent', 'color': '#1f4e79',
                              'border-bottom': '3px solid #d96a1f', 'box-shadow': 'none'},
        'icon': {'font-size': '1rem', 'color': 'inherit'}})

if seccion == 'Resumen':
    resumen.render()
elif seccion == 'Ciudad':
    _col_c, _col_a, _col_sp = st.columns([3, 1, 5])
    with _col_c:
        _idx_c = ciudades_disponibles.index(ciudad_sel) if ciudad_sel in ciudades_disponibles else 0
        _sel_c = st.selectbox('Ciudad', ciudades_disponibles, index=_idx_c,
                              key='_main_ciudad', label_visibility='collapsed')
        if _sel_c != ciudad_sel:
            st.session_state['ciudad_sel'] = _sel_c
            st.session_state['anio_sel']   = city_years[_sel_c][-1]
            st.rerun()
    with _col_a:
        _anios_c = city_years.get(ciudad_sel, [anio_sel])
        if len(_anios_c) > 1:
            _idx_a = len(_anios_c) - 1
            try:
                _idx_a = [int(a) for a in _anios_c].index(int(anio_sel))
            except (ValueError, TypeError):
                pass
            _sel_a = st.selectbox('Año', [int(a) for a in _anios_c], index=_idx_a,
                                  key='_main_anio', label_visibility='collapsed')
            if int(_sel_a) != int(anio_sel):
                st.session_state['anio_sel'] = _sel_a
                st.rerun()
        else:
            st.caption(f'EOD {int(anio_sel)}')
    ciudad.render(ciudad_sel, anio_sel)
elif seccion == 'Comparador':
    comparador.render()
elif seccion == 'Ranking':
    ranking.render()
