# gui/screens/auditoria.py — Log de auditoría
import tkinter as tk
from tkinter import ttk
from servicios.db import get_connection
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)


class AuditoriaScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._build()

    def _build(self):
        make_header(self, "📋  Log de Auditoría del Sistema")

        tb = tk.Frame(self, bg=WHITE,
                      highlightbackground=GRAY_BORDER, highlightthickness=1)
        tb.pack(fill="x", padx=PAD_X, pady=(12,0))
        inner = tk.Frame(tb, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        tk.Label(inner, text="🔍", font=("Segoe UI",11),
                 bg=WHITE, fg=GRAY_TEXT).pack(side="left")
        self.ent = tk.Entry(inner, font=FONT_NORMAL, relief="solid",
                             bd=1, bg=WHITE, width=30)
        self.ent.pack(side="left", padx=(4,12), ipady=4)
        self.ent.bind("<KeyRelease>", lambda e: self._filtrar())

        make_button(inner, "🔄 Refrescar", self._cargar, "info").pack(side="left", padx=3)

        self.lbl_total = tk.Label(inner, text="", font=FONT_SMALL,
                                   bg=WHITE, fg=GRAY_TEXT)
        self.lbl_total.pack(side="right")

        tree_frame = tk.Frame(self, bg=GRAY_BG)
        tree_frame.pack(fill="both", expand=True, padx=PAD_X, pady=10)

        style = ttk.Style()
        style.configure("A.Treeview", font=("Consolas",9), rowheight=24,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("A.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE,
                         relief="flat", padding=(8,5))

        cols = ("ID","Fecha","Usuario","Acción","Tabla","Registro","Detalle")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", style="A.Treeview")
        ws = {"ID":50,"Fecha":145,"Usuario":130,"Acción":160,
              "Tabla":90,"Registro":70,"Detalle":260}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=ws[c],
                              anchor="center" if c in ("ID","Registro") else "w")

        sb_v = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(tree_frame, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.pack(side="right", fill="y")
        sb_h.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self._datos = []
        self._cargar()

    def _cargar(self):
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT a.id, a.fecha, COALESCE(u.nombre,'Sistema'),
                   a.accion, a.tabla, a.registro_id, a.detalle
            FROM auditoria a
            LEFT JOIN usuarios u ON u.id=a.usuario_id
            ORDER BY a.fecha DESC LIMIT 500
        """)
        self._datos = c.fetchall()
        conn.close()
        self._filtrar()

    def _filtrar(self):
        q = self.ent.get().lower().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        n = 0
        for r in self._datos:
            if q and not any(q in str(v).lower() for v in r):
                continue
            self.tree.insert("","end", values=(
                r[0], r[1][:19] if r[1] else "—",
                r[2], r[3], r[4] or "—", r[5] or "—",
                (r[6][:60]+"…" if r[6] and len(r[6])>60 else r[6]) or "—"
            ))
            n += 1
        self.lbl_total.config(text=f"{n} registros")
