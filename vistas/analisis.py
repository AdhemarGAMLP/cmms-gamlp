# vistas/analisis.py
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from estilos import *
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

class VistaAnalisis(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.hoy = self.app.hoy
        self.anio_actual = self.hoy.year
        self.canvas_widgets = [] # Guardar referencias para limpiar en cada refresco
        self.figuras = [] # Guardar referencias de figuras matplotlib
        self.construir_ui()

    def construir_ui(self):
        # Cabecera
        f_cab = ctk.CTkFrame(self, fg_color="transparent")
        f_cab.pack(pady=(30, 10), padx=30, fill="x")
        ctk.CTkLabel(f_cab, text="Estadísticas y Análisis de Mantenimiento", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        # Selector de Año
        f_filtro = ctk.CTkFrame(f_cab, fg_color="transparent")
        f_filtro.pack(side="right")
        ctk.CTkLabel(f_filtro, text="Año de Análisis:", font=ctk.CTkFont(weight="bold", size=13), text_color=C_TEXT).pack(side="left", padx=5)
        
        self.combo_anio = ctk.CTkComboBox(f_filtro, values=["2026", "2027", "2028"], command=lambda e: self.refrescar_datos(), width=100, fg_color=C_CARD, border_color=C_BORDER)
        self.combo_anio.pack(side="left", padx=5)
        self.combo_anio.set(str(self.anio_actual))

        # Contenedor con Scroll para gráficos
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
        # Destruir widgets de tkinter
        for widget in self.canvas_widgets:
            widget.destroy()
        self.canvas_widgets.clear()
        
        # Cerrar figuras matplotlib para liberar memoria
        for fig in self.figuras:
            plt.close(fig)
        self.figuras.clear()

    def refrescar_datos(self):
        self.limpiar_graficos()
        
        # Extraer todas las intervenciones completadas desde memoria
        intervenciones = []
        for eq in self.app.datos.get("equipos", []):
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
        # CARD 1: MANTENIMIENTOS POR MES (PREVENTIVOS VS CORRECTIVOS)
        # ----------------------------------------------------
        f_card1 = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card1.grid(row=0, column=0, columnspan=2, padx=12, pady=12, sticky="nsew")
        self.canvas_widgets.append(f_card1)
        self.dibujar_mensuales(f_card1, inter_anio, anio_sel)

        # ----------------------------------------------------
        # CARD 2: TIPO DE MANTENIMIENTO (PIE CHART)
        # ----------------------------------------------------
        f_card2 = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card2.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.canvas_widgets.append(f_card2)
        self.dibujar_proporcion_tipo(f_card2, inter_anio, anio_sel)

        # ----------------------------------------------------
        # CARD 3: TOP 5 EQUIPOS CON MÁS MANTENIMIENTOS
        # ----------------------------------------------------
        f_card3 = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card3.grid(row=1, column=1, padx=12, pady=12, sticky="nsew")
        self.canvas_widgets.append(f_card3)
        self.dibujar_top_equipos(f_card3, inter_anio)

        # ----------------------------------------------------
        # CARD 4: TOP 5 ÁREAS CON MÁS MANTENIMIENTOS
        # ----------------------------------------------------
        f_card4 = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card4.grid(row=2, column=0, padx=12, pady=12, sticky="nsew")
        self.canvas_widgets.append(f_card4)
        self.dibujar_top_areas(f_card4, inter_anio)

        # ----------------------------------------------------
        # CARD 5: REPUESTOS MÁS UTILIZADOS (TOP 5)
        # ----------------------------------------------------
        f_card5 = ctk.CTkFrame(self.scroll_frame, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_card5.grid(row=2, column=1, padx=12, pady=12, sticky="nsew")
        self.canvas_widgets.append(f_card5)
        self.dibujar_top_repuestos(f_card5, inter_anio)


    # ========================================================
    # FUNCIONES AUXILIARES DE DIBUJO DE GRÁFICOS
    # ========================================================
    def configurar_estilo_figura(self, fig, ax, titulo):
        fig.patch.set_facecolor(C_BG)
        ax.set_facecolor(C_BG)
        ax.set_title(titulo, fontsize=14, weight="bold", color=C_TEXT, pad=15, family="Segoe UI")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(C_BORDER)
        ax.spines['bottom'].set_color(C_BORDER)
        ax.tick_params(colors=C_SUBTEXT, labelsize=10)

    def dibujar_mensuales(self, parent, inter, anio):
        ctk.CTkLabel(parent, text="Resumen Mensual de Intervenciones", font=ctk.CTkFont(size=16, weight="bold"), text_color=C_TEXT).pack(pady=(10, 5))
        
        if not inter:
            ctk.CTkLabel(parent, text="No hay registros de mantenimientos en este año.", font=ctk.CTkFont(size=12), text_color=C_SUBTEXT).pack(pady=40)
            return

        # Agrupar por mes y tipo
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

        # Centrar leyenda y mejorar aspecto circular
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
        nombres = [n[:18] + '..' if len(n) > 20 else n for n in nombres] # truncar etiquetas largas

        fig, ax = plt.subplots(figsize=(4.5, 3))
        self.figuras.append(fig)
        self.configurar_estilo_figura(fig, ax, "Top 5 Equipos Más Intervenidos")

        bars = ax.barh(nombres, counts, color=C_BLUE, height=0.55)
        ax.invert_yaxis()  # Mostrar mayor arriba
        ax.grid(axis='x', linestyle='--', alpha=0.3, color=C_SUBTEXT)
        
        # Agregar etiquetas de valor a las barras
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
        
        # Consolidar cantidades por repuesto
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
