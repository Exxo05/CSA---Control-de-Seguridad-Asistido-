# gui/screens/configuracion.py — Configuración del sistema v2.0
import tkinter as tk
from tkinter import ttk, messagebox
import json, os, webbrowser, hashlib
from datetime import datetime

from servicios.db     import get_connection, hacer_backup, registrar_auditoria
from servicios.sesion import uid as sesion_uid, es_admin
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    BAJA_BG, BAJA_FG, ALTA_BG, ALTA_FG, CRITICA_BG, CRITICA_FG,
    FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, make_header, PAD_X, PAD_Y
)

_RUTA_CONFIG = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config.json"))

def _leer():
    if os.path.exists(_RUTA_CONFIG):
        try:
            with open(_RUTA_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _guardar_cfg(cfg):
    try:
        with open(_RUTA_CONFIG, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        return str(e)

def _hash(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()


class ConfiguracionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=GRAY_BG)
        self._build()

    def _build(self):
        make_header(self, "⚙️  Configuración del Sistema")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=PAD_X, pady=12)

        self.tab_geo     = tk.Frame(nb, bg=GRAY_BG)
        self.tab_users   = tk.Frame(nb, bg=GRAY_BG)
        self.tab_sistema = tk.Frame(nb, bg=GRAY_BG)

        nb.add(self.tab_geo,     text="  🗺️  Geocodificación  ")
        nb.add(self.tab_users,   text="  👮 Usuarios  ")
        nb.add(self.tab_sistema, text="  🔧 Sistema  ")

        self._build_geo()
        self._build_users()
        self._build_sistema()

    # ── Tab Geocodificación ───────────────────────────────────────
    def _build_geo(self):
        tab = self.tab_geo

        def card(titulo, subtitulo=None):
            f = tk.Frame(tab, bg=WHITE,
                         highlightbackground=GRAY_BORDER, highlightthickness=1)
            f.pack(fill="x", padx=PAD_X, pady=(12,0))
            hdr = tk.Frame(f, bg="#F8FAFC")
            hdr.pack(fill="x")
            tk.Label(hdr, text=titulo, font=FONT_SUBTITLE,
                     bg="#F8FAFC", fg=DARK_TEXT, pady=8, padx=PAD_X).pack(anchor="w")
            if subtitulo:
                tk.Label(hdr, text=subtitulo, font=FONT_SMALL,
                         bg="#F8FAFC", fg=GRAY_TEXT, padx=PAD_X).pack(anchor="w", pady=(0,6))
            tk.Frame(f, bg=GRAY_BORDER, height=1).pack(fill="x")
            inner = tk.Frame(f, bg=WHITE)
            inner.pack(fill="x", padx=PAD_X, pady=PAD_Y)
            return inner

        # Google Maps
        g = card("🗺️  Google Maps Geocoding API",
                 "La más precisa. Gratuita hasta 40.000 geocodificaciones/mes.")
        tk.Label(g, text="GOOGLE_MAPS_API_KEY", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        row = tk.Frame(g, bg=WHITE)
        row.pack(fill="x", pady=(2,8))
        self.ent_google = tk.Entry(row, font=FONT_NORMAL, relief="solid",
                                    bd=1, bg=WHITE, show="•")
        self.ent_google.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Button(row, text="👁", font=("Segoe UI",10), bg=WHITE,
                  relief="flat", cursor="hand2",
                  command=lambda: self.ent_google.config(
                      show="" if self.ent_google.cget("show")=="•" else "•")
                  ).pack(side="left", padx=(4,0))
        make_button(g, "🌐  Obtener clave gratis",
                    lambda: webbrowser.open(
                        "https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com"),
                    "info").pack(anchor="w")
        tk.Label(g, text="Pasos: Google Cloud Console → Crear proyecto → Habilitar Geocoding API → Credenciales → Copiar clave API",
                 font=("Segoe UI",8), bg=WHITE, fg=GRAY_TEXT,
                 wraplength=580, justify="left").pack(anchor="w", pady=(6,0))

        # HERE
        h = card("📡  HERE Maps API (opcional)",
                 "250.000 geocodificaciones/mes gratuitas.")
        tk.Label(h, text="HERE_API_KEY", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        row2 = tk.Frame(h, bg=WHITE)
        row2.pack(fill="x", pady=(2,8))
        self.ent_here = tk.Entry(row2, font=FONT_NORMAL, relief="solid",
                                  bd=1, bg=WHITE, show="•")
        self.ent_here.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Button(row2, text="👁", font=("Segoe UI",10), bg=WHITE,
                  relief="flat", cursor="hand2",
                  command=lambda: self.ent_here.config(
                      show="" if self.ent_here.cget("show")=="•" else "•")
                  ).pack(side="left", padx=(4,0))
        make_button(h, "🌐  Obtener clave gratis",
                    lambda: webbrowser.open("https://developer.here.com/sign-up"),
                    "info").pack(anchor="w")

        # Estado y prueba
        est = card("📊  Estado y prueba")
        self.lbl_geo_estado = tk.Label(est, text="", font=FONT_NORMAL,
                                        bg=WHITE, fg=DARK_TEXT,
                                        anchor="w", wraplength=560, justify="left")
        self.lbl_geo_estado.pack(fill="x")
        btn_row = tk.Frame(est, bg=WHITE)
        btn_row.pack(fill="x", pady=(10,0))
        make_button(btn_row, "💾  Guardar configuración",
                    self._guardar_geo, "success").pack(side="left", padx=(0,8))
        make_button(btn_row, "🔍  Probar geocodificación",
                    self._probar_geo, "primary").pack(side="left")

        self._cargar_geo()

    def _cargar_geo(self):
        cfg = _leer()
        g = cfg.get("GOOGLE_MAPS_API_KEY","")
        h = cfg.get("HERE_API_KEY","")
        if g: self.ent_google.insert(0, g)
        if h: self.ent_here.insert(0, h)
        self._actualizar_estado_geo(cfg)

    def _actualizar_estado_geo(self, cfg=None):
        if cfg is None: cfg = _leer()
        google = cfg.get("GOOGLE_MAPS_API_KEY","")
        here   = cfg.get("HERE_API_KEY","")
        lineas = []
        if google:
            lineas.append(f"✅ Google Maps: configurada ({google[:8]}…)")
        else:
            lineas.append("⚠️  Google Maps: no configurada — se usará Photon (menor precisión)")
        if here:
            lineas.append(f"✅ HERE Maps: configurada ({here[:8]}…)")
        else:
            lineas.append("ℹ️  HERE Maps: no configurada (opcional)")
        lineas.append("\nOrden: Google → Photon/OSM → Zona aproximada")
        self.lbl_geo_estado.config(text="\n".join(lineas))

    def _guardar_geo(self):
        cfg = _leer()
        cfg["GOOGLE_MAPS_API_KEY"] = self.ent_google.get().strip()
        cfg["HERE_API_KEY"]        = self.ent_here.get().strip()
        cfg.pop("_instrucciones", None)
        r = _guardar_cfg(cfg)
        if r is True:
            try:
                import servicios.geocodificador as gc
                gc._cache.clear()
            except Exception:
                pass
            messagebox.showinfo("✅ Guardado","Configuración guardada.")
            self._actualizar_estado_geo(cfg)
        else:
            messagebox.showerror("Error", str(r))

    def _probar_geo(self):
        from servicios.geocodificador import geocodificar
        pruebas = [
            "Calle Mayor 15",
            "Calle de la Era Honda 3",
            "Calle Rio Sorbe 1",
            "Avenida de los Inventores 5",
        ]
        resultados = []
        for d in pruebas:
            lat, lon, barrio, fuente = geocodificar(d)
            if lat:
                resultados.append(f"✅ {d}\n   → {lat:.5f}, {lon:.5f} | {barrio or '—'} | {fuente}")
            else:
                resultados.append(f"❌ {d}\n   → Sin resultado")
        messagebox.showinfo("Prueba de geocodificación", "\n\n".join(resultados))

    # ── Tab Usuarios ──────────────────────────────────────────────
    def _build_users(self):
        tab = self.tab_users

        if not es_admin():
            tk.Label(tab, text="⚠️  Solo los administradores pueden gestionar usuarios.",
                     font=FONT_NORMAL, bg=GRAY_BG, fg=GRAY_TEXT).pack(pady=40)
            return

        tb = tk.Frame(tab, bg=WHITE,
                      highlightbackground=GRAY_BORDER, highlightthickness=1)
        tb.pack(fill="x", padx=PAD_X, pady=(12,0))
        inner = tk.Frame(tb, bg=WHITE)
        inner.pack(fill="x", padx=12, pady=8)
        make_button(inner, "➕ Nuevo usuario", self._nuevo_usuario, "success").pack(side="left", padx=3)
        make_button(inner, "✏️ Cambiar contraseña", self._cambiar_pwd, "warning").pack(side="left", padx=3)
        make_button(inner, "🔄 Refrescar", self._cargar_usuarios, "info").pack(side="left", padx=3)

        tree_frame = tk.Frame(tab, bg=GRAY_BG)
        tree_frame.pack(fill="both", expand=True, padx=PAD_X, pady=10)

        style = ttk.Style()
        style.configure("U2.Treeview", font=FONT_NORMAL, rowheight=28,
                         background=WHITE, fieldbackground=WHITE,
                         foreground=DARK_TEXT, borderwidth=0)
        style.configure("U2.Treeview.Heading", font=FONT_SUBTITLE,
                         background=POLICE_BLUE, foreground=WHITE,
                         relief="flat", padding=(8,5))

        cols = ("ID","Usuario","Nombre","Rol","Activo","Creado")
        self.tree_users = ttk.Treeview(tree_frame, columns=cols,
                                        show="headings", style="U2.Treeview")
        widths = {"ID":45,"Usuario":120,"Nombre":180,"Rol":100,"Activo":70,"Creado":160}
        for c in cols:
            self.tree_users.heading(c, text=c)
            self.tree_users.column(c, width=widths[c],
                                    anchor="center" if c in ("ID","Activo") else "w")
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_users.yview)
        self.tree_users.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree_users.pack(fill="both", expand=True)
        self._cargar_usuarios()

    def _cargar_usuarios(self):
        if not hasattr(self, "tree_users"): return
        for i in self.tree_users.get_children():
            self.tree_users.delete(i)
        conn = get_connection()
        c    = conn.cursor()
        c.execute("SELECT id,usuario,nombre,rol,activo,created_at FROM usuarios ORDER BY id")
        for r in c.fetchall():
            activo = "✅ Sí" if r[4] else "❌ No"
            self.tree_users.insert("","end",
                                    values=(r[0],r[1],r[2],r[3],activo,r[5][:10] if r[5] else "—"))
        conn.close()

    def _nuevo_usuario(self):
        NuevoUsuarioDialog(self, on_save=self._cargar_usuarios)

    def _cambiar_pwd(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showwarning("Sin selección","Selecciona un usuario.")
            return
        uid_sel = int(self.tree_users.item(sel[0],"values")[0])
        CambiarPwdDialog(self, uid_sel, on_save=self._cargar_usuarios)

    # ── Tab Sistema ───────────────────────────────────────────────
    def _build_sistema(self):
        tab = self.tab_sistema
        inner = tk.Frame(tab, bg=GRAY_BG)
        inner.pack(fill="x", padx=PAD_X, pady=12)

        def card_sys(titulo):
            f = tk.Frame(inner, bg=WHITE,
                         highlightbackground=GRAY_BORDER, highlightthickness=1)
            f.pack(fill="x", pady=(0,10))
            tk.Label(f, text=titulo, font=FONT_SUBTITLE,
                     bg="#F8FAFC", fg=DARK_TEXT,
                     pady=8, padx=PAD_X).pack(anchor="w", fill="x")
            tk.Frame(f, bg=GRAY_BORDER, height=1).pack(fill="x")
            i2 = tk.Frame(f, bg=WHITE)
            i2.pack(fill="x", padx=PAD_X, pady=PAD_Y)
            return i2

        # Backup
        bk = card_sys("💾  Copia de seguridad")
        tk.Label(bk,
                 text="Los backups se crean automáticamente al arrancar el programa.\n"
                      "Se guardan en datos/backups/ con retención de 30 días.",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w", pady=(0,8))
        self.lbl_bk = tk.Label(bk, text="", font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT)
        self.lbl_bk.pack(anchor="w")
        make_button(bk, "💾  Crear backup ahora", self._hacer_backup, "success").pack(anchor="w", pady=(8,0))

        # Info BD
        inf = card_sys("ℹ️  Información del sistema")
        try:
            from servicios.db import get_connection
            conn  = get_connection()
            c     = conn.cursor()
            tablas = ["incidentes","personas","vehiculos","unidades","usuarios","auditoria"]
            for t in tablas:
                c.execute(f"SELECT COUNT(*) FROM {t}")
                n = c.fetchone()[0]
                tk.Label(inf, text=f"  {t.capitalize()}: {n} registros",
                         font=FONT_SMALL, bg=WHITE, fg=DARK_TEXT, anchor="w").pack(fill="x")
            conn.close()
        except Exception as e:
            tk.Label(inf, text=str(e), font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack()

        import sys
        tk.Label(inf, text=f"\nPython: {sys.version.split()[0]}  |  CSA v2.0",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT, anchor="w").pack(fill="x", pady=(8,0))

    def _hacer_backup(self):
        from servicios.db import hacer_backup
        ruta = hacer_backup()
        if ruta:
            self.lbl_bk.config(
                text=f"✅ Backup creado: {os.path.basename(ruta)}", fg="#059669")
            messagebox.showinfo("✅ Backup", f"Copia guardada en:\n{ruta}")
        else:
            messagebox.showerror("Error","No se pudo crear el backup.")


class NuevoUsuarioDialog(tk.Toplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Nuevo usuario")
        self.geometry("400x380")
        self.configure(bg=WHITE, padx=24, pady=20)
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._build()
        self.update_idletasks()
        x = (self.winfo_screenwidth()-400)//2
        y = (self.winfo_screenheight()-380)//2
        self.geometry(f"400x380+{x}+{y}")

    def _build(self):
        tk.Label(self, text="➕  Nuevo usuario",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE).pack(anchor="w", pady=(0,14))

        def campo(lbl, show=""):
            tk.Label(self, text=lbl, font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
            e = tk.Entry(self, font=FONT_NORMAL, relief="solid", bd=1, bg=WHITE, show=show)
            e.pack(fill="x", ipady=6, pady=(2,10))
            return e

        self.e_usuario = campo("Usuario")
        self.e_nombre  = campo("Nombre completo")
        self.e_pwd     = campo("Contraseña", show="•")
        self.e_pwd2    = campo("Repetir contraseña", show="•")

        tk.Label(self, text="Rol", font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.combo_rol = ttk.Combobox(self, values=["operador","supervisor","admin"],
                                       state="readonly", font=FONT_NORMAL)
        self.combo_rol.current(0)
        self.combo_rol.pack(anchor="w", pady=(2,16))

        make_button(self, "✅  Crear usuario", self._crear, "success").pack(fill="x")

    def _crear(self):
        usuario = self.e_usuario.get().strip().lower()
        nombre  = self.e_nombre.get().strip()
        pwd     = self.e_pwd.get()
        pwd2    = self.e_pwd2.get()
        rol     = self.combo_rol.get()

        if not usuario or not nombre or not pwd:
            messagebox.showwarning("Campos requeridos","Completa todos los campos.")
            return
        if pwd != pwd2:
            messagebox.showerror("Error","Las contraseñas no coinciden.")
            return
        if len(pwd) < 6:
            messagebox.showwarning("Contraseña corta","Mínimo 6 caracteres.")
            return

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO usuarios (usuario,hash_pwd,nombre,rol,activo,created_at)"
                " VALUES (?,?,?,?,1,?)",
                (usuario, _hash(pwd), nombre, rol, datetime.now().isoformat())
            )
            conn.commit()
            registrar_auditoria(sesion_uid(),"CREAR_USUARIO","usuarios",None,usuario)
            messagebox.showinfo("✅ Creado",f"Usuario «{usuario}» creado correctamente.")
            self.destroy()
            if self._on_save: self._on_save()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()


class CambiarPwdDialog(tk.Toplevel):
    def __init__(self, parent, uid_sel, on_save=None):
        super().__init__(parent)
        self.title("Cambiar contraseña")
        self.geometry("360x260")
        self.configure(bg=WHITE, padx=24, pady=20)
        self.resizable(False, False)
        self.grab_set()
        self._uid     = uid_sel
        self._on_save = on_save
        self._build()

    def _build(self):
        tk.Label(self, text="🔑  Cambiar contraseña",
                 font=FONT_SUBTITLE, bg=WHITE, fg=POLICE_BLUE).pack(anchor="w", pady=(0,14))

        def campo(lbl):
            tk.Label(self, text=lbl, font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
            e = tk.Entry(self, font=FONT_NORMAL, relief="solid", bd=1, bg=WHITE, show="•")
            e.pack(fill="x", ipady=6, pady=(2,10))
            return e

        self.e_nueva   = campo("Nueva contraseña (mínimo 6 caracteres)")
        self.e_repetir = campo("Repetir contraseña")

        make_button(self, "✅  Cambiar", self._cambiar, "success").pack(fill="x", pady=(8,0))

    def _cambiar(self):
        nueva   = self.e_nueva.get()
        repetir = self.e_repetir.get()
        if len(nueva) < 6:
            messagebox.showwarning("Error","Mínimo 6 caracteres.")
            return
        if nueva != repetir:
            messagebox.showerror("Error","Las contraseñas no coinciden.")
            return
        conn = get_connection()
        conn.execute("UPDATE usuarios SET hash_pwd=? WHERE id=?",
                     (_hash(nueva), self._uid))
        conn.commit()
        conn.close()
        registrar_auditoria(sesion_uid(),"CAMBIAR_CONTRASEÑA","usuarios",self._uid)
        messagebox.showinfo("✅","Contraseña cambiada.")
        self.destroy()
        if self._on_save: self._on_save()
