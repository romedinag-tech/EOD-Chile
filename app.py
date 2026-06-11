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

# ---------------- Sidebar: selección de ciudad / año ----------------
cat = D.catalogo_ciudades()
with st.sidebar:
    st.markdown('### 🧭 Navegación')
    regiones = ['(Todas)'] + sorted(cat['region'].dropna().unique().tolist())
    reg = st.selectbox('Región', regiones, index=0)
    sub = cat if reg == '(Todas)' else cat[cat['region'] == reg]
    ciudades = sub['ciudad'].tolist()
    ciudad_sel = st.selectbox('Ciudad', ciudades, index=0)
    anios = sorted(cat[cat['ciudad'] == ciudad_sel]['anio'].dropna().unique().tolist())
    anio_sel = st.selectbox('Año de la encuesta', anios, index=len(anios) - 1)
    nota = D.RATIO_NOTA.get(ciudad_sel)
    if nota:
        st.info(f'ℹ️ {nota}', icon=None)
    st.divider()
    st.caption('Fuente: Biblioteca MTT. Viajes en día laboral, expandidos por su '
               'factor de expansión (corregido por sesgo).')

# ---------------- Menú superior ----------------
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
    st.markdown(f'### {ciudad_sel}')
    ciudad.render(ciudad_sel, anio_sel)
elif seccion == 'Comparador':
    comparador.render()
elif seccion == 'Ranking':
    ranking.render()
