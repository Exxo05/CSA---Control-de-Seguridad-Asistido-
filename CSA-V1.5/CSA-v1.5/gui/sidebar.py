# gui/sidebar.py — Sidebar v2.0 con indicador de pantalla activa
import tkinter as tk
from gui.styles import POLICE_BLUE, POLICE_BLUE_LIGHT, WHITE, GRAY_TEXT, FONT_MENU, FONT_SMALL, SIDEBAR_WIDTH

MENU_ITEMS = [
    ("🚨 Registrar incidente", "registrar"),
    ("📋 Incidentes",          "incidentes"),
    ("🗺️  Mapa operativo",     "mapa"),
    ("🔥 Mapa de calor",       "mapa_calor"),
    ("📊 Estadísticas",        "estadisticas"),
    ("🤖 Prevención (IA)",     "prevencion"),
    ("🧠 Recomendación",       "recomendacion"),
    ("🚓 Gestión Unidades",    "unidades"),
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
        # Logo / título
        logo_frame = tk.Frame(self, bg=POLICE_BLUE)
        logo_frame.pack(fill="x", pady=(20, 8))

        tk.Label(logo_frame, text="🛡️", font=("Segoe UI", 28),
                 bg=POLICE_BLUE, fg=WHITE).pack()
        tk.Label(logo_frame, text="CSA", font=("Segoe UI", 16, "bold"),
                 bg=POLICE_BLUE, fg=WHITE).pack()
        tk.Label(logo_frame, text="Control de Seguridad\nAsistido",
                 font=("Segoe UI", 8), bg=POLICE_BLUE,
                 fg="#94A3B8", justify="center").pack()

        # Separador
        sep = tk.Frame(self, bg="#1E3A5F", height=1)
        sep.pack(fill="x", padx=16, pady=(8, 12))

        # Botones de navegación
        nav_frame = tk.Frame(self, bg=POLICE_BLUE)
        nav_frame.pack(fill="x", padx=10)

        for texto, clave in MENU_ITEMS:
            btn = self._make_nav_btn(nav_frame, texto, clave)
            btn.pack(fill="x", pady=2)
            self._botones[clave] = btn

        # Pie del sidebar
        sep2 = tk.Frame(self, bg="#1E3A5F", height=1)
        sep2.pack(fill="x", padx=16, pady=(16, 8), side="bottom")
        tk.Label(self, text="CSA v2.0 — 2025",
                 font=("Segoe UI", 8), bg=POLICE_BLUE,
                 fg="#475569", justify="center").pack(side="bottom", pady=8)

    def _make_nav_btn(self, parent, texto, clave):
        btn = tk.Button(
            parent, text=texto,
            font=FONT_MENU,
            bg=POLICE_BLUE, fg="#CBD5E1",
            activebackground=POLICE_BLUE_LIGHT,
            activeforeground=WHITE,
            relief="flat", anchor="w",
            padx=14, pady=8,
            cursor="hand2",
            command=lambda c=clave: self._on_click(c)
        )
        btn.bind("<Enter>", lambda e, b=btn, c=clave: self._on_hover(b, c, True))
        btn.bind("<Leave>", lambda e, b=btn, c=clave: self._on_hover(b, c, False))
        return btn

    def _on_hover(self, btn, clave, entering):
        if clave == self._pantalla_activa:
            return
        btn.config(bg=POLICE_BLUE_LIGHT if entering else POLICE_BLUE,
                   fg=WHITE if entering else "#CBD5E1")

    def _on_click(self, clave):
        self.marcar_activo(clave)
        self.callback(clave)

    def marcar_activo(self, clave):
        # Resetear anterior
        if self._pantalla_activa and self._pantalla_activa in self._botones:
            self._botones[self._pantalla_activa].config(
                bg=POLICE_BLUE, fg="#CBD5E1")
        # Marcar nuevo
        self._pantalla_activa = clave
        if clave in self._botones:
            self._botones[clave].config(
                bg=POLICE_BLUE_LIGHT, fg=WHITE)
