# servicios/unidades.py — v2.1
import sqlite3
from servicios.db import get_connection


def _limpiar_zona(texto: str) -> str:
    """Evita que se guarde una descripción larga como zona."""
    if not texto:
        return "Sin zona"
    # Si es demasiado largo o parece una descripción, truncar
    t = str(texto).strip()
    if len(t) > 60:
        t = t[:57] + "…"
    return t


def inicializar_unidades():
    """Compatibilidad con código antiguo — ahora lo hace inicializar_bd()."""
    pass


def listar_unidades(solo_en_servicio=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if solo_en_servicio:
            cursor.execute("SELECT * FROM unidades WHERE en_servicio = 1")
        else:
            cursor.execute("SELECT * FROM unidades")
        return cursor.fetchall()
    finally:
        conn.close()


def alternar_servicio(u_id, valor):
    conn = get_connection()
    try:
        estado = "Patrullando" if valor == 1 else "En Base"
        conn.execute("UPDATE unidades SET en_servicio=?, estado=? WHERE id=?",
                     (valor, estado, u_id))
        conn.commit()
    finally:
        conn.close()
    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=u_id)


def cambiar_estado_operativo(u_id, nuevo_estado):
    conn = get_connection()
    try:
        conn.execute("UPDATE unidades SET estado=? WHERE id=?", (nuevo_estado, u_id))
        conn.commit()
    finally:
        conn.close()
    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=u_id)


def asignar_unidad_a_incidente(unidad_id, zona_destino):
    """Asigna una unidad a un incidente. zona_destino es el nombre de zona, no la descripción."""
    zona_limpia = _limpiar_zona(zona_destino)
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE unidades
            SET estado='En Intervención', ubicacion_actual=?
            WHERE id=?
        """, (zona_limpia, unidad_id))
        conn.commit()
    finally:
        conn.close()
    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=unidad_id)


def finalizar_intervencion(u_id: int, zona_base: str = None):
    """Devuelve la unidad a Patrullando y cierra el incidente de su zona."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ubicacion_actual FROM unidades WHERE id=?", (u_id,))
        row = cursor.fetchone()
        zona_intervencion = row[0] if row else None
        nueva_zona = zona_base or zona_intervencion or "Sin zona"
        conn.execute("""
            UPDATE unidades SET estado='Patrullando', ubicacion_actual=?
            WHERE id=?
        """, (nueva_zona, u_id))
        conn.commit()
    finally:
        conn.close()

    if zona_intervencion:
        from servicios.incidentes import finalizar_incidente_por_zona
        finalizar_incidente_por_zona(zona_intervencion)

    from servicios.eventos import emitir
    emitir("unidad_actualizada", u_id=u_id)
    emitir("incidente_finalizado")
    return zona_intervencion
