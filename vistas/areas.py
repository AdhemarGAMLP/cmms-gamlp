# vistas/areas.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import psycopg2.extras
from database import (
    obtener_conexion, 
    mover_a_papelera, 
    ejecutar_en_segundo_plano, 
    guardar_cache_local_datos,
    obtener_jerarquia_sedes_db
)
from estilos import *

class VistaAreas(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self._sedes_data = None
        self.construir_ui()

    def _obtener_sedes_jerarquia(self):
        if not self._sedes_data:
            self._sedes_data = obtener_jerarquia_sedes_db()
        return self._sedes_data

    def construir_ui(self):
        # Cabecera
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(pady=(20, 10), padx=30, fill="x")

        ctk.CTkLabel(
            f_top, 
            text="Gestión en Áreas", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color=C_TEXT
        ).pack(side="left")

        # Barra de Filtros
        f_filtros = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        f_filtros.pack(padx=30, pady=(0, 10), fill="x")

        f_f_inner = ctk.CTkFrame(f_filtros, fg_color="transparent")
        f_f_inner.pack(padx=12, pady=10, fill="x")

        # Búsqueda
        ctk.CTkLabel(f_f_inner, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 4))
        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", lambda *a: self.refrescar_datos())
        e_buscar = ctk.CTkEntry(
            f_f_inner, 
            textvariable=self.busqueda_var, 
            placeholder_text="Buscar área, doctor, cargo, centro, piso, CI...", 
            width=250, 
            fg_color=C_BG, 
            border_color=C_BORDER, 
            corner_radius=8
        )
        e_buscar.pack(side="left", padx=(0, 10))

        # Inicializar filtros desde la sede activa del inicio
        sedes = self._obtener_sedes_jerarquia()
        contexto = getattr(self.app, "contexto_sede", None)
        red_inicial = "[ Todas las Redes ]"
        centro_inicial = "[ Todos los Centros ]"
        centros_iniciales = ["[ Todos los Centros ]"] + [c["nombre"] for c in sedes.get("centros", [])]
        
        if contexto and not contexto.get("es_global", True):
            cen_nom = contexto.get("centro_salud")
            red_nom = contexto.get("red_salud")
            if red_nom:
                red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_nom), None)
                if red_obj:
                    red_inicial = red_nom
                    centros_iniciales = ["[ Todos los Centros ]"] + [c["nombre"] for c in sedes.get("centros", []) if c.get("red_salud_id") == red_obj["id"]]
            if cen_nom and not str(cen_nom).startswith("[ Todos"):
                centro_inicial = cen_nom

        # Filtro Red
        ctk.CTkLabel(f_f_inner, text="Red:", font=ctk.CTkFont(size=11, weight="bold"), text_color=C_TEXT).pack(side="left", padx=(4, 2))
        nombres_redes = ["[ Todas las Redes ]"] + [r["nombre"] for r in sedes.get("redes", [])]
        self.combo_filtro_red = ctk.CTkComboBox(
            f_f_inner, 
            values=nombres_redes, 
            width=180, 
            command=self._al_cambiar_filtro_red, 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_red.pack(side="left", padx=(0, 10))
        self.combo_filtro_red.set(red_inicial)

        # Filtro Centro
        ctk.CTkLabel(f_f_inner, text="Centro:", font=ctk.CTkFont(size=11, weight="bold"), text_color=C_TEXT).pack(side="left", padx=(4, 2))
        self.combo_filtro_centro = ctk.CTkComboBox(
            f_f_inner, 
            values=centros_iniciales, 
            width=180, 
            command=lambda e: self.refrescar_datos(), 
            fg_color=C_BG, 
            border_color=C_BORDER
        )
        self.combo_filtro_centro.pack(side="left", padx=(0, 10))
        self.combo_filtro_centro.set(centro_inicial)

        # Botón Limpiar
        ctk.CTkButton(
            f_f_inner, 
            text="↺ Limpiar", 
            width=70, 
            height=28, 
            fg_color="#E2E8F0", 
            text_color=C_TEXT, 
            hover_color="#CBD5E1", 
            corner_radius=6, 
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.limpiar_filtros
        ).pack(side="right")
        
        # Tabla Principal (Ocultamos ID visible y añadimos Cargo)
        marco = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        marco.pack(padx=30, pady=(0, 10), fill="both", expand=True)
        
        cols = ("Centro de Salud", "Red de Salud", "Área / Unidad", "Piso", "Encargado / Doctor(a)", "Cargo", "C.I. Encargado", "Contacto")
        f_tree_areas = ctk.CTkFrame(marco, fg_color="transparent")
        f_tree_areas.pack(pady=12, padx=12, fill="both", expand=True)
        self.tabla_areas = ttk.Treeview(f_tree_areas, columns=cols, show="headings")
        scrollbar_areas = ctk.CTkScrollbar(f_tree_areas, orientation="vertical", command=self.tabla_areas.yview, width=12)
        scroll_x = ctk.CTkScrollbar(f_tree_areas, orientation="horizontal", command=self.tabla_areas.xview, height=12)
        self.tabla_areas.configure(yscrollcommand=scrollbar_areas.set, xscrollcommand=scroll_x.set)

        ancho_cols = {
            "Centro de Salud": 170,
            "Red de Salud": 140,
            "Área / Unidad": 160,
            "Piso": 70,
            "Encargado / Doctor(a)": 160,
            "Cargo": 140,
            "C.I. Encargado": 95,
            "Contacto": 95
        }
        
        for c in cols:
            self.tabla_areas.heading(c, text=c)
            w = ancho_cols.get(c, 100)
            align = "center" if c in ("Piso", "C.I. Encargado", "Contacto") else "w"
            self.tabla_areas.column(c, width=w, minwidth=40, anchor=align)

        self.tabla_areas.pack(side="left", fill="both", expand=True)
        self.tabla_areas.tag_configure("fila_par", background="#FFFFFF", foreground=C_TEXT)
        self.tabla_areas.tag_configure("fila_impar", background="#F8FAFC", foreground=C_TEXT)
        scrollbar_areas.pack(side="right", fill="y", padx=(4, 0))
        
        self.tabla_areas.bind("<Double-1>", lambda e: self.modificar_area())

        # Botones Inferiores
        f_bot = ctk.CTkFrame(self, fg_color="transparent")
        f_bot.pack(pady=(5, 20), padx=30, fill="x")
        
        self.btn_anadir = ctk.CTkButton(f_bot, text="✚ Añadir Área al Centro", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, text_color="#FFFFFF", corner_radius=8, height=40, command=self.abrir_formulario_area)
        self.btn_anadir.pack(side="left", expand=True, padx=8)
        self.btn_modificar = ctk.CTkButton(f_bot, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE_LIGHT, hover_color="#D8E8FC", text_color=C_BLUE, corner_radius=8, height=40, command=self.modificar_area)
        self.btn_modificar.pack(side="left", expand=True, padx=8)
        
        self.btn_eliminar = ctk.CTkButton(f_bot, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, text_color="#FFFFFF", corner_radius=8, height=40, command=self.eliminar_area)
        self.btn_eliminar.pack(side="left", expand=True, padx=8)

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

    def sincronizar_con_contexto_sede(self):
        """Sincroniza los filtros de la vista con la sede activa del sistema si no es global."""
        contexto = getattr(self.app, "contexto_sede", None)
        sedes = self._obtener_sedes_jerarquia()
        if contexto and not contexto.get("es_global", True):
            cen_nom = contexto.get("centro_salud")
            red_nom = contexto.get("red_salud")
            if red_nom:
                self.combo_filtro_red.set(red_nom)
                red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_nom), None)
                if red_obj:
                    centros = ["[ Todos los Centros ]"] + [c["nombre"] for c in sedes.get("centros", []) if c.get("red_salud_id") == red_obj["id"]]
                    self.combo_filtro_centro.configure(values=centros)
            if cen_nom and not str(cen_nom).startswith("[ Todos"):
                self.combo_filtro_centro.set(cen_nom)

    def limpiar_filtros(self):
        self.busqueda_var.set("")
        contexto = getattr(self.app, "contexto_sede", None)
        if contexto and not contexto.get("es_global", True):
            self.sincronizar_con_contexto_sede()
        else:
            self.combo_filtro_red.set("[ Todas las Redes ]")
            self._al_cambiar_filtro_red("[ Todas las Redes ]")
        self.refrescar_datos()

    def refrescar_datos(self):
        for i in self.tabla_areas.get_children():
            self.tabla_areas.delete(i)
        
        filas = self.app.datos.get("areas", [])
        q = self.busqueda_var.get().strip().lower()
        red_f = self.combo_filtro_red.get().strip()
        cen_f = self.combo_filtro_centro.get().strip()

        idx_vis = 0
        for r in filas:
            nom_cen = str(r.get("centro_salud_nombre") or "").strip()
            nom_red = str(r.get("red_salud_nombre") or "").strip()
            nom_area = str(r.get("nombre") or "").strip()
            piso = str(r.get("piso") or "").strip()
            enc = str(r.get("encargado") or "").strip()
            cargo = str(r.get("cargo") or "").strip()
            ci_enc = str(r.get("ci_encargado") or "").strip()
            con = str(r.get("contacto") or "").strip()

            if red_f != "[ Todas las Redes ]" and red_f.upper() not in nom_red.upper():
                continue
            if cen_f != "[ Todos los Centros ]" and cen_f.upper() not in nom_cen.upper():
                continue

            if q:
                campos = [nom_cen, nom_red, nom_area, piso, enc, cargo, ci_enc, con]
                if not any(q in c.lower() for c in campos):
                    continue

            tag_fila = "fila_par" if idx_vis % 2 == 0 else "fila_impar"
            idx_vis += 1

            self.tabla_areas.insert("", "end", iid=str(r.get("id") or f"area_{idx_vis}"), values=(
                nom_cen or "-",
                nom_red or "-",
                nom_area,
                piso or "-",
                enc or "-",
                cargo or "-",
                ci_enc or "-",
                con or "-"
            ), tags=(tag_fila,))

        can_add = self.app.tiene_permiso("Areas", "agregar")
        can_edit = self.app.tiene_permiso("Areas", "cambiar")
        can_del = self.app.tiene_permiso("Areas", "eliminar")
        self.btn_anadir.configure(state="normal" if can_add else "disabled", fg_color=C_BLUE if can_add else C_BORDER, text_color="#FFFFFF" if can_add else C_SUBTEXT)
        self.btn_modificar.configure(state="normal" if can_edit else "disabled", fg_color=C_BLUE_LIGHT if can_edit else C_BORDER, text_color=C_BLUE if can_edit else C_SUBTEXT)
        self.btn_eliminar.configure(state="normal" if can_del else "disabled", fg_color=C_RED if can_del else C_BORDER, text_color="#FFFFFF" if can_del else C_SUBTEXT)

    def obtener_seleccion(self):
        sel_iid = self.tabla_areas.focus()
        if not sel_iid:
            return None, None
        return sel_iid, self.tabla_areas.item(sel_iid, "values")

    def abrir_formulario_area(self, area_editar=None):
        if area_editar:
            if not self.app.tiene_permiso("Areas", "cambiar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para modificar áreas.")
                return
        else:
            if not self.app.tiene_permiso("Areas", "agregar"):
                messagebox.showwarning("Permiso Denegado", "No tiene permisos para añadir áreas.")
                return

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

        vent = ctk.CTkToplevel(self)
        titulo_modal = "Modificar Área del Centro" if area_editar else "Añadir Nueva Área al Centro"
        vent.title(titulo_modal)
        vent.geometry("560x700")
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_CARD)

        # Centrar
        vent.update_idletasks()
        w, h = 560, 700
        x = (vent.winfo_screenwidth() // 2) - (w // 2)
        y = (vent.winfo_screenheight() // 2) - (h // 2)
        vent.geometry(f"{w}x{h}+{x}+{y}")
        
        # Título sin emoji
        ctk.CTkLabel(vent, text=titulo_modal, font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(18, 10))
        
        # Red de Salud (sin asterisco)
        ctk.CTkLabel(vent, text="Dirección Administrativa (Red de Salud)", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        combo_red = ctk.CTkComboBox(vent, values=lista_redes, width=460)
        combo_red.pack(pady=(2, 6))

        # Centro de Salud (sin asterisco)
        ctk.CTkLabel(vent, text="Unidad Organizacional (Centro de Salud)", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        combo_centro = ctk.CTkComboBox(vent, values=["Seleccione Red..."], width=460)
        combo_centro.pack(pady=(2, 6))

        def actualizar_centros(red_nom, cen_sel_def=None):
            red_obj = next((r for r in sedes.get("redes", []) if r["nombre"] == red_nom), None)
            if red_obj:
                centros = [c["nombre"] for c in sedes.get("centros", []) if c.get("red_salud_id") == red_obj["id"]]
            else:
                centros = [c["nombre"] for c in sedes.get("centros", [])]
            if "RED 1" in (red_nom or "").upper() and "167 AUXILIO" not in centros:
                centros.append("167 AUXILIO")
            if not centros:
                centros = ["CENTRO DE SALUD GAMLP"]
            combo_centro.configure(values=centros)
            if cen_sel_def and cen_sel_def in centros:
                combo_centro.set(cen_sel_def)
            elif centros:
                combo_centro.set(centros[0])

        combo_red.configure(command=lambda r: actualizar_centros(r))

        # Red y Centro iniciales respetando contexto activo
        if area_editar:
            red_ini = area_editar.get("red_salud_nombre") or (lista_redes[0] if lista_redes else "")
            cen_ini = area_editar.get("centro_salud_nombre")
            combo_red.set(red_ini)
            actualizar_centros(red_ini, cen_ini)
        else:
            red_sel_filtro = self.combo_filtro_red.get()
            cen_sel_filtro = self.combo_filtro_centro.get()
            if red_sel_filtro and red_sel_filtro != "[ Todas las Redes ]":
                combo_red.set(red_sel_filtro)
                actualizar_centros(red_sel_filtro, cen_sel_filtro if cen_sel_filtro != "[ Todos los Centros ]" else None)
            else:
                combo_red.set(lista_redes[0] if lista_redes else "")
                actualizar_centros(combo_red.get())

        # Nombre del Área (sin asterisco)
        ctk.CTkLabel(vent, text="Nombre del Área / Unidad", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        e_nombre = ctk.CTkEntry(vent, placeholder_text="Ej: Ecografía, Emergencias, Farmacia, Odontología...", width=460)
        e_nombre.pack(pady=(2, 6))
        
        # Piso / Nivel
        ctk.CTkLabel(vent, text="Piso / Nivel", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        e_piso = ctk.CTkEntry(vent, placeholder_text="Ej: Piso 1, PB, Piso 2...", width=460)
        e_piso.pack(pady=(2, 6))

        # Encargado(a) / Doctor(a)
        ctk.CTkLabel(vent, text="Encargado(a) / Doctor(a) del Área", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        e_encargado = ctk.CTkEntry(vent, placeholder_text="Nombre completo del personal o doctor(a) a cargo...", width=460)
        e_encargado.pack(pady=(2, 6))

        # Cargo (ubicado abajo de Encargado)
        ctk.CTkLabel(vent, text="Cargo", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        e_cargo = ctk.CTkEntry(vent, placeholder_text="Ej: Responsable de Área, Médico de Turno, Lic. en Enfermería...", width=460)
        e_cargo.pack(pady=(2, 6))

        # C.I. Doctor(a)
        ctk.CTkLabel(vent, text="C.I. Encargado(a) / Doctor(a)", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        e_ci_encargado = ctk.CTkEntry(vent, placeholder_text="Ej: 4892711 LP...", width=460)
        e_ci_encargado.pack(pady=(2, 6))

        # Contacto
        ctk.CTkLabel(vent, text="Número de Contacto / Interno", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", padx=45, pady=(4, 0))
        e_contacto = ctk.CTkEntry(vent, placeholder_text="Teléfono o interno...", width=460)
        e_contacto.pack(pady=(2, 6))
        
        if area_editar:
            e_nombre.insert(0, str(area_editar.get("nombre") or ""))
            if area_editar.get("piso"):
                e_piso.insert(0, str(area_editar["piso"]))
            if area_editar.get("encargado"):
                e_encargado.insert(0, str(area_editar["encargado"]))
            if area_editar.get("cargo"):
                e_cargo.insert(0, str(area_editar["cargo"]))
            if area_editar.get("ci_encargado"):
                e_ci_encargado.insert(0, str(area_editar["ci_encargado"]))
            if area_editar.get("contacto"):
                e_contacto.insert(0, str(area_editar["contacto"]))
            
        def guardar_area():
            red_val = combo_red.get().strip()
            cen_val = combo_centro.get().strip()
            nom = e_nombre.get().strip()
            pis = e_piso.get().strip()
            enc = e_encargado.get().strip()
            car = e_cargo.get().strip()
            ci_enc = e_ci_encargado.get().strip()
            con = e_contacto.get().strip()
            
            if not nom:
                messagebox.showwarning("Dato Obligatorio", "Debe introducir el nombre del área o unidad.", parent=vent)
                e_nombre.focus_set()
                return

            # Resolver IDs
            cen_obj = next((c for c in sedes.get("centros", []) if c["nombre"] == cen_val), None)
            cen_id = cen_obj["id"] if cen_obj else None
                
            area_id = area_editar.get("id") if area_editar else None

            area_obj = {
                "id": area_id,
                "centro_salud_id": cen_id,
                "centro_salud_nombre": cen_val,
                "red_salud_nombre": red_val,
                "nombre": nom,
                "piso": pis,
                "contacto": con,
                "encargado": enc,
                "cargo": car,
                "ci_encargado": ci_enc
            }

            if area_editar:
                for idx_a, ex in enumerate(self.app.datos.get("areas", [])):
                    if (area_id and str(ex.get("id")) == str(area_id)) or (ex.get("nombre") == area_editar.get("nombre") and ex.get("centro_salud_nombre") == area_editar.get("centro_salud_nombre")):
                        self.app.datos["areas"][idx_a] = area_obj
                        break
            else:
                self.app.datos.setdefault("areas", []).insert(0, area_obj)

            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()
            vent.destroy()

            # Guardar en PostgreSQL en segundo plano (con cola offline ante desconexión)
            def _guardar_area_db(a_dict, es_edit, old_a):
                from database import guardar_area_offline_cola
                conn = obtener_conexion()
                if not conn:
                    guardar_area_offline_cola(dict(a_dict))
                    return
                try:
                    cur = conn.cursor()
                    if es_edit and a_dict.get("id"):
                        cur.execute("""
                            UPDATE areas 
                            SET centro_salud_id=%s, centro_salud_nombre=%s, red_salud_nombre=%s,
                                nombre=%s, piso=%s, contacto=%s, encargado=%s, cargo=%s, ci_encargado=%s 
                            WHERE id=%s
                        """, (
                            a_dict["centro_salud_id"], a_dict["centro_salud_nombre"], a_dict["red_salud_nombre"],
                            a_dict["nombre"], a_dict["piso"], a_dict["contacto"],
                            a_dict["encargado"], a_dict["cargo"], a_dict["ci_encargado"], a_dict["id"]
                        ))
                    elif es_edit and old_a:
                        cur.execute("""
                            UPDATE areas 
                            SET centro_salud_id=%s, centro_salud_nombre=%s, red_salud_nombre=%s,
                                nombre=%s, piso=%s, contacto=%s, encargado=%s, cargo=%s, ci_encargado=%s 
                            WHERE nombre=%s AND COALESCE(centro_salud_nombre, '') = COALESCE(%s, '')
                        """, (
                            a_dict["centro_salud_id"], a_dict["centro_salud_nombre"], a_dict["red_salud_nombre"],
                            a_dict["nombre"], a_dict["piso"], a_dict["contacto"],
                            a_dict["encargado"], a_dict["cargo"], a_dict["ci_encargado"],
                            old_a.get("nombre"), old_a.get("centro_salud_nombre", "")
                        ))
                    else:
                        cur.execute("""
                            INSERT INTO areas (centro_salud_id, centro_salud_nombre, red_salud_nombre, nombre, piso, contacto, encargado, cargo, ci_encargado) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            a_dict["centro_salud_id"], a_dict["centro_salud_nombre"], a_dict["red_salud_nombre"],
                            a_dict["nombre"], a_dict["piso"], a_dict["contacto"],
                            a_dict["encargado"], a_dict["cargo"], a_dict["ci_encargado"]
                        ))
                        row_new = cur.fetchone()
                        if row_new:
                            a_dict["id"] = row_new[0]
                    conn.commit()
                    cur.close()
                    conn.close()
                except Exception as err:
                    print(f"[ERROR] Error al guardar área en PostgreSQL: {err}. Guardando en cola offline...")
                    if conn:
                        try: conn.rollback(); conn.close()
                        except: pass
                    guardar_area_offline_cola(dict(a_dict))

            ejecutar_en_segundo_plano(_guardar_area_db, area_obj, bool(area_editar), area_editar)
                
        ctk.CTkButton(vent, text="💾 Guardar Área", fg_color=C_BLUE, font=ctk.CTkFont(weight="bold", size=13), height=38, command=guardar_area).pack(pady=15)

    def modificar_area(self):
        sel_iid, vals = self.obtener_seleccion()
        if not sel_iid:
            messagebox.showwarning("Selección Requerida", "Por favor seleccione un área de la tabla para modificar.")
            return

        area_obj = None
        for a in self.app.datos.get("areas", []):
            if str(a.get("id")) == str(sel_iid):
                area_obj = a
                break

        if not area_obj and vals:
            area_obj = {
                "id": sel_iid if not str(sel_iid).startswith("area_") else None,
                "centro_salud_nombre": vals[0] if vals[0] != "-" else "",
                "red_salud_nombre": vals[1] if vals[1] != "-" else "",
                "nombre": vals[2],
                "piso": vals[3] if vals[3] != "-" else "",
                "encargado": vals[4] if vals[4] != "-" else "",
                "cargo": vals[5] if vals[5] != "-" else "",
                "ci_encargado": vals[6] if vals[6] != "-" else "",
                "contacto": vals[7] if vals[7] != "-" else ""
            }

        if area_obj:
            self.abrir_formulario_area(area_obj)

    def eliminar_area(self):
        if not self.app.tiene_permiso("Areas", "eliminar"):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para eliminar áreas.")
            return
        sel_iid, vals = self.obtener_seleccion()
        if not sel_iid:
            messagebox.showwarning("Selección Requerida", "Por favor seleccione un área de la tabla para eliminar.")
            return

        area_obj = next((a for a in self.app.datos.get("areas", []) if str(a.get("id")) == str(sel_iid)), None)
        nom_area = area_obj.get("nombre") if area_obj else (vals[2] if vals else "")
        nom_cen = area_obj.get("centro_salud_nombre") if area_obj else (vals[0] if vals else "")
        a_id = area_obj.get("id") if area_obj else (sel_iid if not str(sel_iid).startswith("area_") else None)

        msg = f"¿Está seguro de eliminar el área '{nom_area}'"
        if nom_cen and nom_cen != "-":
            msg += f" del centro '{nom_cen}'?"
        else:
            msg += "?"

        if messagebox.askyesno("Confirmar", msg):
            self.app.datos["areas"] = [
                a for a in self.app.datos.get("areas", [])
                if not ((a_id and str(a.get("id")) == str(a_id)) or (a.get("nombre") == nom_area and str(a.get("centro_salud_nombre") or "") == str(nom_cen or "")))
            ]
            guardar_cache_local_datos(self.app.datos)
            self.refrescar_datos()

            def _eliminar_area_db(aid, n, c, user):
                conn = obtener_conexion()
                if conn:
                    try:
                        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        if aid and str(aid) != "-":
                            cur.execute("SELECT * FROM areas WHERE id=%s;", (aid,))
                            r = cur.fetchone()
                            if r:
                                mover_a_papelera(cur, "areas", aid, dict(r), user)
                                cur.execute("DELETE FROM areas WHERE id=%s;", (aid,))
                        else:
                            cur.execute("DELETE FROM areas WHERE nombre=%s AND COALESCE(centro_salud_nombre, '') = COALESCE(%s, '');", (n, c or ""))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Error al eliminar área en BD: {e}")

            usuario_act = getattr(self.app, "usuario_actual", {}).get("nombre_usuario", "Sistema")
            ejecutar_en_segundo_plano(_eliminar_area_db, a_id, nom_area, nom_cen, usuario_act)
            messagebox.showinfo("Éxito", "Área eliminada correctamente.")

