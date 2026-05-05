# gui/main_window.py — Ventana principal v2.0
import tkinter as tk
from gui.sidebar import Sidebar
from gui.styles import GRAY_BG, POLICE_BLUE

from gui.screens.registrar    import RegistrarScreen
from gui.screens.incidentes   import IncidentesScreen
from gui.screens.mapa         import MapaScreen
from gui.screens.mapa_calor   import MapaCalorScreen
from gui.screens.estadisticas import EstadisticasScreen
from gui.screens.recomendacion import RecomendacionScreen
from gui.screens.prevencion   import PrevencionScreen
from gui.screens.unidades     import UnidadesScreen

PANTALLAS = {
    "registrar":    RegistrarScreen,
    "incidentes":   IncidentesScreen,
    "mapa":         MapaScreen,
    "mapa_calor":   MapaCalorScreen,
    "estadisticas": EstadisticasScreen,
    "recomendacion":RecomendacionScreen,
    "prevencion":   PrevencionScreen,
    "unidades":     UnidadesScreen,
}

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSA — Control de Seguridad Asistido v2.0")
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.configure(bg=POLICE_BLUE)

        # Intentar icono (si existe)
        try:
            self.iconbitmap("assets/logo_CSA.ico")
        except Exception:
            pass

        self.sidebar = Sidebar(self, self.cambiar_pantalla)
        self.sidebar.pack(side="left", fill="y")

        self.container = tk.Frame(self, bg=GRAY_BG)
        self.container.pack(side="right", expand=True, fill="both")

        self.pantalla_actual = None
        self.cambiar_pantalla("registrar")

    def cambiar_pantalla(self, nombre, id_a_resaltar=None):
        if self.pantalla_actual:
            self.pantalla_actual.destroy()

        self.sidebar.marcar_activo(nombre)

        cls = PANTALLAS.get(nombre)
        if cls:
            self.pantalla_actual = cls(self.container)
            self.pantalla_actual.pack(expand=True, fill="both")
            if id_a_resaltar and hasattr(self.pantalla_actual, "resaltar_id"):
                self.pantalla_actual.resaltar_id(id_a_resaltar)
