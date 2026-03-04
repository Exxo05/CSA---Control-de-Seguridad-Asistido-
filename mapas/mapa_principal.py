import folium
from branca.element import Element
from servicios.incidentes import listar_incidentes

def crear_mapa_principal():
    # 1. Crear el mapa base centrado en Alcalá
    mapa = folium.Map(location=[40.4839, -3.3644], zoom_start=14, tiles="cartodbpositron")

    coords_barrios = {
        "Centro": [40.4819, -3.3635],
        "La Garena": [40.4824, -3.3892],
        "Chorrillo": [40.4930, -3.3590],
        "Reyes Católicos": [40.4780, -3.3750],
        "Espartales": [40.5050, -3.3500],
        "El Val": [40.4800, -3.3450]
    }

    # 2. Dibujar Incidentes (Solo Activos)
    registros = listar_incidentes()
    for inc in registros:
        # inc[6] es el estado
        if str(inc[6]).strip().lower() == "activo":
            zona = inc[4]
            if zona in coords_barrios:
                folium.Marker(
                    location=coords_barrios[zona],
                    popup=f"<b>🚨 {inc[1]}</b><br>{inc[2]}",
                    icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
                ).add_to(mapa)

    # 3. EL BOTÓN DE REFRESCO (Inyectamos HTML/CSS/JS)
    boton_refresh_html = """
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 150px; height: 40px; 
                z-index:9999; font-size:14px;
                ">
        <button onclick="location.reload()" 
                style="width: 100%; height: 100%; 
                background-color: #2ecc71; color: white; 
                border: 2px solid white; border-radius: 5px; 
                font-weight: bold; cursor: pointer;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.2);">
            🔄 ACTUALIZAR MAPA
        </button>
    </div>
    """
    
    # Añadimos el elemento al HTML del mapa
    mapa.get_root().html.add_child(Element(boton_refresh_html))

    return mapa