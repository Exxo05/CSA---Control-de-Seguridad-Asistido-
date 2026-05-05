import pandas as pd
from servicios.db import get_connection

def listar_historicos_df():
    try:
        conn = get_connection()
        # APUNTAMOS A TU TABLA REAL: delitos_historicos
        query = "SELECT * FROM delitos_historicos"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            print("⚠️ La tabla delitos_historicos está vacía.")
            return df

        # Limpieza crucial: convertir lat/lon a números y eliminar filas corruptas
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        # Filtramos filas que no tengan coordenadas válidas
        df_limpio = df.dropna(subset=['lat', 'lon'])
        
        print(f"✅ Cargados {len(df_limpio)} delitos históricos correctamente.")
        return df_limpio

    except Exception as e:
        print(f"❌ Error al leer delitos_historicos: {e}")
        return pd.DataFrame()