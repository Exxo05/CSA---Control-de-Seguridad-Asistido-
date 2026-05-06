# gui/main_window.py — v2.1 con barra de estado global
import tkinter as tk
import datetime
from gui.sidebar import Sidebar
from gui.styles import GRAY_BG, POLICE_BLUE, WHITE, GRAY_BORDER, GRAY_TEXT, FONT_SMALL

from gui.screens.registrar    import RegistrarScreen
from gui.screens.incidentes   import IncidentesScreen
from gui.screens.mapa         import MapaScreen
from gui.screens.mapa_calor   import MapaCalorScreen
from gui.screens.estadisticas import EstadisticasScreen
from gui.screens.recomendacion import RecomendacionScreen
from gui.screens.prevencion   import PrevencionScreen
from gui.screens.unidades     import UnidadesScreen
from servicios.eventos import suscribir

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

MENSAJES_EVENTO = {
    "incidente_registrado":  "🚨 Nuevo incidente registrado",
    "incidente_finalizado":  "✅ Incidente finalizado",
    "incidente_modificado":  "✏️ Incidente modificado",
    "unidad_actualizada":    "🚓 Unidad actualizada",
}


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSA — Control de Seguridad Asistido v2.0")
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.configure(bg=POLICE_BLUE)

        try:
            self.iconbitmap("assets/logo_CSA.ico")
        except Exception:
            pass

        # Layout principal
        self.sidebar = Sidebar(self, self.cambiar_pantalla)
        self.sidebar.pack(side="left", fill="y")

        main_area = tk.Frame(self, bg=GRAY_BG)
        main_area.pack(side="right", expand=True, fill="both")

        self.container = tk.Frame(main_area, bg=GRAY_BG)
        self.container.pack(fill="both", expand=True)

        # Barra de estado inferior
        self._status_bar = tk.Frame(main_area, bg=WHITE,
                                     highlightbackground=GRAY_BORDER,
                                     highlightthickness=1, height=26)
        self._status_bar.pack(fill="x", side="bottom")
        self._status_bar.pack_propagate(False)

        self._lbl_status = tk.Label(
            self._status_bar,
            text="  🛡️  CSA v2.0 — Sistema operativo",
            font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT, anchor="w"
        )
        self._lbl_status.pack(side="left", padx=8)

        self._lbl_hora = tk.Label(
            self._status_bar, text="",
            font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT, anchor="e"
        )
        self._lbl_hora.pack(side="right", padx=8)
        self._actualizar_reloj()

        # Suscribir barra de estado a todos los eventos
        for ev, msg in MENSAJES_EVENTO.items():
            suscribir(ev, lambda m=msg, **kw: self._mostrar_estado(m))

        self.pantalla_actual = None
        self.cambiar_pantalla("registrar")

    def _actualizar_reloj(self):
        hora = datetime.datetime.now().strftime("%A %d/%m/%Y  %H:%M:%S")
        self._lbl_hora.config(text=f"{hora}  ")
        self.after(1000, self._actualizar_reloj)

    def _mostrar_estado(self, mensaje: str):
        self._lbl_status.config(text=f"  {mensaje}  —  "
                                     f"{datetime.datetime.now().strftime('%H:%M:%S')}",
                                fg="#059669")
        self.after(5000, lambda: self._lbl_status.config(
            text="  🛡️  CSA v2.0 — Sistema operativo", fg=GRAY_TEXT))

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
