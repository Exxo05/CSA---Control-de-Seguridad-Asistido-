# gui/screens/vehiculos.py — Registro de vehículos v1.0
# PREPARADO PARA USO REAL: BD local + sistema de alertas.
# AMPLIACIÓN FUTURA: consulta a DGT vía API cuando se disponga de credenciales.
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from servicios.db     import get_connection, registrar_auditoria
from servicios.sesion import uid as sesion_uid
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    CRITICA_BG, CRITICA_FG, ALTA_BG, ALTA_FG, BAJA_BG, BAJA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

TIPOS_VEHICULO = ["Turismo","Furgoneta","Camión","Moto","Ciclomotor",
                  "Autobús","Bicicleta","Patinete","Otro"]
COLORES_COMUNES = ["Blanco","Negro","Gris","Rojo","Azul","Verde",
                   "Amarillo","Naranja","Marrón","Plata","Otro"]


class VehiculosScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._viva = True
        self._build()
        self.bind("<Destroy>", lambda e: setattr(self, "_viva", False))

    def _build(self):
        make_header(self, "🚗  Registro de Vehículos")

        aviso = tk.Frame(self, bg="#EFF6FF",
                         highlightbackground="#BFDBFE", highlightthickness=1)
        aviso.pack(fill="x", padx=PAD_X, pady=(8,0))
        tk.Label(aviso,
                 text="ℹ️  Base de datos local con sistema de alertas. "
                      "Ampliación futura: consulta automática a DGT.",
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
                                    relief="solid", bd=1, bg=WHITE, width=24)
        self.ent_buscar.pack(side="left", padx=(4,4), ipady=4)
        self.ent_buscar.bind("<KeyRelease>", lambda e: self._filtrar())
        self.ent_buscar.insert(0, "Matrícula, marca o propietario…")
        self.ent_buscar.config(fg=GRAY_TEXT)
        self.ent_buscar.bind("<FocusIn>",  lambda e: self._clear_ph())
        self.ent_buscar.bind("<FocusOut>", lambda e: self._restore_ph())

        # Búsqueda rápida de matrícula
        make_button(inner, "🔎 Consultar matrícula",
                    self._consulta_rapida, "primary").pack(side="left", padx=(8,3))
        make_button(inner, "➕ Añadir",    self._nuevo,   "success").pack(side="left", padx=3)
        make_button(inner, "✏️ Editar",    self._editar,  "warning").pack(side="left", padx=3)
        make_button(inner, "🚨 Alerta",    self._alerta,  "danger").pack(side="left", padx=3)
        make_button(inner, "🔄 Refrescar", self._cargar,  "neutral").pack(side="left", padx=3)

        self.lbl_total = tk.Label(inner, text="", font=FONT_SMALL,
                                   bg=WHITE, fg=GRAY_TEXT)
        self.lbl_total.pack(side="right")

        # Tabla
        tree_frame = tk.Frame(self, bg=GRAY_BG)
        tree_frame.pack(fill="both", expand=True, padx=PAD_X, pady=10)

        style = ttk.Style()
        style.configure("V.Treeview", font=FONT_NORMAL, rowheight=28,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("V.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE,
                         relief="flat", padding=(8,5))
        style.map("V.Treeview",
                  background=[("selected","#DBEAFE")],
                  foreground=[("selected",DARK_TEXT)])

        cols = ("ID","Matrícula","Marca","Modelo","Color","Tipo",
                "Propietario","Alerta","Incidentes")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", style="V.Treeview")
        widths = {"ID":40,"Matrícula":100,"Marca":100,"Modelo":100,
                  "Color":80,"Tipo":90,"Propietario":150,
                  "Alerta":80,"Incidentes":75}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c],
                              anchor="center" if c in ("ID","Alerta","Incidentes") else "w")

        self.tree.tag_configure("alerta",   background=CRITICA_BG, foreground=CRITICA_FG)
        self.tree.tag_configure("normal",   background=WHITE,       foreground=DARK_TEXT)
        self.tree.tag_configure("con_inc",  background="#EFF6FF",   foreground=DARK_TEXT)

        sb_v = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(tree_frame, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.pack(side="right", fill="y")
        sb_h.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._editar())

        self._datos = []
        self._cargar()

    def _clear_ph(self):
        if self.ent_buscar.get() == "Matrícula, marca o propietario…":
            self.ent_buscar.delete(0, tk.END)
            self.ent_buscar.config(fg=DARK_TEXT)

    def _restore_ph(self):
        if not self.ent_buscar.get():
            self.ent_buscar.insert(0, "Matrícula, marca o propietario…")
            self.ent_buscar.config(fg=GRAY_TEXT)

    def _cargar(self):
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT v.id, v.matricula, v.marca, v.modelo, v.color, v.tipo,
                   v.propietario, v.alerta, v.motivo_alerta,
                   COUNT(vi.incidente_id) as n_inc
            FROM vehiculos v
            LEFT JOIN vehiculos_incidentes vi ON vi.vehiculo_id=v.id
            GROUP BY v.id ORDER BY v.matricula
        """)
        self._datos = c.fetchall()
        conn.close()
        self._filtrar()

    def _filtrar(self):
        q = self.ent_buscar.get().lower()
        if q == "matrícula, marca o propietario…":
            q = ""
        for i in self.tree.get_children():
            self.tree.delete(i)
        n = 0
        for row in self._datos:
            if q and not any(q in str(v).lower() for v in row):
                continue
            tiene_alerta = bool(row[7])
            n_inc        = row[9] or 0
            alerta_txt   = "🚨 SÍ" if tiene_alerta else "—"
            tag = "alerta" if tiene_alerta else ("con_inc" if n_inc > 0 else "normal")
            self.tree.insert("", "end", iid=str(row[0]),
                              values=(row[0], row[1], row[2] or "—",
                                      row[3] or "—", row[4] or "—",
                                      row[5] or "—", row[6] or "—",
                                      alerta_txt,
                                      f"📋 {n_inc}" if n_inc else "—"),
                              tags=(tag,))
            n += 1
        alertas = sum(1 for r in self._datos if r[7])
        self.lbl_total.config(
            text=f"{n} vehículos  |  🚨 {alertas} con alerta")

    def _sel_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección","Seleccione un vehículo.")
            return None
        return int(self.tree.item(sel[0],"values")[0])

    def _consulta_rapida(self):
        ConsultaMatricula(self, on_resultado=self._cargar)

    def _nuevo(self):
        FormVehiculo(self, on_save=self._cargar)

    def _editar(self):
        vid = self._sel_id()
        if vid is None: return
        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT * FROM vehiculos WHERE id=?", (vid,))
        row = c.fetchone()
        conn.close()
        if row:
            FormVehiculo(self, datos=row, on_save=self._cargar)

    def _alerta(self):
        vid = self._sel_id()
        if vid is None: return
        # Toggle alerta
        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT alerta, matricula FROM vehiculos WHERE id=?", (vid,))
        row = c.fetchone()
        if row:
            nueva = 0 if row[0] else 1
            if nueva:
                motivo = tk.simpledialog.askstring(
                    "Motivo de alerta",
                    f"Motivo de alerta para {row[1]}:",
                    parent=self) or "Sin especificar"
            else:
                motivo = None
            conn.execute("UPDATE vehiculos SET alerta=?, motivo_alerta=? WHERE id=?",
                         (nueva, motivo, vid))
            conn.commit()
            registrar_auditoria(sesion_uid(),
                                f"{'ACTIVAR' if nueva else 'DESACTIVAR'}_ALERTA_VEHICULO",
                                "vehiculos", vid, motivo)
        conn.close()
        self._cargar()


class ConsultaMatricula(tk.Toplevel):
    """Búsqueda rápida de matrícula — preparada para DGT."""
    def __init__(self, parent, on_resultado=None):
        super().__init__(parent)
        self.title("Consulta rápida de matrícula")
        self.geometry("480x360")
        self.configure(bg=WHITE, padx=24, pady=20)
        self.resizable(False, False)
        self.grab_set()
        self._on_resultado = on_resultado
        self._build()

    def _build(self):
        tk.Label(self, text="🔎  Consulta de Matrícula",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE).pack(anchor="w", pady=(0,12))

        row = tk.Frame(self, bg=WHITE)
        row.pack(fill="x", pady=(0,8))
        self.ent_mat = tk.Entry(row, font=("Segoe UI",16,"bold"),
                                 relief="solid", bd=2, bg=WHITE, width=12,
                                 justify="center")
        self.ent_mat.pack(side="left", ipady=8)
        self.ent_mat.bind("<Return>", lambda e: self._buscar())
        make_button(row, "CONSULTAR", self._buscar, "primary").pack(side="left", padx=8)
        self.ent_mat.focus()

        self.frame_resultado = tk.Frame(self, bg=WHITE)
        self.frame_resultado.pack(fill="x", pady=12)

        # Aviso DGT
        av = tk.Frame(self, bg="#FAEEDA",
                      highlightbackground="#FCD34D", highlightthickness=1)
        av.pack(fill="x")
        tk.Label(av,
                 text="⚠️  Consulta a base de datos local.\n"
                      "Integración DGT disponible cuando se proporcionen credenciales de acceso.\n"
                      "Configura en ⚙️ Configuración → DGT API.",
                 font=("Segoe UI",8), bg="#FAEEDA", fg="#92400E",
                 justify="center", pady=8).pack()

    def _buscar(self):
        mat = self.ent_mat.get().strip().upper().replace(" ","").replace("-","")
        if not mat:
            return
        for w in self.frame_resultado.winfo_children():
            w.destroy()

        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT v.*, COUNT(vi.incidente_id) as n_inc
            FROM vehiculos v
            LEFT JOIN vehiculos_incidentes vi ON vi.vehiculo_id=v.id
            WHERE REPLACE(REPLACE(UPPER(v.matricula),'-',''),' ','')=?
            GROUP BY v.id
        """, (mat,))
        row = c.fetchone()
        conn.close()

        fr = self.frame_resultado
        if row:
            color_bg = CRITICA_BG if row[8] else BAJA_BG
            color_fg = CRITICA_FG if row[8] else BAJA_FG
            tk.Frame(fr, bg=color_bg, padx=14, pady=10).pack(fill="x")
            info_fr = tk.Frame(fr, bg=color_bg, padx=14, pady=10)
            info_fr.pack(fill="x")

            def lbl(text, bold=False):
                tk.Label(info_fr, text=text,
                         font=("Segoe UI",10,"bold" if bold else "normal"),
                         bg=color_bg, fg=color_fg, anchor="w").pack(fill="x")

            lbl(f"🚗 {row[1]}  —  {row[2] or '?'} {row[3] or ''}", bold=True)
            lbl(f"Color: {row[4] or '—'}   Tipo: {row[5] or '—'}")
            lbl(f"Propietario: {row[6] or '—'}")
            lbl(f"Incidentes previos: {row[10] or 0}")
            if row[8]:
                lbl(f"🚨 ALERTA: {row[9]}", bold=True)
        else:
            tk.Label(fr,
                     text=f"✅  Matrícula {mat} no encontrada en base de datos local.",
                     font=FONT_NORMAL, bg=WHITE, fg="#059669",
                     pady=12).pack()
            make_button(fr, "➕ Registrar este vehículo",
                        lambda: (self.destroy(),
                                 FormVehiculo(self.master,
                                             datos_mat=mat,
                                             on_save=self._on_resultado)),
                        "success").pack(pady=4)


