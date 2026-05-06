# servicios/eventos.py — Bus de eventos global para CSA
# Permite que cualquier módulo notifique cambios y otros reaccionen
from typing import Callable

_listeners: dict[str, list[Callable]] = {}

def suscribir(evento: str, callback: Callable):
    """Registra una función que se llamará cuando ocurra el evento."""
    _listeners.setdefault(evento, [])
    if callback not in _listeners[evento]:
        _listeners[evento].append(callback)

def desuscribir(evento: str, callback: Callable):
    """Elimina un listener."""
    if evento in _listeners:
        _listeners[evento] = [c for c in _listeners[evento] if c != callback]

def emitir(evento: str, **datos):
    """Dispara el evento y llama a todos los listeners registrados."""
    for cb in _listeners.get(evento, []):
        try:
            cb(**datos)
        except Exception as e:
            print(f"[EventBus] Error en listener de '{evento}': {e}")

# Eventos estándar del sistema:
#   "incidente_registrado"  → cuando se crea uno nuevo
#   "incidente_finalizado"  → cuando se cierra uno
#   "incidente_modificado"  → cuando se edita
#   "unidad_actualizada"    → cuando cambia estado/ubicación de una unidad
