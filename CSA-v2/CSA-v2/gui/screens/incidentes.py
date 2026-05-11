# gui/screens/incidentes.py — v2.1 con auto-refresco por eventos
import tkinter as tk
from tkinter import ttk, messagebox
from servicios.incidentes import listar_incidentes, modificar_incidente_completo, finalizar_incidente_db
from servicios.listar import eliminar_incidente_db
from servicios.eventos import suscribir, desuscribir
from gui.screens.notas_incidente import NotasIncidenteDialog
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG, MEDIA_BG, MEDIA_FG,
    BAJA_BG, BAJA_FG, FINAL_BG, FINAL_FG,
    FONT_NORMAL, FONT_SMALL, FONT_SUBTITLE, FONT_MENU,
    make_button, make_header, PAD_X, PAD_Y
)

TAG_COLORS = {
    "critica":    (CRITICA_BG, CRITICA_FG),
    "alta":       (ALTA_BG,    ALTA_FG),
    "media":      (MEDIA_BG,   MEDIA_FG),
    "baja":       (BAJA_BG,    BAJA_FG),
    "finalizado": (FINAL_BG,   FINAL_FG),
}

def _tag_desde_tipo(tipo: str) -> str:
    t = str(tipo).upper()
    if "FINALIZADO" in t: return "finalizado"
    if any(x in t for x in ["CRÍTICA","CRITICA","MUY ALTA","ARMA","DISPARO","PRIORIDAD"]): return "critica"
    if "ALTA" in t:  return "alta"
    if "MEDIA" in t: return "media"
    return "baja"


class IncidentesScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._build()
        # Suscribirse a todos los eventos que afectan a la lista
        for ev in ("incidente_registrado","incidente_finalizado",
                   "incidente_modificado","unidad_actualizada"):
            suscribir(ev, self._on_evento)
        self.bind("<Destroy>", self._cleanup)

    def _cleanup(self, e=None):
        for ev in ("incidente_registrado","incidente_finalizado",
                   "incidente_modificado","unidad_actualizada"):
            desuscribir(ev, self._on_evento)

    def _on_evento(self, **kwargs):
        self.after(100, self.cargar_datos)

    def _build(self):
        make_header(self, "📋  Gestión Operativa de Incidentes")

        # ── Toolbar ───────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=WHITE,
                           highlightbackground=GRAY_BORDER, highlightthickness=1)
        toolbar.pack(fill="x", padx=PAD_X, pady=(12, 0))
        inner_tb = tk.Frame(toolbar, bg=WHITE)
        inner_tb.pack(fill="x", padx=12, pady=8)

        tk.Label(inner_tb, text="🔍", font=("Segoe UI",11),
                 bg=WHITE, fg=GRAY_TEXT).pack(side="left")
        self.ent_buscar = tk.Entry(inner_tb, font=FONT_NORMAL, relief="solid",
                                    bd=1, bg=WHITE, fg=DARK_TEXT, width=28)
        self.ent_buscar.pack(side="left", padx=(4,12), ipady=4)
        self.ent_buscar.bind("<KeyRelease>", lambda e: self._filtrar())
        self.ent_buscar.insert(0, "Buscar por tipo, zona o descripción…")
        self.ent_buscar.config(fg=GRAY_TEXT)
        self.ent_buscar.bind("<FocusIn>",  self._clear_ph)
        self.ent_buscar.bind("<FocusOut>", self._restore_ph)

        tk.Label(inner_tb, text="Estado:", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(side="left")
        self.combo_estado = ttk.Combobox(inner_tb, state="readonly",
                                          values=["Todos","Solo activos","Solo finalizados"],
                                          width=16, font=FONT_SMALL)
        self.combo_estado.current(0)
        self.combo_estado.pack(side="left", padx=(4,16))
        self.combo_estado.bind("<<ComboboxSelected>>", lambda e: self._filtrar())

        self.lbl_conteo = tk.Label(inner_tb, text="", font=FONT_SMALL,
                                    bg=WHITE, fg=GRAY_TEXT)
        self.lbl_conteo.pack(side="left")

        btn_area = tk.Frame(inner_tb, bg=WHITE)
        btn_area.pack(side="right")
        make_button(btn_area, "🔄 Refrescar",  self.cargar_datos, "info").pack(side="left", padx=3)
        make_button(btn_area, "✅ Finalizar",   self._finalizar,   "success").pack(side="left", padx=3)
        make_button(btn_area, "📝 Notas",       self._ver_notas,   "primary").pack(side="left", padx=3)
        make_button(btn_area, "✏️ Editar",      self._editar,      "warning").pack(side="left", padx=3)
        make_button(btn_area, "🗑️ Eliminar",   self._eliminar,    "danger").pack(side="left", padx=3)

        # ── Treeview ──────────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=GRAY_BG)
        tree_frame.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("CSA.Treeview",
                         font=FONT_NORMAL, rowheight=28,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("CSA.Treeview.Heading",
                         font=FONT_SUBTITLE, background=POLICE_BLUE,
                         foreground=WHITE, relief="flat", padding=(8,6))
        style.map("CSA.Treeview",
                  background=[("selected","#DBEAFE")],
                  foreground=[("selected",DARK_TEXT)])

        cols = ("ID","Tipo","Descripción","Fecha","Ubicación","Estado")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", style="CSA.Treeview")
        widths = {"ID":50,"Tipo":180,"Descripción":280,
                  "Fecha":145,"Ubicación":200,"Estado":110}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c],
                              anchor="center" if c in ("ID","Estado","Fecha") else "w")

        for tag, (bg, fg) in TAG_COLORS.items():
            self.tree.tag_configure(tag, background=bg, foreground=fg)

        sb_v = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(tree_frame, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.pack(side="right",  fill="y")
        sb_h.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # ── Leyenda ───────────────────────────────────────────────
        leyenda = tk.Frame(self, bg=GRAY_BG)
        leyenda.pack(fill="x", padx=PAD_X, pady=(0,12))
        for etiqueta, (bg, fg) in [
            ("🔴 Crítica",    TAG_COLORS["critica"]),
            ("🟠 Alta",       TAG_COLORS["alta"]),
            ("🟡 Media",      TAG_COLORS["media"]),
            ("🟢 Baja",       TAG_COLORS["baja"]),
            ("✅ Finalizado", TAG_COLORS["finalizado"]),
        ]:
            tk.Label(leyenda, text=f"  {etiqueta}  ", font=FONT_SMALL,
                     bg=bg, fg=fg, relief="solid", bd=1,
                     padx=4, pady=2).pack(side="left", padx=4)

        self._todos = []
        self.cargar_datos()

    # ── Placeholder ───────────────────────────────────────────────
    def _clear_ph(self, e):
        if self.ent_buscar.get() == "Buscar por tipo, zona o descripción…":
            self.ent_buscar.delete(0, tk.END)
            self.ent_buscar.config(fg=DARK_TEXT)

    def _restore_ph(self, e):
        if not self.ent_buscar.get():
            self.ent_buscar.insert(0, "Buscar por tipo, zona o descripción…")
            self.ent_buscar.config(fg=GRAY_TEXT)

    # ── Datos ─────────────────────────────────────────────────────
    def cargar_datos(self):
        registros = listar_incidentes()
        self._todos = []
        for row in registros:
            estado = str(row[6]).strip() if len(row) > 6 else "Activo"
            ubi    = f"{row[5]}  ({row[4]})" if row[5] else row[4]
            estado_v = "✅ Finalizado" if estado == "Finalizado" else "🚨 Activo"
            self._todos.append({
                "id": row[0], "tipo": row[1], "desc": row[2],
                "fecha": row[3], "ubi": ubi, "estado": estado,
                "estado_v": estado_v,
                "tag": "finalizado" if estado == "Finalizado"
                       else _tag_desde_tipo(row[1])
            })
        self._filtrar()

    def _filtrar(self):
        query = self.ent_buscar.get().lower()
        if query == "buscar por tipo, zona o descripción…":
            query = ""
        filtro_estado = self.combo_estado.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        mostrados = 0
        for r in self._todos:
            if filtro_estado == "Solo activos"     and r["estado"] != "Activo":     continue
            if filtro_estado == "Solo finalizados" and r["estado"] != "Finalizado": continue
            if query and not any(query in str(v).lower()
                                 for v in [r["tipo"], r["desc"], r["ubi"]]):
                continue
            desc_corta = r["desc"][:60] + "…" if len(r["desc"]) > 60 else r["desc"]
            self.tree.insert("", "end", iid=str(r["id"]),
                              values=(r["id"], r["tipo"], desc_corta,
                                      r["fecha"], r["ubi"], r["estado_v"]),
                              tags=(r["tag"],))
            mostrados += 1

        self.lbl_conteo.config(text=f"{mostrados} de {len(self._todos)} incidentes")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un incidente de la lista.")
            return None
        return self.tree.item(sel[0], "values")[0]

    def _ver_notas(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un incidente.")
            return
        vals = self.tree.item(sel[0], "values")
        inc_id = int(vals[0])
        tipo   = vals[1]
        NotasIncidenteDialog(self, inc_id, tipo)

    def _finalizar(self):
        inc_id = self._selected_id()
        if inc_id is None: return
        if messagebox.askyesno("Confirmar", f"¿Marcar incidente #{inc_id} como resuelto?"):
            finalizar_incidente_db(inc_id)   # emite evento → auto-refresco

    def _eliminar(self):
        inc_id = self._selected_id()
        if inc_id is None: return
        if messagebox.askyesno("⚠️ Confirmar eliminación",
                               f"¿Eliminar definitivamente el incidente #{inc_id}?\n"
                               "Esta acción no se puede deshacer."):
            eliminar_incidente_db(inc_id)
            self.cargar_datos()

    def _editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un incidente.")
            return
        vals = self.tree.item(sel[0], "values")
        EditorIncidente(self, vals[0], vals[1], vals[2], vals[4],
                        on_save=self.cargar_datos)

    def resaltar_id(self, inc_id):
        self.cargar_datos()
        iid = str(inc_id)
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.see(iid)


class EditorIncidente(tk.Toplevel):
    def __init__(self, parent, inc_id, tipo, desc, ubi, on_save):
        super().__init__(parent)
        self.title(f"Editar Incidente #{inc_id}")
        self.geometry("500x420")
        self.configure(bg=WHITE, padx=24, pady=20)
        self.resizable(False, False)
        self.grab_set()

        self._id      = inc_id
        self._on_save = on_save

        tk.Label(self, text=f"✏️  Editar Incidente #{inc_id}",
                 font=("Segoe UI",13,"bold"),
                 bg=WHITE, fg=POLICE_BLUE).pack(anchor="w", pady=(0,12))

        def field(lbl, val, height=None):
            tk.Label(self, text=lbl, font=("Segoe UI",9),
                     bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
            if height:
                w = tk.Text(self, height=height, font=FONT_NORMAL,
                            relief="solid", bd=1, bg=WHITE)
                w.insert("1.0", val)
            else:
                w = tk.Entry(self, font=FONT_NORMAL, relief="solid",
                             bd=1, bg=WHITE)
                w.insert(0, val)
            w.pack(fill="x", pady=(2,10), ipady=4)
            return w

        self.ent_tipo = field("Tipo de incidente", tipo)
        self.ent_desc = field("Descripción", desc, height=4)
        self.ent_ubi  = field("Ubicación  (Calle (Barrio))", ubi)

        make_button(self, "💾  Guardar cambios", self._guardar, "success").pack(fill="x", pady=(8,0))

    def _guardar(self):
        tipo = self.ent_tipo.get().strip()
        desc = self.ent_desc.get("1.0", tk.END).strip()
        ubi  = self.ent_ubi.get().strip()
        if "(" not in ubi or ")" not in ubi:
            messagebox.showerror("Formato incorrecto",
                                 "La ubicación debe incluir el barrio entre paréntesis.\n"
                                 "Ejemplo: Calle Mayor (Casco Histórico / Centro)")
            return
        try:
            partes    = ubi.split(" (")
            direccion = partes[0].strip()
            zona      = partes[1].replace(")", "").strip()
            modificar_incidente_completo(self._id, tipo, desc, zona, direccion)
            self._on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
