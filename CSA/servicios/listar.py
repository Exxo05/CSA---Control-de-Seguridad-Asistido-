# servicios/listar.py
from servicios.db import get_conn
import pandas as pd

def listar_incidentes_df(limit=1000):
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM incidentes ORDER BY fecha DESC LIMIT ?", conn, params=(limit,))
    conn.close()
    return df
