# mapas/mapa_principal.py — Mapa principal v2.0
import folium
from folium.plugins import MarkerCluster
from branca.element import Element
from servicios.incidentes import listar_incidentes
from servicios.geo_logic import COORDS_ZONAS

# Colores de marcadores por gravedad
COLOR_MARCADOR = {
    "CRÍTICA":  "red",
    "CRITICA":  "red",
    "MUY ALTA": "red",
    "ALTA":     "orange",
    "MEDIA":    "beige",
    "BAJA":     "green",
    "DEFAULT":  "blue",
}

ICON_MARCADOR = {
    "CRÍTICA":  "exclamation-triangle",
    "CRITICA":  "exclamation-triangle",
    "MUY ALTA": "exclamation-triangle",
    "ALTA":     "warning-sign",
    "MEDIA":    "info-sign",
    "BAJA":     "map-marker",
    "DEFAULT":  "map-marker",
}


def _color_para_tipo(tipo: str) -> tuple:
    t = str(tipo).upper()
    for key in COLOR_MARCADOR:
        if key in t:
            return COLOR_MARCADOR[key], ICON_MARCADOR.get(key, "map-marker")
    return COLOR_MARCADOR["DEFAULT"], "map-marker"


def _popup_html(inc) -> str:
    """Genera HTML rico para el popup del marcador."""
    tipo  = inc[1] if inc[1] else "Sin tipo"
    desc  = inc[2] if inc[2] else "Sin descripción"
    fecha = inc[3] if inc[3] else "—"
    zona  = inc[4] if inc[4] else "—"
    estado = str(inc[6]).strip() if len(inc) > 6 else "Activo"
    estado_badge = (
        "<span style='color:#059669;font-weight:bold'>✅ Finalizado</span>"
        if estado == "Finalizado" else
        "<span style='color:#DC2626;font-weight:bold'>🚨 Activo</span>"
    )
    return f"""
    <div style='font-family:Segoe UI,sans-serif;min-width:220px;max-width:300px'>
        <div style='background:#0A1F44;color:white;padding:8px 12px;border-radius:4px 4px 0 0;
                    font-size:13px;font-weight:bold'>{tipo}</div>
        <div style='padding:10px 12px;border:1px solid #E2E8F0;border-top:none;
                    border-radius:0 0 4px 4px;background:white'>
            <p style='margin:4px 0;font-size:12px;color:#334155'>{desc[:120]}{'…' if len(desc)>120 else ''}</p>
            <hr style='border:none;border-top:1px solid #F1F5F9;margin:8px 0'>
            <p style='margin:2px 0;font-size:11px;color:#64748B'>📍 {zona}</p>
            <p style='margin:2px 0;font-size:11px;color:#64748B'>🕐 {fecha}</p>
            <p style='margin:4px 0;font-size:11px'>{estado_badge}</p>
        </div>
    </div>
    """


def crear_mapa_principal(solo_activos: bool = False):
    """
    Genera y devuelve el mapa Folium con todos los incidentes marcados.
    solo_activos=True muestra únicamente los incidentes en estado Activo.
    """
    mapa = folium.Map(
        location=[40.4839, -3.3644],
        zoom_start=14,
        tiles="cartodbpositron"
    )

    # ── Capa de zonas (círculos suaves) ──────────────────────────
    zona_layer = folium.FeatureGroup(name="Zonas", show=True)
    for zona, (lat, lon) in COORDS_ZONAS.items():
        if zona == "Zona desconocida":
            continue
        folium.Circle(
            location=[lat, lon],
            radius=600,
            color="#1976D2", fill=True, fill_color="#1976D2",
            fill_opacity=0.05, weight=1, opacity=0.3,
            tooltip=zona
        ).add_to(zona_layer)
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:10px;color:#1976D2;font-weight:bold;'
                     f'white-space:nowrap;opacity:0.7">{zona}</div>',
                icon_size=(160, 20), icon_anchor=(0, 10)
            )
        ).add_to(zona_layer)
    zona_layer.add_to(mapa)

    # ── Capas por gravedad ────────────────────────────────────────
    capas = {
        "🔴 Críticos":    folium.FeatureGroup(name="🔴 Críticos",  show=True),
        "🟠 Alta":        folium.FeatureGroup(name="🟠 Alta",      show=True),
        "🟡 Media/Baja":  folium.FeatureGroup(name="🟡 Media/Baja",show=True),
        "✅ Finalizados": folium.FeatureGroup(name="✅ Finalizados",show=False),
    }

    registros = listar_incidentes()
    activos = finalizados = 0

    for inc in registros:
        estado = str(inc[6]).strip() if len(inc) > 6 else "Activo"
        if solo_activos and estado != "Activo":
            continue

        zona = inc[4] or "Zona desconocida"
        coords = COORDS_ZONAS.get(zona, COORDS_ZONAS["Zona desconocida"])
        # Pequeño offset aleatorio para evitar solapamiento exacto
        import random
        offset = lambda: random.uniform(-0.002, 0.002)
        lat, lon = coords[0] + offset(), coords[1] + offset()

        color, icon_name = _color_para_tipo(inc[1])
        popup = folium.Popup(folium.IFrame(_popup_html(inc), width=320, height=180),
                             max_width=320)

        marker = folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=f"{inc[1][:40]} — {zona}",
            icon=folium.Icon(color=color, icon=icon_name, prefix="glyphicon")
        )

        if estado == "Finalizado":
            marker.add_to(capas["✅ Finalizados"])
            finalizados += 1
        else:
            t = str(inc[1]).upper()
            if any(x in t for x in ["CRÍTICA","CRITICA","MUY ALTA","ARMA","DISPARO"]):
                marker.add_to(capas["🔴 Críticos"])
            elif "ALTA" in t:
                marker.add_to(capas["🟠 Alta"])
            else:
                marker.add_to(capas["🟡 Media/Baja"])
            activos += 1

    for capa in capas.values():
        capa.add_to(mapa)

    folium.LayerControl(collapsed=False).add_to(mapa)

    # ── Panel de resumen en el mapa ───────────────────────────────
    resumen_html = f"""
    <div style="position:fixed;bottom:30px;left:30px;z-index:9999;
                background:white;padding:12px 16px;border-radius:8px;
                box-shadow:0 2px 12px rgba(0,0,0,0.15);font-family:Segoe UI,sans-serif">
        <div style="font-size:13px;font-weight:bold;color:#0A1F44;margin-bottom:6px">
            🛡️ CSA — Estado operativo
        </div>
        <div style="font-size:12px;color:#DC2626">🚨 Activos: <b>{activos}</b></div>
        <div style="font-size:12px;color:#059669">✅ Finalizados: <b>{finalizados}</b></div>
    </div>
    """
    mapa.get_root().html.add_child(Element(resumen_html))

    return mapa
