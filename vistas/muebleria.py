# vistas/muebleria.py
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
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

SECTORES_DISPONIBLES = ["SALUD", "G.A.M.L.P."]
DETALLES_TRANSACCION = ["ASIGNACION", "REASIGNACION", "TRANSFERENCIA", "ALTA", "BAJA", "DONACION", "EN CUSTODIA"]


class AutocompletarEntryPopup:
    """
    Despliega un menú emergente flotante, sutil y no obligatorio con sugerencias
    al escribir en un CTkEntry. El usuario puede seleccionar una opción o seguir
    escribiendo libremente sin ninguna imposición.
    """
    def __init__(self, ctk_entry, proveedor_datos, min_chars=1, max_items=6):
        self.entry = ctk_entry
        self.proveedor_datos = proveedor_datos
        self.min_chars = min_chars
        self.max_items = max_items
        self.popup = None
        self.listbox = None
        self._cerrando_id = None

        # Vincular eventos del campo de texto
        self.entry.bind("<KeyRelease>", self._al_escribir, add="+")
        self.entry.bind("<FocusOut>", self._al_perder_foco, add="+")
        self.entry.bind("<Down>", self._al_presionar_abajo, add="+")
        self.entry.bind("<Escape>", lambda e: self.cerrar_popup(), add="+")

    def _obtener_sugerencias(self, query):
        q = query.strip().upper()
        if not q:
            return []
        if callable(self.proveedor_datos):
            datos = self.proveedor_datos(q)
        else:
            datos = self.proveedor_datos

        starts = []
        contains = []
        for item in datos:
            item_str = str(item).strip()
            item_upper = item_str.upper()
            if not item_str:
                continue
            if item_upper == q:
                continue  # Ya es idéntico a lo que escribió
            if item_upper.startswith(q):
                if item_str not in starts:
                    starts.append(item_str)
            elif q in item_upper:
                if item_str not in contains and item_str not in starts:
                    contains.append(item_str)

        resultados = starts + contains
        return resultados[:self.max_items]

    def _al_escribir(self, event=None):
        if event and event.keysym in ("Down", "Up", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
            return

        texto = self.entry.get().strip()
        if len(texto) < self.min_chars:
            self.cerrar_popup()
            return

        sugerencias = self._obtener_sugerencias(texto)
        if not sugerencias:
            self.cerrar_popup()
            return

        self._mostrar_popup(sugerencias)

    def _al_presionar_abajo(self, event):
        if self.popup and self.listbox and self.listbox.size() > 0:
            self.listbox.focus_set()
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(0)
            self.listbox.activate(0)
            return "break"

    def _mostrar_popup(self, sugerencias):
        self.entry.update_idletasks()
        try:
            root_x = self.entry.winfo_rootx()
            root_y = self.entry.winfo_rooty()
            width = self.entry.winfo_width()
            height = self.entry.winfo_height()
        except:
            return

        if root_x <= 0 or width <= 10:
            return

        pos_y = root_y + height + 2
        alto_item = 24
        num_items = min(len(sugerencias), self.max_items)
        alto_popup = max(28, num_items * alto_item + 8)

        if not self.popup or not self.popup.winfo_exists():
            self.popup = tk.Toplevel(self.entry.winfo_toplevel())
            self.popup.wm_overrideredirect(True)
            self.popup.attributes("-topmost", True)
            self.popup.configure(bg="#94A3B8")

            f_inner = tk.Frame(self.popup, bg="#FFFFFF", padx=1, pady=1)
            f_inner.pack(fill="both", expand=True)

            self.listbox = tk.Listbox(
                f_inner,
                font=("Segoe UI", 9),
                bg="#FFFFFF",
                fg="#1E293B",
                selectbackground="#DBEAFE",
                selectforeground="#1E40AF",
                activestyle="none",
                relief="flat",
                highlightthickness=0,
                cursor="hand2"
            )
            self.listbox.pack(fill="both", expand=True, padx=2, pady=2)

            self.listbox.bind("<ButtonRelease-1>", self._al_seleccionar_click)
            self.listbox.bind("<Return>", self._al_seleccionar_tecla)
            self.listbox.bind("<Escape>", lambda e: self.cerrar_popup())
            self.listbox.bind("<FocusOut>", self._al_perder_foco_popup)
        else:
            self.popup.lift()

        self.popup.geometry(f"{width}x{alto_popup}+{root_x}+{pos_y}")

        self.listbox.delete(0, "end")
        for s in sugerencias:
            self.listbox.insert("end", f"  🔍  {s}")

    def _al_seleccionar_click(self, event=None):
        sel = self.listbox.curselection()
        if sel:
            texto_raw = self.listbox.get(sel[0]).strip()
            texto_limpio = texto_raw.replace("🔍", "").strip()
            self._aplicar_texto(texto_limpio)

    def _al_seleccionar_tecla(self, event=None):
        sel = self.listbox.curselection()
        if sel:
            texto_raw = self.listbox.get(sel[0]).strip()
            texto_limpio = texto_raw.replace("🔍", "").strip()
            self._aplicar_texto(texto_limpio)
            return "break"

    def _aplicar_texto(self, texto):
        self.entry.delete(0, "end")
        self.entry.insert(0, texto)
        self.cerrar_popup()
        self.entry.focus_set()
        try:
            self.entry._entry.icursor("end")
        except:
            pass

    def _al_perder_foco(self, event=None):
        if self._cerrando_id:
            self.entry.after_cancel(self._cerrando_id)
        self._cerrando_id = self.entry.after(200, self._verificar_y_cerrar)

    def _al_perder_foco_popup(self, event=None):
        if self._cerrando_id:
            self.entry.after_cancel(self._cerrando_id)
        self._cerrando_id = self.entry.after(200, self._verificar_y_cerrar)

    def _verificar_y_cerrar(self):
        try:
            foco = self.entry.focus_get()
            if self.popup and foco != self.listbox and foco != self.entry and foco != getattr(self.entry, "_entry", None):
                self.cerrar_popup()
        except:
            self.cerrar_popup()

    def cerrar_popup(self):
        if self.popup and self.popup.winfo_exists():
            try:
                self.popup.destroy()
            except:
                pass
        self.popup = None
        self.listbox = None


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
            text="🛋️ Activos Fijos, Mobiliario, TI y Equipos Médicos", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color=C_TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            f_titulos, 
            text="Inventario Institucional Unificado de Activos Fijos, TI, Mobiliario y Equipamiento Médico GAMLP", 
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

        # 2. Tarjetas KPI de Resumen (4 Tarjetas Unificadas)
        self.f_kpis = ctk.CTkFrame(self, fg_color="transparent")
        self.f_kpis.pack(padx=25, pady=(4, 10), fill="x")
        self.f_kpis.columnconfigure(0, weight=1)
        self.f_kpis.columnconfigure(1, weight=1)
        self.f_kpis.columnconfigure(2, weight=1)
        self.f_kpis.columnconfigure(3, weight=1)

        self.card_total = self._crear_kpi_card(self.f_kpis, 0, "📦 Total Activos", "0", C_BLUE)
        self.card_equipos = self._crear_kpi_card(self.f_kpis, 1, "🩺 Equipos Médicos", "0", C_GREEN)
        self.card_muebles = self._crear_kpi_card(self.f_kpis, 2, "🪑 Mobiliario / TI", "0", C_ORANGE)
        self.card_asignados = self._crear_kpi_card(self.f_kpis, 3, "👤 Con Asignación", "0", C_BLUE)

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
            values=["[ Todos ]", "SALUD", "G.A.M.L.P."], 
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
            values=["[ Todos los Activos ]", "🩺 Equipos Médicos", "💻 Computación / TI", "🪑 Mobiliario / Enseres", "📑 Otros"], 
            width=175, 
            command=lambda e: self.refrescar_datos(), 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_tipo.pack(side="left", padx=(0, 10))
        self.combo_filtro_tipo.set("[ Todos los Activos ]")

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
            "Marca",
            "Modelo",
            "Serie",
            "Persona Asignada",
            "C.I. Asignado",
            "Cód. SISPAM",
            "BERTIN",
            "SAPM",
            "Ubicación",
            "Estado",
            "Fecha Asignación"
        )

        f_tree = ctk.CTkFrame(marco_tabla, fg_color="transparent")
        f_tree.pack(pady=10, padx=10, fill="both", expand=True)

        self.tabla = ttk.Treeview(f_tree, columns=cols, show="headings", selectmode="browse")
        scroll_y = ctk.CTkScrollbar(f_tree, orientation="vertical", command=self.tabla.yview, width=12)
        scroll_x = ctk.CTkScrollbar(f_tree, orientation="horizontal", command=self.tabla.xview, height=12)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        ancho_columnas = {
            "ID": 45,
            "Sector": 80,
            "Red de Salud": 130,
            "Unidad / Centro": 150,
            "Tipo Activo": 140,
            "Descripción": 180,
            "Marca": 100,
            "Modelo": 95,
            "Serie": 95,
            "Persona Asignada": 150,
            "C.I. Asignado": 90,
            "Cód. SISPAM": 95,
            "BERTIN": 85,
            "SAPM": 85,
            "Ubicación": 130,
            "Estado": 85,
            "Fecha Asignación": 95
        }

        for col_name in cols:
            self.tabla.heading(col_name, text=col_name)
            w = ancho_columnas.get(col_name, 100)
            align = "center" if col_name in ("ID", "Sector", "Red de Salud", "Marca", "Modelo", "Serie", "C.I. Asignado", "Cód. SISPAM", "BERTIN", "SAPM", "Estado", "Fecha Asignación") else "w"
            self.tabla.column(col_name, width=w, minwidth=40, anchor=align)

        self.tabla.tag_configure("fila_par", background="#FFFFFF", foreground=C_TEXT)
        self.tabla.tag_configure("fila_impar", background="#F8FAFC", foreground=C_TEXT)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(4, 0))
        scroll_x.grid(row=1, column=0, sticky="ew", pady=(4, 0))

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
            text_color="#FFFFFF",
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
            fg_color=C_GREEN, 
            hover_color=C_GREEN_HOVER, 
            text_color="#FFFFFF",
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
            fg_color=C_BLUE_LIGHT, 
            hover_color="#D8E8FC", 
            text_color=C_BLUE,
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
            fg_color=C_SECONDARY_BTN, 
            hover_color=C_SECONDARY_BTN_HOVER, 
            text_color=C_TEXT,
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
            text_color="#FFFFFF",
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
        self.combo_filtro_tipo.set("[ Todos los Activos ]")
        self.combo_filtro_red.set("[ Todas las Redes ]")
        self._al_cambiar_filtro_red("[ Todas las Redes ]")

    def _es_tipo_computacion(self, tipo_str):
        t = str(tipo_str).upper()
        return any(k in t for k in ["COMPUTADORA", "LAPTOP", "IMPRESORA", "MONITOR", "SERVIDOR", "SWITCH", "ROUTER", "UPS", "ESTABILIZADOR", "PC", "NOTEBOOK", "SCANNER", "TECLADO", "MOUSE"])

    def _es_tipo_muebleria(self, tipo_str):
        t = str(tipo_str).upper()
        return any(k in t for k in ["SILLA", "MESA", "ESCRITORIO", "VITRINA", "ESTANTE", "GAVETERO", "ARCHIVADOR", "CASILLERO", "LOCKER", "SILLÓN", "CAMILLA", "MUEBLE", "ROPERO", "BANCO"])

    def _mapear_equipo_a_activo(self, eq):
        eq_id = str(eq.get("id") or "")
        return {
            "id": eq_id,
            "_iid": f"EQ_{eq_id}",
            "id_mostrar": eq_id,
            "id_original": eq_id,
            "es_equipo_medico": True,
            "sector_actual": eq.get("sector_actual") or "SALUD",
            "direccion_administrativa": eq.get("red_salud_nombre") or "",
            "unidad_organizacional": eq.get("centro_salud_nombre") or "",
            "fecha_asignacion": str(eq.get("fecha_adquisicion") or eq.get("fecha_registro") or ""),
            "tecnico_inventareador": eq.get("tecnico_responsable") or eq.get("creado_por") or "",
            "persona_asignada": eq.get("persona_asignada") or "",
            "cargo_asignado": eq.get("cargo_asignado") or "",
            "ci_asignado": eq.get("ci_asignado") or "",
            "tipo_activo": "🩺 EQUIPO MÉDICO",
            "descripcion": eq.get("nombre") or "",
            "marca": eq.get("marca") or "S/M",
            "modelo": eq.get("modelo") or "S/M",
            "serie": eq.get("numero_serie") or "S/C",
            "detalle_transaccion": eq.get("tipo_adquisicion") or "Asignacion 2026",
            "codigo_sispam": eq.get("codigo_sispam") or "S/C",
            "bertin": eq.get("bertin") or "S/C",
            "sapm": eq.get("sapm") or "S/C",
            "observaciones_de_asignacion": eq.get("observaciones") or "",
            "ubicacion": eq.get("area") or eq.get("servicio") or "General",
            "estado_conservacion": eq.get("estado") or "Operativo",
            "estado": "Activo",
            "red_salud_id": eq.get("red_salud_id"),
            "centro_salud_id": eq.get("centro_salud_id")
        }

    def refrescar_datos(self):
        # Actualizar badge de sede activa
        ctx = getattr(self.app, "contexto_sede", None)
        if ctx and not ctx.get("es_global", True):
            self.lbl_badge_sede.configure(text=f"📍 {ctx.get('resumen_texto', 'Sede Activa')}")
        else:
            self.lbl_badge_sede.configure(text="🌐 Acceso General GAMLP")

        # 1. Cargar Muebles y TI
        todos_muebles = []
        for m in self.app.datos.get("muebleria", []):
            item_m = dict(m)
            item_m["es_equipo_medico"] = False
            item_m["_iid"] = f"M_{item_m.get('id')}"
            item_m["id_mostrar"] = str(item_m.get("id"))
            todos_muebles.append(item_m)

        # 2. Cargar y Unificar Equipos Médicos del Inventario
        todos_equipos = self.app.datos.get("equipos", [])
        equipos_mapeados = []
        for eq in todos_equipos:
            est = str(eq.get("estado") or "").strip().lower()
            if est in ("baja", "eliminado", "inactivo"):
                continue
            equipos_mapeados.append(self._mapear_equipo_a_activo(eq))

        todos_activos = todos_muebles + equipos_mapeados
        self._todos_activos_unificados = todos_activos

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
        c_equipos = 0
        c_muebles = 0
        c_asig = 0

        for m in todos_activos:
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
            es_eq = m.get("es_equipo_medico", False)
            t_act = str(m.get("tipo_activo", "")).strip().upper()

            if tipo_f == "🩺 Equipos Médicos":
                if not es_eq:
                    continue
            elif tipo_f == "💻 Computación / TI":
                if es_eq or not self._es_tipo_computacion(t_act):
                    continue
            elif tipo_f == "🪑 Mobiliario / Enseres":
                if es_eq or not self._es_tipo_muebleria(t_act):
                    continue
            elif tipo_f == "📑 Otros":
                if es_eq or self._es_tipo_computacion(t_act) or self._es_tipo_muebleria(t_act):
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
                    str(m.get("id") or ""),
                    str(m.get("codigo_sispam") or ""),
                    str(m.get("bertin") or ""),
                    str(m.get("sapm") or ""),
                    str(m.get("tipo_activo") or ""),
                    str(m.get("descripcion") or ""),
                    str(m.get("marca") or ""),
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
            if es_eq:
                c_equipos += 1
            else:
                c_muebles += 1

            if str(m.get("persona_asignada") or "").strip():
                c_asig += 1

        self.datos_filtrados = filtrados

        # Actualizar 4 KPIs
        self.card_total.configure(text=str(len(filtrados)))
        self.card_equipos.configure(text=str(c_equipos))
        self.card_muebles.configure(text=str(c_muebles))
        self.card_asignados.configure(text=str(c_asig))

        # Poblar Treeview
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for idx, m in enumerate(filtrados):
            tag_fila = "fila_par" if idx % 2 == 0 else "fila_impar"
            self.tabla.insert(
                "", 
                "end", 
                iid=str(m.get("_iid", m.get("id"))), 
                values=(
                    m.get("id_mostrar") or m.get("id"),
                    m.get("sector_actual") or "SALUD",
                    m.get("direccion_administrativa") or "",
                    m.get("unidad_organizacional") or "",
                    m.get("tipo_activo") or "",
                    m.get("descripcion") or "",
                    m.get("marca") or "",
                    m.get("modelo") or "",
                    m.get("serie") or "S/C",
                    m.get("persona_asignada") or "",
                    m.get("ci_asignado") or "",
                    m.get("codigo_sispam") or "S/C",
                    m.get("bertin") or "S/C",
                    m.get("sapm") or "S/C",
                    m.get("ubicacion") or "",
                    m.get("estado_conservacion") or m.get("estado_bien") or "Bueno",
                    m.get("fecha_asignacion") or ""
                ),
                tags=(tag_fila,)
            )

    def _obtener_lista_tipos(self, query=""):
        tipos_set = set(TIPOS_ACTIVOS_COMUNES)
        for m in self.app.datos.get("muebleria", []):
            t = str(m.get("tipo_activo") or "").strip()
            if t:
                tipos_set.add(t)
        return sorted(list(tipos_set))

    def _obtener_lista_marcas(self, query=""):
        marcas_set = {
            "DELL", "HP", "LENOVO", "EPSON", "CANON", "SAMSUNG", "LG", "SONY",
            "SONOSCAPE", "MINDRAY", "PHILIPS", "GENERAL ELECTRIC", "SIEMENS",
            "BILMEX", "METALMEDICA", "GENÉRICO", "S/M"
        }
        for m in self.app.datos.get("muebleria", []):
            mar = str(m.get("marca") or "").strip()
            if mar:
                marcas_set.add(mar)
        return sorted(list(marcas_set))

    def _obtener_lista_modelos(self, query=""):
        modelos_set = {
            "OptiPlex 7080", "OptiPlex 3050", "ThinkPad E14", "ThinkCentre",
            "LaserJet Pro M404", "LaserJet MFP M428", "EcoTank L3150",
            "Ergonómica Mesh", "Oficina Estándar", "Tandem 3P", "Clínica 2C",
            "5 Baldas", "4 Gavetas", "PowerEdge R440", "Smart-UPS 1500"
        }
        for m in self.app.datos.get("muebleria", []):
            mod = str(m.get("modelo") or "").strip()
            if mod:
                modelos_set.add(mod)
        return sorted(list(modelos_set))

    def _obtener_lista_descripciones(self, query=""):
        desc_set = {
            "COMPUTADORA CORE I7 16GB RAM 512GB SSD CON MONITOR Y TECLADO",
            "COMPUTADORA CORE I5 8GB RAM 1TB HDD CON MONITOR",
            "LAPTOP CORE I5 8GB RAM 256GB SSD",
            "IMPRESORA MULTIFUNCIONAL LÁSER MONOCROMÁTICA",
            "ESCRITORIO METÁLICO CON TAPA DE MELAMINA Y 3 GAVETAS",
            "SILLA GIRATORIA ERGONÓMICA CON RESPALDO DE MALLA Y APOYABRAZOS",
            "SILLA TANDEM DE 3 ASIENTOS METÁLICOS PARA SALA DE ESPERA",
            "VITRINA MÉDICA DE 2 CUERPOS DE VIDRIO Y METAL",
            "ESTANTE METÁLICO DE 5 NIVELES REFORZADO",
            "ARCHIVADOR METÁLICO DE 4 GAVETAS CON LLAVE",
            "MESA DE TRABAJO DE ESTRUCTURA TUBULAR Y MELAMINA",
            "CAMILLA DE EXAMEN CLÍNICO CON COLCHONETA",
            "SERVIDOR DE DATOS EN RACK XEON 32GB RAM"
        }
        for m in self.app.datos.get("muebleria", []):
            d = str(m.get("descripcion") or "").strip()
            if d:
                desc_set.add(d)
        return sorted(list(desc_set))

    def _obtener_lista_series(self, query=""):
        series_set = {"S/C", "SIN SERIE", "SIN CODIGO"}
        for m in self.app.datos.get("muebleria", []):
            ser = str(m.get("serie") or "").strip()
            if ser and ser.upper() not in ("-", "0"):
                series_set.add(ser)
        return sorted(list(series_set))

    def _obtener_lista_sispam(self, query=""):
        sispam_set = {"S/C", "0", "DONACION", "SIN CODIGO"}
        for m in self.app.datos.get("muebleria", []):
            s = str(m.get("codigo_sispam") or "").strip()
            if s and s not in ("-",):
                sispam_set.add(s)
        return sorted(list(sispam_set))

    def _obtener_lista_bertin(self, query=""):
        bertin_set = {"S/C", "0", "SIN CODIGO"}
        for m in self.app.datos.get("muebleria", []):
            b = str(m.get("bertin") or "").strip()
            if b and b not in ("-",):
                bertin_set.add(b)
        return sorted(list(bertin_set))

    def _obtener_lista_sapm(self, query=""):
        sapm_set = {"S/C", "0", "SIN CODIGO"}
        for m in self.app.datos.get("muebleria", []):
            sp = str(m.get("sapm") or "").strip()
            if sp and sp not in ("-",):
                sapm_set.add(sp)
        return sorted(list(sapm_set))

    def _formatear_area_nombre(self, a):
        nom = str(a.get("nombre") or "").strip()
        piso = str(a.get("piso") or "").strip()
        if not piso or piso == "-":
            return nom
        if not piso.lower().startswith("piso") and not piso.lower().startswith("planta") and not piso.lower().startswith("pb"):
            piso_str = f"Piso {piso}"
        else:
            piso_str = piso
        return f"{piso_str} - {nom}"

    def abrir_formulario_mueble(self, mueble_editar=None):
        """Abre la ventana modal para registrar o modificar un activo."""
        modal = ctk.CTkToplevel(self)
        titulo_modal = "Modificar Activo" if mueble_editar else "Registrar Nuevo Activo"
        modal.title(titulo_modal)
        modal.geometry("880x760")
        modal.configure(fg_color=C_BG)
        modal.transient(self)
        modal.grab_set()

        # Centrar ventana
        modal.update_idletasks()
        w, h = 880, 760
        x = (modal.winfo_screenwidth() // 2) - (w // 2)
        y = (modal.winfo_screenheight() // 2) - (h // 2)
        modal.geometry(f"{w}x{h}+{x}+{y}")

        # Cabecera Modal
        f_head = ctk.CTkFrame(modal, fg_color=C_CARD, height=60, corner_radius=0)
        f_head.pack(fill="x")
        f_head.pack_propagate(False)

        ctk.CTkLabel(
            f_head, 
            text=f"📦 {titulo_modal}", 
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

        # -------------------------------------------------------------
        # FILA 1: Dirección Administrativa (Red) & Unidad Organizacional (Centro)
        # -------------------------------------------------------------
        f_r1 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r1.pack(fill="x", pady=6)
        f_r1.columnconfigure(0, weight=1)
        f_r1.columnconfigure(1, weight=1)

        # Dirección Adm. (Red)
        f_red = ctk.CTkFrame(f_r1, fg_color="transparent")
        f_red.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_red, text="Dirección Administrativa (Red de Salud)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_red = ctk.CTkComboBox(f_red, values=lista_redes, fg_color=C_CARD, border_color=C_BORDER)
        combo_red.pack(fill="x")

        # Unidad Org. (Centro)
        f_centro = ctk.CTkFrame(f_r1, fg_color="transparent")
        f_centro.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_centro, text="Unidad Organizacional (Centro de Salud)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_centro = ctk.CTkComboBox(f_centro, values=["Seleccione Red primero..."], fg_color=C_CARD, border_color=C_BORDER)
        combo_centro.pack(fill="x")

        # -------------------------------------------------------------
        # FILA 2: Ubicación Física (Piso - Área) & Sector Actual
        # -------------------------------------------------------------
        f_r2 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r2.pack(fill="x", pady=6)
        f_r2.columnconfigure(0, weight=1)
        f_r2.columnconfigure(1, weight=1)

        # Ubicación física vinculada a Áreas (Piso - Área)
        f_ubi = ctk.CTkFrame(f_r2, fg_color="transparent")
        f_ubi.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_ubi, text="Ubicación Física (Piso - Área)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_ubicacion = ctk.CTkComboBox(f_ubi, values=["Cargando áreas..."], fg_color=C_CARD, border_color=C_BORDER)
        combo_ubicacion.pack(fill="x")

        # Sector Actual
        f_sec = ctk.CTkFrame(f_r2, fg_color="transparent")
        f_sec.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_sec, text="Sector Actual", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_sector = ctk.CTkComboBox(f_sec, values=SECTORES_DISPONIBLES, fg_color=C_CARD, border_color=C_BORDER)
        combo_sector.pack(fill="x")
        combo_sector.set(mueble_editar.get("sector_actual", "SALUD") if mueble_editar else "SALUD")

        # -------------------------------------------------------------
        # FILA 3: Persona Asignada & C.I. Asignado (Auto-llenado por Área, editable)
        # -------------------------------------------------------------
        f_r3 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r3.pack(fill="x", pady=6)
        f_r3.columnconfigure(0, weight=1)
        f_r3.columnconfigure(1, weight=1)

        f_pers = ctk.CTkFrame(f_r3, fg_color="transparent")
        f_pers.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_pers, text="Persona Asignada (Doctora / Custodio)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_persona = ctk.CTkEntry(f_pers, placeholder_text="Nombre de la doctora o responsable a cargo...", fg_color=C_CARD, border_color=C_BORDER)
        e_persona.pack(fill="x")

        f_ci = ctk.CTkFrame(f_r3, fg_color="transparent")
        f_ci.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_ci, text="C.I. Asignado", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_ci = ctk.CTkEntry(f_ci, placeholder_text="Ej: 4892711 LP...", fg_color=C_CARD, border_color=C_BORDER)
        e_ci.pack(fill="x")

        # -------------------------------------------------------------
        # VINCULACIÓN DINÁMICA: RED -> CENTRO -> UBICACIÓN (ÁREA) -> DOCTOR & CI
        # -------------------------------------------------------------
        mapa_areas_actuales = {}

        def al_cambiar_ubicacion(val_ubi=None):
            sel = (val_ubi or combo_ubicacion.get()).strip()
            area_obj = mapa_areas_actuales.get(sel)
            if not area_obj:
                sel_low = sel.lower()
                for k, v in mapa_areas_actuales.items():
                    if k.lower() == sel_low or str(v.get("nombre", "")).lower() == sel_low:
                        area_obj = v
                        break
            if area_obj:
                enc = str(area_obj.get("encargado") or "").strip()
                ci_enc = str(area_obj.get("ci_encargado") or "").strip()
                if enc:
                    e_persona.delete(0, "end")
                    e_persona.insert(0, enc)
                if ci_enc:
                    e_ci.delete(0, "end")
                    e_ci.insert(0, ci_enc)

        def actualizar_ubicaciones_por_centro(centro_nom, red_nom=None, ubi_sel_default=None, auto_llenar_doctor=True):
            mapa_areas_actuales.clear()
            areas_db = self.app.datos.get("areas", [])
            
            areas_centro = []
            if centro_nom:
                cen_nom_clean = str(centro_nom).strip().upper()
                areas_centro = [
                    a for a in areas_db 
                    if str(a.get("centro_salud_nombre") or "").strip().upper() == cen_nom_clean
                ]
            
            if not areas_centro:
                areas_centro = [
                    a for a in areas_db 
                    if not str(a.get("centro_salud_nombre") or "").strip() or str(a.get("centro_salud_nombre") or "").strip() == "-"
                ]
            if not areas_centro:
                areas_centro = areas_db

            lista_areas_fmt = []
            for a in areas_centro:
                fmt = self._formatear_area_nombre(a)
                mapa_areas_actuales[fmt] = a
                mapa_areas_actuales[str(a.get("nombre", ""))] = a
                if fmt not in lista_areas_fmt:
                    lista_areas_fmt.append(fmt)

            if not lista_areas_fmt:
                lista_areas_fmt = ["Piso 1 - Consulta Externa", "PB - Emergencias", "Piso 1 - Ecografía"]

            combo_ubicacion.configure(values=lista_areas_fmt)

            if ubi_sel_default and (ubi_sel_default in lista_areas_fmt or ubi_sel_default in mapa_areas_actuales):
                combo_ubicacion.set(ubi_sel_default)
                if auto_llenar_doctor:
                    al_cambiar_ubicacion(ubi_sel_default)
            elif ubi_sel_default:
                combo_ubicacion.set(ubi_sel_default)
            elif lista_areas_fmt:
                combo_ubicacion.set(lista_areas_fmt[0])
                if auto_llenar_doctor:
                    al_cambiar_ubicacion(lista_areas_fmt[0])

        def actualizar_centros_por_red(red_nom, centro_sel_default=None, ubi_sel_default=None, auto_llenar_doctor=True):
            red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_nom), None)
            if red_obj:
                centros_de_red = [c["nombre"] for c in sedes.get("centros", []) if c.get("red_salud_id") == red_obj["id"]]
            else:
                centros_de_red = [c["nombre"] for c in sedes.get("centros", [])]
            if "RED 1" in (red_nom or "").upper() and "167 AUXILIO" not in centros_de_red:
                centros_de_red.append("167 AUXILIO")
            if not centros_de_red:
                centros_de_red = ["CENTRO DE SALUD GAMLP"]

            combo_centro.configure(values=centros_de_red)
            if centro_sel_default and centro_sel_default in centros_de_red:
                cen_sel = centro_sel_default
            elif centros_de_red:
                cen_sel = centros_de_red[0]
            else:
                cen_sel = ""
            combo_centro.set(cen_sel)

            actualizar_ubicaciones_por_centro(cen_sel, red_nom, ubi_sel_default=ubi_sel_default, auto_llenar_doctor=auto_llenar_doctor)

        combo_red.configure(command=lambda r: actualizar_centros_por_red(r, auto_llenar_doctor=True))
        combo_centro.configure(command=lambda c: actualizar_ubicaciones_por_centro(c, combo_red.get(), auto_llenar_doctor=True))
        combo_ubicacion.configure(command=al_cambiar_ubicacion)

        # -------------------------------------------------------------
        # FILA 4: Tipo de Activo & Marca
        # -------------------------------------------------------------
        f_r4 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r4.pack(fill="x", pady=6)
        f_r4.columnconfigure(0, weight=1)
        f_r4.columnconfigure(1, weight=1)

        f_tipo = ctk.CTkFrame(f_r4, fg_color="transparent")
        f_tipo.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_tipo, text="Tipo de Activo", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_tipo = ctk.CTkEntry(f_tipo, placeholder_text="Ej: COMPUTADORA DE ESCRITORIO, SILLA, ESCRITORIO...", fg_color=C_CARD, border_color=C_BORDER)
        e_tipo.pack(fill="x")
        if mueble_editar and mueble_editar.get("tipo_activo"):
            e_tipo.insert(0, mueble_editar["tipo_activo"])
        pop_tipo = AutocompletarEntryPopup(e_tipo, self._obtener_lista_tipos)

        f_mar = ctk.CTkFrame(f_r4, fg_color="transparent")
        f_mar.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_mar, text="Marca", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_marca = ctk.CTkEntry(f_mar, placeholder_text="Ej: Dell, HP, Lenovo, SonoScape, Bilmex...", fg_color=C_CARD, border_color=C_BORDER)
        e_marca.pack(fill="x")
        if mueble_editar and mueble_editar.get("marca"):
            e_marca.insert(0, mueble_editar["marca"])
        pop_mar = AutocompletarEntryPopup(e_marca, self._obtener_lista_marcas)

        # -------------------------------------------------------------
        # FILA 5: Modelo & Número de Serie (Único)
        # -------------------------------------------------------------
        f_r5 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r5.pack(fill="x", pady=6)
        f_r5.columnconfigure(0, weight=1)
        f_r5.columnconfigure(1, weight=1)

        f_mod = ctk.CTkFrame(f_r5, fg_color="transparent")
        f_mod.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_mod, text="Modelo", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_modelo = ctk.CTkEntry(f_mod, placeholder_text="Ej: OptiPlex 7080, LaserJet Pro M404, Ergonómica...", fg_color=C_CARD, border_color=C_BORDER)
        e_modelo.pack(fill="x")
        if mueble_editar and mueble_editar.get("modelo"):
            e_modelo.insert(0, mueble_editar["modelo"])
        pop_mod = AutocompletarEntryPopup(e_modelo, self._obtener_lista_modelos)

        f_ser = ctk.CTkFrame(f_r5, fg_color="transparent")
        f_ser.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_ser, text="Número de Serie (Por defecto S/C)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_serie = ctk.CTkEntry(f_ser, placeholder_text="S/C", fg_color=C_CARD, border_color=C_BORDER)
        e_serie.pack(fill="x")
        ser_val = mueble_editar.get("serie") if mueble_editar else ""
        if ser_val and ser_val != "S/C":
            e_serie.insert(0, ser_val)
        pop_ser = AutocompletarEntryPopup(e_serie, self._obtener_lista_series)

        # -------------------------------------------------------------
        # FILA 6: Código SISPAM & BERTIN
        # -------------------------------------------------------------
        f_r6 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r6.pack(fill="x", pady=6)
        f_r6.columnconfigure(0, weight=1)
        f_r6.columnconfigure(1, weight=1)

        f_sispam = ctk.CTkFrame(f_r6, fg_color="transparent")
        f_sispam.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_sispam, text="Código SISPAM (Por defecto S/C o DONACION)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_sispam = ctk.CTkEntry(f_sispam, placeholder_text="S/C", fg_color=C_CARD, border_color=C_BORDER)
        e_sispam.pack(fill="x")
        sis_val = mueble_editar.get("codigo_sispam") if mueble_editar else ""
        if sis_val and sis_val != "S/C":
            e_sispam.insert(0, sis_val)
        pop_sis = AutocompletarEntryPopup(e_sispam, self._obtener_lista_sispam)

        f_bertin = ctk.CTkFrame(f_r6, fg_color="transparent")
        f_bertin.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_bertin, text="BERTIN (Por defecto S/C)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_bertin = ctk.CTkEntry(f_bertin, placeholder_text="S/C", fg_color=C_CARD, border_color=C_BORDER)
        e_bertin.pack(fill="x")
        ber_val = mueble_editar.get("bertin") if mueble_editar else ""
        if ber_val and ber_val != "S/C":
            e_bertin.insert(0, ber_val)
        pop_ber = AutocompletarEntryPopup(e_bertin, self._obtener_lista_bertin)

        # -------------------------------------------------------------
        # FILA 7: SAPM & Detalle Transacción
        # -------------------------------------------------------------
        f_r7 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r7.pack(fill="x", pady=6)
        f_r7.columnconfigure(0, weight=1)
        f_r7.columnconfigure(1, weight=1)

        f_sapm = ctk.CTkFrame(f_r7, fg_color="transparent")
        f_sapm.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_sapm, text="SAPM (Por defecto S/C)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_sapm = ctk.CTkEntry(f_sapm, placeholder_text="S/C", fg_color=C_CARD, border_color=C_BORDER)
        e_sapm.pack(fill="x")
        sap_val = mueble_editar.get("sapm") if mueble_editar else ""
        if sap_val and sap_val != "S/C":
            e_sapm.insert(0, sap_val)
        pop_sap = AutocompletarEntryPopup(e_sapm, self._obtener_lista_sapm)

        f_trans = ctk.CTkFrame(f_r7, fg_color="transparent")
        f_trans.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_trans, text="Detalle Transacción (Llenado libre)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_trans = ctk.CTkEntry(f_trans, placeholder_text="Ej: Asignacion 2026, REASIGNACION...", fg_color=C_CARD, border_color=C_BORDER)
        e_trans.pack(fill="x")
        trans_def = mueble_editar.get("detalle_transaccion") if mueble_editar else "Asignacion 2026"
        e_trans.insert(0, trans_def or "Asignacion 2026")

        # -------------------------------------------------------------
        # FILA 8: Estado de Conservación (Bueno, Regular, Baja) & Fecha Asignación
        # -------------------------------------------------------------
        f_r8 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r8.pack(fill="x", pady=6)
        f_r8.columnconfigure(0, weight=1)
        f_r8.columnconfigure(1, weight=1)

        f_est = ctk.CTkFrame(f_r8, fg_color="transparent")
        f_est.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_est, text="Estado de Conservación", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        combo_estado = ctk.CTkComboBox(f_est, values=["Bueno", "Regular", "Baja"], fg_color=C_CARD, border_color=C_BORDER)
        combo_estado.pack(fill="x")
        combo_estado.set(mueble_editar.get("estado_conservacion", "Bueno") if mueble_editar else "Bueno")

        f_fasig = ctk.CTkFrame(f_r8, fg_color="transparent")
        f_fasig.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(f_fasig, text="Fecha Asignación (YYYY-MM-DD)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_fasig = ctk.CTkEntry(f_fasig, placeholder_text="YYYY-MM-DD", fg_color=C_CARD, border_color=C_BORDER)
        e_fasig.pack(fill="x")
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        e_fasig.insert(0, mueble_editar.get("fecha_asignacion", hoy_str) if mueble_editar else hoy_str)

        # -------------------------------------------------------------
        # FILA 9: Descripción del Activo
        # -------------------------------------------------------------
        f_r9 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r9.pack(fill="x", pady=6)

        ctk.CTkLabel(f_r9, text="Descripción del Activo", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_desc = ctk.CTkEntry(f_r9, placeholder_text="Ej: COMPUTADORA CORE I7 16GB RAM, ESCRITORIO DE MADERA 3 GAVETAS...", fg_color=C_CARD, border_color=C_BORDER)
        e_desc.pack(fill="x")
        if mueble_editar and mueble_editar.get("descripcion"):
            e_desc.insert(0, mueble_editar["descripcion"])
        pop_desc = AutocompletarEntryPopup(e_desc, self._obtener_lista_descripciones)

        # -------------------------------------------------------------
        # FILA 10: Técnico Inventariador (Auto-completado con Usuario en Sesión)
        # -------------------------------------------------------------
        f_r10 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r10.pack(fill="x", pady=6)

        ctk.CTkLabel(f_r10, text="Técnico Inventariador (Llenado automático)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        e_tecnico = ctk.CTkEntry(f_r10, placeholder_text="Nombre del técnico inventariador...", fg_color=C_CARD, border_color=C_BORDER)
        e_tecnico.pack(fill="x")
        usuario_act = getattr(self.app, "usuario_actual", {}) or {}
        tecnico_default = usuario_act.get("nombre_completo") or usuario_act.get("nombre_usuario", "")
        if mueble_editar and mueble_editar.get("tecnico_inventareador"):
            e_tecnico.insert(0, mueble_editar["tecnico_inventareador"])
        else:
            e_tecnico.insert(0, tecnico_default)

        # -------------------------------------------------------------
        # FILA 11: Observaciones de Asignación
        # -------------------------------------------------------------
        f_r11 = ctk.CTkFrame(sf, fg_color="transparent")
        f_r11.pack(fill="x", pady=6)

        ctk.CTkLabel(f_r11, text="Observaciones de Asignación", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w", pady=(0, 2))
        txt_obs = ctk.CTkTextbox(f_r11, height=75, fg_color=C_CARD, border_color=C_BORDER, border_width=1)
        txt_obs.pack(fill="x")
        if mueble_editar and mueble_editar.get("observaciones_de_asignacion"):
            txt_obs.insert("1.0", mueble_editar["observaciones_de_asignacion"])

        # Inicializar selección territorial / edición
        ctx = getattr(self.app, "contexto_sede", None)
        if mueble_editar:
            red_inicial = mueble_editar.get("direccion_administrativa") or (lista_redes[0] if lista_redes else "")
            cen_inicial = mueble_editar.get("unidad_organizacional")
            ubi_inicial = mueble_editar.get("ubicacion")
            combo_red.set(red_inicial)
            actualizar_centros_por_red(red_inicial, centro_sel_default=cen_inicial, ubi_sel_default=ubi_inicial, auto_llenar_doctor=False)
            if mueble_editar.get("persona_asignada"):
                e_persona.delete(0, "end")
                e_persona.insert(0, mueble_editar["persona_asignada"])
            if mueble_editar.get("ci_asignado"):
                e_ci.delete(0, "end")
                e_ci.insert(0, mueble_editar["ci_asignado"])
        elif ctx and not ctx.get("es_global", True):
            red_ctx = ctx.get("red_salud")
            cen_ctx = ctx.get("centro_salud")
            if red_ctx and red_ctx in lista_redes:
                combo_red.set(red_ctx)
                actualizar_centros_por_red(red_ctx, centro_sel_default=cen_ctx, auto_llenar_doctor=True)
            else:
                combo_red.set(lista_redes[0] if lista_redes else "")
                actualizar_centros_por_red(combo_red.get(), centro_sel_default=cen_ctx, auto_llenar_doctor=True)
        else:
            combo_red.set(lista_redes[0] if lista_redes else "")
            actualizar_centros_por_red(combo_red.get(), auto_llenar_doctor=True)

        # Cerrar popups si se hace scroll o cierra modal
        def cerrar_todos_popups(e=None):
            pop_tipo.cerrar_popup()
            pop_mar.cerrar_popup()
            pop_mod.cerrar_popup()
            pop_desc.cerrar_popup()
            pop_ser.cerrar_popup()
            pop_sis.cerrar_popup()
            pop_ber.cerrar_popup()
            pop_sap.cerrar_popup()

        sf.bind("<MouseWheel>", cerrar_todos_popups)

        def al_cerrar_modal():
            cerrar_todos_popups()
            modal.destroy()

        modal.protocol("WM_DELETE_WINDOW", al_cerrar_modal)

        # Botones de Acción Modal
        f_mod_bot = ctk.CTkFrame(modal, fg_color=C_CARD, height=60, corner_radius=0)
        f_mod_bot.pack(fill="x", side="bottom")
        f_mod_bot.pack_propagate(False)

        def guardar_accion():
            sec_val = combo_sector.get().strip()
            red_val = combo_red.get().strip()
            cen_val = combo_centro.get().strip()
            tipo_val = e_tipo.get().strip()
            marca_val = e_marca.get().strip()
            desc_val = e_desc.get().strip()

            if not tipo_val:
                messagebox.showwarning("Campo Requerido", "Por favor ingrese el tipo de activo.", parent=modal)
                e_tipo.focus_set()
                return

            if not desc_val:
                messagebox.showwarning("Campo Requerido", "Por favor ingrese la descripción del activo.", parent=modal)
                e_desc.focus_set()
                return

            # Valores de Códigos y Serie con valor por defecto S/C
            serie_val = e_serie.get().strip() or "S/C"
            sispam_val = e_sispam.get().strip() or "S/C"
            bertin_val = e_bertin.get().strip() or "S/C"
            sapm_val = e_sapm.get().strip() or "S/C"
            trans_val = e_trans.get().strip() or "Asignacion 2026"
            ubi_val = combo_ubicacion.get().strip()
            estado_val = combo_estado.get().strip() or "Bueno"

            # -------------------------------------------------------------
            # VALIDACIÓN DE NO DUPLICADOS (SERIE, SISPAM, BERTIN, SAPM)
            # Excepciones permitidas que pueden repetirse: S/C, 0, DONACION, SIN CODIGO, etc.
            # -------------------------------------------------------------
            EXENTOS_DUPLICADOS = {"", "S/C", "0", "DONACION", "SIN CODIGO", "SIN SERIE", "NINGUNO", "N/A", "NO APLICA", "S/N", "SN", "-"}
            id_actual = str(mueble_editar.get("id")) if mueble_editar else None

            for m in self.app.datos.get("muebleria", []):
                if id_actual and str(m.get("id")) == id_actual:
                    continue
                if str(m.get("estado", "Activo")).lower() != "activo":
                    continue

                # 1. Validar Serie
                m_serie = str(m.get("serie") or "").strip()
                if serie_val.upper() not in EXENTOS_DUPLICADOS and m_serie.upper() not in EXENTOS_DUPLICADOS:
                    if serie_val.upper() == m_serie.upper():
                        messagebox.showerror(
                            "Número de Serie Duplicado",
                            f"El Número de Serie '{serie_val}' ya se encuentra registrado en el activo:\n\n"
                            f"• ID: {m.get('id')}\n"
                            f"• Descripción: {m.get('descripcion')}\n"
                            f"• Ubicación: {m.get('ubicacion')}\n\n"
                            f"No se permite registrar activos con el mismo número de serie.",
                            parent=modal
                        )
                        e_serie.focus_set()
                        return

                # 2. Validar SISPAM
                m_sispam = str(m.get("codigo_sispam") or "").strip()
                if sispam_val.upper() not in EXENTOS_DUPLICADOS and m_sispam.upper() not in EXENTOS_DUPLICADOS:
                    if sispam_val.upper() == m_sispam.upper():
                        messagebox.showerror(
                            "Código SISPAM Duplicado",
                            f"El Código SISPAM '{sispam_val}' ya se encuentra registrado en el activo:\n\n"
                            f"• ID: {m.get('id')}\n"
                            f"• Descripción: {m.get('descripcion')}\n"
                            f"• Ubicación: {m.get('ubicacion')}\n\n"
                            f"No se permite registrar códigos SISPAM duplicados.",
                            parent=modal
                        )
                        e_sispam.focus_set()
                        return

                # 3. Validar BERTIN
                m_bertin = str(m.get("bertin") or "").strip()
                if bertin_val.upper() not in EXENTOS_DUPLICADOS and m_bertin.upper() not in EXENTOS_DUPLICADOS:
                    if bertin_val.upper() == m_bertin.upper():
                        messagebox.showerror(
                            "Código BERTIN Duplicado",
                            f"El Código BERTIN '{bertin_val}' ya se encuentra registrado en el activo:\n\n"
                            f"• ID: {m.get('id')}\n"
                            f"• Descripción: {m.get('descripcion')}\n"
                            f"• Ubicación: {m.get('ubicacion')}\n\n"
                            f"No se permite registrar códigos BERTIN duplicados.",
                            parent=modal
                        )
                        e_bertin.focus_set()
                        return

                # 4. Validar SAPM
                m_sapm = str(m.get("sapm") or "").strip()
                if sapm_val.upper() not in EXENTOS_DUPLICADOS and m_sapm.upper() not in EXENTOS_DUPLICADOS:
                    if sapm_val.upper() == m_sapm.upper():
                        messagebox.showerror(
                            "Código SAPM Duplicado",
                            f"El Código SAPM '{sapm_val}' ya se encuentra registrado en el activo:\n\n"
                            f"• ID: {m.get('id')}\n"
                            f"• Descripción: {m.get('descripcion')}\n"
                            f"• Ubicación: {m.get('ubicacion')}\n\n"
                            f"No se permite registrar códigos SAPM duplicados.",
                            parent=modal
                        )
                        e_sapm.focus_set()
                        return

            cerrar_todos_popups()

            # Resolver IDs de Red y Centro
            red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_val), None)
            red_id = red_obj["id"] if red_obj else None
            cen_obj = next((c for c in sedes.get("centros", []) if c["nombre"] == cen_val), None)
            cen_id = cen_obj["id"] if cen_obj else None

            datos_guardar = {
                "sector_actual": sec_val or "SALUD",
                "direccion_administrativa": red_val,
                "unidad_organizacional": cen_val,
                "fecha_asignacion": e_fasig.get().strip() or hoy_str,
                "tecnico_inventareador": e_tecnico.get().strip(),
                "persona_asignada": e_persona.get().strip(),
                "ci_asignado": e_ci.get().strip(),
                "tipo_activo": tipo_val,
                "descripcion": desc_val,
                "marca": marca_val,
                "modelo": e_modelo.get().strip(),
                "serie": serie_val,
                "detalle_transaccion": trans_val,
                "codigo_sispam": sispam_val,
                "bertin": bertin_val,
                "sapm": sapm_val,
                "observaciones_de_asignacion": txt_obs.get("1.0", "end-1c").strip(),
                "ubicacion": ubi_val,
                "fecha_incorporacion": "",
                "red_salud_id": red_id,
                "centro_salud_id": cen_id,
                "estado_conservacion": estado_val,
                "estado": "Activo"
            }

            if mueble_editar:
                datos_guardar["id"] = mueble_editar.get("id")

            exito, resp = guardar_mueble_db(datos_guardar)
            es_offline = False
            if not exito:
                # Si falló por falta de conexión a Internet, guardar en cola offline
                from database import guardar_mueble_offline_cola
                import time
                if not datos_guardar.get("id"):
                    datos_guardar["id"] = -int(time.time() * 1000) % 1000000000
                guardar_mueble_offline_cola(dict(datos_guardar))
                exito = True
                es_offline = True
                resp = datos_guardar["id"]

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
                msg_txt = f"Activo {'modificado' if mueble_editar else 'registrado'} correctamente."
                if es_offline:
                    msg_txt += "\n(Guardado localmente en modo Offline. Se sincronizará automáticamente al conectar)."
                messagebox.showinfo("Éxito", msg_txt)
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
            command=al_cerrar_modal
        ).pack(side="right", padx=5, pady=10)

    def modificar_mueble(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un activo de la tabla para modificar.")
            return

        sel_iid = sel[0]
        activo_obj = next((m for m in getattr(self, "datos_filtrados", []) if str(m.get("_iid", m.get("id"))) == str(sel_iid) or str(m.get("id")) == str(sel_iid)), None)
        if not activo_obj:
            activo_obj = next((m for m in self.app.datos.get("muebleria", []) if str(m.get("id")) == str(sel_iid)), None)
            if not activo_obj:
                messagebox.showerror("Error", "No se encontró el registro seleccionado.")
                return

        if activo_obj.get("es_equipo_medico"):
            if not self.app.tiene_permiso("Inventario", "cambiar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para modificar fichas técnicas de equipos médicos.")
                return
            eq_orig_id = activo_obj.get("id_original") or activo_obj.get("id")
            eq = next((e for e in self.app.datos.get("equipos", []) if str(e.get("id")) == str(eq_orig_id)), None)
            if eq and hasattr(self.app, "abrir_formulario_equipo"):
                self.app.abrir_formulario_equipo(eq)
            elif eq:
                messagebox.showinfo("Ficha de Equipo Médico", f"• Nombre: {eq.get('nombre')}\n• ID: {eq.get('id')}\n• Marca: {eq.get('marca')}\n• Modelo: {eq.get('modelo')}\n• Serie: {eq.get('numero_serie')}\n• SISPAM: {eq.get('codigo_sispam')}\n• Ubicación: {eq.get('area') or eq.get('servicio')}")
            else:
                messagebox.showerror("Error", f"No se encontró el equipo médico con ID {eq_orig_id}.")
            return

        if not self.app.tiene_permiso("Muebleria", "cambiar"):
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para modificar registros de muebles y computación.")
            return

        self.abrir_formulario_mueble(activo_obj)

    def eliminar_mueble(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un activo de la tabla para eliminar.")
            return

        sel_iid = sel[0]
        activo_obj = next((m for m in getattr(self, "datos_filtrados", []) if str(m.get("_iid", m.get("id"))) == str(sel_iid) or str(m.get("id")) == str(sel_iid)), None)
        if not activo_obj:
            activo_obj = next((m for m in self.app.datos.get("muebleria", []) if str(m.get("id")) == str(sel_iid)), None)
            if not activo_obj:
                messagebox.showerror("Error", "No se encontró el registro seleccionado.")
                return

        if activo_obj.get("es_equipo_medico"):
            if not self.app.tiene_permiso("Inventario", "eliminar"):
                messagebox.showwarning("Acceso Denegado", "No tiene permisos para dar de baja o eliminar equipos médicos.")
                return

            eq_id = activo_obj.get("id_original") or activo_obj.get("id")
            eq_nombre = activo_obj.get("descripcion", "")
            confirm = messagebox.askyesno(
                "Confirmar Baja de Equipo Médico",
                f"¿Está seguro de trasladar a la papelera el siguiente equipo médico?\n\n"
                f"• ID: {eq_id}\n"
                f"• Equipo: {eq_nombre}\n"
                f"• Serie: {activo_obj.get('serie', 'S/C')}\n"
                f"• Centro: {activo_obj.get('unidad_organizacional', '')}\n\n"
                f"El registro se trasladará a la papelera de reciclaje.",
                parent=self
            )
            if not confirm:
                return

            try:
                conn = obtener_conexion()
                if not conn:
                    messagebox.showerror("Error", "No se pudo conectar a la base de datos para eliminar el equipo.")
                    return
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM equipos WHERE id = %s", (eq_id,))
                fila = cur.fetchone()
                if fila:
                    from database import mover_a_papelera
                    usuario_act = getattr(self.app, "usuario_actual", {}).get("nombre_usuario", "Sistema")
                    mover_a_papelera(cur, "equipos", eq_id, dict(fila), usuario_act)
                cur.execute("DELETE FROM equipos WHERE id = %s", (eq_id,))
                conn.commit()
                cur.close()
                conn.close()
                self.app.cargar_datos_memoria()
                self.refrescar_datos()
                messagebox.showinfo("Éxito", "El equipo médico fue trasladado a la papelera correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el equipo médico:\n{e}")
            return

        if not self.app.tiene_permiso("Muebleria", "eliminar"):
            messagebox.showwarning("Acceso Denegado", "No tiene permisos para eliminar registros de muebles y computación.")
            return

        mueble_id = activo_obj.get("id")
        desc = activo_obj.get("descripcion", f"ID {mueble_id}")
        confirm = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de que desea eliminar el siguiente activo?\n\n"
            f"• {desc}\n"
            f"• Tipo: {activo_obj.get('tipo_activo', '')}\n"
            f"• SISPAM: {activo_obj.get('codigo_sispam', '')}\n\n"
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
        """Exporta la lista actual (muebles, computadoras y equipos médicos) a un archivo Excel basado en la plantilla oficial."""
        if not self.datos_filtrados:
            messagebox.showwarning("Sin Datos", "No hay activos en la vista actual para exportar.")
            return

        items_a_exportar = self.datos_filtrados
        total_global = len(getattr(self, "_todos_activos_unificados", []))
        if total_global > len(self.datos_filtrados):
            resp_filtro = messagebox.askyesnocancel(
                "Exportar Inventario a Excel",
                f"Tiene filtros activos: se muestran {len(self.datos_filtrados)} registros de un total de {total_global} activos.\n\n"
                f"• Presione SÍ para exportar TODOS los activos ({total_global} activos incluyendo muebles, TI y equipos médicos).\n"
                f"• Presione NO para exportar únicamente los registros FILTRADOS ({len(self.datos_filtrados)} activos).\n"
                f"• Presione CANCELAR para salir."
            )
            if resp_filtro is None:
                return
            elif resp_filtro is True:
                items_a_exportar = self._todos_activos_unificados

        f_def = f"Inventario_Activos_GAMLP_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        ruta_guardar = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel (*.xlsx)", "*.xlsx")],
            initialfile=f_def,
            title="Guardar Inventario Unificado de Activos GAMLP"
        )
        if not ruta_guardar:
            return

        try:
            exito, msg = exportar_muebleria_excel(items_a_exportar, ruta_guardar)
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
