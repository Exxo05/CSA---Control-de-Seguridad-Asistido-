# servicios/mapa_manager.py — Regenerador global del mapa
"""
Vive durante toda la sesión del programa, independientemente
de qué pantalla esté visible. Se suscribe a los eventos globales
y regenera el HTML del mapa en un hilo secundario cada vez que
hay un cambio. El servidor HTTP sirve el archivo actualizado.
"""
import threading
import os

_regenerando = False
_ruta_base   = None
_lock        = threading.Lock()


def inicializar(ruta_base: str):
    """Llamar una sola vez desde run_gui.py."""
    global _ruta_base
    _ruta_base = ruta_base

    from servicios.eventos import suscribir
    for ev in ("incidente_registrado", "incidente_finalizado",
               "incidente_modificado", "unidad_actualizada"):
        suscribir(ev, _on_evento)

    # Generar mapas iniciales
    _regenerar_todos()


def _on_evento(**kw):
    """Callback del bus de eventos — siempre se ejecuta en hilo principal."""
    # Debounce simple con threading.Timer
    _cancelar_timer()
    t = threading.Timer(0.8, _regenerar_todos)
    t.daemon = True
    t.start()
    _guardar_timer(t)


_timer      = None
_timer_lock = threading.Lock()

def _guardar_timer(t):
    global _timer
    with _timer_lock:
        _timer = t

def _cancelar_timer():
    global _timer
    with _timer_lock:
        if _timer:
            _timer.cancel()
            _timer = None


def _regenerar_todos():
    """Regenera mapa principal y mapa de calor en un hilo."""
    global _regenerando
    with _lock:
        if _regenerando:
            return
        _regenerando = True

    threading.Thread(target=_worker, daemon=True).start()


def _worker():
    global _regenerando
    try:
        if not _ruta_base:
            return

        from mapas.mapa_principal import crear_mapa_principal
        from mapas.mapa_calor     import crear_mapa_calor

        ruta_principal = os.path.join(_ruta_base, "mapa.html")
        ruta_calor     = os.path.join(_ruta_base, "mapa_calor.html")

        try:
            mapa = crear_mapa_principal(solo_activos=False)
            mapa.save(ruta_principal)
        except Exception as e:
            print(f"[MapaManager] Error mapa principal: {e}")

        try:
            calor = crear_mapa_calor()
            calor.save(ruta_calor)
        except Exception as e:
            print(f"[MapaManager] Error mapa calor: {e}")

        print(f"[MapaManager] Mapas regenerados")
    finally:
        _regenerando = False
