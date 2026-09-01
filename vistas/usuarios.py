# vistas/usuarios.py
import os
import shutil
import json
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera
from auth import hash_password
from estilos import *

MODULOS_SISTEMA = [
    ("Inventario", "📦 Inventario de Equipos"),
    ("Catalogo", "🩺 Equipos Médicos (Catálogo)"),
    ("Repuestos", "🔧 Gestión de Repuestos"),
    ("Cronograma", "📅 Cronograma y Calendario"),
    ("Historial", "📋 Mantenimientos e Intervenciones"),
    ("Analisis", "📊 Análisis Estadístico y Censo"),
    ("Areas", "📍 Áreas y Unidades Clínicas"),
    ("Sedes", "🏥 Sedes y Centros de Salud"),
    ("Respaldos", "💾 Respaldos y Base de Datos"),
    ("Usuarios", "👥 Gestión de Usuarios y Permisos")
]

ROLES_DISPONIBLES = ["Administrador", "Técnico", "Relevamiento", "Visita"]

def obtener_permisos_por_defecto_rol(rol_nombre):
    rol_clean = str(rol_nombre).strip().lower()
    permisos = {}

    for mod_key, _ in MODULOS_SISTEMA:
        if rol_clean in ["administrador", "admin", "jefe"]:
            permisos[mod_key] = {"ver": True, "agregar": True, "cambiar": True, "eliminar": True}
        elif rol_clean == "técnico" or rol_clean == "tecnico":
            if mod_key in ["Respaldos", "Usuarios"]:
                permisos[mod_key] = {"ver": False, "agregar": False, "cambiar": False, "eliminar": False}
            elif mod_key in ["Analisis"]:
                permisos[mod_key] = {"ver": True, "agregar": False, "cambiar": False, "eliminar": False}
            else:
                permisos[mod_key] = {"ver": True, "agregar": True, "cambiar": True, "eliminar": False}
        elif rol_clean == "relevamiento":
            if mod_key in ["Inventario", "Catalogo", "Areas", "Sedes"]:
                permisos[mod_key] = {"ver": True, "agregar": True, "cambiar": True, "eliminar": False}
            elif mod_key in ["Cronograma", "Analisis"]:
                permisos[mod_key] = {"ver": True, "agregar": False, "cambiar": False, "eliminar": False}
            else:
                permisos[mod_key] = {"ver": False, "agregar": False, "cambiar": False, "eliminar": False}
        elif rol_clean == "visita":
            if mod_key in ["Respaldos", "Usuarios"]:
                permisos[mod_key] = {"ver": False, "agregar": False, "cambiar": False, "eliminar": False}
            else:
                permisos[mod_key] = {"ver": True, "agregar": False, "cambiar": False, "eliminar": False}
        else:
            permisos[mod_key] = {"ver": True, "agregar": False, "cambiar": False, "eliminar": False}

    # Compatibilidad con claves legacy
    permisos["can_delete"] = (rol_clean in ["administrador", "admin", "jefe"])
    permisos["can_edit"] = (rol_clean != "visita")
    return permisos


