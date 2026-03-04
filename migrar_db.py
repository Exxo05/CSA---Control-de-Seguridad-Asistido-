# Ejecuta esto para "arreglar" la base de datos si ya existía
import sqlite3
from servicios.db import get_connection

def parchear_base_datos():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Intentamos añadir la columna estado por si no existe
        cursor.execute("ALTER TABLE incidentes ADD COLUMN estado TEXT DEFAULT 'Activo'")
        conn.commit()
        print("✅ Columna 'estado' añadida correctamente.")
    except sqlite3.OperationalError:
        print("ℹ️ La columna 'estado' ya existía.")
    finally:
        conn.close()

parchear_base_datos()