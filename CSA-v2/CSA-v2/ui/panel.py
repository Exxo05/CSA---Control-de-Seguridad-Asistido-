# ui/panel.py
import os
import streamlit as st
from servicios.registrar import registrar_incidente, borrar_incidentes_por_ids
from servicios.listar import listar_incidentes_df
from mapas.mapa_principal import crear_mapa_basico
from streamlit_folium import st_folium
from utils.helpers import geocode_address
import pandas as pd
import io

def app():
    st.set_page_config(layout="wide", page_title="CSA - Control de Seguridad Asistido")
    st.title("CSA - Control de Seguridad Asistido")

    # logo (seguro)
    logo_path = "assets/logo_CSA.png"
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=160)
    else:
        st.sidebar.write("Coloca el logo en 'assets/logo.png' para mostrarlo aquí.")

    menu = st.sidebar.selectbox("Menú", ["Registrar incidente", "Incidentes", "Mapa", "Estadísticas"])

    # ---------- Registrar incidente (solo dirección) ----------
    if menu == "Registrar incidente":
        st.header("Registrar nuevo incidente")
        st.markdown("**Campos obligatorios marcados con *:**")
        with st.form("form_incidente", clear_on_submit=True):
            tipo = st.selectbox("Tipo de delito *", [
                "Robo (violencia o intimidación)",
                "Robo (fuerza en las cosas)",
                "Hurto",
                "Daños / Vandalismo",
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
            ])
            descripcion = st.text_area("Descripción *", placeholder="Describe lo ocurrido (mínimo 10 caracteres)")
            gravedad = st.selectbox("Gravedad *", ["alta", "media", "baja"])

            # SOLO DIRECCIÓN
            st.markdown("**Localización (introduce dirección)**")
            calle = st.text_input("Calle *", placeholder="Calle Mayor")
            numero = st.text_input("Número", placeholder="10")
            localidad = st.text_input("Localidad *", value="Alcalá de Henares")

            submitted = st.form_submit_button("Registrar incidente")
            if submitted:
                if not descripcion or len(descripcion.strip()) < 10:
                    st.warning("La descripción debe tener al menos 10 caracteres.")
                elif not (calle and localidad):
                    st.warning("Introduce calle y localidad.")
                else:
                    address = f"{calle} {numero}, {localidad}".strip()
                    with st.spinner("Geolocalizando dirección..."):
                        lat, lon = geocode_address(address)
                    if lat is None or lon is None:
                        st.error("No se pudo geolocalizar la dirección. Comprueba los datos.")
                    elif not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180):
                        st.error("Coordenadas fuera de rango.")
                    else:
                        registrar_incidente(tipo, descripcion.strip(), float(lat), float(lon), gravedad, address=address)
                        st.success("✅ Incidente registrado correctamente.")

    # ---------- Incidentes: mostrar, seleccionar por fila y borrar ----------
    elif menu == "Incidentes":
        st.header("Listado de incidentes")
        df = listar_incidentes_df()

        if df.empty:
            st.info("No hay incidentes registrados.")
        else:
            # Mostrar tabla resumida
            df_display = df.copy()
            # Convertir fecha a string legible
            if 'fecha' in df_display.columns:
                df_display['fecha'] = df_display['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(df_display)

            st.markdown("**Selecciona los incidentes que quieras eliminar:**")
            # Checkbox por fila
            ids_to_delete = []
            for _, row in df_display.iterrows():
                rid = int(row['id'])
                label = f"{rid} — {row['tipo']} — {row.get('fecha','')} — {row.get('address','')}"
                if st.checkbox(label, key=f"del_{rid}"):
                    ids_to_delete.append(rid)

            if ids_to_delete:
                if st.button("🗑️ Eliminar seleccionados"):
                    borrar_incidentes_por_ids(ids_to_delete)
                    st.success(f"Eliminados {len(ids_to_delete)} incidentes. Recarga la página.")
            else:
                st.info("No hay incidentes seleccionados.")

    # ---------- Mapa grande con filtros y POIs ----------
    elif menu == "Mapa":
        st.header("Mapa de incidentes")
        df = listar_incidentes_df()
        if df.empty:
            st.info("No hay datos para mostrar en el mapa.")
        else:
            st.sidebar.markdown("### 🔎 Filtros de mapa")
            tipos = sorted(df['tipo'].unique().tolist())
            gravedades = sorted(df['gravedad'].unique().tolist())

            tipo_sel = st.sidebar.multiselect("Tipo de incidente", options=tipos, default=tipos)
            gravedad_sel = st.sidebar.multiselect("Gravedad", options=gravedades, default=gravedades)

            filtros = {'tipos': tipo_sel, 'gravedades': gravedad_sel}
            m = crear_mapa_basico(df, ancho="100%", alto="800px", filtros=filtros)
            st_folium(m, width=1400, height=800)

    # ---------- Estadísticas (descarga CSV/Excel) ----------
    elif menu == "Estadísticas":
        st.header("📊 Estadísticas detalladas")
        df = listar_incidentes_df()
        if df.empty:
            st.info("No hay datos para mostrar.")
        else:
            tipos = df['tipo'].value_counts()
            gravedades = df['gravedad'].value_counts()

            st.subheader("Incidentes por tipo")
            st.bar_chart(tipos)

            st.subheader("Incidentes por gravedad")
            st.bar_chart(gravedades)

            # Top y porcentajes
            st.subheader("Porcentaje por tipo (Top 10)")
            top = tipos.head(10)
            pct = (top / top.sum() * 100).round(1)
            st.table(pd.DataFrame({'Tipo': top.index, 'Cantidad': top.values, 'Porcentaje (%)': pct.values}))

            # Descargar estadísticas como CSV
            csv = df.to_csv(index=False)
            st.download_button("📥 Descargar estadísticas (CSV)", data=csv, file_name="estadisticas_incidentes.csv", mime="text/csv")

            # Descargar como Excel (si openpyxl está instalado)
            try:
                import openpyxl
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # escribir la tabla completa y también resumen
                    df.to_excel(writer, sheet_name='incidentes', index=False)
                    pd.DataFrame({'Tipo': tipos.index, 'Cantidad': tipos.values}).to_excel(writer, sheet_name='por_tipo', index=False)
                    pd.DataFrame({'Gravedad': gravedades.index, 'Cantidad': gravedades.values}).to_excel(writer, sheet_name='por_gravedad', index=False)
                st.download_button("📥 Descargar estadísticas (Excel)", data=output.getvalue(), file_name="estadisticas_incidentes.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception:
                st.info("Para descargar Excel instala 'openpyxl' en tu entorno (pip install openpyxl).")
