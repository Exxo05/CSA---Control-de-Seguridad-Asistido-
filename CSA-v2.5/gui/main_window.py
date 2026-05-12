# gui/main_window.py — v3.0
import tkinter as tk
import datetime

from gui.sidebar  import Sidebar
from gui.styles   import GRAY_BG, POLICE_BLUE, WHITE, GRAY_BORDER, GRAY_TEXT, FONT_SMALL
from servicios.eventos import suscribir, registrar_root
from servicios.sesion  import nombre as sesion_nombre, rol as sesion_rol, cerrar_sesion

from gui.screens.dashboard      import DashboardScreen
from gui.screens.registrar      import RegistrarScreen
from gui.screens.incidentes     import IncidentesScreen
from gui.screens.busqueda       import BusquedaScreen
from gui.screens.mapa           import MapaScreen
from gui.screens.mapa_calor     import MapaCalorScreen
from gui.screens.patrullas_mapa import PatrullasMapaScreen
from gui.screens.estadisticas   import EstadisticasScreen
from gui.screens.prevencion     import PrevencionScreen
from gui.screens.recomendacion  import RecomendacionScreen
from gui.screens.unidades       import UnidadesScreen
from gui.screens.personas       import PersonasScreen
from gui.screens.vehiculos      import VehiculosScreen
from gui.screens.exportar       import ExportarScreen
from gui.screens.auditoria      import AuditoriaScreen
from gui.screens.configuracion  import ConfiguracionScreen

PANTALLAS = {
    "dashboard":     DashboardScreen,
    "registrar":     RegistrarScreen,
    "incidentes":    IncidentesScreen,
    "busqueda":      BusquedaScreen,
    "mapa":          MapaScreen,
    "mapa_calor":    MapaCalorScreen,
    "patrullas_mapa":PatrullasMapaScreen,
    "estadisticas":  EstadisticasScreen,
    "prevencion":    PrevencionScreen,
    "recomendacion": RecomendacionScreen,
    "unidades":      UnidadesScreen,
    "personas":      PersonasScreen,
    "vehiculos":     VehiculosScreen,
    "exportar":      ExportarScreen,
    "auditoria":     AuditoriaScreen,
    "configuracion":  ConfiguracionScreen,
    "dashboard":      DashboardScreen,
    "personas":       PersonasScreen,
    "vehiculos":      VehiculosScreen,
    "busqueda":       BusquedaScreen,
    "patrullas_mapa": PatrullasMapaScreen,
}

MENSAJES_EVENTO = {
    "incidente_registrado": "🚨 Nuevo incidente registrado",
    "incidente_finalizado": "✅ Incidente finalizado",
    "incidente_modificado": "✏️  Incidente modificado",
    "unidad_actualizada":   "🚓 Unidad actualizada",
}


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSA — Control de Seguridad Asistido v2.0")
        self.geometry("1366x860")
        self.minsize(1200, 720)
        self.configure(bg=POLICE_BLUE)

        registrar_root(self)

        try:
            self.iconbitmap("assets/logo_CSA.ico")
        except Exception:
            pass

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Layout
        self.sidebar = Sidebar(self, self.cambiar_pantalla)
        self.sidebar.pack(side="left", fill="y")

        main_area = tk.Frame(self, bg=GRAY_BG)
        main_area.pack(side="right", expand=True, fill="both")

        self.container = tk.Frame(main_area, bg=GRAY_BG)
        self.container.pack(fill="both", expand=True)

        # Barra de estado
        status = tk.Frame(main_area, bg=WHITE,
                          highlightbackground=GRAY_BORDER,
                          highlightthickness=1, height=28)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)

        # Info usuario
        self._lbl_usuario = tk.Label(
            status,
            text=f"  👮 {sesion_nombre()}  |  {sesion_rol().upper()}",
            font=FONT_SMALL, bg=WHITE, fg="#1976D2", anchor="w"
        )
        self._lbl_usuario.pack(side="left", padx=4)

        tk.Frame(status, bg=GRAY_BORDER, width=1).pack(side="left", fill="y", pady=4)

        self._lbl_status = tk.Label(
            status, text="  🛡️  CSA v2.0 — Sistema operativo",
            font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT, anchor="w"
        )
        self._lbl_status.pack(side="left", padx=8)

        self._lbl_hora = tk.Label(status, text="", font=FONT_SMALL,
                                   bg=WHITE, fg=GRAY_TEXT, anchor="e")
        self._lbl_hora.pack(side="right", padx=8)

        # Botón cerrar sesión
        tk.Button(status, text="🚪 Cerrar sesión",
                  font=FONT_SMALL, bg=WHITE, fg="#DC2626",
                  relief="flat", cursor="hand2",
                  command=self._cerrar_sesion).pack(side="right", padx=8)

        self._tick()

        for ev, msg in MENSAJES_EVENTO.items():
            suscribir(ev, lambda m=msg, **kw: self._set_status(m))

        self.pantalla_actual = None
        self.cambiar_pantalla("dashboard")

    def _tick(self):
        h = datetime.datetime.now().strftime("%A %d/%m/%Y  %H:%M:%S").capitalize()
        self._lbl_hora.config(text=f"{h}  ")
        self.after(1000, self._tick)

    def _set_status(self, msg):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self._lbl_status.config(text=f"  {msg}  —  {hora}", fg="#059669")
        self.after(6000, lambda: self._lbl_status.config(
            text="  🛡️  CSA v2.0 — Sistema operativo", fg=GRAY_TEXT))

    def _on_close(self):
        from tkinter import messagebox
        if messagebox.askyesno("Cerrar CSA","¿Cerrar el sistema CSA?"):
            cerrar_sesion()
            self.destroy()

    def _cerrar_sesion(self):
        from tkinter import messagebox
        if messagebox.askyesno("Cerrar sesión","¿Cerrar sesión y volver al login?"):
            cerrar_sesion()
            self.destroy()
            # Relanzar login
            from gui.login import LoginWindow
            login = LoginWindow()
            login.mainloop()
            if login.autenticado():
                nueva = MainWindow()
                nueva.mainloop()

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
