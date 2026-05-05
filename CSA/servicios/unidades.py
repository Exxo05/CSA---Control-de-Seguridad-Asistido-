import sqlite3
from servicios.db import get_connection

def inicializar_unidades():
    conn = get_connection()
    cursor = conn.cursor()
    # 1. Crear tabla base
    cursor.execute('''CREATE TABLE IF NOT EXISTS unidades 
                     (id INTEGER PRIMARY KEY, indicativo TEXT UNIQUE, estado TEXT, 
                      en_servicio INTEGER DEFAULT 0, ubicacion_actual TEXT)''')
    
    # 2. PARCHE: Asegurar que existe la columna de ubicación
    try:
        cursor.execute("ALTER TABLE unidades ADD COLUMN ubicacion_actual TEXT")
    except sqlite3.OperationalError:
        pass 

    # 3. Datos iniciales de Alcalá
    cursor.execute("SELECT COUNT(*) FROM unidades")
    if cursor.fetchone()[0] == 0:
        patrullas = [
            ('Z-10', 'Disponible', 'Casco Histórico'),
            ('Z-20', 'Disponible', 'Reyes Católicos'),
            ('Z-30', 'Disponible', 'Chorrillo / Ensanche'),
            ('Z-40', 'Disponible', 'La Garena'),
            ('K-5', 'Disponible', 'Espartales')
        ]
        cursor.executemany("INSERT INTO unidades (indicativo, estado, ubicacion_actual) VALUES (?, ?, ?)", patrullas)
    conn.commit()
    conn.close()

def listar_unidades(solo_en_servicio=False):
    conn = get_connection()
    cursor = conn.cursor()
    if solo_en_servicio:
        cursor.execute("SELECT * FROM unidades WHERE en_servicio = 1")
    else:
        cursor.execute("SELECT * FROM unidades")
    unidades = cursor.fetchall()
    conn.close()
    return unidades

def alternar_servicio(u_id, valor):
    """Activa o desactiva la unidad para el turno"""
    conn = get_connection()
    cursor = conn.cursor()
    estado_inicial = "Patrullando" if valor == 1 else "En Base"
    cursor.execute("UPDATE unidades SET en_servicio = ?, estado = ? WHERE id = ?", (valor, estado_inicial, u_id))
    conn.commit()
    conn.close()

def cambiar_estado_operativo(u_id, nuevo_estado):
    """Cambia el estado de radio (Patrullando, Intervención, etc.)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE unidades SET estado = ? WHERE id = ?", (nuevo_estado, u_id))
    conn.commit()
    conn.close()

def asignar_unidad_a_incidente(unidad_id, nueva_zona):
    """Mueve la unidad al lugar del incidente y la pone en intervención"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE unidades 
        SET estado = 'En Intervención', ubicacion_actual = ? 
        WHERE id = ?
    """, (nueva_zona, unidad_id))
    conn.commit()
    conn.close()