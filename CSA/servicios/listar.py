import pandas as pd
from servicios.db import get_connection

def listar_incidentes_df():
    conn = get_connection()
    try:
        # Leemos TODOS los datos para que el DataFrame no esté vacío
        df = pd.read_sql_query("SELECT * FROM incidentes", conn)
        return df
    except Exception as e:
        print(f"Error en DF: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def eliminar_incidente_db(id_incidente):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM incidentes WHERE id = ?", (id_incidente,))
        conn.commit()
    finally:
        conn.close() # Esto libera la base de datos inmediatamente

def actualizar_incidente_db(id_inc, tipo, direccion, descripcion, gravedad):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        UPDATE incidentes 
        SET tipo=?, direccion=?, descripcion=?, gravedad=? 
        WHERE id=?
    """
    cursor.execute(query, (tipo, direccion, descripcion, gravedad, id_inc))
    conn.commit()
    conn.close()