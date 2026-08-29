# vistas/repuestos.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera, ejecutar_en_segundo_plano, guardar_cache_local_datos
from estilos import *
from datetime import date, datetime

class VistaRepuestos(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        f_title = ctk.CTkFrame(self, fg_color="transparent")
        f_title.pack(pady=(20, 5), padx=30, fill="x")
        ctk.CTkLabel(f_title, text="Control de Repuestos", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        self.tabview = ctk.CTkTabview(self, fg_color=C_CARD, corner_radius=16, text_color=C_TEXT,
                                      border_width=1, border_color=C_BORDER,
                                      segmented_button_fg_color=C_BG,
                                      segmented_button_selected_color=C_BLUE,
                                      segmented_button_selected_hover_color=C_BLUE_HOVER,
                                      segmented_button_unselected_color=C_BG,
                                      segmented_button_unselected_hover_color=C_CARD_HOVER)
        self.tabview.pack(padx=30, pady=10, fill="both", expand=True)
        
        tab_inv = self.tabview.add("Inventario de Repuestos")
        tab_hist = self.tabview.add("Historial de Repuestos Usados")
        
        # --- TAB: INVENTARIO DE REPUESTOS ---
        marco = ctk.CTkFrame(tab_inv, fg_color="transparent")
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filtros de Inventario
        f_filtros_inv = ctk.CTkFrame(marco, fg_color="transparent")
        f_filtros_inv.pack(fill="x", pady=(0, 10))
        
        self.busqueda_inv_var = ctk.StringVar()
        self.busqueda_inv_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_filtros_inv, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_inv = ctk.CTkEntry(f_filtros_inv, textvariable=self.busqueda_inv_var, placeholder_text="Buscar Equipo o Repuesto...", width=220, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_inv.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_filtros_inv, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_inv = ctk.CTkComboBox(f_filtros_inv, values=["Repuesto (A-Z)", "Repuesto (Z-A)", "Equipo Médico", "Cantidad (Mayor)", "Cantidad (Menor)"], command=lambda e: self.refrescar_datos(), width=160, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_inv.pack(side="left", padx=5)
        self.combo_ordenar_inv.set("Repuesto (A-Z)")
        
        cols_rep = ("Equipo Médico", "Repuesto", "Cantidad Disponible")
        f_tree_rep = ctk.CTkFrame(marco, fg_color="transparent")
        f_tree_rep.pack(pady=8, padx=5, fill="both", expand=True)
        self.tabla_rep = ttk.Treeview(f_tree_rep, columns=cols_rep, show="headings")
        scrollbar_rep = ttk.Scrollbar(f_tree_rep, orient="vertical", command=self.tabla_rep.yview, style="Vertical.TScrollbar")
        self.tabla_rep.configure(yscrollcommand=scrollbar_rep.set)
        for c in cols_rep:
            self.tabla_rep.heading(c, text=c); self.tabla_rep.column(c, anchor="center")
        self.tabla_rep.pack(side="left", fill="both", expand=True)
        scrollbar_rep.pack(side="right", fill="y", padx=(5, 0))
        
        f_bot_rep = ctk.CTkFrame(tab_inv, fg_color="transparent")
        f_bot_rep.pack(pady=(5, 15), padx=10, fill="x")
        ctk.CTkButton(f_bot_rep, text="✚ Añadir Repuesto", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=40, command=self.abrir_formulario_repuesto).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot_rep, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=40, command=self.modificar_repuesto).pack(side="left", expand=True, padx=8)
        self.btn_eliminar = ctk.CTkButton(f_bot_rep, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=40, command=self.eliminar_repuesto)
        self.btn_eliminar.pack(side="left", expand=True, padx=8)
        if not self.app.es_jefe: self.btn_eliminar.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)

        
        # --- TAB: HISTORIAL DE REPUESTOS USADOS ---
        marco_hist = ctk.CTkFrame(tab_hist, fg_color="transparent")
        marco_hist.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filtros de Historial
        f_filtros_hist = ctk.CTkFrame(marco_hist, fg_color="transparent")
        f_filtros_hist.pack(fill="x", pady=(0, 10))
        
        self.busqueda_hist_var = ctk.StringVar()
        self.busqueda_hist_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_filtros_hist, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_hist = ctk.CTkEntry(f_filtros_hist, textvariable=self.busqueda_hist_var, placeholder_text="Buscar Equipo, Repuesto, Servicio...", width=220, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_hist.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_filtros_hist, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_hist = ctk.CTkComboBox(f_filtros_hist, values=["Fecha (Reciente)", "Fecha (Antiguo)", "Equipo Médico", "Repuesto Usado", "Cantidad (Mayor)", "Cantidad (Menor)"], command=lambda e: self.refrescar_datos(), width=160, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_hist.pack(side="left", padx=5)
        self.combo_ordenar_hist.set("Fecha (Reciente)")
        
        cols_hist = ("Fecha", "Equipo Médico (ID - Nombre)", "Servicio", "Área", "Repuesto Usado", "Cantidad")
        f_tree_hist = ctk.CTkFrame(marco_hist, fg_color="transparent")
        f_tree_hist.pack(pady=10, padx=10, fill="both", expand=True)
        self.tabla_hist_rep = ttk.Treeview(f_tree_hist, columns=cols_hist, show="headings")
        scrollbar_hist = ttk.Scrollbar(f_tree_hist, orient="vertical", command=self.tabla_hist_rep.yview, style="Vertical.TScrollbar")
        self.tabla_hist_rep.configure(yscrollcommand=scrollbar_hist.set)
        for c in cols_hist:
            self.tabla_hist_rep.heading(c, text=c)
            self.tabla_hist_rep.column(c, anchor="center")
        self.tabla_hist_rep.pack(side="left", fill="both", expand=True)
        scrollbar_hist.pack(side="right", fill="y", padx=(5, 0))

    def refrescar_datos(self):
        # 1. Refrescar Inventario de Repuestos
        for i in self.tabla_rep.get_children(): 
            self.tabla_rep.delete(i)
            
        repuestos = list(self.app.datos.get("repuestos", []))
        
        # Filtro de búsqueda
        t_inv = self.busqueda_inv_var.get().lower().strip()
        if t_inv:
            repuestos = [r for r in repuestos if (
                t_inv in str(r.get("tipo_equipo", "")).lower() or
                t_inv in str(r.get("nombre_repuesto", "")).lower()
            )]
            
        # Ordenación
        crit_inv = self.combo_ordenar_inv.get() if hasattr(self, "combo_ordenar_inv") else "Repuesto (A-Z)"
        if crit_inv == "Repuesto (A-Z)":
            repuestos.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower())
        elif crit_inv == "Repuesto (Z-A)":
            repuestos.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower(), reverse=True)
        elif crit_inv == "Equipo Médico":
            repuestos.sort(key=lambda x: str(x.get("tipo_equipo", "")).lower())
        elif crit_inv == "Cantidad (Mayor)":
            repuestos.sort(key=lambda x: int(x.get("cantidad", 0)), reverse=True)
        elif crit_inv == "Cantidad (Menor)":
            repuestos.sort(key=lambda x: int(x.get("cantidad", 0)))
            
        for r in repuestos: 
            self.tabla_rep.insert("", "end", values=(r.get("tipo_equipo", ""), r.get("nombre_repuesto", ""), r.get("cantidad", "")))
        
        # 2. Refrescar Historial de Repuestos Usados (Extraído en memoria instantáneamente)
        for i in self.tabla_hist_rep.get_children(): 
            self.tabla_hist_rep.delete(i)
            
        try:
            historial_datos = []
            for eq in self.app.datos.get("equipos", []):
                for inter in eq.get("historial_intervenciones", []):
                    if inter.get("repuesto_usado"):
                        historial_datos.append({
                            "fecha": inter.get("fecha"),
                            "eq_id": eq.get("id", ""),
                            "eq_nombre": eq.get("nombre", ""),
                            "eq_servicio": eq.get("servicio", ""),
                            "eq_area": eq.get("area", ""),
                            "repuesto_nombre": inter.get("repuesto_nombre", ""),
                            "repuesto_cantidad": inter.get("repuesto_cantidad", 0)
                        })
                
            # Filtro de búsqueda
            t_hist = self.busqueda_hist_var.get().lower().strip()
            if t_hist:
                historial_datos = [h for h in historial_datos if (
                    t_hist in str(h["eq_id"]).lower() or
                    t_hist in str(h["eq_nombre"]).lower() or
                    t_hist in str(h.get("eq_servicio", "")).lower() or
                    t_hist in str(h.get("eq_area", "")).lower() or
                    t_hist in str(h.get("repuesto_nombre", "")).lower()
                )]
                
            # Ordenación
            crit_hist = self.combo_ordenar_hist.get() if hasattr(self, "combo_ordenar_hist") else "Fecha (Reciente)"
            if crit_hist == "Fecha (Reciente)":
                def get_fecha(x):
                    f = x.get("fecha")
                    if isinstance(f, str):
                        try: return datetime.strptime(f, "%Y-%m-%d").date()
                        except: return date.min
                    return f or date.min
                historial_datos.sort(key=get_fecha, reverse=True)
            elif crit_hist == "Fecha (Antiguo)":
                def get_fecha(x):
                    f = x.get("fecha")
                    if isinstance(f, str):
                        try: return datetime.strptime(f, "%Y-%m-%d").date()
                        except: return date.min
                    return f or date.min
                historial_datos.sort(key=get_fecha)
            elif crit_hist == "Equipo Médico":
                historial_datos.sort(key=lambda x: str(x.get("eq_nombre", "")).lower())
            elif crit_hist == "Repuesto Usado":
                historial_datos.sort(key=lambda x: str(x.get("repuesto_nombre", "")).lower())
            elif crit_hist == "Cantidad (Mayor)":
                historial_datos.sort(key=lambda x: int(x.get("repuesto_cantidad", 0)), reverse=True)
            elif crit_hist == "Cantidad (Menor)":
                historial_datos.sort(key=lambda x: int(x.get("repuesto_cantidad", 0)))
                
            for h in historial_datos:
                eq_str = f"{h['eq_id']} - {h['eq_nombre']}"
                self.tabla_hist_rep.insert("", "end", values=(h["fecha"], eq_str, h["eq_servicio"], h["eq_area"], h["repuesto_nombre"], h["repuesto_cantidad"]))
        except Exception as e:
            print("Error al cargar historial de repuestos:", e)

    def obtener_seleccion(self):
        sel = self.tabla_rep.focus()
        return self.tabla_rep.item(sel, "values") if sel else None

    def abrir_formulario_repuesto(self, rep_editar=None):
        vent = ctk.CTkToplevel(self)
        vent.title("Repuesto / Accesorio")
        vent.geometry("500x550")
        vent.transient(self.app); vent.grab_set(); vent.configure(fg_color=C_CARD)
        opciones_cat = [f"{c['nombre']} - {c.get('marca', '')} - {c.get('modelo', '')}" for c in self.app.datos["catalogo"]]
        combo_tipo = ctk.CTkComboBox(vent, values=opciones_cat if opciones_cat else ["Vacío"], width=400)
        combo_tipo.pack(pady=10)
        e_nombre = ctk.CTkEntry(vent, placeholder_text="Nombre del repuesto", width=400)
        e_nombre.pack(pady=10); e_cantidad = ctk.CTkEntry(vent, placeholder_text="Cantidad", width=400)
        e_cantidad.pack(pady=10)
        ruta_foto = ctk.StringVar()
        ctk.CTkButton(vent, text="Adjuntar foto", command=lambda: ruta_foto.set(filedialog.askopenfilename() or ""), fg_color=C_ORANGE).pack(pady=10)
        if rep_editar:
            combo_tipo.set(rep_editar.get("tipo_equipo", "")); e_nombre.insert(0, rep_editar.get("nombre_repuesto", "")); e_cantidad.insert(0, str(rep_editar.get("cantidad", "")))
        def guardar_repuesto():
            t_eq = combo_tipo.get().strip()
            n_rep = e_nombre.get().strip()
            try:
                c_cant = int(e_cantidad.get().strip())
            except:
                messagebox.showwarning("Dato Inválido", "La cantidad debe ser un número entero.")
                return

            if not n_rep:
                messagebox.showwarning("Dato Requerido", "Ingrese el nombre del repuesto.")
                return

            r_foto = ruta_foto.get()

            # 1. Actualizar memoria y caché de inmediato (0 ms)
            rep_obj = {
                "tipo_equipo": t_eq,
                "nombre_repuesto": n_rep,
                "cantidad": c_cant,
                "foto": r_foto
            }
            if rep_editar:
                for idx_r, ex in enumerate(self.app.datos.get("repuestos", [])):
                    if ex.get("tipo_equipo") == rep_editar["tipo_equipo"] and ex.get("nombre_repuesto") == rep_editar["nombre_repuesto"]:
                        self.app.datos["repuestos"][idx_r] = rep_obj
                        break
            else:
                self.app.datos.setdefault("repuestos", []).append(rep_obj)

            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            vent.destroy()

            # 2. Guardar en PostgreSQL en segundo plano
            def _guardar_rep_db(tipo_e, nom_r, cant_r, fot_r, es_edit, old_rep):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor()
                        if es_edit:
                            cur.execute("""
                                UPDATE repuestos 
                                SET tipo_equipo=%s, nombre_repuesto=%s, cantidad=%s, foto=%s 
                                WHERE tipo_equipo=%s AND nombre_repuesto=%s
                            """, (tipo_e, nom_r, cant_r, fot_r, old_rep["tipo_equipo"], old_rep["nombre_repuesto"]))
                        else:
                            cur.execute("""
                                INSERT INTO repuestos (tipo_equipo, nombre_repuesto, cantidad, foto) 
                                VALUES (%s, %s, %s, %s)
                            """, (tipo_e, nom_r, cant_r, fot_r))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Error al guardar repuesto en PostgreSQL: {e}")

            ejecutar_en_segundo_plano(_guardar_rep_db, t_eq, n_rep, c_cant, r_foto, bool(rep_editar), rep_editar)
        ctk.CTkButton(vent, text="Guardar", fg_color=C_BLUE, command=guardar_repuesto).pack(pady=20)

    def modificar_repuesto(self):
        if not self.app.es_jefe:
            messagebox.showerror("Permiso denegado", "Solo el Jefe de servicio puede modificar repuestos.")
            return
        v = self.obtener_seleccion()
        if v:
            rep = next((r for r in self.app.datos["repuestos"] if r["tipo_equipo"] == v[0] and r["nombre_repuesto"] == v[1]), None)
            if rep: self.abrir_formulario_repuesto(rep)

    def eliminar_repuesto(self):
        if not self.app.es_jefe: return
        v = self.obtener_seleccion()
        if v and messagebox.askyesno("Confirmar", f"¿Eliminar repuesto '{v[1]}'?"):
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM repuestos WHERE tipo_equipo=%s AND nombre_repuesto=%s", (v[0], v[1]))
                fila = cur.fetchone()
                if fila:
                    mover_a_papelera(cur, "repuestos", fila["id"], dict(fila), self.app.usuario_actual.get("nombre_usuario", "jefe"))
                cur.execute("DELETE FROM repuestos WHERE id = %s", (fila["id"],))
                conn.commit(); cur.close(); conn.close()
                self.app.cargar_datos_memoria(); self.refrescar_datos()
            except Exception as e: messagebox.showerror("Error", str(e))