# servicios/mapa_server.py — v2.0 con polling inteligente (sin romper popups)
"""
Servidor HTTP local en localhost:8765.

Estrategia de actualización sin romper popups:
- NO usa meta refresh (que recarga la página entera y cierra popups)
- Sirve un endpoint /version que devuelve el timestamp del archivo
- El JS del mapa consulta /version cada 5s y solo recarga si cambió
- Si hay un popup abierto en Leaflet, NO recarga hasta que se cierre
"""
import threading, http.server, os, socketserver, json, time

_PORT      = 8765
_servidor  = None
_hilo      = None
_ruta_base = None

# JS que se inyecta en el HTML del mapa
_JS_SMART_RELOAD = """
<script>
(function() {
  var _lastVer = null;
  var _checkInterval = 5000; // ms entre comprobaciones

  function _tienePopupAbierto() {
    // Comprueba si hay algún popup de Leaflet abierto
    var popups = document.querySelectorAll('.leaflet-popup');
    return popups.length > 0;
  }

  function _comprobarVersion() {
    fetch('/version?mapa=' + encodeURIComponent(window.location.pathname))
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (_lastVer === null) {
          _lastVer = data.version;
          return;
        }
        if (data.version !== _lastVer) {
          if (_tienePopupAbierto()) {
            // Hay popup abierto: marcar que hay actualización pendiente
            _pendingUpdate = true;
            _mostrarBanner('⚡ Hay actualizaciones — cierra el popup para aplicar');
          } else {
            _lastVer = data.version;
            window.location.reload();
          }
        }
      })
      .catch(function() {});
  }

  var _pendingUpdate = false;

  function _mostrarBanner(msg) {
    var b = document.getElementById('_csa_banner_update');
    if (!b) return;
    b.textContent = msg;
    b.style.background = '#D97706';
  }

  // Cuando se cierra un popup, aplicar actualización pendiente
  document.addEventListener('click', function(e) {
    setTimeout(function() {
      if (_pendingUpdate && !_tienePopupAbierto()) {
        _pendingUpdate = false;
        window.location.reload();
      }
    }, 300);
  });

  setInterval(_comprobarVersion, _checkInterval);
  setTimeout(_comprobarVersion, 1000); // primera comprobación a 1s
})();
</script>
"""

_BANNER_HTML = """
<div id="_csa_banner" style="position:fixed;top:0;left:0;right:0;z-index:99999;
  background:#0A1F44;color:white;padding:5px 14px;font-family:Segoe UI,sans-serif;
  font-size:12px;display:flex;justify-content:space-between;align-items:center">
  <span>&#128737;&#65039; CSA &mdash; Mapa Operativo en Tiempo Real</span>
  <span id="_csa_banner_update" style="color:#94A3B8">Actualización automática activa</span>
</div>
<div style="height:28px"></div>
"""


class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        # Endpoint de versión
        if self.path.startswith('/version'):
            nombre = 'mapa_calor.html' if 'calor' in self.path else 'mapa.html'
            ruta = os.path.join(_ruta_base, nombre)
            try:
                ts = str(int(os.path.getmtime(ruta) * 1000))
            except Exception:
                ts = "0"
            body = json.dumps({"version": ts}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
            return

        # Servir HTML con JS inteligente inyectado
        if self.path.split('?')[0] in ('/', '/mapa.html', '/mapa_calor.html'):
            nombre = ('mapa_calor.html'
                      if 'calor' in self.path else 'mapa.html')
            ruta = os.path.join(_ruta_base, nombre)
            if os.path.exists(ruta):
                with open(ruta, 'rb') as f:
                    html = f.read()

                banner = _BANNER_HTML.encode('utf-8')
                js     = _JS_SMART_RELOAD.encode('utf-8')

                # Inyectar banner justo después de <body>
                html = html.replace(b'<body>', b'<body>' + banner, 1)
                # Inyectar JS justo antes de </body>
                html = html.replace(b'</body>', js + b'</body>', 1)

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(html)
                return

        super().do_GET()

    def translate_path(self, path):
        p   = super().translate_path(path.split('?')[0])
        rel = os.path.relpath(p, os.getcwd())
        return os.path.join(_ruta_base, rel)


def iniciar(ruta_mapas: str, puerto: int = _PORT):
    global _servidor, _hilo, _ruta_base, _PORT
    if _hilo and _hilo.is_alive():
        return
    _PORT      = puerto
    _ruta_base = ruta_mapas
    try:
        socketserver.TCPServer.allow_reuse_address = True
        _servidor = socketserver.TCPServer(("127.0.0.1", puerto), _Handler)
        _hilo = threading.Thread(target=_servidor.serve_forever, daemon=True)
        _hilo.start()
        print(f"[MapaServer] http://localhost:{puerto}/mapa.html")
    except OSError as e:
        print(f"[MapaServer] Puerto ocupado ({e}) — intentando {puerto+1}")
        try:
            _PORT += 1
            _servidor = socketserver.TCPServer(("127.0.0.1", _PORT), _Handler)
            _hilo = threading.Thread(target=_servidor.serve_forever, daemon=True)
            _hilo.start()
            print(f"[MapaServer] http://localhost:{_PORT}/mapa.html")
        except Exception as e2:
            print(f"[MapaServer] No se pudo iniciar: {e2}")


def url_mapa()  -> str: return f"http://localhost:{_PORT}/mapa.html"
def url_calor() -> str: return f"http://localhost:{_PORT}/mapa_calor.html"
def puerto()    -> int:  return _PORT
