# gui/screens/estadisticas.py — Estadísticas v2.0 con gráficos reales
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from servicios.listar import listar_incidentes_df
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_FG, ALTA_FG, MEDIA_FG, BAJA_FG,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

# Paleta de colores para gráficos
COLORES_GRAVEDAD = ["#DC2626","#D97706","#CA8A04","#059669","#1976D2","#7C3AED","#DB2777","#0891B2"]


def _limpiar_tipo(tipo: str) -> str:
    """Extrae la categoría principal quitando emojis y calificativos."""
    import re
    t = re.sub(r'[^\w\s\-/]', '', str(tipo)).strip()
    # Quitar prefijos de gravedad
    for pfx in ["CRÍTICA —","CRITICA —","ALTA —","MEDIA —","BAJA —","MUY ALTA —"]:
        t = t.replace(pfx, "").strip()
    return t[:30] if t else "Sin tipo"


class EstadisticasScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._build()

    def _build(self):
        make_header(self, "📊  Panel de Estadísticas Operativas")

        # Botón actualizar
        ctrl = tk.Frame(self, bg=GRAY_BG)
        ctrl.pack(fill="x", padx=PAD_X, pady=(10, 0))
        make_button(ctrl, "🔄  Actualizar datos", self._refrescar, "info").pack(side="left")

        # Notebook con pestañas
        style = ttk.Style()
        style.configure("TNotebook", background=GRAY_BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=FONT_NORMAL, padding=(16, 6))

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        self.tab_resumen   = tk.Frame(self.nb, bg=WHITE)
        self.tab_zonas     = tk.Frame(self.nb, bg=WHITE)
        self.tab_tipos     = tk.Frame(self.nb, bg=WHITE)
        self.tab_temporal  = tk.Frame(self.nb, bg=WHITE)

        self.nb.add(self.tab_resumen,  text="  Resumen  ")
        self.nb.add(self.tab_zonas,    text="  Por Zonas  ")
        self.nb.add(self.tab_tipos,    text="  Por Tipo  ")
        self.nb.add(self.tab_temporal, text="  Temporal  ")

        self._refrescar()

    def _refrescar(self):
        for tab in [self.tab_resumen, self.tab_zonas, self.tab_tipos, self.tab_temporal]:
            for w in tab.winfo_children():
                w.destroy()

        df = listar_incidentes_df()

        if df.empty:
            for tab in [self.tab_resumen, self.tab_zonas, self.tab_tipos, self.tab_temporal]:
                tk.Label(tab, text="⚠️  Sin datos suficientes para generar estadísticas.",
                         font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT).pack(pady=60)
            return

        # Normalizar
        if "zona"  not in df.columns: df["zona"]  = "Sin zona"
        if "tipo"  not in df.columns: df["tipo"]  = "Sin tipo"
        if "estado" not in df.columns: df["estado"] = "Activo"
        df["tipo_limpio"] = df["tipo"].apply(_limpiar_tipo)

        self._tab_resumen(df)
        self._tab_zonas(df)
        self._tab_tipos(df)
        self._tab_temporal(df)

    # ── Pestaña Resumen ───────────────────────────────────────────
    def _tab_resumen(self, df):
        tab = self.tab_resumen
        total     = len(df)
        activos   = len(df[df["estado"] == "Activo"]) if "estado" in df.columns else total
        finalizados = total - activos

        # KPIs
        kpi_frame = tk.Frame(tab, bg=WHITE)
        kpi_frame.pack(fill="x", padx=24, pady=20)

        kpis = [
            ("📋 Total incidentes", total,       POLICE_BLUE),
            ("🚨 Activos",          activos,      "#DC2626"),
            ("✅ Finalizados",       finalizados,  "#059669"),
            ("📍 Zonas afectadas",  df["zona"].nunique(), "#1976D2"),
        ]
        for i, (label, val, color) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=color, padx=20, pady=14)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=str(val), font=("Segoe UI", 24, "bold"),
                     bg=color, fg=WHITE).pack()
            tk.Label(card, text=label, font=("Segoe UI", 9),
                     bg=color, fg="#E2E8F0").pack()

        # Mini gráfico de pastel activo/finalizado
        fig = Figure(figsize=(4, 3), dpi=90, facecolor=WHITE)
        ax  = fig.add_subplot(111)
        if activos + finalizados > 0:
            ax.pie([activos, finalizados],
                   labels=["Activos","Finalizados"],
                   colors=["#DC2626","#059669"],
                   autopct="%1.0f%%", startangle=90,
                   textprops={"fontsize": 9})
        ax.set_title("Distribución de estados", fontsize=10, pad=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # ── Pestaña Zonas ─────────────────────────────────────────────
    def _tab_zonas(self, df):
        tab = self.tab_zonas
        conteo = df["zona"].value_counts()

        fig = Figure(figsize=(8, 4), dpi=90, facecolor=WHITE)
        ax  = fig.add_subplot(111)
        bars = ax.barh(conteo.index[::-1], conteo.values[::-1],
                       color=COLORES_GRAVEDAD[:len(conteo)], edgecolor="none")
        for bar, val in zip(bars, conteo.values[::-1]):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    str(val), va="center", fontsize=9, color=DARK_TEXT)
        ax.set_title("Incidentes por zona", fontsize=11, pad=10)
        ax.set_xlabel("Número de incidentes")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", labelsize=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)

    # ── Pestaña Tipos ─────────────────────────────────────────────
    def _tab_tipos(self, df):
        tab = self.tab_tipos
        conteo = df["tipo_limpio"].value_counts().head(10)

        fig = Figure(figsize=(8, 4), dpi=90, facecolor=WHITE)
        ax  = fig.add_subplot(111)
        ax.bar(range(len(conteo)), conteo.values,
               color=COLORES_GRAVEDAD[:len(conteo)], edgecolor="none")
        ax.set_xticks(range(len(conteo)))
        ax.set_xticklabels(conteo.index, rotation=30, ha="right", fontsize=8)
        ax.set_title("Top 10 tipologías de incidentes", fontsize=11, pad=10)
        ax.set_ylabel("Número de incidentes")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for i, v in enumerate(conteo.values):
            ax.text(i, v + 0.1, str(v), ha="center", fontsize=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)

    # ── Pestaña Temporal ──────────────────────────────────────────
    def _tab_temporal(self, df):
        tab = self.tab_temporal

        try:
            df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
            df = df.dropna(subset=["fecha_dt"])
            df["hora"] = df["fecha_dt"].dt.hour
            por_hora = df.groupby("hora").size().reindex(range(24), fill_value=0)

            fig = Figure(figsize=(8, 3.5), dpi=90, facecolor=WHITE)
            ax  = fig.add_subplot(111)
            ax.fill_between(por_hora.index, por_hora.values,
                            alpha=0.3, color="#1976D2")
            ax.plot(por_hora.index, por_hora.values,
                    color="#1976D2", linewidth=2, marker="o", markersize=4)
            ax.set_xticks(range(0, 24, 2))
            ax.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 2)], fontsize=8)
            ax.set_title("Distribución horaria de incidentes", fontsize=11, pad=10)
            ax.set_xlabel("Hora del día")
            ax.set_ylabel("Incidentes")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)

        except Exception as e:
            tk.Label(tab, text=f"No hay suficientes datos temporales.\n({e})",
                     font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT).pack(pady=60)
