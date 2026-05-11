import folium

def crear_mapa_principal(df):

    mapa = folium.Map(
        location=[40.4810, -3.3640],  # Alcalá de Henares
        zoom_start=13,
        prefer_canvas=True
    )

    for _, row in df.iterrows():
        if row["lat"] and row["lon"]:
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=f"""
                <b>Tipo:</b> {row['tipo']}<br>
                <b>Dirección:</b> {row['direccion']}<br>
                <b>Descripción:</b> {row['descripcion']}<br>
                <b>Gravedad:</b> {row['gravedad']}
                """,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(mapa)

    return mapa._repr_html_()
