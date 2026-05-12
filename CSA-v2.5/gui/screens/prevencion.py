# gui/screens/prevencion.py — v3.0 con IA real (Claude API) y dos pestañas
import tkinter as tk
from tkinter import ttk
import threading, datetime

from servicios.prevencion import obtener_analisis_predictivo
from servicios.eventos    import suscribir, desuscribir
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG, BAJA_BG, BAJA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

# ── Constante de la API ───────────────────────────────────────────
API_URL   = "https://api.anthropic.com/v1/messages"
API_MODEL = "claude-sonnet-4-20250514"


def _llamar_api_ia(contexto: dict) -> str:
    """Llama a Claude API y devuelve la orden de servicio generada."""
    import json, urllib.request, urllib.error

    prompt = f"""Eres un sistema de análisis predictivo de seguridad pública para la Policía Local de Alcalá de Henares.

Con base en los siguientes datos estadísticos de incidentes registrados, genera una ORDEN DE SERVICIO OPERATIVA real y concreta:

DATOS:
- Zona más conflictiva: {contexto.get('barrio_critico','—')}
- Franja horaria de mayor riesgo: {contexto.get('hora_critica','—')}
- Tipo de incidente más frecuente: {contexto.get('tipo_frecuente','—')}
- Total incidentes analizados: {contexto.get('total_incidentes',0)}
- Distribución por zonas: {json.dumps(contexto.get('lista_barrios', {}), ensure_ascii=False)}

Genera una orden de servicio con:
1. Análisis de la situación (2-3 líneas)
2. Medidas concretas y específicas para el turno (con zonas reales de Alcalá de Henares)
3. Recomendaciones de despliegue de unidades
4. Alertas especiales si las hay

Sé específico, usa lenguaje policial operativo, menciona zonas concretas de Alcalá de Henares. Máximo 200 palabras."""

    payload = json.dumps({
        "model":      API_MODEL,
        "max_tokens": 500,
        "messages":   [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return _orden_estatica(contexto)
        return f"[Error API {e.code}] {e.reason}\n\n" + _orden_estatica(contexto)
    except Exception as e:
        return _orden_estatica(contexto)


def _orden_estatica(ctx: dict) -> str:
    """Fallback si la API no está disponible."""
    from servicios.prevencion import generar_orden_dinamica
    return generar_orden_dinamica(
        ctx.get("barrio_critico","—"),
        ctx.get("hora_critica","—"),
        ctx.get("tipo_frecuente","—")
    )


class PrevencionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._auto_id       = None
        self._orden_ia_txt  = None
        self._generando_ia  = False
        self._build()
        suscribir("incidente_registrado", self._on_evento)
        suscribir("incidente_finalizado", self._on_evento)
        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        desuscribir("incidente_registrado", self._on_evento)
        desuscribir("incidente_finalizado", self._on_evento)
        if self._auto_id:
            self.after_cancel(self._auto_id)

    def _on_evento(self, **kw):
        if self._auto_id:
            self.after_cancel(self._auto_id)
        self._auto_id = self.after(1500, self._refrescar_datos)

    def _build(self):
        make_header(self, "🤖  Módulo de Prevención — Análisis Predictivo IA")

        # ── Toolbar ───────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=GRAY_BG)
        ctrl.pack(fill="x", padx=PAD_X, pady=(10, 0))
        make_button(ctrl, "🔄 Actualizar datos",       self._refrescar_datos, "info").pack(side="left")
        make_button(ctrl, "🤖 Generar orden con IA",   self._generar_ia,      "primary").pack(side="left", padx=8)
        self.lbl_hora = tk.Label(ctrl, text="", font=FONT_SMALL, bg=GRAY_BG, fg=GRAY_TEXT)
        self.lbl_hora.pack(side="left", padx=8)
        self.lbl_ia_estado = tk.Label(ctrl, text="", font=FONT_SMALL, bg=GRAY_BG, fg=GRAY_TEXT)
        self.lbl_ia_estado.pack(side="right")

        # ── Notebook: Actuales / Históricos ───────────────────────
        style = ttk.Style()
        style.configure("Prev.TNotebook", background=GRAY_BG, borderwidth=0)
        style.configure("Prev.TNotebook.Tab", font=("Segoe UI",10,"bold"), padding=(20,8))

        self.nb = ttk.Notebook(self, style="Prev.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        self.tab_actuales  = tk.Frame(self.nb, bg=GRAY_BG)
        self.tab_historicos = tk.Frame(self.nb, bg=GRAY_BG)

        self.nb.add(self.tab_actuales,   text="  📋 Incidentes Actuales  ")
        self.nb.add(self.tab_historicos, text="  📂 Histórico de Delitos  ")

        self._datos = None
        self._refrescar_datos()
        self._build_historicos()

    # ── Tab Actuales ──────────────────────────────────────────────
    def _refrescar_datos(self):
        self._auto_id = None
        for w in self.tab_actuales.winfo_children():
            w.destroy()

        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_hora.config(text=f"Último análisis: {hora}")

        self._datos = obtener_analisis_predictivo()
        if not self._datos:
            tk.Label(self.tab_actuales,
                     text="⚠️  Sin incidentes registrados aún.\n\nRegistre incidentes para ver el análisis.",
                     font=FONT_NORMAL, bg=GRAY_BG, fg=GRAY_TEXT,
                     justify="center").pack(pady=80)
            return

        self._build_tab_actuales(self._datos)

    def _build_tab_actuales(self, datos):
        tab = self.tab_actuales

        # KPIs
        kpi_frame = tk.Frame(tab, bg=GRAY_BG)
        kpi_frame.pack(fill="x", pady=16)
        kpis = [
            ("📍 Zona más conflictiva", datos.get("barrio_critico","—"), CRITICA_BG, CRITICA_FG),
            ("🕐 Franja crítica",        datos.get("hora_critica","—"), ALTA_BG, ALTA_FG),
            ("🚨 Tipo más frecuente",    datos.get("tipo_frecuente","—")[:22], "#EFF6FF","#1D4ED8"),
            ("📊 Incidentes analizados", str(datos.get("total_incidentes","0")), BAJA_BG, BAJA_FG),
        ]
        for i, (lbl, val, bg, fg) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=bg, padx=16, pady=14,
                            highlightbackground=GRAY_BORDER, highlightthickness=1)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=val, font=("Segoe UI",12,"bold"),
                     bg=bg, fg=fg, wraplength=200).pack()
            tk.Label(card, text=lbl, font=("Segoe UI",8), bg=bg, fg=fg).pack()

        # Ranking
        rk = tk.Frame(tab, bg=WHITE,
                      highlightbackground=GRAY_BORDER, highlightthickness=1)
        rk.pack(fill="x", pady=(0,10))
        tk.Label(rk, text="📈  Ranking de zonas por incidencias",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE,
                 pady=10, padx=PAD_X).pack(anchor="w")
        tk.Frame(rk, bg=GRAY_BORDER, height=1).pack(fill="x")

        lista = datos.get("lista_barrios", {})
        max_v = max(lista.values()) if lista else 1
        for zona, cnt in sorted(lista.items(), key=lambda x: -x[1]):
            row = tk.Frame(rk, bg=WHITE)
            row.pack(fill="x", padx=PAD_X, pady=3)
            tk.Label(row, text=zona, font=FONT_NORMAL, bg=WHITE,
                     fg=DARK_TEXT, width=32, anchor="w").pack(side="left")
            pct = max(4, int((cnt / max_v) * 220))
            bar_bg = tk.Frame(row, bg="#EFF6FF", height=16, width=220)
            bar_bg.pack(side="left", padx=8)
            bar_bg.pack_propagate(False)
            tk.Frame(bar_bg, bg="#1976D2", height=16, width=pct).pack(side="left", fill="y")
            tk.Label(row, text=str(cnt), font=FONT_SMALL,
                     bg=WHITE, fg=GRAY_TEXT).pack(side="left")

        # Orden de servicio IA
        orden_card = tk.Frame(tab, bg=WHITE,
                              highlightbackground=GRAY_BORDER, highlightthickness=1)
        orden_card.pack(fill="x", pady=(0,12))
        hdr = tk.Frame(orden_card, bg=POLICE_BLUE)
        hdr.pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg=POLICE_BLUE)
        hdr_inner.pack(fill="x", padx=PAD_X, pady=8)
        tk.Label(hdr_inner, text="🤖  Orden de Servicio",
                 font=FONT_SUBTITLE, bg=POLICE_BLUE, fg=WHITE).pack(side="left")
        tk.Label(hdr_inner,
                 text="(generada por IA — pulse el botón para actualizar)",
                 font=("Segoe UI",8), bg=POLICE_BLUE, fg="#94A3B8").pack(side="left", padx=8)

        self._txt_orden = tk.Text(orden_card, height=8, font=FONT_NORMAL,
                                   bg="#F8FAFC", fg=DARK_TEXT, relief="flat",
                                   wrap="word", padx=PAD_X, pady=12)
        rec = self._datos.get("recomendacion_ia","") if self._datos else ""
        self._txt_orden.insert("1.0", rec or "Pulse «🤖 Generar orden con IA» para obtener recomendaciones.")
        self._txt_orden.config(state="disabled")
        self._txt_orden.pack(fill="x")

    def _generar_ia(self):
        if self._generando_ia or not self._datos:
            return
        self._generando_ia = True
        self.lbl_ia_estado.config(text="⏳ Consultando IA…", fg="#D97706")
        threading.Thread(target=self._ia_worker, daemon=True).start()

    def _ia_worker(self):
        try:
            texto = _llamar_api_ia(self._datos)
            def _actualizar():
                if self._txt_orden:
                    self._txt_orden.config(state="normal")
                    self._txt_orden.delete("1.0", tk.END)
                    self._txt_orden.insert("1.0", texto)
                    self._txt_orden.config(state="disabled")
                self.lbl_ia_estado.config(
                    text=f"✅ Orden generada — {datetime.datetime.now().strftime('%H:%M:%S')}",
                    fg="#059669")
            self.after(0, _actualizar)
        except Exception as e:
            self.after(0, lambda: self.lbl_ia_estado.config(
                text=f"❌ Error IA: {e}", fg="#DC2626"))
        finally:
            self._generando_ia = False

    # ── Tab Históricos ────────────────────────────────────────────
    def _build_historicos(self):
        tab = self.tab_historicos

        tk.Label(tab,
                 text="📂  Histórico de Delitos",
                 font=FONT_SUBTITLE, bg=GRAY_BG, fg=POLICE_BLUE).pack(anchor="w", pady=(12,4))
        tk.Label(tab,
                 text="Esta sección muestra los delitos del histórico cargado en la base de datos.\n"
                      "Para cargar datos históricos usa: scripts/cargar_delitos_historicos.py",
                 font=FONT_SMALL, bg=GRAY_BG, fg=GRAY_TEXT).pack(anchor="w", padx=4, pady=(0,8))

        # Tabla
        from tkinter import ttk
        style = ttk.Style()
        style.configure("H.Treeview", font=FONT_NORMAL, rowheight=26,
                         background=WHITE, fieldbackground=WHITE, foreground=DARK_TEXT)
        style.configure("H.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE, relief="flat")

        cols = ("ID","Tipo","Fecha","Zona","Descripción")
        tree = ttk.Treeview(tab, columns=cols, show="headings", style="H.Treeview")
        widths = {"ID":50,"Tipo":150,"Fecha":140,"Zona":180,"Descripción":300}
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=widths[c], anchor="w")

        sb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # Cargar datos históricos
        try:
            from servicios.historicos import listar_historicos_df
            df = listar_historicos_df()
            if df.empty:
                tree.insert("", "end", values=("—","Sin datos históricos","—","—",
                            "Cargue datos con scripts/cargar_delitos_historicos.py"))
            else:
                for _, row in df.iterrows():
                    tree.insert("", "end", values=(
                        row.get("id",""),
                        row.get("tipo","")[:30],
                        row.get("fecha",""),
                        row.get("zona",""),
                        row.get("descripcion","")[:60],
                    ))
        except Exception as e:
            tree.insert("", "end", values=("","Error cargando históricos","","",str(e)))
