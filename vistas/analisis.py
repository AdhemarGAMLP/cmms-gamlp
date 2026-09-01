# vistas/analisis.py
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from estilos import *
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

def simplificar_nombre_red(red_str):
    if not red_str:
        return "Sin Red"
    s = str(red_str).strip()
    m = re.search(r'RED\s*([0-9]+)', s, re.IGNORECASE)
    if m:
        return f"Red {m.group(1)}"
    if "(" in s:
        s = s.split("(")[0].strip()
    return s.title() if s.isupper() else s

class VistaAnalisis(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.hoy = getattr(self.app, "hoy", date.today())
        self.anio_actual = self.hoy.year
        self.canvas_widgets = [] 
        self.figuras = [] 
        self.modal_equipos = None
        
        # Estado de navegación interna en la pestaña de análisis
        self.drill_red = None
        self.drill_centro = None
        self.busqueda_tabla_var = ctk.StringVar()
        
        self.construir_ui()

    def construir_ui(self):
        # Cabecera principal
        f_cab = ctk.CTkFrame(self, fg_color="transparent")
        f_cab.pack(pady=(20, 10), padx=30, fill="x")
        
        ctk.CTkLabel(f_cab, text="Estadísticas y Análisis de Mantenimiento", font=ctk.CTkFont(size=26, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        # Selector de Año
        f_filtro = ctk.CTkFrame(f_cab, fg_color="transparent")
        f_filtro.pack(side="right")
        ctk.CTkLabel(f_filtro, text="Año de Análisis:", font=ctk.CTkFont(weight="bold", size=13), text_color=C_TEXT).pack(side="left", padx=5)
        
        self.combo_anio = ctk.CTkComboBox(f_filtro, values=["2026", "2027", "2028"], command=lambda e: self.refrescar_datos(), width=100, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_anio.pack(side="left", padx=5)
        self.combo_anio.set(str(self.anio_actual))

        # Contenedor con Scroll para todo el dashboard
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=C_BG, corner_radius=0, border_width=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        # Configurar grid de 2 columnas para el scroll_frame
        self.scroll_frame.columnconfigure(0, weight=1, uniform="col")
        self.scroll_frame.columnconfigure(1, weight=1, uniform="col")

    def parsear_fecha(self, f):
        if isinstance(f, datetime):
            return f.date()
        elif isinstance(f, date):
            return f
        elif isinstance(f, str):
            try:
                return datetime.strptime(f.split(" ")[0], "%Y-%m-%d").date()
            except:
                return None
        return None

    def limpiar_graficos(self):
        for widget in self.canvas_widgets:
            try:
                widget.destroy()
            except:
                pass
        self.canvas_widgets.clear()
        
        for fig in self.figuras:
            try:
                plt.close(fig)
            except:
                pass
        self.figuras.clear()

    def navegar_a_red(self, nombre_red):
        self.drill_red = nombre_red
        self.drill_centro = None
        self.refrescar_datos()

    def navegar_a_centro(self, nombre_centro):
        self.drill_centro = nombre_centro
        self.refrescar_datos()

    def navegar_a_global(self):
        self.drill_red = None
        self.drill_centro = None
        self.refrescar_datos()

    def refrescar_datos(self):
        self.limpiar_graficos()
        
        todos_equipos = list(self.app.datos.get("equipos", []))
        contexto = getattr(self.app, "contexto_sede", None)
        
        # Sincronizar contexto global si la app principal cambió de sede
        red_ctx = None
        cen_ctx = None
        if contexto and not contexto.get("es_global", True):
            cen_nom = contexto.get("centro_salud")
            red_nom = contexto.get("red_salud")
            if cen_nom and not str(cen_nom).startswith("[ Todos"):
                cen_ctx = cen_nom
            elif red_nom and not str(red_nom).startswith("[ Todas"):
                red_ctx = red_nom

        # Prevalencia del drill-down interactivo
        red_activa = self.drill_red or red_ctx
        centro_activo = self.drill_centro or cen_ctx

        # ----------------------------------------------------
        # BREADCRUMB / BARRA DE NAVEGACIÓN TERRITORIAL
        # ----------------------------------------------------
        f_bread = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        f_bread.grid(row=0, column=0, columnspan=2, padx=12, pady=(4, 8), sticky="ew")
        self.canvas_widgets.append(f_bread)
        
        f_bread_in = ctk.CTkFrame(f_bread, fg_color="transparent")
        f_bread_in.pack(fill="x", padx=14, pady=10)

        # Botón de Inicio Global
        btn_glob = ctk.CTkButton(
            f_bread_in, 
            text="🌐 GAMLP (Todas las Redes)", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#EFF6FF" if (red_activa or centro_activo) else C_BLUE,
            text_color=C_BLUE if (red_activa or centro_activo) else "white",
            hover_color="#DBEAFE" if (red_activa or centro_activo) else C_BLUE_HOVER,
            height=30,
            corner_radius=8,
            command=self.navegar_a_global
        )
        btn_glob.pack(side="left")

        if red_activa:
            ctk.CTkLabel(f_bread_in, text=" ➔ ", font=ctk.CTkFont(size=14, weight="bold"), text_color=C_SUBTEXT).pack(side="left", padx=4)
            btn_r = ctk.CTkButton(
                f_bread_in, 
                text=f"🏥 {simplificar_nombre_red(red_activa)}", 
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#EFF6FF" if centro_activo else C_GREEN,
                text_color=C_GREEN if centro_activo else "white",
                hover_color="#DCFCE7" if centro_activo else "#047857",
                height=30,
                corner_radius=8,
                command=lambda: self.navegar_a_red(red_activa)
            )
            btn_r.pack(side="left")

        if centro_activo:
            ctk.CTkLabel(f_bread_in, text=" ➔ ", font=ctk.CTkFont(size=14, weight="bold"), text_color=C_SUBTEXT).pack(side="left", padx=4)
            lbl_c = ctk.CTkLabel(
                f_bread_in, 
                text=f"📍 {centro_activo}", 
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=C_PURPLE
            )
            lbl_c.pack(side="left", padx=4)

        # Botón para volver un nivel
        if centro_activo:
            btn_volver = ctk.CTkButton(
                f_bread_in, 
                text=f"⬅ Volver a {simplificar_nombre_red(red_activa) if red_activa else 'Redes'}", 
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#F1F5F9",
                text_color=C_TEXT,
                hover_color="#E2E8F0",
                height=28,
                corner_radius=8,
                command=lambda: self.navegar_a_red(red_activa) if red_activa else self.navegar_a_global()
            )
            btn_volver.pack(side="right")
        elif red_activa:
            btn_volver = ctk.CTkButton(
                f_bread_in, 
                text="⬅ Volver a Todas las Redes", 
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#F1F5F9",
                text_color=C_TEXT,
                hover_color="#E2E8F0",
                height=28,
                corner_radius=8,
                command=self.navegar_a_global
            )
            btn_volver.pack(side="right")

        # ----------------------------------------------------
        # CARD 1: CENSO JERÁRQUICO (TARJETAS CLICABLES)
        # ----------------------------------------------------
        f_card_dist = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_dist.grid(row=1, column=0, columnspan=2, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_dist)
        items_censo, modo_censo, eqs_contexto, tit_censo = self.dibujar_distribucion_censo(f_card_dist, todos_equipos, red_activa, centro_activo)

        # ----------------------------------------------------
        # CARD 2.1: GRÁFICA VISUAL DE DISTRIBUCIÓN (BARRAS)
        # ----------------------------------------------------
        f_card_g1 = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_g1.grid(row=2, column=0, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_g1)
        self.dibujar_grafica_distribucion_equipos(f_card_g1, items_censo, modo_censo)

        # ----------------------------------------------------
        # CARD 2.2: GRÁFICA DE TIPOS DE EQUIPOS MÁS FRECUENTES
        # ----------------------------------------------------
        f_card_g2 = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_g2.grid(row=2, column=1, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_g2)
        self.dibujar_grafica_tipos_equipos(f_card_g2, eqs_contexto, modo_censo)

        # ----------------------------------------------------
        # CARD 3: TABLA DE EQUIPOS EN LA MISMA PESTAÑA
        # (Se muestra siempre, permitiendo explorar equipos directamente)
        # ----------------------------------------------------
        f_card_tabla = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_tabla.grid(row=3, column=0, columnspan=2, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_tabla)
        self.dibujar_tabla_equipos_en_pestana(f_card_tabla, eqs_contexto, modo_censo, red_activa, centro_activo)

        # Extraer intervenciones de mantenimiento
        intervenciones = []
        for eq in eqs_contexto:
            for m in eq.get("historial_intervenciones", []):
                f_parsed = self.parsear_fecha(m.get("fecha"))
                if f_parsed:
                    intervenciones.append({
                        "eq_id": eq["id"],
                        "eq_nombre": eq["nombre"],
                        "area": eq.get("area", "Sin Área"),
                        "fecha": f_parsed,
                        "tipo": m.get("tipo"),
                        "repuesto_usado": m.get("repuesto_usado", False),
                        "repuesto_nombre": m.get("repuesto_nombre", ""),
                        "repuesto_cantidad": m.get("repuesto_cantidad", 0)
                    })

        # Filtrar por el año seleccionado
        anio_sel = int(self.combo_anio.get())
        inter_anio = [i for i in intervenciones if i["fecha"].year == anio_sel]

        # ----------------------------------------------------
        # CARD 4: MANTENIMIENTOS POR MES (PREVENTIVOS VS CORRECTIVOS)
        # ----------------------------------------------------
        f_card_m = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_m.grid(row=4, column=0, columnspan=2, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_m)
        self.dibujar_mensuales(f_card_m, inter_anio, anio_sel)

        # ----------------------------------------------------
        # CARD 5: PROPORCIÓN Y TOP EQUIPOS
        # ----------------------------------------------------
        f_card_p = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_p.grid(row=5, column=0, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_p)
        self.dibujar_proporcion_tipo(f_card_p, inter_anio, anio_sel)

        f_card_t = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_t.grid(row=5, column=1, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_t)
        self.dibujar_top_equipos(f_card_t, inter_anio)

        # ----------------------------------------------------
        # CARD 6: TOP ÁREAS Y REPUESTOS
        # ----------------------------------------------------
        f_card_a = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_a.grid(row=6, column=0, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_a)
        self.dibujar_top_areas(f_card_a, inter_anio)

        f_card_r = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card_r.grid(row=6, column=1, padx=12, pady=8, sticky="nsew")
        self.canvas_widgets.append(f_card_r)
        self.dibujar_top_repuestos(f_card_r, inter_anio)

    # ========================================================
    # CENSO Y DISTRIBUCIÓN JERÁRQUICA INTERACTIVA
    # ========================================================
    def dibujar_distribucion_censo(self, parent, todos_equipos, red_activa, centro_activo):
        f_header = ctk.CTkFrame(parent, fg_color="transparent")
        f_header.pack(fill="x", padx=16, pady=(14, 6))

        if not red_activa and not centro_activo:
            titulo_seccion = "🌐 Censo y Distribución de Equipos Médicos por Red de Salud"
            sub_seccion = f"Total en GAMLP: {len(todos_equipos):,} equipos | Haz clic en una Red para abrir sus Centros y Equipos"
            
            grupos = {}
            for eq in todos_equipos:
                r_nom = eq.get("red_salud_nombre") or "Sin Red Asignada"
                grupos.setdefault(r_nom, []).append(eq)
                
            items_ordenados = sorted(grupos.items(), key=lambda x: str(x[0]))
            modo = "red"
            eqs_contexto = todos_equipos

        elif red_activa and not centro_activo:
            eqs_en_red = [e for e in todos_equipos if str(e.get("red_salud_nombre", "")).strip().lower() == str(red_activa).strip().lower()]
            r_corta = simplificar_nombre_red(red_activa)
            titulo_seccion = f"🏥 Distribución de Equipos por Centro de Salud — {r_corta}"
            sub_seccion = f"Total en esta Red: {len(eqs_en_red):,} equipos en {len(set(e.get('centro_salud_nombre') for e in eqs_en_red)):,} centros | Haz clic en un Centro para ver sus Áreas"
            
            grupos = {}
            for eq in eqs_en_red:
                c_nom = eq.get("centro_salud_nombre") or "Centro No Asignado"
                grupos.setdefault(c_nom, []).append(eq)
                
            items_ordenados = sorted(grupos.items(), key=lambda x: len(x[1]), reverse=True)
            modo = "centro"
            eqs_contexto = eqs_en_red

        else:
            eqs_en_centro = [e for e in todos_equipos if str(e.get("centro_salud_nombre", "")).strip().lower() == str(centro_activo).strip().lower()]
            titulo_seccion = f"📍 Distribución de Equipos por Área / Servicio — {centro_activo}"
            sub_seccion = f"Total en este Centro: {len(eqs_en_centro):,} equipos | Haz clic en un Área para filtrar los equipos"
            
            grupos = {}
            for eq in eqs_en_centro:
                a_nom = eq.get("area") or eq.get("servicio") or "General"
                grupos.setdefault(a_nom, []).append(eq)
                
            items_ordenados = sorted(grupos.items(), key=lambda x: len(x[1]), reverse=True)
            modo = "area"
            eqs_contexto = eqs_en_centro

        ctk.CTkLabel(f_header, text=titulo_seccion, font=ctk.CTkFont(size=17, weight="bold"), text_color=C_TEXT).pack(anchor="w")
        ctk.CTkLabel(f_header, text=sub_seccion, font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(anchor="w", pady=(2, 0))

        # Contenedor de Tarjetas Interactivas
        f_cards_grid = ctk.CTkFrame(parent, fg_color="transparent")
        f_cards_grid.pack(fill="x", padx=16, pady=(10, 16))

        palette = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#DC2626", "#0891B2", "#4F46E5", "#EA580C"]

        if not items_ordenados:
            ctk.CTkLabel(f_cards_grid, text="No hay equipos registrados para este filtro.", font=ctk.CTkFont(size=13), text_color=C_SUBTEXT).pack(pady=20)
            return items_ordenados, modo, eqs_contexto, titulo_seccion

        max_cols = 3 if modo == "centro" or modo == "area" else 5
        for idx, (nombre_item, eqs_grupo) in enumerate(items_ordenados):
            row_i = idx // max_cols
            col_i = idx % max_cols
            
            color_accent = palette[idx % len(palette)]
            cant_eqs = len(eqs_grupo)
            
            display_title = simplificar_nombre_red(nombre_item) if modo == "red" else nombre_item
            if len(display_title) > 28:
                display_title = display_title[:26] + "..."

            card_btn = ctk.CTkFrame(f_cards_grid, fg_color="#F8FAFC", corner_radius=12, border_width=1, border_color="#E2E8F0")
            card_btn.grid(row=row_i, column=col_i, padx=6, pady=6, sticky="nsew")
            f_cards_grid.columnconfigure(col_i, weight=1)

            bar_acc = ctk.CTkFrame(card_btn, fg_color=color_accent, height=4, corner_radius=2)
            bar_acc.pack(fill="x", side="top")

            f_in = ctk.CTkFrame(card_btn, fg_color="transparent")
            f_in.pack(fill="both", expand=True, padx=12, pady=10)

            ctk.CTkLabel(f_in, text=display_title, font=ctk.CTkFont(size=13, weight="bold"), text_color=C_TEXT, wraplength=180).pack(anchor="w")
            
            f_num = ctk.CTkFrame(f_in, fg_color="transparent")
            f_num.pack(fill="x", pady=(6, 8))
            ctk.CTkLabel(f_num, text=f"{cant_eqs}", font=ctk.CTkFont(size=22, weight="bold"), text_color=color_accent).pack(side="left")
            ctk.CTkLabel(f_num, text=" equipos", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(side="left", padx=4, pady=(6, 0))

            # Acción de navegación al hacer clic
            if modo == "red":
                btn_txt = "📊 Abrir Centros"
                cmd_accion = lambda n=nombre_item: self.navegar_a_red(n)
            elif modo == "centro":
                btn_txt = "📍 Abrir Áreas y Equipos"
                cmd_accion = lambda n=nombre_item: self.navegar_a_centro(n)
            else:
                btn_txt = "🔍 Filtrar esta Área"
                cmd_accion = lambda n=nombre_item, eq_list=eqs_grupo: self.abrir_modal_detalle_equipos(n, eq_list, "area")

            btn_ver = ctk.CTkButton(
                f_in, 
                text=btn_txt, 
                font=ctk.CTkFont(size=11, weight="bold"), 
                height=28, 
                fg_color=color_accent, 
                hover_color="#1E293B",
                corner_radius=8,
                command=cmd_accion
            )
            btn_ver.pack(fill="x", pady=(2, 0))

        return items_ordenados, modo, eqs_contexto, titulo_seccion

    # ========================================================
    # GRÁFICA VISUAL 1: DISTRIBUCIÓN DE EQUIPOS (BARRAS)
    # ========================================================
    def dibujar_grafica_distribucion_equipos(self, parent, items_ordenados, modo):
        if modo == "red":
            tit = "Distribución de Equipos Médicos por Red"
        elif modo == "centro":
            tit = "Equipos por Centro de Salud en esta Red"
        else:
            tit = "Cantidad de Equipos por Área Clínica"

        ctk.CTkLabel(parent, text=tit, font=ctk.CTkFont(size=15, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))

        if not items_ordenados:
            ctk.CTkLabel(parent, text="Sin datos disponibles.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        items_plot = items_ordenados[:10]
        if modo == "red":
            nombres = [simplificar_nombre_red(n) for n, _ in items_plot]
        else:
            nombres = [n[:16] + '..' if len(n) > 18 else n for n, _ in items_plot]
        
        cantidades = [len(eqs) for _, eqs in items_plot]

        fig, ax = plt.subplots(figsize=(4.5, 3.2))
        self.figuras.append(fig)
        self.configurar_estilo_figura(fig, ax, "")

        if modo == "red":
            colores = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#DC2626"]
            bars = ax.bar(nombres, cantidades, color=colores[:len(nombres)], width=0.55)
            ax.grid(axis='y', linestyle='--', alpha=0.3, color=C_SUBTEXT)
            ax.bar_label(bars, color=C_TEXT, padding=3, weight="bold", size=10)
        else:
            bars = ax.barh(nombres, cantidades, color="#2563EB", height=0.55)
            ax.invert_yaxis()
            ax.grid(axis='x', linestyle='--', alpha=0.3, color=C_SUBTEXT)
            ax.bar_label(bars, color=C_TEXT, padding=3, weight="bold", size=10)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ========================================================
    # GRÁFICA VISUAL 2: TIPOS DE EQUIPOS MÁS FRECUENTES
    # ========================================================
    def dibujar_grafica_tipos_equipos(self, parent, eqs_contexto, modo):
        if modo == "area":
            tit = "Tipos de Equipos en este Hospital y Área"
        elif modo == "centro":
            tit = "Tipos de Equipos en este Centro de Salud"
        else:
            tit = "Tipos de Equipos Médicos más Frecuentes"

        ctk.CTkLabel(parent, text=tit, font=ctk.CTkFont(size=15, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))

        if not eqs_contexto:
            ctk.CTkLabel(parent, text="Sin datos de equipos.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        conteo_tipos = Counter([eq.get("nombre", "Equipo").strip() for eq in eqs_contexto if eq.get("nombre")])
        top_tipos = conteo_tipos.most_common(7)

        if not top_tipos:
            ctk.CTkLabel(parent, text="Sin datos.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        nombres, counts = zip(*top_tipos)
        nombres = [n[:16] + '..' if len(n) > 18 else n for n in nombres]

        fig, ax = plt.subplots(figsize=(4.5, 3.2))
        self.figuras.append(fig)
        self.configurar_estilo_figura(fig, ax, "")

        bars = ax.barh(nombres, counts, color="#059669", height=0.55)
        ax.invert_yaxis()
        ax.grid(axis='x', linestyle='--', alpha=0.3, color=C_SUBTEXT)
        ax.bar_label(bars, color=C_TEXT, padding=3, weight="bold", size=10)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ========================================================
    # SECCIÓN DE TABLA DE EQUIPOS EN LA MISMA PESTAÑA
    # ========================================================
    def dibujar_tabla_equipos_en_pestana(self, parent, eqs_lista, modo, red_activa, centro_activo):
        # Cabecera de la sección de tabla
        f_top = ctk.CTkFrame(parent, fg_color="transparent")
        f_top.pack(fill="x", padx=16, pady=(14, 8))

        if centro_activo:
            tit_t = f"📋 Inventario de Equipos Médicos — {centro_activo}"
            sub_t = f"{len(eqs_lista)} equipos registrados | Doble clic en cualquier fila para ver su Ficha Técnica"
        elif red_activa:
            tit_t = f"📋 Inventario de Equipos Médicos — {simplificar_nombre_red(red_activa)}"
            sub_t = f"{len(eqs_lista)} equipos en esta Red | Doble clic en cualquier fila para ver su Ficha Técnica"
        else:
            tit_t = "📋 Listado de Equipos Médicos Consolidados (GAMLP)"
            sub_t = f"{len(eqs_lista)} equipos registrados en total | Doble clic en cualquier fila para ver su Ficha Técnica"

        f_tit = ctk.CTkFrame(f_top, fg_color="transparent")
        f_tit.pack(side="left")
        ctk.CTkLabel(f_tit, text=tit_t, font=ctk.CTkFont(size=16, weight="bold"), text_color=C_TEXT).pack(anchor="w")
        ctk.CTkLabel(f_tit, text=sub_t, font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(anchor="w", pady=(2, 0))

        # Buscador rápido
        f_search = ctk.CTkFrame(f_top, fg_color="transparent")
        f_search.pack(side="right")
        ctk.CTkLabel(f_search, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=4)
        
        e_busq = ctk.CTkEntry(
            f_search, 
            textvariable=self.busqueda_tabla_var, 
            placeholder_text="Buscar equipo, marca, Cod. AF...", 
            width=240, 
            fg_color=C_BG, 
            border_color=C_BORDER, 
            corner_radius=8
        )
        e_busq.pack(side="left")

        # Contenedor de la tabla Treeview
        f_tab_box = ctk.CTkFrame(parent, fg_color="transparent")
        f_tab_box.pack(fill="x", padx=16, pady=(4, 14))

        cols = ("Red", "Centro de Salud", "Área/Servicio", "Equipo Médico", "Marca", "Modelo", "Cod. AF", "Estado")
        tree = ttk.Treeview(f_tab_box, columns=cols, show="headings", height=8, selectmode="browse")
        sb = ttk.Scrollbar(f_tab_box, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree.configure(yscrollcommand=sb.set)

        col_w = {"Red": 75, "Centro de Salud": 170, "Área/Servicio": 130, "Equipo Médico": 200, "Marca": 100, "Modelo": 100, "Cod. AF": 100, "Estado": 90}
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=col_w.get(c, 100))

        tree.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")

        def _poblar_tabla_inline():
            for i in tree.get_children():
                tree.delete(i)
            filtro = self.busqueda_tabla_var.get().lower().strip()
            for eq in eqs_lista:
                eq_nom = str(eq.get("nombre", ""))
                eq_id = str(eq.get("id", ""))
                eq_mar = str(eq.get("marca") or "-")
                eq_mod = str(eq.get("modelo") or "-")
                eq_cen = str(eq.get("centro_salud_nombre") or "-")
                eq_ser = str(eq.get("servicio") or eq.get("area") or "-")
                eq_red = simplificar_nombre_red(eq.get("red_salud_nombre"))
                eq_est = str(eq.get("estado") or "Operativo")

                if filtro:
                    if not (filtro in eq_nom.lower() or filtro in eq_id.lower() or filtro in eq_mar.lower() or filtro in eq_mod.lower() or filtro in eq_cen.lower() or filtro in eq_ser.lower()):
                        continue

                tree.insert("", "end", values=(eq_red, eq_cen, eq_ser, eq_nom, eq_mar, eq_mod, eq_id, eq_est))

        self.busqueda_tabla_var.trace_add("write", lambda *args: _poblar_tabla_inline())
        _poblar_tabla_inline()

        def _abrir_hv_inline(event=None):
            sel = tree.selection() or ([tree.focus()] if tree.focus() else [])
            if sel:
                v = tree.item(sel[0], "values")
                eq_id = v[6] if len(v) > 6 else v[0]
                self.app.abrir_hoja_vida_click(equipo_id=eq_id)

        tree.bind("<Double-1>", _abrir_hv_inline)

    # ========================================================
    # MODAL INTERACTIVO DE DETALLE DE EQUIPOS
    # ========================================================
    def abrir_modal_detalle_equipos(self, nombre_grupo, lista_equipos, modo):
        if self.modal_equipos and self.modal_equipos.winfo_exists():
            self.modal_equipos.destroy()

        self.modal_equipos = ctk.CTkToplevel(self)
        self.modal_equipos.title(f"Detalle de Equipos: {nombre_grupo}")
        self.modal_equipos.geometry("980x620")
        self.modal_equipos.minsize(800, 500)
        self.modal_equipos.configure(fg_color=C_BG)
        self.modal_equipos.transient(self.app)
        self.modal_equipos.focus_force()

        f_top = ctk.CTkFrame(self.modal_equipos, fg_color=C_CARD, corner_radius=0, height=70)
        f_top.pack(fill="x", side="top")
        
        f_title = ctk.CTkFrame(f_top, fg_color="transparent")
        f_title.pack(side="left", padx=20, pady=12)
        
        titulo_modal = f"Equipos en: {simplificar_nombre_red(nombre_grupo) if modo == 'red' else nombre_grupo}"
        ctk.CTkLabel(f_title, text=titulo_modal, font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(anchor="w")
        ctk.CTkLabel(f_title, text=f"Total: {len(lista_equipos)} equipos médicos registrados | Doble clic en cualquier fila para ver Ficha Técnica", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(anchor="w")

        busq_modal_var = ctk.StringVar()
        f_search = ctk.CTkFrame(f_top, fg_color="transparent")
        f_search.pack(side="right", padx=20, pady=12)
        ctk.CTkLabel(f_search, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=4)
        e_busq = ctk.CTkEntry(f_search, textvariable=busq_modal_var, placeholder_text="Buscar en esta lista...", width=220, fg_color=C_BG, border_color=C_BORDER, corner_radius=8)
        e_busq.pack(side="left")

        f_tabla = ctk.CTkFrame(self.modal_equipos, fg_color="transparent")
        f_tabla.pack(fill="both", expand=True, padx=20, pady=15)

        cols = ("Red", "Centro de Salud", "Área/Servicio", "Equipo Médico", "Marca", "Modelo", "Cod. AF", "Estado")
        tree = ttk.Treeview(f_tabla, columns=cols, show="headings", selectmode="browse")
        sb = ttk.Scrollbar(f_tabla, orient="vertical", command=tree.yview, style="Vertical.TScrollbar")
        tree.configure(yscrollcommand=sb.set)

        col_w = {"Red": 75, "Centro de Salud": 170, "Área/Servicio": 130, "Equipo Médico": 200, "Marca": 100, "Modelo": 100, "Cod. AF": 100, "Estado": 90}
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=col_w.get(c, 100))

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def _poblar_tabla():
            for i in tree.get_children():
                tree.delete(i)
            filtro = busq_modal_var.get().lower().strip()
            for eq in lista_equipos:
                eq_nom = str(eq.get("nombre", ""))
                eq_id = str(eq.get("id", ""))
                eq_mar = str(eq.get("marca") or "-")
                eq_mod = str(eq.get("modelo") or "-")
                eq_cen = str(eq.get("centro_salud_nombre") or "-")
                eq_ser = str(eq.get("servicio") or eq.get("area") or "-")
                eq_red = simplificar_nombre_red(eq.get("red_salud_nombre"))
                eq_est = str(eq.get("estado") or "Operativo")

                if filtro:
                    if not (filtro in eq_nom.lower() or filtro in eq_id.lower() or filtro in eq_mar.lower() or filtro in eq_mod.lower() or filtro in eq_cen.lower() or filtro in eq_ser.lower()):
                        continue

                tree.insert("", "end", values=(eq_red, eq_cen, eq_ser, eq_nom, eq_mar, eq_mod, eq_id, eq_est))

        busq_modal_var.trace_add("write", lambda *args: _poblar_tabla())
        _poblar_tabla()

        def _abrir_hv_desde_modal(event=None):
            sel = tree.selection() or ([tree.focus()] if tree.focus() else [])
            if sel:
                v = tree.item(sel[0], "values")
                eq_id = v[6] if len(v) > 6 else v[0]
                self.app.abrir_hoja_vida_click(equipo_id=eq_id)

        tree.bind("<Double-1>", _abrir_hv_desde_modal)

        f_bot = ctk.CTkFrame(self.modal_equipos, fg_color=C_CARD, corner_radius=0, height=50)
        f_bot.pack(fill="x", side="bottom")

        btn_abrir = ctk.CTkButton(f_bot, text="📄 Ver Ficha Técnica / Hoja de Vida", font=ctk.CTkFont(weight="bold", size=12), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, height=36, corner_radius=8, command=_abrir_hv_desde_modal)
        btn_abrir.pack(side="left", padx=20, pady=10)

        btn_cerrar = ctk.CTkButton(f_bot, text="Cerrar", font=ctk.CTkFont(weight="bold", size=12), fg_color=C_CARD, text_color=C_TEXT, hover_color=C_BORDER, height=36, corner_radius=8, command=self.modal_equipos.destroy)
        btn_cerrar.pack(side="right", padx=20, pady=10)

    # ========================================================
    # FUNCIONES AUXILIARES DE DIBUJO DE GRÁFICOS
    # ========================================================
    def configurar_estilo_figura(self, fig, ax, titulo):
        fig.patch.set_facecolor(C_BG)
        ax.set_facecolor(C_BG)
        if titulo:
            ax.set_title(titulo, fontsize=14, weight="bold", color=C_TEXT, pad=15, family="Segoe UI")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(C_BORDER)
        ax.spines['bottom'].set_color(C_BORDER)
        ax.tick_params(colors=C_SUBTEXT, labelsize=10)

    def dibujar_mensuales(self, parent, inter, anio):
        ctk.CTkLabel(parent, text="Resumen Mensual de Intervenciones", font=ctk.CTkFont(size=16, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))
        
        if not inter:
            ctk.CTkLabel(parent, text="No hay registros de mantenimientos en este año para el filtro seleccionado.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        prevs_por_mes = [0] * 12
        corrs_por_mes = [0] * 12
        for i in inter:
            m_idx = i["fecha"].month - 1
            if i["tipo"] == "Preventivo":
                prevs_por_mes[m_idx] += 1
            elif i["tipo"] == "Correctivo":
                corrs_por_mes[m_idx] += 1

        nombres_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        fig, ax = plt.subplots(figsize=(9, 3.2))
        self.figuras.append(fig)
        self.configurar_estilo_figura(fig, ax, f"Mantenimientos por Mes - Gestión {anio}")

        width = 0.35
        x = range(12)
        
        rects1 = ax.bar([pos - width/2 for pos in x], prevs_por_mes, width, label='Preventivo', color=C_GREEN)
        rects2 = ax.bar([pos + width/2 for pos in x], corrs_por_mes, width, label='Correctivo', color=C_RED)

        ax.set_xticks(x)
        ax.set_xticklabels(nombres_meses)
        ax.legend(facecolor=C_CARD, edgecolor="none", labelcolor=C_TEXT)
        ax.grid(axis='y', linestyle='--', alpha=0.3, color=C_SUBTEXT)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def dibujar_proporcion_tipo(self, parent, inter, anio):
        ctk.CTkLabel(parent, text="Proporción por Tipo de Intervención", font=ctk.CTkFont(size=15, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))
        
        if not inter:
            ctk.CTkLabel(parent, text="No hay registros para este año.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        tipos = [i["tipo"] for i in inter if i["tipo"] in ["Preventivo", "Correctivo"]]
        c = Counter(tipos)
        
        if not c:
            ctk.CTkLabel(parent, text="No hay clasificaciones preventivas o correctivas.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        labels = list(c.keys())
        sizes = list(c.values())
        colors = [C_GREEN if l == "Preventivo" else C_RED for l in labels]

        fig, ax = plt.subplots(figsize=(4, 3))
        self.figuras.append(fig)
        fig.patch.set_facecolor(C_BG)
        ax.set_facecolor(C_BG)

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          startangle=90, colors=colors, 
                                          textprops=dict(color=C_TEXT, weight="bold", size=9),
                                          wedgeprops=dict(width=0.4, edgecolor='none'))

        ax.legend(wedges, labels, title="Tipo", loc="center left", bbox_to_anchor=(0.85, 0.5), facecolor=C_CARD, edgecolor="none", labelcolor=C_TEXT)
        ax.axis('equal')  

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def dibujar_top_equipos(self, parent, inter):
        ctk.CTkLabel(parent, text="Equipos con Mayor Frecuencia de Fallos/Mantenimientos", font=ctk.CTkFont(size=15, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))
        
        if not inter:
            ctk.CTkLabel(parent, text="No hay registros para este año.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        equipos = [i["eq_nombre"] for i in inter]
        c = Counter(equipos).most_common(5)
        
        if not c:
            ctk.CTkLabel(parent, text="No hay datos de equipos.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        nombres, counts = zip(*c)
        nombres = [n[:18] + '..' if len(n) > 20 else n for n in nombres]

        fig, ax = plt.subplots(figsize=(4.5, 3))
        self.figuras.append(fig)
        self.configurar_estilo_figura(fig, ax, "Top 5 Equipos Más Intervenidos")

        bars = ax.barh(nombres, counts, color=C_BLUE, height=0.55)
        ax.invert_yaxis()
        ax.grid(axis='x', linestyle='--', alpha=0.3, color=C_SUBTEXT)
        ax.bar_label(bars, color=C_TEXT, padding=3, weight="bold")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def dibujar_top_areas(self, parent, inter):
        ctk.CTkLabel(parent, text="Áreas Clínicas que más Mantenimientos Piden", font=ctk.CTkFont(size=15, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))
        
        if not inter:
            ctk.CTkLabel(parent, text="No hay registros para este año.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        areas = [i["area"] for i in inter if i["area"]]
        c = Counter(areas).most_common(5)
        
        if not c:
            ctk.CTkLabel(parent, text="No hay datos de áreas.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        nombres, counts = zip(*c)
        nombres = [n[:18] + '..' if len(n) > 20 else n for n in nombres]

        fig, ax = plt.subplots(figsize=(4.5, 3))
        self.figuras.append(fig)
        self.configurar_estilo_figura(fig, ax, "Top 5 Áreas Clínicas")

        bars = ax.barh(nombres, counts, color=C_PURPLE, height=0.55)
        ax.invert_yaxis()
        ax.grid(axis='x', linestyle='--', alpha=0.3, color=C_SUBTEXT)
        ax.bar_label(bars, color=C_TEXT, padding=3, weight="bold")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def dibujar_top_repuestos(self, parent, inter):
        ctk.CTkLabel(parent, text="Repuestos Más Utilizados (Top 5 Cantidades)", font=ctk.CTkFont(size=15, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))
        
        rep_counts = {}
        for i in inter:
            if i["repuesto_usado"] and i["repuesto_nombre"]:
                rep_counts[i["repuesto_nombre"]] = rep_counts.get(i["repuesto_nombre"], 0) + int(i["repuesto_cantidad"])

        if not rep_counts:
            ctk.CTkLabel(parent, text="No hay repuestos registrados en este año.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        top_reps = sorted(rep_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        nombres, counts = zip(*top_reps)
        nombres = [n[:12] + '..' if len(n) > 14 else n for n in nombres]

        fig, ax = plt.subplots(figsize=(4.5, 3))
        self.figuras.append(fig)
        self.configurar_estilo_figura(fig, ax, "Top 5 Repuestos Usados")

        bars = ax.bar(nombres, counts, color=C_YELLOW, width=0.5)
        ax.grid(axis='y', linestyle='--', alpha=0.3, color=C_SUBTEXT)
        ax.bar_label(bars, color=C_TEXT, padding=3, weight="bold")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
