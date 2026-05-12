# servicios/sesion.py — Sesión del usuario activo
from datetime import datetime

_usuario_activo: dict | None = None
_sesion_id: int | None = None

def iniciar_sesion(usuario_dict: dict, turno: str = ""):
    global _usuario_activo, _sesion_id
    _usuario_activo = usuario_dict
    from servicios.db import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO sesiones (usuario_id, inicio, turno) VALUES (?,?,?)",
        (usuario_dict["id"], datetime.now().isoformat(), turno)
    )
    conn.commit()
    _sesion_id = c.lastrowid
    conn.close()

def cerrar_sesion():
    global _usuario_activo, _sesion_id
    if _sesion_id:
        from servicios.db import get_connection
        conn = get_connection()
        conn.execute("UPDATE sesiones SET fin=? WHERE id=?",
                     (datetime.now().isoformat(), _sesion_id))
        conn.commit()
        conn.close()
    _usuario_activo = None
    _sesion_id = None

def usuario_activo() -> dict | None:
    return _usuario_activo

def uid() -> int | None:
    return _usuario_activo["id"] if _usuario_activo else None

def nombre() -> str:
    return _usuario_activo["nombre"] if _usuario_activo else "—"

def rol() -> str:
    return _usuario_activo["rol"] if _usuario_activo else ""

def es_admin() -> bool:
    return rol() == "admin"

def es_supervisor() -> bool:
    return rol() in ("admin", "supervisor")
