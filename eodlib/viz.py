# -*- coding: utf-8 -*-
"""Gráficos Plotly con estilo consistente para el dashboard EOD."""
import plotly.express as px
import plotly.graph_objects as go

# paleta por modo (consistente en todo el dashboard)
COLOR_MODO = {
    'Privado': '#e45756', 'Público': '#4c78a8', 'No motorizado': '#54a24b',
    'Combinado': '#f58518', 'Otro': '#9d9d9d',
}
COLOR_PROP = {'Trabajo': '#4c78a8', 'Estudio': '#f58518', 'Otro': '#9d9d9d'}
SECUENCIA = px.colors.qualitative.Safe


def _layout(fig, titulo=None, alto=360):
    fig.update_layout(
        title=titulo, height=alto, margin=dict(l=10, r=10, t=40 if titulo else 10, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, x=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def barra_modal(serie, titulo='Partición modal'):
    fig = go.Figure(go.Bar(
        x=serie.index, y=serie.values, marker_color=[COLOR_MODO.get(i, '#888') for i in serie.index],
        text=[f'{v:.1f}%' for v in serie.values], textposition='outside'))
    fig.update_yaxes(title='% de viajes', ticksuffix='%')
    return _layout(fig, titulo)


def dona(serie, titulo, colores=None):
    cols = [colores.get(i, None) for i in serie.index] if colores else None
    fig = go.Figure(go.Pie(labels=serie.index, values=serie.values, hole=0.55,
                           marker=dict(colors=cols), textinfo='label+percent', sort=False))
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
                        fill='tozeroy', line=dict(width=2.5, color='#4c78a8'))
    fig.update_xaxes(title='Hora del día', dtick=2)
    fig.update_yaxes(title='% de viajes', ticksuffix='%')
    return _layout(fig, titulo, alto=380)
