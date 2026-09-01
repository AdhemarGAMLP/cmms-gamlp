# vistas/repuestos.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera, ejecutar_en_segundo_plano, guardar_cache_local_datos, comprimir_imagen_base64, obtener_jerarquia_sedes_db
from estilos import *
from datetime import date, datetime
import os
from generador_repuestos_excel import guardar_excel_repuestos

class VistaRepuestos(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        f_title = ctk.CTkFrame(self, fg_color="transparent")
        f_title.pack(pady=(20, 5), padx=30, fill="x")
        ctk.CTkLabel(f_title, text="Control de Repuestos y Accesorios", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        # Barra de Pestañas con Contorno Elegante y Alto Contraste
        f_tab_bar_outer = ctk.CTkFrame(self, fg_color="transparent")
        f_tab_bar_outer.pack(padx=30, pady=(10, 0), fill="x")

        self.f_tab_bar = ctk.CTkFrame(f_tab_bar_outer, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        self.f_tab_bar.pack(side="left")

        self.btn_tab_stock = ctk.CTkButton(self.f_tab_bar, text="📦 Repuestos en Stock", font=ctk.CTkFont(weight="bold", size=13),
                                          corner_radius=8, height=36, command=lambda: self.cambiar_tab("stock"))
        self.btn_tab_stock.pack(side="left", padx=4, pady=4)

        self.btn_tab_req = ctk.CTkButton(self.f_tab_bar, text="📋 Repuestos Requeridos (Necesarios)", font=ctk.CTkFont(weight="bold", size=13),
                                        corner_radius=8, height=36, command=lambda: self.cambiar_tab("req"))
        self.btn_tab_req.pack(side="left", padx=4, pady=4)

        self.btn_tab_hist = ctk.CTkButton(self.f_tab_bar, text="📜 Historial de Repuestos Usados", font=ctk.CTkFont(weight="bold", size=13),
                                         corner_radius=8, height=36, command=lambda: self.cambiar_tab("hist"))
        self.btn_tab_hist.pack(side="left", padx=4, pady=4)

        # Contenedor Principal de Contenido
        self.f_contenedor_tabs = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        self.f_contenedor_tabs.pack(padx=30, pady=10, fill="both", expand=True)

        self.tab_stock = ctk.CTkFrame(self.f_contenedor_tabs, fg_color="transparent")
        self.tab_req = ctk.CTkFrame(self.f_contenedor_tabs, fg_color="transparent")
        self.tab_hist = ctk.CTkFrame(self.f_contenedor_tabs, fg_color="transparent")

        # =========================================================================
        # --- TAB 1: REPUESTOS EN STOCK (DISPONIBLES) ---
        # =========================================================================
        marco_stock = ctk.CTkFrame(self.tab_stock, fg_color="transparent")
        marco_stock.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filtros de Stock
        f_filtros_stock = ctk.CTkFrame(marco_stock, fg_color="transparent")
        f_filtros_stock.pack(fill="x", pady=(0, 10))
        
        self.busqueda_stock_var = ctk.StringVar()
        self.busqueda_stock_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_filtros_stock, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_stock = ctk.CTkEntry(f_filtros_stock, textvariable=self.busqueda_stock_var, placeholder_text="Buscar por Repuesto, Red, Centro, Marca, Modelo...", width=260, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_stock.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_filtros_stock, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_stock = ctk.CTkComboBox(f_filtros_stock, values=["Repuesto (A-Z)", "Repuesto (Z-A)", "Centro de Salud", "Red de Salud", "Cantidad (Mayor)", "Cantidad (Menor)", "Costo (Mayor)"], command=lambda e: self.refrescar_datos(), width=170, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_stock.pack(side="left", padx=5)
        self.combo_ordenar_stock.set("Repuesto (A-Z)")
        
        cols_stock = ("Centro de Salud", "Área", "Repuesto", "Marca", "Modelo / P/N", "Cantidad")
        f_tree_stock = ctk.CTkFrame(marco_stock, fg_color="transparent")
        f_tree_stock.pack(pady=5, padx=5, fill="both", expand=True)
        self.tabla_stock = ttk.Treeview(f_tree_stock, columns=cols_stock, show="headings")
        scrollbar_stock = ttk.Scrollbar(f_tree_stock, orient="vertical", command=self.tabla_stock.yview, style="Vertical.TScrollbar")
        self.tabla_stock.configure(yscrollcommand=scrollbar_stock.set)
        for c in cols_stock:
            self.tabla_stock.heading(c, text=c)
            self.tabla_stock.column(c, anchor="center")
        self.tabla_stock.pack(side="left", fill="both", expand=True)
        scrollbar_stock.pack(side="right", fill="y", padx=(5, 0))
        
        f_bot_stock = ctk.CTkFrame(self.tab_stock, fg_color="transparent")
        f_bot_stock.pack(pady=(5, 15), padx=10, fill="x")
        ctk.CTkButton(f_bot_stock, text="✚ Añadir a Stock", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=40, command=lambda: self.abrir_formulario_repuesto(estado_inicial="En Stock")).pack(side="left", expand=True, padx=6)
        ctk.CTkButton(f_bot_stock, text="📥 Descargar Inventario (.xlsx)", font=ctk.CTkFont(weight="bold", size=13), fg_color="#059669", hover_color="#047857", corner_radius=10, height=40, command=lambda: self.descargar_excel_repuestos(tipo="Stock")).pack(side="left", expand=True, padx=6)
        ctk.CTkButton(f_bot_stock, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=40, command=lambda: self.modificar_repuesto(tabla_origen="stock")).pack(side="left", expand=True, padx=6)
        self.btn_eliminar_stock = ctk.CTkButton(f_bot_stock, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=40, command=lambda: self.eliminar_repuesto(tabla_origen="stock"))
        self.btn_eliminar_stock.pack(side="left", expand=True, padx=6)
        if not self.app.es_jefe: self.btn_eliminar_stock.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)

        # =========================================================================
        # --- TAB 2: REPUESTOS REQUERIDOS (NECESARIOS / PENDIENTES) ---
        # =========================================================================
        marco_req = ctk.CTkFrame(self.tab_req, fg_color="transparent")
        marco_req.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filtros de Requerimientos + KPI resumen
        f_top_req = ctk.CTkFrame(marco_req, fg_color="transparent")
        f_top_req.pack(fill="x", pady=(0, 10))
        
        self.busqueda_req_var = ctk.StringVar()
        self.busqueda_req_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_top_req, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_req = ctk.CTkEntry(f_top_req, textvariable=self.busqueda_req_var, placeholder_text="Buscar Requerimiento, Red, Centro, Marca, P/N...", width=260, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_req.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_top_req, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_req = ctk.CTkComboBox(f_top_req, values=["Repuesto (A-Z)", "Repuesto (Z-A)", "Centro de Salud", "Red de Salud", "Cantidad (Mayor)", "Costo Estimado (Mayor)"], command=lambda e: self.refrescar_datos(), width=180, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_req.pack(side="left", padx=5)
        self.combo_ordenar_req.set("Repuesto (A-Z)")
        
        self.lbl_kpi_req = ctk.CTkLabel(f_top_req, text="Requerimientos: 0 | Total Est.: 0.00 Bs.", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_ORANGE)
        self.lbl_kpi_req.pack(side="right", padx=10)
        
        cols_req = ("Centro de Salud", "Área", "Repuesto Necesario", "Marca", "Modelo / P/N", "Cantidad")
        f_tree_req = ctk.CTkFrame(marco_req, fg_color="transparent")
        f_tree_req.pack(pady=5, padx=5, fill="both", expand=True)
        self.tabla_req = ttk.Treeview(f_tree_req, columns=cols_req, show="headings")
        scrollbar_req = ttk.Scrollbar(f_tree_req, orient="vertical", command=self.tabla_req.yview, style="Vertical.TScrollbar")
        self.tabla_req.configure(yscrollcommand=scrollbar_req.set)
        for c in cols_req:
            self.tabla_req.heading(c, text=c)
            self.tabla_req.column(c, anchor="center")
        self.tabla_req.pack(side="left", fill="both", expand=True)
        scrollbar_req.pack(side="right", fill="y", padx=(5, 0))
        
        f_bot_req = ctk.CTkFrame(self.tab_req, fg_color="transparent")
        f_bot_req.pack(pady=(5, 15), padx=10, fill="x")
        ctk.CTkButton(f_bot_req, text="✚ Solicitar Repuesto", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_ORANGE, hover_color="#D97706", corner_radius=10, height=40, command=lambda: self.abrir_formulario_repuesto(estado_inicial="Requerido")).pack(side="left", expand=True, padx=6)
        ctk.CTkButton(f_bot_req, text="📥 Descargar Requerimientos (.xlsx)", font=ctk.CTkFont(weight="bold", size=13), fg_color="#059669", hover_color="#047857", corner_radius=10, height=40, command=lambda: self.descargar_excel_repuestos(tipo="Requerido")).pack(side="left", expand=True, padx=6)
        ctk.CTkButton(f_bot_req, text="✅ Pasar a Stock", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_GREEN, hover_color=C_GREEN_HOVER, corner_radius=10, height=40, command=self.pasar_a_stock).pack(side="left", expand=True, padx=6)
        ctk.CTkButton(f_bot_req, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=40, command=lambda: self.modificar_repuesto(tabla_origen="req")).pack(side="left", expand=True, padx=6)
        self.btn_eliminar_req = ctk.CTkButton(f_bot_req, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=40, command=lambda: self.eliminar_repuesto(tabla_origen="req"))
        self.btn_eliminar_req.pack(side="left", expand=True, padx=6)
        if not self.app.es_jefe: self.btn_eliminar_req.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)
        
        # =========================================================================
        # --- TAB 3: HISTORIAL DE REPUESTOS USADOS ---
        # =========================================================================
        marco_hist = ctk.CTkFrame(self.tab_hist, fg_color="transparent")
        marco_hist.pack(fill="both", expand=True, padx=10, pady=10)
        
        f_filtros_hist = ctk.CTkFrame(marco_hist, fg_color="transparent")
        f_filtros_hist.pack(fill="x", pady=(0, 10))
        
        self.busqueda_hist_var = ctk.StringVar()
        self.busqueda_hist_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_filtros_hist, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_hist = ctk.CTkEntry(f_filtros_hist, textvariable=self.busqueda_hist_var, placeholder_text="Buscar Equipo, Repuesto, Servicio...", width=240, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
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

        # Mostrar por defecto Tab 1
        self.cambiar_tab("stock")

    def cambiar_tab(self, tab_name):
        self.tab_activa = tab_name
        self.tab_stock.pack_forget()
        self.tab_req.pack_forget()
        self.tab_hist.pack_forget()

        # Inactivos: fondo transparente, texto negro/oscuro legible, borde suave
        for btn in (self.btn_tab_stock, self.btn_tab_req, self.btn_tab_hist):
            btn.configure(fg_color="transparent", text_color=C_TEXT, hover_color="#E2E8F0")

        # Activo: fondo azul vibrante, texto blanco
        if tab_name == "stock":
            self.btn_tab_stock.configure(fg_color=C_BLUE, text_color="#FFFFFF", hover_color=C_BLUE_HOVER)
            self.tab_stock.pack(fill="both", expand=True)
        elif tab_name == "req":
            self.btn_tab_req.configure(fg_color=C_BLUE, text_color="#FFFFFF", hover_color=C_BLUE_HOVER)
            self.tab_req.pack(fill="both", expand=True)
        elif tab_name == "hist":
            self.btn_tab_hist.configure(fg_color=C_BLUE, text_color="#FFFFFF", hover_color=C_BLUE_HOVER)
            self.tab_hist.pack(fill="both", expand=True)

    def refrescar_datos(self):
        todos_rep = list(self.app.datos.get("repuestos", []))
        
        # 1. Separar por Estado de Disponibilidad
        rep_stock = [r for r in todos_rep if str(r.get("estado_disponibilidad", "En Stock")).strip().lower() != "requerido"]
        rep_req = [r for r in todos_rep if str(r.get("estado_disponibilidad", "En Stock")).strip().lower() == "requerido"]
        
        # --- TAB 1: STOCK ---
        for i in self.tabla_stock.get_children(): 
            self.tabla_stock.delete(i)
            
        t_stock = self.busqueda_stock_var.get().lower().strip()
        if t_stock:
            rep_stock = [r for r in rep_stock if (
                t_stock in str(r.get("nombre_repuesto", "")).lower() or
                t_stock in str(r.get("red_salud_nombre", "")).lower() or
                t_stock in str(r.get("centro_salud_nombre", "")).lower() or
                t_stock in str(r.get("area", "")).lower() or
                t_stock in str(r.get("marca", "")).lower() or
                t_stock in str(r.get("modelo", "")).lower() or
                t_stock in str(r.get("modelo_parte", "")).lower() or
                t_stock in str(r.get("tipo_equipo", "")).lower() or
                t_stock in str(r.get("caracteristicas", "")).lower() or
                t_stock in str(r.get("observaciones", "")).lower()
            )]
            
        crit_stock = self.combo_ordenar_stock.get() if hasattr(self, "combo_ordenar_stock") else "Repuesto (A-Z)"
        if crit_stock == "Repuesto (A-Z)":
            rep_stock.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower())
        elif crit_stock == "Repuesto (Z-A)":
            rep_stock.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower(), reverse=True)
        elif crit_stock == "Centro de Salud":
            rep_stock.sort(key=lambda x: str(x.get("centro_salud_nombre", "")).lower())
        elif crit_stock == "Red de Salud":
            rep_stock.sort(key=lambda x: str(x.get("red_salud_nombre", "")).lower())
        elif crit_stock == "Cantidad (Mayor)":
            rep_stock.sort(key=lambda x: int(x.get("cantidad", 0) or 0), reverse=True)
        elif crit_stock == "Cantidad (Menor)":
            rep_stock.sort(key=lambda x: int(x.get("cantidad", 0) or 0))
        elif crit_stock == "Costo (Mayor)":
            rep_stock.sort(key=lambda x: float(x.get("costo", 0) or 0), reverse=True)
            
        for r in rep_stock:
            cant_val = int(r.get("cantidad", 0) or 0)
            self.tabla_stock.insert("", "end", values=(
                r.get("centro_salud_nombre") or "-",
                r.get("area") or "-",
                r.get("nombre_repuesto", ""),
                r.get("marca") or "-",
                r.get("modelo") or r.get("modelo_parte") or "-",
                cant_val
            ))
        
        # --- TAB 2: REQUERIMIENTOS ---
        for i in self.tabla_req.get_children(): 
            self.tabla_req.delete(i)
            
        t_req = self.busqueda_req_var.get().lower().strip()
        if t_req:
            rep_req = [r for r in rep_req if (
                t_req in str(r.get("nombre_repuesto", "")).lower() or
                t_req in str(r.get("red_salud_nombre", "")).lower() or
                t_req in str(r.get("centro_salud_nombre", "")).lower() or
                t_req in str(r.get("area", "")).lower() or
                t_req in str(r.get("marca", "")).lower() or
                t_req in str(r.get("modelo", "")).lower() or
                t_req in str(r.get("modelo_parte", "")).lower() or
                t_req in str(r.get("tipo_equipo", "")).lower() or
                t_req in str(r.get("caracteristicas", "")).lower() or
                t_req in str(r.get("observaciones", "")).lower()
            )]
            
        crit_req = self.combo_ordenar_req.get() if hasattr(self, "combo_ordenar_req") else "Repuesto (A-Z)"
        if crit_req == "Repuesto (A-Z)":
            rep_req.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower())
        elif crit_req == "Repuesto (Z-A)":
            rep_req.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower(), reverse=True)
        elif crit_req == "Centro de Salud":
            rep_req.sort(key=lambda x: str(x.get("centro_salud_nombre", "")).lower())
        elif crit_req == "Red de Salud":
            rep_req.sort(key=lambda x: str(x.get("red_salud_nombre", "")).lower())
        elif crit_req == "Cantidad (Mayor)":
            rep_req.sort(key=lambda x: int(x.get("cantidad", 0) or 0), reverse=True)
        elif crit_req == "Costo Estimado (Mayor)":
            rep_req.sort(key=lambda x: float(x.get("costo", 0) or 0) * int(x.get("cantidad", 0) or 0), reverse=True)
            
        total_inversion_req = 0.0
        for r in rep_req:
            cant_r = int(r.get("cantidad", 0) or 0)
            costo_u = float(r.get("costo", 0) or 0)
            total_inversion_req += cant_r * costo_u
            
            self.tabla_req.insert("", "end", values=(
                r.get("centro_salud_nombre") or "-",
                r.get("area") or "-",
                r.get("nombre_repuesto", ""),
                r.get("marca") or "-",
                r.get("modelo") or r.get("modelo_parte") or "-",
                cant_r
            ))
            
        if hasattr(self, "lbl_kpi_req"):
            self.lbl_kpi_req.configure(text=f"Requerimientos: {len(rep_req)} | Total Estimado: {total_inversion_req:,.2f} Bs.")
        
        # --- TAB 3: HISTORIAL DE REPUESTOS USADOS ---
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
                
            t_hist = self.busqueda_hist_var.get().lower().strip()
            if t_hist:
                historial_datos = [h for h in historial_datos if (
                    t_hist in str(h["eq_id"]).lower() or
                    t_hist in str(h["eq_nombre"]).lower() or
                    t_hist in str(h.get("eq_servicio", "")).lower() or
                    t_hist in str(h.get("eq_area", "")).lower() or
                    t_hist in str(h.get("repuesto_nombre", "")).lower()
                )]
                
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

    def obtener_seleccion(self, tabla_origen="stock"):
        tabla = self.tabla_stock if tabla_origen == "stock" else self.tabla_req
        sel = tabla.focus()
        return tabla.item(sel, "values") if sel else None

    def descargar_excel_repuestos(self, tipo="Stock"):
        try:
            todos_rep = list(self.app.datos.get("repuestos", []))
            tipo_filtro = str(tipo).strip().lower()
            
            if tipo_filtro in ["stock", "inventario", "en stock"]:
                rep_filtrados = [r for r in todos_rep if str(r.get("estado_disponibilidad", "En Stock")).strip().lower() != "requerido"]
                t_busqueda = self.busqueda_stock_var.get().lower().strip()
                nombre_defecto = f"Inventario_Repuestos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            else:
                rep_filtrados = [r for r in todos_rep if str(r.get("estado_disponibilidad", "En Stock")).strip().lower() == "requerido"]
                t_busqueda = self.busqueda_req_var.get().lower().strip()
                nombre_defecto = f"Repuestos_Requeridos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            if t_busqueda:
                rep_filtrados = [r for r in rep_filtrados if (
                    t_busqueda in str(r.get("nombre_repuesto", "")).lower() or
                    t_busqueda in str(r.get("red_salud_nombre", "")).lower() or
                    t_busqueda in str(r.get("centro_salud_nombre", "")).lower() or
                    t_busqueda in str(r.get("area", "")).lower() or
                    t_busqueda in str(r.get("marca", "")).lower() or
                    t_busqueda in str(r.get("modelo", "")).lower() or
                    t_busqueda in str(r.get("modelo_parte", "")).lower() or
                    t_busqueda in str(r.get("tipo_equipo", "")).lower()
                )]

            if not rep_filtrados:
                messagebox.showinfo("Sin Datos", f"No hay repuestos registrados en '{tipo}' para exportar.")
                return

            ruta_guardar = filedialog.asksaveasfilename(
                title=f"Guardar Lista de Repuestos ({tipo})",
                defaultextension=".xlsx",
                initialfile=nombre_defecto,
                filetypes=[("Archivos Excel", "*.xlsx")]
            )
            if not ruta_guardar:
                return

            guardar_excel_repuestos(rep_filtrados, tipo=tipo, ruta_salida=ruta_guardar)
            
            try:
                os.startfile(ruta_guardar)
            except Exception as oe:
                print(f"[WARN] No se pudo abrir automáticamente el archivo: {oe}")

            messagebox.showinfo("Exportación Exitosa", f"Se generó correctamente la lista con {len(rep_filtrados)} repuestos en:\n\n{os.path.basename(ruta_guardar)}")
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"Ocurrió un error al generar el archivo Excel:\n{e}")

    def abrir_formulario_repuesto(self, rep_editar=None, estado_inicial="En Stock"):
        vent = ctk.CTkToplevel(self)
        vent.title("Registrar Repuesto / Requerimiento" if not rep_editar else "Modificar Repuesto")
        vent.geometry("600x780")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)
        
        sf = ctk.CTkScrollableFrame(vent, fg_color="transparent")
        sf.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(sf, text="Ficha Técnica de Repuesto / Accesorio", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(0, 15))
        
        # 1. Selector de Disponibilidad / Estado
        ctk.CTkLabel(sf, text="Estado de Disponibilidad:", font=ctk.CTkFont(weight="bold", size=13), text_color=C_TEXT).pack(anchor="w", pady=(5, 4))
        
        var_estado = ctk.StringVar(value=rep_editar.get("estado_disponibilidad", estado_inicial) if rep_editar else estado_inicial)

        f_seg_box = ctk.CTkFrame(sf, fg_color="#F1F5F9", corner_radius=10, border_width=1, border_color="#CBD5E1", height=44)
        f_seg_box.pack(fill="x", pady=(0, 12))
        f_seg_box.grid_columnconfigure(0, weight=1)
        f_seg_box.grid_columnconfigure(1, weight=1)

        def actualizar_botones_estado():
            est = var_estado.get()
            if est == "En Stock":
                btn_stock_seg.configure(fg_color=C_BLUE, text_color="#FFFFFF", hover_color=C_BLUE_HOVER)
                btn_req_seg.configure(fg_color="transparent", text_color="#0F172A", hover_color="#E2E8F0")
            else:
                btn_stock_seg.configure(fg_color="transparent", text_color="#0F172A", hover_color="#E2E8F0")
                btn_req_seg.configure(fg_color=C_BLUE, text_color="#FFFFFF", hover_color=C_BLUE_HOVER)

        def seleccionar_estado(nuevo_estado):
            var_estado.set(nuevo_estado)
            actualizar_botones_estado()

        btn_stock_seg = ctk.CTkButton(f_seg_box, text="📦 En Stock", font=ctk.CTkFont(weight="bold", size=13),
                                      corner_radius=8, height=34, command=lambda: seleccionar_estado("En Stock"))
        btn_stock_seg.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        btn_req_seg = ctk.CTkButton(f_seg_box, text="📋 Requerido (Necesario)", font=ctk.CTkFont(weight="bold", size=13),
                                    corner_radius=8, height=34, command=lambda: seleccionar_estado("Requerido"))
        btn_req_seg.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        actualizar_botones_estado()

        # 2. Red de Salud
        ctk.CTkLabel(sf, text="Red de Salud *:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        
        sedes_data = getattr(self.app, "sedes_data", None)
        if not sedes_data:
            try:
                sedes_data = obtener_jerarquia_sedes_db()
                self.app.sedes_data = sedes_data
            except Exception as e:
                print(f"[WARN] Error obteniendo sedes: {e}")
                sedes_data = {}
                
        redes_opts = [r["nombre"] for r in sedes_data.get("redes", [])]
        if not redes_opts:
            redes_opts = [
                "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)",
                "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)",
                "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)",
                "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)",
                "RED 5-SUR (MACRODISTRITO SUR)"
            ]
        
        red_inicial = rep_editar.get("red_salud_nombre") if rep_editar else (getattr(self.app, "contexto_seleccionado", {}).get("red_salud") if hasattr(self.app, "contexto_seleccionado") else redes_opts[1])
        if not red_inicial or str(red_inicial).startswith("[ Todas"):
            red_inicial = redes_opts[1]

        combo_red = ctk.CTkComboBox(sf, values=redes_opts, height=36)
        combo_red.pack(fill="x", pady=(0, 10))
        if red_inicial in redes_opts:
            combo_red.set(red_inicial)

        # 3. Centro de Salud (Dinámico)
        ctk.CTkLabel(sf, text="Centro de Salud *:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        combo_centro = ctk.CTkComboBox(sf, values=["Cargando centros..."], height=36)
        combo_centro.pack(fill="x", pady=(0, 10))

        # 4. Área (Dinámico)
        ctk.CTkLabel(sf, text="Área Hospitalaria / Servicio *:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        combo_area = ctk.CTkComboBox(sf, values=["General"], height=36)
        combo_area.pack(fill="x", pady=(0, 10))

        def actualizar_centros_y_areas(red_sel):
            red_obj = next((r for r in sedes_data.get("redes", []) if r["nombre"] == red_sel), None)
            red_id = red_obj["id"] if red_obj else None
            centros_nombres = [c["nombre"] for c in sedes_data.get("centros", []) if c.get("red_salud_id") == red_id]
            if not centros_nombres:
                centros_nombres = ["Centro de Salud General"]
            combo_centro.configure(values=centros_nombres)
            
            c_ini = rep_editar.get("centro_salud_nombre") if rep_editar else (getattr(self.app, "contexto_seleccionado", {}).get("centro_salud") if hasattr(self.app, "contexto_seleccionado") else None)
            if c_ini and c_ini in centros_nombres:
                combo_centro.set(c_ini)
            else:
                combo_centro.set(centros_nombres[0])
            actualizar_areas(combo_centro.get())

        def actualizar_areas(centro_sel):
            cen_obj = next((c for c in sedes_data.get("centros", []) if c["nombre"] == centro_sel), None)
            cen_id = cen_obj["id"] if cen_obj else None
            areas_nombres = sorted(list(set(a["nombre"] for a in self.app.datos.get("areas", []) if a.get("centro_salud_id") == cen_id)))
            if not areas_nombres:
                areas_nombres = ["General", "Emergencias", "Odontología", "Laboratorio", "Enfermería", "Esterilización"]
            combo_area.configure(values=areas_nombres)
            
            a_ini = rep_editar.get("area") if rep_editar else None
            if a_ini:
                combo_area.set(a_ini)
            else:
                combo_area.set(areas_nombres[0])

        combo_red.configure(command=actualizar_centros_y_areas)
        combo_centro.configure(command=actualizar_areas)
        actualizar_centros_y_areas(combo_red.get())

        # 5. Nombre del Repuesto con Sugerencias
        ctk.CTkLabel(sf, text="Nombre del Repuesto / Accesorio *:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        
        f_rep_box = ctk.CTkFrame(sf, fg_color="transparent")
        f_rep_box.pack(fill="x", pady=(0, 10))
        
        e_nombre = ctk.CTkEntry(f_rep_box, placeholder_text="Ej: Sensor SpO2 adulto, Batería 12V 7Ah, Manguera NIBP, Turbina...", height=36)
        e_nombre.pack(fill="x")
        
        f_sug_rep = ctk.CTkFrame(f_rep_box, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#CBD5E1")
        
        # Lista de repuestos conocidos para sugerencias
        nombres_rep_conocidos = sorted(list(set(
            str(r.get("nombre_repuesto", "")).strip() for r in self.app.datos.get("repuestos", []) if r.get("nombre_repuesto")
        )))

        def seleccionar_sug_rep(nom_txt):
            e_nombre.delete(0, "end")
            e_nombre.insert(0, nom_txt)
            f_sug_rep.pack_forget()
            # Buscar datos previos de este repuesto para auto-rellenar
            rep_prev = next((r for r in self.app.datos.get("repuestos", []) if str(r.get("nombre_repuesto", "")).strip().lower() == nom_txt.lower()), None)
            if rep_prev:
                if rep_prev.get("marca") and not e_marca.get().strip():
                    e_marca.delete(0, "end"); e_marca.insert(0, rep_prev["marca"])
                if (rep_prev.get("modelo") or rep_prev.get("modelo_parte")) and not e_modelo.get().strip():
                    e_modelo.delete(0, "end"); e_modelo.insert(0, rep_prev.get("modelo") or rep_prev.get("modelo_parte") or "")
                if rep_prev.get("costo") and (not e_costo.get().strip() or e_costo.get().strip() == "0.00"):
                    e_costo.delete(0, "end"); e_costo.insert(0, str(rep_prev["costo"]))
                    actualizar_total_en_vivo()

        def on_escribir_repuesto(event):
            if event.keysym in ("Escape", "Tab", "Return"):
                f_sug_rep.pack_forget()
                return
            t = e_nombre.get().strip().lower()
            if not t or len(t) < 2:
                f_sug_rep.pack_forget()
                return
            matches = [nr for nr in nombres_rep_conocidos if t in nr.lower()][:4]
            if not matches:
                f_sug_rep.pack_forget()
                return
            for w in f_sug_rep.winfo_children():
                w.destroy()
            ctk.CTkLabel(f_sug_rep, text="💡 Repuestos sugeridos previamente:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B").pack(anchor="w", padx=8, pady=(4, 2))
            for m in matches:
                ctk.CTkButton(
                    f_sug_rep, text=f"🔧 {m}", anchor="w", fg_color="#FFFFFF", hover_color="#EFF6FF",
                    text_color="#1E293B", font=ctk.CTkFont(size=12), height=26, corner_radius=6,
                    command=lambda nom=m: seleccionar_sug_rep(nom)
                ).pack(fill="x", padx=4, pady=2)
            f_sug_rep.pack(fill="x", pady=(4, 0))

        e_nombre.bind("<KeyRelease>", on_escribir_repuesto)

        # 6. Marca y Modelo
        f_row_mm = ctk.CTkFrame(sf, fg_color="transparent")
        f_row_mm.pack(fill="x", pady=(0, 10))
        
        f_col_marca = ctk.CTkFrame(f_row_mm, fg_color="transparent")
        f_col_marca.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_col_marca, text="Marca del Repuesto / Equipo:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_marca = ctk.CTkEntry(f_col_marca, placeholder_text="Ej: Mindray, NSK, Philips...", height=36)
        e_marca.pack(fill="x")
        
        f_col_mod = ctk.CTkFrame(f_row_mm, fg_color="transparent")
        f_col_mod.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_col_mod, text="Modelo / N° Parte (P/N):", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_modelo = ctk.CTkEntry(f_col_mod, placeholder_text="Ej: P/N 115-002345, Pana-Max...", height=36)
        e_modelo.pack(fill="x")

        # 7. Cantidad y Costo Unitario
        f_row_cc = ctk.CTkFrame(sf, fg_color="transparent")
        f_row_cc.pack(fill="x", pady=(0, 10))
        
        f_col_cant = ctk.CTkFrame(f_row_cc, fg_color="transparent")
        f_col_cant.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_col_cant, text="Cantidad *:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_cantidad = ctk.CTkEntry(f_col_cant, placeholder_text="1", height=36)
        e_cantidad.pack(fill="x")
        
        f_col_costo = ctk.CTkFrame(f_row_cc, fg_color="transparent")
        f_col_costo.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_col_costo, text="Costo Unitario Estimado (Bs.):", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_costo = ctk.CTkEntry(f_col_costo, placeholder_text="0.00", height=36)
        e_costo.pack(fill="x")

        # Badge de Costo Total en Vivo
        f_costo_tot = ctk.CTkFrame(sf, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#E2E8F0")
        f_costo_tot.pack(fill="x", pady=(0, 12))
        lbl_costo_tot_live = ctk.CTkLabel(f_costo_tot, text="💰 Costo Total Calculado: 0.00 Bs.", font=ctk.CTkFont(weight="bold", size=13), text_color="#1D4ED8")
        lbl_costo_tot_live.pack(pady=8, padx=10)

        def actualizar_total_en_vivo(*args):
            try:
                c = int(e_cantidad.get().strip() or 0)
                u = float(e_costo.get().strip() or 0)
                tot = c * u
                lbl_costo_tot_live.configure(text=f"💰 Costo Total Calculado: {tot:,.2f} Bs.")
            except:
                lbl_costo_tot_live.configure(text="💰 Costo Total Calculado: 0.00 Bs.")

        e_cantidad.bind("<KeyRelease>", actualizar_total_en_vivo)
        e_costo.bind("<KeyRelease>", actualizar_total_en_vivo)

        # 8. Equipo Compatible (Opcional) con Sugerencias Predictivas en Vivo
        ctk.CTkLabel(sf, text="Equipo Médico Compatible / Catálogo (Opcional):", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        
        # Consolidar base de catálogo y equipos para búsqueda predictiva
        catalogo_items = []
        vistos_eq = set()
        for c in self.app.datos.get("catalogo", []):
            nom = str(c.get("nombre", "")).strip()
            mrc = str(c.get("marca", "")).strip()
            mdl = str(c.get("modelo", "")).strip()
            partes = [p for p in [nom, mrc, mdl] if p]
            item_str = " - ".join(partes)
            if item_str and item_str not in vistos_eq:
                vistos_eq.add(item_str)
                catalogo_items.append({"nombre": nom, "marca": mrc, "modelo": mdl, "texto": item_str})
                
        for eq in self.app.datos.get("equipos", []):
            nom = str(eq.get("nombre", "")).strip()
            mrc = str(eq.get("marca", "")).strip()
            mdl = str(eq.get("modelo", "")).strip()
            partes = [p for p in [nom, mrc, mdl] if p]
            item_str = " - ".join(partes)
            if item_str and item_str not in vistos_eq:
                vistos_eq.add(item_str)
                catalogo_items.append({"nombre": nom, "marca": mrc, "modelo": mdl, "texto": item_str})

        f_equipo_box = ctk.CTkFrame(sf, fg_color="transparent")
        f_equipo_box.pack(fill="x", pady=(0, 10))

        e_equipo_compat = ctk.CTkEntry(f_equipo_box, placeholder_text="🔍 Escribe para buscar equipo (Ej: Sillón dental, Monitor, Balanza...)", height=38)
        e_equipo_compat.pack(fill="x")

        f_sugerencias_eq = ctk.CTkFrame(f_equipo_box, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#CBD5E1")

        def seleccionar_sugerencia_eq(item):
            e_equipo_compat.delete(0, "end")
            e_equipo_compat.insert(0, item["texto"])
            f_sugerencias_eq.pack_forget()
            
            # Auto-completar marca y modelo si están vacíos
            if item.get("marca") and not e_marca.get().strip():
                e_marca.delete(0, "end")
                e_marca.insert(0, item["marca"])
            if item.get("modelo") and not e_modelo.get().strip():
                e_modelo.delete(0, "end")
                e_modelo.insert(0, item["modelo"])

        def on_escribir_equipo(event):
            if event.keysym in ("Escape", "Tab", "Return"):
                f_sugerencias_eq.pack_forget()
                return
            
            texto = e_equipo_compat.get().strip().lower()
            if not texto or len(texto) < 1:
                f_sugerencias_eq.pack_forget()
                return

            # Filtrar coincidencias
            coincidencias = []
            for item in catalogo_items:
                if texto in item["texto"].lower():
                    coincidencias.append(item)
                if len(coincidencias) >= 6:
                    break

            if not coincidencias:
                f_sugerencias_eq.pack_forget()
                return

            for w in f_sugerencias_eq.winfo_children():
                w.destroy()

            ctk.CTkLabel(f_sugerencias_eq, text="💡 Sugerencias de Equipos Compatibles (haz clic para elegir):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B").pack(anchor="w", padx=8, pady=(4, 2))

            for match in coincidencias:
                btn_sug = ctk.CTkButton(
                    f_sugerencias_eq,
                    text=f"🏥 {match['texto']}",
                    anchor="w",
                    fg_color="#FFFFFF",
                    hover_color="#EFF6FF",
                    text_color="#1E293B",
                    font=ctk.CTkFont(size=12),
                    height=28,
                    corner_radius=6,
                    command=lambda m=match: seleccionar_sugerencia_eq(m)
                )
                btn_sug.pack(fill="x", padx=4, pady=2)

            f_sugerencias_eq.pack(fill="x", pady=(4, 0))

        e_equipo_compat.bind("<KeyRelease>", on_escribir_equipo)

        # 9. Características Técnicas
        ctk.CTkLabel(sf, text="Características Técnicas y Especificaciones:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        txt_caract = ctk.CTkTextbox(sf, height=60, fg_color=C_BG, corner_radius=8)
        txt_caract.pack(fill="x", pady=(0, 10))

        # 10. Observaciones / Motivo
        ctk.CTkLabel(sf, text="Observaciones / Motivo del Requerimiento:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        txt_obs = ctk.CTkTextbox(sf, height=60, fg_color=C_BG, corner_radius=8)
        txt_obs.pack(fill="x", pady=(0, 10))

        # 11. Foto / Imagen
        ruta_foto = ctk.StringVar(value=rep_editar.get("foto", "") if rep_editar else "")
        f_foto = ctk.CTkFrame(sf, fg_color="transparent")
        f_foto.pack(fill="x", pady=(5, 15))
        
        lbl_foto_status = ctk.CTkLabel(f_foto, text="📷 Sin imagen adjunta" if not ruta_foto.get() else ("📷 Foto Adjuntada (Base64)" if ruta_foto.get().startswith("data:image") else f"📷 Foto: {os.path.basename(ruta_foto.get())}"), text_color=C_SUBTEXT, font=ctk.CTkFont(size=12))
        lbl_foto_status.pack(side="left", padx=5)
        
        def seleccionar_foto():
            f = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png;*.webp;*.bmp")])
            if f:
                b64_rep = comprimir_imagen_base64(f)
                if b64_rep:
                    ruta_foto.set(b64_rep)
                    lbl_foto_status.configure(text="✅ Foto Comprimida y Lista", text_color=C_GREEN)
                else:
                    ruta_foto.set(f)
                    lbl_foto_status.configure(text=f"📷 Foto: {os.path.basename(f)}", text_color=C_GREEN)
                
        ctk.CTkButton(f_foto, text="Adjuntar Foto", width=120, command=seleccionar_foto, fg_color=C_ORANGE, hover_color="#D97706").pack(side="right", padx=5)

        # Cargar datos si estamos editando
        if rep_editar:
            if rep_editar.get("tipo_equipo"): e_equipo_compat.insert(0, rep_editar.get("tipo_equipo"))
            e_nombre.insert(0, rep_editar.get("nombre_repuesto", ""))
            if rep_editar.get("marca"): e_marca.insert(0, rep_editar.get("marca"))
            if rep_editar.get("modelo") or rep_editar.get("modelo_parte"): e_modelo.insert(0, rep_editar.get("modelo") or rep_editar.get("modelo_parte") or "")
            e_costo.insert(0, str(rep_editar.get("costo", "") or "0.00"))
            e_cantidad.insert(0, str(rep_editar.get("cantidad", 1)))
            if rep_editar.get("caracteristicas"):
                txt_caract.insert("1.0", str(rep_editar.get("caracteristicas")))
            if rep_editar.get("observaciones"):
                txt_obs.insert("1.0", str(rep_editar.get("observaciones")))
            actualizar_total_en_vivo()
        else:
            e_cantidad.insert(0, "1")
            e_costo.insert(0, "0.00")
            actualizar_total_en_vivo()

        def guardar_repuesto():
            est_disp = var_estado.get().strip()
            red_val = combo_red.get().strip()
            cen_val = combo_centro.get().strip()
            area_val = combo_area.get().strip()
            n_rep = e_nombre.get().strip()
            marca_val = e_marca.get().strip()
            mod_val = e_modelo.get().strip()
            t_eq = e_equipo_compat.get().strip()
            caract_val = txt_caract.get("1.0", "end-1c").strip()
            obs_val = txt_obs.get("1.0", "end-1c").strip()
            
            try:
                c_cant = int(e_cantidad.get().strip())
                if c_cant < 0: raise ValueError()
            except:
                messagebox.showwarning("Dato Inválido", "La cantidad debe ser un número entero mayor o igual a 0.")
                return

            try:
                c_costo = float(e_costo.get().strip() or 0)
                if c_costo < 0: raise ValueError()
            except:
                messagebox.showwarning("Dato Inválido", "El costo debe ser un número válido.")
                return

            if not n_rep:
                messagebox.showwarning("Dato Requerido", "Ingrese el nombre del repuesto.")
                return

            r_foto = ruta_foto.get()

            # 1. Actualizar memoria y caché de inmediato
            rep_obj = {
                "tipo_equipo": t_eq,
                "nombre_repuesto": n_rep,
                "red_salud_nombre": red_val,
                "centro_salud_nombre": cen_val,
                "area": area_val,
                "marca": marca_val,
                "modelo": mod_val,
                "modelo_parte": mod_val,
                "cantidad": c_cant,
                "costo": c_costo,
                "estado_disponibilidad": est_disp,
                "caracteristicas": caract_val,
                "observaciones": obs_val,
                "foto": r_foto
            }
            if rep_editar and rep_editar.get("id"):
                rep_obj["id"] = rep_editar["id"]
            
            if rep_editar:
                for idx_r, ex in enumerate(self.app.datos.get("repuestos", [])):
                    if (rep_editar.get("id") and ex.get("id") == rep_editar["id"]) or (ex.get("nombre_repuesto") == rep_editar["nombre_repuesto"] and ex.get("centro_salud_nombre") == rep_editar.get("centro_salud_nombre")):
                        self.app.datos["repuestos"][idx_r] = rep_obj
                        break
            else:
                self.app.datos.setdefault("repuestos", []).append(rep_obj)

            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            vent.destroy()

            # 2. Guardar en PostgreSQL en segundo plano
            def _guardar_rep_db(tipo_e, nom_r, red_r, cen_r, area_r, marca_r, mod_r, cant_r, cos_r, est_r, car_r, obs_r, fot_r, es_edit, old_rep):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor()
                        if es_edit and old_rep:
                            old_id = old_rep.get("id")
                            if old_id:
                                cur.execute("""
                                    UPDATE repuestos 
                                    SET tipo_equipo=%s, nombre_repuesto=%s, red_salud_nombre=%s, centro_salud_nombre=%s, 
                                        area=%s, marca=%s, modelo=%s, modelo_parte=%s, cantidad=%s, 
                                        costo=%s, estado_disponibilidad=%s, caracteristicas=%s, observaciones=%s, foto=%s 
                                    WHERE id=%s
                                """, (tipo_e, nom_r, red_r, cen_r, area_r, marca_r, mod_r, mod_r, cant_r, cos_r, est_r, car_r, obs_r, fot_r, old_id))
                            else:
                                cur.execute("""
                                    UPDATE repuestos 
                                    SET tipo_equipo=%s, nombre_repuesto=%s, red_salud_nombre=%s, centro_salud_nombre=%s, 
                                        area=%s, marca=%s, modelo=%s, modelo_parte=%s, cantidad=%s, 
                                        costo=%s, estado_disponibilidad=%s, caracteristicas=%s, observaciones=%s, foto=%s 
                                    WHERE nombre_repuesto=%s
                                """, (tipo_e, nom_r, red_r, cen_r, area_r, marca_r, mod_r, mod_r, cant_r, cos_r, est_r, car_r, obs_r, fot_r, old_rep["nombre_repuesto"]))
                        else:
                            cur.execute("""
                                INSERT INTO repuestos (tipo_equipo, nombre_repuesto, red_salud_nombre, centro_salud_nombre, area, marca, modelo, modelo_parte, cantidad, costo, estado_disponibilidad, caracteristicas, observaciones, foto) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (tipo_e, nom_r, red_r, cen_r, area_r, marca_r, mod_r, mod_r, cant_r, cos_r, est_r, car_r, obs_r, fot_r))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Error al guardar repuesto en PostgreSQL: {e}")

            ejecutar_en_segundo_plano(_guardar_rep_db, t_eq, n_rep, red_val, cen_val, area_val, marca_val, mod_val, c_cant, c_costo, est_disp, caract_val, obs_val, r_foto, bool(rep_editar), rep_editar)

        ctk.CTkButton(sf, text="Guardar Ficha de Repuesto", font=ctk.CTkFont(weight="bold", size=14), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, height=42, command=guardar_repuesto).pack(fill="x", pady=(10, 20))

    def pasar_a_stock(self):
        """Acción rápida para marcar un repuesto Requerido como Adquirido/En Stock"""
        v = self.obtener_seleccion(tabla_origen="req")
        if not v:
            messagebox.showinfo("Selección Requerida", "Seleccione un repuesto de la lista de requerimientos.")
            return
            
        n_rep = v[2]
        cen_rep = v[0]
        rep = next((r for r in self.app.datos.get("repuestos", []) if r.get("nombre_repuesto") == n_rep and (not r.get("centro_salud_nombre") or r.get("centro_salud_nombre") == cen_rep or cen_rep == "-")), None)
        if not rep:
            rep = next((r for r in self.app.datos.get("repuestos", []) if r.get("nombre_repuesto") == n_rep), None)
        if not rep:
            return
            
        if messagebox.askyesno("Confirmar Ingreso a Stock", f"¿Marcar el repuesto '{n_rep}' como ADQUIRIDO y pasarlo a Stock disponible?"):
            rep["estado_disponibilidad"] = "En Stock"
            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            
            def _actualizar_stock_db(rep_id, nom_r):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor()
                        if rep_id:
                            cur.execute("UPDATE repuestos SET estado_disponibilidad='En Stock' WHERE id=%s", (rep_id,))
                        else:
                            cur.execute("UPDATE repuestos SET estado_disponibilidad='En Stock' WHERE nombre_repuesto=%s", (nom_r,))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Error al actualizar estado de repuesto: {e}")
                        
            ejecutar_en_segundo_plano(_actualizar_stock_db, rep.get("id"), n_rep)
            messagebox.showinfo("Éxito", f"El repuesto '{n_rep}' ahora está disponible en Stock.")

    def modificar_repuesto(self, tabla_origen="stock"):
        if not self.app.es_jefe:
            messagebox.showerror("Permiso denegado", "Solo el Jefe de servicio puede modificar repuestos.")
            return
        v = self.obtener_seleccion(tabla_origen=tabla_origen)
        if v:
            n_rep = v[2]
            cen_rep = v[0]
            rep = next((r for r in self.app.datos["repuestos"] if r.get("nombre_repuesto") == n_rep and (not r.get("centro_salud_nombre") or r.get("centro_salud_nombre") == cen_rep or cen_rep == "-")), None)
            if not rep:
                rep = next((r for r in self.app.datos["repuestos"] if r.get("nombre_repuesto") == n_rep), None)
            if rep: self.abrir_formulario_repuesto(rep)
        else:
            messagebox.showinfo("Selección Requerida", "Seleccione un repuesto de la tabla para modificar.")

    def eliminar_repuesto(self, tabla_origen="stock"):
        if not self.app.es_jefe: return
        v = self.obtener_seleccion(tabla_origen=tabla_origen)
        if not v:
            messagebox.showinfo("Selección Requerida", "Seleccione un repuesto de la tabla para eliminar.")
            return
        n_rep = v[2]
        cen_rep = v[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el registro de repuesto '{n_rep}'?"):
            try:
                rep_encontrado = next((r for r in self.app.datos.get("repuestos", []) if r.get("nombre_repuesto") == n_rep and (not r.get("centro_salud_nombre") or r.get("centro_salud_nombre") == cen_rep or cen_rep == "-")), None)
                if not rep_encontrado:
                    rep_encontrado = next((r for r in self.app.datos.get("repuestos", []) if r.get("nombre_repuesto") == n_rep), None)
                
                # 1. Eliminar en memoria instantáneamente
                if rep_encontrado:
                    self.app.datos["repuestos"].remove(rep_encontrado)
                else:
                    self.app.datos["repuestos"] = [r for r in self.app.datos.get("repuestos", []) if r.get("nombre_repuesto") != n_rep]
                    
                guardar_cache_local_datos(self.app.datos)
                self.refrescar_datos()
                
                # 2. Eliminar en base de datos en segundo plano
                def _eliminar_rep_db(nom_r, r_id, usr_nom):
                    conn = obtener_conexion()
                    if conn:
                        try:
                            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                            if r_id:
                                cur.execute("SELECT * FROM repuestos WHERE id=%s", (r_id,))
                            else:
                                cur.execute("SELECT * FROM repuestos WHERE nombre_repuesto=%s", (nom_r,))
                            fila = cur.fetchone()
                            if fila:
                                mover_a_papelera(cur, "repuestos", fila["id"], dict(fila), usr_nom)
                                cur.execute("DELETE FROM repuestos WHERE id = %s", (fila["id"],))
                            conn.commit()
                            cur.close()
                            conn.close()
                        except Exception as e:
                            print(f"[ERROR] Error al eliminar repuesto de DB: {e}")
                            
                ejecutar_en_segundo_plano(_eliminar_rep_db, n_rep, rep_encontrado.get("id") if rep_encontrado else None, self.app.usuario_actual.get("nombre_usuario", "jefe"))
            except Exception as e: 
                messagebox.showerror("Error", str(e))