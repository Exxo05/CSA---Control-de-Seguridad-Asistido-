# gui/screens/personas.py — Registro de personas v1.0
# PREPARADO PARA USO REAL: conecta a BD local.
# AMPLIACIÓN FUTURA: conectar a BDD Policía (BNIPJ, etc.) via API cuando se disponga de acceso.
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from servicios.db     import get_connection, registrar_auditoria
from servicios.sesion import uid as sesion_uid
from servicios.eventos import suscribir, desuscribir
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    BAJA_BG, BAJA_FG, CRITICA_BG, CRITICA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

ROLES_INCIDENTE = ["implicado", "denunciante", "testigo", "víctima", "investigado", "detenido"]
NACIONALIDADES  = ["Española","Marroquí","Rumana","Colombiana","Ecuatoriana",
                   "Venezolana","Peruana","China","Italiana","Francesa","Otra"]


class PersonasScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._viva = True
        self._build()
        self.bind("<Destroy>", lambda e: setattr(self, "_viva", False))

    def _build(self):
        make_header(self, "👤  Registro de Personas")

        # Aviso estado
        aviso = tk.Frame(self, bg="#EFF6FF",
                         highlightbackground="#BFDBFE", highlightthickness=1)
        aviso.pack(fill="x", padx=PAD_X, pady=(8,0))
        tk.Label(aviso,
                 text="ℹ️  Base de datos local. Ampliación futura: integración con BNIPJ/BDD Policía Nacional.",
                 font=FONT_SMALL, bg="#EFF6FF", fg="#1D4ED8",
                 pady=6, padx=12).pack(anchor="w")

        # Toolbar
        tb = tk.Frame(self, bg=WHITE,
                      highlightbackground=GRAY_BORDER, highlightthickness=1)
        tb.pack(fill="x", padx=PAD_X, pady=(8,0))
        inner = tk.Frame(tb, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)

        tk.Label(inner, text="🔍", font=("Segoe UI",11),
                 bg=WHITE, fg=GRAY_TEXT).pack(side="left")
        self.ent_buscar = tk.Entry(inner, font=FONT_NORMAL,
                                    relief="solid", bd=1, bg=WHITE, width=30)
        self.ent_buscar.pack(side="left", padx=(4,12), ipady=4)
        self.ent_buscar.bind("<KeyRelease>", lambda e: self._filtrar())

        make_button(inner, "➕ Nueva persona", self._nueva,  "success").pack(side="left", padx=3)
        make_button(inner, "✏️ Editar",         self._editar, "warning").pack(side="left", padx=3)
        make_button(inner, "🔍 Ver incidentes", self._ver_incidentes, "info").pack(side="left", padx=3)
        make_button(inner, "🗑️ Eliminar",       self._eliminar, "danger").pack(side="left", padx=3)
        make_button(inner, "🔄 Refrescar",      self._cargar, "neutral").pack(side="left", padx=3)

        self.lbl_total = tk.Label(inner, text="", font=FONT_SMALL,
                                   bg=WHITE, fg=GRAY_TEXT)
        self.lbl_total.pack(side="right")

        # Tabla
        tree_frame = tk.Frame(self, bg=GRAY_BG)
        tree_frame.pack(fill="both", expand=True, padx=PAD_X, pady=10)

        style = ttk.Style()
        style.configure("P.Treeview", font=FONT_NORMAL, rowheight=28,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("P.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE,
                         relief="flat", padding=(8,5))
        style.map("P.Treeview",
                  background=[("selected","#DBEAFE")],
                  foreground=[("selected", DARK_TEXT)])

        cols = ("ID","Nombre","Apellidos","DNI","Fecha Nac.","Nacionalidad",
                "Teléfono","Incidentes")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", style="P.Treeview")
        widths = {"ID":45,"Nombre":140,"Apellidos":160,"DNI":100,
                  "Fecha Nac.":95,"Nacionalidad":110,"Teléfono":110,"Incidentes":80}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c],
                              anchor="center" if c in ("ID","Incidentes") else "w")

        sb_v = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(tree_frame, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.pack(side="right", fill="y")
        sb_h.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._editar())

        self._datos = []
        self._cargar()

    def _cargar(self):
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT p.id, p.nombre, p.apellidos, p.dni, p.fecha_nac,
                   p.nacionalidad, p.telefono,
                   COUNT(pi.incidente_id) as n_inc
            FROM personas p
            LEFT JOIN personas_incidentes pi ON pi.persona_id = p.id
            GROUP BY p.id ORDER BY p.apellidos, p.nombre
        """)
        self._datos = c.fetchall()
        conn.close()
        self._filtrar()

    def _filtrar(self):
        q = self.ent_buscar.get().lower().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        n = 0
        for row in self._datos:
            if q and not any(q in str(v).lower() for v in row):
                continue
            n_inc = row[7] or 0
            tag   = "con_inc" if n_inc > 0 else ""
            self.tree.insert("", "end", iid=str(row[0]),
                              values=(row[0], row[1], row[2] or "—",
                                      row[3] or "—", row[4] or "—",
                                      row[5] or "—", row[6] or "—",
                                      f"📋 {n_inc}" if n_inc else "—"),
                              tags=(tag,))
            n += 1
        self.tree.tag_configure("con_inc", background="#EFF6FF")
        self.lbl_total.config(text=f"{n} personas")

    def _sel_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección","Seleccione una persona.")
            return None
        return int(self.tree.item(sel[0],"values")[0])

    def _nueva(self):
        FormPersona(self, on_save=self._cargar)

    def _editar(self):
        pid = self._sel_id()
        if pid is None: return
        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT * FROM personas WHERE id=?", (pid,))
        row = c.fetchone()
        conn.close()
        if row:
            FormPersona(self, datos=row, on_save=self._cargar)

    def _eliminar(self):
        pid = self._sel_id()
        if pid is None: return
        if messagebox.askyesno("Confirmar","¿Eliminar esta persona? Se desvinculará de todos los incidentes."):
            conn = get_connection()
            conn.execute("DELETE FROM personas WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            registrar_auditoria(sesion_uid(), "ELIMINAR_PERSONA", "personas", pid)
            self._cargar()

    def _ver_incidentes(self):
        pid = self._sel_id()
        if pid is None: return
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT i.id, i.tipo, i.fecha, i.zona, pi.rol
            FROM incidentes i
            JOIN personas_incidentes pi ON pi.incidente_id=i.id
            WHERE pi.persona_id=?
            ORDER BY i.fecha DESC
        """, (pid,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("Sin incidentes","Esta persona no tiene incidentes asociados.")
            return
        txt = "\n".join(
            f"#{r[0]} [{r[4].upper()}]  {r[1][:35]}  —  {r[3]}  ({r[2][:10]})"
            for r in rows
        )
        messagebox.showinfo(f"Incidentes de la persona #{pid}", txt)


class FormPersona(tk.Toplevel):
    def __init__(self, parent, datos=None, on_save=None):
        super().__init__(parent)
        self.title("Nueva persona" if datos is None else "Editar persona")
        self.geometry("540x600")
        self.minsize(480, 500)
        self.configure(bg=WHITE)
        self.resizable(True, True)
        self.grab_set()
        self._datos   = datos
        self._on_save = on_save
        self._build()
        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 540) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"540x600+{x}+{y}")

    def _build(self):
        # Cabecera fija
        hdr = tk.Frame(self, bg=POLICE_BLUE)
        hdr.pack(fill="x")
        tk.Label(hdr, text="👤  Datos de la persona",
                 font=FONT_SUBTITLE, bg=POLICE_BLUE, fg=WHITE,
                 pady=10, padx=20).pack(anchor="w")

        # Área scrollable
        canvas = tk.Canvas(self, bg=WHITE, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.inner = tk.Frame(canvas, bg=WHITE)
        win_id = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())
        self.inner.bind("<Configure>", _resize)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind("<Enter>",
                    lambda e: canvas.bind_all("<MouseWheel>",
                        lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)),"units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        pad = tk.Frame(self.inner, bg=WHITE)
        pad.pack(fill="x", padx=24, pady=16)

        def campo(lbl, val="", ancho=None):
            tk.Label(pad, text=lbl, font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
            e = tk.Entry(pad, font=FONT_NORMAL, relief="solid", bd=1, bg=WHITE,
                         width=ancho or 44)
            e.insert(0, val or "")
            e.pack(fill="x" if not ancho else None, ipady=6, pady=(2,10), anchor="w")
            return e

        d = self._datos
        self.e_nombre = campo("Nombre *",                    d[1] if d else "")
        self.e_apell  = campo("Apellidos",                   d[2] if d else "")
        self.e_dni    = campo("DNI / NIE",                   d[3] if d else "", ancho=14)
        self.e_fnac   = campo("Fecha de nacimiento (YYYY-MM-DD)", d[4] if d else "")
        self.e_tel    = campo("Teléfono",                    d[6] if d else "", ancho=16)
        self.e_dom    = campo("Domicilio",                   d[7] if d else "")

        tk.Label(pad, text="Nacionalidad", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.combo_nac = ttk.Combobox(pad, values=NACIONALIDADES,
                                       font=FONT_NORMAL, width=22)
        self.combo_nac.set(d[5] if d and d[5] else "Española")
        self.combo_nac.pack(anchor="w", pady=(2,10))

        tk.Label(pad, text="Notas / antecedentes", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.txt_notas = tk.Text(pad, height=4, font=FONT_NORMAL,
                                  relief="solid", bd=1, bg=WHITE, wrap="word")
        self.txt_notas.insert("1.0", d[8] if d and d[8] else "")
        self.txt_notas.pack(fill="x", pady=(2,0))

        # Botón guardar fuera del scroll (siempre visible)
        btn_frame = tk.Frame(self, bg=WHITE,
                             highlightbackground="#DDE3ED", highlightthickness=1)
        btn_frame.pack(fill="x", side="bottom")
        make_button(btn_frame, "💾  Guardar persona",
                    self._guardar, "success").pack(fill="x", padx=20, pady=12)

    def _guardar(self):
        nombre = self.e_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Campo requerido","El nombre es obligatorio.")
            return
        datos = (
            nombre,
            self.e_apell.get().strip() or None,
            self.e_dni.get().strip().upper() or None,
            self.e_fnac.get().strip() or None,
            self.combo_nac.get() or "Española",
            self.e_tel.get().strip() or None,
            self.e_dom.get().strip() or None,
            self.txt_notas.get("1.0","end").strip() or None,
        )
        conn = get_connection()
        try:
            if self._datos:
                conn.execute("""
                    UPDATE personas SET nombre=?,apellidos=?,dni=?,fecha_nac=?,
                    nacionalidad=?,telefono=?,domicilio=?,notas=? WHERE id=?
                """, (*datos, self._datos[0]))
                registrar_auditoria(sesion_uid(),"EDITAR_PERSONA","personas",self._datos[0])
            else:
                conn.execute("""
                    INSERT INTO personas
                    (nombre,apellidos,dni,fecha_nac,nacionalidad,telefono,domicilio,notas,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (*datos, datetime.now().isoformat()))
                registrar_auditoria(sesion_uid(),"CREAR_PERSONA","personas")
            conn.commit()
        finally:
            conn.close()
        self.destroy()
        if self._on_save:
            self.after(50, self._on_save)
