# -*- coding: utf-8 -*-
"""EOD Chile — Dashboard de Encuestas Origen-Destino homologadas."""
import streamlit as st
from streamlit_option_menu import option_menu

from eodlib import data as D
from views import ciudad, comparador, ranking

st.set_page_config(page_title='EOD Chile', page_icon='🚍', layout='wide')

# ---------------- Sidebar: selección de ciudad / año ----------------
cat = D.catalogo_ciudades()
with st.sidebar:
    st.markdown('## 🚍 EOD Chile')
    st.caption('Encuestas Origen-Destino homologadas')
    regiones = ['(Todas)'] + sorted(cat['region'].dropna().unique().tolist())
    reg = st.selectbox('Región', regiones, index=0)
    sub = cat if reg == '(Todas)' else cat[cat['region'] == reg]
    ciudades = sub['ciudad'].tolist()
    ciudad_sel = st.selectbox('Ciudad', ciudades, index=0)
    anios = sorted(cat[cat['ciudad'] == ciudad_sel]['anio'].dropna().unique().tolist())
    anio_sel = st.selectbox('Año de la encuesta', anios, index=len(anios) - 1)
    st.divider()
    nota = D.RATIO_NOTA.get(ciudad_sel)
    if nota:
        st.warning(f'⚠️ {nota}')
    st.caption('Fuente: Biblioteca MTT · viajes en día laboral, expandidos por factor.')

st.session_state['ciudad'] = ciudad_sel
st.session_state['anio'] = anio_sel

# ---------------- Menú superior: herramientas ----------------
seccion = option_menu(
    None, ['Ciudad', 'Comparador', 'Ranking'],
    icons=['geo-alt', 'bar-chart-steps', 'trophy'],
    orientation='horizontal', default_index=0,
    styles={'container': {'padding': '0', 'background-color': '#f0f2f6'},
            'nav-link-selected': {'background-color': '#4c78a8'}})

if seccion == 'Ciudad':
    ciudad.render(ciudad_sel, anio_sel)
elif seccion == 'Comparador':
    comparador.render()
elif seccion == 'Ranking':
    ranking.render()
