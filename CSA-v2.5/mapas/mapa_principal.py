# mapas/mapa_principal.py — v3.2 con patrullas en mapa
import folium
import random
from branca.element import Element
from servicios.incidentes import listar_incidentes
from servicios.geo_logic  import COORDS_ZONAS

COLOR_MAP = {
    "CRÍTICA":"red","CRITICA":"red","MUY ALTA":"red",
    "ALTA":"orange","MEDIA":"beige","BAJA":"green",
}
ICON_MAP = {
    "CRÍTICA":"exclamation-sign","CRITICA":"exclamation-sign",
    "MUY ALTA":"exclamation-sign","ALTA":"warning-sign",
    "MEDIA":"info-sign","BAJA":"map-marker",
}

def _color_icono(tipo: str):
    t = str(tipo).upper()
    for k in COLOR_MAP:
        if k in t:
            return COLOR_MAP[k], ICON_MAP.get(k,"map-marker")
    return "blue","map-marker"

def _popup_html(inc, lat, lon) -> str:
    tipo  = inc[1] or "Sin tipo"
    desc  = inc[2] or "Sin descripción"
    fecha = inc[3] or "—"
    zona  = inc[4] or "—"
    dir_  = inc[5] or "—"
    estado = str(inc[6]).strip() if len(inc) > 6 else "Activo"
    badge = ("<span style='color:#059669;font-weight:bold'>✅ Finalizado</span>"
             if estado == "Finalizado" else
             "<span style='color:#DC2626;font-weight:bold'>🚨 Activo</span>")
    coords_txt = f"{lat:.5f}, {lon:.5f}" if lat else "Aprox."
    return f"""
    <div style='font-family:Segoe UI,sans-serif;min-width:240px;max-width:320px'>
      <div style='background:#0A1F44;color:white;padding:8px 12px;
                  border-radius:4px 4px 0 0;font-size:13px;font-weight:bold'>{tipo}</div>
      <div style='padding:10px 12px;border:1px solid #E2E8F0;border-top:none;
                  border-radius:0 0 4px 4px;background:white'>
        <p style='margin:4px 0;font-size:12px;color:#334155'>
          {desc[:130]}{'…' if len(desc)>130 else ''}</p>
        <hr style='border:none;border-top:1px solid #F1F5F9;margin:8px 0'>
        <p style='margin:2px 0;font-size:11px;color:#64748B'>📍 {dir_}  ({zona})</p>
        <p style='margin:2px 0;font-size:11px;color:#64748B'>🗺️ {coords_txt}</p>
        <p style='margin:2px 0;font-size:11px;color:#64748B'>🕐 {fecha}</p>
        <p style='margin:4px 0;font-size:11px'>{badge}</p>
      </div>
    </div>"""

def _popup_patrulla(u) -> str:
    ind    = u[1] or "?"
    estado = u[2] or "Disponible"
    zona   = u[4] or "Sin zona"
    srv    = "✅ En servicio" if u[3] else "❌ Fuera de servicio"
    color  = "#D97706" if "Intervención" in estado else "#059669" if u[3] else "#6B7280"
    return f"""
    <div style='font-family:Segoe UI,sans-serif;min-width:180px'>
      <div style='background:#0A1F44;color:white;padding:8px 12px;
                  border-radius:4px 4px 0 0;font-size:14px;font-weight:bold'>
        🚓 {ind}</div>
      <div style='padding:10px 12px;border:1px solid #E2E8F0;
                  border-top:none;background:white;border-radius:0 0 4px 4px'>
        <p style='margin:3px 0;font-size:12px;color:{color};font-weight:bold'>{estado}</p>
        <p style='margin:3px 0;font-size:11px;color:#64748B'>📍 {zona}</p>
        <p style='margin:3px 0;font-size:11px;color:#64748B'>{srv}</p>
      </div>
    </div>"""

