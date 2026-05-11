from servicios.db import get_connection
from datetime import datetime

def registrar_incidente(tipo, direccion, descripcion, lat, lon, gravedad, patrulla):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        query = """
            INSERT INTO incidentes (fecha, tipo, direccion, descripcion, lat, lon, gravedad, patrulla)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (fecha_actual, tipo, direccion, descripcion, lat, lon, gravedad, patrulla))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error en registrar_incidente: {e}")
        return False