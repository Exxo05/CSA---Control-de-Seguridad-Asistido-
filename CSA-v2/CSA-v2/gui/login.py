# gui/login.py — Pantalla de login
import tkinter as tk
from tkinter import messagebox
from servicios.db     import verificar_usuario
from servicios.sesion import iniciar_sesion
from gui.styles import (
    POLICE_BLUE, POLICE_BLUE_LIGHT, WHITE, GRAY_BG, GRAY_BORDER,
    DARK_TEXT, GRAY_TEXT, FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL,
    FONT_SMALL, make_button
)

TURNOS = ["Mañana (06-14h)", "Tarde (14-22h)", "Noche (22-06h)"]

class LoginWindow(tk.Tk):
    """Ventana de login que precede a MainWindow."""

    def __init__(self):
        super().__init__()
        self.title("CSA — Acceso al sistema")
        self.geometry("420x560")
        self.resizable(False, False)
        self.configure(bg=POLICE_BLUE)
        self._autenticado = False
        self._build()
        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 420) // 2
        y = (self.winfo_screenheight() - 560) // 2
        self.geometry(f"420x560+{x}+{y}")
        # Enter = login
        self.bind("<Return>", lambda e: self._login())

    def _build(self):
        # Cabecera azul
        hdr = tk.Frame(self, bg=POLICE_BLUE)
        hdr.pack(fill="x", pady=(40, 0))
        tk.Label(hdr, text="🛡️", font=("Segoe UI", 48),
                 bg=POLICE_BLUE, fg=WHITE).pack()
        tk.Label(hdr, text="CSA", font=("Segoe UI", 24, "bold"),
                 bg=POLICE_BLUE, fg=WHITE).pack()
        tk.Label(hdr, text="Control de Seguridad Asistido",
                 font=("Segoe UI", 10), bg=POLICE_BLUE, fg="#94A3B8").pack()
        tk.Label(hdr, text="Policía Local — Alcalá de Henares",
                 font=("Segoe UI", 9), bg=POLICE_BLUE, fg="#64748B").pack(pady=(2,0))

        # Tarjeta blanca
        card = tk.Frame(self, bg=WHITE,
                        highlightbackground=GRAY_BORDER, highlightthickness=1)
        card.pack(fill="x", padx=32, pady=32)

        inner = tk.Frame(card, bg=WHITE)
        inner.pack(fill="x", padx=28, pady=24)

        tk.Label(inner, text="Identificación del operador",
                 font=FONT_SUBTITLE, bg=WHITE, fg=DARK_TEXT).pack(anchor="w", pady=(0,16))

        # Usuario
        tk.Label(inner, text="Usuario", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        self.ent_user = tk.Entry(inner, font=FONT_NORMAL,
                                  relief="solid", bd=1, bg=WHITE)
        self.ent_user.pack(fill="x", ipady=7, pady=(2, 12))
        self.ent_user.focus()

        # Contraseña
        tk.Label(inner, text="Contraseña", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        pwd_row = tk.Frame(inner, bg=WHITE)
        pwd_row.pack(fill="x", pady=(2, 12))
        self.ent_pwd = tk.Entry(pwd_row, font=FONT_NORMAL,
                                 relief="solid", bd=1, bg=WHITE, show="•")
        self.ent_pwd.pack(side="left", fill="x", expand=True, ipady=7)
        self._mostrar_pwd = False
        tk.Button(pwd_row, text="👁", font=("Segoe UI", 10),
                  bg=WHITE, relief="flat", cursor="hand2",
                  command=self._toggle_pwd).pack(side="left", padx=(4,0))

        # Turno
        tk.Label(inner, text="Turno", font=FONT_SMALL,
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")
        from tkinter import ttk
        from datetime import datetime as dt
        self.combo_turno = ttk.Combobox(inner, values=TURNOS,
                                         state="readonly", font=FONT_NORMAL)
        h = dt.now().hour
        self.combo_turno.current(0 if 6<=h<14 else 1 if 14<=h<22 else 2)
        self.combo_turno.pack(fill="x", pady=(2, 16))

        # Mensaje de error
        self.lbl_error = tk.Label(inner, text="", font=FONT_SMALL,
                                   bg=WHITE, fg="#DC2626")
        self.lbl_error.pack(fill="x")

        make_button(inner, "🔐  ACCEDER AL SISTEMA",
                    self._login, "primary").pack(fill="x", pady=(8,0))

        # Credenciales por defecto (solo en desarrollo)
        tk.Label(card, text="Usuarios por defecto: admin/admin123 — operador/csa2025",
                 font=("Segoe UI", 8), bg=WHITE, fg=GRAY_TEXT).pack(pady=(0,12))

    def _toggle_pwd(self):
        self._mostrar_pwd = not self._mostrar_pwd
        self.ent_pwd.config(show="" if self._mostrar_pwd else "•")

    def _login(self):
        usuario = self.ent_user.get().strip()
        pwd     = self.ent_pwd.get()
        turno   = self.combo_turno.get()

        if not usuario or not pwd:
            self.lbl_error.config(text="Introduce usuario y contraseña.")
            return

        u = verificar_usuario(usuario, pwd)
        if u:
            iniciar_sesion(u, turno)
            self._autenticado = True
            self.destroy()
        else:
            self.lbl_error.config(text="Usuario o contraseña incorrectos.")
            self.ent_pwd.delete(0, tk.END)
            self.ent_pwd.focus()

    def autenticado(self) -> bool:
        return self._autenticado
