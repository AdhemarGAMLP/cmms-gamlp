# -*- coding: utf-8 -*-
"""
VISTA DE ASISTENTE DE INTELIGENCIA ARTIFICIAL Y DIAGNÓSTICO BIOMÉDICO (SGEM GAMLP)
==================================================================================
Subpestañas:
1. 🩺 Diagnóstico Inteligente de Fallas (Inferencia Técnica y Solución Paso a Paso)
2. 📊 Mantenimiento Predictivo & RUL (Probabilidad de Falla y Curvas de Degradación)
3. 💰 Presupuestador Predictivo de Repuestos (Demanda Semestral por Red)
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
import json
from datetime import datetime

from estilos import (
    C_BG, C_CARD, C_BORDER, C_TEXT, C_SUBTEXT, 
    C_BLUE, C_BLUE_HOVER, C_GREEN, C_RED, C_PURPLE, C_AMBER
)
from ia_biomedica import (
    diagnosticar_falla_ia, 
    calcular_riesgo_predictivo_equipo, 
    generar_pronostico_repuestos_ia,
    BASE_CONOCIMIENTO_FALLAS
)

class VistaAsistenteIA(ctk.CTkFrame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color="transparent")
        self.app = app_controller
        self.equipos_analizados = []
        self._debounce_timer = None
        
        self.construir_ui()

    def construir_ui(self):
        # Cabecera Principal
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(fill="x", padx=25, pady=(15, 10))

        lbl_tit = ctk.CTkLabel(
            f_top, 
            text="🧠 Asistente de Inteligencia Artificial & Ingeniería Clínica", 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color=C_TEXT
        )
        lbl_tit.pack(side="left")

        lbl_sub = ctk.CTkLabel(
            f_top, 
            text="⚡ Diagnóstico Experto Local | Mantenimiento Predictivo RUL | 100% Offline ($0 Costo)", 
            font=ctk.CTkFont(size=12), 
            text_color="#2563EB"
        )
        lbl_sub.pack(side="right", pady=(4, 0))

        # Tabview principal con 3 subpestañas
        self.tabview = ctk.CTkTabview(self, fg_color=C_CARD, corner_radius=12)
        self.tabview.pack(fill="both", expand=True, padx=25, pady=(5, 15))

        self.tab_diag = self.tabview.add("🩺 Diagnóstico de Fallas")
        self.tab_pred = self.tabview.add("📊 Mantenimiento Predictivo (RUL)")
        self.tab_pres = self.tabview.add("💰 Presupuestador de Repuestos")

        self.construir_tab_diagnostico()
        self.construir_tab_predictivo()
        self.construir_tab_presupuestador()

    # =========================================================================
    # SUBPESTAÑA 1: DIAGNÓSTICO INTELIGENTE DE FALLAS
    # =========================================================================
    def construir_tab_diagnostico(self):
        # Panel superior de búsqueda
        f_search_box = ctk.CTkFrame(self.tab_diag, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E2E8F0")
        f_search_box.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(
            f_search_box, 
            text="🔍 Describe el síntoma, falla o código de error del equipo biomédico:", 
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color=C_TEXT
        ).pack(anchor="w", padx=15, pady=(10, 4))

        f_in_row = ctk.CTkFrame(f_search_box, fg_color="transparent")
        f_in_row.pack(fill="x", padx=15, pady=(0, 10))

        self.e_sintoma = ctk.CTkEntry(
            f_in_row, 
            placeholder_text="Ej: 'Error de presión E01 en autoclave', 'SpO2 curva plana', 'Sillón dental fuga aire', 'Desfibrilador no carga joules'...", 
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.e_sintoma.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.e_sintoma.bind("<Return>", lambda e: self.ejecutar_diagnostico())

        # Tipos de equipo
        tipos_disponibles = ["Todos"] + [c["tipo_equipo"] for c in BASE_CONOCIMIENTO_FALLAS]
        self.cb_tipo_diag = ctk.CTkComboBox(f_in_row, values=tipos_disponibles, width=220, height=38)
        self.cb_tipo_diag.set("Todos")
        self.cb_tipo_diag.pack(side="left", padx=(0, 10))

        btn_analizar = ctk.CTkButton(
            f_in_row, 
            text="⚡ Diagnosticar con IA", 
            font=ctk.CTkFont(weight="bold", size=13),
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            height=38,
            width=160,
            command=self.ejecutar_diagnostico
        )
        btn_analizar.pack(side="left")

        # Botones de sugerencias rápidas comunes
        f_suggs = ctk.CTkFrame(self.tab_diag, fg_color="transparent")
        f_suggs.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(f_suggs, text="💡 Consultas frecuentes:", font=ctk.CTkFont(size=11, weight="bold"), text_color=C_SUBTEXT).pack(side="left", padx=(0, 8))
        
        consultas_rapidas = [
            ("Autoclave E01 / Fuga", "Fuga de vapor o error de presión en autoclave"),
            ("Monitor SpO2 / NIBP", "Monitor signos vitales sensor SpO2 desconectado o error NIBP"),
            ("Desfibrilador No Carga", "Desfibrilador no carga los Joules seleccionados"),
            ("Sillón Dental Fuga", "Sillón odontológico pérdida de potencia en turbina o fuga"),
            ("Bomba Oclusión", "Bomba de infusión alarma de oclusión o burbuja")
        ]
        for label_btn, prompt_txt in consultas_rapidas:
            ctk.CTkButton(
                f_suggs,
                text=label_btn,
                font=ctk.CTkFont(size=11),
                fg_color="#EFF6FF",
                text_color="#1D4ED8",
                hover_color="#DBEAFE",
                height=26,
                corner_radius=6,
                command=lambda p=prompt_txt: self.cargar_consulta_rapida(p)
            ).pack(side="left", padx=4)

        # Contenedor con Scroll para resultados
        self.sf_resultado_diag = ctk.CTkScrollableFrame(self.tab_diag, fg_color="transparent")
        self.sf_resultado_diag.pack(fill="both", expand=True, padx=15, pady=5)

        self.renderizar_resultado_inicial()

    def cargar_consulta_rapida(self, prompt):
        self.e_sintoma.delete(0, "end")
        self.e_sintoma.insert(0, prompt)
        self.ejecutar_diagnostico()

    def renderizar_resultado_inicial(self):
        for w in self.sf_resultado_diag.winfo_children():
            w.destroy()

        f_intro = ctk.CTkFrame(self.sf_resultado_diag, fg_color="#F8FAFC", corner_radius=12, border_width=1, border_color="#E2E8F0")
        f_intro.pack(fill="both", expand=True, pady=10, padx=5)

        ctk.CTkLabel(
            f_intro, 
            text="🩺 Motor de Diagnóstico Clínico Asistido por Inteligencia Artificial", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=C_TEXT
        ).pack(pady=(20, 8))

        txt_info = (
            "Este modulo analiza fallas biomedicas en tiempo real de forma 100% OFFLINE (sin consumir internet).\n"
            "• Identifica la causa raiz de la falla a partir de los sintomas o codigos de error.\n"
            "• Proporciona el procedimiento tecnico ordenado paso a paso para la intervencion.\n"
            "• Recomienda los repuestos exactos que deben solicitarse al almacen de repuestos del GAMLP.\n"
            "• Recuerda los estandares internacionales de seguridad electrica (IEC 62353 e IEC 60601)."
        )
        ctk.CTkLabel(
            f_intro, 
            text=txt_info, 
            font=ctk.CTkFont(size=13), 
            text_color="#475569", 
            justify="left"
        ).pack(padx=30, pady=(0, 20))

    def ejecutar_diagnostico(self):
        texto = self.e_sintoma.get().strip()
        if not texto:
            messagebox.showwarning("Consulta Vacía", "Por favor describe el síntoma o código de error del equipo.")
            return

        tipo_sel = self.cb_tipo_diag.get()
        resultado = diagnosticar_falla_ia(texto, tipo_sel)

        for w in self.sf_resultado_diag.winfo_children():
            w.destroy()

        if not resultado.get("encontrado"):
            # Diagnóstico genérico o no coincidente
            f_res = ctk.CTkFrame(self.sf_resultado_diag, fg_color="#FFFBEB", corner_radius=10, border_width=1, border_color="#FDE68A")
            f_res.pack(fill="x", pady=10, padx=5)

            ctk.CTkLabel(f_res, text="⚠️ Guía General de Verificación", font=ctk.CTkFont(size=15, weight="bold"), text_color="#B45309").pack(anchor="w", padx=15, pady=(12, 4))
            ctk.CTkLabel(f_res, text=resultado.get("mensaje", ""), font=ctk.CTkFont(size=12), text_color="#78350F", wraplength=800, justify="left").pack(anchor="w", padx=15, pady=(0, 10))

            if resultado.get("recomendacion_general"):
                for paso in resultado["recomendacion_general"]:
                    ctk.CTkLabel(f_res, text=f"• {paso}", font=ctk.CTkFont(size=12), text_color="#92400E", wraplength=800, justify="left").pack(anchor="w", padx=25, pady=2)
            return

        # ------------------ RESULTADO POSITIVO ------------------
        # Tarjeta 1: Encabezado del Diagnóstico y Nivel de Confianza
        f_card_top = ctk.CTkFrame(self.sf_resultado_diag, fg_color="#F0FDF4", corner_radius=10, border_width=1, border_color="#BBF7D0")
        f_card_top.pack(fill="x", pady=(5, 10), padx=5)

        f_tit_row = ctk.CTkFrame(f_card_top, fg_color="transparent")
        f_tit_row.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            f_tit_row, 
            text=f"🎯 Diagnóstico: {resultado['problema']}", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#15803D"
        ).pack(side="left")

        confianza = resultado.get("confianza", 85)
        badge_conf = ctk.CTkLabel(
            f_tit_row, 
            text=f"Confianza IA: {confianza}%", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            fg_color="#DCFCE7", 
            text_color="#166534", 
            corner_radius=6, 
            padx=10, 
            pady=3
        )
        badge_conf.pack(side="right")

        ctk.CTkLabel(
            f_card_top, 
            text=f"Categoría: {resultado['tipo_equipo']}", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="#166534"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Tarjeta 2: Causas Raíz Probables
        f_card_causas = ctk.CTkFrame(self.sf_resultado_diag, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E2E8F0")
        f_card_causas.pack(fill="x", pady=6, padx=5)

        ctk.CTkLabel(f_card_causas, text="🔍 Causas Raíz Probables:", font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=15, pady=(10, 6))
        for idx, causa in enumerate(resultado.get("causas", []), start=1):
            ctk.CTkLabel(f_card_causas, text=f" {idx}. {causa}", font=ctk.CTkFont(size=12), text_color="#334155", wraplength=850, justify="left").pack(anchor="w", padx=20, pady=2)
        ctk.CTkLabel(f_card_causas, text="").pack(pady=2)

        # Tarjeta 3: Procedimiento Técnico de Solución Paso a Paso
        f_card_proc = ctk.CTkFrame(self.sf_resultado_diag, fg_color="#EFF6FF", corner_radius=10, border_width=1, border_color="#BFDBFE")
        f_card_proc.pack(fill="x", pady=6, padx=5)

        ctk.CTkLabel(f_card_proc, text="🛠️ Procedimiento de Reparación y Verificación:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1E40AF").pack(anchor="w", padx=15, pady=(10, 6))
        for paso in resultado.get("procedimiento", []):
            ctk.CTkLabel(f_card_proc, text=f"  {paso}", font=ctk.CTkFont(size=12), text_color="#1E3A8A", wraplength=850, justify="left").pack(anchor="w", padx=20, pady=3)
        ctk.CTkLabel(f_card_proc, text="").pack(pady=2)

        # Tarjeta 4: Repuestos y Herramientas Necesarias (Grid de 2 columnas)
        f_grid_rep = ctk.CTkFrame(self.sf_resultado_diag, fg_color="transparent")
        f_grid_rep.pack(fill="x", pady=6, padx=5)
        f_grid_rep.grid_columnconfigure(0, weight=1)
        f_grid_rep.grid_columnconfigure(1, weight=1)

        # Columna Izq: Repuestos sugeridos
        f_col_r = ctk.CTkFrame(f_grid_rep, fg_color="#FEF2F2", corner_radius=10, border_width=1, border_color="#FECACA")
        f_col_r.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        ctk.CTkLabel(f_col_r, text="📦 Repuestos Sugeridos del Almacén:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#991B1B").pack(anchor="w", padx=12, pady=(10, 4))
        for rep in resultado.get("repuestos", []):
            ctk.CTkLabel(f_col_r, text=f"• {rep}", font=ctk.CTkFont(size=12), text_color="#7F1D1D", wraplength=400, justify="left").pack(anchor="w", padx=16, pady=2)
        ctk.CTkLabel(f_col_r, text="").pack(pady=2)

        # Columna Der: Herramientas
        f_col_h = ctk.CTkFrame(f_grid_rep, fg_color="#FAF5FF", corner_radius=10, border_width=1, border_color="#E9D5FF")
        f_col_h.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ctk.CTkLabel(f_col_h, text="🧰 Instrumentos de Medición Requeridos:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B21A8").pack(anchor="w", padx=12, pady=(10, 4))
        for her in resultado.get("herramientas", []):
            ctk.CTkLabel(f_col_h, text=f"• {her}", font=ctk.CTkFont(size=12), text_color="#581C87", wraplength=400, justify="left").pack(anchor="w", padx=16, pady=2)
        ctk.CTkLabel(f_col_h, text="").pack(pady=2)

        # Tarjeta 5: Normativa y Seguridad Eléctrica
        if resultado.get("norma_seguridad"):
            f_card_sec = ctk.CTkFrame(self.sf_resultado_diag, fg_color="#FFFBEB", corner_radius=10, border_width=1, border_color="#FDE68A")
            f_card_sec.pack(fill="x", pady=6, padx=5)
            ctk.CTkLabel(f_card_sec, text="⚡ Medida de Seguridad y Metrología (IEC 62353 / IEC 60601):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#92400E").pack(anchor="w", padx=15, pady=(8, 2))
            ctk.CTkLabel(f_card_sec, text=resultado["norma_seguridad"], font=ctk.CTkFont(size=12), text_color="#78350F", wraplength=850, justify="left").pack(anchor="w", padx=15, pady=(0, 8))

    # =========================================================================
    # SUBPESTAÑA 2: MANTENIMIENTO PREDICTIVO & RUL (REMAINING USEFUL LIFE)
    # =========================================================================
    def construir_tab_predictivo(self):
        # Barra superior con filtros y tarjetas KPI
        f_top_pred = ctk.CTkFrame(self.tab_pred, fg_color="transparent")
        f_top_pred.pack(fill="x", padx=15, pady=(10, 8))

        # KPIs Rápidos
        self.f_kpis = ctk.CTkFrame(f_top_pred, fg_color="transparent")
        self.f_kpis.pack(fill="x", pady=(0, 8))
        self.f_kpis.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_alto_riesgo = self.crear_kpi_card(self.f_kpis, 0, "🔴 Alto Riesgo de Fallo (60d)", "0 Equipos", "#FEF2F2", "#DC2626")
        self.kpi_preventivo = self.crear_kpi_card(self.f_kpis, 1, "🟡 Preventivo Requerido", "0 Equipos", "#FFFBEB", "#D97706")
        self.kpi_confiable = self.crear_kpi_card(self.f_kpis, 2, "🟢 Confiabilidad Óptima", "0 Equipos", "#F0FDF4", "#16A34A")
        self.kpi_vida_util = self.crear_kpi_card(self.f_kpis, 3, "⏳ Vida Útil Promedio (RUL)", "0.0 Años", "#EFF6FF", "#2563EB")

        # Filtros
        f_filtros = ctk.CTkFrame(self.tab_pred, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#E2E8F0")
        f_filtros.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(f_filtros, text="Filtro Red:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(10, 4), pady=6)
        self.cb_pred_red = ctk.CTkComboBox(f_filtros, values=["[ Todas las Redes ]"], width=230, height=32, command=lambda v: self.filtrar_tabla_predictiva())
        self.cb_pred_red.pack(side="left", padx=4, pady=6)

        ctk.CTkLabel(f_filtros, text="Nivel de Riesgo:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 4), pady=6)
        self.cb_pred_riesgo = ctk.CTkComboBox(f_filtros, values=["Todos", "🔴 Alto Riesgo (>75%)", "🟡 Preventivo (45-75%)", "🟢 Confiable (<45%)"], width=200, height=32, command=lambda v: self.filtrar_tabla_predictiva())
        self.cb_pred_riesgo.pack(side="left", padx=4, pady=6)

        self.e_buscar_pred = ctk.CTkEntry(f_filtros, placeholder_text="🔍 Buscar equipo o centro...", width=200, height=32)
        self.e_buscar_pred.pack(side="right", padx=10, pady=6)
        self.e_buscar_pred.bind("<KeyRelease>", self.on_buscar_pred_debounce)

        btn_recalc = ctk.CTkButton(
            f_filtros, 
            text="🔄 Recalcular IA", 
            font=ctk.CTkFont(weight="bold", size=12),
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            height=32,
            width=120,
            command=self.calcular_predictivo_completo
        )
        btn_recalc.pack(side="right", padx=5)

        # Tabla Treeview para el Parque de Equipos
        cols = ("af", "nombre", "centro", "red", "edad", "rul", "prob", "dias", "estado", "recomendacion")
        self.tree_pred = ttk.Treeview(self.tab_pred, columns=cols, show="headings", height=12)
        
        self.tree_pred.heading("af", text="Cod. AF")
        self.tree_pred.heading("nombre", text="Equipo Médico")
        self.tree_pred.heading("centro", text="Centro de Salud")
        self.tree_pred.heading("red", text="Red de Salud")
        self.tree_pred.heading("edad", text="Edad")
        self.tree_pred.heading("rul", text="RUL (Años)")
        self.tree_pred.heading("prob", text="Prob. Falla 60d")
        self.tree_pred.heading("dias", text="Est. Días Fallo")
        self.tree_pred.heading("estado", text="Estado Predictivo")
        self.tree_pred.heading("recomendacion", text="Acción Recomendada por IA")

        self.tree_pred.column("af", width=95, anchor="center")
        self.tree_pred.column("nombre", width=160, anchor="w")
        self.tree_pred.column("centro", width=140, anchor="w")
        self.tree_pred.column("red", width=110, anchor="w")
        self.tree_pred.column("edad", width=60, anchor="center")
        self.tree_pred.column("rul", width=75, anchor="center")
        self.tree_pred.column("prob", width=95, anchor="center")
        self.tree_pred.column("dias", width=85, anchor="center")
        self.tree_pred.column("estado", width=160, anchor="w")
        self.tree_pred.column("recomendacion", width=260, anchor="w")

        scroll_y = ttk.Scrollbar(self.tab_pred, orient="vertical", command=self.tree_pred.yview)
        self.tree_pred.configure(yscrollcommand=scroll_y.set)
        
        self.tree_pred.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=(0, 15))
        scroll_y.pack(side="right", fill="y", padx=(0, 15), pady=(0, 15))

    def crear_kpi_card(self, parent, col, titulo, valor_ini, bg_col, text_col):
        f = ctk.CTkFrame(parent, fg_color=bg_col, corner_radius=10, border_width=1, border_color="#E2E8F0")
        f.grid(row=0, column=col, sticky="nsew", padx=4)
        ctk.CTkLabel(f, text=titulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#475569").pack(anchor="w", padx=10, pady=(6, 2))
        lbl_v = ctk.CTkLabel(f, text=valor_ini, font=ctk.CTkFont(size=16, weight="bold"), text_color=text_col)
        lbl_v.pack(anchor="w", padx=10, pady=(0, 6))
        return lbl_v

    def on_buscar_pred_debounce(self, event=None):
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(150, self.filtrar_tabla_predictiva)

    def calcular_predictivo_completo(self):
        equipos = self.app.datos.get("equipos", [])
        historial = self.app.datos.get("historial", [])
        
        self.equipos_analizados = []
        for eq in equipos:
            res = calcular_riesgo_predictivo_equipo(eq, historial)
            if res:
                self.equipos_analizados.append(res)

        # Actualizar opciones de red
        redes_disponibles = sorted(list(set(str(e.get("red", "")).strip() for e in self.equipos_analizados if e.get("red"))))
        self.cb_pred_red.configure(values=["[ Todas las Redes ]"] + redes_disponibles)

        # Actualizar KPIs
        cant_alto = sum(1 for e in self.equipos_analizados if e["probabilidad_fallo_60d"] > 75)
        cant_prev = sum(1 for e in self.equipos_analizados if 45 < e["probabilidad_fallo_60d"] <= 75)
        cant_conf = sum(1 for e in self.equipos_analizados if e["probabilidad_fallo_60d"] <= 45)
        prom_rul = round(sum(e["rul_anios"] for e in self.equipos_analizados) / max(1, len(self.equipos_analizados)), 1)

        self.kpi_alto_riesgo.configure(text=f"{cant_alto} Equipos")
        self.kpi_preventivo.configure(text=f"{cant_prev} Equipos")
        self.kpi_confiable.configure(text=f"{cant_conf} Equipos")
        self.kpi_vida_util.configure(text=f"{prom_rul} Años")

        self.filtrar_tabla_predictiva()

    def filtrar_tabla_predictiva(self):
        for i in self.tree_pred.get_children():
            self.tree_pred.delete(i)

        red_sel = self.cb_pred_red.get()
        riesgo_sel = self.cb_pred_riesgo.get()
        busq = self.e_buscar_pred.get().strip().lower()

        for e in self.equipos_analizados:
            # Filtro Red
            if not str(red_sel).startswith("[ Todas") and e.get("red") != red_sel:
                continue
            # Filtro Riesgo
            if "Alto" in riesgo_sel and e["probabilidad_fallo_60d"] <= 75:
                continue
            elif "Preventivo" in riesgo_sel and not (45 < e["probabilidad_fallo_60d"] <= 75):
                continue
            elif "Confiable" in riesgo_sel and e["probabilidad_fallo_60d"] > 45:
                continue
            # Filtro texto
            if busq:
                match_txt = (
                    busq in str(e["equipo_id"]).lower() or
                    busq in str(e["nombre"]).lower() or
                    busq in str(e.get("centro", "")).lower() or
                    busq in str(e.get("red", "")).lower()
                )
                if not match_txt:
                    continue

            self.tree_pred.insert("", "end", values=(
                e["equipo_id"],
                e["nombre"],
                e.get("centro") or "-",
                e.get("red") or "-",
                f"{e['edad_anios']} a",
                f"{e['rul_anios']} a",
                f"{e['probabilidad_fallo_60d']}%",
                f"~{e['dias_estimados_fallo']} d",
                e["estado_predictivo"],
                e["recomendacion"]
            ))

    # =========================================================================
    # SUBPESTAÑA 3: PRESUPUESTADOR PREDICTIVO DE REPUESTOS
    # =========================================================================
    def construir_tab_presupuestador(self):
        f_top_pres = ctk.CTkFrame(self.tab_pres, fg_color="transparent")
        f_top_pres.pack(fill="x", padx=15, pady=(10, 8))

        # Tarjetas de Resumen Financiero
        self.f_kpis_pres = ctk.CTkFrame(f_top_pres, fg_color="transparent")
        self.f_kpis_pres.pack(fill="x", pady=(0, 8))
        self.f_kpis_pres.grid_columnconfigure((0, 1, 2), weight=1)

        self.kpi_pres_inversion = self.crear_kpi_card(self.f_kpis_pres, 0, "💵 Presupuesto Total Proyectado (6 Meses)", "0.00 Bs.", "#EFF6FF", "#1D4ED8")
        self.kpi_pres_criticos = self.crear_kpi_card(self.f_kpis_pres, 1, "🔴 Repuestos en Quiebre de Stock", "0 Tipos", "#FEF2F2", "#DC2626")
        self.kpi_pres_cubiertos = self.crear_kpi_card(self.f_kpis_pres, 2, "🟢 Demanda Cubierta con Stock", "0 %", "#F0FDF4", "#16A34A")

        # Barra de Filtros
        f_bar_pres = ctk.CTkFrame(self.tab_pres, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#E2E8F0")
        f_bar_pres.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(f_bar_pres, text="Proyectar para Red:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(10, 4), pady=6)
        self.cb_pres_red = ctk.CTkComboBox(f_bar_pres, values=["[ Todas las Redes ]"], width=260, height=32, command=lambda v: self.actualizar_presupuestador())
        self.cb_pres_red.pack(side="left", padx=4, pady=6)

        btn_act_pres = ctk.CTkButton(
            f_bar_pres, 
            text="📊 Recalcular Proyección", 
            font=ctk.CTkFont(weight="bold", size=12),
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            height=32,
            command=self.actualizar_presupuestador
        )
        btn_act_pres.pack(side="right", padx=10, pady=6)

        # Tabla Treeview de Presupuesto
        cols_pres = ("repuesto", "equipos", "demanda", "stock", "deficit", "costo_u", "total", "prioridad")
        self.tree_pres = ttk.Treeview(self.tab_pres, columns=cols_pres, show="headings", height=12)

        self.tree_pres.heading("repuesto", text="Repuesto Crítico / Accesorio")
        self.tree_pres.heading("equipos", text="Equipos Compatibles")
        self.tree_pres.heading("demanda", text="Demanda Semestral")
        self.tree_pres.heading("stock", text="Stock Almacén")
        self.tree_pres.heading("deficit", text="Sugerencia Compra")
        self.tree_pres.heading("costo_u", text="Costo Unit. (Bs.)")
        self.tree_pres.heading("total", text="Inversión Estimada (Bs.)")
        self.tree_pres.heading("prioridad", text="Prioridad Abastecimiento")

        self.tree_pres.column("repuesto", width=220, anchor="w")
        self.tree_pres.column("equipos", width=120, anchor="center")
        self.tree_pres.column("demanda", width=110, anchor="center")
        self.tree_pres.column("stock", width=95, anchor="center")
        self.tree_pres.column("deficit", width=115, anchor="center")
        self.tree_pres.column("costo_u", width=105, anchor="e")
        self.tree_pres.column("total", width=135, anchor="e")
        self.tree_pres.column("prioridad", width=140, anchor="center")

        scroll_y_pres = ttk.Scrollbar(self.tab_pres, orient="vertical", command=self.tree_pres.yview)
        self.tree_pres.configure(yscrollcommand=scroll_y_pres.set)

        self.tree_pres.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=(0, 15))
        scroll_y_pres.pack(side="right", fill="y", padx=(0, 15), pady=(0, 15))

    def actualizar_presupuestador(self):
        for i in self.tree_pres.get_children():
            self.tree_pres.delete(i)

        equipos = self.app.datos.get("equipos", [])
        repuestos = self.app.datos.get("repuestos", [])
        red_sel = self.cb_pres_red.get()

        pronostico = generar_pronostico_repuestos_ia(equipos, repuestos, red_sel)

        total_inversion = sum(p["costo_total_estimado"] for p in pronostico)
        cant_quiebre = sum(1 for p in pronostico if "ALTA" in p["prioridad"])
        total_items = max(1, len(pronostico))
        cubiertos = sum(1 for p in pronostico if "CUBIERTO" in p["prioridad"])
        porc_cubierto = round((cubiertos / total_items) * 100, 1)

        self.kpi_pres_inversion.configure(text=f"{total_inversion:,.2f} Bs.")
        self.kpi_pres_criticos.configure(text=f"{cant_quiebre} Repuestos")
        self.kpi_pres_cubiertos.configure(text=f"{porc_cubierto}%")

        for p in pronostico:
            self.tree_pres.insert("", "end", values=(
                p["repuesto"],
                f"{p['equipos_instalados']} equipos",
                f"{p['demanda_estimada_6m']} un.",
                f"{p['stock_disponible']} un.",
                f"{p['sugerencia_compra']} un.",
                f"{p['costo_unitario']:,.2f}",
                f"{p['costo_total_estimado']:,.2f}",
                p["prioridad"]
            ))

    def refrescar_datos(self):
        """Llamado al abrir la pestaña para cargar datos en memoria."""
        self.calcular_predictivo_completo()
        
        # Redes para el presupuestador
        redes_data = getattr(self.app, "sedes_data", {}) or {}
        redes_nombres = [r["nombre"] for r in redes_data.get("redes", [])]
        if redes_nombres:
            self.cb_pres_red.configure(values=["[ Todas las Redes ]"] + redes_nombres)
            
        self.actualizar_presupuestador()
