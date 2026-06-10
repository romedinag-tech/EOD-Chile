# -*- coding: utf-8 -*-
"""Mapa O/D en 3D con pydeck: zona origen destacada + destinos como columnas 3D."""
import numpy as np
import pandas as pd
import pydeck as pdk


def _zoom(extent):
    return float(np.clip(11.5 - np.log2(max(extent, 0.05) / 0.05), 8, 13))


def _color(norm):
    """norm 0..1 -> RGB tipo amarillo→naranjo→rojo."""
    stops = [(0.0, (255, 237, 160)), (0.5, (253, 141, 60)), (1.0, (189, 0, 38))]
    norm = 0.0 if np.isnan(norm) else min(max(norm, 0.0), 1.0)
    for (x0, c0), (x1, c1) in zip(stops, stops[1:]):
        if norm <= x1:
            t = (norm - x0) / (x1 - x0) if x1 > x0 else 0
            return [int(c0[i] + t * (c1[i] - c0[i])) for i in range(3)]
    return list(stops[-1][1])


def od_3d(geojson, origen, dest_df, nivel, cents):
    cents = cents.dropna(subset=['lon', 'lat'])
    lon_c, lat_c = float(cents['lon'].mean()), float(cents['lat'].mean())
    extent = max(cents['lon'].max() - cents['lon'].min(),
                 cents['lat'].max() - cents['lat'].min(), 0.05)
    radius = max(extent * 111000 / max(len(cents), 1) ** 0.5 * 0.35, 120)
    elev_max = extent * 111000 * 0.55

    layers = []
    # contexto: polígonos de zona
    if geojson:
        layers.append(pdk.Layer(
            'GeoJsonLayer', geojson, stroked=True, filled=True,
            get_fill_color=[210, 215, 222, 35], get_line_color=[150, 158, 170, 90],
            line_width_min_pixels=0.5, pickable=(nivel == 'zona'), auto_highlight=True, id='zonas'))
        if nivel == 'zona':
            feats = [f for f in geojson['features'] if str(f['properties'].get('zona')) == str(origen)]
            if feats:
                layers.append(pdk.Layer(
                    'GeoJsonLayer', {'type': 'FeatureCollection', 'features': feats},
                    stroked=True, filled=True, get_fill_color=[31, 111, 235, 120],
                    get_line_color=[31, 111, 235, 255], line_width_min_pixels=2.5, id='orig'))

    # destinos como columnas 3D
    dd = dest_df[dest_df['zona'].astype(str) != str(origen)].dropna(subset=['lon', 'lat']).copy()
    if len(dd):
        mx = dd['viajes'].max() or 1
        dd['norm'] = dd['viajes'] / mx
        dd['elev'] = dd['norm'] * elev_max
        cols = dd['norm'].map(_color)
        dd['r'] = [c[0] for c in cols]; dd['g'] = [c[1] for c in cols]; dd['b'] = [c[2] for c in cols]
        dd['viajes_fmt'] = dd['viajes'].round(0).astype(int)
        layers.append(pdk.Layer(
            'ColumnLayer', dd, get_position=['lon', 'lat'], get_elevation='elev',
            elevation_scale=1, radius=radius, get_fill_color=['r', 'g', 'b', 225],
            pickable=True, auto_highlight=True, id='dest'))

    # capa seleccionable de comunas (no hay polígonos de comuna)
    if nivel == 'comuna':
        cc = cents.copy(); cc['zona'] = cc['zona'].astype(str)
        layers.append(pdk.Layer(
            'ScatterplotLayer', cc, get_position=['lon', 'lat'], get_radius=radius * 0.6,
            get_fill_color=[31, 111, 235, 160], pickable=True, auto_highlight=True, id='sel_comuna'))

    view = pdk.ViewState(longitude=lon_c, latitude=lat_c, zoom=_zoom(extent), pitch=50, bearing=10)
    tooltip = {'html': '<b>{zona}</b><br/>{viajes_fmt} viajes', 'style': {'color': 'white'}}
    return pdk.Deck(layers=layers, initial_view_state=view, map_provider='carto',
                    map_style='light', tooltip=tooltip)


def id_seleccionado(event):
    """Extrae el id de zona/comuna clickeado desde el evento de st.pydeck_chart."""
    try:
        sel = event.get('selection') if isinstance(event, dict) else getattr(event, 'selection', None)
        objs = (sel or {}).get('objects', {}) if sel else {}
        for capa in ('zonas', 'sel_comuna'):
            lst = objs.get(capa) or []
            if lst:
                o = lst[0]
                if 'zona' in o:
                    return str(o['zona'])
                props = o.get('properties') if isinstance(o, dict) else None
                if props and 'zona' in props:
                    return str(props['zona'])
    except Exception:
        pass
    return None
