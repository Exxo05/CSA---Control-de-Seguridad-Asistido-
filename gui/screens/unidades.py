import tkinter as tk
from tkinter import ttk, messagebox
from servicios.unidades import listar_unidades, alternar_servicio, cambiar_estado_operativo
from gui.styles import POLICE_BLUE, WHITE  # Asegúrate de tener estos estilos

class UnidadesScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # VOLVEMOS AL HEADER AZUL ORIGINAL
        header = tk.Frame(self, bg="#1c2b46")
        header.pack(fill="x")
        tk.Label(header, text="🚓 GESTIÓN DE UNIDADES Y ESTADO DE FUERZAS", 
                 font=("Arial", 16, "bold"), fg="white", bg="#1c2b46", pady=15).pack()

        main_container = tk.Frame(self, bg="white")
        main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # TABLA ORIGINAL
        columnas = ("ID", "Indicativo", "Servicio", "Situación", "Zona Actual")
        self.tree = ttk.Treeview(main_container, columns=columnas, show='headings', height=12)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(side="left", expand=True, fill="both")

        # PANEL DERECHO ORIGINAL
        panel_control = tk.Frame(main_container, bg="#F8F9FA", padx=15, pady=15, relief="ridge", bd=1)
        panel_control.pack(side="right", fill="y", padx=(10, 0))

        tk.Label(panel_control, text="CONTROL OPERATIVO", font=("Arial", 10, "bold"), bg="#F8F9FA").pack(pady=5)
        
        tk.Button(panel_control, text="➕ ALTA TURNO", bg="#28A745", fg="white", font=("Arial", 9, "bold"),
                  command=lambda: self.modificar_servicio(1)).pack(fill="x", pady=5)
        
        tk.Button(panel_control, text="➖ BAJA TURNO", bg="#6C757D", fg="white", font=("Arial", 9, "bold"),
                  command=lambda: self.modificar_servicio(0)).pack(fill="x", pady=5)

        ttk.Separator(panel_control, orient="horizontal").pack(fill="x", pady=15)

        # BOTONES DE ESTADO RADIO
        tk.Button(panel_control, text="📢 PATRULLANDO", bg="#17A2B8", fg="white", 
                  command=lambda: self.set_estado("Patrullando")).pack(fill="x", pady=5)
        
        tk.Button(panel_control, text="⚡ INTERVENCIÓN", bg="#FFC107", 
                  command=lambda: self.set_estado("En Intervención")).pack(fill="x", pady=5)
        
        tk.Button(panel_control, text="🔄 REFRESCAR", command=self.cargar_datos).pack(fill="x", pady=20)

        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for u in listar_unidades():
            status_turno = "OPERATIVO" if u[3] == 1 else "FUERA DE TURNO"
            self.tree.insert("", "end", values=(u[0], u[1], status_turno, u[2], u[4]))

    def modificar_servicio(self, valor):
        sel = self.tree.selection()
        if not sel: return
        u_id = self.tree.item(sel[0], "values")[0]
        alternar_servicio(u_id, valor)
        self.cargar_datos()

    def set_estado(self, estado):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0], "values")
        u_id, indicativo, _, situacion_actual, zona_actual = item

        # Si pasa de Intervención a Patrullando, cerramos el incidente con el nuevo sistema
        if estado == "Patrullando" and situacion_actual == "En Intervención":
            if messagebox.askyesno("Finalizar Servicio", f"¿La unidad {indicativo} ha resuelto el aviso en {zona_actual}?"):
                # IMPORTANTE: Cambiamos la importación aquí para evitar el ImportError
                from servicios.incidentes import finalizar_incidente_por_zona
                finalizar_incidente_por_zona(zona_actual)
                messagebox.showinfo("Sistema CSA", "Incidente marcado como ✅ FINALIZADO.")

        cambiar_estado_operativo(u_id, estado)
        self.cargar_datos()