# vistas/areas.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera, ejecutar_en_segundo_plano, guardar_cache_local_datos
from estilos import *

class VistaAreas(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        ctk.CTkLabel(self, text="Gestión de Áreas y Unidades", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(pady=30, padx=30)
        
        marco = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        marco.pack(padx=30, pady=10, fill="both", expand=True)
        
        cols = ("Nombre", "Piso", "Contacto", "Encargado")
        f_tree_areas = ctk.CTkFrame(marco, fg_color="transparent")
        f_tree_areas.pack(pady=12, padx=12, fill="both", expand=True)
        self.tabla_areas = ttk.Treeview(f_tree_areas, columns=cols, show="headings")
        scrollbar_areas = ttk.Scrollbar(f_tree_areas, orient="vertical", command=self.tabla_areas.yview, style="Vertical.TScrollbar")
        self.tabla_areas.configure(yscrollcommand=scrollbar_areas.set)
        for c in cols:
            self.tabla_areas.heading(c, text=c)
            self.tabla_areas.column(c, anchor="center" if c != "Nombre" else "w")
        self.tabla_areas.pack(side="left", fill="both", expand=True)
        scrollbar_areas.pack(side="right", fill="y", padx=(5, 0))
        
        f_bot = ctk.CTkFrame(self, fg_color="transparent")
        f_bot.pack(pady=(10, 25), padx=30, fill="x")
        
        ctk.CTkButton(f_bot, text="✚ Añadir Área", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=42, command=self.abrir_formulario_area).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=42, command=self.modificar_area).pack(side="left", expand=True, padx=8)
        
        self.btn_eliminar = ctk.CTkButton(f_bot, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=42, command=self.eliminar_area)
        self.btn_eliminar.pack(side="left", expand=True, padx=8)
        if not self.app.es_jefe:
            self.btn_eliminar.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)


    def refrescar_datos(self):
        for i in self.tabla_areas.get_children():
            self.tabla_areas.delete(i)
        
        filas = self.app.datos.get("areas", [])
        for r in filas:
            self.tabla_areas.insert("", "end", values=(r.get("nombre", ""), r.get("piso", "") or "-", r.get("contacto", "") or "-", r.get("encargado", "") or "-"))

    def obtener_seleccion(self):
        sel = self.tabla_areas.focus()
        return self.tabla_areas.item(sel, "values") if sel else None

    def abrir_formulario_area(self, area_editar=None):
        vent = ctk.CTkToplevel(self)
        vent.title("Área / Unidad")
        vent.geometry("500x450")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)
        
        ctk.CTkLabel(vent, text="Detalles de la Unidad/Área", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=15)
        
        ctk.CTkLabel(vent, text="Nombre de la Unidad/Área:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=50, pady=(5,0))
        e_nombre = ctk.CTkEntry(vent, placeholder_text="Nombre de la Unidad (ej: Emergencias)", width=400)
        e_nombre.pack(pady=5)
        
        ctk.CTkLabel(vent, text="Piso / Nivel:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=50, pady=(5,0))
        e_piso = ctk.CTkEntry(vent, placeholder_text="Piso / Nivel (opcional)", width=400)
        e_piso.pack(pady=5)
        
        ctk.CTkLabel(vent, text="Número de Contacto:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=50, pady=(5,0))
        e_contacto = ctk.CTkEntry(vent, placeholder_text="Número telefónico o de red interna", width=400)
        e_contacto.pack(pady=5)
        
        ctk.CTkLabel(vent, text="Encargado del Área:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=50, pady=(5,0))
        e_encargado = ctk.CTkEntry(vent, placeholder_text="Nombre del Licenciado(a) o Jefe(a) a cargo", width=400)
        e_encargado.pack(pady=5)
        
        if area_editar:
            e_nombre.insert(0, area_editar["nombre"])
            if area_editar.get("piso"):
                e_piso.insert(0, area_editar["piso"])
            e_contacto.insert(0, area_editar.get("contacto") or "")
            e_encargado.insert(0, area_editar.get("encargado") or "")
            
        def guardar_area():
            nom = e_nombre.get().strip()
            pis = e_piso.get().strip()
            con = e_contacto.get().strip()
            enc = e_encargado.get().strip()
            
            if not nom:
                messagebox.showwarning("Dato Obligatorio", "Debe introducir el nombre de la unidad.")
                return
                
            # 1. Actualizar memoria y caché de inmediato (0 ms)
            area_obj = {
                "nombre": nom,
                "piso": pis,
                "contacto": con,
                "encargado": enc
            }
            if area_editar:
                for idx_a, ex in enumerate(self.app.datos.get("areas", [])):
                    if ex.get("nombre") == area_editar["nombre"]:
                        self.app.datos["areas"][idx_a] = area_obj
                        break
            else:
                self.app.datos.setdefault("areas", []).append(area_obj)

            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            vent.destroy()

            # 2. Guardar en PostgreSQL en segundo plano
            def _guardar_area_db(n, p, c, e, es_edit, old_a):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor()
                        if es_edit:
                            cur.execute("""
                                UPDATE areas 
                                SET nombre=%s, piso=%s, contacto=%s, encargado=%s 
                                WHERE nombre=%s
                            """, (n, p, c, e, old_a["nombre"]))
                        else:
                            cur.execute("""
                                INSERT INTO areas (nombre, piso, contacto, encargado) 
                                VALUES (%s, %s, %s, %s)
                            """, (n, p, c, e))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as err:
                        print(f"[ERROR] Error al guardar área en PostgreSQL: {err}")

            ejecutar_en_segundo_plano(_guardar_area_db, nom, pis, con, enc, bool(area_editar), area_editar)
                
        ctk.CTkButton(vent, text="Guardar Cambios", fg_color=C_BLUE, font=ctk.CTkFont(weight="bold"), height=35, command=guardar_area).pack(pady=25)

    def modificar_area(self):
        v = self.obtener_seleccion()
        if v:
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM areas WHERE nombre=%s", (v[0],))
                area = dict(cur.fetchone())
                cur.close()
                conn.close()
                self.abrir_formulario_area(area)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def eliminar_area(self):
        if not self.app.es_jefe:
            return
        v = self.obtener_seleccion()
        if v and messagebox.askyesno("Confirmar", f"¿Eliminar la unidad/área '{v[0]}'?"):
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM areas WHERE nombre=%s", (v[0],))
                datos_area = dict(cur.fetchone())
                
                # Mover a papelera
                mover_a_papelera(cur, "areas", datos_area["id"], datos_area, self.app.usuario_actual.get("nombre_usuario", "desconocido"))
                
                # Eliminar de areas
                cur.execute("DELETE FROM areas WHERE nombre=%s", (v[0],))
                conn.commit()
                cur.close()
                conn.close()
                
                self.app.cargar_datos_memoria()
                self.refrescar_datos()
                messagebox.showinfo("Éxito", "Eliminado correctamente de la base de datos.")
            except Exception as e:
                messagebox.showerror("Error SQL", str(e))
