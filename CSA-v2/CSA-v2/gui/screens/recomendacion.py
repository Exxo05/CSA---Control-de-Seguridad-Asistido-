# gui/screens/recomendacion.py — v3.0 sin _rebuild, refresco parcial
import tkinter as tk
from tkinter import ttk, messagebox

from servicios.unidades   import listar_unidades, asignar_unidad_a_incidente
from servicios.incidentes import listar_incidentes
from servicios.eventos    import suscribir, desuscribir
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG, MEDIA_BG, MEDIA_FG,
    BAJA_BG, BAJA_FG, FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

GRAVEDAD_UI = {
    "CRÍTICA": (CRITICA_BG, CRITICA_FG, "🔴", 3, "Despliegue INMEDIATO — Todas las unidades disponibles"),
    "ALTA":    (ALTA_BG,    ALTA_FG,    "🟠", 2, "Urgente — Mínimo 2 unidades"),
    "MEDIA":   (MEDIA_BG,   MEDIA_FG,   "🟡", 1, "Intervención estándar — 1-2 unidades"),
    "BAJA":    (BAJA_BG,    BAJA_FG,    "🟢", 1, "Patrulla preventiva — 1 unidad"),
}

def _gravedad(tipo: str) -> str:
    t = str(tipo).upper()
    if any(x in t for x in ["CRÍTICA","CRITICA","MUY ALTA","ARMA","DISPARO","PRIORIDAD"]):
        return "CRÍTICA"
    if "ALTA" in t:  return "ALTA"
    if "MEDIA" in t: return "MEDIA"
    return "BAJA"


