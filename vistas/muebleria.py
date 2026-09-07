# vistas/muebleria.py
import os
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import psycopg2.extras

from database import (
    obtener_conexion,
    guardar_mueble_db,
    eliminar_mueble_db,
    importar_muebleria_db,
    obtener_jerarquia_sedes_db,
    guardar_cache_local_datos
)
from generador_muebleria_excel import exportar_muebleria_excel, importar_muebleria_excel
from estilos import *

TIPOS_ACTIVOS_COMUNES = [
    "COMPUTADORA DE ESCRITORIO",
    "LAPTOP / PORTÁTIL",
    "IMPRESORA / MULTIFUNCIONAL",
    "MONITOR",
    "SERVIDOR",
    "SWITCH / ROUTER",
    "ESTABILIZADOR / UPS",
    "ESCRITORIO",
    "MESA DE TRABAJO",
    "SILLA EJECUTIVA / GIRATORIA",
    "SILLA TANDEM / ESPERA",
    "VITRINA MÉDICA",
    "ESTANTE METÁLICO",
    "GAVETERO / ARCHIVADOR",
    "CASILLERO / LOCKER",
    "SILLÓN DENTAL",
    "CAMILLA DE ATENCIÓN",
    "OTRO MOBILIARIO / EQUIPO"
]

SECTORES_DISPONIBLES = ["SALUD", "G.A.M.L.P.", "ADMINISTRACIÓN CENTRAL"]
DETALLES_TRANSACCION = ["ASIGNACION", "REASIGNACION", "TRANSFERENCIA", "ALTA", "BAJA", "DONACION", "EN CUSTODIA"]

