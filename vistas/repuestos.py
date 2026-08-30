# vistas/repuestos.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera, ejecutar_en_segundo_plano, guardar_cache_local_datos
from estilos import *
from datetime import date, datetime
import os

class VistaRepuestos(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        f_title = ctk.CTkFrame(self, fg_color="transparent")
        f_title.pack(pady=(20, 5), padx=30, fill="x")
        ctk.CTkLabel(f_title, text="Control de Repuestos y Accesorios", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        self.tabview = ctk.CTkTabview(self, fg_color=C_CARD, corner_radius=16, text_color=C_TEXT,
                                      border_width=1, border_color=C_BORDER,
                                      segmented_button_fg_color=C_BG,
                                      segmented_button_selected_color=C_BLUE,
                                      segmented_button_selected_hover_color=C_BLUE_HOVER,
                                      segmented_button_unselected_color=C_BG,
                                      segmented_button_unselected_hover_color=C_CARD_HOVER)
        self.tabview.pack(padx=30, pady=10, fill="both", expand=True)
        
        tab_stock = self.tabview.add("📦 Repuestos en Stock")
        tab_req = self.tabview.add("📋 Repuestos Requeridos (Necesarios)")
        tab_hist = self.tabview.add("📜 Historial de Repuestos Usados")
        
        # =========================================================================
        # --- TAB 1: REPUESTOS EN STOCK (DISPONIBLES) ---
        # =========================================================================
        marco_stock = ctk.CTkFrame(tab_stock, fg_color="transparent")
        marco_stock.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filtros de Stock
        f_filtros_stock = ctk.CTkFrame(marco_stock, fg_color="transparent")
        f_filtros_stock.pack(fill="x", pady=(0, 10))
        
        self.busqueda_stock_var = ctk.StringVar()
        self.busqueda_stock_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_filtros_stock, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_stock = ctk.CTkEntry(f_filtros_stock, textvariable=self.busqueda_stock_var, placeholder_text="Buscar por Equipo, Repuesto, Modelo/PN...", width=260, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_stock.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_filtros_stock, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_stock = ctk.CTkComboBox(f_filtros_stock, values=["Repuesto (A-Z)", "Repuesto (Z-A)", "Equipo Médico", "Cantidad (Mayor)", "Cantidad (Menor)", "Costo (Mayor)"], command=lambda e: self.refrescar_datos(), width=170, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_stock.pack(side="left", padx=5)
        self.combo_ordenar_stock.set("Repuesto (A-Z)")
        
        cols_stock = ("Equipo Médico", "Repuesto", "Modelo / P/N", "Cant. Disponible", "Costo Unit. (Bs.)", "Características", "Observaciones")
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
        
        f_bot_stock = ctk.CTkFrame(tab_stock, fg_color="transparent")
        f_bot_stock.pack(pady=(5, 15), padx=10, fill="x")
        ctk.CTkButton(f_bot_stock, text="✚ Añadir a Stock", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=40, command=lambda: self.abrir_formulario_repuesto(estado_inicial="En Stock")).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot_stock, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=40, command=lambda: self.modificar_repuesto(tabla_origen="stock")).pack(side="left", expand=True, padx=8)
        self.btn_eliminar_stock = ctk.CTkButton(f_bot_stock, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=40, command=lambda: self.eliminar_repuesto(tabla_origen="stock"))
        self.btn_eliminar_stock.pack(side="left", expand=True, padx=8)
        if not self.app.es_jefe: self.btn_eliminar_stock.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)

        # =========================================================================
        # --- TAB 2: REPUESTOS REQUERIDOS (NECESARIOS / PENDIENTES) ---
        # =========================================================================
        marco_req = ctk.CTkFrame(tab_req, fg_color="transparent")
        marco_req.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filtros de Requerimientos + KPI resumen
        f_top_req = ctk.CTkFrame(marco_req, fg_color="transparent")
        f_top_req.pack(fill="x", pady=(0, 10))
        
        self.busqueda_req_var = ctk.StringVar()
        self.busqueda_req_var.trace_add("write", lambda *args: self.refrescar_datos())
        ctk.CTkLabel(f_top_req, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar_req = ctk.CTkEntry(f_top_req, textvariable=self.busqueda_req_var, placeholder_text="Buscar Requerimiento, Equipo, P/N...", width=260, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar_req.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_top_req, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(15, 5))
        self.combo_ordenar_req = ctk.CTkComboBox(f_top_req, values=["Repuesto (A-Z)", "Repuesto (Z-A)", "Equipo Médico", "Cantidad (Mayor)", "Costo Estimado (Mayor)"], command=lambda e: self.refrescar_datos(), width=180, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_ordenar_req.pack(side="left", padx=5)
        self.combo_ordenar_req.set("Repuesto (A-Z)")
        
        self.lbl_kpi_req = ctk.CTkLabel(f_top_req, text="Requerimientos: 0 | Total Est.: 0.00 Bs.", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_ORANGE)
        self.lbl_kpi_req.pack(side="right", padx=10)
        
        cols_req = ("Equipo Médico", "Repuesto Necesario", "Modelo / P/N", "Cant. Requerida", "Costo Est. (Bs.)", "Costo Total (Bs.)", "Características", "Observaciones / Motivo")
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
        
        f_bot_req = ctk.CTkFrame(tab_req, fg_color="transparent")
        f_bot_req.pack(pady=(5, 15), padx=10, fill="x")
        ctk.CTkButton(f_bot_req, text="✚ Solicitar Repuesto", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_ORANGE, hover_color="#D97706", corner_radius=10, height=40, command=lambda: self.abrir_formulario_repuesto(estado_inicial="Requerido")).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot_req, text="✅ Pasar a Stock (Adquirido)", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_GREEN, hover_color=C_GREEN_HOVER, corner_radius=10, height=40, command=self.pasar_a_stock).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot_req, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=40, command=lambda: self.modificar_repuesto(tabla_origen="req")).pack(side="left", expand=True, padx=8)
        self.btn_eliminar_req = ctk.CTkButton(f_bot_req, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=40, command=lambda: self.eliminar_repuesto(tabla_origen="req"))
        self.btn_eliminar_req.pack(side="left", expand=True, padx=8)
        if not self.app.es_jefe: self.btn_eliminar_req.configure(state="disabled", fg_color=C_BORDER, text_color=C_SUBTEXT)
        
        # =========================================================================
        # --- TAB 3: HISTORIAL DE REPUESTOS USADOS ---
        # =========================================================================
        marco_hist = ctk.CTkFrame(tab_hist, fg_color="transparent")
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
                t_stock in str(r.get("tipo_equipo", "")).lower() or
                t_stock in str(r.get("nombre_repuesto", "")).lower() or
                t_stock in str(r.get("modelo_parte", "")).lower() or
                t_stock in str(r.get("caracteristicas", "")).lower() or
                t_stock in str(r.get("observaciones", "")).lower()
            )]
            
        crit_stock = self.combo_ordenar_stock.get() if hasattr(self, "combo_ordenar_stock") else "Repuesto (A-Z)"
        if crit_stock == "Repuesto (A-Z)":
            rep_stock.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower())
        elif crit_stock == "Repuesto (Z-A)":
            rep_stock.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower(), reverse=True)
        elif crit_stock == "Equipo Médico":
            rep_stock.sort(key=lambda x: str(x.get("tipo_equipo", "")).lower())
        elif crit_stock == "Cantidad (Mayor)":
            rep_stock.sort(key=lambda x: int(x.get("cantidad", 0)), reverse=True)
        elif crit_stock == "Cantidad (Menor)":
            rep_stock.sort(key=lambda x: int(x.get("cantidad", 0)))
        elif crit_stock == "Costo (Mayor)":
            rep_stock.sort(key=lambda x: float(x.get("costo", 0) or 0), reverse=True)
            
        for r in rep_stock:
            costo_val = float(r.get("costo", 0) or 0)
            costo_str = f"{costo_val:.2f}" if costo_val > 0 else "-"
            self.tabla_stock.insert("", "end", values=(
                r.get("tipo_equipo", ""),
                r.get("nombre_repuesto", ""),
                r.get("modelo_parte", "-") or "-",
                r.get("cantidad", 0),
                costo_str,
                r.get("caracteristicas", "-") or "-",
                r.get("observaciones", "-") or "-"
            ))
        
        # --- TAB 2: REQUERIMIENTOS ---
        for i in self.tabla_req.get_children(): 
            self.tabla_req.delete(i)
            
        t_req = self.busqueda_req_var.get().lower().strip()
        if t_req:
            rep_req = [r for r in rep_req if (
                t_req in str(r.get("tipo_equipo", "")).lower() or
                t_req in str(r.get("nombre_repuesto", "")).lower() or
                t_req in str(r.get("modelo_parte", "")).lower() or
                t_req in str(r.get("caracteristicas", "")).lower() or
                t_req in str(r.get("observaciones", "")).lower()
            )]
            
        crit_req = self.combo_ordenar_req.get() if hasattr(self, "combo_ordenar_req") else "Repuesto (A-Z)"
        if crit_req == "Repuesto (A-Z)":
            rep_req.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower())
        elif crit_req == "Repuesto (Z-A)":
            rep_req.sort(key=lambda x: str(x.get("nombre_repuesto", "")).lower(), reverse=True)
        elif crit_req == "Equipo Médico":
            rep_req.sort(key=lambda x: str(x.get("tipo_equipo", "")).lower())
        elif crit_req == "Cantidad (Mayor)":
            rep_req.sort(key=lambda x: int(x.get("cantidad", 0)), reverse=True)
        elif crit_req == "Costo Estimado (Mayor)":
            rep_req.sort(key=lambda x: float(x.get("costo", 0) or 0) * int(x.get("cantidad", 0)), reverse=True)
            
        total_inversion_req = 0.0
        for r in rep_req:
            cant_r = int(r.get("cantidad", 0) or 0)
            costo_u = float(r.get("costo", 0) or 0)
            costo_tot = cant_r * costo_u
            total_inversion_req += costo_tot
            
            c_u_str = f"{costo_u:.2f}" if costo_u > 0 else "-"
            c_tot_str = f"{costo_tot:.2f}" if costo_tot > 0 else "-"
            
            self.tabla_req.insert("", "end", values=(
                r.get("tipo_equipo", ""),
                r.get("nombre_repuesto", ""),
                r.get("modelo_parte", "-") or "-",
                cant_r,
                c_u_str,
                c_tot_str,
                r.get("caracteristicas", "-") or "-",
                r.get("observaciones", "-") or "-"
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

    def abrir_formulario_repuesto(self, rep_editar=None, estado_inicial="En Stock"):
        vent = ctk.CTkToplevel(self)
        vent.title("Registrar Repuesto / Requerimiento" if not rep_editar else "Modificar Repuesto")
        vent.geometry("580x720")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)
        
        # Scroll container para el formulario
        sf = ctk.CTkScrollableFrame(vent, fg_color="transparent")
        sf.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(sf, text="Ficha Técnica de Repuesto / Accesorio", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(0, 15))
        
        # 1. Selector de Disponibilidad / Estado
        ctk.CTkLabel(sf, text="Estado de Disponibilidad:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        var_estado = ctk.StringVar(value=rep_editar.get("estado_disponibilidad", estado_inicial) if rep_editar else estado_inicial)
        
        seg_estado = ctk.CTkSegmentedButton(sf, values=["En Stock", "Requerido"], variable=var_estado,
                                            selected_color=C_BLUE, selected_hover_color=C_BLUE_HOVER,
                                            unselected_color=C_BG, unselected_hover_color=C_CARD_HOVER,
                                            font=ctk.CTkFont(weight="bold", size=13), height=36)
        seg_estado.pack(fill="x", pady=(0, 12))

        # 2. Equipo Médico Compatible (Catálogo)
        ctk.CTkLabel(sf, text="Equipo Médico Compatible / Tipo:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        opciones_cat = [f"{c['nombre']} - {c.get('marca', '')} - {c.get('modelo', '')}" for c in self.app.datos.get("catalogo", [])]
        if not opciones_cat:
            opciones_cat = ["General / Multiuso"]
        combo_tipo = ctk.CTkComboBox(sf, values=opciones_cat, height=36)
        combo_tipo.pack(fill="x", pady=(0, 12))
        
        # 3. Nombre del Repuesto
        ctk.CTkLabel(sf, text="Nombre del Repuesto / Accesorio *:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        e_nombre = ctk.CTkEntry(sf, placeholder_text="Ej: Sensor SpO2 adulto, Batería 12V 7Ah, Manguera NIBP...", height=36)
        e_nombre.pack(fill="x", pady=(0, 12))
        
        # 4. Modelo / Número de Parte (P/N) y Costo Unitario
        f_row1 = ctk.CTkFrame(sf, fg_color="transparent")
        f_row1.pack(fill="x", pady=(0, 12))
        
        f_col_mod = ctk.CTkFrame(f_row1, fg_color="transparent")
        f_col_mod.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(f_col_mod, text="Modelo / N° Parte (P/N):", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_modelo = ctk.CTkEntry(f_col_mod, placeholder_text="Ej: P/N 115-002345, Mod. BC-500", height=36)
        e_modelo.pack(fill="x")
        
        f_col_costo = ctk.CTkFrame(f_row1, fg_color="transparent")
        f_col_costo.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(f_col_costo, text="Costo Unitario Estimado (Bs.):", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_costo = ctk.CTkEntry(f_col_costo, placeholder_text="0.00", height=36)
        e_costo.pack(fill="x")

        # 5. Cantidad
        ctk.CTkLabel(sf, text="Cantidad (Stock disponible o Unidades requeridas) *:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        e_cantidad = ctk.CTkEntry(sf, placeholder_text="1", height=36)
        e_cantidad.pack(fill="x", pady=(0, 12))

        # 6. Características Técnicas
        ctk.CTkLabel(sf, text="Características Técnicas y Especificaciones:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        txt_caract = ctk.CTkTextbox(sf, height=65, fg_color=C_BG, corner_radius=8)
        txt_caract.pack(fill="x", pady=(0, 12))

        # 7. Observaciones / Motivo de Solicitud
        ctk.CTkLabel(sf, text="Observaciones / Motivo del Requerimiento:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(5, 2))
        txt_obs = ctk.CTkTextbox(sf, height=65, fg_color=C_BG, corner_radius=8)
        txt_obs.pack(fill="x", pady=(0, 12))

        # 8. Foto / Imagen
        ruta_foto = ctk.StringVar(value=rep_editar.get("foto", "") if rep_editar else "")
        f_foto = ctk.CTkFrame(sf, fg_color="transparent")
        f_foto.pack(fill="x", pady=(5, 15))
        
        lbl_foto_status = ctk.CTkLabel(f_foto, text="📷 Sin imagen adjunta" if not ruta_foto.get() else f"📷 Foto: {os.path.basename(ruta_foto.get())}", text_color=C_SUBTEXT, font=ctk.CTkFont(size=12))
        lbl_foto_status.pack(side="left", padx=5)
        
        def seleccionar_foto():
            f = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png;*.webp")])
            if f:
                ruta_foto.set(f)
                lbl_foto_status.configure(text=f"📷 Foto: {os.path.basename(f)}", text_color=C_GREEN)
                
        ctk.CTkButton(f_foto, text="Adjuntar Foto", width=120, command=seleccionar_foto, fg_color=C_ORANGE, hover_color="#D97706").pack(side="right", padx=5)

        # Cargar datos si estamos editando
        if rep_editar:
            combo_tipo.set(rep_editar.get("tipo_equipo", ""))
            e_nombre.insert(0, rep_editar.get("nombre_repuesto", ""))
            e_modelo.insert(0, rep_editar.get("modelo_parte", "") or "")
            e_costo.insert(0, str(rep_editar.get("costo", "") or ""))
            e_cantidad.insert(0, str(rep_editar.get("cantidad", 1)))
            if rep_editar.get("caracteristicas"):
                txt_caract.insert("1.0", str(rep_editar.get("caracteristicas")))
            if rep_editar.get("observaciones"):
                txt_obs.insert("1.0", str(rep_editar.get("observaciones")))
        else:
            e_cantidad.insert(0, "1")
            e_costo.insert(0, "0.00")

        def guardar_repuesto():
            est_disp = var_estado.get().strip()
            t_eq = combo_tipo.get().strip()
            n_rep = e_nombre.get().strip()
            mod_p = e_modelo.get().strip()
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

            # 1. Actualizar memoria y caché de inmediato (0 ms)
            rep_obj = {
                "tipo_equipo": t_eq,
                "nombre_repuesto": n_rep,
                "modelo_parte": mod_p,
                "cantidad": c_cant,
                "costo": c_costo,
                "estado_disponibilidad": est_disp,
                "caracteristicas": caract_val,
                "observaciones": obs_val,
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
            def _guardar_rep_db(tipo_e, nom_r, mod_r, cant_r, cos_r, est_r, car_r, obs_r, fot_r, es_edit, old_rep):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor()
                        if es_edit:
                            cur.execute("""
                                UPDATE repuestos 
                                SET tipo_equipo=%s, nombre_repuesto=%s, modelo_parte=%s, cantidad=%s, 
                                    costo=%s, estado_disponibilidad=%s, caracteristicas=%s, observaciones=%s, foto=%s 
                                WHERE tipo_equipo=%s AND nombre_repuesto=%s
                            """, (tipo_e, nom_r, mod_r, cant_r, cos_r, est_r, car_r, obs_r, fot_r, old_rep["tipo_equipo"], old_rep["nombre_repuesto"]))
                        else:
                            cur.execute("""
                                INSERT INTO repuestos (tipo_equipo, nombre_repuesto, modelo_parte, cantidad, costo, estado_disponibilidad, caracteristicas, observaciones, foto) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (tipo_equipo, nombre_repuesto) DO UPDATE
                                SET modelo_parte=EXCLUDED.modelo_parte,
                                    cantidad=EXCLUDED.cantidad,
                                    costo=EXCLUDED.costo,
                                    estado_disponibilidad=EXCLUDED.estado_disponibilidad,
                                    caracteristicas=EXCLUDED.caracteristicas,
                                    observaciones=EXCLUDED.observaciones,
                                    foto=EXCLUDED.foto
                            """, (tipo_e, nom_r, mod_r, cant_r, cos_r, est_r, car_r, obs_r, fot_r))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Error al guardar repuesto en PostgreSQL: {e}")

            ejecutar_en_segundo_plano(_guardar_rep_db, t_eq, n_rep, mod_p, c_cant, c_costo, est_disp, caract_val, obs_val, r_foto, bool(rep_editar), rep_editar)

        ctk.CTkButton(sf, text="Guardar Ficha de Repuesto", font=ctk.CTkFont(weight="bold", size=14), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, height=42, command=guardar_repuesto).pack(fill="x", pady=(10, 20))

    def pasar_a_stock(self):
        """Acción rápida para marcar un repuesto Requerido como Adquirido/En Stock"""
        v = self.obtener_seleccion(tabla_origen="req")
        if not v:
            messagebox.showinfo("Selección Requerida", "Seleccione un repuesto de la lista de requerimientos.")
            return
            
        t_eq, n_rep = v[0], v[1]
        rep = next((r for r in self.app.datos.get("repuestos", []) if r["tipo_equipo"] == t_eq and r["nombre_repuesto"] == n_rep), None)
        if not rep:
            return
            
        if messagebox.askyesno("Confirmar Ingreso a Stock", f"¿Marcar el repuesto '{n_rep}' como ADQUIRIDO y pasarlo a Stock disponible?"):
            rep["estado_disponibilidad"] = "En Stock"
            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            
            def _actualizar_stock_db(tipo_e, nom_r):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor()
                        cur.execute("UPDATE repuestos SET estado_disponibilidad='En Stock' WHERE tipo_equipo=%s AND nombre_repuesto=%s", (tipo_e, nom_r))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Error al actualizar estado de repuesto: {e}")
                        
            ejecutar_en_segundo_plano(_actualizar_stock_db, t_eq, n_rep)
            messagebox.showinfo("Éxito", f"El repuesto '{n_rep}' ahora está disponible en Stock.")

    def modificar_repuesto(self, tabla_origen="stock"):
        if not self.app.es_jefe:
            messagebox.showerror("Permiso denegado", "Solo el Jefe de servicio puede modificar repuestos.")
            return
        v = self.obtener_seleccion(tabla_origen=tabla_origen)
        if v:
            rep = next((r for r in self.app.datos["repuestos"] if r["tipo_equipo"] == v[0] and r["nombre_repuesto"] == v[1]), None)
            if rep: self.abrir_formulario_repuesto(rep)
        else:
            messagebox.showinfo("Selección Requerida", "Seleccione un repuesto de la tabla para modificar.")

    def eliminar_repuesto(self, tabla_origen="stock"):
        if not self.app.es_jefe: return
        v = self.obtener_seleccion(tabla_origen=tabla_origen)
        if not v:
            messagebox.showinfo("Selección Requerida", "Seleccione un repuesto de la tabla para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar el registro de repuesto '{v[1]}'?"):
            try:
                # 1. Eliminar en memoria instantáneamente
                self.app.datos["repuestos"] = [r for r in self.app.datos.get("repuestos", []) if not (r["tipo_equipo"] == v[0] and r["nombre_repuesto"] == v[1])]
                guardar_cache_local_datos(self.app.datos)
                self.refrescar_datos()
                
                # 2. Eliminar en base de datos en segundo plano
                def _eliminar_rep_db(tipo_e, nom_r, usr_nom):
                    conn = obtener_conexion()
                    if conn:
                        try:
                            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                            cur.execute("SELECT * FROM repuestos WHERE tipo_equipo=%s AND nombre_repuesto=%s", (tipo_e, nom_r))
                            fila = cur.fetchone()
                            if fila:
                                mover_a_papelera(cur, "repuestos", fila["id"], dict(fila), usr_nom)
                                cur.execute("DELETE FROM repuestos WHERE id = %s", (fila["id"],))
                            conn.commit()
                            cur.close()
                            conn.close()
                        except Exception as e:
                            print(f"[ERROR] Error al eliminar repuesto de DB: {e}")
                            
                ejecutar_en_segundo_plano(_eliminar_rep_db, v[0], v[1], self.app.usuario_actual.get("nombre_usuario", "jefe"))
            except Exception as e: 
                messagebox.showerror("Error", str(e))