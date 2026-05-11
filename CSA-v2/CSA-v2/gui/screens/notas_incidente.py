# gui/screens/notas_incidente.py — Notas internas por incidente
# Se lanza como ventana emergente desde la pantalla de Incidentes
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from servicios.db     import get_connection, registrar_auditoria
from servicios.sesion import uid as sesion_uid, nombre as sesion_nombre
from gui.styles import (
    POLICE_BLUE, WHITE, GRAY_BG, GRAY_BORDER, DARK_TEXT, GRAY_TEXT,
    BAJA_BG, BAJA_FG, FONT_NORMAL, FONT_SUBTITLE, FONT_SMALL,
    make_button, PAD_X, PAD_Y
)


class NotasIncidenteDialog(tk.Toplevel):
    def __init__(self, parent, incidente_id: int, tipo: str):
        super().__init__(parent)
        self.title(f"📝 Notas — Incidente #{incidente_id}")
        self.geometry("580x520")
        self.configure(bg=WHITE)
        self.resizable(True, True)
        self._inc_id = incidente_id
        self._build(tipo)
        self._cargar()

    def _build(self, tipo):
        # Cabecera
        hdr = tk.Frame(self, bg=POLICE_BLUE)
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text=f"📝  Notas del incidente #{self._inc_id}",
                 font=FONT_SUBTITLE, bg=POLICE_BLUE, fg=WHITE,
                 pady=10, padx=PAD_X).pack(anchor="w")
        tk.Label(hdr, text=tipo[:60], font=FONT_SMALL,
                 bg=POLICE_BLUE, fg="#94A3B8",
                 padx=PAD_X).pack(anchor="w", pady=(0,8))

        # Lista de notas existentes
        lista_frame = tk.Frame(self, bg=WHITE)
        lista_frame.pack(fill="both", expand=True, padx=PAD_X, pady=(PAD_Y,0))
        tk.Label(lista_frame, text="Historial de notas:",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")

        self.txt_historial = tk.Text(lista_frame, font=FONT_NORMAL,
                                      relief="solid", bd=1, bg="#F8FAFC",
                                      fg=DARK_TEXT, wrap="word",
                                      state="disabled", height=12)
        sb = tk.Scrollbar(lista_frame, command=self.txt_historial.yview)
        self.txt_historial.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.txt_historial.pack(fill="both", expand=True, pady=(4,0))

        # Nueva nota
        nueva_frame = tk.Frame(self, bg=WHITE,
                               highlightbackground=GRAY_BORDER, highlightthickness=1)
        nueva_frame.pack(fill="x", padx=PAD_X, pady=PAD_Y)
        tk.Label(nueva_frame,
                 text="Añadir nota:",
                 font=FONT_SMALL, bg=WHITE, fg=GRAY_TEXT,
                 padx=PAD_X, pady=6).pack(anchor="w")
        tk.Frame(nueva_frame, bg=GRAY_BORDER, height=1).pack(fill="x")

        inner = tk.Frame(nueva_frame, bg=WHITE)
        inner.pack(fill="x", padx=PAD_X, pady=PAD_Y)

        self.txt_nueva = tk.Text(inner, font=FONT_NORMAL, height=4,
                                  relief="solid", bd=1, bg=WHITE,
                                  wrap="word")
        self.txt_nueva.pack(fill="x")
        self.txt_nueva.bind("<Control-Return>", lambda e: self._guardar())

        btn_row = tk.Frame(inner, bg=WHITE)
        btn_row.pack(fill="x", pady=(8,0))
        tk.Label(btn_row, text="Ctrl+Enter para guardar",
                 font=("Segoe UI",8), bg=WHITE, fg=GRAY_TEXT).pack(side="left")
        make_button(btn_row, "💾  Guardar nota",
                    self._guardar, "success").pack(side="right")

    def _cargar(self):
        conn = get_connection()
        c    = conn.cursor()
        c.execute("""
            SELECT n.fecha, u.nombre, n.texto
            FROM notas_incidente n
            LEFT JOIN usuarios u ON u.id = n.operador_id
            WHERE n.incidente_id = ?
            ORDER BY n.fecha ASC
        """, (self._inc_id,))
        notas = c.fetchall()
        conn.close()

        self.txt_historial.config(state="normal")
        self.txt_historial.delete("1.0", tk.END)

        if not notas:
            self.txt_historial.insert("1.0",
                "Sin notas aún. Añade la primera nota a continuación.")
        else:
            for fecha, operador, texto in notas:
                hora = fecha[11:19] if fecha else "—"
                dia  = fecha[:10]   if fecha else "—"
                self.txt_historial.insert(tk.END,
                    f"[{dia} {hora}] {operador or 'Sistema'}\n"
                    f"{texto}\n"
                    f"{'─'*50}\n")

        self.txt_historial.config(state="disabled")
        self.txt_historial.see(tk.END)

    def _guardar(self):
        texto = self.txt_nueva.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Vacío","Escribe algo antes de guardar.")
            return
        conn = get_connection()
        conn.execute("""
            INSERT INTO notas_incidente (incidente_id, operador_id, texto, fecha)
            VALUES (?,?,?,?)
        """, (self._inc_id, sesion_uid(), texto, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        registrar_auditoria(sesion_uid(), "AÑADIR_NOTA",
                            "notas_incidente", self._inc_id)
        self.txt_nueva.delete("1.0", tk.END)
        self._cargar()
