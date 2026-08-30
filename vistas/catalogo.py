# vistas/catalogo.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera, ejecutar_en_segundo_plano, guardar_cache_local_datos
from estilos import *

class VistaCatalogo(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(pady=(30, 10), padx=30, fill="x")
        ctk.CTkLabel(f_top, text="Equipos Médicos", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", lambda *args: self.refrescar_datos())
        
        # Caja de búsqueda con etiqueta explícita "🔍 Buscar:"
        f_search = ctk.CTkFrame(f_top, fg_color="transparent")
        f_search.pack(side="right")
        ctk.CTkLabel(f_search, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar = ctk.CTkEntry(f_search, textvariable=self.busqueda_var, placeholder_text="Buscar Nombre, Marca o Modelo...", width=250, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar.pack(side="left")

        # Barra de Ordenación/Filtros
        f_filtros = ctk.CTkFrame(self, fg_color="transparent")
        f_filtros.pack(pady=(5, 10), padx=30, fill="x")
        ctk.CTkLabel(f_filtros, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(0, 5))
        self.combo_ordenar = ctk.CTkComboBox(f_filtros, values=["Nombre (A-Z)", "Nombre (Z-A)", "Marca", "Modelo", "Área", "Piso"], command=lambda e: self.refrescar_datos(), width=180, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar.pack(side="left")
        self.combo_ordenar.set("Nombre (A-Z)")

        marco = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        marco.pack(padx=30, pady=10, fill="both", expand=True)
        
        f_tree_cat = ctk.CTkFrame(marco, fg_color="transparent")
        f_tree_cat.pack(pady=12, padx=12, fill="both", expand=True)
        self.tabla_cat = ttk.Treeview(f_tree_cat, columns=("Nombre", "Marca", "Modelo", "Área", "Piso"), show="headings")
        scrollbar_cat = ttk.Scrollbar(f_tree_cat, orient="vertical", command=self.tabla_cat.yview, style="Vertical.TScrollbar")
        self.tabla_cat.configure(yscrollcommand=scrollbar_cat.set)
        for c in ("Nombre", "Marca", "Modelo", "Área", "Piso"):
            self.tabla_cat.heading(c, text=c)
            self.tabla_cat.column(c, anchor="center")
        self.tabla_cat.pack(side="left", fill="both", expand=True)
        scrollbar_cat.pack(side="right", fill="y", padx=(5, 0))
        
        f_bot_cat = ctk.CTkFrame(self, fg_color="transparent")
        f_bot_cat.pack(pady=(10, 25), padx=30, fill="x")
        ctk.CTkButton(f_bot_cat, text="✚ Añadir Modelo", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=42, command=self.abrir_formulario_catalogo).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot_cat, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=42, command=self.modificar_catalogo).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot_cat, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=42, command=self.eliminar_catalogo).pack(side="left", expand=True, padx=8)


    def refrescar_datos(self):
        for i in self.tabla_cat.get_children(): 
            self.tabla_cat.delete(i)
            
        catalogo = list(self.app.datos.get("catalogo", []))
        
        # Filtro de búsqueda
        t = self.busqueda_var.get().lower().strip()
        if t:
            catalogo = [c for c in catalogo if (
                t in str(c.get("nombre", "")).lower() or
                t in str(c.get("marca", "")).lower() or
                t in str(c.get("modelo", "")).lower() or
                t in str(c.get("area", "")).lower() or
                t in str(c.get("piso", "")).lower()
            )]
            
        # Ordenación
        criterio = self.combo_ordenar.get() if hasattr(self, "combo_ordenar") else "Nombre (A-Z)"
        if criterio == "Nombre (A-Z)":
            catalogo.sort(key=lambda x: str(x.get("nombre", "")).lower())
        elif criterio == "Nombre (Z-A)":
            catalogo.sort(key=lambda x: str(x.get("nombre", "")).lower(), reverse=True)
        elif criterio == "Marca":
            catalogo.sort(key=lambda x: str(x.get("marca", "")).lower())
        elif criterio == "Modelo":
            catalogo.sort(key=lambda x: str(x.get("modelo", "")).lower())
        elif criterio == "Área":
            catalogo.sort(key=lambda x: str(x.get("area", "")).lower())
        elif criterio == "Piso":
            catalogo.sort(key=lambda x: str(x.get("piso", "")).lower())
            
        for c in catalogo: 
            self.tabla_cat.insert("", "end", values=(c["nombre"], c.get("marca", ""), c.get("modelo", ""), c.get("area", ""), c.get("piso", "")))

    def obtener_seleccion(self):
        sel = self.tabla_cat.focus()
        return self.tabla_cat.item(sel, "values") if sel else None

    def abrir_formulario_catalogo(self, edit_data=None):
        v = ctk.CTkToplevel(self)
        v.title("Modelo Estandarizado")
        v.geometry("500x520")
        v.transient(self.app)
        v.grab_set()
        v.configure(fg_color=C_CARD)
        
        nombres_existentes = sorted(list(set(c["nombre"] for c in self.app.datos["catalogo"])))
        
        ctk.CTkLabel(v, text="Nombre del Equipo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=100, pady=(15, 0))
        en = ctk.CTkComboBox(v, values=nombres_existentes if nombres_existentes else ["Bomba de infusion"], width=300)
        en.pack(pady=5)
        
        ctk.CTkLabel(v, text="Marca:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=100, pady=(5, 0))
        em = ctk.CTkEntry(v, placeholder_text="Marca", width=300)
        em.pack(pady=5)
        
        ctk.CTkLabel(v, text="Modelo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=100, pady=(5, 0))
        emo = ctk.CTkEntry(v, placeholder_text="Modelo", width=300)
        emo.pack(pady=5)
        
        ctk.CTkLabel(v, text="Área / Unidad:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=100, pady=(5, 0))
        val_areas = [a["nombre"] for a in self.app.datos["areas"]]
        combo_area = ctk.CTkComboBox(v, values=val_areas if val_areas else ["No hay áreas"], width=300)
        combo_area.pack(pady=5)
        
        ctk.CTkLabel(v, text="Piso:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=100, pady=(5, 0))
        e_piso = ctk.CTkEntry(v, placeholder_text="Piso (se llena solo)", width=300)
        e_piso.configure(state="disabled")
        e_piso.pack(pady=5)
        
        def update_piso(*args):
            area_sel = combo_area.get()
            area_obj = next((a for a in self.app.datos["areas"] if a["nombre"] == area_sel), None)
            piso_val = area_obj.get("piso", "") if area_obj else ""
            e_piso.configure(state="normal")
            e_piso.delete(0, "end")
            e_piso.insert(0, piso_val)
            e_piso.configure(state="disabled")
            
        combo_area.configure(command=update_piso)
        if hasattr(combo_area, "_entry"):
            combo_area._entry.bind("<FocusOut>", lambda e: update_piso())
            
        habilitar_autocompletado(en, nombres_existentes)
        habilitar_autocompletado(combo_area, val_areas)
        
        def al_seleccionar_nombre(val_sel):
            match = next((c for c in self.app.datos["catalogo"] if c["nombre"] == val_sel), None)
            if match:
                em.delete(0, "end")
                em.insert(0, match.get("marca") or "")
                emo.delete(0, "end")
                emo.insert(0, match.get("modelo") or "")
                if match.get("area"):
                    combo_area.set(match["area"])
                    update_piso()
                    
        en.configure(command=al_seleccionar_nombre)
        
        if edit_data:
            en.set(edit_data["nombre"])
            em.insert(0, edit_data.get("marca") or "")
            emo.insert(0, edit_data.get("modelo") or "")
            if edit_data.get("area"):
                combo_area.set(edit_data["area"])
                update_piso()

        def guardar():
            update_piso()
            
            nombre_val = en.get().strip()
            marca_val = em.get().strip()
            modelo_val = emo.get().strip()
            area_val = combo_area.get()
            
            e_piso.configure(state="normal")
            piso_val = e_piso.get()
            e_piso.configure(state="disabled")
            
            if not nombre_val:
                messagebox.showwarning("Dato Obligatorio", "Debe introducir el nombre del equipo.")
                return
                
            duplicado = next((c for c in self.app.datos["catalogo"] if 
                              c["nombre"].strip().lower() == nombre_val.lower() and 
                              (c.get("marca") or "").strip().lower() == marca_val.lower() and 
                              (c.get("modelo") or "").strip().lower() == modelo_val.lower() and 
                              (c.get("area") or "").strip().lower() == area_val.lower()), None)
            
            if duplicado and (not edit_data or (edit_data["nombre"] != nombre_val or edit_data.get("marca","") != marca_val or edit_data.get("modelo","") != modelo_val or edit_data.get("area","") != area_val)):
                if not messagebox.askyesno("Alerta de Duplicado", f"Alerta: Ya existe exactamente el modelo '{nombre_val}' de marca '{marca_val}', modelo '{modelo_val}' registrado en la unidad '{area_val}'.\n\n¿Desea registrar otro de todas formas?"):
                    return
                
            # 1. Actualizar memoria y caché de inmediato (0 ms)
            cat_obj = {
                "nombre": nombre_val,
                "marca": marca_val,
                "modelo": modelo_val,
                "area": area_val,
                "piso": piso_val
            }
            if edit_data:
                for idx_c, ex in enumerate(self.app.datos.get("catalogo", [])):
                    if ex.get("nombre") == edit_data["nombre"] and ex.get("marca","") == edit_data.get("marca","") and ex.get("modelo","") == edit_data.get("modelo",""):
                        self.app.datos["catalogo"][idx_c] = cat_obj
                        break
            else:
                self.app.datos.setdefault("catalogo", []).append(cat_obj)

            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            v.destroy()

            # 2. Guardar en PostgreSQL en segundo plano
            def _guardar_cat_db(nom, mar, mdl, ar, ps, es_edicion, old_data):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor()
                        if es_edicion:
                            cur.execute("""
                                UPDATE catalogo 
                                SET nombre=%s, marca=%s, modelo=%s, area=%s, piso=%s 
                                WHERE nombre=%s AND marca=%s AND modelo=%s
                            """, (nom, mar, mdl, ar, ps, old_data["nombre"], old_data.get("marca",""), old_data.get("modelo","")))
                        else:
                            cur.execute("""
                                INSERT INTO catalogo (nombre, marca, modelo, area, piso) 
                                VALUES (%s, %s, %s, %s, %s)
                            """, (nom, mar, mdl, ar, ps))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Error al guardar catálogo en PostgreSQL: {e}")

            ejecutar_en_segundo_plano(_guardar_cat_db, nombre_val, marca_val, modelo_val, area_val, piso_val, bool(edit_data), edit_data)
                
        ctk.CTkButton(v, text="Guardar", font=ctk.CTkFont(weight="bold"), fg_color=C_BLUE, command=guardar).pack(pady=20)

    def modificar_catalogo(self):
        v = self.obtener_seleccion()
        if v:
            model_obj = next((c for c in self.app.datos["catalogo"] if c["nombre"] == v[0] and c.get("marca","") == v[1] and c.get("modelo","") == v[2]), None)
            if model_obj:
                self.abrir_formulario_catalogo(edit_data=model_obj)

    def eliminar_catalogo(self):
        if not self.app.es_jefe:
            messagebox.showerror("Permiso Denegado", "Solo el Jefe puede eliminar modelos.")
            return
        v = self.obtener_seleccion()
        if v and messagebox.askyesno("Confirmar", f"¿Eliminar el modelo {v[0]}?"):
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM catalogo WHERE nombre=%s AND marca=%s AND modelo=%s", (v[0], v[1], v[2]))
                fila = cur.fetchone()
                if fila:
                    mover_a_papelera(cur, "catalogo", fila["id"], dict(fila), self.app.usuario_actual.get("nombre_usuario", "jefe"))
                    cur.execute("DELETE FROM catalogo WHERE id = %s", (fila["id"],))
                    conn.commit()
                cur.close()
                conn.close()
                self.app.cargar_datos_memoria()
                self.refrescar_datos()
            except Exception as e: 
                messagebox.showerror("Error SQL", str(e))