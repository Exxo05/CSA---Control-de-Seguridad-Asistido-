import tkinter as tk
from tkinter import messagebox
from servicios.incidentes import clasificar_tipo_incidente
from servicios.geo_logic import obtener_zona_por_direccion # Importamos el mapeador
from servicios.db import get_connection
from datetime import datetime

class RegistrarScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        tk.Label(self, text="🚨 REGISTRO OPERATIVO AUTOMÁTICO", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Dirección en Alcalá de Henares:").pack(anchor="w", padx=20)
        self.direccion_entry = tk.Entry(self)
        self.direccion_entry.pack(fill="x", padx=20, pady=5)

        tk.Label(self, text="Descripción de los hechos:").pack(anchor="w", padx=20)
        self.descripcion_text = tk.Text(self, height=5)
        self.descripcion_text.pack(fill="x", padx=20, pady=5)

        tk.Button(self, text="REGISTRAR INCIDENTE", bg="#1c2b46", fg="white", 
                  command=self.registrar, font=("Arial", 10, "bold")).pack(pady=20)

    def registrar(self):
        direccion = self.direccion_entry.get().strip()
        descripcion = self.descripcion_text.get("1.0", tk.END).strip()

        if not direccion or not descripcion:
            messagebox.showwarning("Error", "Rellene todos los campos.")
            return

        # 1. Detección automática de Zona y Clasificación Legal
        zona = obtener_zona_por_direccion(direccion)
        tipo_legal = clasificar_tipo_incidente(descripcion)
        fecha = datetime.now().strftime("%H:%M:%S")

        # 2. Guardado en DB (Asegurando que pasamos TODOS los campos)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # Añadimos 'direccion' al INSERT para evitar el IntegrityError
            cursor.execute("""
                INSERT INTO incidentes (tipo, descripcion, fecha, zona, direccion) 
                VALUES (?, ?, ?, ?, ?)
            """, (tipo_legal, descripcion, fecha, zona, direccion))
            conn.commit()
            messagebox.showinfo("Éxito", f"Registrado en {zona}\nCategoría: {tipo_legal}")
        except Exception as e:
            messagebox.showerror("Error de DB", f"No se pudo guardar: {e}")
        finally:
            conn.close() # Vital cerrar para evitar 'database is locked'

        self.direccion_entry.delete(0, tk.END)
        self.descripcion_text.delete("1.0", tk.END)