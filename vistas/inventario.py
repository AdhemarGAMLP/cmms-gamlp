# vistas/inventario.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import json
import re
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera, calcular_proximos_mantenimientos
from estilos import *
from datetime import date, datetime

def simplificar_red(red_str):
    """
    Simplifica el nombre largo de la red de salud para que muestre 'Red 1', 'Red 2', etc.
    """
    if not red_str:
        return "-"
    s = str(red_str).strip()
    m = re.search(r'RED\s*([0-9]+)', s, re.IGNORECASE)
    if m:
        return f"Red {m.group(1)}"
    if "(" in s:
        s = s.split("(")[0].strip()
    return s.title() if s.isupper() else s

class VistaInventario(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(pady=(30, 10), padx=30, fill="x")
        ctk.CTkLabel(f_top, text="Inventario de Equipos", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")
        
        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace_add("write", lambda *args: self.refrescar_datos())
        
        # Caja de búsqueda con etiqueta explícita "🔍 Buscar:"
        f_search = ctk.CTkFrame(f_top, fg_color="transparent")
        f_search.pack(side="right")
        ctk.CTkLabel(f_search, text="🔍 Buscar:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(side="left", padx=5)
        e_buscar = ctk.CTkEntry(f_search, textvariable=self.busqueda_var, placeholder_text="Buscar Red, Centro, Servicio, Equipo, AF...", width=280, fg_color=C_CARD, border_color=C_BORDER, corner_radius=10)
        e_buscar.pack(side="left")

        # Barra de Ordenación/Filtros
        f_filtros = ctk.CTkFrame(self, fg_color="transparent")
        f_filtros.pack(pady=(5, 10), padx=30, fill="x")
        ctk.CTkLabel(f_filtros, text="Ordenar por:", font=ctk.CTkFont(weight="bold", size=12), text_color=C_TEXT).pack(side="left", padx=(0, 5))
        self.combo_ordenar = ctk.CTkComboBox(
            f_filtros, 
            values=["Red", "Centro de Salud", "Servicio", "Equipo (A-Z)", "Equipo (Z-A)", "Cod. AF", "Marca", "Modelo", "Fecha Registro", "Garantía"], 
            command=lambda e: self.refrescar_datos(), 
            width=190, 
            fg_color=C_CARD, 
            border_color=C_BORDER
        )
        self.combo_ordenar.pack(side="left")
        self.combo_ordenar.set("Red")

        marco_tabla = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        marco_tabla.pack(pady=10, padx=30, fill="both", expand=True)
        
        # Columnas solicitadas: Red, Centro de Salud, Servicio, Equipo, Marca, Modelo, Cod. AF
        cols = ("Red", "Centro de Salud", "Servicio", "Equipo", "Marca", "Modelo", "Cod. AF")
        f_tree_inv = ctk.CTkFrame(marco_tabla, fg_color="transparent")
        f_tree_inv.pack(pady=12, padx=12, fill="both", expand=True)
        self.tabla_inv = ttk.Treeview(f_tree_inv, columns=cols, show="headings")
        scrollbar_inv = ttk.Scrollbar(f_tree_inv, orient="vertical", command=self.tabla_inv.yview, style="Vertical.TScrollbar")
        self.tabla_inv.configure(yscrollcommand=scrollbar_inv.set)
        self.tabla_inv.tag_configure("Sin Garantia", background="#FFFFFF", foreground=C_TEXT)
        self.tabla_inv.tag_configure("Con Garantia", background="#F8FAFC", foreground=C_SUBTEXT)
        self.tabla_inv.tag_configure("Garantia Vencer", background="#FEF3C7", foreground="#B45309")
        
        widths = {
            "Red": 80,
            "Centro de Salud": 200,
            "Servicio": 140,
            "Equipo": 230,
            "Marca": 120,
            "Modelo": 120,
            "Cod. AF": 120
        }
        for c in cols:
            self.tabla_inv.heading(c, text=c, command=lambda _c=c: self.ordenar_columna(_c, False))
            self.tabla_inv.column(c, anchor="center", width=widths.get(c, 110))
        self.tabla_inv.pack(side="left", fill="both", expand=True)
        scrollbar_inv.pack(side="right", fill="y", padx=(5, 0))
        self.tabla_inv.bind("<Double-1>", lambda e: self.app.abrir_hoja_vida_click(e))

        f_bot = ctk.CTkFrame(self, fg_color="transparent")
        f_bot.pack(pady=(10, 25), padx=30, fill="x")
        self.btn_registrar = ctk.CTkButton(f_bot, text="✚ Registrar Equipo", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=42, command=self.registrar_equipo)
        self.btn_registrar.pack(side="left", expand=True, padx=8)
        self.btn_modificar = ctk.CTkButton(f_bot, text="✎ Modificar Ficha", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=42, command=self.modificar_equipo)
        self.btn_modificar.pack(side="left", expand=True, padx=8)
        self.btn_eliminar = ctk.CTkButton(f_bot, text="🗑 Eliminar Activo", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=42, command=self.eliminar_equipo)
        self.btn_eliminar.pack(side="left", expand=True, padx=8)

    def obtener_id_seleccionado(self):
        sel = self.tabla_inv.selection()
        if not sel:
            sel_focus = self.tabla_inv.focus()
            if sel_focus:
                sel = [sel_focus]
        if not sel:
            return None
        valores = self.tabla_inv.item(sel[0], "values")
        # Cod. AF está en el índice 6
        return valores[6] if len(valores) > 6 else (valores[0] if valores else None)

    def refrescar_datos(self):
        for i in self.tabla_inv.get_children(): 
            self.tabla_inv.delete(i)
        
        equipos = list(self.app.datos.get("equipos", []))
        
        # Filtro territorial / Sede activa
        contexto = getattr(self.app, "contexto_sede", None)
        if contexto and not contexto.get("es_global", True):
            cen_id = contexto.get("centro_salud_id")
            cen_nom = contexto.get("centro_salud")
            red_id = contexto.get("red_salud_id")
            red_nom = contexto.get("red_salud")

            if cen_id or (cen_nom and not str(cen_nom).startswith("[ Todos")):
                equipos = [eq for eq in equipos if 
                           (cen_id and eq.get("centro_salud_id") == cen_id) or 
                           (cen_nom and str(eq.get("centro_salud_nombre", "")).strip().lower() == str(cen_nom).strip().lower()) or
                           (cen_nom and str(eq.get("servicio", "")).strip().lower() == str(cen_nom).strip().lower())]
            elif red_id or (red_nom and not str(red_nom).startswith("[ Todas")):
                equipos = [eq for eq in equipos if 
                           (red_id and eq.get("red_salud_id") == red_id) or 
                           (red_nom and str(eq.get("red_salud_nombre", "")).strip().lower() == str(red_nom).strip().lower())]

        # Filtro de búsqueda
        t = self.busqueda_var.get().lower().strip()
        if t:
            equipos = [eq for eq in equipos if (
                t in str(eq.get("id", "")).lower() or 
                t in str(eq.get("nombre", "")).lower() or 
                t in str(eq.get("red_salud_nombre", "")).lower() or
                t in str(eq.get("centro_salud_nombre", "")).lower() or
                t in str(eq.get("servicio", "")).lower() or
                t in str(eq.get("area", "")).lower() or
                t in str(eq.get("marca", "")).lower() or
                t in str(eq.get("modelo", "")).lower() or
                t in str(eq.get("numero_serie", "")).lower()
            )]
            
        # Ordenación
        criterio = self.combo_ordenar.get() if hasattr(self, "combo_ordenar") else "Red"
        if criterio == "Red":
            equipos.sort(key=lambda x: (
                str(x.get("red_salud_nombre") or "ZZZ").lower(),
                str(x.get("centro_salud_nombre") or "ZZZ").lower(),
                str(x.get("servicio") or x.get("area") or "ZZZ").lower(),
                str(x.get("nombre") or "ZZZ").lower()
            ))
        elif criterio == "Centro de Salud":
            equipos.sort(key=lambda x: (
                str(x.get("centro_salud_nombre") or "ZZZ").lower(),
                str(x.get("servicio") or x.get("area") or "ZZZ").lower(),
                str(x.get("nombre") or "ZZZ").lower()
            ))
        elif criterio == "Servicio":
            equipos.sort(key=lambda x: (
                str(x.get("servicio") or x.get("area") or "ZZZ").lower(),
                str(x.get("nombre") or "ZZZ").lower()
            ))
        elif criterio == "Equipo (A-Z)":
            equipos.sort(key=lambda x: str(x.get("nombre", "")).lower())
        elif criterio == "Equipo (Z-A)":
            equipos.sort(key=lambda x: str(x.get("nombre", "")).lower(), reverse=True)
        elif criterio == "Cod. AF":
            def parse_id(x):
                val = str(x.get("id", ""))
                try: return (0, int(val))
                except: return (1, val.lower())
            equipos.sort(key=parse_id)
        elif criterio == "Marca":
            equipos.sort(key=lambda x: str(x.get("marca", "")).lower())
        elif criterio == "Modelo":
            equipos.sort(key=lambda x: str(x.get("modelo", "")).lower())
        elif criterio == "Fecha Registro":
            def get_fecha_reg(x):
                f = x.get("fecha_registro")
                if not f: return date.min
                if isinstance(f, str):
                    try: return datetime.strptime(f, "%Y-%m-%d").date()
                    except: return date.min
                return f
            equipos.sort(key=get_fecha_reg, reverse=True)
        elif criterio == "Garantía":
            equipos.sort(key=lambda x: x.get("garantia") == "Con Garantía", reverse=True)

        for eq in equipos:
            # 1. Determinar tag de garantía para colorear fila
            gar = eq.get("garantia", "Sin Garantía")
            f_venc = eq.get("fecha_vencimiento_garantia")
            tag_gar = "Sin Garantia"
            
            if gar == "Con Garantía" and f_venc:
                if isinstance(f_venc, str):
                    try: f_venc = datetime.strptime(f_venc, "%Y-%m-%d").date()
                    except: f_venc = None
                if f_venc:
                    dias = (f_venc - date.today()).days
                    if dias < 0:
                        tag_gar = "Sin Garantia"
                    elif dias <= 30:
                        tag_gar = "Garantia Vencer"
                    else:
                        tag_gar = "Con Garantia"

            # 2. Insertar en la tabla: cols = ("Red", "Centro de Salud", "Servicio", "Equipo", "Marca", "Modelo", "Cod. AF")
            red_corta = simplificar_red(eq.get("red_salud_nombre"))
            centro_txt = eq.get("centro_salud_nombre") or "-"
            servicio_txt = eq.get("servicio") or eq.get("area") or "-"
            
            self.tabla_inv.insert("", "end", values=(
                red_corta,
                centro_txt,
                servicio_txt,
                eq.get("nombre", ""),
                eq.get("marca") or "-",
                eq.get("modelo") or "-",
                eq.get("id", "")
            ), tags=(tag_gar,))

        # Control dinámico de botones según permisos
        can_add = self.app.tiene_permiso("Inventario", "agregar")
        can_edit = self.app.tiene_permiso("Inventario", "cambiar")
        can_del = self.app.tiene_permiso("Inventario", "eliminar")

        self.btn_registrar.configure(state="normal" if can_add else "disabled", fg_color=C_BLUE if can_add else C_BORDER, text_color="white" if can_add else C_SUBTEXT)
        self.btn_modificar.configure(state="normal" if can_edit else "disabled", fg_color=C_PURPLE if can_edit else C_BORDER, text_color="white" if can_edit else C_SUBTEXT)
        self.btn_eliminar.configure(state="normal" if can_del else "disabled", fg_color=C_RED if can_del else C_BORDER, text_color="white" if can_del else C_SUBTEXT)

    def ordenar_columna(self, col, reverse):
        datos = [(self.tabla_inv.set(k, col), k) for k in self.tabla_inv.get_children("")]
        datos.sort(reverse=reverse)
        for i, (val, k) in enumerate(datos): self.tabla_inv.move(k, "", i)
        self.tabla_inv.heading(col, command=lambda: self.ordenar_columna(col, not reverse))

    def registrar_equipo(self):
        if not self.app.tiene_permiso("Inventario", "agregar"):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para registrar nuevos equipos.")
            return
        if getattr(self.app, "modo_offline", False):
            from tkinter import messagebox
            messagebox.showwarning("Modo Sin Conexión", "La creación de nuevos equipos está deshabilitada en Modo Fuera de Línea.\n\nDebes conectarte a la red del Servidor Central para registrar nuevos activos.")
            return
        self.app.abrir_formulario_equipo()

    def modificar_equipo(self):
        from tkinter import messagebox
        if not self.app.tiene_permiso("Inventario", "cambiar"):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para modificar fichas técnicas de equipos.")
            return
        if getattr(self.app, "modo_offline", False):
            messagebox.showwarning("Modo Sin Conexión", "La modificación de fichas técnicas está deshabilitada en Modo Fuera de Línea (Solo Lectura).\n\nConéctate a la red del Servidor Central para guardar cambios.")
            return
        eq_id = self.obtener_id_seleccionado()
        if not eq_id: return
        eq = next((e for e in self.app.datos["equipos"] if str(e["id"]) == str(eq_id)), None)
        if eq: self.app.abrir_formulario_equipo(eq)

    def eliminar_equipo(self):
        from tkinter import messagebox
        if not self.app.tiene_permiso("Inventario", "eliminar"):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para eliminar o dar de baja equipos.")
            return
        if getattr(self.app, "modo_offline", False):
            messagebox.showwarning("Modo Sin Conexión", "La eliminación de equipos está deshabilitada en Modo Fuera de Línea.\n\nDebes estar conectado al Servidor Central.")
            return
        eq_id = self.obtener_id_seleccionado()
        if not eq_id: return
        if messagebox.askyesno("Confirmar Baja", f"¿Eliminar permanentemente el equipo {eq_id}?"):
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM equipos WHERE id = %s", (eq_id,))
                fila = cur.fetchone()
                if fila:
                    mover_a_papelera(cur, "equipos", eq_id, dict(fila), self.app.usuario_actual.get("nombre_usuario", "jefe"))
                cur.execute("DELETE FROM equipos WHERE id = %s", (eq_id,))
                conn.commit()
                cur.close(); conn.close()
                self.app.cargar_datos_memoria()
                self.refrescar_datos()
                messagebox.showinfo("Éxito", "Activo eliminado correctamente.")
            except Exception as e: messagebox.showerror("Error", str(e))