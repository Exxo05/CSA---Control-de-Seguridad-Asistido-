import tkinter as tk
from gui.styles import POLICE_BLUE, WHITE, FONT_MENU

class Sidebar(tk.Frame):
    def __init__(self, parent, callback):
        super().__init__(parent, bg=POLICE_BLUE, width=220)
        self.callback = callback
        self.pack_propagate(False)

        titulo = tk.Label(
            self,
            text="CSA\nControl de Seguridad\nAsistido",
            bg=POLICE_BLUE,
            fg=WHITE,
            font=("Arial", 14, "bold"),
            justify="center"
        )
        titulo.pack(pady=20)

        # Añadida la clave "prevencion" a la lista de botones
        botones = [
            ("Registrar incidente", "registrar"),
            ("Incidentes", "incidentes"),
            ("Mapa", "mapa"),
            ("Mapa de calor", "mapa_calor"),
            ("Estadísticas", "estadisticas"),
            ("Prevención (IA)", "prevencion"), # <--- Nueva función predictiva
            ("Recomendación", "recomendacion"),
            ("Gestión Unidades", "unidades")
        ]

        for texto, clave in botones:
            btn = tk.Button(
                self,
                text=texto,
                font=FONT_MENU,
                bg=WHITE,
                fg=POLICE_BLUE,
                relief="flat",
                command=lambda c=clave: self.callback(c)
            )
            btn.pack(fill="x", padx=15, pady=6)