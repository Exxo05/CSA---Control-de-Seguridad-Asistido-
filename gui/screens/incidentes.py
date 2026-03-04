import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from servicios.incidentes import listar_incidentes, modificar_incidente_completo, finalizar_incidente_db
from servicios.listar import eliminar_incidente_db

class IncidentesScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Encabezado
        header = tk.Frame(self, bg="#1c2b46")
        header.pack(fill="x")
        tk.Label(header, text="📋 GESTIÓN OPERATIVA DE INCIDENTES", 
                 font=("Arial", 14, "bold"), fg="white", bg="#1c2b46", pady=10).pack()

        container = tk.Frame(self, bg="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Añadimos la columna "Estado" a la tabla
        columnas = ("ID", "Tipo", "Descripción", "Hora", "Ubicación", "Estado")
        self.tree = ttk.Treeview(container, columns=columnas, show='headings')
        
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40, anchor="center")
        self.tree.heading("Tipo", text="TIPO"); self.tree.column("Tipo", width=150)
        self.tree.heading("Descripción", text="DESCRIPCIÓN"); self.tree.column("Descripción", width=250)
        self.tree.heading("Hora", text="HORA"); self.tree.column("Hora", width=80, anchor="center")
        self.tree.heading("Ubicación", text="UBICACIÓN"); self.tree.column("Ubicación", width=200)
        self.tree.heading("Estado", text="ESTADO"); self.tree.column("Estado", width=120, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)

        # Botonera
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="🔄 REFRESCAR", bg="#17A2B8", fg="white", 
                  font=("Arial", 9, "bold"), command=self.cargar_datos).pack(side="left", padx=10)
        
        # --- EL BOTÓN QUE BUSCABAS ---
        tk.Button(btn_frame, text="✅ FINALIZAR", bg="#28A745", fg="white", 
                  font=("Arial", 9, "bold"), command=self.marcar_finalizado).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="✏️ EDITAR", bg="#FFC107", 
                  font=("Arial", 9, "bold"), command=self.editar_incidente).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="🗑️ ELIMINAR", bg="#DC3545", fg="white", 
                  font=("Arial", 9, "bold"), command=self.eliminar).pack(side="left", padx=10)

        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        registros = listar_incidentes() # Asegúrate que esta función devuelva las 7 columnas
        
        for row in registros:
            # row tiene: (id, tipo, desc, fecha, zona, direccion, estado)
            # Si tu tabla tiene 6 columnas visuales, úsalas así:
            estado_visual = "✅ FINALIZADO" if row[6] == "Finalizado" else "🚨 ACTIVO"
            ubi = f"{row[5]} ({row[4]})"
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], ubi, estado_visual))
    def marcar_finalizado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un incidente de la lista")
            return
        
        item_id = self.tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Confirmar", "¿Marcar este incidente como resuelto?"):
            finalizar_incidente_db(item_id)
            self.cargar_datos() # Actualiza la tabla para que salga el ✅

    def editar_incidente(self):
        sel = self.tree.selection()
        if not sel: 
            messagebox.showwarning("Atención", "Seleccione un incidente para editar")
            return
            
        item = self.tree.item(sel[0], "values")
        # item[0]=ID, item[1]=Tipo, item[2]=Desc, item[3]=Hora, item[4]=Ubicación (Calle (Barrio)), item[5]=Estado
        
        win = tk.Toplevel(self)
        win.title(f"Editar Incidente #{item[0]}")
        win.geometry("450x400")
        win.configure(padx=20, pady=20)

        # Campos a editar
        tk.Label(win, text="Tipo de Incidente:", font=("Arial", 10, "bold")).pack(anchor="w")
        ent_tipo = tk.Entry(win, width=50)
        ent_tipo.insert(0, item[1])
        ent_tipo.pack(pady=5)

        tk.Label(win, text="Descripción:", font=("Arial", 10, "bold")).pack(anchor="w")
        ent_desc = tk.Entry(win, width=50)
        ent_desc.insert(0, item[2])
        ent_desc.pack(pady=5)

        tk.Label(win, text="Dirección Completa (Ej: Calle Mayor (Centro)):", font=("Arial", 10, "bold")).pack(anchor="w")
        ent_ubi = tk.Entry(win, width=50)
        ent_ubi.insert(0, item[4]) # Aquí ahora cargamos correctamente la Ubicación, no la hora
        ent_ubi.pack(pady=5)

        def guardar():
            nueva_ubi = ent_ubi.get()
            # Validamos el formato "Calle (Barrio)"
            if "(" not in nueva_ubi or ")" not in nueva_ubi:
                messagebox.showerror("Error de Formato", "La ubicación debe incluir el barrio entre paréntesis.\nEjemplo: Calle Rio Sorbe (El Val)")
                return

            try:
                # Separamos la calle del barrio
                partes = nueva_ubi.split(" (")
                direccion = partes[0].strip()
                zona = partes[1].replace(")", "").strip()
                
                from servicios.incidentes import modificar_incidente_completo
                modificar_incidente_completo(item[0], ent_tipo.get(), ent_desc.get(), zona, direccion)
                
                win.destroy()
                self.cargar_datos()
                messagebox.showinfo("Éxito", "Incidente actualizado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        tk.Button(win, text="💾 GUARDAR CAMBIOS", bg="#28A745", fg="white", 
                  font=("Arial", 10, "bold"), command=guardar, pady=10).pack(pady=20, fill="x")
    def eliminar(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar definitivamente de la base de datos?"):
            eliminar_incidente_db(self.tree.item(sel[0], "values")[0])
            self.cargar_datos()