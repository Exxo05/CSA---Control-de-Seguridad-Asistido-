import tkinter as tk
from tkinter import ttk, messagebox
from servicios.listar import listar_incidentes_df
import pandas as pd

class EstadisticasScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        for w in self.winfo_children(): w.destroy()
        
        tk.Label(self, text="📊 ESTADÍSTICAS OPERATIVAS CSA", font=("Arial", 16, "bold")).pack(pady=15)

        df = listar_incidentes_df()
        if df.empty:
            tk.Label(self, text="⚠️ No hay datos suficientes para generar estadísticas.").pack(pady=50)
            return

        # Normalizar columnas para evitar errores
        if "tipo" not in df.columns: df["tipo"] = "Otros"
        if "zona" not in df.columns: df["zona"] = "Sin Zona"

        # Resumen por Barrios
        frame_zona = ttk.LabelFrame(self, text=" Incidentes por Barrios ")
        frame_zona.pack(fill="x", padx=20, pady=10)
        
        stats_zona = df["zona"].value_counts()
        for zona, cant in stats_zona.items():
            tk.Label(frame_zona, text=f"📍 {zona}: {cant} avisos").pack(anchor="w", padx=10)

        # Resumen por Tipología
        frame_tipo = ttk.LabelFrame(self, text=" Tipología de Delitos ")
        frame_tipo.pack(fill="x", padx=20, pady=10)
        
        stats_tipo = df["tipo"].value_counts()
        for tipo, cant in stats_tipo.items():
            tk.Label(frame_tipo, text=f"🚨 {tipo}: {cant} registros").pack(anchor="w", padx=10)

        tk.Button(self, text="🔄 ACTUALIZAR", command=self.init_ui).pack(pady=20)