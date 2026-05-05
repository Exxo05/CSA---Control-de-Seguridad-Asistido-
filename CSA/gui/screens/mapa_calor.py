import tkinter as tk
import webbrowser
import os
from mapas.mapa_calor import crear_mapa_calor

class MapaCalorScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        tk.Label(self, text="🔥 Análisis de Puntos Calientes", font=("Arial", 16, "bold")).pack(pady=20)
        
        btn = tk.Button(self, text="ABRIR MAPA DE CALOR", font=("Arial", 12, "bold"), 
                        bg="#e74c3c", fg="white", padx=20, pady=10, command=self.abrir_en_navegador)
        btn.pack(pady=20)

    def abrir_en_navegador(self):
        mapa_obj = crear_mapa_calor()
        ruta_html = os.path.abspath("temp_calor.html")
        mapa_obj.save(ruta_html)
        webbrowser.open(f"file:///{ruta_html}")