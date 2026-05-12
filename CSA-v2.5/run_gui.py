import sys, os, threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── 1. Base de datos ─────────────────────────────────────────────
print("🔧 Inicializando base de datos...")
from servicios.db import inicializar_bd, hacer_backup
inicializar_bd()

# Compatibilidad: si ya existe BD antigua sin unidades, rellenarlas
try:
    from servicios.db import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM unidades")
    if c.fetchone()[0] == 0:
        patrullas = [
            ("Z-10","Disponible",0,"Casco Histórico / Centro"),
            ("Z-20","Disponible",0,"Reyes Católicos"),
            ("Z-30","Disponible",0,"Chorrillo / Ensanche"),
            ("Z-40","Disponible",0,"La Garena"),
            ("K-5", "Disponible",0,"Espartales"),
            ("A-1", "Disponible",0,"El Val"),
        ]
        c.executemany(
            "INSERT INTO unidades (indicativo,estado,en_servicio,ubicacion_actual)"
            " VALUES (?,?,?,?)", patrullas)
        conn.commit()
        print("✅ Patrullas por defecto creadas.")
    conn.close()
except Exception as e:
    print(f"⚠️  Error comprobando unidades: {e}")

print("✅ Base de datos lista.")

# ── 2. Backup automático al arrancar ─────────────────────────────
def _backup():
    ruta = hacer_backup()
    if ruta:
        print(f"✅ Backup creado: {os.path.basename(ruta)}")
    else:
        print("⚠️  No se pudo crear backup (BD no existe aún).")
threading.Thread(target=_backup, daemon=True).start()

# ── 3. Servidor de mapas ──────────────────────────────────────────
print("🌐 Iniciando servidor de mapas...")
import servicios.mapa_server as mapa_server
mapa_server.iniciar(BASE_DIR)
print(f"✅ {mapa_server.url_mapa()}")

# ── 4. Gestor global de mapas ─────────────────────────────────────
print("🗺️  Iniciando gestor de mapas...")
import servicios.mapa_manager as mapa_manager
mapa_manager.inicializar(BASE_DIR)
print("✅ Gestor de mapas activo.")

# ── 5. Alertas sonoras ────────────────────────────────────────────
from gui.screens.alertas_sonido import inicializar as init_alertas
init_alertas()

# ── 6. Login ──────────────────────────────────────────────────────
print("🔐 Mostrando pantalla de login...")
from gui.login import LoginWindow
login = LoginWindow()
login.mainloop()

if not login.autenticado():
    print("Login cancelado. Cerrando.")
    sys.exit(0)

# ── 7. Interfaz principal ─────────────────────────────────────────
print("🖥️  Arrancando interfaz principal...")
from gui.main_window import MainWindow
app = MainWindow()
app.mainloop()

# ── 8. Cerrar sesión ──────────────────────────────────────────────
from servicios.sesion import cerrar_sesion
cerrar_sesion()
print("👋 Sesión cerrada.")
