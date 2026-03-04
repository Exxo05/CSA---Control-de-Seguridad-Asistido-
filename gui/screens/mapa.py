import tkinter as tk
import webbrowser
import os
from mapas.mapa_principal import crear_mapa_principal

class MapaScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#f0f0f0")
        
        # Usamos UN SOLO archivo fijo
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.ruta_mapa = os.path.join(base_dir, "mapa_csa.html")

        tk.Label(self, text="Gestión de Mapa", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Botón para GUARDAR cambios en el archivo
        self.btn_save = tk.Button(self, text="1. GUARDAR CAMBIOS EN MAPA", bg="#3498db", fg="white", 
                                  font=("Arial", 10, "bold"), padx=10, pady=10, command=self.guardar_mapa)
        self.btn_save.pack(pady=5)

        # Botón para ABRIR el navegador (solo hace falta una vez)
        self.btn_open = tk.Button(self, text="2. ABRIR EN NAVEGADOR", bg="#2ecc71", fg="white", 
                                  padx=10, pady=10, command=self.abrir_navegador)
        self.btn_open.pack(pady=5)

        self.lbl_status = tk.Label(self, text="Instrucciones:\n1. Pulsa 'Guardar'\n2. Pulsa 'Actualizar' dentro del mapa abierto", 
                                   fg="gray", bg="#f0f0f0", justify="left")
        self.lbl_status.pack(pady=20)

    def guardar_mapa(self):
        try:
            mapa_obj = crear_mapa_principal()
            mapa_obj.save(self.ruta_mapa)
            self.lbl_status.config(text="✅ Archivo actualizado. Ahora pulsa el botón en el navegador.", fg="green")
        except Exception as e:
            print(f"Error: {e}")

    def abrir_navegador(self):
        # Abre el archivo en el navegador (si ya está abierto, el navegador suele ir a esa pestaña)
        webbrowser.open(f"file:///{self.ruta_mapa.replace('\\', '/')}")