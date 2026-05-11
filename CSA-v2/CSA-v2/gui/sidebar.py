# gui/sidebar.py — Sidebar v3.0
import tkinter as tk
from gui.styles import (POLICE_BLUE, POLICE_BLUE_LIGHT, WHITE,
                         FONT_MENU, FONT_SMALL, SIDEBAR_WIDTH)

MENU_SECTIONS = [
    ("OPERACIONES", [
        ("🏠 Dashboard",          "dashboard"),
        ("🚨 Registrar incidente","registrar"),
        ("📋 Incidentes",         "incidentes"),
        ("🔍 Búsqueda global",    "busqueda"),
    ]),
    ("MAPAS", [
        ("🗺️  Mapa operativo",    "mapa"),
        ("🔥 Mapa de calor",      "mapa_calor"),
        ("📡 Patrullas GPS",      "patrullas_mapa"),
    ]),
    ("ANÁLISIS", [
        ("📊 Estadísticas",       "estadisticas"),
        ("🤖 Prevención IA",      "prevencion"),
        ("🧠 Recomendación",      "recomendacion"),
    ]),
    ("RECURSOS", [
        ("🚓 Gestión unidades",   "unidades"),
        ("👤 Personas",           "personas"),
        ("🚗 Vehículos",          "vehiculos"),
    ]),
    ("SISTEMA", [
        ("📄 Exportar/Informes",  "exportar"),
        ("📋 Auditoría",          "auditoria"),
        ("⚙️  Configuración",     "configuracion"),
    ]),
]


class Sidebar(tk.Frame):
    def __init__(self, parent, callback):
        super().__init__(parent, bg=POLICE_BLUE, width=SIDEBAR_WIDTH)
        self.callback = callback
        self.pack_propagate(False)
        self._botones = {}
        self._pantalla_activa = None
        self._build()

    def _build(self):
        # Logo
        logo = tk.Frame(self, bg=POLICE_BLUE)
        logo.pack(fill="x", pady=(16, 8))
        tk.Label(logo, text="🛡️", font=("Segoe UI",26),
                 bg=POLICE_BLUE, fg=WHITE).pack()
        tk.Label(logo, text="CSA", font=("Segoe UI",15,"bold"),
                 bg=POLICE_BLUE, fg=WHITE).pack()
        tk.Label(logo, text="Policía Local · Alcalá de Henares",
                 font=("Segoe UI",7), bg=POLICE_BLUE, fg="#64748B",
                 wraplength=200, justify="center").pack()

        tk.Frame(self, bg="#1E3A5F", height=1).pack(fill="x", padx=12, pady=(8,4))

        # Canvas con scroll para el menú
        canvas = tk.Canvas(self, bg=POLICE_BLUE, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        nav = tk.Frame(canvas, bg=POLICE_BLUE)
        canvas.create_window((0,0), window=nav, anchor="nw")
        nav.bind("<Configure>",
                 lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for seccion, items in MENU_SECTIONS:
            # Etiqueta de sección
            tk.Label(nav, text=seccion, font=("Segoe UI",7,"bold"),
                     bg=POLICE_BLUE, fg="#475569",
                     padx=16).pack(anchor="w", pady=(8,2))
            for texto, clave in items:
                btn = self._make_btn(nav, texto, clave)
                btn.pack(fill="x", padx=8, pady=1)
                self._botones[clave] = btn

        # Pie — usuario activo
        tk.Frame(self, bg="#1E3A5F", height=1).pack(
            fill="x", padx=12, pady=(4,4), side="bottom")
        tk.Label(self, text="CSA v2.0 — 2025", font=("Segoe UI",7),
                 bg=POLICE_BLUE, fg="#475569").pack(side="bottom", pady=(0,4))
        try:
            from servicios.sesion import nombre as _n, rol as _r
            _nombre_txt = _n() or "—"
            _rol_txt    = _r().capitalize() if _r() else ""
            tk.Label(self, text=_rol_txt, font=("Segoe UI",7),
                     bg=POLICE_BLUE, fg="#64748B").pack(side="bottom")
            tk.Label(self, text=f"👮 {_nombre_txt}", font=("Segoe UI",8,"bold"),
                     bg=POLICE_BLUE, fg="#CBD5E1").pack(side="bottom", pady=(4,0))
        except Exception:
            pass

    def _make_btn(self, parent, texto, clave):
        btn = tk.Button(
            parent, text=texto, font=FONT_MENU,
            bg=POLICE_BLUE, fg="#CBD5E1",
            activebackground=POLICE_BLUE_LIGHT, activeforeground=WHITE,
            relief="flat", anchor="w", padx=12, pady=6,
            cursor="hand2",
            command=lambda c=clave: self._on_click(c)
        )
        btn.bind("<Enter>", lambda e, b=btn, c=clave: self._hover(b, c, True))
        btn.bind("<Leave>", lambda e, b=btn, c=clave: self._hover(b, c, False))
        return btn

    def _hover(self, btn, clave, entering):
        if clave == self._pantalla_activa: return
        btn.config(bg=POLICE_BLUE_LIGHT if entering else POLICE_BLUE,
                   fg=WHITE if entering else "#CBD5E1")

    def _on_click(self, clave):
        self.marcar_activo(clave)
        self.callback(clave)

    def marcar_activo(self, clave):
        if self._pantalla_activa and self._pantalla_activa in self._botones:
            self._botones[self._pantalla_activa].config(
                bg=POLICE_BLUE, fg="#CBD5E1")
        self._pantalla_activa = clave
        if clave in self._botones:
            self._botones[clave].config(bg=POLICE_BLUE_LIGHT, fg=WHITE)
