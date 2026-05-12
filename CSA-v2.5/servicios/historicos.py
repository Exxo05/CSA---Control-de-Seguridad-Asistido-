# servicios/historicos.py
import pandas as pd
from servicios.db import get_connection


def _inicializar_tabla():
    """Crea la tabla delitos_historicos si no existe."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS delitos_historicos (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo    TEXT,
                fecha   TEXT,
                lat     REAL,
                lon     REAL,
                zona    TEXT,
                descripcion TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()


def listar_historicos_df() -> pd.DataFrame:
    _inicializar_tabla()
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM delitos_historicos", conn)
        conn.close()

        if df.empty:
            return df

        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df.dropna(subset=['lat', 'lon'])

    except Exception as e:
        print(f"Error al leer históricos: {e}")
        return pd.DataFrame()


def registrar_historico(tipo: str, fecha: str, lat: float,
                         lon: float, zona: str = "", descripcion: str = "") -> bool:
    """Inserta un registro en el histórico."""
    _inicializar_tabla()
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO delitos_historicos (tipo, fecha, lat, lon, zona, descripcion) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (tipo, fecha, lat, lon, zona, descripcion)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al registrar histórico: {e}")
        return False
