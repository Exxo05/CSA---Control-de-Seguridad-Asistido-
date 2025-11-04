# servicios/registrar.py
from servicios.db import get_conn
from datetime import datetime

def registrar_incidente(tipo, descripcion, lat, lon, gravedad):
    conn = get_conn()
    c = conn.cursor()
    fecha = datetime.now().isoformat(timespec='seconds')
    c.execute("""
        INSERT INTO incidentes (fecha, tipo, descripcion, lat, lon, gravedad)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha, tipo, descripcion, lat, lon, gravedad))
    conn.commit()
    conn.close()
