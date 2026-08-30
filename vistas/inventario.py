# vistas/inventario.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import json
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera, calcular_proximos_mantenimientos
from estilos import *
from datetime import date, datetime

class VistaInventario(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(pady=(30, 10), padx=30, fill="x")
        ctk.CTkLabel(f_top, text="Inventario de Equipos", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", lambda *args: self.refrescar_datos())
        
        # Caja de búsqueda con etiqueta explícita "🔍 Buscar:"
        f_search = ctk.CTkFrame(f_top, fg_color="transparent")
        f_search.pack(side="right")
        ctk.CTkLabel(f_search, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar = ctk.CTkEntry(f_search, textvariable=self.busqueda_var, placeholder_text="Buscar ID, Equipo o Servicio...", width=250, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar.pack(side="left")

        # Barra de Ordenación/Filtros
        f_filtros = ctk.CTkFrame(self, fg_color="transparent")
        f_filtros.pack(pady=(5, 10), padx=30, fill="x")
        ctk.CTkLabel(f_filtros, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(0, 5))
        self.combo_ordenar = ctk.CTkComboBox(f_filtros, values=["Siguiente Mantenimiento", "Equipo (A-Z)", "Equipo (Z-A)", "Fecha Registro", "Garantía"], command=lambda e: self.refrescar_datos(), width=180, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar.pack(side="left")
        self.combo_ordenar.set("Siguiente Mantenimiento")

        marco_tabla = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        marco_tabla.pack(pady=10, padx=30, fill="both", expand=True)
        cols = ("Equipo", "Marca", "Modelo", "Serie", "Código/AF", "Servicio", "Siguiente Mantenimiento")
        f_tree_inv = ctk.CTkFrame(marco_tabla, fg_color="transparent")
        f_tree_inv.pack(pady=12, padx=12, fill="both", expand=True)
        self.tabla_inv = ttk.Treeview(f_tree_inv, columns=cols, show="headings")
        scrollbar_inv = ttk.Scrollbar(f_tree_inv, orient="vertical", command=self.tabla_inv.yview, style="Vertical.TScrollbar")
        self.tabla_inv.configure(yscrollcommand=scrollbar_inv.set)
        self.tabla_inv.tag_configure("Sin Garantia", background="#FFFFFF", foreground=C_TEXT)
        self.tabla_inv.tag_configure("Con Garantia", background="#F8FAFC", foreground=C_SUBTEXT)
        self.tabla_inv.tag_configure("Garantia Vencer", background="#FEF3C7", foreground="#B45309")
        
        widths = {
            "Equipo": 180,
            "Marca": 100,
            "Modelo": 100,
            "Serie": 100,
            "Código/AF": 120,
            "Servicio": 120,
            "Siguiente Mantenimiento": 200
        }
        for c in cols:
            self.tabla_inv.heading(c, text=c, command=lambda _c=c: self.ordenar_columna(_c, False))
            self.tabla_inv.column(c, anchor="center", width=widths.get(c, 100))
        self.tabla_inv.pack(side="left", fill="both", expand=True)
        scrollbar_inv.pack(side="right", fill="y", padx=(5, 0))
        self.tabla_inv.bind("<Double-1>", lambda e: self.app.abrir_hoja_vida_click(e))

        f_bot = ctk.CTkFrame(self, fg_color="transparent")
        f_bot.pack(pady=(10, 25), padx=30, fill="x")
        ctk.CTkButton(f_bot, text="✚ Registrar Equipo", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=42, command=self.registrar_equipo).pack(side="left", expand=True, padx=8)
        self.btn_modificar = ctk.CTkButton(f_bot, text="✎ Modificar Ficha", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=42, command=self.modificar_equipo)
        self.btn_modificar.pack(side="left", expand=True, padx=8)
        self.btn_eliminar = ctk.CTkButton(f_bot, text="🗑 Eliminar Activo", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=42, command=self.eliminar_equipo)
        self.btn_eliminar.pack(side="left", expand=True, padx=8)
        if not self.app.es_jefe:
            self.btn_eliminar.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)
            self.btn_modificar.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)


    def obtener_id_seleccionado(self):
        sel = self.tabla_inv.focus()
        if not sel:
            return None
        valores = self.tabla_inv.item(sel, "values")
        return valores[4] if len(valores) > 4 else None

    def refrescar_datos(self):
        for i in self.tabla_inv.get_children(): 
            self.tabla_inv.delete(i)
        
        equipos = list(self.app.datos.get("equipos", []))
        
        # Filtro territorial / Sede activa
        contexto = getattr(self.app, "contexto_sede", None)
        if contexto and not contexto.get("es_global", True):
            cen_id = contexto.get("centro_salud_id")
            cen_nom = contexto.get("centro_salud")
            red_id = contexto.get("red_salud_id")
            red_nom = contexto.get("red_salud")

            if cen_id or (cen_nom and not str(cen_nom).startswith("[ Todos")):
                equipos = [eq for eq in equipos if 
                           (cen_id and eq.get("centro_salud_id") == cen_id) or 
                           (cen_nom and str(eq.get("centro_salud_nombre", "")).strip().lower() == str(cen_nom).strip().lower()) or
                           (cen_nom and str(eq.get("servicio", "")).strip().lower() == str(cen_nom).strip().lower())]
            elif red_id or (red_nom and not str(red_nom).startswith("[ Todas")):
                equipos = [eq for eq in equipos if 
                           (red_id and eq.get("red_salud_id") == red_id) or 
                           (red_nom and str(eq.get("red_salud_nombre", "")).strip().lower() == str(red_nom).strip().lower())]

        # Asegurar que f_prox esté calculado para todos los equipos
        for eq in equipos:
            if eq.get("f_prox") is None and eq.get("estado") != "Baja":
                proximos = calcular_proximos_mantenimientos(eq, cantidad=1, hoy=getattr(self.app, "hoy", date.today()))
                if proximos:
                    eq["f_prox"] = proximos[0]
        
        # Filtro de búsqueda
        t = self.busqueda_var.get().lower().strip()
        if t:
            equipos = [eq for eq in equipos if (
                t in str(eq["id"]).lower() or 
                t in str(eq["nombre"]).lower() or 
                t in str(eq.get("servicio", "")).lower() or
                t in str(eq.get("marca", "")).lower() or
                t in str(eq.get("modelo", "")).lower()
            )]
            
        # Ordenación
        criterio = self.combo_ordenar.get() if hasattr(self, "combo_ordenar") else "Siguiente Mantenimiento"
        if criterio == "Equipo (A-Z)":
            equipos.sort(key=lambda x: str(x.get("nombre", "")).lower())
        elif criterio == "Equipo (Z-A)":
            equipos.sort(key=lambda x: str(x.get("nombre", "")).lower(), reverse=True)
        elif criterio == "Fecha Registro":
            def get_fecha_reg(x):
                f = x.get("fecha_registro")
                if not f: return date.min
                if isinstance(f, str):
                    try: return datetime.strptime(f, "%Y-%m-%d").date()
                    except: return date.min
                return f
            equipos.sort(key=get_fecha_reg, reverse=True)
        elif criterio == "Garantía":
            equipos.sort(key=lambda x: x.get("garantia") == "Con Garantía", reverse=True)
        else: # "Siguiente Mantenimiento"
            def get_siguiente_mtto_date(eq):
                if eq.get("estado") == "Baja":
                    return date.max
                
                # Chequear garantía
                gar = eq.get("garantia", "Sin Garantía")
                f_venc_g = eq.get("fecha_vencimiento_garantia")
                esta_en_gar = False
                if gar == "Con Garantía" and f_venc_g:
                    try:
                        if isinstance(f_venc_g, str):
                            f_venc_g_dt = datetime.strptime(f_venc_g, "%Y-%m-%d").date()
                        else:
                            f_venc_g_dt = f_venc_g
                        if f_venc_g_dt and f_venc_g_dt >= date.today():
                            esta_en_gar = True
                    except:
                        pass
                if esta_en_gar:
                    return date(9999, 12, 30) # justo antes de Baja
                
                f_prox = eq.get("f_prox")
                if not f_prox:
                    return date.max
                if isinstance(f_prox, str):
                    try:
                        return datetime.strptime(f_prox, "%Y-%m-%d").date()
                    except:
                        return date.max
                return f_prox
                
            equipos.sort(key=get_siguiente_mtto_date)

        for eq in equipos:
            # 1. Determinar tag de garantía para colorear fila
            gar = eq.get("garantia", "Sin Garantía")
            f_venc = eq.get("fecha_vencimiento_garantia")
            tag_gar = "Sin Garantia"
            esta_en_garantia = False
            f_venc_str = ""
            
            if gar == "Con Garantía" and f_venc:
                if isinstance(f_venc, str):
                    try: f_venc = datetime.strptime(f_venc, "%Y-%m-%d").date()
                    except: f_venc = None
                if f_venc:
                    dias = (f_venc - date.today()).days
                    if dias < 0:
                        tag_gar = "Sin Garantia"
                    elif dias <= 30:
                        tag_gar = "Garantia Vencer"
                        esta_en_garantia = True
                        f_venc_str = f_venc.strftime('%d / %m / %Y')
                    else:
                        tag_gar = "Con Garantia"
                        esta_en_garantia = True
                        f_venc_str = f_venc.strftime('%d / %m / %Y')

            # 2. Formatear Siguiente Mantenimiento
            f_prox_val = eq.get("f_prox")
            if not f_prox_val and eq.get("estado") != "Baja":
                proximos = calcular_proximos_mantenimientos(eq, cantidad=1, hoy=getattr(self.app, "hoy", date.today()))
                if proximos:
                    f_prox_val = proximos[0]
                    eq["f_prox"] = f_prox_val

            if eq.get("estado") == "Baja":
                txt_siguiente = "Dado de Baja"
            elif esta_en_garantia:
                txt_siguiente = f"En Garantía (hasta {f_venc_str})"
            elif f_prox_val:
                try:
                    if isinstance(f_prox_val, str):
                        f_prox_dt = datetime.strptime(f_prox_val, "%Y-%m-%d").date()
                    else:
                        f_prox_dt = f_prox_val
                    txt_siguiente = f_prox_dt.strftime('%d / %m / %Y')
                except:
                    txt_siguiente = str(f_prox_val)
            else:
                txt_siguiente = "-"

            # Insertar en la tabla: cols = ("Equipo", "Marca", "Modelo", "Serie", "Código/AF", "Servicio", "Siguiente Mantenimiento")
            self.tabla_inv.insert("", "end", values=(
                eq.get("nombre", ""),
                eq.get("marca", ""),
                eq.get("modelo", ""),
                eq.get("numero_serie", ""),
                eq.get("id", ""),
                eq.get("servicio", ""),
                txt_siguiente
            ), tags=(tag_gar,))

    def ordenar_columna(self, col, reverse):
        datos = [(self.tabla_inv.set(k, col), k) for k in self.tabla_inv.get_children("")]
        datos.sort(reverse=reverse)
        for i, (val, k) in enumerate(datos): self.tabla_inv.move(k, "", i)
        self.tabla_inv.heading(col, command=lambda: self.ordenar_columna(col, not reverse))

    def registrar_equipo(self):
        if getattr(self.app, "modo_offline", False):
            from tkinter import messagebox
            messagebox.showwarning("Modo Sin Conexión", "La creación de nuevos equipos está deshabilitada en Modo Fuera de Línea.\n\nDebes conectarte a la red del Servidor Central para registrar nuevos activos.")
            return
        self.app.abrir_formulario_equipo()

    def modificar_equipo(self):
        from tkinter import messagebox
        if getattr(self.app, "modo_offline", False):
            messagebox.showwarning("Modo Sin Conexión", "La modificación de fichas técnicas está deshabilitada en Modo Fuera de Línea (Solo Lectura).\n\nConéctate a la red del Servidor Central para guardar cambios.")
            return
        if not self.app.es_jefe:
            messagebox.showerror("Permiso denegado", "Solo el Jefe de servicio puede modificar fichas técnicas.")
            return
        eq_id = self.obtener_id_seleccionado()
        if not eq_id: return
        eq = next((e for e in self.app.datos["equipos"] if str(e["id"]) == str(eq_id)), None)
        if eq: self.app.abrir_formulario_equipo(eq)

    def eliminar_equipo(self):
        from tkinter import messagebox
        if getattr(self.app, "modo_offline", False):
            messagebox.showwarning("Modo Sin Conexión", "La eliminación de equipos está deshabilitada en Modo Fuera de Línea.\n\nDebes estar conectado al Servidor Central.")
            return
        if not self.app.es_jefe:
            messagebox.showerror("Permiso denegado", "Solo el Jefe puede dar de baja activos.")
            return
        eq_id = self.obtener_id_seleccionado()
        if not eq_id: return
        if messagebox.askyesno("Confirmar Baja", f"¿Eliminar permanentemente el equipo {eq_id}?"):
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM equipos WHERE id = %s", (eq_id,))
                fila = cur.fetchone()
                if fila:
                    mover_a_papelera(cur, "equipos", eq_id, dict(fila), self.app.usuario_actual.get("nombre_usuario", "jefe"))
                cur.execute("DELETE FROM equipos WHERE id = %s", (eq_id,))
                conn.commit()
                cur.close(); conn.close()
                self.app.cargar_datos_memoria()
                self.refrescar_datos()
                messagebox.showinfo("Éxito", "Activo eliminado correctamente.")
            except Exception as e: messagebox.showerror("Error", str(e))