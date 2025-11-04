# mapas/mapa.py
import folium
from folium.plugins import MarkerCluster
from branca.colormap import linear

# Coordenadas centrales de Alcalá de Henares (aprox.)
CENTRO = (40.4810, -3.3635)

def crear_mapa(df_incidentes):
    m = folium.Map(location=CENTRO, zoom_start=13)
    marker_cluster = MarkerCluster().add_to(m)

    # Colores por gravedad
    color_map = {'baja':'green', 'media':'orange', 'alta':'red'}

    for _, row in df_incidentes.iterrows():
        if not (row.get('lat') and row.get('lon')):
            continue
        popup = folium.Popup(f"""
            <b>Tipo:</b> {row.get('tipo')}<br>
            <b>Fecha:</b> {row.get('fecha')}<br>
            <b>Gravedad:</b> {row.get('gravedad')}<br>
            <b>Desc:</b> {row.get('descripcion')}
        """, max_width=300)
        folium.Marker(
            location=(row['lat'], row['lon']),
            popup=popup,
            icon=folium.Icon(color=color_map.get(str(row.get('gravedad')).lower(), 'blue'))
        ).add_to(marker_cluster)

    return m
