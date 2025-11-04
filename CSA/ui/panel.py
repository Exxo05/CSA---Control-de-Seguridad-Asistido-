# ui/panel.py
import streamlit as st
from servicios.registrar import registrar_incidente
from servicios.listar import listar_incidentes_df
from mapas.mapa import crear_mapa
from streamlit_folium import st_folium
from utils.helpers import geocode_address
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import os

def app():
    st.set_page_config(layout="wide", page_title="CSA - Hito 1 Mejorado")
    st.title("CSA - Control de Seguridad Asistido (Hito 1)")

    menu = st.sidebar.selectbox(
        "Menú",
        ["Registrar incidente", "Incidentes", "Mapa", "Estadísticas"]
    )

    # --- REGISTRAR INCIDENTE ---
    if menu == "Registrar incidente":
        st.header("Registrar nuevo incidente")

        # Lista ampliada de tipos
        tipos_delitos = [
            "Robo", 
            "Hurto", 
            "Daños", 
            "Fraudes y estafas",
            "Lesiones", 
            "Amenazas y coacciones",
            "Violencia de género o doméstica",
            "Homicidio o asesinato",
            "Agresiones y abusos sexuales",
            "Acoso sexual",
            "Desórdenes públicos",
            "Tráfico de drogas y narcomenudeo",
            "Tenencia ilícita de armas",
            "Delitos contra la seguridad vial",
            "Otro"
        ]

        tipo = st.selectbox("Tipo de delito", tipos_delitos)
        descripcion = st.text_area("Descripción del incidente")
        gravedad = st.selectbox("Gravedad", ["baja", "media", "alta"])
        usar_direccion = st.checkbox("Usar dirección en vez de coordenadas")

        # Variables iniciales
        lat = lon = None
        direccion = ""

        if usar_direccion:
            direccion = st.text_input("Dirección (ej: Calle Mayor, Alcalá de Henares)")
        else:
            lat = st.number_input("Latitud", format="%.6f", value=40.4810)
            lon = st.number_input("Longitud", format="%.6f", value=-3.3635)

        # Botón registrar
        if st.button("Registrar incidente"):
            if not descripcion.strip():
                st.warning("Por favor, introduce una descripción del incidente.")
            else:
                if usar_direccion:
                    if not direccion:
                        st.warning("Introduce una dirección o desactiva la opción.")
                    else:
                        with st.spinner("Geolocalizando dirección..."):
                            lat, lon = geocode_address(direccion)
                if lat is None or lon is None:
                    st.error("No se pudieron obtener coordenadas válidas.")
                else:
                    registrar_incidente(tipo, descripcion, lat, lon, gravedad)
                    st.success("✅ Incidente registrado correctamente.")

    # --- LISTADO DE INCIDENTES ---
    elif menu == "Incidentes":
        st.header("Listado de incidentes registrados")
        df = listar_incidentes_df()

        if df.empty:
            st.info("No hay incidentes registrados.")
        else:
            st.dataframe(df)

            # Botón para borrar todos los incidentes
            if st.button("🧹 Borrar todos los incidentes"):
                ruta = "data/incidentes.csv"
                if os.path.exists(ruta):
                    os.remove(ruta)
                    st.warning("Todos los incidentes han sido eliminados.")
                else:
                    st.info("No hay archivo de incidentes que borrar.")

    # --- MAPA DE INCIDENTES ---
    elif menu == "Mapa":
        st.header("Mapa de incidentes")
        df = listar_incidentes_df()

        if df.empty:
            st.info("No hay datos para mostrar en el mapa.")
        else:
            # Filtros dinámicos
            st.sidebar.markdown("### 🔎 Filtros de mapa")
            tipos = sorted(df['tipo'].unique().tolist())
            gravedades = sorted(df['gravedad'].unique().tolist())

            tipo_sel = st.sidebar.multiselect("Tipo de incidente", options=tipos, default=tipos)
            gravedad_sel = st.sidebar.multiselect("Gravedad", options=gravedades, default=gravedades)

            df_filtrado = df[(df['tipo'].isin(tipo_sel)) & (df['gravedad'].isin(gravedad_sel))]

            if df_filtrado.empty:
                st.warning("No hay incidentes que coincidan con los filtros seleccionados.")
            else:
                # Mapa grande y dinámico
                centro = [40.4810, -3.3635]
                m = folium.Map(location=centro, zoom_start=13, width="100%", height="100%")
                marker_cluster = MarkerCluster().add_to(m)

                color_map = {"baja": "green", "media": "orange", "alta": "red"}

                for _, row in df_filtrado.iterrows():
                    try:
                        lat_row = float(row.get("lat"))
                        lon_row = float(row.get("lon"))
                    except Exception:
                        continue

                    popup_html = f"""
                    <b>Tipo:</b> {row.get('tipo')}<br>
                    <b>Gravedad:</b> {row.get('gravedad')}<br>
                    <b>Descripción:</b> {row.get('descripcion')}<br>
                    <b>Lat/Lon:</b> {lat_row:.6f}, {lon_row:.6f}
                    """

                    folium.Marker(
                        location=(lat_row, lon_row),
                        popup=folium.Popup(popup_html, max_width=350),
                        tooltip=row.get("tipo"),
                        icon=folium.Icon(color=color_map.get(str(row.get("gravedad")).lower(), "blue")),
                    ).add_to(marker_cluster)

                # Mapa ampliado
                st_folium(m, width=1400, height=800)

    # --- ESTADÍSTICAS ---
    elif menu == "Estadísticas":
        st.header("📊 Estadísticas básicas")
        df = listar_incidentes_df()
        if df.empty:
            st.info("No hay datos para mostrar.")
        else:
            tipos = df["tipo"].value_counts()
            st.subheader("Incidentes por tipo")
            st.bar_chart(tipos)

            st.subheader("Tabla resumen")
            st.table(tipos.reset_index().rename(columns={"index": "Tipo", "tipo": "Cantidad"}))