class VistaMuebleria(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self._debounce_id = None
        self._sedes_data = None
        self.datos_filtrados = []
        self.construir_ui()

    def _on_busqueda_cambiada(self, *args):
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(160, self.refrescar_datos)

    def _obtener_sedes_jerarquia(self):
        if not self._sedes_data:
            self._sedes_data = obtener_jerarquia_sedes_db()
        return self._sedes_data

    def construir_ui(self):
        # 1. Cabecera con Título
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(pady=(16, 6), padx=25, fill="x")

        f_titulos = ctk.CTkFrame(f_top, fg_color="transparent")
        f_titulos.pack(side="left")

        ctk.CTkLabel(
            f_titulos, 
            text="🛋️ Mueblería, Equipos de Computación y Enseres", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color=C_TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            f_titulos, 
            text="Inventario Institucional de Activos Fijos, TI, Mobiliario y Equipamiento GAMLP", 
            font=ctk.CTkFont(size=12, slant="italic"), 
            text_color=C_SUBTEXT
        ).pack(anchor="w")

        # Badge de Sede Activa
        self.lbl_badge_sede = ctk.CTkLabel(
            f_top, 
            text="🌐 Acceso General", 
            fg_color=C_CARD, 
            corner_radius=8, 
            text_color=C_BLUE, 
            font=ctk.CTkFont(size=11, weight="bold"),
            padx=12, 
            pady=6
        )
        self.lbl_badge_sede.pack(side="right")

        # 2. Tarjetas KPI de Resumen
        self.f_kpis = ctk.CTkFrame(self, fg_color="transparent")
        self.f_kpis.pack(padx=25, pady=(4, 10), fill="x")
        self.f_kpis.columnconfigure(0, weight=1)
        self.f_kpis.columnconfigure(1, weight=1)
        self.f_kpis.columnconfigure(2, weight=1)
        self.f_kpis.columnconfigure(3, weight=1)

        self.card_total = self._crear_kpi_card(self.f_kpis, 0, "📦 Total Activos", "0", C_BLUE)
        self.card_ti = self._crear_kpi_card(self.f_kpis, 1, "💻 Computación / TI", "0", C_GREEN)
        self.card_muebles = self._crear_kpi_card(self.f_kpis, 2, "🪑 Mobiliario / Enseres", "0", C_ORANGE)
        self.card_asignados = self._crear_kpi_card(self.f_kpis, 3, "👤 Con Asignación", "0", C_PURPLE)

        # 3. Barra de Búsqueda y Filtros
        f_filtros = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        f_filtros.pack(padx=25, pady=(0, 10), fill="x")

        f_f_inner = ctk.CTkFrame(f_filtros, fg_color="transparent")
        f_f_inner.pack(padx=12, pady=10, fill="x")

        # Búsqueda rápida
        ctk.CTkLabel(f_f_inner, text="🔍", font=ctk.CTkFont(size=16)).pack(side="left", padx=(0, 4))
        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", self._on_busqueda_cambiada)
        e_buscar = ctk.CTkEntry(
            f_f_inner, 
            textvariable=self.busqueda_var, 
            placeholder_text="Buscar por SISPAM, BERTIN, SAPM, Descripción, Serie, Custodio, Ubicación, Red, Centro...", 
            width=320, 
            fg_color=C_BG, 
            border_color=C_BORDER, 
            corner_radius=8
        )
        e_buscar.pack(side="left", padx=(0, 10))

        # Filtro Sector
        ctk.CTkLabel(f_f_inner, text="Sector:", font=ctk.CTkFont(size=11, weight="bold"), text_color=C_TEXT).pack(side="left", padx=(4, 2))
        self.combo_filtro_sector = ctk.CTkComboBox(
            f_f_inner, 
            values=["[ Todos ]", "SALUD", "G.A.M.L.P.", "ADMINISTRACIÓN CENTRAL"], 
            width=130, 
            command=lambda e: self.refrescar_datos(), 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_sector.pack(side="left", padx=(0, 10))
        self.combo_filtro_sector.set("[ Todos ]")

        # Filtro Tipo de Activo
        ctk.CTkLabel(f_f_inner, text="Tipo:", font=ctk.CTkFont(size=11, weight="bold"), text_color=C_TEXT).pack(side="left", padx=(4, 2))
        self.combo_filtro_tipo = ctk.CTkComboBox(
            f_f_inner, 
            values=["[ Todos ]", "💻 Computación / TI", "🪑 Mobiliario / Enseres", "📑 Otros"], 
            width=150, 
            command=lambda e: self.refrescar_datos(), 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_tipo.pack(side="left", padx=(0, 10))
        self.combo_filtro_tipo.set("[ Todos ]")

        # Filtro Red de Salud
        ctk.CTkLabel(f_f_inner, text="Red:", font=ctk.CTkFont(size=11, weight="bold"), text_color=C_TEXT).pack(side="left", padx=(4, 2))
        sedes = self._obtener_sedes_jerarquia()
        nombres_redes = ["[ Todas las Redes ]"] + [r["nombre"] for r in sedes.get("redes", [])]
        self.combo_filtro_red = ctk.CTkComboBox(
            f_f_inner, 
            values=nombres_redes, 
            width=170, 
            command=self._al_cambiar_filtro_red, 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_red.pack(side="left", padx=(0, 10))
        self.combo_filtro_red.set("[ Todas las Redes ]")

        # Filtro Centro de Salud
        ctk.CTkLabel(f_f_inner, text="Centro:", font=ctk.CTkFont(size=11, weight="bold"), text_color=C_TEXT).pack(side="left", padx=(4, 2))
        self.combo_filtro_centro = ctk.CTkComboBox(
            f_f_inner, 
            values=["[ Todos los Centros ]"], 
            width=170, 
            command=lambda e: self.refrescar_datos(), 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_centro.pack(side="left", padx=(0, 10))
        self.combo_filtro_centro.set("[ Todos los Centros ]")

        # Botón Limpiar Filtros
        ctk.CTkButton(
            f_f_inner, 
            text="↺ Limpiar", 
            width=75, 
            height=28, 
            fg_color="#E2E8F0", 
            text_color=C_TEXT, 
            hover_color="#CBD5E1", 
            corner_radius=6, 
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.limpiar_filtros
        ).pack(side="right")

        # 4. Tabla Principal (Treeview)
        marco_tabla = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        marco_tabla.pack(padx=25, pady=(0, 10), fill="both", expand=True)

        cols = (
            "ID",
            "Sector",
            "Red de Salud",
            "Unidad / Centro",
            "Tipo Activo",
            "Descripción",
            "Modelo",
            "Serie",
            "Persona Asignada",
            "C.I. Asignado",
            "Cód. SISPAM",
            "BERTIN",
            "SAPM",
            "Ubicación",
            "Fecha Asignación"
        )

        f_tree = ctk.CTkFrame(marco_tabla, fg_color="transparent")
        f_tree.pack(pady=10, padx=10, fill="both", expand=True)

        self.tabla = ttk.Treeview(f_tree, columns=cols, show="headings", selectmode="browse")
        scroll_y = ttk.Scrollbar(f_tree, orient="vertical", command=self.tabla.yview, style="Vertical.TScrollbar")
        scroll_x = ttk.Scrollbar(f_tree, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        ancho_columnas = {
            "ID": 45,
            "Sector": 80,
            "Red de Salud": 130,
            "Unidad / Centro": 150,
            "Tipo Activo": 140,
            "Descripción": 180,
            "Modelo": 95,
            "Serie": 95,
            "Persona Asignada": 150,
            "C.I. Asignado": 90,
            "Cód. SISPAM": 95,
            "BERTIN": 85,
            "SAPM": 85,
            "Ubicación": 120,
            "Fecha Asignación": 95
        }

        for col_name in cols:
            self.tabla.heading(col_name, text=col_name)
            w = ancho_columnas.get(col_name, 100)
            align = "center" if col_name in ("ID", "Sector", "Red de Salud", "Modelo", "Serie", "C.I. Asignado", "Cód. SISPAM", "BERTIN", "SAPM", "Fecha Asignación") else "w"
            self.tabla.column(col_name, width=w, minwidth=40, anchor=align)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        f_tree.grid_rowconfigure(0, weight=1)
        f_tree.grid_columnconfigure(0, weight=1)

        self.tabla.bind("<Double-1>", lambda e: self.modificar_mueble())

        # 5. Barra Inferior de Acciones
        f_botones = ctk.CTkFrame(self, fg_color="transparent")
        f_botones.pack(pady=(0, 16), padx=25, fill="x")

        # Botón Registrar
        self.btn_agregar = ctk.CTkButton(
            f_botones, 
            text="✚ Registrar Activo", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            corner_radius=8, 
            height=38, 
            command=lambda: self.abrir_formulario_mueble()
        )
        if self.app.tiene_permiso("Muebleria", "agregar"):
            self.btn_agregar.pack(side="left", padx=(0, 8))

        # Botón Descargar Excel
        self.btn_descargar = ctk.CTkButton(
            f_botones, 
            text="📥 Descargar Excel", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color="#059669", 
            hover_color="#047857", 
            corner_radius=8, 
            height=38, 
            command=self.descargar_excel_muebleria
        )
        self.btn_descargar.pack(side="left", padx=(0, 8))

        # Botón Importar Excel
        self.btn_importar = ctk.CTkButton(
            f_botones, 
            text="📤 Importar Excel", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color="#0D9488", 
            hover_color="#0F766E", 
            corner_radius=8, 
            height=38, 
            command=self.importar_excel_muebleria
        )
        if self.app.tiene_permiso("Muebleria", "agregar"):
            self.btn_importar.pack(side="left", padx=(0, 8))

        # Botón Modificar
        self.btn_modificar = ctk.CTkButton(
            f_botones, 
            text="✎ Modificar", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_PURPLE, 
            hover_color=C_PURPLE_HOVER, 
            corner_radius=8, 
            height=38, 
            command=self.modificar_mueble
        )
        if self.app.tiene_permiso("Muebleria", "cambiar"):
            self.btn_modificar.pack(side="left", padx=(0, 8))

        # Botón Eliminar
        self.btn_eliminar = ctk.CTkButton(
            f_botones, 
            text="🗑 Eliminar", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_RED, 
            hover_color=C_RED_HOVER, 
            corner_radius=8, 
            height=38, 
            command=self.eliminar_mueble
        )
        if self.app.tiene_permiso("Muebleria", "eliminar"):
            self.btn_eliminar.pack(side="left", padx=(0, 8))

    def _crear_kpi_card(self, parent, col, titulo, valor_inicial, color_icono):
        f = ctk.CTkFrame(parent, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        f.grid(row=0, column=col, padx=5, sticky="nsew")
        ctk.CTkLabel(f, text=titulo, font=ctk.CTkFont(size=12, weight="bold"), text_color=color_icono).pack(pady=(8, 2), padx=10, anchor="w")
        lbl_v = ctk.CTkLabel(f, text=valor_inicial, font=ctk.CTkFont(size=20, weight="bold"), text_color=C_TEXT)
        lbl_v.pack(pady=(0, 8), padx=10, anchor="w")
        return lbl_v

    def _al_cambiar_filtro_red(self, red_seleccionada):
        sedes = self._obtener_sedes_jerarquia()
        if not red_seleccionada or red_seleccionada.startswith("[ Todas"):
            centros_disponibles = ["[ Todos los Centros ]"] + [c["nombre"] for c in sedes.get("centros", [])]
        else:
            red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_seleccionada), None)
            if red_obj:
                centros_disponibles = ["[ Todos los Centros ]"] + [c["nombre"] for c in sedes.get("centros", []) if c.get("red_salud_id") == red_obj["id"]]
            else:
                centros_disponibles = ["[ Todos los Centros ]"]

        self.combo_filtro_centro.configure(values=centros_disponibles)
        self.combo_filtro_centro.set("[ Todos los Centros ]")
        self.refrescar_datos()

    def limpiar_filtros(self):
        self.busqueda_var.set("")
        self.combo_filtro_sector.set("[ Todos ]")
        self.combo_filtro_tipo.set("[ Todos ]")
        self.combo_filtro_red.set("[ Todas las Redes ]")
        self._al_cambiar_filtro_red("[ Todas las Redes ]")

    def _es_tipo_computacion(self, tipo_str):
        t = str(tipo_str).upper()
        return any(k in t for k in ["COMPUTADORA", "LAPTOP", "IMPRESORA", "MONITOR", "SERVIDOR", "SWITCH", "ROUTER", "UPS", "ESTABILIZADOR", "PC", "NOTEBOOK", "SCANNER", "TECLADO", "MOUSE"])

    def _es_tipo_muebleria(self, tipo_str):
        t = str(tipo_str).upper()
        return any(k in t for k in ["SILLA", "MESA", "ESCRITORIO", "VITRINA", "ESTANTE", "GAVETERO", "ARCHIVADOR", "CASILLERO", "LOCKER", "SILLÓN", "CAMILLA", "MUEBLE", "ROPERO", "BANCO"])

    def refrescar_datos(self):
        # Actualizar badge de sede activa
        ctx = getattr(self.app, "contexto_sede", None)
        if ctx and not ctx.get("es_global", True):
            self.lbl_badge_sede.configure(text=f"📍 {ctx.get('resumen_texto', 'Sede Activa')}")
        else:
            self.lbl_badge_sede.configure(text="🌐 Acceso General GAMLP")

        todos_muebles = self.app.datos.get("muebleria", [])
        q = self.busqueda_var.get().strip().lower()
        sec_f = self.combo_filtro_sector.get()
        tipo_f = self.combo_filtro_tipo.get()
        red_f = self.combo_filtro_red.get()
        cen_f = self.combo_filtro_centro.get()

        # Filtrar por contexto de sede activa si existe
        ctx_cen_id = ctx.get("centro_salud_id") if ctx else None
        ctx_cen_nom = ctx.get("centro_salud") if ctx else None
        ctx_red_id = ctx.get("red_salud_id") if ctx else None
        ctx_red_nom = ctx.get("red_salud") if ctx else None

        filtrados = []
        c_ti = 0
        c_muebles = 0
        c_asig = 0

        for m in todos_muebles:
            if str(m.get("estado", "Activo")).lower() != "activo":
                continue

            # Contexto territorial activo
            if ctx and not ctx.get("es_global", True):
                if ctx_cen_id or (ctx_cen_nom and not str(ctx_cen_nom).startswith("[ Todos")):
                    m_cen = str(m.get("unidad_organizacional", "")).strip().lower()
                    if ctx_cen_nom and str(ctx_cen_nom).strip().lower() not in m_cen and m.get("centro_salud_id") != ctx_cen_id:
                        continue
                elif ctx_red_id or (ctx_red_nom and not str(ctx_red_nom).startswith("[ Todas")):
                    m_red = str(m.get("direccion_administrativa", "")).strip().lower()
                    if ctx_red_nom and str(ctx_red_nom).strip().lower() not in m_red and m.get("red_salud_id") != ctx_red_id:
                        continue

            # Filtro Sector
            if sec_f != "[ Todos ]" and str(m.get("sector_actual", "")).strip().upper() != sec_f.strip().upper():
                continue

            # Filtro Tipo de Activo
            t_act = str(m.get("tipo_activo", "")).strip().upper()
            if tipo_f == "💻 Computación / TI" and not self._es_tipo_computacion(t_act):
                continue
            elif tipo_f == "🪑 Mobiliario / Enseres" and not self._es_tipo_muebleria(t_act):
                continue
            elif tipo_f == "📑 Otros" and (self._es_tipo_computacion(t_act) or self._es_tipo_muebleria(t_act)):
                continue

            # Filtro Red
            if red_f != "[ Todas las Redes ]":
                m_red_txt = str(m.get("direccion_administrativa", "")).strip().upper()
                if red_f.strip().upper() not in m_red_txt:
                    continue

            # Filtro Centro
            if cen_f != "[ Todos los Centros ]":
                m_cen_txt = str(m.get("unidad_organizacional", "")).strip().upper()
                if cen_f.strip().upper() not in m_cen_txt:
                    continue

            # Filtro de búsqueda libre
            if q:
                campos_busqueda = [
                    str(m.get("codigo_sispam") or ""),
                    str(m.get("bertin") or ""),
                    str(m.get("sapm") or ""),
                    str(m.get("tipo_activo") or ""),
                    str(m.get("descripcion") or ""),
                    str(m.get("modelo") or ""),
                    str(m.get("serie") or ""),
                    str(m.get("persona_asignada") or ""),
                    str(m.get("ci_asignado") or ""),
                    str(m.get("ubicacion") or ""),
                    str(m.get("unidad_organizacional") or ""),
                    str(m.get("direccion_administrativa") or "")
                ]
                if not any(q in c.lower() for c in campos_busqueda):
                    continue

            filtrados.append(m)

            # Contadores KPI
            if self._es_tipo_computacion(t_act):
                c_ti += 1
            if self._es_tipo_muebleria(t_act):
                c_muebles += 1
            if str(m.get("persona_asignada") or "").strip():
                c_asig += 1

        self.datos_filtrados = filtrados

        # Actualizar KPIs
        self.card_total.configure(text=str(len(filtrados)))
        self.card_ti.configure(text=str(c_ti))
        self.card_muebles.configure(text=str(c_muebles))
        self.card_asignados.configure(text=str(c_asig))

        # Poblar Treeview
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for m in filtrados:
            self.tabla.insert(
                "", 
                "end", 
                iid=str(m.get("id")), 
                values=(
                    m.get("id"),
                    m.get("sector_actual") or "SALUD",
                    m.get("direccion_administrativa") or "",
                    m.get("unidad_organizacional") or "",
                    m.get("tipo_activo") or "",
                    m.get("descripcion") or "",
                    m.get("modelo") or "",
                    m.get("serie") or "",
                    m.get("persona_asignada") or "",
                    m.get("ci_asignado") or "",
                    m.get("codigo_sispam") or "",
                    m.get("bertin") or "",
                    m.get("sapm") or "",
                    m.get("ubicacion") or "",
                    m.get("fecha_asignacion") or ""
                )
            )

    def _obtener_tipos_activos_dinamicos(self):
        """Retorna la lista de tipos de activos combinando los comunes con los ya registrados en BD."""
        tipos_set = set(TIPOS_ACTIVOS_COMUNES)
        for m in self.app.datos.get("muebleria", []):
            t = str(m.get("tipo_activo") or "").strip().upper()
            if t:
                tipos_set.add(t)
        return sorted(list(tipos_set))

    def _obtener_catalogo_activos_existentes(self):
        """Retorna plantillas de activos existentes para sugerencias de autocompletado inteligente."""
        muebles = self.app.datos.get("muebleria", [])
        vistas = set()
        catalogo = []
        for m in muebles:
            tipo = str(m.get("tipo_activo") or "").strip()
            desc = str(m.get("descripcion") or "").strip()
            mod = str(m.get("modelo") or "").strip()
            sec = str(m.get("sector_actual") or "SALUD").strip()
            if not desc and not tipo:
                continue
            key = (tipo.upper(), desc.upper(), mod.upper())
            if key not in vistas:
                vistas.add(key)
                catalogo.append({
                    "tipo_activo": tipo or "COMPUTADORA DE ESCRITORIO",
                    "descripcion": desc,
                    "modelo": mod,
                    "sector_actual": sec
                })

        defaults = [
            {"tipo_activo": "COMPUTADORA DE ESCRITORIO", "descripcion": "COMPUTADORA CORE I7 16GB RAM 512GB SSD CON MONITOR Y TECLADO", "modelo": "OptiPlex 7080", "sector_actual": "SALUD"},
            {"tipo_activo": "LAPTOP / PORTÁTIL", "descripcion": "LAPTOP CORE I5 8GB RAM 256GB SSD", "modelo": "ThinkPad E14", "sector_actual": "SALUD"},
            {"tipo_activo": "IMPRESORA / MULTIFUNCIONAL", "descripcion": "IMPRESORA MULTIFUNCIONAL LÁSER MONOCROMÁTICA", "modelo": "LaserJet Pro M404", "sector_actual": "SALUD"},
            {"tipo_activo": "ESCRITORIO", "descripcion": "ESCRITORIO METÁLICO CON TAPA DE MELAMINA Y 3 GAVETAS", "modelo": "Oficina Estándar", "sector_actual": "SALUD"},
            {"tipo_activo": "SILLA EJECUTIVA / GIRATORIA", "descripcion": "SILLA GIRATORIA ERGONÓMICA CON RESPALDO DE MALLA Y APOYABRAZOS", "modelo": "Ergonómica Mesh", "sector_actual": "SALUD"},
            {"tipo_activo": "SILLA TANDEM / ESPERA", "descripcion": "TANDEM DE 3 ASIENTOS METÁLICOS PARA SALA DE ESPERA", "modelo": "Tandem 3P", "sector_actual": "SALUD"},
            {"tipo_activo": "VITRINA MÉDICA", "descripcion": "VITRINA MÉDICA DE 2 CUERPOS DE VIDRIO Y METAL", "modelo": "Clínica 2C", "sector_actual": "SALUD"},
            {"tipo_activo": "ESTANTE METÁLICO", "descripcion": "ESTANTE METÁLICO DE 5 NIVELES REFORZADO", "modelo": "5 Baldas", "sector_actual": "SALUD"},
            {"tipo_activo": "GAVETERO / ARCHIVADOR", "descripcion": "ARCHIVADOR METÁLICO DE 4 GAVETAS CON LLAVE", "modelo": "4 Gavetas", "sector_actual": "SALUD"},
            {"tipo_activo": "MESA DE TRABAJO", "descripcion": "MESA DE TRABAJO DE ESTRUCTURA TUBULAR Y MELAMINA", "modelo": "Trabajo 120x60", "sector_actual": "SALUD"},
            {"tipo_activo": "CAMILLA DE ATENCIÓN", "descripcion": "CAMILLA DE EXAMEN CLÍNICO CON COLCHONETA", "modelo": "Clínica Standard", "sector_actual": "SALUD"},
            {"tipo_activo": "SERVIDOR", "descripcion": "SERVIDOR DE DATOS EN RACK XEON 32GB RAM", "modelo": "PowerEdge R440", "sector_actual": "SALUD"}
        ]
        for d in defaults:
            key = (d["tipo_activo"].upper(), d["descripcion"].upper(), d["modelo"].upper())
            if key not in vistas:
                vistas.add(key)
                catalogo.append(d)

        return catalogo

    def abrir_formulario_mueble(self, mueble_editar=None):
        """Abre la ventana modal para registrar o modificar un mueble / equipo de computación con recomendación inteligente."""
        modal = ctk.CTkToplevel(self)
        titulo_modal = "Modificar Activo (Mueblería / Computación)" if mueble_editar else "Registrar Nuevo Activo (Mueblería / Computación)"
        modal.title(titulo_modal)
        modal.geometry("860x750")
        modal.configure(fg_color=C_BG)
        modal.transient(self)
        modal.grab_set()

        # Centrar ventana
        modal.update_idletasks()
        w, h = 860, 750
        x = (modal.winfo_screenwidth() // 2) - (w // 2)
        y = (modal.winfo_screenheight() // 2) - (h // 2)
        modal.geometry(f"{w}x{h}+{x}+{y}")

        # Cabecera Modal
        f_head = ctk.CTkFrame(modal, fg_color=C_CARD, height=60, corner_radius=0)
        f_head.pack(fill="x")
        f_head.pack_propagate(False)

        ctk.CTkLabel(
            f_head, 
            text=f"🛋️ {titulo_modal}", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=C_TEXT
        ).pack(side="left", padx=20, pady=12)

        # Contenedor Scrollable
        sf = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        sf.pack(fill="both", expand=True, padx=20, pady=10)

        sedes = self._obtener_sedes_jerarquia()
        lista_redes = [r["nombre"] for r in sedes.get("redes", [])]
        if not lista_redes:
            lista_redes = [
                "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)",
                "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)",
                "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)",
                "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)",
                "RED 5-SUR (MACRODISTRITO SUR)"
            ]

        catalogo_existentes = self._obtener_catalogo_activos_existentes()
        tipos_disponibles = self._obtener_tipos_activos_dinamicos()

        # Fila 1: Sector Actual & Detalle Transacción (Llenado Libre)
        f_r1 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r1.pack(fill="x", pady=4)
        f_r1.columnconfigure(0, weight=1)
        f_r1.columnconfigure(1, weight=1)

        # Sector Actual
        f_sec = ctk.CTkFrame(f_r1, fg_color="transparent")
        f_sec.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_sec, text="1. Sector Actual *", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_sector = ctk.CTkComboBox(f_sec, values=SECTORES_DISPONIBLES, fg_color=C_CARD, border_color=C_BORDER)
        combo_sector.pack(fill="x")
        combo_sector.set(mueble_editar.get("sector_actual", "SALUD") if mueble_editar else "SALUD")

        # Detalle Transacción (Llenado libre con sugerencias rápidas)
        f_trans = ctk.CTkFrame(f_r1, fg_color="transparent")
        f_trans.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_trans, text="2. Detalle Transacción (Llenado libre)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_trans = ctk.CTkComboBox(f_trans, values=DETALLES_TRANSACCION, fg_color=C_CARD, border_color=C_BORDER)
        combo_trans.pack(fill="x")
        combo_trans.set(mueble_editar.get("detalle_transaccion", "ASIGNACION") if mueble_editar else "ASIGNACION")

        # Fila 2: Dirección Administrativa (Red) & Unidad Organizacional (Centro)
        f_r2 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r2.pack(fill="x", pady=6)
        f_r2.columnconfigure(0, weight=1)
        f_r2.columnconfigure(1, weight=1)

        # Dirección Adm. (Red)
        f_red = ctk.CTkFrame(f_r2, fg_color="transparent")
        f_red.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_red, text="3. Dirección Administrativa (Red de Salud) *", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_red = ctk.CTkComboBox(f_red, values=lista_redes, fg_color=C_CARD, border_color=C_BORDER)
        combo_red.pack(fill="x")

        # Unidad Org. (Centro)
        f_centro = ctk.CTkFrame(f_r2, fg_color="transparent")
        f_centro.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_centro, text="4. Unidad Organizacional (Centro de Salud) *", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_centro = ctk.CTkComboBox(f_centro, values=["Seleccione Red primero..."], fg_color=C_CARD, border_color=C_BORDER)
        combo_centro.pack(fill="x")

        def actualizar_centros_por_red(red_nom, centro_sel_default=None):
            red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_nom), None)
            if red_obj:
                centros_de_red = [c["nombre"] for c in sedes.get("centros", []) if c.get("red_salud_id") == red_obj["id"]]
            else:
                centros_de_red = [c["nombre"] for c in sedes.get("centros", [])]
            if not centros_de_red:
                centros_de_red = ["CENTRO DE SALUD GAMLP"]
            combo_centro.configure(values=centros_de_red)
            if centro_sel_default and centro_sel_default in centros_de_red:
                combo_centro.set(centro_sel_default)
            elif centros_de_red:
                combo_centro.set(centros_de_red[0])

        combo_red.configure(command=lambda r: actualizar_centros_por_red(r))

        # Determinar valores por defecto de Red y Centro (respetando contexto activo o edición)
        ctx = getattr(self.app, "contexto_sede", None)
        if mueble_editar:
            red_inicial = mueble_editar.get("direccion_administrativa") or (lista_redes[0] if lista_redes else "")
            cen_inicial = mueble_editar.get("unidad_organizacional")
            combo_red.set(red_inicial)
            actualizar_centros_por_red(red_inicial, cen_inicial)
        elif ctx and not ctx.get("es_global", True):
            red_ctx = ctx.get("red_salud")
            cen_ctx = ctx.get("centro_salud")
            if red_ctx and red_ctx in lista_redes:
                combo_red.set(red_ctx)
                actualizar_centros_por_red(red_ctx, cen_ctx)
            else:
                combo_red.set(lista_redes[0] if lista_redes else "")
                actualizar_centros_por_red(combo_red.get(), cen_ctx)
        else:
            combo_red.set(lista_redes[0] if lista_redes else "")
            actualizar_centros_por_red(combo_red.get())

        # Fila 3: Tipo de Activo (Llenable Libre con Sugerencias) & Modelo
        f_r3 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r3.pack(fill="x", pady=6)
        f_r3.columnconfigure(0, weight=1)
        f_r3.columnconfigure(1, weight=1)

        f_tipo = ctk.CTkFrame(f_r3, fg_color="transparent")
        f_tipo.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_tipo, text="5. Tipo de Activo (Escribe o Selecciona) *", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        
        tipo_var = ctk.StringVar()
        combo_tipo = ctk.CTkComboBox(f_tipo, values=tipos_disponibles, variable=tipo_var, fg_color=C_CARD, border_color=C_BORDER)
        combo_tipo.pack(fill="x")
        combo_tipo.set(mueble_editar.get("tipo_activo", "COMPUTADORA DE ESCRITORIO") if mueble_editar else "COMPUTADORA DE ESCRITORIO")

        f_mod = ctk.CTkFrame(f_r3, fg_color="transparent")
        f_mod.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_mod, text="6. Modelo", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        modelo_var = ctk.StringVar()
        e_modelo = ctk.CTkEntry(f_mod, textvariable=modelo_var, placeholder_text="Ej: OptiPlex 7080, LaserJet Pro M404, Ergonómica...", fg_color=C_CARD, border_color=C_BORDER)
        e_modelo.pack(fill="x")
        if mueble_editar and mueble_editar.get("modelo"):
            e_modelo.insert(0, mueble_editar["modelo"])

        # Fila 4: Descripción del Activo & Número de Serie
        f_r4 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r4.pack(fill="x", pady=6)
        f_r4.columnconfigure(0, weight=1)
        f_r4.columnconfigure(1, weight=1)

        f_desc = ctk.CTkFrame(f_r4, fg_color="transparent")
        f_desc.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_desc, text="7. Descripción del Activo *", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        desc_var = ctk.StringVar()
        e_desc = ctk.CTkEntry(f_desc, textvariable=desc_var, placeholder_text="Ej: COMPUTADORA CORE I7 16GB RAM, ESCRITORIO DE MADERA 3 GAVETAS...", fg_color=C_CARD, border_color=C_BORDER)
        e_desc.pack(fill="x")
        if mueble_editar and mueble_editar.get("descripcion"):
            e_desc.insert(0, mueble_editar["descripcion"])

        f_ser = ctk.CTkFrame(f_r4, fg_color="transparent")
        f_ser.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_ser, text="8. Número de Serie", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_serie = ctk.CTkEntry(f_ser, placeholder_text="Ej: CN-0H754T-74261, S/N...", fg_color=C_CARD, border_color=C_BORDER)
        e_serie.pack(fill="x")
        if mueble_editar and mueble_editar.get("serie"):
            e_serie.insert(0, mueble_editar["serie"])

        # =========================================================================
        # 💡 PANEL DE RECOMENDACIÓN INTELIGENTE (AUTOCOMPLETADO DE ACTIVOS EXISTENTES)
        # =========================================================================
        f_recom = ctk.CTkFrame(sf, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#CBD5E1")
        f_recom.pack(fill="x", pady=(4, 10), padx=2)

        f_recom_head = ctk.CTkFrame(f_recom, fg_color="transparent")
        f_recom_head.pack(fill="x", padx=10, pady=(6, 2))

        lbl_recom_icon = ctk.CTkLabel(
            f_recom_head, 
            text="✨ Recomendación Inteligente:", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color=C_BLUE
        )
        lbl_recom_icon.pack(side="left")

        lbl_recom_status = ctk.CTkLabel(
            f_recom_head, 
            text="Activos existentes encontrados. Haz clic para autocompletar:", 
            font=ctk.CTkFont(size=11, slant="italic"), 
            text_color=C_SUBTEXT
        )
        lbl_recom_status.pack(side="left", padx=8)

        f_pills_container = ctk.CTkFrame(f_recom, fg_color="transparent")
        f_pills_container.pack(fill="x", padx=10, pady=(2, 8))

        def aplicar_sugerencia(sug):
            if sug.get("tipo_activo"):
                combo_tipo.set(sug["tipo_activo"])
            if sug.get("descripcion"):
                e_desc.delete(0, "end")
                e_desc.insert(0, sug["descripcion"])
            if sug.get("modelo"):
                e_modelo.delete(0, "end")
                e_modelo.insert(0, sug["modelo"])
            if sug.get("sector_actual"):
                combo_sector.set(sug["sector_actual"])
            lbl_recom_status.configure(
                text=f"✅ ¡Autocompletado con éxito ({sug.get('tipo_activo')} - {sug.get('modelo')})!",
                text_color="#16A34A"
            )

        def actualizar_recomendaciones(*args):
            # Limpiar botones previos
            for w in f_pills_container.winfo_children():
                w.destroy()

            q_tipo = combo_tipo.get().strip().lower()
            q_desc = desc_var.get().strip().lower()
            q_mod = modelo_var.get().strip().lower()

            coincidencias = []
            for item in catalogo_existentes:
                t_str = str(item.get("tipo_activo", "")).lower()
                d_str = str(item.get("descripcion", "")).lower()
                m_str = str(item.get("modelo", "")).lower()

                score = 0
                if q_tipo and q_tipo in t_str:
                    score += 3
                if q_desc and (q_desc in d_str or any(word in d_str for word in q_desc.split() if len(word) > 2)):
                    score += 4
                if q_mod and q_mod in m_str:
                    score += 3

                if score > 0 or (not q_desc and not q_mod and q_tipo and q_tipo in t_str):
                    coincidencias.append((score, item))

            coincidencias.sort(key=lambda x: x[0], reverse=True)
            top_sugerencias = [c[1] for c in coincidencias[:4]]

            if not top_sugerencias:
                # Si no hay coincidencias exactas, mostrar los primeros 3 comunes
                top_sugerencias = catalogo_existentes[:3]
                lbl_recom_status.configure(
                    text="Plantillas de activos comunes (haz clic para rellenar rápido):", 
                    text_color=C_SUBTEXT
                )
            else:
                lbl_recom_status.configure(
                    text=f"Se encontraron {len(coincidencias)} activos similares. Haz clic para autocompletar:", 
                    text_color=C_BLUE
                )

            for sug in top_sugerencias:
                t_label = f"⚡ {sug.get('tipo_activo')}: {sug.get('modelo', 'Estándar')} - {sug.get('descripcion', '')[:28]}..."
                btn_pill = ctk.CTkButton(
                    f_pills_container, 
                    text=t_label, 
                    font=ctk.CTkFont(size=11, weight="bold"), 
                    fg_color="#EFF6FF", 
                    text_color=C_BLUE, 
                    hover_color="#DBEAFE", 
                    height=28, 
                    corner_radius=6,
                    command=lambda s=sug: aplicar_sugerencia(s)
                )
                btn_pill.pack(side="left", padx=3, pady=2)

        # Escuchar cambios en campos clave para actualizar sugerencias
        tipo_var.trace_add("write", actualizar_recomendaciones)
        desc_var.trace_add("write", actualizar_recomendaciones)
        modelo_var.trace_add("write", actualizar_recomendaciones)
        actualizar_recomendaciones()

        # Fila 5: Código SISPAM & BERTIN
        f_r5 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r5.pack(fill="x", pady=6)
        f_r5.columnconfigure(0, weight=1)
        f_r5.columnconfigure(1, weight=1)

        f_sispam = ctk.CTkFrame(f_r5, fg_color="transparent")
        f_sispam.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_sispam, text="9. Código SISPAM", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_sispam = ctk.CTkEntry(f_sispam, placeholder_text="Código institucional SISPAM...", fg_color=C_CARD, border_color=C_BORDER)
        e_sispam.pack(fill="x")
        if mueble_editar and mueble_editar.get("codigo_sispam"):
            e_sispam.insert(0, mueble_editar["codigo_sispam"])

        f_bertin = ctk.CTkFrame(f_r5, fg_color="transparent")
        f_bertin.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_bertin, text="10. BERTIN", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_bertin = ctk.CTkEntry(f_bertin, placeholder_text="Código BERTIN...", fg_color=C_CARD, border_color=C_BORDER)
        e_bertin.pack(fill="x")
        if mueble_editar and mueble_editar.get("bertin"):
            e_bertin.insert(0, mueble_editar["bertin"])

        # Fila 6: SAPM & Ubicación Física
        f_r6 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r6.pack(fill="x", pady=6)
        f_r6.columnconfigure(0, weight=1)
        f_r6.columnconfigure(1, weight=1)

        f_sapm = ctk.CTkFrame(f_r6, fg_color="transparent")
        f_sapm.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_sapm, text="11. SAPM", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_sapm = ctk.CTkEntry(f_sapm, placeholder_text="Código SAPM...", fg_color=C_CARD, border_color=C_BORDER)
        e_sapm.pack(fill="x")
        if mueble_editar and mueble_editar.get("sapm"):
            e_sapm.insert(0, mueble_editar["sapm"])

        f_ubi = ctk.CTkFrame(f_r6, fg_color="transparent")
        f_ubi.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_ubi, text="12. Ubicación Física (Ambiente / Oficina / Piso)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_ubicacion = ctk.CTkEntry(f_ubi, placeholder_text="Ej: DIRECCIÓN MÉDICA, CONSULTORIO 1, FARMACIA, PISO 2...", fg_color=C_CARD, border_color=C_BORDER)
        e_ubicacion.pack(fill="x")
        if mueble_editar and mueble_editar.get("ubicacion"):
            e_ubicacion.insert(0, mueble_editar["ubicacion"])

        # Fila 7: Persona Asignada & C.I. Asignado
        f_r7 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r7.pack(fill="x", pady=6)
        f_r7.columnconfigure(0, weight=1)
        f_r7.columnconfigure(1, weight=1)

        f_pers = ctk.CTkFrame(f_r7, fg_color="transparent")
        f_pers.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_pers, text="13. Persona Asignada (Custodio Responsable)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_persona = ctk.CTkEntry(f_pers, placeholder_text="Nombre completo del personal a cargo...", fg_color=C_CARD, border_color=C_BORDER)
        e_persona.pack(fill="x")
        if mueble_editar and mueble_editar.get("persona_asignada"):
            e_persona.insert(0, mueble_editar["persona_asignada"])

        f_ci = ctk.CTkFrame(f_r7, fg_color="transparent")
        f_ci.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_ci, text="14. C.I. Asignado", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_ci = ctk.CTkEntry(f_ci, placeholder_text="Ej: 4892711 LP...", fg_color=C_CARD, border_color=C_BORDER)
        e_ci.pack(fill="x")
        if mueble_editar and mueble_editar.get("ci_asignado"):
            e_ci.insert(0, mueble_editar["ci_asignado"])

        # Fila 8: Fechas (Asignación & Incorporación)
        f_r8 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r8.pack(fill="x", pady=6)
        f_r8.columnconfigure(0, weight=1)
        f_r8.columnconfigure(1, weight=1)

        f_fasig = ctk.CTkFrame(f_r8, fg_color="transparent")
        f_fasig.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_fasig, text="15. Fecha Asignación (YYYY-MM-DD)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_fasig = ctk.CTkEntry(f_fasig, placeholder_text="YYYY-MM-DD", fg_color=C_CARD, border_color=C_BORDER)
        e_fasig.pack(fill="x")
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        e_fasig.insert(0, mueble_editar.get("fecha_asignacion", hoy_str) if mueble_editar else hoy_str)

        f_finc = ctk.CTkFrame(f_r8, fg_color="transparent")
        f_finc.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_finc, text="16. Fecha Incorporación (YYYY-MM-DD)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_finc = ctk.CTkEntry(f_finc, placeholder_text="YYYY-MM-DD", fg_color=C_CARD, border_color=C_BORDER)
        e_finc.pack(fill="x")
        if mueble_editar and mueble_editar.get("fecha_incorporacion"):
            e_finc.insert(0, mueble_editar["fecha_incorporacion"])

        # Fila 9: Técnico Inventareador (Llenado libre)
        f_r9 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r9.pack(fill="x", pady=6)

        ctk.CTkLabel(f_r9, text="17. Técnico Inventareador (Llenado libre)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_tecnico = ctk.CTkEntry(f_r9, placeholder_text="Ej: Nombre o cargo del técnico inventariador...", fg_color=C_CARD, border_color=C_BORDER)
        e_tecnico.pack(fill="x")
        if mueble_editar and mueble_editar.get("tecnico_inventareador"):
            e_tecnico.insert(0, mueble_editar["tecnico_inventareador"])

        # Fila 10: Observaciones de Asignación
        f_r10 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r10.pack(fill="x", pady=6)

        ctk.CTkLabel(f_r10, text="18. Observaciones de Asignación", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        txt_obs = ctk.CTkTextbox(f_r10, height=75, fg_color=C_CARD, border_color=C_BORDER, border_width=1)
        txt_obs.pack(fill="x")
        if mueble_editar and mueble_editar.get("observaciones_de_asignacion"):
            txt_obs.insert("1.0", mueble_editar["observaciones_de_asignacion"])

        # Botones de Acción Modal
        f_mod_bot = ctk.CTkFrame(modal, fg_color=C_CARD, height=60, corner_radius=0)
        f_mod_bot.pack(fill="x", side="bottom")
        f_mod_bot.pack_propagate(False)

        def guardar_accion():
            sec_val = combo_sector.get().strip()
            red_val = combo_red.get().strip()
            cen_val = combo_centro.get().strip()
            tipo_val = combo_tipo.get().strip()
            desc_val = e_desc.get().strip()

            if not desc_val:
                messagebox.showwarning("Campo Requerido", "Por favor ingrese la descripción del activo.", parent=modal)
                e_desc.focus_set()
                return

            # Resolver IDs de Red y Centro
            red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_val), None)
            red_id = red_obj["id"] if red_obj else None
            cen_obj = next((c for c in sedes.get("centros", []) if c["nombre"] == cen_val), None)
            cen_id = cen_obj["id"] if cen_obj else None

            datos_guardar = {
                "sector_actual": sec_val or "SALUD",
                "direccion_administrativa": red_val,
                "unidad_organizacional": cen_val,
                "fecha_asignacion": e_fasig.get().strip(),
                "tecnico_inventareador": e_tecnico.get().strip(),
                "persona_asignada": e_persona.get().strip(),
                "ci_asignado": e_ci.get().strip(),
                "tipo_activo": tipo_val or "COMPUTADORA DE ESCRITORIO",
                "descripcion": desc_val,
                "modelo": e_modelo.get().strip(),
                "serie": e_serie.get().strip(),
                "detalle_transaccion": combo_trans.get().strip() or "ASIGNACION",
                "codigo_sispam": e_sispam.get().strip(),
                "bertin": e_bertin.get().strip(),
                "sapm": e_sapm.get().strip(),
                "observaciones_de_asignacion": txt_obs.get("1.0", "end-1c").strip(),
                "ubicacion": e_ubicacion.get().strip(),
                "fecha_incorporacion": e_finc.get().strip(),
                "red_salud_id": red_id,
                "centro_salud_id": cen_id,
                "estado": "Activo"
            }

            if mueble_editar:
                datos_guardar["id"] = mueble_editar.get("id")

            exito, resp = guardar_mueble_db(datos_guardar)
            if exito:
                nuevo_id = resp
                datos_guardar["id"] = nuevo_id
                
                # Actualizar memoria local
                if "muebleria" not in self.app.datos:
                    self.app.datos["muebleria"] = []
                
                if mueble_editar:
                    for idx, item in enumerate(self.app.datos["muebleria"]):
                        if str(item.get("id")) == str(mueble_editar.get("id")):
                            self.app.datos["muebleria"][idx] = datos_guardar
                            break
                else:
                    self.app.datos["muebleria"].insert(0, datos_guardar)

                guardar_cache_local_datos(self.app.datos)
                self.refrescar_datos()
                modal.destroy()
                messagebox.showinfo("Éxito", f"Activo {'modificado' if mueble_editar else 'registrado'} correctamente.")
            else:
                messagebox.showerror("Error", f"No se pudo guardar el activo:\n{resp}", parent=modal)

        ctk.CTkButton(
            f_mod_bot, 
            text="💾 Guardar Registro", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            width=170, 
            height=38, 
            command=guardar_accion
        ).pack(side="right", padx=15, pady=10)

        ctk.CTkButton(
            f_mod_bot, 
            text="✖ Cancelar", 
            font=ctk.CTkFont(size=12), 
            fg_color="#E2E8F0", 
            text_color=C_TEXT, 
            hover_color="#CBD5E1", 
            width=100, 
            height=38, 
            command=modal.destroy
        ).pack(side="right", padx=5, pady=10)

    def modificar_mueble(self):
        if not self.app.tiene_permiso("Muebleria", "cambiar"):
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para modificar registros de muebles y computación.")
            return

        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un activo de la tabla para modificar.")
            return

        mueble_id = sel[0]
        mueble_obj = next((m for m in self.app.datos.get("muebleria", []) if str(m.get("id")) == str(mueble_id)), None)
        if not mueble_obj:
            messagebox.showerror("Error", "No se encontró el registro seleccionado.")
            return

        self.abrir_formulario_mueble(mueble_obj)

    def eliminar_mueble(self):
        if not self.app.tiene_permiso("Muebleria", "eliminar"):
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para eliminar registros de muebles y computación.")
            return

        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un activo de la tabla para eliminar.")
            return

        mueble_id = sel[0]
        mueble_obj = next((m for m in self.app.datos.get("muebleria", []) if str(m.get("id")) == str(mueble_id)), None)
        desc = mueble_obj.get("descripcion", f"ID {mueble_id}") if mueble_obj else f"ID {mueble_id}"

        confirm = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de que desea eliminar el siguiente activo?\n\n"
            f"• {desc}\n"
            f"• Tipo: {mueble_obj.get('tipo_activo', '') if mueble_obj else ''}\n"
            f"• SISPAM: {mueble_obj.get('codigo_sispam', '') if mueble_obj else ''}\n\n"
            f"El registro se moverá a la papelera con respaldo de auditoría."
        )
        if not confirm:
            return

        usuario_act = getattr(self.app, "usuario_actual", {}).get("nombre_usuario", "Sistema")
        exito, resp = eliminar_mueble_db(mueble_id, usuario=usuario_act)
        if exito:
            self.app.datos["muebleria"] = [m for m in self.app.datos.get("muebleria", []) if str(m.get("id")) != str(mueble_id)]
            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            messagebox.showinfo("Eliminado", "El activo ha sido eliminado correctamente.")
        else:
            messagebox.showerror("Error", f"No se pudo eliminar el activo:\n{resp}")

    def descargar_excel_muebleria(self):
        """Exporta la lista actual filtrada a un archivo Excel basado en la plantilla oficial."""
        if not self.datos_filtrados:
            messagebox.showwarning("Sin Datos", "No hay activos en la vista actual para exportar.")
            return

        f_def = f"Inventario_Muebleria_Computadoras_GAMLP_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        ruta_guardar = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel (*.xlsx)", "*.xlsx")],
            initialfile=f_def,
            title="Guardar Inventario de Mueblería y Computadoras"
        )
        if not ruta_guardar:
            return

        try:
            exito, msg = exportar_muebleria_excel(self.datos_filtrados, ruta_guardar)
            if exito:
                resp = messagebox.askyesno("Exportación Exitosa", f"{msg}\n\n¿Desea abrir el archivo generado ahora?")
                if resp:
                    try:
                        os.startfile(ruta_guardar)
                    except:
                        pass
            else:
                messagebox.showerror("Error de Exportación", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar archivo Excel:\n{e}")

    def importar_excel_muebleria(self):
        """Carga masiva de activos de mueblería y computadoras desde un archivo Excel."""
        if not self.app.tiene_permiso("Muebleria", "agregar"):
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para importar activos.")
            return

        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos de Excel (*.xlsx *.xls)", "*.xlsx *.xls")],
            title="Seleccionar Archivo Excel de Mueblería y Computadoras"
        )
        if not ruta:
            return

        try:
            lista_muebles, total_filas, err = importar_muebleria_excel(ruta)
            if err:
                messagebox.showerror("Error de Lectura", f"No se pudo leer el archivo Excel:\n{err}")
                return

            if not lista_muebles:
                messagebox.showwarning("Archivo Vacío", "No se encontraron filas de activos válidas en el archivo Excel seleccionado.")
                return

            confirm = messagebox.askyesno(
                "Confirmar Importación Masiva", 
                f"Se detectaron {len(lista_muebles)} registros de muebles y computadoras en el archivo.\n\n"
                f"¿Desea importarlos a la base de datos central de GAMLP?"
            )
            if not confirm:
                return

            # Si se encuentra en contexto territorial, asociar automáticamente si no vienen especificados
            ctx = getattr(self.app, "contexto_sede", None)
            sedes = self._obtener_sedes_jerarquia()

            for m in lista_muebles:
                # Intentar mapear red_salud_id y centro_salud_id por nombres
                red_txt = str(m.get("direccion_administrativa") or "").strip().upper()
                cen_txt = str(m.get("unidad_organizacional") or "").strip().upper()

                red_obj = next((r for r in sedes.get("redes", []) if r["nombre"].upper() == red_txt or r["codigo"].upper() == red_txt), None)
                if red_obj:
                    m["red_salud_id"] = red_obj["id"]
                elif ctx and not ctx.get("es_global", True):
                    m["red_salud_id"] = ctx.get("red_salud_id")

                cen_obj = next((c for c in sedes.get("centros", []) if c["nombre"].upper() == cen_txt), None)
                if cen_obj:
                    m["centro_salud_id"] = cen_obj["id"]
                elif ctx and not ctx.get("es_global", True):
                    m["centro_salud_id"] = ctx.get("centro_salud_id")

            # Insertar en BD
            insertados, msg_db = importar_muebleria_db(lista_muebles)
            if insertados > 0:
                # Recargar memoria desde PostgreSQL
                self.app.cargar_datos_memoria(usar_cache_primero=False)
                self.refrescar_datos()
                messagebox.showinfo("Importación Exitosa", f"Se importaron exitosamente {insertados} registros.")
            else:
                messagebox.showerror("Error de Importación", f"No se pudieron guardar los registros:\n{msg_db}")

        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error durante la importación:\n{e}")
