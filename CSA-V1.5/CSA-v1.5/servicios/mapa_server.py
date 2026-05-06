# servicios/mapa_server.py — Servidor HTTP interno para mapa en tiempo real
"""
Lanza un servidor HTTP local en un hilo secundario.
El mapa Folium se sirve desde localhost:8765/mapa.html
La página se auto-recarga cada 4 segundos (via meta refresh),
de modo que el operador sólo necesita tener la pestaña abierta.
También sirve /mapa_calor.html con el mapa de calor.
"""
import threading
import http.server
import os
import socketserver

_PORT      = 8765
_servidor  = None
_hilo      = None
_ruta_base = None   # directorio donde se guardan los HTML

class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar log de peticiones

    def do_GET(self):
        # Inyectar auto-refresh en los HTML del mapa
        if self.path in ("/", "/mapa.html", "/mapa_calor.html"):
            nombre = "mapa.html" if self.path != "/mapa_calor.html" else "mapa_calor.html"
            ruta = os.path.join(_ruta_base, nombre)
            if os.path.exists(ruta):
                with open(ruta, "rb") as f:
                    html = f.read()
                # Inyectar meta refresh cada 4s y banner de estado
                refresh = b'<meta http-equiv="refresh" content="4">'
                banner  = (
                    b'<div style="position:fixed;top:0;left:0;right:0;z-index:99999;'
                    b'background:#0A1F44;color:white;padding:5px 12px;font-family:Segoe UI,sans-serif;'
                    b'font-size:12px;display:flex;justify-content:space-between;align-items:center">'
                    b'<span>&#128737;&#65039; CSA &mdash; Mapa Operativo en Tiempo Real</span>'
                    b'<span style="color:#94A3B8">Auto-refresco cada 4s</span></div>'
                    b'<div style="height:26px"></div>'
                )
                html = html.replace(b"<head>", b"<head>" + refresh, 1)
                html = html.replace(b"<body>", b"<body>" + banner, 1)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return
        super().do_GET()

    def translate_path(self, path):
        # Servir desde _ruta_base en vez del cwd
        p = super().translate_path(path)
        rel = os.path.relpath(p, os.getcwd())
        return os.path.join(_ruta_base, rel)


def iniciar(ruta_mapas: str, puerto: int = _PORT):
    """Inicia el servidor en un hilo daemon. Idempotente (no arranca dos veces)."""
    global _servidor, _hilo, _ruta_base, _PORT
    if _hilo and _hilo.is_alive():
        return  # Ya corriendo

    _PORT      = puerto
    _ruta_base = ruta_mapas

    try:
        socketserver.TCPServer.allow_reuse_address = True
        _servidor = socketserver.TCPServer(("127.0.0.1", puerto), _Handler)
        _hilo = threading.Thread(target=_servidor.serve_forever, daemon=True)
        _hilo.start()
        print(f"[MapaServer] Servidor HTTP iniciado en http://localhost:{puerto}/mapa.html")
    except OSError as e:
        print(f"[MapaServer] No se pudo iniciar ({e}) — usando modo fallback")


def detener():
    global _servidor
    if _servidor:
        _servidor.shutdown()
        _servidor = None


def url_mapa() -> str:
    return f"http://localhost:{_PORT}/mapa.html"

def url_calor() -> str:
    return f"http://localhost:{_PORT}/mapa_calor.html"

def puerto() -> int:
    return _PORT
