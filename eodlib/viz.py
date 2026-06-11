# -*- coding: utf-8 -*-
"""Gráficos Plotly con paleta del sitio ciudades_y_tendencias."""
import plotly.express as px
import plotly.graph_objects as go

_FONT = 'Inter,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif'

COLOR_MODO = {
    'Privado': '#d6453a',
    'Público': '#1f4e79',
    'No motorizado': '#1a9850',
    'Combinado': '#d96a1f',
    'Otro': '#8696a7',
}
COLOR_PROP = {'Trabajo': '#1f4e79', 'Estudio': '#d96a1f', 'Otro': '#8696a7'}
SECUENCIA = ['#1f4e79', '#d96a1f', '#1a9850', '#1f8a86', '#d6453a', '#e0a92b', '#8696a7']


def _layout(fig, titulo=None, alto=360):
    kw = dict(
        height=alto,
        margin=dict(l=10, r=10, t=44 if titulo else 10, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, x=0,
                    font=dict(family=_FONT, size=12, color='#5e6e80')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=_FONT, color='#172430'),
    )
    if titulo:
        kw['title'] = dict(text=titulo, font=dict(family=_FONT, size=15, color='#1f4e79'),
                           x=0, pad=dict(l=4))
    fig.update_layout(**kw)
    fig.update_xaxes(showgrid=False, linecolor='#e4eaf2',
                     tickfont=dict(size=12, color='#5e6e80'), tickcolor='#e4eaf2')
    fig.update_yaxes(gridcolor='#eef3f9', linecolor='rgba(0,0,0,0)',
                     tickfont=dict(size=12, color='#5e6e80'), gridwidth=1)
    return fig


def barra_modal(serie, titulo='Partición modal'):
    fig = go.Figure(go.Bar(
        x=serie.index, y=serie.values,
        marker_color=[COLOR_MODO.get(i, '#8696a7') for i in serie.index],
        text=[f'{v:.1f}%' for v in serie.values], textposition='outside',
        textfont=dict(size=12, family=_FONT)))
    fig.update_yaxes(title='% de viajes', ticksuffix='%')
    return _layout(fig, titulo)


def dona(serie, titulo, colores=None):
    cols = [colores.get(i, None) for i in serie.index] if colores else None
    fig = go.Figure(go.Pie(labels=serie.index, values=serie.values, hole=0.55,
                           marker=dict(colors=cols), textinfo='label+percent', sort=False,
                           textfont=dict(size=12, family=_FONT)))
    return _layout(fig, titulo)


def barras_apiladas(tabla, titulo, colores=None, ytitulo='% de viajes'):
    fig = go.Figure()
    for c in tabla.columns:
        fig.add_bar(name=str(c), x=tabla.index.astype(str), y=tabla[c],
                    marker_color=(colores.get(c) if colores else None))
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title=ytitulo, ticksuffix='%')
    return _layout(fig, titulo)


def lineas_horarias(tabla_o_serie, titulo='Distribución horaria', colores=None):
    fig = go.Figure()
    if hasattr(tabla_o_serie, 'columns'):
        for c in tabla_o_serie.columns:
            fig.add_scatter(x=tabla_o_serie.index, y=tabla_o_serie[c], mode='lines',
                            name=str(c), line=dict(width=2.5, color=(colores.get(c) if colores else None)),
                            stackgroup='one')
    else:
        fig.add_scatter(x=tabla_o_serie.index, y=tabla_o_serie.values, mode='lines',
                        fill='tozeroy', line=dict(width=2.5, color='#1f4e79'))
    fig.update_xaxes(title='Hora del día', dtick=2)
    fig.update_yaxes(title='% de viajes', ticksuffix='%')
    return _layout(fig, titulo, alto=380)


_PERIODO_BAND = [
    (6,  9,  '#1f4e79', 'Punta mañana'),
    (9,  12, '#8696a7', 'Fuera punta mañana'),
    (12, 14, '#d96a1f', 'Punta mediodía'),
    (14, 18, '#8696a7', 'Fuera punta tarde'),
    (18, 21, '#1f8a86', 'Punta tarde'),
]
COLOR_PERIODO = {n: c for _, _, c, n in _PERIODO_BAND}


def _hora_to_periodo(h):
    """Asigna período a una hora entera; coincide con periodo_dia del parquet."""
    h = int(h)
    if 6 <= h < 9:    return 'Punta mañana'
    if 9 <= h < 12:   return 'Fuera punta mañana'
    if 12 <= h < 14:  return 'Punta mediodía'
    if 14 <= h < 18:  return 'Fuera punta tarde'
    if 18 <= h < 21:  return 'Punta tarde'
    return 'Resto'


def histograma_periodos(pct_h, am_h=8, pm_h=18):
    """Histograma horario con barras coloreadas por período y marcadores de peak.

    pct_h : pd.Series index 0-23, valores = % de viajes.
    """
    serie = pct_h.reindex(range(24), fill_value=0)
    bar_colors = [
        COLOR_PERIODO.get(_hora_to_periodo(h), '#e4eaf2') for h in range(24)
    ]
    fig = go.Figure(go.Bar(
        x=list(range(24)),
        y=list(serie.values),
        marker_color=bar_colors,
        hovertemplate='%{x}h: %{y:.1f}%<extra></extra>',
        showlegend=False,
    ))
    # Marcadores de peak AM y PM
    for ph, color in [(am_h, '#1f4e79'), (pm_h, '#1f8a86')]:
        y_val = float(serie.get(ph, 0))
        fig.add_annotation(
            x=ph, y=y_val,
            text=f'▲{ph}h', showarrow=False,
            yanchor='bottom', yshift=4,
            font=dict(size=10, color=color, family=_FONT),
        )
    # Mini-leyenda de períodos (anotaciones en la parte inferior)
    leyenda = [
        (7.5,  '#1f4e79', 'Punta AM'),
        (10.5, '#8696a7', 'F. punta'),
        (13,   '#d96a1f', 'Mediodía'),
        (16,   '#8696a7', None),
        (19.5, '#1f8a86', 'Punta tarde'),
    ]
    for xpos, col, lbl in leyenda:
        if lbl:
            fig.add_annotation(x=xpos, y=-0.55, text=lbl, showarrow=False,
                               yref='paper', xref='x',
                               font=dict(size=9, color=col, family=_FONT))
    fig.update_xaxes(
        tickmode='array', tickvals=list(range(0, 24, 3)),
        ticktext=[f'{h}h' for h in range(0, 24, 3)],
        tickfont=dict(size=11), showgrid=False, linecolor='#e4eaf2',
    )
    fig.update_yaxes(ticksuffix='%', tickfont=dict(size=11))
    return _layout(fig, None, alto=200)
