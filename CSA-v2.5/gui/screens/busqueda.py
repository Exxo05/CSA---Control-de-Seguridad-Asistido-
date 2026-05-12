# gui/screens/busqueda.py — Búsqueda global unificada
import tkinter as tk
from tkinter import ttk, messagebox
from servicios.db import get_connection
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, BAJA_BG, BAJA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)


class BusquedaScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._viva    = True
        self._debounce = None
        self._build()
        self.bind("<Destroy>", lambda e: setattr(self, "_viva", False))

    def _build(self):
        make_header(self, "🔍  Búsqueda Global")

        # Barra de búsqueda grande
        search_card = tk.Frame(self, bg=WHITE,
                               highlightbackground=GRAY_BORDER, highlightthickness=1)
        search_card.pack(fill="x", padx=PAD_X, pady=(16,8))
        inner = tk.Frame(search_card, bg=WHITE)
        inner.pack(fill="x", padx=20, pady=16)

        tk.Label(inner,
                 text="Busca en todos los registros: incidentes, personas, vehículos y unidades",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w", pady=(0,8))

        row = tk.Frame(inner, bg=WHITE)
        row.pack(fill="x")
        self.ent = tk.Entry(row, font=("Segoe UI",13), relief="solid",
                            bd=2, bg=WHITE, fg=DARK_TEXT)
        self.ent.pack(side="left", fill="x", expand=True, ipady=9)
        self.ent.bind("<KeyRelease>", self._on_key)
        self.ent.bind("<Return>",     lambda e: self._buscar())
        self.ent.focus()

        make_button(row, "🔍  Buscar", self._buscar, "primary").pack(side="left", padx=(8,0))

        # Filtros
        filtros = tk.Frame(inner, bg=WHITE)
        filtros.pack(fill="x", pady=(10,0))
        tk.Label(filtros, text="Buscar en:", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(side="left")
        self._vars = {}
        for txt in ["Incidentes","Personas","Vehículos","Unidades"]:
            v = tk.BooleanVar(value=True)
            self._vars[txt] = v
            tk.Checkbutton(filtros, text=txt, variable=v,
                           font=FONT_SMALL, bg=WHITE).pack(side="left", padx=6)

        # Notebook de resultados
        style = ttk.Style()
        style.configure("B.TNotebook", background=GRAY_BG, borderwidth=0)
        style.configure("B.TNotebook.Tab", font=FONT_NORMAL, padding=(14,6))

        self.nb = ttk.Notebook(self, style="B.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=PAD_X, pady=(0,12))

        self.tab_inc = tk.Frame(self.nb, bg=WHITE)
        self.tab_per = tk.Frame(self.nb, bg=WHITE)
        self.tab_veh = tk.Frame(self.nb, bg=WHITE)
        self.tab_uni = tk.Frame(self.nb, bg=WHITE)

        self.nb.add(self.tab_inc, text="  📋 Incidentes (0)  ")
        self.nb.add(self.tab_per, text="  👤 Personas (0)  ")
        self.nb.add(self.tab_veh, text="  🚗 Vehículos (0)  ")
        self.nb.add(self.tab_uni, text="  🚓 Unidades (0)  ")

        self._init_tabs()
        self._msg("Escribe para buscar en todos los registros del sistema.")

    def _init_tabs(self):
        # Incidentes
        cols = ("ID","Tipo","Descripción","Fecha","Zona","Estado")
        self.tree_inc = self._make_tree(self.tab_inc, cols,
                                        {"ID":50,"Tipo":180,"Descripción":260,
                                         "Fecha":140,"Zona":160,"Estado":90})
        # Personas
        cols = ("ID","Nombre","Apellidos","DNI","Teléfono")
        self.tree_per = self._make_tree(self.tab_per, cols,
                                        {"ID":50,"Nombre":160,"Apellidos":180,
                                         "DNI":110,"Teléfono":110})
        # Vehículos
        cols = ("ID","Matrícula","Marca","Modelo","Color","Propietario","Alerta")
        self.tree_veh = self._make_tree(self.tab_veh, cols,
                                        {"ID":50,"Matrícula":100,"Marca":100,
                                         "Modelo":100,"Color":80,
                                         "Propietario":160,"Alerta":80})
        self.tree_veh.tag_configure("alerta", background=CRITICA_BG, foreground=CRITICA_FG)
        # Unidades
        cols = ("ID","Indicativo","Estado","En servicio","Ubicación")
        self.tree_uni = self._make_tree(self.tab_uni, cols,
                                        {"ID":50,"Indicativo":110,"Estado":160,
                                         "En servicio":100,"Ubicación":240})

    def _make_tree(self, parent, cols, widths):
        style = ttk.Style()
        style.configure("B.Treeview", font=FONT_NORMAL, rowheight=26,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("B.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE,
                         relief="flat", padding=(8,5))
        style.map("B.Treeview",
                  background=[("selected","#DBEAFE")],
                  foreground=[("selected",DARK_TEXT)])

        tree = ttk.Treeview(parent, columns=cols, show="headings",
                             style="B.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=widths.get(c,100),
                         anchor="center" if c in ("ID","Alerta","En servicio") else "w")

        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return tree

    def _msg(self, texto):
        for tab, tree in [(self.tab_inc, self.tree_inc),
                          (self.tab_per, self.tree_per),
                          (self.tab_veh, self.tree_veh),
                          (self.tab_uni, self.tree_uni)]:
            for i in tree.get_children():
                tree.delete(i)

    def _on_key(self, e=None):
        if self._debounce:
            self.after_cancel(self._debounce)
        self._debounce = self.after(400, self._buscar)

    def _buscar(self):
        q = self.ent.get().strip()
        if len(q) < 2:
            self._msg("Escribe al menos 2 caracteres para buscar.")
            return

        like = f"%{q}%"
        conn = get_connection()
        c    = conn.cursor()

        n_inc = n_per = n_veh = n_uni = 0

        # Incidentes
        for i in self.tree_inc.get_children():
            self.tree_inc.delete(i)
        if self._vars["Incidentes"].get():
            c.execute("""
                SELECT id,tipo,descripcion,fecha,zona,estado FROM incidentes
                WHERE tipo LIKE ? OR descripcion LIKE ? OR zona LIKE ? OR direccion LIKE ?
                ORDER BY fecha DESC LIMIT 50
            """, (like,like,like,like))
            for row in c.fetchall():
                desc = row[2][:55]+"…" if len(row[2])>55 else row[2]
                est  = "✅ Finalizado" if row[5]=="Finalizado" else "🚨 Activo"
                self.tree_inc.insert("","end",values=(row[0],row[1],desc,row[3],row[4],est))
                n_inc += 1

        # Personas
        for i in self.tree_per.get_children():
            self.tree_per.delete(i)
        if self._vars["Personas"].get():
            c.execute("""
                SELECT id,nombre,apellidos,dni,telefono FROM personas
                WHERE nombre LIKE ? OR apellidos LIKE ? OR dni LIKE ? OR telefono LIKE ?
                ORDER BY apellidos LIMIT 50
            """, (like,like,like,like))
            for row in c.fetchall():
                self.tree_per.insert("","end",
                                      values=(row[0],row[1],row[2] or "—",
                                              row[3] or "—",row[4] or "—"))
                n_per += 1

        # Vehículos
        for i in self.tree_veh.get_children():
            self.tree_veh.delete(i)
        if self._vars["Vehículos"].get():
            c.execute("""
                SELECT id,matricula,marca,modelo,color,propietario,alerta FROM vehiculos
                WHERE matricula LIKE ? OR marca LIKE ? OR modelo LIKE ? OR propietario LIKE ?
                ORDER BY matricula LIMIT 50
            """, (like,like,like,like))
            for row in c.fetchall():
                tag    = "alerta" if row[6] else ""
                alerta = "🚨 SÍ" if row[6] else "—"
                self.tree_veh.insert("","end",iid=None,
                                      values=(row[0],row[1],row[2] or "—",
                                              row[3] or "—",row[4] or "—",
                                              row[5] or "—",alerta),
                                      tags=(tag,))
                n_veh += 1

        # Unidades
        for i in self.tree_uni.get_children():
            self.tree_uni.delete(i)
        if self._vars["Unidades"].get():
            c.execute("""
                SELECT id,indicativo,estado,en_servicio,ubicacion_actual FROM unidades
                WHERE indicativo LIKE ? OR estado LIKE ? OR ubicacion_actual LIKE ?
                ORDER BY indicativo LIMIT 50
            """, (like,like,like))
            for row in c.fetchall():
                srv = "✅ Sí" if row[3] else "❌ No"
                self.tree_uni.insert("","end",
                                      values=(row[0],row[1],row[2] or "—",
                                              srv, row[4] or "—"))
                n_uni += 1

        conn.close()

        # Actualizar contadores de pestañas
        self.nb.tab(self.tab_inc, text=f"  📋 Incidentes ({n_inc})  ")
        self.nb.tab(self.tab_per, text=f"  👤 Personas ({n_per})  ")
        self.nb.tab(self.tab_veh, text=f"  🚗 Vehículos ({n_veh})  ")
        self.nb.tab(self.tab_uni, text=f"  🚓 Unidades ({n_uni})  ")

        # Ir a la pestaña con más resultados
        maximos = [(n_inc,0),(n_per,1),(n_veh,2),(n_uni,3)]
        mejor   = max(maximos, key=lambda x: x[0])
        if mejor[0] > 0:
            self.nb.select(mejor[1])
