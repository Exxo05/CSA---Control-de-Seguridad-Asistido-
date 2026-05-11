import folium
from folium.plugins import HeatMap
import pandas as pd
from servicios.listar import listar_incidentes_df
from servicios.historicos import listar_historicos_df

def crear_mapa_calor():
    df_hist = listar_historicos_df()
    
    mapa = folium.Map(location=[40.4820, -3.3596], zoom_start=13, tiles="CartoDB positron")
    
    try:
        df_h = df_hist.copy()
        df_h['lat'] = pd.to_numeric(df_h['lat'], errors='coerce')
        df_h['lon'] = pd.to_numeric(df_h['lon'], errors='coerce')
        puntos = df_h[['lat', 'lon']].dropna().values.tolist()

        if puntos:
            HeatMap(puntos, radius=15).add_to(mapa)
            mapa.fit_bounds(puntos)
    except:
        pass

    return mapa