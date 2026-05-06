# servicios/unidades.py
import sqlite3
from servicios.db import get_connection

def inicializar_unidades():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS unidades 
                     (id INTEGER PRIMARY KEY, indicativo TEXT UNIQUE, estado TEXT, 
                      en_servicio INTEGER DEFAULT 0, ubicacion_actual TEXT)''')
    try:
        cursor.execute("ALTER TABLE unidades ADD COLUMN ubicacion_actual TEXT")
    except sqlite3.OperationalError:
        pass
    cursor.execute("SELECT COUNT(*) FROM unidades")
    if cursor.fetchone()[0] == 0:
        patrullas = [
            ('Z-10', 'Disponible', 'Casco Histórico / Centro'),
            ('Z-20', 'Disponible', 'Reyes Católicos'),
            ('Z-30', 'Disponible', 'Chorrillo / Ensanche'),
            ('Z-40', 'Disponible', 'La Garena'),
            ('K-5',  'Disponible', 'Espartales'),
        ]
        cursor.executemany(
            "INSERT INTO unidades (indicativo, estado, ubicacion_actual) VALUES (?, ?, ?)",
            patrullas
        )
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
    conn = get_connection()
    cursor = conn.cursor()
    estado_inicial = "Patrullando" if valor == 1 else "En Base"
    cursor.execute(
        "UPDATE unidades SET en_servicio = ?, estado = ? WHERE id = ?",
        (valor, estado_inicial, u_id)
    )
    conn.commit()
    conn.close()
    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=u_id)

def cambiar_estado_operativo(u_id, nuevo_estado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE unidades SET estado = ? WHERE id = ?", (nuevo_estado, u_id))
    conn.commit()
    conn.close()
    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=u_id)

def asignar_unidad_a_incidente(unidad_id, nueva_zona):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE unidades 
        SET estado = 'En Intervención', ubicacion_actual = ? 
        WHERE id = ?
    """, (nueva_zona, unidad_id))
    conn.commit()
    conn.close()
    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=unidad_id)

def finalizar_intervencion(u_id: int, zona_base: str = None):
    """
    Devuelve la unidad a 'Patrullando', la regresa a su zona base
    y cierra el incidente activo de la zona donde estaba interviniendo.
    Devuelve la zona donde estaba para poder cerrar el incidente.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ubicacion_actual FROM unidades WHERE id = ?", (u_id,))
    row = cursor.fetchone()
    zona_intervencion = row[0] if row else None

    nueva_zona = zona_base or zona_intervencion or "Sin zona"
    cursor.execute("""
        UPDATE unidades SET estado = 'Patrullando', ubicacion_actual = ?
        WHERE id = ?
    """, (nueva_zona, u_id))
    conn.commit()
    conn.close()

    # Cerrar el incidente activo en esa zona
    if zona_intervencion:
        from servicios.incidentes import finalizar_incidente_por_zona
        finalizar_incidente_por_zona(zona_intervencion)

    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=u_id)
    emitir("incidente_finalizado")
    return zona_intervencion
