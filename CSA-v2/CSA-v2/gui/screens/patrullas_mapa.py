# gui/screens/patrullas_mapa.py — Patrullas en tiempo real v1.0
# PREPARADO: Interfaz completa lista.
# AMPLIACIÓN FUTURA: enchufar API GPS/AVL cuando se disponga del hardware.
import tkinter as tk
from tkinter import ttk, messagebox
from servicios.db      import get_connection, registrar_auditoria
from servicios.sesion  import uid as sesion_uid
from servicios.eventos import suscribir, desuscribir, emitir
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    BAJA_BG, BAJA_FG, ALTA_BG, ALTA_FG, CRITICA_BG, CRITICA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)
from servicios.geo_logic import listar_zonas


class PatrullasMapaScreen(tk.Frame):
    """
    Panel de posiciones de patrullas.
    - Actualización manual: el operador introduce la posición
    - Actualización automática GPS: lista para conectar API AVL/GPS
    """
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._viva     = True
        self._debounce = None
        self._build()
        suscribir("unidad_actualizada", self._on_evento)
        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        self._viva = False
        desuscribir("unidad_actualizada", self._on_evento)
        if self._debounce:
            self.after_cancel(self._debounce)

    def _on_evento(self, **kw):
        if not self._viva: return
        if self._debounce: self.after_cancel(self._debounce)
        self._debounce = self.after(400, self._cargar)

    def _build(self):
        make_header(self, "📡  Posiciones de Patrullas en Tiempo Real")

        # Banner GPS
        gps_frame = tk.Frame(self, bg="#FAEEDA",
                             highlightbackground="#FCD34D", highlightthickness=1)
        gps_frame.pack(fill="x", padx=PAD_X, pady=(8,0))
        inner_gps = tk.Frame(gps_frame, bg="#FAEEDA")
        inner_gps.pack(fill="x", padx=12, pady=8)
        tk.Label(inner_gps,
                 text="⚠️  Modo manual activo — sin GPS conectado",
                 font=("Segoe UI",10,"bold"), bg="#FAEEDA", fg="#92400E").pack(anchor="w")
        tk.Label(inner_gps,
                 text="Las posiciones se actualizan manualmente. "
                      "Cuando se disponga de hardware GPS/AVL, "
                      "conecta el módulo en ⚙️ Configuración → GPS para activar tracking automático.",
                 font=FONT_SMALL, bg="#FAEEDA", fg="#92400E",
                 wraplength=800, justify="left").pack(anchor="w")

        # Toolbar
        tb = tk.Frame(self, bg=WHITE,
                      highlightbackground=GRAY_BORDER, highlightthickness=1)
        tb.pack(fill="x", padx=PAD_X, pady=(8,0))
        inner = tk.Frame(tb, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        make_button(inner, "📍 Actualizar posición",
                    self._actualizar_pos, "primary").pack(side="left", padx=3)
        make_button(inner, "🔄 Refrescar",
                    self._cargar, "info").pack(side="left", padx=3)
        make_button(inner, "🌐 Ver en mapa",
                    self._abrir_mapa, "neutral").pack(side="left", padx=3)

        self.lbl_info = tk.Label(inner, text="", font=FONT_SMALL,
                                  bg=WHITE, fg=GRAY_TEXT)
        self.lbl_info.pack(side="right")

        # Panel dividido: tabla izquierda + detalle derecha
        body = tk.Frame(self, bg=GRAY_BG)
        body.pack(fill="both", expand=True, padx=PAD_X, pady=10)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # Tabla de unidades
        left = tk.Frame(body, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,6))

        tk.Label(left, text="Unidades operativas",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE,
                 pady=8, padx=PAD_X).pack(anchor="w")
        tk.Frame(left, bg=GRAY_BORDER, height=1).pack(fill="x")

        style = ttk.Style()
        style.configure("GPS.Treeview", font=FONT_NORMAL, rowheight=30,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("GPS.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE,
                         relief="flat", padding=(8,5))
        style.map("GPS.Treeview",
                  background=[("selected","#DBEAFE")],
                  foreground=[("selected",DARK_TEXT)])

        cols = ("ID","Indicativo","Estado","Posición actual","Última actualización","GPS")
        self.tree = ttk.Treeview(left, columns=cols,
                                  show="headings", style="GPS.Treeview")
        widths = {"ID":45,"Indicativo":90,"Estado":130,
                  "Posición actual":180,"Última actualización":150,"GPS":60}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c],
                              anchor="center" if c in ("ID","GPS") else "w")

        self.tree.tag_configure("activo",    background=BAJA_BG,  foreground=BAJA_FG)
        self.tree.tag_configure("interv",    background=ALTA_BG,  foreground=ALTA_FG)
        self.tree.tag_configure("inactivo",  background=GRAY_BG,  foreground=GRAY_TEXT)

        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Panel derecho: detalle de unidad seleccionada
        right = tk.Frame(body, bg=WHITE,
                         highlightbackground=GRAY_BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Detalle de unidad",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE,
                 pady=8, padx=PAD_X).pack(anchor="w")
        tk.Frame(right, bg=GRAY_BORDER, height=1).pack(fill="x")

        self.frame_detalle = tk.Frame(right, bg=WHITE)
        self.frame_detalle.pack(fill="both", expand=True, padx=PAD_X, pady=PAD_Y)
        self._mostrar_detalle(None)

        self._cargar()

    def _cargar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT id, indicativo, estado, en_servicio,
                   ubicacion_actual, lat, lon, ultima_pos
            FROM unidades ORDER BY indicativo
        """)
        rows = c.fetchall()
        conn.close()

        en_srv = 0
        for r in rows:
            estado = r[2] or "Disponible"
            gps    = "🟢" if (r[5] and r[6]) else "⬜"
            tag    = ("interv" if "Intervención" in estado
                      else "activo" if r[3] else "inactivo")
            emoji  = {"En Intervención":"🟠 ","Patrullando":"🟢 "}.get(estado,"⬜ ")
            if r[3]: en_srv += 1
            ultima = (r[7][:16] if r[7] else "—")
            self.tree.insert("","end", iid=str(r[0]),
                              values=(r[0], r[1], f"{emoji}{estado}",
                                      r[4] or "Sin posición", ultima, gps),
                              tags=(tag,))

        self.lbl_info.config(text=f"{en_srv} en servicio / {len(rows)} total")

    def _on_select(self, e=None):
        sel = self.tree.selection()
        if not sel: return
        uid = int(self.tree.item(sel[0],"values")[0])
        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT * FROM unidades WHERE id=?", (uid,))
        row = c.fetchone()
        conn.close()
        self._mostrar_detalle(row)

    def _mostrar_detalle(self, row):
        for w in self.frame_detalle.winfo_children():
            w.destroy()
        if row is None:
            tk.Label(self.frame_detalle,
                     text="Selecciona una unidad para ver el detalle.",
                     font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(pady=40)
            return

        def fila(label, valor, color=None):
            f = tk.Frame(self.frame_detalle, bg=WHITE)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, font=FONT_SMALL,
                     bg=WHITE, fg=GRAY_TEXT, width=18, anchor="w").pack(side="left")
            tk.Label(f, text=str(valor) if valor else "—",
                     font=FONT_NORMAL, bg=WHITE,
                     fg=color or DARK_TEXT, anchor="w").pack(side="left")

        fila("Indicativo:",    row[1])
        fila("Estado:",        row[2])
        fila("En servicio:",   "✅ Sí" if row[3] else "❌ No")
        fila("Posición:",      row[4])

        if row[5] and row[6]:
            fila("Coordenadas:", f"{row[5]:.5f}, {row[6]:.5f}", "#1976D2")
            fila("Última pos.:", row[7][:19] if row[7] else "—")

        tk.Frame(self.frame_detalle, bg=GRAY_BORDER, height=1).pack(fill="x", pady=10)
        make_button(self.frame_detalle,
                    "📍 Actualizar posición de esta unidad",
                    lambda r=row: self._actualizar_pos(r[0]),
                    "primary").pack(fill="x")

        # Coordenadas manuales
        coords_frame = tk.Frame(self.frame_detalle, bg=WHITE)
        coords_frame.pack(fill="x", pady=8)
        tk.Label(coords_frame, text="GPS manual (lat, lon):",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        row2 = tk.Frame(coords_frame, bg=WHITE)
        row2.pack(fill="x")
        self.ent_lat = tk.Entry(row2, font=FONT_NORMAL, relief="solid",
                                 bd=1, bg=WHITE, width=12)
        self.ent_lat.insert(0, str(row[5]) if row[5] else "")
        self.ent_lat.pack(side="left", ipady=4)
        tk.Label(row2, text=",", font=FONT_NORMAL, bg=WHITE).pack(side="left", padx=2)
        self.ent_lon = tk.Entry(row2, font=FONT_NORMAL, relief="solid",
                                 bd=1, bg=WHITE, width=12)
        self.ent_lon.insert(0, str(row[6]) if row[6] else "")
        self.ent_lon.pack(side="left", ipady=4)
        make_button(row2, "✅",
                    lambda uid=row[0]: self._guardar_coords(uid),
                    "success").pack(side="left", padx=4)

        # Zona desde selector
        tk.Label(self.frame_detalle, text="O seleccionar zona:",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w", pady=(8,2))
        self.combo_zona = ttk.Combobox(self.frame_detalle,
                                        values=listar_zonas(), state="readonly",
                                        font=FONT_NORMAL)
        if row[4]:
            self.combo_zona.set(row[4])
        self.combo_zona.pack(fill="x")
        make_button(self.frame_detalle, "📍 Actualizar zona",
                    lambda uid=row[0]: self._guardar_zona(uid),
                    "info").pack(fill="x", pady=(6,0))

    def _actualizar_pos(self, uid_forzado=None):
        sel = self.tree.selection()
        uid = uid_forzado or (int(self.tree.item(sel[0],"values")[0]) if sel else None)
        if uid is None:
            messagebox.showwarning("Sin selección","Selecciona una unidad primero.")
            return
        self._on_select()

    def _guardar_coords(self, uid):
        try:
            lat = float(self.ent_lat.get().strip())
            lon = float(self.ent_lon.get().strip())
        except ValueError:
            messagebox.showerror("Error","Coordenadas no válidas.")
            return
        from datetime import datetime
        conn = get_connection()
        conn.execute(
            "UPDATE unidades SET lat=?, lon=?, ultima_pos=? WHERE id=?",
            (lat, lon, datetime.now().isoformat(), uid)
        )
        conn.commit()
        conn.close()
        emitir("unidad_actualizada", u_id=uid)
        messagebox.showinfo("✅","Coordenadas actualizadas.")

    def _guardar_zona(self, uid):
        zona = self.combo_zona.get()
        if not zona: return
        from servicios.geo_logic import obtener_coords_zona
        from datetime import datetime
        lat, lon = obtener_coords_zona(zona)
        conn = get_connection()
        conn.execute(
            "UPDATE unidades SET ubicacion_actual=?, lat=?, lon=?, ultima_pos=? WHERE id=?",
            (zona, lat, lon, datetime.now().isoformat(), uid)
        )
        conn.commit()
        conn.close()
        emitir("unidad_actualizada", u_id=uid)

    def _abrir_mapa(self):
        import webbrowser, servicios.mapa_server as ms
        webbrowser.open(ms.url_mapa())
