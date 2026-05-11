# servicios/incidentes.py
import sqlite3
from servicios.db import get_connection

def inicializar_incidentes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL,
            zona TEXT NOT NULL,
            direccion TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """)
    conn.commit()
    conn.close()

def clasificar_tipo_incidente(texto):
    t = texto.lower()
    if any(w in t for w in ["pistola","arma","cuchillo","navaja","disparo","atentado","matar"]):
        return "CRÍTICA (ARMAS)"
    if any(w in t for w in ["robo","atraco","pelea","agresion","tienda","tiron","violencia"]):
        return "ALTA (DELITO VIOLENTO)"
    return "MEDIA (ASISTENCIA)"

def listar_incidentes(solo_activos=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT id, tipo, descripcion, fecha, zona, direccion, estado FROM incidentes"
        if solo_activos:
            query += " WHERE estado = 'Activo'"
        query += " ORDER BY id DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except:
        return []
    finally:
        conn.close()

def finalizar_incidente_db(id_incidente):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE incidentes SET estado = 'Finalizado' WHERE id = ?", (id_incidente,))
        conn.commit()
    finally:
        conn.close()
    from servicios.eventos import emitir
    emitir("incidente_finalizado", id=id_incidente)

def finalizar_incidente_por_zona(zona_nombre):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        zona_limpia = zona_nombre.split('(')[0].strip()
        cursor.execute("""
            UPDATE incidentes SET estado = 'Finalizado' 
            WHERE id = (
                SELECT id FROM incidentes 
                WHERE (UPPER(zona) LIKE UPPER(?) OR UPPER(direccion) LIKE UPPER(?))
                AND estado = 'Activo' ORDER BY id ASC LIMIT 1
            )
        """, (f"%{zona_limpia}%", f"%{zona_limpia}%"))
        if cursor.rowcount > 0:
            conn.commit()
            return
        cursor.execute("""
            UPDATE incidentes SET estado = 'Finalizado' 
            WHERE id = (
                SELECT id FROM incidentes WHERE estado = 'Activo' 
                ORDER BY fecha ASC LIMIT 1
            )
        """)
        conn.commit()
    finally:
        conn.close()
    from servicios.eventos import emitir
    emitir("incidente_finalizado")

def modificar_incidente_completo(id_db, tipo, desc, zona, direccion):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE incidentes SET tipo=?, descripcion=?, zona=?, direccion=? WHERE id=?
        """, (tipo, desc, zona, direccion, id_db))
        conn.commit()
    finally:
        conn.close()
    from servicios.eventos import emitir
    emitir("incidente_modificado", id=id_db)

def registrar_incidente_completo(tipo, descripcion, fecha, zona, direccion):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO incidentes (tipo, descripcion, fecha, zona, direccion) VALUES (?,?,?,?,?)",
            (tipo, descripcion, fecha, zona, direccion)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
    finally:
        conn.close()
    from servicios.eventos import emitir
    emitir("incidente_registrado", id=nuevo_id)
    return nuevo_id
