import sys
import os

# Añadir el directorio raíz del proyecto al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from gui.main_window import MainWindow
# Importamos las funciones de inicialización
from servicios.unidades import inicializar_unidades
from servicios.incidentes import inicializar_incidentes

if __name__ == "__main__":
    # --- PASO CRUCIAL: Preparar la base de datos ---
    print("Iniciando servicios...")
    inicializar_unidades()    # Crea la tabla de patrullas con 'ubicacion_actual'
    inicializar_incidentes()  # Crea la tabla de incidentes con la columna 'zona'
    print("Servicios listos.")
    
    app = MainWindow()
    app.mainloop()