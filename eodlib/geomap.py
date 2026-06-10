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


def mapa_zonas_click(geojson, zdf, valor='generados', titulo=None):
    """Coroplético de zonas seleccionable (click devuelve la zona en 'location')."""
    z = zdf.dropna(subset=['lon', 'lat'])
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson, locations=zdf['zona'], z=zdf[valor],
        featureidkey='properties.zona', colorscale='YlOrRd', marker_opacity=0.55,
        marker_line_width=0.4, colorbar=dict(title='viajes'),
        customdata=zdf['zona'], hovertemplate='Zona %{location}<br>%{z:,.0f} viajes<extra></extra>'))
    fig.update_layout(mapbox=dict(style='open-street-map', center=_centro(z), zoom=_zoom(z)),
                      height=520, margin=dict(l=0, r=0, t=30 if titulo else 0, b=0), title=titulo,
                      clickmode='event+select')
    return fig


def mapa_comunas_click(ccdf, valor='generados', titulo=None):
    """Puntos de comuna seleccionables (click devuelve la comuna en customdata)."""
    c = ccdf.dropna(subset=['lon', 'lat']).copy()
    mx = c[valor].max() if len(c) and c[valor].max() > 0 else 1
    fig = go.Figure(go.Scattermapbox(
        lon=c['lon'], lat=c['lat'], mode='markers',
        marker=dict(size=(12 + 36 * (c[valor] / mx)), color=c[valor], colorscale='YlOrRd',
                    showscale=True, colorbar=dict(title='viajes')),
        customdata=c['zona'], hovertemplate='Comuna %{customdata}<br>%{marker.color:,.0f} viajes<extra></extra>'))
    fig.update_layout(mapbox=dict(style='open-street-map', center=_centro(c), zoom=_zoom(c)),
                      height=520, margin=dict(l=0, r=0, t=30 if titulo else 0, b=0), title=titulo,
                      clickmode='event+select')
    return fig


def destinos_map(dest, zona_origen):
    """Mapa de destinos desde una zona origen: origen marcado + destinos por volumen."""
    d = dest.dropna(subset=['lon', 'lat']).copy()
    org = d[d['zona'].astype(str) == str(zona_origen)]
    dst = d[d['zona'].astype(str) != str(zona_origen)]
    cen = dict(lat=float(d['lat'].mean()), lon=float(d['lon'].mean()))
    fig = go.Figure()
    if not dst.empty:
        mx = dst['viajes'].max()
        fig.add_trace(go.Scattermapbox(
            lon=dst['lon'], lat=dst['lat'], mode='markers',
            marker=dict(size=(6 + 34 * (dst['viajes'] / mx)), color=dst['viajes'],
                        colorscale='YlOrRd', showscale=True, colorbar=dict(title='viajes')),
            hovertext=[f'Zona {z}: {int(v):,}'.replace(',', '.') for z, v in zip(dst['zona'], dst['viajes'])],
            hoverinfo='text', name='destinos'))
    if not org.empty:
        fig.add_trace(go.Scattermapbox(lon=org['lon'], lat=org['lat'], mode='markers',
                      marker=dict(size=16, color='#1f6feb'), hovertext=f'Origen: zona {zona_origen}',
                      hoverinfo='text', name='origen'))
    fig.update_layout(mapbox=dict(style='open-street-map', center=cen, zoom=_zoom(d)),
                      height=520, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    return fig
