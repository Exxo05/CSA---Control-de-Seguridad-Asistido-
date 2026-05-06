# gui/screens/unidades.py — v2.1 con Finalizar Intervención
import tkinter as tk
from tkinter import ttk, messagebox
from servicios.unidades import (
    listar_unidades, alternar_servicio,
    cambiar_estado_operativo, finalizar_intervencion
)
from servicios.eventos import suscribir, desuscribir
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    BAJA_BG, BAJA_FG, ALTA_BG, ALTA_FG, CRITICA_BG, CRITICA_FG,
    FINAL_BG, FINAL_FG, FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

ESTADOS_OPERATIVOS = ["Patrullando", "En Intervención", "En Base", "Fuera de Servicio"]

ESTADO_TAG = {
    "Patrullando":       ("baja",    "🟢"),
    "En Intervención":   ("alta",    "🟠"),
    "En Base":           ("neutral", "⬜"),
    "Fuera de Servicio": ("final",   "⚫"),
    "Disponible":        ("baja",    "🟢"),
}


class UnidadesScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._build()
        suscribir("unidad_actualizada", self._on_evento)
        suscribir("incidente_finalizado", self._on_evento)
        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        desuscribir("unidad_actualizada", self._on_evento)
        desuscribir("incidente_finalizado", self._on_evento)

    def _on_evento(self, **kwargs):
        self.after(50, self.cargar)

    def _build(self):
        make_header(self, "🚓  Gestión de Unidades Operativas")

        # ── Toolbar ───────────────────────────────────────────────
        tb = tk.Frame(self, bg=WHITE,
                      highlightbackground=GRAY_BORDER, highlightthickness=1)
        tb.pack(fill="x", padx=PAD_X, pady=(12, 0))
        inner = tk.Frame(tb, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        make_button(inner, "🔄 Refrescar",           self.cargar,              "info").pack(side="left", padx=3)
        make_button(inner, "✅ Activar turno",        self._activar,            "success").pack(side="left", padx=3)
        make_button(inner, "🔴 Desactivar turno",     self._desactivar,         "danger").pack(side="left", padx=3)
        make_button(inner, "🔁 Cambiar estado",       self._cambiar_estado,     "warning").pack(side="left", padx=3)

        # ── BOTÓN CLAVE: Finalizar intervención ───────────────────
        tk.Frame(inner, bg=GRAY_BORDER, width=1).pack(side="left", fill="y", padx=8)
        make_button(inner, "🏁 Finalizar intervención", self._finalizar_intervencion,
                    "primary").pack(side="left", padx=3)

        self.lbl_info = tk.Label(inner, text="", font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT)
        self.lbl_info.pack(side="right")

        # ── Treeview ──────────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=GRAY_BG)
        tree_frame.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        style = ttk.Style()
        style.configure("U.Treeview",
                         font=FONT_NORMAL, rowheight=32,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("U.Treeview.Heading",
                         font=FONT_SUBTITLE, background=POLICE_BLUE,
                         foreground=WHITE, relief="flat", padding=(8, 6))
        style.map("U.Treeview",
                  background=[("selected", "#DBEAFE")],
                  foreground=[("selected", DARK_TEXT)])

        cols = ("ID", "Indicativo", "Estado", "En Servicio", "Ubicación actual")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", style="U.Treeview")
        widths = {"ID": 50, "Indicativo": 110, "Estado": 180,
                  "En Servicio": 100, "Ubicación actual": 260}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c],
                              anchor="center" if c in ("ID", "En Servicio") else "w")

        self.tree.tag_configure("baja",    background=BAJA_BG,    foreground=BAJA_FG)
        self.tree.tag_configure("alta",    background=ALTA_BG,    foreground=ALTA_FG)
        self.tree.tag_configure("critica", background=CRITICA_BG, foreground=CRITICA_FG)
        self.tree.tag_configure("neutral", background=GRAY_BG,    foreground=GRAY_TEXT)
        self.tree.tag_configure("final",   background=FINAL_BG,   foreground=FINAL_FG)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # ── Leyenda ───────────────────────────────────────────────
        ley = tk.Frame(self, bg=GRAY_BG)
        ley.pack(fill="x", padx=PAD_X, pady=(0, 12))
        for txt, bg, fg in [
            ("🟢 Patrullando",      BAJA_BG,  BAJA_FG),
            ("🟠 En Intervención",  ALTA_BG,  ALTA_FG),
            ("⬜ En Base",          GRAY_BG,  GRAY_TEXT),
            ("⚫ Fuera de Servicio", FINAL_BG, FINAL_FG),
        ]:
            tk.Label(ley, text=f"  {txt}  ", font=FONT_SMALL,
                     bg=bg, fg=fg, relief="solid", bd=1,
                     padx=4, pady=2).pack(side="left", padx=4)

        # Ayuda contextual
        tk.Label(ley,
                 text="  💡 Selecciona una unidad En Intervención y pulsa «Finalizar intervención»",
                 font=FONT_SMALL, bg=GRAY_BG, fg=GRAY_TEXT).pack(side="left", padx=16)

        self.cargar()

    # ── Datos ─────────────────────────────────────────────────────
    def cargar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        unidades = listar_unidades()
        en_servicio = 0
        for u in unidades:
            srv    = "✅ Sí" if u[3] else "❌ No"
            estado = u[2] or "Disponible"
            tag_key = ESTADO_TAG.get(estado, ("neutral", "⬜"))
            tag, emoji = tag_key[0], tag_key[1]
            if u[3]:
                en_servicio += 1
            self.tree.insert("", "end", iid=str(u[0]),
                              values=(u[0], u[1], f"{emoji} {estado}",
                                      srv, u[4] or "—"),
                              tags=(tag,))
        total = len(unidades)
        self.lbl_info.config(
            text=f"  {en_servicio} en servicio / {total} total"
        )

    # ── Acciones ──────────────────────────────────────────────────
    def _sel_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione una unidad de la lista.")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _activar(self):
        uid = self._sel_id()
        if uid:
            alternar_servicio(uid, 1)

    def _desactivar(self):
        uid = self._sel_id()
        if uid:
            alternar_servicio(uid, 0)

    def _cambiar_estado(self):
        uid = self._sel_id()
        if uid is None:
            return
        CambiarEstadoDialog(self, uid, on_save=self.cargar)

    def _finalizar_intervencion(self):
        uid = self._sel_id()
        if uid is None:
            return

        # Verificar que la unidad esté realmente en intervención
        vals = self.tree.item(str(uid), "values")
        estado_actual = vals[2] if vals else ""
        if "Intervención" not in estado_actual and "Intervencion" not in estado_actual:
            messagebox.showwarning(
                "Unidad no en intervención",
                "Esta unidad no está en intervención.\n\n"
                "Solo se pueden finalizar unidades con estado «🟠 En Intervención»."
            )
            return

        zona_actual = vals[4] if vals else "—"
        indicativo  = vals[1] if vals else f"#{uid}"

        if not messagebox.askyesno(
            "Finalizar intervención",
            f"¿Finalizar la intervención de {indicativo}?\n\n"
            f"Zona: {zona_actual}\n\n"
            f"La unidad volverá a estado «Patrullando» y el incidente\n"
            f"asociado a esa zona quedará marcado como Finalizado."
        ):
            return

        zona_cerrada = finalizar_intervencion(uid)
        messagebox.showinfo(
            "✅ Intervención finalizada",
            f"Unidad {indicativo} de vuelta a patrullaje.\n"
            f"Incidente en zona «{zona_cerrada or zona_actual}» cerrado."
        )


class CambiarEstadoDialog(tk.Toplevel):
    def __init__(self, parent, uid, on_save):
        super().__init__(parent)
        self.title("Cambiar estado operativo")
        self.geometry("320x210")
        self.configure(bg=WHITE, padx=24, pady=20)
        self.resizable(False, False)
        self.grab_set()

        self._uid     = uid
        self._on_save = on_save

        tk.Label(self, text=f"Nuevo estado — Unidad #{uid}",
                 font=("Segoe UI", 11, "bold"),
                 bg=WHITE, fg=POLICE_BLUE).pack(anchor="w", pady=(0, 12))

        self.combo = ttk.Combobox(self, values=ESTADOS_OPERATIVOS,
                                   state="readonly", font=FONT_NORMAL)
        self.combo.current(0)
        self.combo.pack(fill="x", pady=(0, 16))

        make_button(self, "✅  Aplicar", self._aplicar, "success").pack(fill="x")

    def _aplicar(self):
        cambiar_estado_operativo(self._uid, self.combo.get())
        self._on_save()
        self.destroy()