def crear_mapa_principal(solo_activos: bool = False):
    mapa = folium.Map(location=[40.4839,-3.3644], zoom_start=14,
                      tiles="cartodbpositron")

    # Capa de barrios
    zona_layer = folium.FeatureGroup(name="Barrios", show=True)
    for zona,(zlat,zlon) in COORDS_ZONAS.items():
        if zona.startswith("Zona") or zona.startswith("Municipio"):
            continue
        folium.Circle(location=[zlat,zlon], radius=550,
                      color="#1976D2", fill=True, fill_color="#1976D2",
                      fill_opacity=0.04, weight=1, opacity=0.25,
                      tooltip=zona).add_to(zona_layer)
        folium.Marker(
            location=[zlat,zlon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:9px;color:#1976D2;'
                     f'font-weight:bold;white-space:nowrap;opacity:0.6">{zona}</div>',
                icon_size=(180,18), icon_anchor=(0,9))
        ).add_to(zona_layer)
    zona_layer.add_to(mapa)

    # ── Capa de patrullas ─────────────────────────────────────────
    patrulla_layer = folium.FeatureGroup(name="🚓 Patrullas", show=True)
    try:
        from servicios.db import get_connection
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT id,indicativo,estado,en_servicio,
                   ubicacion_actual,lat,lon FROM unidades
        """)
        unidades = c.fetchall()
        conn.close()

        for u in unidades:
            lat_u = lon_u = None
            # Coords GPS si existen
            if len(u) >= 7 and u[5] and u[6]:
                try:
                    lat_u, lon_u = float(u[5]), float(u[6])
                except (TypeError, ValueError):
                    pass

            # Si no hay GPS, usar centroide de zona
            if not lat_u or not lon_u:
                zona_u = u[4] or "Zona desconocida"
                # Limpiar zona si está corrupta (muy larga)
                if len(str(zona_u)) > 60:
                    zona_u = "Zona desconocida"
                zlat, zlon = COORDS_ZONAS.get(zona_u, COORDS_ZONAS["Zona desconocida"])
                lat_u = zlat + random.uniform(-0.0008, 0.0008)
                lon_u = zlon + random.uniform(-0.0008, 0.0008)

            # Color del icono según estado
            estado = str(u[2] or "")
            if "Intervención" in estado:
                icon_color = "orange"
            elif u[3]:  # en servicio
                icon_color = "blue"
            else:
                icon_color = "gray"

            popup = folium.Popup(
                folium.IFrame(_popup_patrulla(u), width=220, height=140),
                max_width=220)
            folium.Marker(
                location=[lat_u, lon_u],
                popup=popup,
                tooltip=f"🚓 {u[1]} — {estado or 'Disponible'}",
                icon=folium.Icon(color=icon_color, icon="car",
                                 prefix="glyphicon")
            ).add_to(patrulla_layer)

    except Exception as e:
        print(f"[Mapa] Error cargando patrullas: {e}")

    patrulla_layer.add_to(mapa)

    # ── Capas de incidentes ───────────────────────────────────────
    capas = {
        "🔴 Críticos":    folium.FeatureGroup(name="🔴 Críticos",   show=True),
        "🟠 Alta":        folium.FeatureGroup(name="🟠 Alta",        show=True),
        "🟡 Media/Baja":  folium.FeatureGroup(name="🟡 Media/Baja",  show=True),
        "✅ Finalizados": folium.FeatureGroup(name="✅ Finalizados",  show=False),
    }

    from servicios.db import get_connection
    conn = get_connection()
    try:
        c = conn.cursor()
        try:
            c.execute("SELECT id,tipo,descripcion,fecha,zona,direccion,estado,lat,lon"
                      " FROM incidentes ORDER BY id DESC")
            registros  = c.fetchall()
            tiene_coords = True
        except Exception:
            c.execute("SELECT id,tipo,descripcion,fecha,zona,direccion,estado"
                      " FROM incidentes ORDER BY id DESC")
            registros  = c.fetchall()
            tiene_coords = False
    finally:
        conn.close()

    activos = finalizados = 0

    for inc in registros:
        estado = str(inc[6]).strip() if len(inc) > 6 else "Activo"
        if solo_activos and estado != "Activo":
            continue

        lat = lon = None
        if tiene_coords and len(inc) >= 9:
            try:
                lat = float(inc[7]) if inc[7] else None
                lon = float(inc[8]) if inc[8] else None
            except (TypeError, ValueError):
                lat = lon = None

        if not lat or not lon:
            zona = inc[4] or "Zona desconocida"
            if len(str(zona)) > 60:
                zona = "Zona desconocida"
            zlat,zlon = COORDS_ZONAS.get(zona, COORDS_ZONAS["Zona desconocida"])
            lat = zlat + random.uniform(-0.0015, 0.0015)
            lon = zlon + random.uniform(-0.0015, 0.0015)

        color, icono = _color_icono(inc[1])
        popup  = folium.Popup(
            folium.IFrame(_popup_html(inc, lat, lon), width=340, height=200),
            max_width=340)
        marker = folium.Marker(
            location=[lat,lon], popup=popup,
            tooltip=f"#{inc[0]} — {str(inc[1])[:40]}",
            icon=folium.Icon(color=color, icon=icono, prefix="glyphicon"))

        if estado == "Finalizado":
            marker.add_to(capas["✅ Finalizados"]); finalizados += 1
        else:
            t = str(inc[1]).upper()
            if any(x in t for x in ["CRÍTICA","CRITICA","MUY ALTA","ARMA","DISPARO"]):
                marker.add_to(capas["🔴 Críticos"])
            elif "ALTA" in t:
                marker.add_to(capas["🟠 Alta"])
            else:
                marker.add_to(capas["🟡 Media/Baja"])
            activos += 1

    for c in capas.values():
        c.add_to(mapa)

    folium.LayerControl(collapsed=False).add_to(mapa)

    panel = f"""
    <div style="position:fixed;bottom:30px;left:30px;z-index:9999;
                background:white;padding:12px 16px;border-radius:8px;
                box-shadow:0 2px 12px rgba(0,0,0,.15);font-family:Segoe UI,sans-serif">
      <div style="font-size:13px;font-weight:bold;color:#0A1F44;margin-bottom:6px">
        🛡️ CSA — Estado operativo</div>
      <div style="font-size:12px;color:#DC2626">🚨 Activos: <b>{activos}</b></div>
      <div style="font-size:12px;color:#059669">✅ Finalizados: <b>{finalizados}</b></div>
      <div style="font-size:12px;color:#1976D2">🚓 Patrullas: <b>{len(unidades) if 'unidades' in dir() else '?'}</b></div>
    </div>"""
    mapa.get_root().html.add_child(Element(panel))
    return mapa
