# gui/screens/registrar.py — v3.2
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import threading

from servicios.clasificador import ClasificadorIncidentes
from servicios.geo_logic    import obtener_zona_por_direccion
from servicios.geocodificador import geocodificar_direccion, geocodificar
from servicios.db           import get_connection
from servicios.eventos      import emitir
from servicios.db           import registrar_auditoria
from servicios.sesion       import uid as sesion_uid
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG,
    MEDIA_BG, MEDIA_FG, BAJA_BG, BAJA_FG,
    FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

CLF = ClasificadorIncidentes()

GRAVEDAD_UI = {
    "muy alta": (CRITICA_BG, CRITICA_FG, "🔴 CRÍTICA — Despliegue inmediato"),
    "alta":     (ALTA_BG,    ALTA_FG,    "🟠 ALTA — Requiere atención urgente"),
    "media":    (MEDIA_BG,   MEDIA_FG,   "🟡 MEDIA — Intervención estándar"),
    "baja":     (BAJA_BG,    BAJA_FG,    "🟢 BAJA — Patrulla preventiva"),
}

TIPOS_RAPIDOS = [
    ("🚗 Accidente",  "Accidente de tráfico con posibles heridos en la vía pública"),
    ("🥊 Pelea",      "Pelea o agresión física entre varias personas"),
    ("👜 Robo/Hurto", "Robo o hurto de pertenencias a ciudadano"),
    ("🔊 Ruidos",     "Ruidos molestos y alteración de la convivencia"),
    ("🏥 Auxilio",    "Persona que necesita asistencia urgente, posible desmayo"),
    ("🔥 Incendio",   "Incendio o conato de incendio con humo visible"),
    ("💊 Drogas",     "Venta o consumo de drogas en vía pública"),
    ("⚠️ V.Género",   "Posible caso de violencia de género, se escuchan golpes"),
]


class RegistrarScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._clasificacion = None
        self._debounce      = None
        self._viva          = True
        self._canvas_ref    = None   # guardamos ref para el scroll
        self._build()
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, e=None):
        self._viva = False
        # Desregistrar scroll al destruir
        if self._canvas_ref:
            try:
                self._canvas_ref.unbind_all("<MouseWheel>")
            except Exception:
                pass

    def _scroll(self, event):
        """Scroll seguro: verifica que el canvas siga vivo."""
        if self._viva and self._canvas_ref:
            try:
                if self._canvas_ref.winfo_exists():
                    self._canvas_ref.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception:
                pass

    def _build(self):
        make_header(self, "🚨  Registro Operativo de Incidentes")

        canvas = tk.Canvas(self, bg=GRAY_BG, highlightthickness=0)
        self._canvas_ref = canvas
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

        # Scroll solo mientras esta pantalla esté activa
        canvas.bind("<MouseWheel>", self._scroll)
        canvas.bind("<Enter>",
                    lambda e: canvas.bind_all("<MouseWheel>", self._scroll))
        canvas.bind("<Leave>",
                    lambda e: canvas.unbind_all("<MouseWheel>"))

        self._build_tipos_rapidos()
        self._build_ubicacion()
        self._build_descripcion()
        self._build_clasificacion()
        self._build_operador()
        self._build_botones()

    # ── Cards ─────────────────────────────────────────────────────
    def _card(self, titulo):
        outer = tk.Frame(self.body, bg=GRAY_BG)
        outer.pack(fill="x", padx=PAD_X, pady=(0, 10))
        card = tk.Frame(outer, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        card.pack(fill="x")
        hdr = tk.Frame(card, bg="#F8FAFC")
        hdr.pack(fill="x")
        tk.Label(hdr, text=titulo, font=FONT_SUBTITLE,
                 bg="#F8FAFC", fg=DARK_TEXT, pady=8, padx=PAD_X).pack(anchor="w")
        tk.Frame(card, bg=GRAY_BORDER, height=1).pack(fill="x")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(fill="x", padx=PAD_X, pady=PAD_Y)
        return inner

    def _build_tipos_rapidos(self):
        outer = tk.Frame(self.body, bg=GRAY_BG)
        outer.pack(fill="x", padx=PAD_X, pady=(12, 4))
        tk.Label(outer, text="Acceso rápido — clic para rellenar descripción:",
                 font=FONT_SMALL, bg=GRAY_BG, fg=GRAY_TEXT).pack(anchor="w", pady=(0,4))
        row = tk.Frame(outer, bg=GRAY_BG)
        row.pack(fill="x")
        for label, desc in TIPOS_RAPIDOS:
            tk.Button(row, text=label, font=("Segoe UI", 9),
                      bg=WHITE, fg=DARK_TEXT, relief="solid", bd=1,
                      cursor="hand2", padx=8, pady=4,
                      command=lambda d=desc: self._insertar_rapido(d)
                      ).pack(side="left", padx=(0,5), pady=2)

    def _insertar_rapido(self, texto):
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", texto)
        self.txt_desc.focus()
        self._clasificar_live()

    def _build_ubicacion(self):
        loc = self._card("📍  Ubicación del incidente")

        tk.Label(loc, text="Calle y número  (ej: Calle Mayor 12)",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.ent_direccion = tk.Entry(loc, font=FONT_NORMAL,
                                       relief="solid", bd=1, bg=WHITE)
        self.ent_direccion.pack(fill="x", ipady=6, pady=(2,10))
        self.ent_direccion.bind("<KeyRelease>", self._on_dir_change)

        tk.Label(loc, text="Barrio / Zona detectada",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        row = tk.Frame(loc, bg=WHITE)
        row.pack(fill="x", pady=(2,0))
        self.lbl_zona = tk.Label(row, text="—", font=FONT_NORMAL,
                                  bg="#EFF6FF", fg="#1D4ED8",
                                  relief="solid", bd=1, anchor="w",
                                  padx=8, pady=4)
        self.lbl_zona.pack(side="left", fill="x", expand=True)
        self.lbl_geo_estado = tk.Label(row, text="", font=FONT_SMALL,
                                        bg=WHITE, fg=GRAY_TEXT)
        self.lbl_geo_estado.pack(side="left", padx=8)

        # Coordenadas detectadas (invisibles para el operador, útiles para el mapa)
        self._lat = None
        self._lon = None

    def _build_descripcion(self):
        desc = self._card("📝  Descripción de los hechos")
        tk.Label(desc,
                 text="Describa lo ocurrido con el mayor detalle posible",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.txt_desc = tk.Text(desc, height=6, font=FONT_NORMAL,
                                 relief="solid", bd=1, bg=WHITE, wrap="word")
        self.txt_desc.pack(fill="x", pady=(4,0))
        self.txt_desc.bind("<KeyRelease>", self._clasificar_live)
        self.lbl_chars = tk.Label(desc, text="0 caracteres",
                                   font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT, anchor="e")
        self.lbl_chars.pack(fill="x")

    def _build_clasificacion(self):
        cls = self._card("🤖  Clasificación automática en tiempo real")
        self.lbl_tipo = tk.Label(cls,
                                  text="Escriba la descripción para clasificar…",
                                  font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT,
                                  anchor="w", wraplength=700, justify="left")
        self.lbl_tipo.pack(fill="x")
        self.lbl_gravedad = tk.Label(cls, text="", font=FONT_SUBTITLE,
                                      bg=WHITE, anchor="w", pady=4, padx=8)
        self.lbl_gravedad.pack(fill="x", pady=(6,0))
        row = tk.Frame(cls, bg=WHITE)
        row.pack(fill="x", pady=(4,0))
        self.lbl_patrullas  = tk.Label(row, text="", font=FONT_NORMAL,
                                        bg=WHITE, fg=GRAY_TEXT, anchor="w")
        self.lbl_patrullas.pack(side="left")
        self.lbl_confianza  = tk.Label(row, text="", font=FONT_SMALL,
                                        bg=WHITE, fg=GRAY_TEXT, anchor="e")
        self.lbl_confianza.pack(side="right")

    def _build_operador(self):
        op = self._card("👮  Datos del operador")
        row = tk.Frame(op, bg=WHITE)
        row.pack(fill="x")

        c1 = tk.Frame(row, bg=WHITE)
        c1.pack(side="left", expand=True, fill="x", padx=(0,12))
        tk.Label(c1, text="Número de operador / placa",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.ent_operador = tk.Entry(c1, font=FONT_NORMAL,
                                      relief="solid", bd=1, bg=WHITE)
        self.ent_operador.pack(fill="x", ipady=5, pady=(2,0))

        c2 = tk.Frame(row, bg=WHITE)
        c2.pack(side="left", expand=True, fill="x")
        tk.Label(c2, text="Turno", font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.combo_turno = ttk.Combobox(c2, state="readonly",
                                         values=["Mañana (06-14h)",
                                                 "Tarde (14-22h)",
                                                 "Noche (22-06h)"],
                                         font=FONT_NORMAL)
        h = datetime.now().hour
        self.combo_turno.current(0 if 6 <= h < 14 else 1 if 14 <= h < 22 else 2)
        self.combo_turno.pack(fill="x", pady=(2,0))

    def _build_botones(self):
        btn = tk.Frame(self.body, bg=GRAY_BG)
        btn.pack(fill="x", padx=PAD_X, pady=(4,24))
        make_button(btn, "🗑️  Limpiar", self._limpiar, "neutral").pack(side="left")
        make_button(btn, "✅  REGISTRAR INCIDENTE",
                    self._registrar, "success").pack(side="right")

    # ── Eventos ───────────────────────────────────────────────────
    def _on_dir_change(self, e=None):
        dir_ = self.ent_direccion.get().strip()
        if len(dir_) < 4:
            self.lbl_zona.config(text="—")
            self._lat = self._lon = None
            return
        zona = obtener_zona_por_direccion(dir_)
        self.lbl_zona.config(text=f"  {zona}")
        # Geocodificación real en hilo secundario
        self.lbl_geo_estado.config(text="⏳", fg="#D97706")
        threading.Thread(target=self._geo_worker,
                         args=(dir_,), daemon=True).start()

    def _geo_worker(self, dir_):
        """Geocodificación multi-motor en segundo plano."""
        lat, lon, barrio, fuente = geocodificar(dir_)
        from servicios.geocodificador import geocodificar_direccion as _gd
        _, _, zona_real = _gd(dir_)

        iconos = {"google": "🗺️ Google Maps", "photon": "🌐 Photon/OSM",
                  "here": "📡 HERE Maps", "local": "📍 Zona aprox."}
        fuente_txt = iconos.get(fuente, "📍 Zona aprox.")

        def _upd():
            if not self._viva:
                return
            if lat and lon:
                self._lat, self._lon = lat, lon
                self.lbl_zona.config(text=f"  {zona_real}")
                color = "#059669" if fuente != "local" else "#D97706"
                self.lbl_geo_estado.config(text=fuente_txt, fg=color)
            else:
                self._lat = self._lon = None
                self.lbl_zona.config(text=f"  {zona_real}")
                self.lbl_geo_estado.config(text="📍 Sin coords exactas", fg="#D97706")
        self.after(0, _upd)

    def _clasificar_live(self, e=None):
        desc = self.txt_desc.get("1.0", tk.END).strip()
        self.lbl_chars.config(text=f"{len(desc)} caracteres")
        if self._debounce:
            self.after_cancel(self._debounce)
        self._debounce = self.after(350, self._clasificar_exec)

    def _clasificar_exec(self):
        self._debounce = None
        desc = self.txt_desc.get("1.0", tk.END).strip()
        if len(desc) < 8:
            self.lbl_tipo.config(
                text="Escriba la descripción para clasificar…",
                fg=GRAY_TEXT, bg=WHITE)
            self.lbl_gravedad.config(text="", bg=WHITE)
            self.lbl_patrullas.config(text="")
            self.lbl_confianza.config(text="")
            self._clasificacion = None
            return
        r = CLF.procesar_descripcion(desc)
        self._clasificacion = r
        bg, fg, etiqueta = GRAVEDAD_UI.get(r["gravedad"], GRAVEDAD_UI["baja"])
        claves = ", ".join(r.get("confianza", [])[:4]) or "—"
        self.lbl_tipo.config(text=f"{r['emoji']}  {r['tipo']}", fg=fg, bg=WHITE)
        self.lbl_gravedad.config(text=f"  {etiqueta}  ", fg=fg, bg=bg)
        self.lbl_patrullas.config(text=f"🚓  Unidades sugeridas: {r['patrulla']}")
        self.lbl_confianza.config(text=f"Clave(s): {claves}")

    # ── Registro ──────────────────────────────────────────────────
    def _registrar(self):
        direccion   = self.ent_direccion.get().strip()
        descripcion = self.txt_desc.get("1.0", tk.END).strip()

        errores = []
        if not direccion:
            errores.append("• Dirección del incidente")
        if len(descripcion) < 10:
            errores.append("• Descripción (mínimo 10 caracteres)")
        if errores:
            messagebox.showwarning("Campos requeridos",
                                   "Complete:\n\n" + "\n".join(errores))
            return

        if not self._clasificacion:
            self._clasificacion = CLF.procesar_descripcion(descripcion)

        r         = self._clasificacion
        zona      = self.lbl_zona.cget("text").strip() or \
                    obtener_zona_por_direccion(direccion)
        if zona.startswith("—"):
            zona = obtener_zona_por_direccion(direccion)
        fecha     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        operador  = self.ent_operador.get().strip() or "—"
        turno     = self.combo_turno.get()
        lat       = self._lat
        lon       = self._lon

        tipo_guardado = f"{r['emoji']} {r['tipo']} ({r['gravedad'].upper()})"
        desc_full     = f"{descripcion}\n[Op:{operador} | {turno}]"

        try:
            conn   = get_connection()
            cursor = conn.cursor()
            # Añadir columnas lat/lon si no existen
            try:
                cursor.execute("ALTER TABLE incidentes ADD COLUMN lat REAL")
                cursor.execute("ALTER TABLE incidentes ADD COLUMN lon REAL")
                conn.commit()
            except Exception:
                pass
            cursor.execute(
                "INSERT INTO incidentes "
                "(tipo, descripcion, fecha, zona, direccion, lat, lon)"
                " VALUES (?,?,?,?,?,?,?)",
                (tipo_guardado, desc_full, fecha, zona, direccion, lat, lon)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
            conn.close()
        except Exception as ex:
            messagebox.showerror("Error de base de datos", str(ex))
            return

        # Emitir evento ANTES del messagebox
        emitir("incidente_registrado", id=nuevo_id)
        registrar_auditoria(sesion_uid(), "REGISTRAR_INCIDENTE",
                            "incidentes", nuevo_id, f"{zona} — {tipo_guardado[:40]}")

        coords_txt = (f"📌 Coordenadas: {lat:.5f}, {lon:.5f}"
                      if lat else "📌 Sin coordenadas exactas (zona aproximada)")
        messagebox.showinfo(
            "✅ Incidente registrado",
            f"ID: #{nuevo_id}\n"
            f"Zona: {zona}\n"
            f"Categoría: {r['tipo']}\n"
            f"Gravedad: {r['gravedad'].upper()}\n"
            f"Unidades sugeridas: {r['patrulla']}\n"
            f"{coords_txt}"
        )
        self._limpiar()

    def _limpiar(self):
        self.ent_direccion.delete(0, tk.END)
        self.txt_desc.delete("1.0", tk.END)
        self.lbl_zona.config(text="—")
        self.lbl_geo_estado.config(text="")
        self.lbl_tipo.config(text="Escriba la descripción para clasificar…",
                              fg=GRAY_TEXT, bg=WHITE)
        self.lbl_gravedad.config(text="", bg=WHITE)
        self.lbl_patrullas.config(text="")
        self.lbl_confianza.config(text="")
        self.lbl_chars.config(text="0 caracteres")
        self._clasificacion = None
        self._lat = self._lon = None
