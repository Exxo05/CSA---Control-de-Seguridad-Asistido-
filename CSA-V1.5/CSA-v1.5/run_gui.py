import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

print("🔧 Inicializando base de datos...")
from servicios.incidentes import inicializar_incidentes
from servicios.unidades   import inicializar_unidades
from servicios.historicos import listar_historicos_df

inicializar_unidades()
inicializar_incidentes()
listar_historicos_df()  # crea tabla si no existe
print("✅ Base de datos lista.")

# Arrancar servidor HTTP del mapa antes de la interfaz
print("🌐 Iniciando servidor de mapas...")
import servicios.mapa_server as mapa_server
mapa_server.iniciar(BASE_DIR)
print(f"✅ Servidor en {mapa_server.url_mapa()}")

# Generar mapa inicial en segundo plano
import threading
from mapas.mapa_principal import crear_mapa_principal
from mapas.mapa_calor import crear_mapa_calor

def _generar_mapas():
    try:
        crear_mapa_principal().save(os.path.join(BASE_DIR, "mapa.html"))
        crear_mapa_calor().save(os.path.join(BASE_DIR, "mapa_calor.html"))
        print("✅ Mapas iniciales generados.")
    except Exception as e:
        print(f"⚠️  Error generando mapas iniciales: {e}")

threading.Thread(target=_generar_mapas, daemon=True).start()

print("🖥️  Arrancando interfaz...")
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
