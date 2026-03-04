import tkinter as tk
from tkinter import ttk
from gui.styles import FONT_TITLE, POLICE_BLUE, WHITE
from servicios.prevencion import obtener_analisis_predictivo

class PrevencionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.analisis = obtener_analisis_predictivo()
        self.init_ui()

    def init_ui(self):
        # Header con altura extra
        header = tk.Frame(self, bg=POLICE_BLUE)
        header.pack(fill="x")
        tk.Label(header, text="🛡️ UNIDAD DE INTELIGENCIA PREVENTIVA - ALCALÁ", 
                 font=("Arial", 20, "bold"), fg=WHITE, bg=POLICE_BLUE, pady=25).pack()

        if not self.analisis:
            tk.Label(self, text="No hay suficientes datos históricos para generar el análisis predictivo.").pack(pady=100)
            return

        # Contenedor Principal con márgenes anchos
        main_container = tk.Frame(self, bg=WHITE)
        main_container.pack(expand=True, fill="both", padx=40, pady=20)

        # --- SECCIÓN SUPERIOR: TARJETAS KPI ---
        cards_frame = tk.Frame(main_container, bg=WHITE)
        cards_frame.pack(fill="x", pady=15)

        self.crear_kpi(cards_frame, "ZONA DE ALTO RIESGO", self.analisis['barrio_critico'], "red").pack(side="left", expand=True, fill="both", padx=10)
        self.crear_kpi(cards_frame, "FRANJA HORARIA CRÍTICA", self.analisis['hora_critica'], "orange").pack(side="left", expand=True, fill="both", padx=10)
        self.crear_kpi(cards_frame, "TIPOLOGÍA RECURRENTE", self.analisis['tipo_frecuente'], "blue").pack(side="left", expand=True, fill="both", padx=10)

        # --- SECCIÓN CENTRAL: RECOMENDACIÓN INTELIGENTE (GRANDE) ---
        rec_label_frame = tk.LabelFrame(main_container, text=" 📝 ORDEN DE SERVICIO GENERADA POR IA ", 
                                       font=("Arial", 14, "bold"), bg="#F1F3F5", fg=POLICE_BLUE, labelanchor="n")
        rec_label_frame.pack(expand=True, fill="both", pady=30)

        lbl_rec = tk.Label(
            rec_label_frame, 
            text=self.analisis['recomendacion_ia'], 
            font=("Courier New", 18, "bold"), 
            bg="#F1F3F5", 
            fg="#212529",
            justify="center", 
            wraplength=850, 
            padx=50, 
            pady=60
        )
        lbl_rec.pack(expand=True, fill="both")

        # --- SECCIÓN INFERIOR: RANKING Y FOOTER ---
        footer_frame = tk.Frame(main_container, bg=WHITE)
        footer_frame.pack(fill="x", side="bottom", pady=10)

        # Ranking simplificado para rellenar
        barrios_str = " | ".join([f"{k} ({v})" for k, v in self.analisis['lista_barrios'].items()])
        tk.Label(footer_frame, text=f"RANKING DE INCIDENCIA: {barrios_str}", 
                 font=("Arial", 9), bg=WHITE, fg="gray").pack(side="left")
        
        tk.Label(footer_frame, text="ALCALÁ DE HENARES - SISTEMA CSA v2.0", 
                 font=("Arial", 9, "bold"), bg=WHITE, fg=POLICE_BLUE).pack(side="right")

    def crear_kpi(self, parent, titulo, valor, color):
        f = tk.Frame(parent, bg=WHITE, highlightbackground=color, highlightthickness=2)
        tk.Label(f, text=titulo, bg=WHITE, font=("Arial", 10, "bold")).pack(pady=(10,0))
        tk.Label(f, text=valor, bg=WHITE, fg=color, font=("Arial", 14, "bold")).pack(pady=(0,10))
        return f