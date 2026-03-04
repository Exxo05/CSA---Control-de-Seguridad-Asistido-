import tkinter as tk
from tkinter import ttk, messagebox
from servicios.unidades import listar_unidades, asignar_unidad_a_incidente
from servicios.incidentes import listar_incidentes

class RecomendacionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.u_data = []
        self.init_ui()

    # Método mágico para que la pantalla se refresque cada vez que entras en la pestaña
    def tkraise(self, aboveThis=None):
        self.init_ui()
        super().tkraise(aboveThis)

    def obtener_gravedad(self, tipo):
        t = tipo.upper()
        if "CRÍTICA" in t:
            return (3, "🔴 CRÍTICA: Despliegue Urgente")
        elif "ALTA" in t:
            return (2, "🟠 ALTA: Requiere Apoyo")
        elif "MEDIA" in t:
            return (1, "🟡 MEDIA: Intervención Estándar")
        else:
            return (1, "🔵 NORMAL: Patrulla Preventiva")

    def init_ui(self):
        for widget in self.winfo_children(): widget.destroy()

        tk.Label(self, text="🧠 ASISTENTE DE DESPLIEGUE OPERATIVO", 
                 font=("Arial", 16, "bold"), fg="#1c2b46").pack(pady=15)

        inc_frame = tk.LabelFrame(self, text=" 1. Seleccione Incidente Activo ", padx=15, pady=15)
        inc_frame.pack(fill="x", padx=30)

        # --- CAMBIO CLAVE AQUÍ: Filtramos por solo activos ---
        incidentes = listar_incidentes(solo_activos=True)
        
        if not incidentes:
            tk.Label(self, text="✅ No hay incidentes pendientes.\nCiudad bajo control.", 
                     font=("Arial", 12), fg="green").pack(pady=40)
            return

        self.combo_inc = ttk.Combobox(inc_frame, state="readonly", font=("Arial", 10))
        # i[0]=ID, i[1]=Tipo, i[4]=Zona, i[6]=Estado
        self.combo_inc['values'] = [f"{i[0]} | {i[1]} en {i[4]}" for i in incidentes]
        self.combo_inc.current(len(incidentes)-1)
        self.combo_inc.pack(fill="x", padx=5)
        self.combo_inc.bind("<<ComboboxSelected>>", self.actualizar_analisis)

        self.analisis_label = tk.Label(self, text="", font=("Arial", 12, "bold"), pady=10)
        self.analisis_label.pack(pady=10)

        unit_frame = tk.LabelFrame(self, text=" 2. Unidades Disponibles ", padx=15, pady=15)
        unit_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self.lista_unidades = tk.Listbox(unit_frame, selectmode="multiple", font=("Arial", 11))
        self.lista_unidades.pack(fill="both", expand=True)

        tk.Button(self, text="🚀 ENVIAR PATRULLAS", bg="#28A745", fg="white", 
                  font=("Arial", 12, "bold"), command=self.confirmar_envio).pack(pady=20)

        self.actualizar_analisis()

    def actualizar_analisis(self, event=None):
        try:
            seleccion = self.combo_inc.get()
            if not seleccion: return
            
            tipo_delito = seleccion.split(" | ")[1].split(" en ")[0].strip()
            num_necesario, texto_grav = self.obtener_gravedad(tipo_delito)
            
            color = "#d9534f" if num_necesario == 3 else "#f0ad4e" if num_necesario == 2 else "#0275d8"
            self.analisis_label.config(text=f"ANÁLISIS: {texto_grav}\nSugerencia: {num_necesario} unidades.", fg=color)
            
            self.lista_unidades.delete(0, tk.END)
            self.u_data = [u for u in listar_unidades(solo_en_servicio=True) if u[2] == 'Patrullando']
            for u in self.u_data:
                self.lista_unidades.insert(tk.END, f" 🚓 {u[1]} (En: {u[4]})")
        except: pass

    def confirmar_envio(self):
        indices = self.lista_unidades.curselection()
        if not indices: 
            messagebox.showwarning("Atención", "Seleccione al menos una unidad.")
            return

        inc_info = self.combo_inc.get()
        # Extraemos el barrio destino
        barrio_destino = inc_info.split(" en ")[1]

        for i in indices:
            u_id = self.u_data[i][0]
            asignar_unidad_a_incidente(u_id, barrio_destino)

        messagebox.showinfo("Desplegado", f"Patrullas enviadas a {barrio_destino}")
        self.init_ui()