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