class VistaUsuarios(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        # Cabecera
        f_cab = ctk.CTkFrame(self, fg_color="transparent")
        f_cab.pack(pady=(20, 10), padx=30, fill="x")
        
        ctk.CTkLabel(
            f_cab, 
            text="Gestión de Usuarios, Roles y Permisos", 
            font=ctk.CTkFont(size=26, weight="bold"), 
            text_color=C_TEXT
        ).pack(side="left")

        # Tarjeta principal de la tabla
        marco = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        marco.pack(padx=25, pady=(5, 15), fill="both", expand=True)

        cols = ("C.I. / Usuario", "Nombre Completo", "Rol", "Pestañas Habilitadas", "Permisos Especiales", "Sello Institucional", "Estado")
        f_tree_users = ctk.CTkFrame(marco, fg_color="transparent")
        f_tree_users.pack(pady=12, padx=12, fill="both", expand=True)
        
        self.tabla_users = ttk.Treeview(f_tree_users, columns=cols, show="headings", selectmode="browse")
        scrollbar_users = ttk.Scrollbar(f_tree_users, orient="vertical", command=self.tabla_users.yview, style="Vertical.TScrollbar")
        self.tabla_users.configure(yscrollcommand=scrollbar_users.set)

        col_w = {
            "C.I. / Usuario": 110,
            "Nombre Completo": 190,
            "Rol": 110,
            "Pestañas Habilitadas": 140,
            "Permisos Especiales": 150,
            "Sello Institucional": 130,
            "Estado": 80
        }
        for c in cols:
            self.tabla_users.heading(c, text=c)
            self.tabla_users.column(c, anchor="center" if c not in ["Nombre Completo", "Permisos Especiales"] else "w", width=col_w.get(c, 100))

        self.tabla_users.pack(side="left", fill="both", expand=True)
        scrollbar_users.pack(side="right", fill="y", padx=(4, 0))
        self.tabla_users.bind("<Double-1>", lambda e: self.modificar_usuario())

        # Botones de Acción Inferiores
        f_bot = ctk.CTkFrame(self, fg_color="transparent")
        f_bot.pack(pady=(0, 20), padx=25, fill="x")

        ctk.CTkButton(
            f_bot, 
            text="✚ Añadir Usuario", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            corner_radius=10, 
            height=40, 
            command=lambda: self.abrir_formulario_usuario(None)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_bot, 
            text="✎ Modificar Permisos y Datos", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_PURPLE, 
            hover_color=C_PURPLE_HOVER, 
            corner_radius=10, 
            height=40, 
            command=self.modificar_usuario
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_bot, 
            text="🗑 Desactivar / Eliminar Usuario", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_RED, 
            hover_color=C_RED_HOVER, 
            corner_radius=10, 
            height=40, 
            command=self.eliminar_usuario
        ).pack(side="left")

    def formatear_rol_display(self, rol_str):
        r = str(rol_str).strip().lower()
        if r in ["jefe", "admin", "administrador"]:
            return "Administrador"
        elif r in ["tecnico", "técnico"]:
            return "Técnico"
        elif r == "relevamiento":
            return "Relevamiento"
        elif r == "visita":
            return "Visita"
        return r.title()

    def refrescar_datos(self):
        for i in self.tabla_users.get_children():
            self.tabla_users.delete(i)

        try:
            conn = obtener_conexion()
            if not conn:
                return
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM usuarios ORDER BY CASE WHEN rol='jefe' OR rol='Administrador' THEN 0 ELSE 1 END, nombre_completo ASC")
            filas = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()

            for r in filas:
                perm = r.get("permisos") or {}
                if isinstance(perm, str):
                    try: perm = json.loads(perm)
                    except: perm = {}

                # Conteo de pestañas habilitadas
                mods_habilitados = 0
                for mod_k, _ in MODULOS_SISTEMA:
                    if isinstance(perm.get(mod_k), dict):
                        if perm[mod_k].get("ver", False):
                            mods_habilitados += 1
                    else:
                        # Fallback por rol
                        rol_cl = str(r.get("rol", "")).lower()
                        if rol_cl in ["jefe", "administrador", "admin"]:
                            mods_habilitados += 1
                        elif rol_cl == "tecnico" and mod_k not in ["Respaldos", "Usuarios"]:
                            mods_habilitados += 1

                pestañas_str = f"{mods_habilitados} / {len(MODULOS_SISTEMA)} módulos"
                if mods_habilitados == len(MODULOS_SISTEMA):
                    pestañas_str = "Acceso Total (10)"

                # Resumen de permisos de acción
                acciones = []
                if r.get("rol") in ["jefe", "Administrador"]:
                    acciones_str = "Total (Agregar, Cambiar, Eliminar)"
                else:
                    can_del = perm.get("can_delete", False)
                    can_edt = perm.get("can_edit", True)
                    if can_edt: acciones.append("Agregar/Cambiar")
                    if can_del: acciones.append("Eliminar")
                    acciones_str = ", ".join(acciones) if acciones else "Solo Lectura"

                sello_status = "✅ Registrado" if r.get("sello_firma") else "❌ No Registrado"
                estado_str = "Activo" if r.get("activo", True) else "Inactivo"

                self.tabla_users.insert(
                    "", 
                    "end", 
                    values=(
                        r["nombre_usuario"], 
                        r["nombre_completo"], 
                        self.formatear_rol_display(r["rol"]), 
                        pestañas_str, 
                        acciones_str, 
                        sello_status,
                        estado_str
                    )
                )
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudieron cargar los usuarios:\n{e}")

    # ========================================================
    # FORMULARIO MODAL: CREAR / MODIFICAR USUARIO Y PERMISOS
    # ========================================================
    def abrir_formulario_usuario(self, user_editar=None):
        vent = ctk.CTkToplevel(self)
        vent.title("Modificar Usuario y Permisos" if user_editar else "Registrar Nuevo Usuario")
        vent.geometry("700x720")
        vent.minsize(620, 600)
        vent.transient(self.app)
        vent.grab_set()
        vent.configure(fg_color=C_BG)

        # Cabecera
        f_top = ctk.CTkFrame(vent, fg_color="transparent")
        f_top.pack(fill="x", padx=24, pady=(16, 8))
        ctk.CTkLabel(
            f_top, 
            text="Ficha de Usuario y Permisos por Pestaña", 
            font=ctk.CTkFont(size=20, weight="bold"), 
            text_color=C_TEXT
        ).pack(anchor="w")
        ctk.CTkLabel(
            f_top, 
            text="Configure los datos de acceso, rol territorial y matriz de permisos por módulo.", 
            font=ctk.CTkFont(size=12), 
            text_color=C_SUBTEXT
        ).pack(anchor="w", pady=(2, 0))

        # Contenedor Scrollable
        sf = ctk.CTkScrollableFrame(vent, fg_color=C_CARD, corner_radius=14, border_width=1, border_color=C_BORDER)
        sf.pack(pady=4, padx=20, fill="both", expand=True)

        # ----------------------------------------------------
        # DATOS PERSONALES Y DE ACCESO
        # ----------------------------------------------------
        f_sec1 = ctk.CTkFrame(sf, fg_color="transparent")
        f_sec1.pack(fill="x", padx=16, pady=10)

        f_grid = ctk.CTkFrame(f_sec1, fg_color="transparent")
        f_grid.pack(fill="x")
        f_grid.columnconfigure(0, weight=1)
        f_grid.columnconfigure(1, weight=1)

        # 1. Nombre Completo
        f_c1 = ctk.CTkFrame(f_grid, fg_color="transparent")
        f_c1.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="nsew")
        ctk.CTkLabel(f_c1, text="Nombre Completo *:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(anchor="w")
        e_nombre = ctk.CTkEntry(f_c1, placeholder_text="ej. Lic. Adhemar Santos Medina", height=34)
        e_nombre.pack(fill="x", pady=(2, 0))

        # 2. C.I. (Cédula de Identidad / Usuario)
        f_c2 = ctk.CTkFrame(f_grid, fg_color="transparent")
        f_c2.grid(row=0, column=1, padx=(10, 0), pady=4, sticky="nsew")
        ctk.CTkLabel(f_c2, text="C.I. (Cédula de Identidad / Usuario) *:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(anchor="w")
        e_ci = ctk.CTkEntry(f_c2, placeholder_text="ej. 10955499", height=34)
        e_ci.pack(fill="x", pady=(2, 0))

        # 3. Contraseña
        f_c3 = ctk.CTkFrame(f_grid, fg_color="transparent")
        f_c3.grid(row=1, column=0, padx=(0, 10), pady=8, sticky="nsew")
        pass_lbl_txt = "Contraseña (dejar en blanco para no cambiar):" if user_editar else "Contraseña *:"
        ctk.CTkLabel(f_c3, text=pass_lbl_txt, font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(anchor="w")
        e_pass = ctk.CTkEntry(f_c3, show="*", placeholder_text="Contraseña segura", height=34)
        e_pass.pack(fill="x", pady=(2, 0))

        # 4. Rol de Usuario
        f_c4 = ctk.CTkFrame(f_grid, fg_color="transparent")
        f_c4.grid(row=1, column=1, padx=(10, 0), pady=8, sticky="nsew")
        ctk.CTkLabel(f_c4, text="Rol de Usuario *:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(anchor="w")
        combo_rol = ctk.CTkComboBox(f_c4, values=ROLES_DISPONIBLES, height=34)
        combo_rol.pack(fill="x", pady=(2, 0))

        # ----------------------------------------------------
        # SECCIÓN SELLO INSTITUCIONAL
        # ----------------------------------------------------
        f_sello = ctk.CTkFrame(sf, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color=C_BORDER)
        f_sello.pack(fill="x", padx=16, pady=10)

        f_sello_in = ctk.CTkFrame(f_sello, fg_color="transparent")
        f_sello_in.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(f_sello_in, text="🏷️ Sello Institucional:", font=ctk.CTkFont(weight="bold", size=13), text_color=C_TEXT).pack(side="left", padx=(0, 10))
        
        ruta_sello_act = ctk.StringVar()
        lbl_sello_status = ctk.CTkLabel(f_sello_in, text="Sin Sello cargado", text_color=C_SUBTEXT, font=ctk.CTkFont(slant="italic", size=12))
        
        def buscar_sello():
            path = filedialog.askopenfilename(filetypes=[("Imágenes de Sello", "*.png;*.jpg;*.jpeg")])
            if path:
                ruta_sello_act.set(path)
                lbl_sello_status.configure(text=f"Seleccionado: {os.path.basename(path)}", text_color=C_GREEN_HOVER)

        def quitar_sello():
            ruta_sello_act.set("")
            lbl_sello_status.configure(text="Sin Sello", text_color=C_SUBTEXT)

        ctk.CTkButton(f_sello_in, text="📁 Subir Sello", font=ctk.CTkFont(weight="bold", size=11), fg_color=C_BLUE, height=28, command=buscar_sello).pack(side="left", padx=4)
        ctk.CTkButton(f_sello_in, text="✖ Quitar", font=ctk.CTkFont(size=11), fg_color="#E2E8F0", text_color=C_TEXT, hover_color="#CBD5E1", height=28, command=quitar_sello).pack(side="left", padx=4)
        lbl_sello_status.pack(side="left", padx=8)

        # ----------------------------------------------------
        # MATRIZ DE PERMISOS POR PESTAÑA
        # ----------------------------------------------------
        f_perm = ctk.CTkFrame(sf, fg_color="transparent")
        f_perm.pack(fill="x", padx=16, pady=(10, 16))

        f_perm_header = ctk.CTkFrame(f_perm, fg_color="transparent")
        f_perm_header.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            f_perm_header, 
            text="🛡️ Permisos por Pestaña / Módulo:", 
            font=ctk.CTkFont(size=15, weight="bold"), 
            text_color=C_TEXT
        ).pack(side="left")

        btn_preset = ctk.CTkButton(
            f_perm_header, 
            text="⚡ Aplicar Valores del Rol", 
            font=ctk.CTkFont(size=11, weight="bold"), 
            fg_color="#EFF6FF", 
            text_color=C_BLUE, 
            hover_color="#DBEAFE", 
            height=26,
            corner_radius=6,
            command=lambda: aplicar_defaults_rol_en_ui(combo_rol.get())
        )
        btn_preset.pack(side="right")

        # Contenedor Tabla de Permisos
        f_matriz = ctk.CTkFrame(f_perm, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color=C_BORDER)
        f_matriz.pack(fill="x")

        # Cabecera de columnas de la matriz
        f_m_hdr = ctk.CTkFrame(f_matriz, fg_color="#F1F5F9", height=32, corner_radius=8)
        f_m_hdr.pack(fill="x", padx=4, pady=4)
        f_m_hdr.columnconfigure(0, weight=4)
        f_m_hdr.columnconfigure(1, weight=2)
        f_m_hdr.columnconfigure(2, weight=2)
        f_m_hdr.columnconfigure(3, weight=2)
        f_m_hdr.columnconfigure(4, weight=2)

        ctk.CTkLabel(f_m_hdr, text="Pestaña / Módulo", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(f_m_hdr, text="👁️ Ver / Acceso", font=ctk.CTkFont(weight="bold", size=11), text_color=C_BLUE).grid(row=0, column=1)
        ctk.CTkLabel(f_m_hdr, text="➕ Agregar", font=ctk.CTkFont(weight="bold", size=11), text_color=C_GREEN).grid(row=0, column=2)
        ctk.CTkLabel(f_m_hdr, text="✎ Cambiar", font=ctk.CTkFont(weight="bold", size=11), text_color=C_PURPLE).grid(row=0, column=3)
        ctk.CTkLabel(f_m_hdr, text="🗑️ Eliminar", font=ctk.CTkFont(weight="bold", size=11), text_color=C_RED).grid(row=0, column=4)

        # Diccionario de variables de control de checkboxes
        matriz_vars = {}

        for idx, (mod_k, mod_lbl) in enumerate(MODULOS_SISTEMA):
            f_row = ctk.CTkFrame(f_matriz, fg_color="white" if idx % 2 == 0 else "#F8FAFC", corner_radius=6)
            f_row.pack(fill="x", padx=4, pady=2)
            f_row.columnconfigure(0, weight=4)
            f_row.columnconfigure(1, weight=2)
            f_row.columnconfigure(2, weight=2)
            f_row.columnconfigure(3, weight=2)
            f_row.columnconfigure(4, weight=2)

            v_ver = ctk.BooleanVar(value=True)
            v_add = ctk.BooleanVar(value=True)
            v_edit = ctk.BooleanVar(value=True)
            v_del = ctk.BooleanVar(value=False)

            matriz_vars[mod_k] = {
                "ver": v_ver,
                "agregar": v_add,
                "cambiar": v_edit,
                "eliminar": v_del
            }

            ctk.CTkLabel(f_row, text=mod_lbl, font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).grid(row=0, column=0, sticky="w", padx=10, pady=4)

            # Si desmarca "Ver", desmarcar y bloquear las demás
            def _al_cambiar_ver(k=mod_k):
                if not matriz_vars[k]["ver"].get():
                    matriz_vars[k]["agregar"].set(False)
                    matriz_vars[k]["cambiar"].set(False)
                    matriz_vars[k]["eliminar"].set(False)

            chk_v = ctk.CTkCheckBox(f_row, text="", variable=v_ver, width=20, command=lambda k=mod_k: _al_cambiar_ver(k))
            chk_v.grid(row=0, column=1)

            chk_a = ctk.CTkCheckBox(f_row, text="", variable=v_add, width=20)
            chk_a.grid(row=0, column=2)

            chk_e = ctk.CTkCheckBox(f_row, text="", variable=v_edit, width=20)
            chk_e.grid(row=0, column=3)

            chk_d = ctk.CTkCheckBox(f_row, text="", variable=v_del, width=20)
            chk_d.grid(row=0, column=4)

        def aplicar_defaults_rol_en_ui(rol_sel):
            defaults = obtener_permisos_por_defecto_rol(rol_sel)
            for mod_k, _ in MODULOS_SISTEMA:
                p_mod = defaults.get(mod_k, {"ver": True, "agregar": False, "cambiar": False, "eliminar": False})
                matriz_vars[mod_k]["ver"].set(p_mod.get("ver", True))
                matriz_vars[mod_k]["agregar"].set(p_mod.get("agregar", False))
                matriz_vars[mod_k]["cambiar"].set(p_mod.get("cambiar", False))
                matriz_vars[mod_k]["eliminar"].set(p_mod.get("eliminar", False))

        combo_rol.configure(command=lambda r: aplicar_defaults_rol_en_ui(r))

        # Cargar datos si se está editando
        if user_editar:
            e_nombre.insert(0, user_editar.get("nombre_completo", ""))
            e_ci.insert(0, user_editar.get("nombre_usuario", ""))
            e_ci.configure(state="disabled")
            
            rol_actual_db = self.formatear_rol_display(user_editar.get("rol", "Técnico"))
            combo_rol.set(rol_actual_db)

            if user_editar.get("sello_firma"):
                ruta_sello_act.set(user_editar["sello_firma"])
                lbl_sello_status.configure(text=f"Sello: {os.path.basename(user_editar['sello_firma'])}", text_color=C_BLUE)

            # Cargar permisos existentes
            p_exist = user_editar.get("permisos") or {}
            if isinstance(p_exist, str):
                try: p_exist = json.loads(p_exist)
                except: p_exist = {}

            if any(k in p_exist for k, _ in MODULOS_SISTEMA):
                for mod_k, _ in MODULOS_SISTEMA:
                    if mod_k in p_exist and isinstance(p_exist[mod_k], dict):
                        matriz_vars[mod_k]["ver"].set(p_exist[mod_k].get("ver", True))
                        matriz_vars[mod_k]["agregar"].set(p_exist[mod_k].get("agregar", False))
                        matriz_vars[mod_k]["cambiar"].set(p_exist[mod_k].get("cambiar", False))
                        matriz_vars[mod_k]["eliminar"].set(p_exist[mod_k].get("eliminar", False))
            else:
                # Aplicar defaults si venía de formato antiguo
                aplicar_defaults_rol_en_ui(rol_actual_db)
        else:
            combo_rol.set("Técnico")
            aplicar_defaults_rol_en_ui("Técnico")

        def guardar_usuario():
            nom = e_nombre.get().strip()
            ci_val = e_ci.get().strip()
            psw = e_pass.get().strip()
            rol_sel = combo_rol.get().strip()

            if not nom or not ci_val:
                messagebox.showerror("Campos Requeridos", "El Nombre Completo y el C.I. son campos obligatorios.")
                return

            if not user_editar and not psw:
                messagebox.showerror("Contraseña Requerida", "Debe asignar una contraseña para el nuevo usuario.")
                return

            # Construir JSON de permisos
            permisos_dict = {}
            can_del_global = False
            can_edt_global = False

            for mod_k, _ in MODULOS_SISTEMA:
                v_v = matriz_vars[mod_k]["ver"].get()
                v_a = matriz_vars[mod_k]["agregar"].get() if v_v else False
                v_c = matriz_vars[mod_k]["cambiar"].get() if v_v else False
                v_e = matriz_vars[mod_k]["eliminar"].get() if v_v else False

                permisos_dict[mod_k] = {
                    "ver": v_v,
                    "agregar": v_a,
                    "cambiar": v_c,
                    "eliminar": v_e
                }
                if v_e: can_del_global = True
                if v_a or v_c: can_edt_global = True

            permisos_dict["can_delete"] = can_del_global
            permisos_dict["can_edit"] = can_edt_global
            permisos_json = psycopg2.extras.Json(permisos_dict)

            # Manejar guardado de la foto del Sello
            destino_sello = user_editar.get("sello_firma", "") if user_editar else ""
            origen_sello = ruta_sello_act.get()

            if origen_sello and origen_sello != destino_sello and os.path.exists(origen_sello):
                dir_sellos = os.path.join(self.app.datos.get("carpeta_datos_base", os.path.expanduser("~")), "Fotos_Sellos")
                os.makedirs(dir_sellos, exist_ok=True)
                extension = os.path.splitext(origen_sello)[1]
                destino_sello = os.path.join(dir_sellos, f"sello_{ci_val}{extension}")
                shutil.copy2(origen_sello, destino_sello)
            elif not origen_sello:
                destino_sello = ""

            # Rol normalizado para la BD
            rol_db = "jefe" if rol_sel == "Administrador" else rol_sel.lower()

            try:
                conn = obtener_conexion()
                if not conn:
                    messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
                    return
                cur = conn.cursor()

                if user_editar:
                    if psw:
                        h_pwd = hash_password(psw)
                        cur.execute("""
                            UPDATE usuarios 
                            SET nombre_completo = %s, password_hash = %s, rol = %s, permisos = %s, sello_firma = %s
                            WHERE nombre_usuario = %s;
                        """, (nom, h_pwd, rol_db, permisos_json, destino_sello, ci_val))
                    else:
                        cur.execute("""
                            UPDATE usuarios 
                            SET nombre_completo = %s, rol = %s, permisos = %s, sello_firma = %s
                            WHERE nombre_usuario = %s;
                        """, (nom, rol_db, permisos_json, destino_sello, ci_val))
                else:
                    cur.execute("SELECT COUNT(*) FROM usuarios WHERE nombre_usuario = %s;", (ci_val,))
                    if cur.fetchone()[0] > 0:
                        messagebox.showerror("C.I. Duplicado", f"El usuario con C.I. '{ci_val}' ya existe en el sistema.")
                        cur.close(); conn.close()
                        return

                    h_pwd = hash_password(psw)
                    cur.execute("""
                        INSERT INTO usuarios (nombre_usuario, nombre_completo, password_hash, rol, permisos, sello_firma, activo)
                        VALUES (%s, %s, %s, %s, %s, %s, TRUE);
                    """, (ci_val, nom, h_pwd, rol_db, permisos_json, destino_sello))

                conn.commit()
                cur.close()
                conn.close()

                # Si el usuario editado es el actual logueado, actualizar en caliente
                if self.app.usuario_actual.get("nombre_usuario") == ci_val:
                    self.app.usuario_actual["nombre_completo"] = nom
                    self.app.usuario_actual["rol"] = rol_db
                    self.app.usuario_actual["permisos"] = permisos_dict
                    self.app.usuario_actual["sello_firma"] = destino_sello

                vent.destroy()
                self.refrescar_datos()
                messagebox.showinfo("Éxito", f"Usuario '{nom}' (C.I. {ci_val}) guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar el usuario:\n{e}")

        # Botones inferiores del modal
        f_bot_v = ctk.CTkFrame(vent, fg_color="transparent")
        f_bot_v.pack(fill="x", padx=24, pady=(8, 16))

        ctk.CTkButton(
            f_bot_v, 
            text="💾 Guardar Cambios y Permisos", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_BLUE, 
            hover_color=C_BLUE_HOVER, 
            height=40, 
            corner_radius=8, 
            command=guardar_usuario
        ).pack(side="left", expand=True, padx=(0, 6))

        ctk.CTkButton(
            f_bot_v, 
            text="Cancelar", 
            font=ctk.CTkFont(weight="bold", size=13), 
            fg_color=C_CARD, 
            text_color=C_TEXT, 
            hover_color=C_BORDER, 
            height=40, 
            corner_radius=8, 
            command=vent.destroy
        ).pack(side="right", expand=True, padx=(6, 0))

    def modificar_usuario(self):
        sel = self.tabla_users.selection() or ([self.tabla_users.focus()] if self.tabla_users.focus() else [])
        if not sel:
            messagebox.showinfo("Selección Requerida", "Por favor seleccione un usuario de la tabla para modificar.")
            return
        valores = self.tabla_users.item(sel[0], "values")
        ci_sel = valores[0]

        try:
            conn = obtener_conexion()
            if not conn:
                return
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s;", (ci_sel,))
            usr = cur.fetchone()
            cur.close()
            conn.close()
            if usr:
                self.abrir_formulario_usuario(dict(usr))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_usuario(self):
        sel = self.tabla_users.selection() or ([self.tabla_users.focus()] if self.tabla_users.focus() else [])
        if not sel:
            messagebox.showinfo("Selección Requerida", "Por favor seleccione un usuario para desactivar.")
            return
        valores = self.tabla_users.item(sel[0], "values")
        ci_sel = valores[0]
        nom_sel = valores[1]

        if ci_sel == "admin" or ci_sel == self.app.usuario_actual.get("nombre_usuario"):
            messagebox.showwarning("Acción No Permitida", "No puede eliminar la cuenta de Administrador principal ni su propia sesión activa.")
            return

        conf = messagebox.askyesno("Confirmar Desactivación", f"¿Está seguro de desactivar al usuario '{nom_sel}' (C.I. {ci_sel})?")
        if conf:
            try:
                conn = obtener_conexion()
                if not conn:
                    return
                cur = conn.cursor()
                cur.execute("UPDATE usuarios SET activo = FALSE WHERE nombre_usuario = %s;", (ci_sel,))
                conn.commit()
                cur.close()
                conn.close()
                self.refrescar_datos()
                messagebox.showinfo("Desactivado", f"El usuario '{nom_sel}' ha sido desactivado.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
