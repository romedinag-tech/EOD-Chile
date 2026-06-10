# -*- coding: utf-8 -*-
"""Componentes y estilos de UI para un look profesional."""
import streamlit as st

CSS = """
<style>
:root { --eod-primary:#1f6feb; --eod-ink:#1b2430; --eod-muted:#5b6b7c; }
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1400px; }
#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }

/* Encabezado de la app */
.eod-hero { display:flex; align-items:center; gap:.7rem; padding:.2rem 0 .6rem 0;
  border-bottom:1px solid #e6eaf0; margin-bottom:.8rem; }
.eod-hero h1 { font-size:1.5rem; margin:0; color:var(--eod-ink); font-weight:700; }
.eod-hero .sub { color:var(--eod-muted); font-size:.85rem; }

/* Tarjetas KPI */
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:.7rem; margin:.2rem 0 1rem 0; }
.kpi { background:#fff; border:1px solid #e6eaf0; border-radius:12px; padding:.8rem 1rem;
  box-shadow:0 1px 2px rgba(16,24,40,.04); transition:.15s; }
.kpi:hover { box-shadow:0 4px 14px rgba(16,24,40,.08); transform:translateY(-1px); }
.kpi .lab { color:var(--eod-muted); font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; font-weight:600; }
.kpi .val { color:var(--eod-ink); font-size:1.55rem; font-weight:700; line-height:1.15; margin-top:.15rem; }
.kpi .sub { color:var(--eod-muted); font-size:.74rem; margin-top:.1rem; }
.kpi.accent { border-top:3px solid var(--eod-primary); }

/* Encabezado de sección */
.sec { margin:.6rem 0 .2rem 0; }
.sec h3 { font-size:1.05rem; color:var(--eod-ink); margin:0; font-weight:700; }
.sec p { color:var(--eod-muted); font-size:.82rem; margin:.1rem 0 .3rem 0; }

/* Chips de contexto */
.chips { display:flex; gap:.4rem; flex-wrap:wrap; margin:.1rem 0 .6rem 0; }
.chip { background:#eef3fe; color:#1f6feb; border-radius:999px; padding:.12rem .6rem; font-size:.75rem; font-weight:600; }

/* Tabs un poco más grandes */
.stTabs [data-baseweb="tab"] { font-size:.9rem; font-weight:600; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(titulo='EOD Chile', sub='Encuestas Origen-Destino · datos homologados'):
    st.markdown(
        f'<div class="eod-hero"><span style="font-size:1.7rem">🚍</span>'
        f'<div><h1>{titulo}</h1><div class="sub">{sub}</div></div></div>',
        unsafe_allow_html=True)


def section(titulo, desc=None):
    html = f'<div class="sec"><h3>{titulo}</h3>'
    if desc:
        html += f'<p>{desc}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def kpis(items):
    """items: lista de (label, valor, sub|None). Render en grilla de tarjetas."""
    cells = ''
    for it in items:
        lab, val = it[0], it[1]
        sub = it[2] if len(it) > 2 and it[2] else ''
        cells += (f'<div class="kpi accent"><div class="lab">{lab}</div>'
                  f'<div class="val">{val}</div><div class="sub">{sub}</div></div>')
    st.markdown(f'<div class="kpi-grid">{cells}</div>', unsafe_allow_html=True)


def chips(items):
    c = ''.join(f'<span class="chip">{x}</span>' for x in items if x)
    st.markdown(f'<div class="chips">{c}</div>', unsafe_allow_html=True)


def fmt_miles(n):
    try:
        return f"{float(n):,.0f}".replace(',', '.')
    except Exception:
        return str(n)