class RecomendacionScreen(tk.Frame):
    """
    Pantalla de despliegue. NO usa _rebuild() para refrescarse:
    actualiza únicamente el combo de incidentes y la lista de unidades
    para evitar perder las suscripciones a eventos.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._u_data   = []
        self._debounce = None
        self._viva     = True   # flag para saber si el widget sigue activo

        self._build()

        # Suscribir UNA SOLA VEZ — nunca se pierden aunque se refresque
        for ev in ("incidente_registrado", "incidente_finalizado", "unidad_actualizada"):
            suscribir(ev, self._on_evento)

        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        self._viva = False
        for ev in ("incidente_registrado", "incidente_finalizado", "unidad_actualizada"):
            desuscribir(ev, self._on_evento)
        if self._debounce:
            self.after_cancel(self._debounce)

    def _on_evento(self, **kw):
        """Debounce 500ms → refresco parcial (NO destruye widgets)."""
        if not self._viva:
            return
        if self._debounce:
            self.after_cancel(self._debounce)
        self._debounce = self.after(500, self._refrescar)

    # ── Construcción inicial (solo una vez) ───────────────────────
    def _build(self):
        make_header(self, "🧠  Asistente de Despliegue Operativo")

        body = tk.Frame(self, bg=GRAY_BG)
        body.pack(fill="both", expand=True, padx=PAD_X, pady=12)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # ── Columna izquierda ─────────────────────────────────────
        left = tk.Frame(body, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(left, text="1.  Seleccione incidente activo",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE,
                 pady=10, padx=PAD_X).pack(anchor="w")
        tk.Frame(left, bg=GRAY_BORDER, height=1).pack(fill="x")

        inc_inner = tk.Frame(left, bg=WHITE)
        inc_inner.pack(fill="x", padx=PAD_X, pady=PAD_Y)

        # Combo incidentes
        self.combo_inc = ttk.Combobox(inc_inner, state="readonly",
                                       font=FONT_NORMAL, width=50)
        self.combo_inc.pack(fill="x", pady=(0, 4))
        self.combo_inc.bind("<<ComboboxSelected>>", self._analizar)

        # Mensaje cuando no hay incidentes activos
        self.lbl_sin_inc = tk.Label(inc_inner,
                                     text="✅  Sin incidentes activos. Ciudad bajo control.",
                                     font=FONT_NORMAL, fg="#059669", bg=WHITE)

        # Panel de análisis de gravedad
        self.frame_analisis = tk.Frame(left, bg=WHITE)
        self.frame_analisis.pack(fill="x", padx=PAD_X)

        self.lbl_gravedad = tk.Label(self.frame_analisis, text="",
                                      font=FONT_SUBTITLE, bg=WHITE, anchor="w", pady=6, padx=10)
        self.lbl_gravedad.pack(fill="x")
        self.lbl_consejo = tk.Label(self.frame_analisis, text="",
                                     font=FONT_SMALL, bg=WHITE, fg=DARK_TEXT,
                                     anchor="w", wraplength=480, justify="left")
        self.lbl_consejo.pack(fill="x", padx=10, pady=(0, 6))
        self.lbl_sugerencia = tk.Label(self.frame_analisis, text="",
                                        font=FONT_NORMAL, bg=WHITE,
                                        fg=POLICE_BLUE, anchor="w", padx=10)
        self.lbl_sugerencia.pack(fill="x")

        # ── Columna derecha: unidades ─────────────────────────────
        right = tk.Frame(body, bg=WHITE,
                         highlightbackground=GRAY_BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="2.  Unidades disponibles",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE,
                 pady=10, padx=PAD_X).pack(anchor="w")
        tk.Frame(right, bg=GRAY_BORDER, height=1).pack(fill="x")

        u_inner = tk.Frame(right, bg=WHITE)
        u_inner.pack(fill="both", expand=True, padx=PAD_X, pady=PAD_Y)

        self.lista_u = tk.Listbox(u_inner, selectmode="multiple",
                                   font=FONT_NORMAL, relief="solid", bd=1,
                                   bg="#F8FAFC", selectbackground="#DBEAFE",
                                   selectforeground=DARK_TEXT, activestyle="none")
        self.lista_u.pack(fill="both", expand=True)

        self.lbl_n_unidades = tk.Label(right, text="",
                                        font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT)
        self.lbl_n_unidades.pack(pady=(2, 4))
        tk.Label(right, text="Ctrl+clic para selección múltiple",
                 font=("Segoe UI", 8), bg=WHITE, fg=GRAY_TEXT).pack(pady=(0, 6))

        # ── Botones ───────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=GRAY_BG)
        btn_frame.pack(fill="x", padx=PAD_X, pady=(0, 16))

        make_button(btn_frame, "🔄  Refrescar",
                    self._refrescar, "info").pack(side="right", padx=(8, 0))
        self.btn_enviar = make_button(btn_frame,
                                       "🚀  ENVIAR PATRULLAS AL INCIDENTE",
                                       self._enviar, "danger")
        self.btn_enviar.pack(side="right")

        # Carga inicial
        self._refrescar()

    # ── Refresco parcial (no destruye widgets) ────────────────────
    def _refrescar(self):
        if not self._viva:
            return
        self._debounce = None

        incidentes = listar_incidentes(solo_activos=True)

        if not incidentes:
            self.combo_inc.pack_forget()
            self.lbl_sin_inc.pack(anchor="w")
            self.lbl_gravedad.config(text="", bg=WHITE)
            self.lbl_consejo.config(text="")
            self.lbl_sugerencia.config(text="")
            self.btn_enviar.config(state="disabled")
        else:
            self.lbl_sin_inc.pack_forget()
            self.combo_inc.pack(fill="x", pady=(0, 4))
            self.btn_enviar.config(state="normal")

            # Guardar selección anterior si sigue siendo válida
            sel_ant = self.combo_inc.get()
            valores = [f"#{i[0]}  |  {i[1][:38]}  —  {i[4]}" for i in incidentes]
            self.combo_inc["values"] = valores

            if sel_ant in valores:
                self.combo_inc.set(sel_ant)
            else:
                self.combo_inc.current(0)

            self._analizar()

        self._cargar_unidades()

    def _cargar_unidades(self):
        self._u_data = [
            u for u in listar_unidades(solo_en_servicio=True)
            if u[2] in ("Patrullando", "Disponible")
        ]
        self.lista_u.delete(0, tk.END)
        for u in self._u_data:
            self.lista_u.insert(tk.END, f"  🚓 {u[1]}  —  {u[4] or 'Sin zona'}")

        total_srv = len(listar_unidades(solo_en_servicio=True))
        self.lbl_n_unidades.config(
            text=f"{len(self._u_data)} disponibles / {total_srv} en servicio"
        )

    def _analizar(self, event=None):
        sel = self.combo_inc.get()
        if not sel:
            return
        tipo  = sel.split("|")[1].strip().split("—")[0].strip() if "|" in sel else ""
        nivel = _gravedad(tipo)
        bg, fg, emoji, n_uds, consejo = GRAVEDAD_UI.get(nivel, GRAVEDAD_UI["BAJA"])

        self.lbl_gravedad.config(text=f"  {emoji}  Nivel {nivel}  ", bg=bg, fg=fg)
        self.lbl_consejo.config(text=consejo)
        self.lbl_sugerencia.config(text=f"🚓  Unidades recomendadas: {n_uds}")

        # Preseleccionar primeras N unidades
        self.lista_u.selection_clear(0, tk.END)
        for i in range(min(n_uds, len(self._u_data))):
            self.lista_u.selection_set(i)

    def _enviar(self):
        indices = self.lista_u.curselection()
        if not indices:
            messagebox.showwarning("Sin unidades", "Seleccione al menos una unidad.")
            return

        sel = self.combo_inc.get()
        if not sel:
            messagebox.showwarning("Sin incidente", "Seleccione un incidente.")
            return

        destino = sel.split("—")[-1].strip() if "—" in sel else "Zona desconocida"
        indicativo_list = []
        for i in indices:
            asignar_unidad_a_incidente(self._u_data[i][0], destino)
            indicativo_list.append(self._u_data[i][1])

        messagebox.showinfo(
            "✅ Unidades desplegadas",
            f"Patrullas enviadas a: {destino}\n\n"
            f"Unidades: {', '.join(indicativo_list)}\n\n"
            "Cuando finalice la intervención, usa\n"
            "«🏁 Finalizar intervención» en Gestión Unidades."
        )
