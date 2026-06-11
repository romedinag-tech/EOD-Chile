# -*- coding: utf-8 -*-
"""Componentes y estilos de UI — design tokens del sitio ciudades_y_tendencias."""
import streamlit as st

CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
:root{
  --eod-navy:#1f4e79;--eod-navy2:#2e5e8c;--eod-navy-d:#143150;
  --eod-or:#d96a1f;--eod-teal:#1f8a86;--eod-green:#1a9850;
  --eod-red:#d6453a;--eod-amber:#e0a92b;
  --eod-bg:#f4f7fb;--eod-surface:#ffffff;--eod-surface2:#eef3f9;
  --eod-ink:#172430;--eod-mut:#5e6e80;--eod-mut2:#8696a7;
  --eod-line:#e4eaf2;--eod-line2:#d3dde9;
  --eod-grad:linear-gradient(135deg,#143150 0%,#1f4e79 60%,#2e5e8c 100%);
  --eod-r:14px;--eod-r-sm:10px;--eod-r-lg:18px;
  --eod-sh:0 2px 10px rgba(20,40,70,.05),0 10px 28px rgba(20,40,70,.05);
  --eod-sh-lg:0 16px 44px rgba(20,40,70,.13);
}
*{box-sizing:border-box}
html,body,.stApp,.main,[data-testid="stAppViewContainer"]{background:var(--eod-bg)!important}
body,[class*="css"],button,input,select,textarea{
  font-family:'Inter',-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif!important;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
.block-container{padding-top:0!important;padding-bottom:2rem;max-width:1400px}
#MainMenu,footer,header [data-testid="stToolbar"]{visibility:hidden}

/* === HERO HEADER (gradient, como el sitio de referencia) === */
.eod-hero{
  background:var(--eod-grad);color:#fff;
  padding:22px 26px 18px;border-radius:var(--eod-r-lg);
  margin-bottom:1.1rem;position:relative;overflow:hidden}
.eod-hero::before{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(900px 280px at 80% -40%,rgba(120,180,255,.18),transparent 70%)}
.eod-hero h1{
  margin:0 0 5px;font-size:1.6rem;font-weight:800;letter-spacing:-.5px;
  color:#fff;position:relative}
.eod-hero .sub{opacity:.88;font-size:.9rem;color:rgba(255,255,255,.9);
  position:relative;margin:0}

/* === KPI CARDS === */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));
  gap:14px;margin:.4rem 0 1.2rem 0}
.kpi{background:var(--eod-surface);border:1px solid var(--eod-line);
  border-radius:var(--eod-r);padding:18px;box-shadow:var(--eod-sh);
  transition:transform .16s ease,box-shadow .16s ease}
.kpi:hover{transform:translateY(-2px);box-shadow:var(--eod-sh-lg)}
.kpi.accent{border-top:3px solid var(--eod-or)}
.kpi .lab{color:var(--eod-mut);font-size:.75rem;text-transform:uppercase;
  letter-spacing:.04em;font-weight:700}
.kpi .val{color:var(--eod-navy);font-size:1.7rem;font-weight:800;
  line-height:1.1;margin-top:.2rem;font-variant-numeric:tabular-nums}
.kpi .sub{color:var(--eod-or);font-weight:700;font-size:.82rem;margin-top:.15rem}

/* === SECTION HEADERS (con barra naranja izquierda) === */
.sec{margin:.9rem 0 .25rem 0}
.sec h3{font-size:1.05rem;color:var(--eod-navy);margin:0;font-weight:700;
  border-left:4px solid var(--eod-or);padding-left:10px}
.sec p{color:var(--eod-mut);font-size:.84rem;margin:.2rem 0 .3rem 0}

/* === CHIPS === */
.chips{display:flex;gap:.4rem;flex-wrap:wrap;margin:.2rem 0 .7rem 0}
.chip{background:var(--eod-navy);color:#fff;border-radius:999px;
  padding:.24rem .78rem;font-size:.78rem;font-weight:600}

/* === STREAMLIT TABS (subrayado naranja, como sitio de referencia) === */
.stTabs [data-baseweb="tab-list"]{
  background:transparent!important;border-bottom:1px solid var(--eod-line)!important;gap:0!important}
.stTabs [data-baseweb="tab"]{
  font-size:.95rem!important;font-weight:700!important;color:var(--eod-mut)!important;
  padding:12px 18px!important;background:transparent!important}
.stTabs [data-baseweb="tab"]:hover{color:var(--eod-navy)!important}
.stTabs [data-baseweb="tab"][aria-selected="true"]{
  color:var(--eod-navy)!important;background:transparent!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--eod-or)!important;height:3px!important}

/* === SEGMENTED CONTROL (píldoras navy, activo = fondo navy) === */
[data-testid="stSegmentedControl"]{margin-top:.1rem}
[data-testid="stSegmentedControl"] button{
  font-size:.9rem!important;font-weight:600!important;padding:.45rem 1.1rem!important;
  border-radius:22px!important;border:1.5px solid var(--eod-navy)!important;
  color:var(--eod-navy)!important;background:#fff!important}
[data-testid="stSegmentedControl"] button:hover{
  background:var(--eod-surface2)!important}
[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[kind="segmented_controlActive"]{
  background:var(--eod-navy)!important;color:#fff!important;
  border-color:var(--eod-navy)!important;
  box-shadow:0 2px 6px rgba(31,78,121,.28)!important}

/* === WIDGET LABELS === */
[data-testid="stWidgetLabel"] label p{
  font-weight:600;color:var(--eod-ink);font-size:.88rem}

/* === SIDEBAR === */
section[data-testid="stSidebar"]{
  background:var(--eod-surface)!important;border-right:1px solid var(--eod-line)}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{color:var(--eod-navy)}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(titulo='EOD Chile', sub='Encuestas Origen-Destino · datos homologados'):
    st.markdown(
        f'<div class="eod-hero">'
        f'<h1>🚍 {titulo}</h1>'
        f'<div class="sub">{sub}</div>'
        f'</div>',
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


def seg(label, options, default=None, key=None, container=None, help=None):
    """Selector tipo botones segmentados (más visible que un radio). Nunca devuelve None."""
    c = container if container is not None else st
    default = default if default is not None else (options[0] if options else None)
    val = c.segmented_control(label, options, default=default, key=key, help=help)
    return val if val is not None else default


def fmt_miles(n):
    try:
        return f"{float(n):,.0f}".replace(',', '.')
    except Exception:
        return str(n)
