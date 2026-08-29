# vistas/historial.py
import os
from datetime import datetime, date
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import openpyxl
from openpyxl.styles import Font, Alignment
import psycopg2.extras

from database import obtener_conexion, mover_a_papelera
from estilos import *
from config import CARPETAS
from excel_utils import obtener_ruta_plantilla, exportar_excel_a_pdf, escribir_en_celda_segura, marcar_x, escribir_texto_largo

class VistaHistorial(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(pady=(20, 5), padx=30, fill="x")
        ctk.CTkLabel(f_top, text="Historial General de Mantenimientos", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")

        # Pestañas de Historial
        self.tabview_hist = ctk.CTkTabview(self, fg_color=C_CARD, corner_radius=16, text_color=C_TEXT,
                                           border_width=1, border_color=C_BORDER,
                                           segmented_button_fg_color=C_BG,
                                           segmented_button_selected_color=C_BLUE,
                                           segmented_button_selected_hover_color=C_BLUE_HOVER,
                                           segmented_button_unselected_color=C_BG,
                                           segmented_button_unselected_hover_color=C_CARD_HOVER)
        self.tabview_hist.pack(padx=30, pady=10, fill="both", expand=True)

        
        self.tab_todo = self.tabview_hist.add("📋 Todo el Historial")
        self.tab_mensual = self.tabview_hist.add("📅 Historial Mensual")
        
        # --- PESTAÑA 1: TODO EL HISTORIAL ---
        marco_todo = ctk.CTkFrame(self.tab_todo, fg_color="transparent")
        marco_todo.pack(fill="both", expand=True, padx=10, pady=10)
        
        f_filtros_todo = ctk.CTkFrame(marco_todo, fg_color="transparent")
        f_filtros_todo.pack(fill="x", pady=(0, 10))
        
        self.busqueda_todo_var = ctk.StringVar()
        self.busqueda_todo_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_filtros_todo, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_todo = ctk.CTkEntry(f_filtros_todo, textvariable=self.busqueda_todo_var, placeholder_text="Buscar ID, Equipo o Detalle...", width=220, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_todo.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_filtros_todo, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_todo = ctk.CTkComboBox(f_filtros_todo, values=["Fecha (Reciente)", "Fecha (Antiguo)", "Equipo (A-Z)", "Equipo (Z-A)", "Responsable"], command=lambda e: self.refrescar_datos(), width=160, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_todo.pack(side="left", padx=5)
        self.combo_ordenar_todo.set("Fecha (Reciente)")
        
        cols = ("Fecha", "Hora", "ID Equipo", "Nombre Equipo", "Tipo Mantenimiento", "Responsable", "Detalle de Trabajo", "ID_BD")
        
        f_tree_todo = ctk.CTkFrame(marco_todo, fg_color="transparent")
        f_tree_todo.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tabla_hist_todo = ttk.Treeview(f_tree_todo, columns=cols, show="headings", displaycolumns=("Fecha", "Hora", "ID Equipo", "Nombre Equipo", "Tipo Mantenimiento", "Responsable", "Detalle de Trabajo"))
        scrollbar_todo = ttk.Scrollbar(f_tree_todo, orient="vertical", command=self.tabla_hist_todo.yview, style="Vertical.TScrollbar")
        self.tabla_hist_todo.configure(yscrollcommand=scrollbar_todo.set)
        
        for c in cols[:-1]:
            self.tabla_hist_todo.heading(c, text=c)
            if c != "Detalle de Trabajo":
                self.tabla_hist_todo.column(c, anchor="center")
            else:
                self.tabla_hist_todo.column(c, anchor="w", width=300)
                
        def abrir_ficha_desde_hist(event, tree):
            sel = tree.focus()
            if sel:
                vals = tree.item(sel, "values")
                if vals and len(vals) > 2:
                    eq_id = vals[2]  # Columna 'ID Equipo'
                    self.app.abrir_hoja_vida_click(equipo_id=eq_id)

        self.tabla_hist_todo.bind("<Double-1>", lambda e: abrir_ficha_desde_hist(e, self.tabla_hist_todo))
        self.tabla_hist_todo.pack(side="left", fill="both", expand=True)
        scrollbar_todo.pack(side="right", fill="y")
        
        # --- PESTAÑA 2: HISTORIAL MENSUAL ---
        marco_mes = ctk.CTkFrame(self.tab_mensual, fg_color="transparent")
        marco_mes.pack(fill="both", expand=True, padx=10, pady=10)
        
        f_filtros_mes = ctk.CTkFrame(marco_mes, fg_color="transparent")
        f_filtros_mes.pack(fill="x", pady=(0, 10))
        
        # Seleccionar Mes y Año
        ctk.CTkLabel(f_filtros_mes, text="Mes:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        nombres_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.combo_mes = ctk.CTkComboBox(f_filtros_mes, values=nombres_meses, command=lambda e: self.refrescar_datos(), width=120, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_mes.pack(side="left", padx=5)
        self.combo_mes.set(nombres_meses[datetime.now().month - 1])
        
        ctk.CTkLabel(f_filtros_mes, text="Año:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_anio = ctk.CTkComboBox(f_filtros_mes, values=[str(y) for y in range(2024, 2032)], command=lambda e: self.refrescar_datos(), width=100, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_anio.pack(side="left", padx=5)
        self.combo_anio.set(str(datetime.now().year))
        
        self.busqueda_mes_var = ctk.StringVar()
        self.busqueda_mes_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_filtros_mes, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        e_buscar_mes = ctk.CTkEntry(f_filtros_mes, textvariable=self.busqueda_mes_var, placeholder_text="Buscar en este mes...", width=180, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_mes.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_filtros_mes, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_mes = ctk.CTkComboBox(f_filtros_mes, values=["Fecha (Reciente)", "Fecha (Antiguo)", "Equipo (A-Z)", "Equipo (Z-A)", "Responsable"], command=lambda e: self.refrescar_datos(), width=140, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_mes.pack(side="left", padx=5)
        self.combo_ordenar_mes.set("Fecha (Reciente)")
        
        f_tree_mes = ctk.CTkFrame(marco_mes, fg_color="transparent")
        f_tree_mes.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tabla_hist_mes = ttk.Treeview(f_tree_mes, columns=cols, show="headings", displaycolumns=("Fecha", "Hora", "ID Equipo", "Nombre Equipo", "Tipo Mantenimiento", "Responsable", "Detalle de Trabajo"))
        scrollbar_mes = ttk.Scrollbar(f_tree_mes, orient="vertical", command=self.tabla_hist_mes.yview, style="Vertical.TScrollbar")
        self.tabla_hist_mes.configure(yscrollcommand=scrollbar_mes.set)
        self.tabla_hist_mes.bind("<Double-1>", lambda e: abrir_ficha_desde_hist(e, self.tabla_hist_mes))

        
        for c in cols[:-1]:
            self.tabla_hist_mes.heading(c, text=c)
            if c != "Detalle de Trabajo":
                self.tabla_hist_mes.column(c, anchor="center")
            else:
                self.tabla_hist_mes.column(c, anchor="w", width=300)
                
        self.tabla_hist_mes.pack(side="left", fill="both", expand=True)
        scrollbar_mes.pack(side="right", fill="y")

        # Botones de Acción
        f_bot_hist = ctk.CTkFrame(self, fg_color="transparent")
        f_bot_hist.pack(pady=(10, 25), padx=30, fill="x")
        
        btn_reconstruir = ctk.CTkButton(f_bot_hist, text="📄 Reconstruir Hoja (Excel)", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=42, command=lambda: self.procesar_hoja_historial(exportar_pdf=False))
        btn_reconstruir.pack(side="left", expand=True, padx=8)
        
        btn_exportar = ctk.CTkButton(f_bot_hist, text="⬇ Exportar a PDF", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=42, command=lambda: self.procesar_hoja_historial(exportar_pdf=True))
        btn_exportar.pack(side="left", expand=True, padx=8)
        
        self.btn_eliminar = ctk.CTkButton(f_bot_hist, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=42, command=self.eliminar_historial)
        self.btn_eliminar.pack(side="left", expand=True, padx=8)
        
        if not self.app.es_jefe:
            self.btn_eliminar.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)


    def refrescar_datos(self):
        # Limpiar ambas tablas
        for i in self.tabla_hist_todo.get_children():
            self.tabla_hist_todo.delete(i)
        for i in self.tabla_hist_mes.get_children():
            self.tabla_hist_mes.delete(i)
            
        todas_intervenciones = []
        for eq in self.app.datos.get("equipos", []):
            for inter in eq.get("historial_intervenciones", []):
                detalle_limpio = inter.get("trabajo") or inter.get("detalle") or ""
                responsable = inter.get("realizado_por") or inter.get("responsable") or inter.get("tecnico") or ""
                todas_intervenciones.append({
                    "fecha": inter["fecha"],
                    "hora": inter.get("hora_entrega") or "",
                    "id": eq["id"],
                    "equipo": eq["nombre"],
                    "tipo": inter["tipo"],
                    "responsable": responsable,
                    "detalle": detalle_limpio,
                    "id_bd": inter.get("id"),
                    "fecha_entrega": inter.get("fecha_entrega") or inter["fecha"]
                })

        # --- 1. RELLENAR TODO EL HISTORIAL ---
        items_todo = list(todas_intervenciones)
        
        # Filtro de búsqueda
        t_todo = self.busqueda_todo_var.get().lower().strip() if hasattr(self, "busqueda_todo_var") else ""
        if t_todo:
            items_todo = [it for it in items_todo if (
                t_todo in str(it["fecha"]).lower() or
                t_todo in str(it["hora"]).lower() or
                t_todo in str(it["id"]).lower() or
                t_todo in str(it["equipo"]).lower() or
                t_todo in str(it["tipo"]).lower() or
                t_todo in str(it["responsable"]).lower() or
                t_todo in str(it["detalle"]).lower()
            )]
            
        # Ordenación
        crit_todo = self.combo_ordenar_todo.get() if hasattr(self, "combo_ordenar_todo") else "Fecha (Reciente)"
        if crit_todo == "Fecha (Reciente)":
            def get_f_h(x):
                f = x.get("fecha_entrega") or x["fecha"]
                h = x["hora"] or "00:00"
                f_str = f.strftime("%Y-%m-%d") if isinstance(f, (date, datetime)) else str(f)
                return (f_str, h, x.get("id_bd") or 0)
            items_todo.sort(key=get_f_h, reverse=True)
        elif crit_todo == "Fecha (Antiguo)":
            def get_f_h(x):
                f = x.get("fecha_entrega") or x["fecha"]
                h = x["hora"] or "00:00"
                f_str = f.strftime("%Y-%m-%d") if isinstance(f, (date, datetime)) else str(f)
                return (f_str, h, x.get("id_bd") or 0)
            items_todo.sort(key=get_f_h)
        elif crit_todo == "Equipo (A-Z)":
            items_todo.sort(key=lambda x: str(x["equipo"]).lower())
        elif crit_todo == "Equipo (Z-A)":
            items_todo.sort(key=lambda x: str(x["equipo"]).lower(), reverse=True)
        elif crit_todo == "Responsable":
            items_todo.sort(key=lambda x: str(x["responsable"]).lower())
            
        for inter in items_todo:
            self.tabla_hist_todo.insert("", "end", values=(inter["fecha"], inter["hora"], inter["id"], inter["equipo"], inter["tipo"], inter["responsable"], inter["detalle"], inter["id_bd"]))

        # --- 2. RELLENAR HISTORIAL MENSUAL ---
        mes_nombre = self.combo_mes.get() if hasattr(self, "combo_mes") else "Enero"
        anio_str = self.combo_anio.get() if hasattr(self, "combo_anio") else str(datetime.now().year)
        
        meses_dict = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
            "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }
        mes_num = meses_dict.get(mes_nombre, 1)
        
        items_mes = []
        for inter in todas_intervenciones:
            f_val = inter["fecha"]
            if isinstance(f_val, str):
                try:
                    dt = datetime.strptime(f_val, "%Y-%m-%d").date()
                except:
                    continue
            elif isinstance(f_val, date):
                dt = f_val
            else:
                continue
                
            if dt.month == mes_num and str(dt.year) == anio_str:
                items_mes.append(inter)
                
        # Filtro de búsqueda mensual
        t_mes = self.busqueda_mes_var.get().lower().strip() if hasattr(self, "busqueda_mes_var") else ""
        if t_mes:
            items_mes = [it for it in items_mes if (
                t_mes in str(it["fecha"]).lower() or
                t_mes in str(it["id"]).lower() or
                t_mes in str(it["equipo"]).lower() or
                t_mes in str(it["tipo"]).lower() or
                t_mes in str(it["responsable"]).lower() or
                t_mes in str(it["detalle"]).lower()
            )]
            
        # Ordenación mensual
        crit_mes = self.combo_ordenar_mes.get() if hasattr(self, "combo_ordenar_mes") else "Fecha (Reciente)"
        if crit_mes == "Fecha (Reciente)":
            def get_f_h(x):
                f = x.get("fecha_entrega") or x["fecha"]
                h = x["hora"] or "00:00"
                f_str = f.strftime("%Y-%m-%d") if isinstance(f, (date, datetime)) else str(f)
                return (f_str, h, x.get("id_bd") or 0)
            items_mes.sort(key=get_f_h, reverse=True)
        elif crit_mes == "Fecha (Antiguo)":
            def get_f_h(x):
                f = x.get("fecha_entrega") or x["fecha"]
                h = x["hora"] or "00:00"
                f_str = f.strftime("%Y-%m-%d") if isinstance(f, (date, datetime)) else str(f)
                return (f_str, h, x.get("id_bd") or 0)
            items_mes.sort(key=get_f_h)
        elif crit_mes == "Equipo (A-Z)":
            items_mes.sort(key=lambda x: str(x["equipo"]).lower())
        elif crit_mes == "Equipo (Z-A)":
            items_mes.sort(key=lambda x: str(x["equipo"]).lower(), reverse=True)
        elif crit_mes == "Responsable":
            items_mes.sort(key=lambda x: str(x["responsable"]).lower())
            
        for inter in items_mes:
            self.tabla_hist_mes.insert("", "end", values=(inter["fecha"], inter["hora"], inter["id"], inter["equipo"], inter["tipo"], inter["responsable"], inter["detalle"], inter["id_bd"]))

    def obtener_seleccion(self):
        # Devolver selección de la pestaña activa
        tab_activa = self.tabview_hist.get()
        if tab_activa == "📋 Todo el Historial":
            sel = self.tabla_hist_todo.focus()
            return self.tabla_hist_todo.item(sel, "values") if sel else None
        else:
            sel = self.tabla_hist_mes.focus()
            return self.tabla_hist_mes.item(sel, "values") if sel else None

    def eliminar_historial(self):
        if not self.app.es_jefe:
            return
            
        valores = self.obtener_seleccion()
        if not valores:
            messagebox.showwarning("Aviso", "Seleccione un mantenimiento del historial primero.")
            return
            
        id_bd = valores[7] # ID_BD
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar la intervención del {valores[0]}?"):
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM historial_intervenciones WHERE id = %s", (id_bd,))
                fila = cur.fetchone()
                if fila:
                    mover_a_papelera(cur, "historial_intervenciones", id_bd, dict(fila), self.app.usuario_actual.get("nombre_usuario", "jefe"))
                cur.execute("DELETE FROM historial_intervenciones WHERE id = %s", (id_bd,))
                conn.commit()
                cur.close()
                conn.close()
                
                self.app.cargar_datos_memoria()
                self.refrescar_datos()
                messagebox.showinfo("Éxito", "Eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error SQL", str(e))

    def procesar_hoja_historial(self, exportar_pdf=False):
        valores = self.obtener_seleccion()
        if not valores:
            messagebox.showwarning("Aviso", "Seleccione un mantenimiento del historial primero.")
            return
            
        fecha_str = valores[0]
        id_eq = valores[2] # ID Equipo
        id_bd = valores[7] # ID_BD
        
        eq_data = next((e for e in self.app.datos["equipos"] if str(e["id"]) == str(id_eq)), None)
        if not eq_data:
            messagebox.showerror("Error", "No se encontró el equipo en la base de datos.")
            return
            
        inter = next((i for i in eq_data.get("historial_intervenciones", []) if str(i.get("id")) == str(id_bd)), None)
        if not inter:
            messagebox.showerror("Error", "No se encontró el detalle de la intervención.")
            return

        condicion = inter.get("condicion", "")
        estado_eq = inter.get("estado_equipo", "")
        defic = inter.get("deficiencia", "")
        trabajo = inter.get("trabajo", inter.get("detalle", ""))
        obs = inter.get("observaciones", "")
        f_entrega_raw = inter.get("fecha_entrega", fecha_str)
        serv_ht = inter.get("servicio_ht", "")
        tipo_ht = inter.get("tipo_ht", "")

        ruta_plantilla_ht = obtener_ruta_plantilla("plantilla_trabajo.xlsx")
        if not os.path.exists(ruta_plantilla_ht):
            messagebox.showerror("Error", f"No se encontró la plantilla en:\n{ruta_plantilla_ht}")
            return

        try:
            wb = openpyxl.load_workbook(ruta_plantilla_ht)
            ws = wb.active
            
            # Escribir campos de cabecera y equipo
            escribir_en_celda_segura(ws, 'F11', eq_data.get('area', ''))
            escribir_en_celda_segura(ws, 'AA11', serv_ht or eq_data.get('servicio', ''))
            escribir_en_celda_segura(ws, 'S21', tipo_ht or '1')
            escribir_en_celda_segura(ws, 'J15', eq_data.get('nombre', ''))
            escribir_en_celda_segura(ws, 'AE15', str(eq_data.get('id', '')))
            escribir_en_celda_segura(ws, 'E17', eq_data.get('procedencia', ''))
            escribir_en_celda_segura(ws, 'AB17', str(eq_data.get('anio_fab', '')))
            escribir_en_celda_segura(ws, 'E19', eq_data.get('marca', ''))
            escribir_en_celda_segura(ws, 'AB19', eq_data.get('fabricante', ''))
            escribir_en_celda_segura(ws, 'F21', eq_data.get('modelo', ''))
            escribir_en_celda_segura(ws, 'AG21', eq_data.get('numero_serie', ''))
            
            # Fechas
            f_rec_raw = inter.get('fecha')
            try:
                if isinstance(f_rec_raw, (date, datetime)):
                    f_rec_str = f_rec_raw.strftime('%d / %m / %Y')
                else:
                    f_rec_dt = datetime.strptime(str(f_rec_raw), '%Y-%m-%d').date()
                    f_rec_str = f_rec_dt.strftime('%d / %m / %Y')
            except:
                f_rec_str = str(f_rec_raw)
            escribir_en_celda_segura(ws, 'M23', f_rec_str)
            h_ent = inter.get("hora_entrega") or ""
            f_ent_raw = inter.get("fecha_entrega") or inter.get("fecha") or ""
            try:
                if isinstance(f_ent_raw, (date, datetime)):
                    f_ent_str = f_ent_raw.strftime('%d / %m / %Y')
                else:
                    f_ent_dt = datetime.strptime(str(f_ent_raw), '%Y-%m-%d').date()
                    f_ent_str = f_ent_dt.strftime('%d / %m / %Y')
            except:
                f_ent_str = str(f_ent_raw)
                
            if f_ent_str and h_ent:
                escribir_en_celda_segura(ws, 'I62', f"{f_ent_str}  {h_ent}")
            elif f_ent_str:
                escribir_en_celda_segura(ws, 'I62', f_ent_str)
            else:
                escribir_en_celda_segura(ws, 'I62', h_ent)

            # Nombre del técnico firmante responsable
            realizado = inter.get('realizado_por') or inter.get('responsable') or ''
            escribir_en_celda_segura(ws, 'J64', realizado)
            
            # Inyectar sello/firma (Imagen) si existe en la BD
            if realizado:
                try:
                    conn = obtener_conexion()
                    cur = conn.cursor()
                    cur.execute("SELECT sello_firma FROM usuarios WHERE nombre_completo = %s", (realizado,))
                    row = cur.fetchone()
                    cur.close()
                    conn.close()
                    if row and row[0]:
                        sello_firma_path = row[0]
                        if os.path.exists(sello_firma_path):
                            from openpyxl.drawing.image import Image as ExcelImage
                            img = ExcelImage(sello_firma_path)
                            img.width = 145
                            img.height = 65
                            ws.add_image(img, 'AD60')
                except Exception as ex:
                    print(f"[ERROR] No se pudo insertar la firma en reconstrucción: {ex}")

            # Condición
            if condicion == "Óptimo": marcar_x(ws, 'P26')
            elif condicion == "Aceptable": marcar_x(ws, 'W26')
            elif condicion == "Crítica": marcar_x(ws, 'AC26')
            elif condicion == "Inoperante": marcar_x(ws, 'AJ26')
            elif condicion == "F/Servicio": marcar_x(ws, 'AP26')

            # Estado Físico
            if estado_eq == "Óptimo": marcar_x(ws, 'O29')
            elif estado_eq == "Bueno": marcar_x(ws, 'U29')
            elif estado_eq == "Regular": marcar_x(ws, 'AB29')
            elif estado_eq == "Malo": marcar_x(ws, 'AH29')
            elif estado_eq == "Obsoleto": marcar_x(ws, 'AO29')

            # Tipo Mantenimiento
            if inter.get("tipo", "") == "Preventivo": marcar_x(ws, 'Q43')
            else: marcar_x(ws, 'AL43')

            # Textos largos
            escribir_texto_largo(ws, 'B33', defic)
            escribir_texto_largo(ws, 'B47', trabajo)
            escribir_texto_largo(ws, 'B53', obs)

            # Inyectar repuestos si los tiene registrados
            rep_nombre = inter.get("repuesto_nombre")
            rep_cant = inter.get("repuesto_cantidad")
            if rep_nombre:
                escribir_en_celda_segura(ws, 'E56', rep_nombre)
                if rep_cant:
                    escribir_en_celda_segura(ws, 'AG56', str(rep_cant))
            
            # Guardar archivo en la subcarpeta del área correspondiente
            area_name = eq_data.get("area", "General")
            area_folder = "".join([c for c in area_name if c.isalnum() or c==' ']).strip()
            dir_mantenimiento = os.path.join(CARPETAS["areas"], area_folder, "mantenimientos")
            os.makedirs(dir_mantenimiento, exist_ok=True)
            
            nom_arch = f"HT_{id_eq}_{fecha_str.replace('-','')}.xlsx"
            ruta_guardar = os.path.join(dir_mantenimiento, nom_arch)
            wb.save(ruta_guardar)
            
            if exportar_pdf:
                pdf_arch = nom_arch.replace(".xlsx", ".pdf")
                ruta_pdf = os.path.join(dir_mantenimiento, pdf_arch)
                exportar_excel_a_pdf(ruta_guardar, ruta_pdf, rango_impresion="$A$1:$AR$67")
                try:
                    os.startfile(ruta_pdf)
                except Exception as ex:
                    print("[ERROR] No se pudo abrir el PDF automáticamente:", ex)
                messagebox.showinfo("Éxito", f"Orden de Trabajo exportada en PDF:\n{ruta_pdf}")
            else:
                try:
                    os.startfile(ruta_guardar)
                except Exception as ex:
                    print("[ERROR] No se pudo abrir el Excel automáticamente:", ex)
                messagebox.showinfo("Éxito", f"Orden de Trabajo guardada en Excel:\n{ruta_guardar}")
        except Exception as e:
            messagebox.showerror("Error al procesar", str(e))