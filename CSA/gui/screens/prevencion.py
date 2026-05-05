# gui/screens/prevencion.py — Prevención IA v2.0
import tkinter as tk
from tkinter import ttk
from servicios.prevencion import obtener_analisis_predictivo
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG, BAJA_BG, BAJA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL, FONT_TITLE,
    make_button, make_header, PAD_X, PAD_Y
)

class PrevencionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._build()

    def _build(self):
        make_header(self, "🤖  Módulo de Prevención — Análisis Predictivo IA")

        ctrl = tk.Frame(self, bg=GRAY_BG)
        ctrl.pack(fill="x", padx=PAD_X, pady=(10,0))
        make_button(ctrl, "🔄  Regenerar análisis", self._refrescar, "info").pack(side="left")

        self.content = tk.Frame(self, bg=GRAY_BG)
        self.content.pack(fill="both", expand=True)

        self._refrescar()

    def _refrescar(self):
        for w in self.content.winfo_children():
            w.destroy()
        datos = obtener_analisis_predictivo()
        if not datos:
            tk.Label(self.content,
                     text="⚠️  Sin datos históricos suficientes para el análisis predictivo.\n"
                          "Registre incidentes para que el sistema aprenda patrones.",
                     font=FONT_NORMAL, bg=GRAY_BG, fg=GRAY_TEXT,
                     justify="center").pack(pady=80)
            return

        # ── KPIs superiores ───────────────────────────────────────
        kpi_frame = tk.Frame(self.content, bg=GRAY_BG)
        kpi_frame.pack(fill="x", padx=PAD_X, pady=16)

        kpis = [
            ("📍 Zona más conflictiva", datos.get("barrio_critico","—"), CRITICA_BG, CRITICA_FG),
            ("🕐 Franja horaria crítica", datos.get("hora_critica","—"), ALTA_BG, ALTA_FG),
            ("🚨 Tipo más frecuente",     datos.get("tipo_frecuente","—")[:20], "#EFF6FF","#1D4ED8"),
            ("📊 Incidentes analizados",  str(datos.get("total_incidentes","—")), BAJA_BG, BAJA_FG),
        ]
        for i, (lbl, val, bg, fg) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=bg, padx=16, pady=12,
                            highlightbackground=GRAY_BORDER, highlightthickness=1)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=val, font=("Segoe UI",14,"bold"),
                     bg=bg, fg=fg, wraplength=180).pack()
            tk.Label(card, text=lbl, font=("Segoe UI",8),
                     bg=bg, fg=fg).pack()

        # ── Ranking de barrios ────────────────────────────────────
        ranking_card = tk.Frame(self.content, bg=WHITE,
                                highlightbackground=GRAY_BORDER, highlightthickness=1)
        ranking_card.pack(fill="x", padx=PAD_X, pady=(0,12))
        tk.Label(ranking_card, text="📈  Ranking de zonas por incidencias",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE,
                 pady=10, padx=PAD_X).pack(anchor="w")
        tk.Frame(ranking_card, bg=GRAY_BORDER, height=1).pack(fill="x")

        lista = datos.get("lista_barrios", {})
        max_v = max(lista.values()) if lista else 1
        for zona, cnt in sorted(lista.items(), key=lambda x: -x[1]):
            row = tk.Frame(ranking_card, bg=WHITE)
            row.pack(fill="x", padx=PAD_X, pady=4)
            tk.Label(row, text=zona, font=FONT_NORMAL, bg=WHITE,
                     fg=DARK_TEXT, width=28, anchor="w").pack(side="left")
            pct = int((cnt / max_v) * 200)
            bar_bg = tk.Frame(row, bg="#EFF6FF", height=16, width=200)
            bar_bg.pack(side="left", padx=8)
            bar_bg.pack_propagate(False)
            bar_fill = tk.Frame(bar_bg, bg="#1976D2", height=16, width=max(4,pct))
            bar_fill.pack(side="left", fill="y")
            tk.Label(row, text=str(cnt), font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(side="left")

        # ── Orden de servicio generada por IA ────────────────────
        orden_card = tk.Frame(self.content, bg=WHITE,
                              highlightbackground=GRAY_BORDER, highlightthickness=1)
        orden_card.pack(fill="x", padx=PAD_X, pady=(0,16))
        header_ord = tk.Frame(orden_card, bg=POLICE_BLUE)
        header_ord.pack(fill="x")
        tk.Label(header_ord, text="🤖  Orden de servicio generada por IA",
                 font=FONT_SUBTITLE, bg=POLICE_BLUE, fg=WHITE,
                 pady=10, padx=PAD_X).pack(anchor="w")

        rec = datos.get("recomendacion_ia","Sin datos suficientes.")
        txt = tk.Text(orden_card, height=6, font=FONT_NORMAL, bg="#F8FAFC",
                      fg=DARK_TEXT, relief="flat", wrap="word",
                      padx=PAD_X, pady=12)
        txt.insert("1.0", rec)
        txt.config(state="disabled")
        txt.pack(fill="x")
