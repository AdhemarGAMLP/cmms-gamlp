# vistas/sedes.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import psycopg2.extras
from database import (
    obtener_conexion, 
    obtener_jerarquia_sedes_db, 
    invalidar_cache_jerarquia,
    guardar_centro_salud_db, 
    eliminar_centro_salud_db,
    guardar_red_salud_db, 
    eliminar_red_salud_db,
    guardar_municipio_db,
    guardar_departamento_db,
    ejecutar_en_segundo_plano
)
from estilos import *

class VistaSedes(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.jerarquia = {"departamentos": [], "municipios": [], "redes": [], "centros": []}
        
        self.filtro_red_var = ctk.StringVar(value="Todas las Redes")
        self.busqueda_centro_var = ctk.StringVar()
        self.busqueda_red_var = ctk.StringVar()
        
        self.construir_ui()

    def construir_ui(self):
        # Cabecera
        f_cab = ctk.CTkFrame(self, fg_color="transparent")
        f_cab.pack(pady=(20, 10), padx=30, fill="x")
        
        ctk.CTkLabel(
            f_cab, 
            text="Estructura Territorial y Sedes de Salud", 
            font=ctk.CTkFont(size=26, weight="bold"), 
            text_color=C_TEXT
        ).pack(side="left")

        # Tabview principal
        self.tabview = ctk.CTkTabview(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        self.tabview.pack(padx=25, pady=(5, 20), fill="both", expand=True)

        self.tab_centros = self.tabview.add("🏥 Centros de Salud")
        self.tab_redes = self.tabview.add("🌐 Redes de Salud")
        self.tab_mun_dep = self.tabview.add("🗺️ Municipios y Departamentos")

        self.construir_tab_centros()
        self.construir_tab_redes()
        self.construir_tab_municipios_deptos()

    # ========================================================
    # TAB 1: CENTROS DE SALUD / HOSPITALES
    # ========================================================
    def construir_tab_centros(self):
        # Barra superior de filtros
        f_bar = ctk.CTkFrame(self.tab_centros, fg_color="transparent")
        f_bar.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(f_bar, text="Filtrar por Red:", font=ctk.CTkFont(weight="bold", size=13), text_color=C_TEXT).pack(side="left", padx=(0, 6))
        self.combo_filtro_red = ctk.CTkComboBox(
            f_bar, 
            values=["Todas las Redes"], 
            variable=self.filtro_red_var, 
            command=lambda e: self.poblar_tabla_centros(),
            width=220, 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_red.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(f_bar, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 4))
        e_busq = ctk.CTkEntry(
            f_bar, 
            textvariable=self.busqueda_centro_var, 
            placeholder_text="Buscar centro, nivel, ubicación, contacto...", 
            width=280, 
            fg_color=C_BG, 
            border_color=C_BORDER,
            corner_radius=8
        )
        e_busq.pack(side="left")
        self.busqueda_centro_var.trace_add("write", lambda *args: self.poblar_tabla_centros())

        # Contenedor de Tabla
        f_tab_box = ctk.CTkFrame(self.tab_centros, fg_color="transparent")
        f_tab_box.pack(fill="both", expand=True, padx=16, pady=8)

        cols = ("ID", "Red de Salud", "Centro de Salud / Hospital", "Nivel", "Ubicación / Dirección", "Teléfono", "Responsable", "Estado")
        self.tabla_centros = ttk.Treeview(f_tab_box, columns=cols, show="headings", selectmode="browse")
        sb = ttk.Scrollbar(f_tab_box, orient="vertical", command=self.tabla_centros.yview, style="Vertical.TScrollbar")
        self.tabla_centros.configure(yscrollcommand=sb.set)

        col_w = {
            "ID": 45, 
            "Red de Salud": 130, 
            "Centro de Salud / Hospital": 200, 
            "Nivel": 110, 
            "Ubicación / Dirección": 200, 
            "Teléfono": 100, 
            "Responsable": 140, 
            "Estado": 75
        }
        for c in cols:
            self.tabla_centros.heading(c, text=c)
            self.tabla_centros.column(c, anchor="center" if c in ["ID", "Nivel", "Teléfono", "Estado"] else "w", width=col_w.get(c, 100))

        self.tabla_centros.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y", padx=(4, 0))
        self.tabla_centros.bind("<Double-1>", lambda e: self.abrir_formulario_centro(editar=True))

        # Barra inferior de botones de acción
        f_bot = ctk.CTkFrame(self.tab_centros, fg_color="transparent")
        f_bot.pack(fill="x", padx=16, pady=(8, 14))

        ctk.CTkButton(
            f_bot, 
            text="✚ Añadir Centro de Salud", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            corner_radius=10, 
            height=38, 
            command=lambda: self.abrir_formulario_centro(editar=False)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_bot, 
            text="✎ Modificar Centro", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_PURPLE, 
            hover_color=C_PURPLE_HOVER, 
            corner_radius=10, 
            height=38, 
            command=lambda: self.abrir_formulario_centro(editar=True)
        ).pack(side="left", padx=(0, 10))

        self.btn_elim_centro = ctk.CTkButton(
            f_bot, 
            text="🗑 Eliminar / Desactivar", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_RED, 
            hover_color=C_RED_HOVER, 
            corner_radius=10, 
            height=38, 
            command=self.eliminar_centro_click
        )
        self.btn_elim_centro.pack(side="left")

    # ========================================================
    # TAB 2: REDES DE SALUD
    # ========================================================
    def construir_tab_redes(self):
        f_bar = ctk.CTkFrame(self.tab_redes, fg_color="transparent")
        f_bar.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(f_bar, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 4))
        e_busq = ctk.CTkEntry(
            f_bar, 
            textvariable=self.busqueda_red_var, 
            placeholder_text="Buscar red, código, macrodistrito, responsable...", 
            width=320, 
            fg_color=C_BG, 
            border_color=C_BORDER,
            corner_radius=8
        )
        e_busq.pack(side="left")
        self.busqueda_red_var.trace_add("write", lambda *args: self.poblar_tabla_redes())

        f_tab_box = ctk.CTkFrame(self.tab_redes, fg_color="transparent")
        f_tab_box.pack(fill="both", expand=True, padx=16, pady=8)

        cols = ("ID", "Código", "Nombre de Red", "Macrodistrito", "Municipio", "Responsable", "Teléfono", "Estado")
        self.tabla_redes = ttk.Treeview(f_tab_box, columns=cols, show="headings", selectmode="browse")
        sb = ttk.Scrollbar(f_tab_box, orient="vertical", command=self.tabla_redes.yview, style="Vertical.TScrollbar")
        self.tabla_redes.configure(yscrollcommand=sb.set)

        col_w = {
            "ID": 45, 
            "Código": 90, 
            "Nombre de Red": 240, 
            "Macrodistrito": 150, 
            "Municipio": 100, 
            "Responsable": 140, 
            "Teléfono": 100, 
            "Estado": 75
        }
        for c in cols:
            self.tabla_redes.heading(c, text=c)
            self.tabla_redes.column(c, anchor="center" if c in ["ID", "Código", "Teléfono", "Estado"] else "w", width=col_w.get(c, 100))

        self.tabla_redes.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y", padx=(4, 0))
        self.tabla_redes.bind("<Double-1>", lambda e: self.abrir_formulario_red(editar=True))

        f_bot = ctk.CTkFrame(self.tab_redes, fg_color="transparent")
        f_bot.pack(fill="x", padx=16, pady=(8, 14))

        ctk.CTkButton(
            f_bot, 
            text="✚ Añadir Red de Salud", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            corner_radius=10, 
            height=38, 
            command=lambda: self.abrir_formulario_red(editar=False)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_bot, 
            text="✎ Modificar Red", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_PURPLE, 
            hover_color=C_PURPLE_HOVER, 
            corner_radius=10, 
            height=38, 
            command=lambda: self.abrir_formulario_red(editar=True)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_bot, 
            text="🗑 Desactivar Red", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_RED, 
            hover_color=C_RED_HOVER, 
            corner_radius=10, 
            height=38, 
            command=self.eliminar_red_click
        ).pack(side="left")

    # ========================================================
    # TAB 3: MUNICIPIOS Y DEPARTAMENTOS
    # ========================================================
    def construir_tab_municipios_deptos(self):
        f_split = ctk.CTkFrame(self.tab_mun_dep, fg_color="transparent")
        f_split.pack(fill="both", expand=True, padx=16, pady=12)
        f_split.columnconfigure(0, weight=1)
        f_split.columnconfigure(1, weight=1)

        # Lado Izquierdo: Municipios
        f_left = ctk.CTkFrame(f_split, fg_color="#F8FAFC", corner_radius=14, border_width=1, border_color=C_BORDER)
        f_left.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="nsew")

        ctk.CTkLabel(f_left, text="🏢 Municipios / Gobiernos Autónomos", font=ctk.CTkFont(size=16, weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=14, pady=(12, 6))
        
        cols_m = ("ID", "Municipio", "Código", "Departamento", "Estado")
        self.tabla_mun = ttk.Treeview(f_left, columns=cols_m, show="headings", selectmode="browse", height=8)
        for c in cols_m:
            self.tabla_mun.heading(c, text=c)
            self.tabla_mun.column(c, anchor="center" if c in ["ID", "Código", "Estado"] else "w", width=70 if c in ["ID", "Código", "Estado"] else 120)
        self.tabla_mun.pack(fill="both", expand=True, padx=12, pady=6)

        f_bot_m = ctk.CTkFrame(f_left, fg_color="transparent")
        f_bot_m.pack(fill="x", padx=12, pady=(4, 12))
        ctk.CTkButton(f_bot_m, text="✚ Añadir Municipio", font=ctk.CTkFont(weight="bold", size=12), fg_color=C_BLUE, height=32, corner_radius=8, command=lambda: self.abrir_formulario_municipio(editar=False)).pack(side="left", padx=(0, 6))
        ctk.CTkButton(f_bot_m, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=12), fg_color=C_PURPLE, height=32, corner_radius=8, command=lambda: self.abrir_formulario_municipio(editar=True)).pack(side="left")

        # Lado Derecho: Departamentos
        f_right = ctk.CTkFrame(f_split, fg_color="#F8FAFC", corner_radius=14, border_width=1, border_color=C_BORDER)
        f_right.grid(row=0, column=1, padx=(8, 0), pady=0, sticky="nsew")

        ctk.CTkLabel(f_right, text="🗺️ Departamentos de Bolivia", font=ctk.CTkFont(size=16, weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=14, pady=(12, 6))

        cols_d = ("ID", "Departamento", "Código", "Estado")
        self.tabla_dep = ttk.Treeview(f_right, columns=cols_d, show="headings", selectmode="browse", height=8)
        for c in cols_d:
            self.tabla_dep.heading(c, text=c)
            self.tabla_dep.column(c, anchor="center" if c in ["ID", "Código", "Estado"] else "w", width=70 if c in ["ID", "Código", "Estado"] else 140)
        self.tabla_dep.pack(fill="both", expand=True, padx=12, pady=6)

        f_bot_d = ctk.CTkFrame(f_right, fg_color="transparent")
        f_bot_d.pack(fill="x", padx=12, pady=(4, 12))
        ctk.CTkButton(f_bot_d, text="✚ Añadir Departamento", font=ctk.CTkFont(weight="bold", size=12), fg_color=C_BLUE, height=32, corner_radius=8, command=lambda: self.abrir_formulario_departamento(editar=False)).pack(side="left", padx=(0, 6))
        ctk.CTkButton(f_bot_d, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=12), fg_color=C_PURPLE, height=32, corner_radius=8, command=lambda: self.abrir_formulario_departamento(editar=True)).pack(side="left")

    # ========================================================
    # POBLAR DATOS
    # ========================================================
    def refrescar_datos(self):
        self.jerarquia = obtener_jerarquia_sedes_db(forzar_recarga=True)
        
        # Actualizar opciones del combo de Redes
        nombres_redes = ["Todas las Redes"] + [r["nombre"] for r in self.jerarquia.get("redes", [])]
        self.combo_filtro_red.configure(values=nombres_redes)
        if self.filtro_red_var.get() not in nombres_redes:
            self.filtro_red_var.set("Todas las Redes")

        self.poblar_tabla_centros()
        self.poblar_tabla_redes()
        self.poblar_tabla_municipios()
        self.poblar_tabla_departamentos()

    def poblar_tabla_centros(self):
        for item in self.tabla_centros.get_children():
            self.tabla_centros.delete(item)

        redes_dict = {r["id"]: r["nombre"] for r in self.jerarquia.get("redes", [])}
        filtro_red = self.filtro_red_var.get().strip()
        filtro_txt = self.busqueda_centro_var.get().lower().strip()

        for c in self.jerarquia.get("centros", []):
            r_nom = redes_dict.get(c.get("red_salud_id"), "Sin Red")
            if filtro_red != "Todas las Redes" and r_nom.lower() != filtro_red.lower():
                continue

            c_id = str(c.get("id", ""))
            c_nom = str(c.get("nombre", ""))
            c_niv = str(c.get("nivel") or "Primer Nivel")
            c_dir = str(c.get("direccion") or "-")
            c_tel = str(c.get("telefono") or "-")
            c_res = str(c.get("responsable") or "-")
            c_est = str(c.get("estado") or "Activo")

            if filtro_txt:
                match = (filtro_txt in c_nom.lower() or 
                         filtro_txt in r_nom.lower() or 
                         filtro_txt in c_niv.lower() or 
                         filtro_txt in c_dir.lower() or 
                         filtro_txt in c_res.lower() or
                         filtro_txt in c_tel.lower())
                if not match:
                    continue

            self.tabla_centros.insert("", "end", values=(c_id, r_nom, c_nom, c_niv, c_dir, c_tel, c_res, c_est))

    def poblar_tabla_redes(self):
        for item in self.tabla_redes.get_children():
            self.tabla_redes.delete(item)

        muns_dict = {m["id"]: m["nombre"] for m in self.jerarquia.get("municipios", [])}
        filtro_txt = self.busqueda_red_var.get().lower().strip()

        for r in self.jerarquia.get("redes", []):
            r_id = str(r.get("id", ""))
            r_cod = str(r.get("codigo", ""))
            r_nom = str(r.get("nombre", ""))
            r_mac = str(r.get("macrodistrito") or "-")
            r_mun = muns_dict.get(r.get("municipio_id"), "GAMLP")
            r_res = str(r.get("responsable") or "-")
            r_tel = str(r.get("telefono") or "-")
            r_est = str(r.get("estado") or "Activo")

            if filtro_txt:
                match = (filtro_txt in r_nom.lower() or 
                         filtro_txt in r_cod.lower() or 
                         filtro_txt in r_mac.lower() or 
                         filtro_txt in r_res.lower())
                if not match:
                    continue

            self.tabla_redes.insert("", "end", values=(r_id, r_cod, r_nom, r_mac, r_mun, r_res, r_tel, r_est))

    def poblar_tabla_municipios(self):
        for item in self.tabla_mun.get_children():
            self.tabla_mun.delete(item)
        deptos_dict = {d["id"]: d["nombre"] for d in self.jerarquia.get("departamentos", [])}
        for m in self.jerarquia.get("municipios", []):
            d_nom = deptos_dict.get(m.get("departamento_id"), "La Paz")
            self.tabla_mun.insert("", "end", values=(m.get("id"), m.get("nombre"), m.get("codigo") or "-", d_nom, m.get("estado") or "Activo"))

    def poblar_tabla_departamentos(self):
        for item in self.tabla_dep.get_children():
            self.tabla_dep.delete(item)
        for d in self.jerarquia.get("departamentos", []):
            self.tabla_dep.insert("", "end", values=(d.get("id"), d.get("nombre"), d.get("codigo") or "-", d.get("estado") or "Activo"))

    # ========================================================
    # FORMULARIO MODAL: CENTRO DE SALUD
    # ========================================================
    def abrir_formulario_centro(self, editar=False):
        if editar:
            if not self.app.tiene_permiso("Sedes", "cambiar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para modificar centros de salud.")
                return
            sel = self.tabla_centros.selection() or ([self.tabla_centros.focus()] if self.tabla_centros.focus() else [])
            if not sel:
                messagebox.showwarning("Selección Requerida", "Por favor seleccione un Centro de Salud de la tabla para modificar.")
                return
            vals = self.tabla_centros.item(sel[0], "values")
            c_id = int(vals[0])
            c_sel = next((c for c in self.jerarquia.get("centros", []) if c["id"] == c_id), None)
        else:
            if not self.app.tiene_permiso("Sedes", "agregar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para registrar nuevos centros de salud.")
                return
            c_sel = None

        vent = ctk.CTkToplevel(self)
        vent.title("Modificar Centro de Salud" if editar else "Añadir Nuevo Centro de Salud")
        vent.geometry("540x600")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)

        ctk.CTkLabel(
            vent, 
            text="Datos del Centro de Salud / Hospital", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=C_TEXT
        ).pack(pady=(16, 12))

        f_form = ctk.CTkFrame(vent, fg_color="transparent")
        f_form.pack(fill="both", expand=True, padx=30, pady=5)

        # Red de Salud
        ctk.CTkLabel(f_form, text="Red de Salud:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        redes_lista = [r["nombre"] for r in self.jerarquia.get("redes", [])]
        cb_red = ctk.CTkComboBox(f_form, values=redes_lista if redes_lista else ["Sin Red"], width=460)
        cb_red.pack(pady=(0, 8))

        # Nombre
        ctk.CTkLabel(f_form, text="Nombre del Centro de Salud / Hospital:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_nombre = ctk.CTkEntry(f_form, placeholder_text="ej. C.M.I. CHASQUIPAMPA", width=460)
        e_nombre.pack(pady=(0, 8))

        # Nivel de atención
        ctk.CTkLabel(f_form, text="Nivel del Centro:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        niveles_opc = ["Primer Nivel", "Segundo Nivel", "Tercer Nivel", "Centro de Salud Integral", "Hospital Municipal", "Puesto de Salud"]
        cb_nivel = ctk.CTkComboBox(f_form, values=niveles_opc, width=460)
        cb_nivel.pack(pady=(0, 8))

        # Ubicación / Dirección
        ctk.CTkLabel(f_form, text="Ubicación / Dirección:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_dir = ctk.CTkEntry(f_form, placeholder_text="ej. Calle 45, Zona Chasquipampa", width=460)
        e_dir.pack(pady=(0, 8))

        # Teléfono
        ctk.CTkLabel(f_form, text="Teléfono / Contacto:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_tel = ctk.CTkEntry(f_form, placeholder_text="ej. 2781234 / 70123456", width=460)
        e_tel.pack(pady=(0, 8))

        # Responsable
        ctk.CTkLabel(f_form, text="Responsable / Director(a):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_res = ctk.CTkEntry(f_form, placeholder_text="ej. Dr. Juan Pérez", width=460)
        e_res.pack(pady=(0, 8))

        # Estado
        ctk.CTkLabel(f_form, text="Estado:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        cb_est = ctk.CTkComboBox(f_form, values=["Activo", "Inactivo"], width=460)
        cb_est.pack(pady=(0, 10))

        # Cargar datos existentes si es edición
        if c_sel:
            e_nombre.insert(0, c_sel.get("nombre", ""))
            cb_nivel.set(c_sel.get("nivel") or "Primer Nivel")
            e_dir.insert(0, c_sel.get("direccion") or "")
            e_tel.insert(0, c_sel.get("telefono") or "")
            e_res.insert(0, c_sel.get("responsable") or "")
            cb_est.set(c_sel.get("estado") or "Activo")
            
            # Buscar nombre de la red
            r_obj = next((r for r in self.jerarquia.get("redes", []) if r["id"] == c_sel.get("red_salud_id")), None)
            if r_obj:
                cb_red.set(r_obj["nombre"])

        def guardar_centro():
            nom = e_nombre.get().strip()
            if not nom:
                messagebox.showwarning("Campo Requerido", "El nombre del Centro de Salud es obligatorio.")
                return

            red_nom = cb_red.get().strip()
            r_obj = next((r for r in self.jerarquia.get("redes", []) if r["nombre"] == red_nom), None)
            red_id = r_obj["id"] if r_obj else None

            payload = {
                "id": c_sel["id"] if c_sel else None,
                "red_salud_id": red_id,
                "nombre": nom,
                "nivel": cb_nivel.get().strip(),
                "direccion": e_dir.get().strip(),
                "telefono": e_tel.get().strip(),
                "responsable": e_res.get().strip(),
                "estado": cb_est.get().strip()
            }

            ok, res = guardar_centro_salud_db(payload)
            if ok:
                messagebox.showinfo("Éxito", f"Centro de Salud '{nom}' guardado correctamente.")
                vent.destroy()
                self.refrescar_datos()
            else:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar el centro de salud:\n{res}")

        f_bot_v = ctk.CTkFrame(vent, fg_color="transparent")
        f_bot_v.pack(fill="x", padx=30, pady=(4, 16))

        ctk.CTkButton(
            f_bot_v, 
            text="💾 Guardar Cambios" if editar else "➕ Crear Centro de Salud", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            height=38, 
            corner_radius=8, 
            command=guardar_centro
        ).pack(side="left", expand=True, padx=(0, 6))

        ctk.CTkButton(
            f_bot_v, 
            text="Cancelar", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BG, 
            text_color=C_TEXT, 
            hover_color=C_BORDER, 
            height=38, 
            corner_radius=8, 
            command=vent.destroy
        ).pack(side="right", expand=True, padx=(6, 0))

    def eliminar_centro_click(self):
        if not self.app.tiene_permiso("Sedes", "eliminar"):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para eliminar o desactivar centros de salud.")
            return
        sel = self.tabla_centros.selection() or ([self.tabla_centros.focus()] if self.tabla_centros.focus() else [])
        if not sel:
            messagebox.showwarning("Selección Requerida", "Por favor seleccione un Centro de Salud para eliminar o desactivar.")
            return
        vals = self.tabla_centros.item(sel[0], "values")
        c_id = int(vals[0])
        c_nom = vals[2]

        conf = messagebox.askyesno("Confirmar Desactivación", f"¿Está seguro de desactivar el Centro de Salud '{c_nom}'?\n\nLos equipos asociados permanecerán protegidos en el historial.")
        if conf:
            ok, res = eliminar_centro_salud_db(c_id, eliminacion_fisica=False)
            if ok:
                messagebox.showinfo("Desactivado", f"El Centro de Salud '{c_nom}' fue desactivado.")
                self.refrescar_datos()
            else:
                messagebox.showerror("Error", f"No se pudo desactivar el centro:\n{res}")

    # ========================================================
    # FORMULARIO MODAL: RED DE SALUD
    # ========================================================
    def abrir_formulario_red(self, editar=False):
        if editar:
            if not self.app.tiene_permiso("Sedes", "cambiar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para modificar redes de salud.")
                return
            sel = self.tabla_redes.selection() or ([self.tabla_redes.focus()] if self.tabla_redes.focus() else [])
            if not sel:
                messagebox.showwarning("Selección Requerida", "Por favor seleccione una Red de Salud de la tabla para modificar.")
                return
            vals = self.tabla_redes.item(sel[0], "values")
            r_id = int(vals[0])
            r_sel = next((r for r in self.jerarquia.get("redes", []) if r["id"] == r_id), None)
        else:
            if not self.app.tiene_permiso("Sedes", "agregar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para crear nuevas redes de salud.")
                return
            r_sel = None

        vent = ctk.CTkToplevel(self)
        vent.title("Modificar Red de Salud" if editar else "Añadir Nueva Red de Salud")
        vent.geometry("540x550")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)

        ctk.CTkLabel(vent, text="Datos de la Red de Salud", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(16, 12))

        f_form = ctk.CTkFrame(vent, fg_color="transparent")
        f_form.pack(fill="both", expand=True, padx=30, pady=5)

        # Código
        ctk.CTkLabel(f_form, text="Código de Red (ej. RED-1, RED-6):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_cod = ctk.CTkEntry(f_form, placeholder_text="ej. RED-6", width=460)
        e_cod.pack(pady=(0, 8))

        # Nombre
        ctk.CTkLabel(f_form, text="Nombre Completo de la Red:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_nom = ctk.CTkEntry(f_form, placeholder_text="ej. RED 6-RURAL (MACRODISTRITO ZONGO/HAMPATURI)", width=460)
        e_nom.pack(pady=(0, 8))

        # Macrodistrito
        ctk.CTkLabel(f_form, text="Macrodistrito Asignado:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_mac = ctk.CTkEntry(f_form, placeholder_text="ej. SUR / COTAHUMA / SAN ANTONIO", width=460)
        e_mac.pack(pady=(0, 8))

        # Responsable
        ctk.CTkLabel(f_form, text="Coordinador(a) / Responsable de Red:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_res = ctk.CTkEntry(f_form, placeholder_text="ej. Dr. Carlos Medina", width=460)
        e_res.pack(pady=(0, 8))

        # Teléfono
        ctk.CTkLabel(f_form, text="Teléfono / Contacto:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_tel = ctk.CTkEntry(f_form, placeholder_text="ej. 2212345", width=460)
        e_tel.pack(pady=(0, 8))

        # Estado
        ctk.CTkLabel(f_form, text="Estado:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        cb_est = ctk.CTkComboBox(f_form, values=["Activo", "Inactivo"], width=460)
        cb_est.pack(pady=(0, 10))

        if r_sel:
            e_cod.insert(0, r_sel.get("codigo", ""))
            e_nom.insert(0, r_sel.get("nombre", ""))
            e_mac.insert(0, r_sel.get("macrodistrito") or "")
            e_res.insert(0, r_sel.get("responsable") or "")
            e_tel.insert(0, r_sel.get("telefono") or "")
            cb_est.set(r_sel.get("estado") or "Activo")

        def guardar_red():
            cod = e_cod.get().strip()
            nom = e_nom.get().strip()
            if not cod or not nom:
                messagebox.showwarning("Campos Requeridos", "El código y el nombre de la Red son obligatorios.")
                return

            payload = {
                "id": r_sel["id"] if r_sel else None,
                "codigo": cod,
                "nombre": nom,
                "macrodistrito": e_mac.get().strip(),
                "responsable": e_res.get().strip(),
                "telefono": e_tel.get().strip(),
                "estado": cb_est.get().strip(),
                "municipio_id": 1,
                "departamento_id": 1
            }

            ok, res = guardar_red_salud_db(payload)
            if ok:
                messagebox.showinfo("Éxito", f"Red de Salud '{nom}' guardada correctamente.")
                vent.destroy()
                self.refrescar_datos()
            else:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar la Red de Salud:\n{res}")

        f_bot_v = ctk.CTkFrame(vent, fg_color="transparent")
        f_bot_v.pack(fill="x", padx=30, pady=(4, 16))

        ctk.CTkButton(
            f_bot_v, 
            text="💾 Guardar Red" if editar else "➕ Crear Red de Salud", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            height=38, 
            corner_radius=8, 
            command=guardar_red
        ).pack(side="left", expand=True, padx=(0, 6))

        ctk.CTkButton(
            f_bot_v, 
            text="Cancelar", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BG, 
            text_color=C_TEXT, 
            hover_color=C_BORDER, 
            height=38, 
            corner_radius=8, 
            command=vent.destroy
        ).pack(side="right", expand=True, padx=(6, 0))

    def eliminar_red_click(self):
        if not self.app.tiene_permiso("Sedes", "eliminar"):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para desactivar redes de salud.")
            return
        sel = self.tabla_redes.selection() or ([self.tabla_redes.focus()] if self.tabla_redes.focus() else [])
        if not sel:
            messagebox.showwarning("Selección Requerida", "Por favor seleccione una Red de Salud para desactivar.")
            return
        vals = self.tabla_redes.item(sel[0], "values")
        r_id = int(vals[0])
        r_nom = vals[2]

        conf = messagebox.askyesno("Confirmar Desactivación", f"¿Está seguro de desactivar la Red '{r_nom}'?")
        if conf:
            ok, res = eliminar_red_salud_db(r_id)
            if ok:
                messagebox.showinfo("Desactivada", f"La Red '{r_nom}' fue desactivada.")
                self.refrescar_datos()
            else:
                messagebox.showerror("Error", f"No se pudo desactivar la Red:\n{res}")

    # ========================================================
    # FORMULARIO MODAL: MUNICIPIO
    # ========================================================
    def abrir_formulario_municipio(self, editar=False):
        if editar:
            if not self.app.tiene_permiso("Sedes", "cambiar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para modificar municipios.")
                return
            sel = self.tabla_mun.selection() or ([self.tabla_mun.focus()] if self.tabla_mun.focus() else [])
            if not sel:
                messagebox.showwarning("Selección Requerida", "Por favor seleccione un Municipio de la tabla para modificar.")
                return
            vals = self.tabla_mun.item(sel[0], "values")
            m_id = int(vals[0])
            m_sel = next((m for m in self.jerarquia.get("municipios", []) if m["id"] == m_id), None)
        else:
            if not self.app.tiene_permiso("Sedes", "agregar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para registrar municipios.")
                return
            m_sel = None

        vent = ctk.CTkToplevel(self)
        vent.title("Modificar Municipio" if editar else "Añadir Nuevo Municipio")
        vent.geometry("450x360")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)

        ctk.CTkLabel(vent, text="Datos del Municipio", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(16, 12))

        f_form = ctk.CTkFrame(vent, fg_color="transparent")
        f_form.pack(fill="both", expand=True, padx=24, pady=5)

        ctk.CTkLabel(f_form, text="Nombre del Municipio:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_nom = ctk.CTkEntry(f_form, placeholder_text="ej. GAMLP", width=380)
        e_nom.pack(pady=(0, 8))

        ctk.CTkLabel(f_form, text="Código / Sigla:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_cod = ctk.CTkEntry(f_form, placeholder_text="ej. GAMLP / LPZ-01", width=380)
        e_cod.pack(pady=(0, 8))

        ctk.CTkLabel(f_form, text="Estado:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        cb_est = ctk.CTkComboBox(f_form, values=["Activo", "Inactivo"], width=380)
        cb_est.pack(pady=(0, 10))

        if m_sel:
            e_nom.insert(0, m_sel.get("nombre", ""))
            e_cod.insert(0, m_sel.get("codigo") or "")
            cb_est.set(m_sel.get("estado") or "Activo")

        def guardar_mun():
            nom = e_nom.get().strip()
            if not nom:
                messagebox.showwarning("Campo Requerido", "El nombre del Municipio es obligatorio.")
                return
            payload = {
                "id": m_sel["id"] if m_sel else None,
                "nombre": nom,
                "codigo": e_cod.get().strip(),
                "estado": cb_est.get().strip(),
                "departamento_id": 1
            }
            ok, res = guardar_municipio_db(payload)
            if ok:
                messagebox.showinfo("Éxito", f"Municipio '{nom}' guardado correctamente.")
                vent.destroy()
                self.refrescar_datos()
            else:
                messagebox.showerror("Error", f"No se pudo guardar el municipio:\n{res}")

        f_bot = ctk.CTkFrame(vent, fg_color="transparent")
        f_bot.pack(fill="x", padx=24, pady=(4, 16))
        ctk.CTkButton(f_bot, text="💾 Guardar", font=ctk.CTkFont(weight="bold"), fg_color=C_BLUE, height=36, corner_radius=8, command=guardar_mun).pack(side="left", expand=True, padx=(0, 4))
        ctk.CTkButton(f_bot, text="Cancelar", font=ctk.CTkFont(weight="bold"), fg_color=C_BG, text_color=C_TEXT, height=36, corner_radius=8, command=vent.destroy).pack(side="right", expand=True, padx=(4, 0))

    # ========================================================
    # FORMULARIO MODAL: DEPARTAMENTO
    # ========================================================
    def abrir_formulario_departamento(self, editar=False):
        if editar:
            if not self.app.tiene_permiso("Sedes", "cambiar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para modificar departamentos.")
                return
            sel = self.tabla_dep.selection() or ([self.tabla_dep.focus()] if self.tabla_dep.focus() else [])
            if not sel:
                messagebox.showwarning("Selección Requerida", "Por favor seleccione un Departamento para modificar.")
                return
            vals = self.tabla_dep.item(sel[0], "values")
            d_id = int(vals[0])
            d_sel = next((d for d in self.jerarquia.get("departamentos", []) if d["id"] == d_id), None)
        else:
            if not self.app.tiene_permiso("Sedes", "agregar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para registrar departamentos.")
                return
            d_sel = None

        vent = ctk.CTkToplevel(self)
        vent.title("Modificar Departamento" if editar else "Añadir Nuevo Departamento")
        vent.geometry("450x360")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)

        ctk.CTkLabel(vent, text="Datos del Departamento", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(16, 12))

        f_form = ctk.CTkFrame(vent, fg_color="transparent")
        f_form.pack(fill="both", expand=True, padx=24, pady=5)

        ctk.CTkLabel(f_form, text="Nombre del Departamento:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_nom = ctk.CTkEntry(f_form, placeholder_text="ej. La Paz, Cochabamba, Santa Cruz", width=380)
        e_nom.pack(pady=(0, 8))

        ctk.CTkLabel(f_form, text="Código / Sigla:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        e_cod = ctk.CTkEntry(f_form, placeholder_text="ej. LPZ, CBBA, SCZ", width=380)
        e_cod.pack(pady=(0, 8))

        ctk.CTkLabel(f_form, text="Estado:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(4, 2))
        cb_est = ctk.CTkComboBox(f_form, values=["Activo", "Inactivo"], width=380)
        cb_est.pack(pady=(0, 10))

        if d_sel:
            e_nom.insert(0, d_sel.get("nombre", ""))
            e_cod.insert(0, d_sel.get("codigo") or "")
            cb_est.set(d_sel.get("estado") or "Activo")

        def guardar_dep():
            nom = e_nom.get().strip()
            if not nom:
                messagebox.showwarning("Campo Requerido", "El nombre del Departamento es obligatorio.")
                return
            payload = {
                "id": d_sel["id"] if d_sel else None,
                "nombre": nom,
                "codigo": e_cod.get().strip(),
                "estado": cb_est.get().strip()
            }
            ok, res = guardar_departamento_db(payload)
            if ok:
                messagebox.showinfo("Éxito", f"Departamento '{nom}' guardado correctamente.")
                vent.destroy()
                self.refrescar_datos()
            else:
                messagebox.showerror("Error", f"No se pudo guardar el departamento:\n{res}")

        f_bot = ctk.CTkFrame(vent, fg_color="transparent")
        f_bot.pack(fill="x", padx=24, pady=(4, 16))
        ctk.CTkButton(f_bot, text="💾 Guardar", font=ctk.CTkFont(weight="bold"), fg_color=C_BLUE, height=36, corner_radius=8, command=guardar_dep).pack(side="left", expand=True, padx=(0, 4))
        ctk.CTkButton(f_bot, text="Cancelar", font=ctk.CTkFont(weight="bold"), fg_color=C_BG, text_color=C_TEXT, height=36, corner_radius=8, command=vent.destroy).pack(side="right", expand=True, padx=(4, 0))
