# gui/main_window.py
import tkinter as tk
from gui.sidebar import Sidebar
from gui.styles import WHITE
from gui.screens.mapa_calor import MapaCalorScreen


# Screens
from gui.screens.registrar import RegistrarScreen
from gui.screens.incidentes import IncidentesScreen
from gui.screens.mapa import MapaScreen
from gui.screens.mapa_calor import MapaCalorScreen
from gui.screens.estadisticas import EstadisticasScreen
from gui.screens.recomendacion import RecomendacionScreen
from gui.screens.prevencion import PrevencionScreen
from gui.screens.unidades import UnidadesScreen


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CSA - Control de Seguridad Asistido")
        self.geometry("1200x800")
        self.minsize(1100, 700)

        # Layout principal
        self.sidebar = Sidebar(self, self.cambiar_pantalla)
        self.sidebar.pack(side="left", fill="y")

        self.container = tk.Frame(self, bg=WHITE)
        self.container.pack(side="right", expand=True, fill="both")

        self.pantalla_actual = None
        self.cambiar_pantalla("registrar")

    def cambiar_pantalla(self, nombre, id_a_resaltar=None):
        if self.pantalla_actual:
            self.pantalla_actual.destroy()

        pantallas = {
            "registrar": RegistrarScreen,
            "incidentes": IncidentesScreen,
            "mapa": MapaScreen,
            "mapa_calor": MapaCalorScreen,
            "estadisticas": EstadisticasScreen,
            "recomendacion": RecomendacionScreen,
            "prevencion": PrevencionScreen ,
            "unidades": UnidadesScreen
        }

        pantalla_clase = pantallas.get(nombre)
        if pantalla_clase:
            # Si la pantalla acepta un ID (como Incidentes o Recomendación), se lo pasamos
            self.pantalla_actual = pantalla_clase(self.container)
            self.pantalla_actual.pack(expand=True, fill="both")
            
            # Si enviamos un ID para resaltar, ejecutamos la búsqueda
            if id_a_resaltar and hasattr(self.pantalla_actual, "resaltar_id"):
                self.pantalla_actual.resaltar_id(id_a_resaltar)

