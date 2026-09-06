# -*- coding: utf-8 -*-
"""
VISTA DE MAPA SATELITAL Y DE CALOR TERRITORIAL GAMLP (DESKTOP)
==============================================================
Proporciona:
1. Resumen y Censo Geoespacial de Equipos por Centro de Salud.
2. Botón de Apertura Rápida del Visor Satelital y de Calor Interactivo (Leaflet + ESRI).
3. KPIs de Cobertura Territorial y Salud Municipal.
"""

import os
import webbrowser
import tempfile
import customtkinter as ctk
from tkinter import ttk, messagebox

from estilos import (
    C_BG, C_CARD, C_BORDER, C_TEXT, C_SUBTEXT, 
    C_BLUE, C_BLUE_HOVER, C_GREEN, C_RED, C_PURPLE, C_AMBER
)
from mapa_geo_utils import (
    consolidar_datos_geoespaciales,
    generar_html_mapa_gamlp
)

class VistaMapa(ctk.CTkFrame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.app = app_controller
        self.centros_geo = []
        self._debounce_timer = None

        self.construir_ui()

    def construir_ui(self):
        # Cabecera
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(fill="x", padx=25, pady=(15, 10))

        lbl_tit = ctk.CTkLabel(
            f_top, 
            text="🛰️ Mapa Satelital y de Calor Territorial GAMLP", 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color=C_TEXT
        )
        lbl_tit.pack(side="left")

        btn_abrir_mapa = ctk.CTkButton(
            f_top, 
            text="🌐 Abrir Visor Satelital Fullscreen", 
            font=ctk.CTkFont(weight="bold", size=13),
            fg_color="#2563EB", 
            hover_color="#1D4ED8",
            height=38,
            command=self.abrir_visor_mapa_navegador
        )
        btn_abrir_mapa.pack(side="right")

        # Tarjetas KPI Territoriales
        self.f_kpis = ctk.CTkFrame(self, fg_color="transparent")
        self.f_kpis.pack(fill="x", padx=25, pady=(0, 10))
        self.f_kpis.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_centros = self.crear_kpi_card(self.f_kpis, 0, "🏥 Centros de Salud Georreferenciados", "0 Centros", "#F8FAFC", "#2563EB")
        self.kpi_total_eq = self.crear_kpi_card(self.f_kpis, 1, "📦 Equipos Mapeados en La Paz", "0 Equipos", "#EFF6FF", "#1D4ED8")
        self.kpi_operatividad = self.crear_kpi_card(self.f_kpis, 2, "🟢 Operatividad Promedio Territorial", "0 %", "#F0FDF4", "#16A34A")
        self.kpi_red_mayor = self.crear_kpi_card(self.f_kpis, 3, "🏆 Red con Mayor Dotación", "-", "#FAF5FF", "#7C3AED")

        # Barra de Filtros
        f_filtros = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E2E8F0")
        f_filtros.pack(fill="x", padx=25, pady=(0, 10))

        ctk.CTkLabel(f_filtros, text="Filtrar por Red:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 4), pady=8)
        self.cb_red_mapa = ctk.CTkComboBox(f_filtros, values=["[ Todas las Redes ]"], width=260, height=34, command=lambda v: self.filtrar_tabla_centros())
        self.cb_red_mapa.pack(side="left", padx=4, pady=8)

        self.e_buscar_centro = ctk.CTkEntry(f_filtros, placeholder_text="🔍 Buscar centro o nivel...", width=220, height=34)
        self.e_buscar_centro.pack(side="right", padx=15, pady=8)
        self.e_buscar_centro.bind("<KeyRelease>", self.on_buscar_debounce)

        btn_ver_centro_mapa = ctk.CTkButton(
            f_filtros,
            text="📍 Centrar en Mapa",
            font=ctk.CTkFont(weight="bold", size=12),
            fg_color=C_BLUE,
            hover_color=C_BLUE_HOVER,
            height=34,
            command=self.abrir_visor_mapa_navegador
        )
        btn_ver_centro_mapa.pack(side="right", padx=5)

        # Tabla Treeview de Centros Georreferenciados
        cols = ("centro", "red", "nivel", "total", "operativos", "baja", "porc", "alto_riesgo", "coords")
        self.tree_centros = ttk.Treeview(self, columns=cols, show="headings", height=14)

        self.tree_centros.heading("centro", text="Centro de Salud / Hospital")
        self.tree_centros.heading("red", text="Red Territorial")
        self.tree_centros.heading("nivel", text="Nivel de Atención")
        self.tree_centros.heading("total", text="Total Equipos")
        self.tree_centros.heading("operativos", text="Operativos")
        self.tree_centros.heading("baja", text="Baja/Falla")
        self.tree_centros.heading("porc", text="% Operatividad")
        self.tree_centros.heading("alto_riesgo", text="Riesgo Alto (IA)")
        self.tree_centros.heading("coords", text="Coordenadas GPS")

        self.tree_centros.column("centro", width=220, anchor="w")
        self.tree_centros.column("red", width=160, anchor="w")
        self.tree_centros.column("nivel", width=140, anchor="center")
        self.tree_centros.column("total", width=95, anchor="center")
        self.tree_centros.column("operativos", width=90, anchor="center")
        self.tree_centros.column("baja", width=85, anchor="center")
        self.tree_centros.column("porc", width=105, anchor="center")
        self.tree_centros.column("alto_riesgo", width=115, anchor="center")
        self.tree_centros.column("coords", width=130, anchor="center")

        scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tree_centros.yview)
        self.tree_centros.configure(yscrollcommand=scroll_y.set)

        self.tree_centros.pack(side="left", fill="both", expand=True, padx=(25, 0), pady=(0, 20))
        scroll_y.pack(side="right", fill="y", padx=(0, 25), pady=(0, 20))

    def crear_kpi_card(self, parent, col, titulo, valor_ini, bg_col, text_col):
        f = ctk.CTkFrame(parent, fg_color=bg_col, corner_radius=10, border_width=1, border_color="#E2E8F0")
        f.grid(row=0, column=col, sticky="nsew", padx=4)
        ctk.CTkLabel(f, text=titulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#475569").pack(anchor="w", padx=12, pady=(8, 2))
        lbl_v = ctk.CTkLabel(f, text=valor_ini, font=ctk.CTkFont(size=16, weight="bold"), text_color=text_col)
        lbl_v.pack(anchor="w", padx=12, pady=(0, 8))
        return lbl_v

    def on_buscar_debounce(self, event=None):
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(150, self.filtrar_tabla_centros)

    def refrescar_datos(self):
        """Consolida la información de inventario y actualiza métricas geoespaciales."""
        equipos = self.app.datos.get("equipos", [])
        sedes_data = getattr(self.app, "sedes_data", {}) or {}
        
        self.centros_geo = consolidar_datos_geoespaciales(equipos, sedes_data)

        # Actualizar opciones de Redes
        redes_disponibles = sorted(list(set(c["red"] for c in self.centros_geo if c.get("red"))))
        self.cb_red_mapa.configure(values=["[ Todas las Redes ]"] + redes_disponibles)

        # Actualizar KPIs
        total_centros = len(self.centros_geo)
        total_eq = sum(c["total_equipos"] for c in self.centros_geo)
        total_op = sum(c["operativos"] for c in self.centros_geo)
        porc_global = round((total_op / max(1, total_eq)) * 100, 1)

        # Red con mayor dotación
        redes_conteos = {}
        for c in self.centros_geo:
            redes_conteos[c["red"]] = redes_conteos.get(c["red"], 0) + c["total_equipos"]
        
        red_top = "-"
        if redes_conteos:
            red_top = max(redes_conteos.items(), key=lambda x: x[1])[0]
            if len(red_top) > 22:
                red_top = red_top[:20] + "..."

        self.kpi_centros.configure(text=f"{total_centros} Centros")
        self.kpi_total_eq.configure(text=f"{total_eq:,} Equipos")
        self.kpi_operatividad.configure(text=f"{porc_global} %")
        self.kpi_red_mayor.configure(text=red_top)

        self.filtrar_tabla_centros()

    def filtrar_tabla_centros(self):
        for i in self.tree_centros.get_children():
            self.tree_centros.delete(i)

        red_sel = self.cb_red_mapa.get()
        busq = self.e_buscar_centro.get().strip().lower()

        for c in self.centros_geo:
            if not str(red_sel).startswith("[ Todas") and c.get("red") != red_sel:
                continue
            if busq:
                match = busq in c["nombre"].lower() or busq in c["red"].lower() or busq in c["nivel"].lower()
                if not match:
                    continue

            self.tree_centros.insert("", "end", values=(
                c["nombre"],
                c["red"],
                c["nivel"],
                c["total_equipos"],
                c["operativos"],
                c["baja_falla"],
                f"{c['porcentaje_operatividad']}%",
                c["riesgo_alto"],
                f"{c['lat']:.4f}, {c['lon']:.4f}"
            ))

    def abrir_visor_mapa_navegador(self):
        """Genera el HTML del mapa con Leaflet + ESRI Satelital + Heatmap y lo abre en el navegador."""
        red_sel = self.cb_red_mapa.get()
        html_content = generar_html_mapa_gamlp(self.centros_geo, red_sel)

        try:
            temp_dir = tempfile.gettempdir()
            map_file = os.path.join(temp_dir, "mapa_satelital_gamlp.html")
            with open(map_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            webbrowser.open(f"file:///{map_file}")
        except Exception as e:
            messagebox.showerror("Error al Abrir Mapa", f"No se pudo generar el visor satelital:\n{e}")
