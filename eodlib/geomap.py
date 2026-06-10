# -*- coding: utf-8 -*-
"""Mapas Plotly (mapbox open-street-map, sin token) para el dashboard EOD."""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def _centro(z):
    return dict(lat=float(z['lat'].mean()), lon=float(z['lon'].mean()))


def _zoom(z):
    span = max(z['lat'].max() - z['lat'].min(), (z['lon'].max() - z['lon'].min()) * 0.8, 0.05)
    return float(np.clip(11.5 - np.log2(span / 0.05), 8, 13))


def choropleth(geojson, zdf, valor, titulo):
    z = zdf.dropna(subset=['lon', 'lat'])
    fig = px.choropleth_mapbox(
        zdf, geojson=geojson, locations='zona', featureidkey='properties.zona',
        color=valor, color_continuous_scale='YlOrRd',
        mapbox_style='open-street-map', opacity=0.6,
        center=_centro(z), zoom=_zoom(z),
        labels={valor: 'viajes'})
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=40, b=0), title=titulo,
                      coloraxis_colorbar=dict(title='viajes'))
    return fig


def lineas_deseo(pares, titulo='Líneas de deseo'):
    z = pares
    cen = dict(lat=float(np.r_[z['lat_o'], z['lat_d']].mean()),
               lon=float(np.r_[z['lon_o'], z['lon_d']].mean()))
    fig = go.Figure()
    # 3 buckets por magnitud de flujo -> distinto grosor/opacidad
    q = pares['factor'].quantile([0.5, 0.85]).values
    buckets = [(0, q[0], 0.8, 'rgba(76,120,168,0.25)'),
               (q[0], q[1], 1.8, 'rgba(76,120,168,0.5)'),
               (q[1], np.inf, 3.5, 'rgba(229,87,86,0.8)')]
    for lo, hi, w, col in buckets:
        sub = pares[(pares['factor'] >= lo) & (pares['factor'] < hi)]
        lons, lats = [], []
        for _, r in sub.iterrows():
            lons += [r['lon_o'], r['lon_d'], None]
            lats += [r['lat_o'], r['lat_d'], None]
        fig.add_trace(go.Scattermapbox(lon=lons, lat=lats, mode='lines',
                      line=dict(width=w, color=col), hoverinfo='skip', showlegend=False))
    # centroides como puntos
    pts = pares.groupby(['zo'])[['lon_o', 'lat_o', 'factor']].agg(
        {'lon_o': 'first', 'lat_o': 'first', 'factor': 'sum'}).reset_index()
    fig.add_trace(go.Scattermapbox(lon=pts['lon_o'], lat=pts['lat_o'], mode='markers',
                  marker=dict(size=5, color='#333'), hovertext=pts['zo'], showlegend=False))
    fig.update_layout(mapbox=dict(style='open-street-map', center=cen, zoom=_zoom(
        pares.rename(columns={'lon_o': 'lon', 'lat_o': 'lat'}))),
        height=560, margin=dict(l=0, r=0, t=40, b=0), title=titulo)
    return fig
