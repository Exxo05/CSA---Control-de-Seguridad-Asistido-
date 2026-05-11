# gui/screens/dashboard.py — Dashboard de turno v1.0
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading

from servicios.db      import get_connection
from servicios.sesion  import nombre as sesion_nombre, rol as sesion_rol
from servicios.eventos import suscribir, desuscribir
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG, BAJA_BG, BAJA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)


class DashboardScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._viva     = True
        self._debounce = None
        self._build()
        for ev in ("incidente_registrado", "incidente_finalizado",
                   "unidad_actualizada", "incidente_modificado"):
            suscribir(ev, self._on_evento)
        self.bind("<Destroy>", self._cleanup)
        # Auto-refresco cada 30s
        self._tick_id = self.after(30000, self._tick)

    def _cleanup(self, e=None):
        self._viva = False
        for ev in ("incidente_registrado", "incidente_finalizado",
                   "unidad_actualizada", "incidente_modificado"):
            desuscribir(ev, self._on_evento)
        if self._debounce:
            self.after_cancel(self._debounce)
        if self._tick_id:
            self.after_cancel(self._tick_id)

    def _on_evento(self, **kw):
        if not self._viva: return
        if self._debounce: self.after_cancel(self._debounce)
        self._debounce = self.after(600, self._refrescar_datos)

    def _tick(self):
        if not self._viva: return
        self._refrescar_datos()
        self._tick_id = self.after(30000, self._tick)

    def _build(self):
        make_header(self, "🏠  Centro de Mando — Resumen del Turno")

        # Scroll
        canvas = tk.Canvas(self, bg=GRAY_BG, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(canvas, bg=GRAY_BG)
        win = canvas.create_window((0, 0), window=self.body, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=canvas.winfo_width())
        self.body.bind("<Configure>", _resize)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind("<Enter>",
                    lambda e: canvas.bind_all("<MouseWheel>",
                        lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)),"units")
                        if self._viva and canvas.winfo_exists() else None))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        self._build_bienvenida()
        self._build_kpis()
        self._build_activos()
        self._build_unidades()
        self._build_ultimos()

    def _card(self, titulo=None):
        outer = tk.Frame(self.body, bg=GRAY_BG)
        outer.pack(fill="x", padx=PAD_X, pady=(0, 10))
        card = tk.Frame(outer, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        card.pack(fill="x")
        if titulo:
            hdr = tk.Frame(card, bg="#F8FAFC")
            hdr.pack(fill="x")
            tk.Label(hdr, text=titulo, font=FONT_SUBTITLE,
                     bg="#F8FAFC", fg=DARK_TEXT, pady=8, padx=PAD_X).pack(anchor="w")
            tk.Frame(card, bg=GRAY_BORDER, height=1).pack(fill="x")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(fill="x", padx=PAD_X, pady=PAD_Y)
        return inner, card

    def _build_bienvenida(self):
        outer = tk.Frame(self.body, bg=POLICE_BLUE)
        outer.pack(fill="x", padx=PAD_X, pady=(12, 10))
        inner = tk.Frame(outer, bg=POLICE_BLUE)
        inner.pack(fill="x", padx=20, pady=14)

        left = tk.Frame(inner, bg=POLICE_BLUE)
        left.pack(side="left", expand=True, fill="x")

        hora = datetime.now().strftime("%H:%M")
        fecha = datetime.now().strftime("%A %d de %B de %Y").capitalize()
        tk.Label(left, text=f"Bienvenido, {sesion_nombre()}",
                 font=("Segoe UI", 14, "bold"), bg=POLICE_BLUE, fg=WHITE).pack(anchor="w")
        tk.Label(left, text=f"Rol: {sesion_rol().capitalize()}   |   {fecha}",
                 font=FONT_SMALL, bg=POLICE_BLUE, fg="#94A3B8").pack(anchor="w", pady=(2,0))

        right = tk.Frame(inner, bg=POLICE_BLUE)
        right.pack(side="right")
        self.lbl_hora_dash = tk.Label(right, text=hora,
                                       font=("Segoe UI", 28, "bold"),
                                       bg=POLICE_BLUE, fg=WHITE)
        self.lbl_hora_dash.pack()
        self._actualizar_hora_dash()

        make_button(outer, "🔄  Actualizar todo",
                    self._refrescar_datos, "info").pack(side="right", padx=16, pady=14)

    def _actualizar_hora_dash(self):
        if not self._viva: return
        self.lbl_hora_dash.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._actualizar_hora_dash)

    def _build_kpis(self):
        inner, _ = self._card()
        self.kpi_frame = inner
        self._refrescar_kpis()

    def _build_activos(self):
        inner, _ = self._card("🚨  Incidentes activos ahora")
        self.frame_activos = inner

        cols = ("ID","Tipo","Zona","Hora","Tiempo activo")
        style = ttk.Style()
        style.configure("D.Treeview", font=FONT_NORMAL, rowheight=26,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("D.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE,
                         relief="flat", padding=(6,4))
        style.map("D.Treeview",
                  background=[("selected","#DBEAFE")],
                  foreground=[("selected",DARK_TEXT)])

        self.tree_activos = ttk.Treeview(inner, columns=cols,
                                          show="headings", style="D.Treeview",
                                          height=6)
        widths = {"ID":50,"Tipo":200,"Zona":180,"Hora":130,"Tiempo activo":120}
        for c in cols:
            self.tree_activos.heading(c, text=c)
            self.tree_activos.column(c, width=widths[c],
                                      anchor="center" if c in ("ID","Tiempo activo") else "w")

        self.tree_activos.tag_configure("critica", background=CRITICA_BG, foreground=CRITICA_FG)
        self.tree_activos.tag_configure("alta",    background=ALTA_BG,    foreground=ALTA_FG)
        self.tree_activos.tag_configure("normal",  background=WHITE,      foreground=DARK_TEXT)
        self.tree_activos.pack(fill="x")

    def _build_unidades(self):
        inner, _ = self._card("🚓  Estado de unidades")
        self.frame_unidades = inner
        self._refrescar_unidades()

    def _build_ultimos(self):
        inner, _ = self._card("📋  Últimas 5 acciones")
        self.frame_ultimos = inner
        self._refrescar_ultimos()

    def _refrescar_datos(self):
        if not self._viva: return
        self._debounce = None
        self._refrescar_kpis()
        self._refrescar_activos()
        self._refrescar_unidades()
        self._refrescar_ultimos()

    def _refrescar_kpis(self):
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT COUNT(*) FROM incidentes WHERE estado='Activo'")
        n_act = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM incidentes WHERE estado='Finalizado' AND fecha >= date('now')")
        n_fin = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM unidades WHERE en_servicio=1")
        n_uni = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM unidades WHERE estado='En Intervención'")
        n_int = c.fetchone()[0]
        conn.close()

        kpis = [
            ("🚨 Activos",        str(n_act),  CRITICA_BG if n_act > 0 else BAJA_BG,
                                                CRITICA_FG if n_act > 0 else BAJA_FG),
            ("✅ Fin. hoy",       str(n_fin),  BAJA_BG,    BAJA_FG),
            ("🚓 En servicio",    str(n_uni),  "#EFF6FF",  "#1D4ED8"),
            ("🟠 En intervención",str(n_int),  ALTA_BG,    ALTA_FG),
        ]
        for i, (lbl, val, bg, fg) in enumerate(kpis):
            card = tk.Frame(self.kpi_frame, bg=bg, padx=20, pady=14,
                            highlightbackground=GRAY_BORDER, highlightthickness=1)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            self.kpi_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=val, font=("Segoe UI",28,"bold"),
                     bg=bg, fg=fg).pack()
            tk.Label(card, text=lbl, font=("Segoe UI",9),
                     bg=bg, fg=fg).pack()

    def _refrescar_activos(self):
        for i in self.tree_activos.get_children():
            self.tree_activos.delete(i)
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT id, tipo, zona, fecha FROM incidentes
            WHERE estado='Activo' ORDER BY fecha ASC LIMIT 20
        """)
        ahora = datetime.now()
        for row in c.fetchall():
            try:
                dt    = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                delta = ahora - dt
                mins  = int(delta.total_seconds() // 60)
                if mins < 60:
                    tiempo = f"{mins} min"
                else:
                    tiempo = f"{mins//60}h {mins%60}m"
            except Exception:
                tiempo = "—"
            tipo = str(row[1])
            tag  = ("critica" if any(x in tipo.upper() for x in ["CRÍTICA","CRITICA","MUY ALTA"])
                    else "alta" if "ALTA" in tipo.upper() else "normal")
            hora = row[3][11:16] if row[3] else "—"
            self.tree_activos.insert("","end",
                                      values=(row[0], tipo[:45], row[2], hora, tiempo),
                                      tags=(tag,))
        conn.close()

    def _refrescar_unidades(self):
        for w in self.frame_unidades.winfo_children():
            w.destroy()
        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT indicativo, estado, en_servicio, ubicacion_actual FROM unidades ORDER BY indicativo")
        rows = c.fetchall()
        conn.close()

        cols = tk.Frame(self.frame_unidades, bg=WHITE)
        cols.pack(fill="x")
        for i, r in enumerate(rows):
            estado = r[1] or "Disponible"
            color  = (ALTA_BG if "Intervención" in estado
                      else BAJA_BG if r[2] else GRAY_BG)
            fcolor = (ALTA_FG if "Intervención" in estado
                      else BAJA_FG if r[2] else GRAY_TEXT)
            badge  = tk.Frame(cols, bg=color, padx=12, pady=8,
                              highlightbackground=GRAY_BORDER, highlightthickness=1)
            badge.grid(row=i//4, column=i%4, padx=4, pady=4, sticky="ew")
            cols.columnconfigure(i%4, weight=1)
            tk.Label(badge, text=r[0], font=("Segoe UI",11,"bold"),
                     bg=color, fg=fcolor).pack()
            tk.Label(badge, text=estado, font=("Segoe UI",8),
                     bg=color, fg=fcolor).pack()
            if r[3]:
                tk.Label(badge, text=r[3][:20], font=("Segoe UI",7),
                         bg=color, fg=fcolor).pack()

    def _refrescar_ultimos(self):
        for w in self.frame_ultimos.winfo_children():
            w.destroy()
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT a.fecha, a.accion, a.tabla, u.nombre
            FROM auditoria a
            LEFT JOIN usuarios u ON u.id = a.usuario_id
            ORDER BY a.fecha DESC LIMIT 5
        """)
        rows = c.fetchall()
        conn.close()
        if not rows:
            tk.Label(self.frame_ultimos,
                     text="Sin acciones registradas aún.",
                     font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
            return
        for r in rows:
            row = tk.Frame(self.frame_ultimos, bg=WHITE)
            row.pack(fill="x", pady=2)
            hora = r[0][11:19] if r[0] else "—"
            tk.Label(row, text=hora, font=("Consolas",9),
                     bg=WHITE, fg=GRAY_TEXT, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=r[1], font=FONT_SMALL,
                     bg=WHITE, fg=DARK_TEXT, anchor="w", width=28).pack(side="left")
            tk.Label(row, text=f"por {r[3] or '—'}",
                     font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT, anchor="w").pack(side="left")
