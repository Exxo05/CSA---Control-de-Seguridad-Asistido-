# gui/screens/unidades.py — Gestión de unidades v2.0
import tkinter as tk
from tkinter import ttk, messagebox
from servicios.unidades import (
    listar_unidades, alternar_servicio, cambiar_estado_operativo
)
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    BAJA_BG, BAJA_FG, ALTA_BG, ALTA_FG, CRITICA_BG, CRITICA_FG,
    FINAL_BG, FINAL_FG, FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

ESTADOS_OPERATIVOS = ["Patrullando","En Intervención","En Base","Fuera de Servicio"]

ESTADO_TAG = {
    "Patrullando":       ("baja",   "🟢"),
    "En Intervención":   ("alta",   "🟠"),
    "En Base":           ("neutral","⬜"),
    "Fuera de Servicio": ("final",  "⚫"),
    "Disponible":        ("baja",   "🟢"),
}

class UnidadesScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._build()

    def _build(self):
        make_header(self, "🚓  Gestión de Unidades Operativas")

        # Toolbar
        tb = tk.Frame(self, bg=WHITE,
                      highlightbackground=GRAY_BORDER, highlightthickness=1)
        tb.pack(fill="x", padx=PAD_X, pady=(12, 0))
        inner = tk.Frame(tb, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        make_button(inner, "🔄 Refrescar",        self.cargar,           "info").pack(side="left", padx=3)
        make_button(inner, "✅ Activar turno",     self._activar,         "success").pack(side="left", padx=3)
        make_button(inner, "🔴 Desactivar turno",  self._desactivar,      "danger").pack(side="left", padx=3)
        make_button(inner, "🔁 Cambiar estado",    self._cambiar_estado,  "warning").pack(side="left", padx=3)

        self.lbl_info = tk.Label(inner, text="", font=FONT_SMALL,
                                  bg=WHITE, fg=GRAY_TEXT)
        self.lbl_info.pack(side="right")

        # Treeview
        tree_frame = tk.Frame(self, bg=GRAY_BG)
        tree_frame.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        style = ttk.Style()
        style.configure("U.Treeview",
                         font=FONT_NORMAL, rowheight=32,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("U.Treeview.Heading",
                         font=FONT_SUBTITLE, background=POLICE_BLUE,
                         foreground=WHITE, relief="flat", padding=(8,6))
        style.map("U.Treeview", background=[("selected","#DBEAFE")],
                  foreground=[("selected",DARK_TEXT)])

        cols = ("ID","Indicativo","Estado","En Servicio","Ubicación")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                  style="U.Treeview")
        widths = {"ID":50,"Indicativo":110,"Estado":160,"En Servicio":110,"Ubicación":220}
        anchors = {"ID":"center","En Servicio":"center"}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c],
                              anchor=anchors.get(c,"w"))

        # Tags
        self.tree.tag_configure("baja",    background=BAJA_BG,   foreground=BAJA_FG)
        self.tree.tag_configure("alta",    background=ALTA_BG,   foreground=ALTA_FG)
        self.tree.tag_configure("critica", background=CRITICA_BG,foreground=CRITICA_FG)
        self.tree.tag_configure("neutral", background=GRAY_BG,   foreground=GRAY_TEXT)
        self.tree.tag_configure("final",   background=FINAL_BG,  foreground=FINAL_FG)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Leyenda estado
        ley = tk.Frame(self, bg=GRAY_BG)
        ley.pack(fill="x", padx=PAD_X, pady=(0,12))
        for txt, bg, fg in [
            ("🟢 Patrullando / Disponible", BAJA_BG,  BAJA_FG),
            ("🟠 En Intervención",           ALTA_BG,  ALTA_FG),
            ("⬜ En Base",                   GRAY_BG,  GRAY_TEXT),
            ("⚫ Fuera de Servicio",          FINAL_BG, FINAL_FG),
        ]:
            tk.Label(ley, text=f"  {txt}  ", font=FONT_SMALL,
                     bg=bg, fg=fg, relief="solid", bd=1, padx=4, pady=2).pack(side="left", padx=4)

        self.cargar()

    def cargar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        unidades = listar_unidades()
        en_servicio = 0
        for u in unidades:
            # (id, indicativo, estado, en_servicio, ubicacion)
            srv = "✅ Sí" if u[3] else "❌ No"
            estado = u[2] or "Disponible"
            emoji, tag = ESTADO_TAG.get(estado, ("⬜","neutral"))[1], ESTADO_TAG.get(estado, ("neutral",))[0]
            if u[3]: en_servicio += 1
            self.tree.insert("", "end", iid=str(u[0]),
                              values=(u[0], u[1], f"{emoji} {estado}", srv, u[4] or "—"),
                              tags=(tag,))
        self.lbl_info.config(
            text=f"  {en_servicio} unidades en servicio / {len(unidades)} total"
        )

    def _sel_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección","Seleccione una unidad.")
            return None
        return int(self.tree.item(sel[0],"values")[0])

    def _activar(self):
        uid = self._sel_id()
        if uid: alternar_servicio(uid, 1); self.cargar()

    def _desactivar(self):
        uid = self._sel_id()
        if uid: alternar_servicio(uid, 0); self.cargar()

    def _cambiar_estado(self):
        uid = self._sel_id()
        if uid is None: return
        CambiarEstadoDialog(self, uid, on_save=self.cargar)


class CambiarEstadoDialog(tk.Toplevel):
    def __init__(self, parent, uid, on_save):
        super().__init__(parent)
        self.title("Cambiar estado operativo")
        self.geometry("320x200")
        self.configure(bg=WHITE, padx=24, pady=20)
        self.resizable(False, False)
        self.grab_set()

        self._uid = uid
        self._on_save = on_save

        tk.Label(self, text=f"Estado para unidad #{uid}",
                 font=("Segoe UI",11,"bold"), bg=WHITE, fg=POLICE_BLUE).pack(anchor="w", pady=(0,12))

        self.combo = ttk.Combobox(self, values=ESTADOS_OPERATIVOS,
                                   state="readonly", font=FONT_NORMAL)
        self.combo.current(0)
        self.combo.pack(fill="x", pady=(0,16))

        make_button(self, "✅  Aplicar", self._aplicar, "success").pack(fill="x")

    def _aplicar(self):
        cambiar_estado_operativo(self._uid, self.combo.get())
        self._on_save()
        self.destroy()
