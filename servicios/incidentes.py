import sqlite3
from servicios.db import get_connection

def inicializar_incidentes():
    """Crea la tabla con la columna estado si no existe"""
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
    """Detecta la gravedad del asunto"""
    t = texto.lower()
    if any(w in t for w in ["pistola", "arma", "cuchillo", "navaja", "disparo", "atentado", "matar"]):
        return "CRÍTICA (ARMAS)"
    if any(w in t for w in ["robo", "atraco", "pelea", "agresion", "tienda", "tiron", "violencia"]):
        return "ALTA (DELITO VIOLENTO)"
    return "MEDIA (ASISTENCIA)"

def listar_incidentes(solo_activos=False):
    """Retorna los incidentes registrados"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT id, tipo, descripcion, fecha, zona, direccion, estado FROM incidentes"
        if solo_activos:
            query += " WHERE estado = 'Activo'"
        cursor.execute(query)
        return cursor.fetchall()
    except:
        return []
    finally:
        conn.close()

def finalizar_incidente_db(id_incidente):
    """Finaliza por ID (usado en pantalla Incidentes)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE incidentes SET estado = 'Finalizado' WHERE id = ?", (id_incidente,))
        conn.commit()
    finally:
        conn.close()

def finalizar_incidente_por_zona(zona_nombre):
    """Busca el incidente en la zona de la patrulla, y si no, cierra el más antiguo activo"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # INTENTO 1: Buscar por zona de la patrulla
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
            print(f"✅ ÉXITO: Incidente en zona {zona_limpia} finalizado.")
            return

        # INTENTO 2: Si no hay en esa zona, cerramos el incidente más antiguo que esté abierto
        # (Ideal para cuando una patrulla de Reyes Católicos va al Centro)
        cursor.execute("""
            UPDATE incidentes SET estado = 'Finalizado' 
            WHERE id = (
                SELECT id FROM incidentes WHERE estado = 'Activo' 
                ORDER BY fecha ASC LIMIT 1
            )
        """)
        
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ ÉXITO: Se ha finalizado el incidente más antiguo del sistema.")
        else:
            print("❌ ERROR: No hay NINGÚN incidente activo en todo el sistema.")
            
    finally:
        conn.close()

def modificar_incidente_completo(id_db, tipo, desc, zona, direccion):
    """Edición total de los datos"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE incidentes 
            SET tipo=?, descripcion=?, zona=?, direccion=? 
            WHERE id=?
        """, (tipo, desc, zona, direccion, id_db))
        conn.commit()
    finally:
        conn.close()