# servicios/alertas_sonido.py — Alertas sonoras para incidentes críticos
import threading, os, sys
from servicios.eventos import suscribir

_activo = True

def _beep_windows(freq=1000, duracion=300):
    try:
        import winsound
        winsound.Beep(freq, duracion)
    except Exception:
        pass

def _beep_unix():
    try:
        os.system("paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null || "
                  "aplay /usr/share/sounds/freedesktop/stereo/bell.wav 2>/dev/null || "
                  "echo -e '\\a'")
    except Exception:
        pass

def _sonar(nivel: str):
    if not _activo:
        return
    def _play():
        if sys.platform == "win32":
            if nivel == "muy alta":
                for _ in range(3):
                    _beep_windows(1500, 200)
                    threading.Event().wait(0.1)
            elif nivel == "alta":
                _beep_windows(1000, 400)
            else:
                _beep_windows(700, 200)
        else:
            _beep_unix()
    threading.Thread(target=_play, daemon=True).start()

def _on_incidente(id=None, **kw):
    """Determina la gravedad del incidente recién registrado y suena."""
    if id is None:
        return
    try:
        from servicios.db import get_connection
        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT tipo FROM incidentes WHERE id=?", (id,))
        row  = c.fetchone()
        conn.close()
        if not row:
            return
        tipo = str(row[0]).upper()
        if any(x in tipo for x in ["CRÍTICA","CRITICA","MUY ALTA","ARMA","DISPARO"]):
            _sonar("muy alta")
        elif "ALTA" in tipo:
            _sonar("alta")
    except Exception:
        pass

def activar():
    global _activo
    _activo = True

def desactivar():
    global _activo
    _activo = False

def inicializar():
    suscribir("incidente_registrado", _on_incidente)
    print("[Alertas] Alertas sonoras activas.")
