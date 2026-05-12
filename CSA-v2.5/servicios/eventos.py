# servicios/eventos.py — Bus de eventos global v2.0
# Thread-safe: los callbacks se ejecutan siempre en el hilo principal de Tkinter
from typing import Callable
import threading

_lock      = threading.Lock()
_listeners: dict[str, list[Callable]] = {}
_tk_root   = None   # referencia a MainWindow para .after()

def registrar_root(root):
    """Llamar desde MainWindow.__init__ para habilitar dispatch seguro."""
    global _tk_root
    _tk_root = root

def suscribir(evento: str, callback: Callable):
    with _lock:
        _listeners.setdefault(evento, [])
        if callback not in _listeners[evento]:
            _listeners[evento].append(callback)

def desuscribir(evento: str, callback: Callable):
    with _lock:
        if evento in _listeners:
            _listeners[evento] = [c for c in _listeners[evento] if c != callback]

def emitir(evento: str, **datos):
    """
    Dispara el evento. Si se llama desde un hilo secundario,
    despacha los callbacks al hilo principal via root.after().
    """
    with _lock:
        cbs = list(_listeners.get(evento, []))

    if not cbs:
        return

    def _dispatch():
        for cb in cbs:
            try:
                cb(**datos)
            except Exception as e:
                print(f"[EventBus] Error en listener de '{evento}': {e}")

    if _tk_root and threading.current_thread() is not threading.main_thread():
        _tk_root.after(0, _dispatch)
    else:
        _dispatch()
