# -*- coding: utf-8 -*-
"""EOD Chile — Dashboard de Encuestas Origen-Destino homologadas."""
import streamlit as st
from streamlit_option_menu import option_menu

from eodlib import data as D, ui
from views import resumen, ciudad, comparador, ranking

st.set_page_config(page_title='EOD Chile', page_icon='🚍', layout='wide',
                   initial_sidebar_state='expanded')
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
if 'ciudad_expand' not in st.session_state:
    st.session_state['ciudad_expand'] = st.session_state['ciudad_sel']

ciudad_sel = st.session_state['ciudad_sel']
anio_sel   = st.session_state['anio_sel']

# ── Sidebar: lista geográfica de ciudades ──────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nav-title">🧭 Ciudades</div>', unsafe_allow_html=True)

    for ciudad_it in ciudades_disponibles:
        anios = city_years[ciudad_it]
        multi  = len(anios) > 1
        activa = (ciudad_it == ciudad_sel)
        expandida = (st.session_state.get('ciudad_expand') == ciudad_it)

        label = (f'{'▾' if expandida else '›'} {ciudad_it}') if multi else ciudad_it

        if st.button(label, key=f'nb_{ciudad_it}', use_container_width=True,
                     type='primary' if (activa and not multi) else 'secondary'):
            if multi:
                st.session_state['ciudad_expand'] = ciudad_it if not expandida else None
            else:
                st.session_state['ciudad_sel'] = ciudad_it
                st.session_state['anio_sel']   = anios[0]
                st.session_state['ciudad_expand'] = ciudad_it
            st.rerun()

        if multi and expandida:
            for anio in anios:
                anio_activo = activa and (int(anio) == int(anio_sel))
                st.markdown('<div class="year-row">', unsafe_allow_html=True)
                if st.button(f'Encuesta {int(anio)}', key=f'nb_{ciudad_it}_{anio}',
                             use_container_width=True,
                             type='primary' if anio_activo else 'secondary'):
                    st.session_state['ciudad_sel'] = ciudad_it
                    st.session_state['anio_sel']   = anio
                    st.session_state['ciudad_expand'] = ciudad_it
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    nota = D.RATIO_NOTA.get(ciudad_sel)
    if nota:
        st.info(f'ℹ️ {nota}', icon=None)
    st.caption('Fuente: Biblioteca MTT. Viajes en día laboral, expandidos por '
               'factor de expansión (corregido por sesgo).')

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
    st.markdown(f'### {ciudad_sel} <span style="font-size:.85rem;color:#5e6e80;font-weight:400">· EOD {int(anio_sel)}</span>',
                unsafe_allow_html=True)
    ciudad.render(ciudad_sel, anio_sel)
elif seccion == 'Comparador':
    comparador.render()
elif seccion == 'Ranking':
    ranking.render()
