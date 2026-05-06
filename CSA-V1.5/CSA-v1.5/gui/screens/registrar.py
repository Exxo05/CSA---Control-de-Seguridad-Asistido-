# gui/screens/registrar.py — Pantalla de registro v2.0
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from servicios.clasificador import ClasificadorIncidentes
from servicios.geo_logic    import obtener_zona_por_direccion, listar_zonas
from servicios.db           import get_connection
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL, FONT_MENU,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG,
    MEDIA_BG, MEDIA_FG, BAJA_BG, BAJA_FG,
    make_button, make_header, color_por_tipo, PAD_X, PAD_Y
)

CLF = ClasificadorIncidentes()

GRAVEDAD_UI = {
    "muy alta": (CRITICA_BG, CRITICA_FG, "🔴 CRÍTICA — Despliegue inmediato"),
    "alta":     (ALTA_BG,    ALTA_FG,    "🟠 ALTA — Requiere atención urgente"),
    "media":    (MEDIA_BG,   MEDIA_FG,   "🟡 MEDIA — Intervención estándar"),
    "baja":     (BAJA_BG,    BAJA_FG,    "🟢 BAJA — Patrulla preventiva"),
}

class RegistrarScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._clasificacion = None
        self._after_id = None
        self._build()

    def _build(self):
        make_header(self, "🚨  Registro Operativo de Incidentes")

        # ── Scrollable content ───────────────────────────────────
        canvas = tk.Canvas(self, bg=GRAY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.content = tk.Frame(canvas, bg=GRAY_BG)
        win_id = canvas.create_window((0, 0), window=self.content, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())

        self.content.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

        self._build_form(self.content)

    def _card(self, parent, titulo=None):
        outer = tk.Frame(parent, bg=GRAY_BG)
        outer.pack(fill="x", padx=PAD_X, pady=8)
        card = tk.Frame(outer, bg=WHITE, relief="flat",
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        card.pack(fill="x")
        if titulo:
            tk.Label(card, text=titulo, font=FONT_SUBTITLE,
                     bg=WHITE, fg=DARK_TEXT, pady=10, padx=PAD_X).pack(anchor="w")
            tk.Frame(card, bg=GRAY_BORDER, height=1).pack(fill="x")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(fill="x", padx=PAD_X, pady=PAD_Y)
        return inner

    def _build_form(self, parent):
        # ── Tarjeta 1: Ubicación ─────────────────────────────────
        loc = self._card(parent, "📍  Ubicación del incidente")

        tk.Label(loc, text="Dirección (calle y número)", font=FONT_NORMAL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.ent_direccion = tk.Entry(loc, font=FONT_NORMAL, relief="solid",
                                      bd=1, bg=WHITE)
        self.ent_direccion.pack(fill="x", pady=(4, 10), ipady=6)
        self.ent_direccion.bind("<KeyRelease>", self._auto_zona)

        tk.Label(loc, text="Zona detectada automáticamente",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.lbl_zona = tk.Label(loc, text="—", font=FONT_NORMAL,
                                  bg="#EFF6FF", fg="#1D4ED8", relief="solid", bd=1,
                                  anchor="w", padx=8, pady=4)
        self.lbl_zona.pack(fill="x", pady=(4, 0))

        # ── Tarjeta 2: Descripción ───────────────────────────────
        desc = self._card(parent, "📝  Descripción de los hechos")

        tk.Label(desc, text="Redacte lo ocurrido con el mayor detalle posible",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.txt_desc = tk.Text(desc, height=6, font=FONT_NORMAL,
                                 relief="solid", bd=1, bg=WHITE, wrap="word")
        self.txt_desc.pack(fill="x", pady=(4, 0))
        self.txt_desc.bind("<KeyRelease>", self._clasificar_live)

        # ── Tarjeta 3: Clasificación automática ──────────────────
        cls_frame = self._card(parent, "🤖  Clasificación automática en tiempo real")

        self.lbl_tipo = tk.Label(cls_frame, text="Escriba la descripción para clasificar…",
                                  font=FONT_NORMAL, bg=WHITE, fg=GRAY_TEXT,
                                  anchor="w", wraplength=650, justify="left")
        self.lbl_tipo.pack(fill="x")

        self.lbl_gravedad = tk.Label(cls_frame, text="", font=FONT_SUBTITLE,
                                      bg=WHITE, anchor="w", pady=4, padx=8)
        self.lbl_gravedad.pack(fill="x", pady=(6, 0))

        self.lbl_patrullas = tk.Label(cls_frame, text="", font=FONT_NORMAL,
                                       bg=WHITE, fg=GRAY_TEXT, anchor="w")
        self.lbl_patrullas.pack(fill="x", pady=(4, 0))

        # ── Botones ──────────────────────────────────────────────
        btn_frame = tk.Frame(parent, bg=GRAY_BG)
        btn_frame.pack(fill="x", padx=PAD_X, pady=(4, 20))

        make_button(btn_frame, "🗑️  Limpiar formulario",
                    self._limpiar, style="neutral").pack(side="left", padx=(0, 8))
        make_button(btn_frame, "✅  REGISTRAR INCIDENTE",
                    self._registrar, style="success").pack(side="right")

    # ── Eventos ───────────────────────────────────────────────────
    def _auto_zona(self, event=None):
        direccion = self.ent_direccion.get().strip()
        if len(direccion) < 4:
            self.lbl_zona.config(text="—")
            return
        zona = obtener_zona_por_direccion(direccion)
        self.lbl_zona.config(text=f"  {zona}")

    def _clasificar_live(self, event=None):
        """Clasificación con debounce de 400ms para no saturar en cada tecla."""
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(400, self._ejecutar_clasificacion)

    def _ejecutar_clasificacion(self):
        desc = self.txt_desc.get("1.0", tk.END).strip()
        if len(desc) < 10:
            self.lbl_tipo.config(text="Escriba la descripción para clasificar…",
                                  fg=GRAY_TEXT, bg=WHITE)
            self.lbl_gravedad.config(text="", bg=WHITE)
            self.lbl_patrullas.config(text="")
            self._clasificacion = None
            return

        r = CLF.procesar_descripcion(desc)
        self._clasificacion = r

        bg, fg, etiqueta = GRAVEDAD_UI.get(r["gravedad"], (BAJA_BG, BAJA_FG, ""))
        confianza_str = ", ".join(r.get("confianza", [])[:5]) or "análisis general"

        self.lbl_tipo.config(
            text=f"{r['emoji']}  {r['tipo']}   |   Clave(s): {confianza_str}",
            fg=fg, bg=WHITE
        )
        self.lbl_gravedad.config(text=etiqueta, fg=fg, bg=bg)
        self.lbl_patrullas.config(
            text=f"🚓  Unidades recomendadas: {r['patrulla']}"
        )

    def _registrar(self):
        direccion = self.ent_direccion.get().strip()
        descripcion = self.txt_desc.get("1.0", tk.END).strip()

        if not direccion:
            messagebox.showwarning("Campo requerido", "Introduzca la dirección del incidente.")
            return
        if not descripcion or len(descripcion) < 10:
            messagebox.showwarning("Campo requerido", "La descripción es demasiado corta.")
            return

        # Clasificar si aún no se ha hecho
        if not self._clasificacion:
            self._clasificacion = CLF.procesar_descripcion(descripcion)

        r = self._clasificacion
        zona = obtener_zona_por_direccion(direccion)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tipo_guardado = f"{r['emoji']} {r['tipo']} ({r['gravedad'].upper()})"

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO incidentes (tipo, descripcion, fecha, zona, direccion) VALUES (?,?,?,?,?)",
                (tipo_guardado, descripcion, fecha, zona, direccion)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
            conn.close()
            # Notificar al resto de pantallas (mapa, incidentes…)
            from servicios.eventos import emitir
            emitir("incidente_registrado", id=nuevo_id)
        except Exception as e:
            messagebox.showerror("Error de base de datos", str(e))
            return

        messagebox.showinfo(
            "✅ Incidente registrado",
            f"Zona: {zona}\n"
            f"Categoría: {r['tipo']}\n"
            f"Gravedad: {r['gravedad'].upper()}\n"
            f"Unidades sugeridas: {r['patrulla']}"
        )
        self._limpiar()

    def _limpiar(self):
        self.ent_direccion.delete(0, tk.END)
        self.txt_desc.delete("1.0", tk.END)
        self.lbl_zona.config(text="—")
        self.lbl_tipo.config(text="Escriba la descripción para clasificar…",
                              fg=GRAY_TEXT, bg=WHITE)
        self.lbl_gravedad.config(text="", bg=WHITE)
        self.lbl_patrullas.config(text="")
        self._clasificacion = None
