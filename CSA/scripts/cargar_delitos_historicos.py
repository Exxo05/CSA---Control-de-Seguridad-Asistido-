from servicios.db import get_conn
import random
from datetime import datetime, timedelta

TIPOS_DELITO = [
    "Robo con violencia o intimidación",
    "Hurto",
    "Daños / vandalismo",
    "Lesiones",
    "Tráfico de drogas / narcomenudeo",
    "Desórdenes públicos"
]

# Zonas aproximadas de Alcalá de Henares
ZONAS = [
    (40.4810, -3.3635),  # Centro
    (40.4845, -3.3700),  # Reyes Católicos
    (40.4750, -3.3550),  # Espartales
    (40.4900, -3.3500),  # La Garena
    (40.4700, -3.3700)   # Juan de Austria
]

def generar_fecha():
    dias_atras = random.randint(30, 365 * 3)
    return (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")

def main():
    conn = get_conn()
    c = conn.cursor()

    for _ in range(120):  # número de delitos ficticios
        tipo = random.choice(TIPOS_DELITO)
        lat, lon = random.choice(ZONAS)
        lat += random.uniform(-0.002, 0.002)
        lon += random.uniform(-0.002, 0.002)
        gravedad = random.choice(["baja", "media", "alta"])
        fecha = generar_fecha()

        c.execute("""
            INSERT INTO delitos_historicos (fecha, tipo, lat, lon, gravedad)
            VALUES (?, ?, ?, ?, ?)
        """, (fecha, tipo, lat, lon, gravedad))

    conn.commit()
    conn.close()
    print("Delitos históricos cargados correctamente.")

if __name__ == "__main__":
    main()