class FormVehiculo(tk.Toplevel):
    def __init__(self, parent, datos=None, datos_mat=None, on_save=None):
        super().__init__(parent)
        self.title("Nuevo vehículo" if datos is None else "Editar vehículo")
        self.geometry("500x520")
        self.minsize(460, 460)
        self.configure(bg=WHITE, padx=24, pady=20)
        self.resizable(True, True)
        self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 500) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"500x520+{x}+{y}")
        self._datos   = datos
        self._on_save = on_save
        self._mat_ini = datos_mat or ""
        self._build()

    def _build(self):
        tk.Label(self, text="🚗  Datos del vehículo",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE).pack(anchor="w", pady=(0,12))

        def campo(lbl, val="", ancho=None):
            tk.Label(self, text=lbl, font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
            e = tk.Entry(self, font=FONT_NORMAL, relief="solid", bd=1, bg=WHITE,
                         width=ancho or 44)
            e.insert(0, val or "")
            e.pack(fill="x" if not ancho else None, ipady=5, pady=(2,8), anchor="w")
            return e

        d = self._datos
        self.e_mat   = campo("Matrícula *",   d[1] if d else self._mat_ini, ancho=14)
        self.e_marca = campo("Marca",          d[2] if d else "")
        self.e_mod   = campo("Modelo",         d[3] if d else "")
        self.e_prop  = campo("Propietario",    d[6] if d else "")
        self.e_notas = campo("Notas",          d[7] if d else "")

        row = tk.Frame(self, bg=WHITE)
        row.pack(fill="x", pady=(0,8))

        c1 = tk.Frame(row, bg=WHITE)
        c1.pack(side="left", expand=True, fill="x", padx=(0,8))
        tk.Label(c1, text="Color", font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.combo_col = ttk.Combobox(c1, values=COLORES_COMUNES, font=FONT_NORMAL, width=14)
        self.combo_col.set(d[4] if d and d[4] else "Blanco")
        self.combo_col.pack(anchor="w")

        c2 = tk.Frame(row, bg=WHITE)
        c2.pack(side="left", expand=True, fill="x")
        tk.Label(c2, text="Tipo", font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.combo_tipo = ttk.Combobox(c2, values=TIPOS_VEHICULO, font=FONT_NORMAL, width=14)
        self.combo_tipo.set(d[5] if d and d[5] else "Turismo")
        self.combo_tipo.pack(anchor="w")

        # Separador y botón siempre visible al fondo
        tk.Frame(self, bg="#DDE3ED", height=1).pack(fill="x", pady=(12,0))
        make_button(self, "💾  Guardar", self._guardar, "success").pack(fill="x", pady=(8,0))

    def _guardar(self):
        mat = self.e_mat.get().strip().upper()
        if not mat:
            messagebox.showwarning("Campo requerido","La matrícula es obligatoria.")
            return
        datos = (mat, self.e_marca.get().strip() or None,
                 self.e_mod.get().strip() or None,
                 self.combo_col.get() or None,
                 self.combo_tipo.get() or None,
                 self.e_prop.get().strip() or None,
                 self.e_notas.get().strip() or None)
        conn = get_connection()
        try:
            if self._datos:
                conn.execute("""
                    UPDATE vehiculos SET matricula=?,marca=?,modelo=?,
                    color=?,tipo=?,propietario=?,notas=? WHERE id=?
                """, (*datos, self._datos[0]))
                registrar_auditoria(sesion_uid(),"EDITAR_VEHICULO","vehiculos",self._datos[0])
            else:
                conn.execute("""
                    INSERT INTO vehiculos
                    (matricula,marca,modelo,color,tipo,propietario,notas,created_at)
                    VALUES (?,?,?,?,?,?,?,?)
                """, (*datos, datetime.now().isoformat()))
                registrar_auditoria(sesion_uid(),"CREAR_VEHICULO","vehiculos")
            conn.commit()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            conn.close()
            return
        conn.close()
        self.destroy()
        if self._on_save:
            self._on_save()

import tkinter.simpledialog
