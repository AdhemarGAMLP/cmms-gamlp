# vistas/usuarios.py
import os
import shutil
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import psycopg2.extras
from database import obtener_conexion, mover_a_papelera
from auth import hash_password
from estilos import *

class VistaUsuarios(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.construir_ui()

    def construir_ui(self):
        ctk.CTkLabel(self, text="Gestión de Usuarios y Permisos", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(pady=30, padx=30)
        
        marco = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        marco.pack(padx=30, pady=10, fill="both", expand=True)
        
        cols = ("Usuario", "Nombre Completo", "Rol", "Eliminar Activos", "Modificar Fichas", "Firma / Sello")
        f_tree_users = ctk.CTkFrame(marco, fg_color="transparent")
        f_tree_users.pack(pady=12, padx=12, fill="both", expand=True)
        self.tabla_users = ttk.Treeview(f_tree_users, columns=cols, show="headings")
        scrollbar_users = ttk.Scrollbar(f_tree_users, orient="vertical", command=self.tabla_users.yview, style="Vertical.TScrollbar")
        self.tabla_users.configure(yscrollcommand=scrollbar_users.set)
        for c in cols:
            self.tabla_users.heading(c, text=c)
            self.tabla_users.column(c, anchor="center" if c != "Nombre Completo" else "w")
        self.tabla_users.pack(side="left", fill="both", expand=True)
        scrollbar_users.pack(side="right", fill="y", padx=(5, 0))
        
        f_bot = ctk.CTkFrame(self, fg_color="transparent")
        f_bot.pack(pady=(10, 25), padx=30, fill="x")
        
        # Solo el rol 'jefe' puede ver y operar estos botones
        ctk.CTkButton(f_bot, text="✚ Añadir Usuario", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_BLUE, hover_color=C_BLUE_HOVER, corner_radius=10, height=42, command=self.abrir_formulario_usuario).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot, text="✎ Modificar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, corner_radius=10, height=42, command=self.modificar_usuario).pack(side="left", expand=True, padx=8)
        ctk.CTkButton(f_bot, text="🗑 Eliminar", font=ctk.CTkFont(weight="bold", size=13), fg_color=C_RED, hover_color=C_RED_HOVER, corner_radius=10, height=42, command=self.eliminar_usuario).pack(side="left", expand=True, padx=8)


    def refrescar_datos(self):
        for i in self.tabla_users.get_children():
            self.tabla_users.delete(i)
        
        try:
            conn = obtener_conexion()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM usuarios ORDER BY rol ASC, nombre_completo ASC")
            filas = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            
            for r in filas:
                perm = r.get("permisos") or {}
                if isinstance(perm, str):
                    import json
                    try: perm = json.loads(perm)
                    except: perm = {}
                can_del = "Sí" if perm.get("can_delete") else "No"
                can_edt = "Sí" if perm.get("can_edit") else "No"
                firma_status = "Registrado" if r.get("sello_firma") else "No Registrado"
                
                self.tabla_users.insert("", "end", values=(r["nombre_usuario"], r["nombre_completo"], r["rol"].upper(), can_del, can_edt, firma_status))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios:\n{e}")

    def abrir_formulario_usuario(self, user_editar=None):
        vent = ctk.CTkToplevel(self)
        vent.title("Ficha de Usuario")
        vent.geometry("500x600")
        vent.transient(self)
        vent.grab_set()
        vent.configure(fg_color=C_BG)
        
        ctk.CTkLabel(vent, text="Registrar/Modificar Usuario", font=ctk.CTkFont(size=20, weight="bold"), text_color=C_TEXT).pack(pady=15)
        
        sf = ctk.CTkScrollableFrame(vent, fg_color=C_CARD, corner_radius=12)
        sf.pack(pady=5, padx=20, fill="both", expand=True)

        ctk.CTkLabel(sf, text="Nombre Completo:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        e_nombre = ctk.CTkEntry(sf, width=400)
        e_nombre.pack(pady=5)
        
        ctk.CTkLabel(sf, text="Nombre de Usuario / C.I.:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        e_user = ctk.CTkEntry(sf, width=400)
        e_user.pack(pady=5)
        
        ctk.CTkLabel(sf, text="Contraseña:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        e_pass = ctk.CTkEntry(sf, show="*", width=400)
        e_pass.pack(pady=5)
        
        ctk.CTkLabel(sf, text="Rol del Usuario:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        combo_rol = ctk.CTkComboBox(sf, values=["tecnico", "jefe"], width=400)
        combo_rol.pack(pady=5)
        
        # Sección Permisos
        ctk.CTkLabel(sf, text="Permisos Especiales:", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=20, pady=(15, 0))
        var_del = ctk.BooleanVar()
        var_edit = ctk.BooleanVar()
        chk_del = ctk.CTkCheckBox(sf, text="Permitir eliminar activos (Dar de Baja)", variable=var_del)
        chk_del.pack(pady=5, anchor="w", padx=30)
        chk_edit = ctk.CTkCheckBox(sf, text="Permitir editar fichas de equipos", variable=var_edit)
        chk_edit.pack(pady=5, anchor="w", padx=30)

        # Sección Firma/Sello Foto
        ctk.CTkLabel(sf, text="Sello y Firma Digital (Foto):", font=ctk.CTkFont(weight="bold"), text_color=C_TEXT).pack(anchor="w", padx=20, pady=(15, 0))
        ruta_firma_act = ctk.StringVar()
        lbl_firma_status = ctk.CTkLabel(sf, text="No seleccionada", text_color=C_SUBTEXT, font=ctk.CTkFont(slant="italic"))
        
        def buscar_firma():
            path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
            if path:
                ruta_firma_act.set(path)
                lbl_firma_status.configure(text=f"Seleccionada: {os.path.basename(path)}", text_color=C_GREEN_HOVER)
                
        ctk.CTkButton(sf, text="📁 Seleccionar Firma/Sello", fg_color=C_BG, text_color=C_TEXT, command=buscar_firma, width=400).pack(pady=5)
        lbl_firma_status.pack(pady=2)

        # Cargar datos si se está editando
        if user_editar:
            e_nombre.insert(0, user_editar.get("nombre_completo", ""))
            e_user.insert(0, user_editar.get("nombre_usuario", ""))
            e_user.configure(state="disabled") # No permitir cambiar el username una vez creado
            combo_rol.set(user_editar.get("rol", "tecnico"))
            
            p = user_editar.get("permisos") or {}
            if isinstance(p, str):
                import json
                try: p = json.loads(p)
                except: p = {}
            var_del.set(p.get("can_delete", False))
            var_edit.set(p.get("can_edit", False))
            
            if user_editar.get("sello_firma"):
                ruta_firma_act.set(user_editar["sello_firma"])
                lbl_firma_status.configure(text="Firma registrada previamente", text_color=C_BLUE)

        def guardar_usuario():
            nom = e_nombre.get().strip()
            usr = e_user.get().strip()
            psw = e_pass.get().strip()
            rol = combo_rol.get()
            
            if not nom or not usr:
                messagebox.showerror("Error", "Nombre Completo y Nombre de Usuario son campos obligatorios.")
                return
                
            try:
                conn = obtener_conexion()
                cur = conn.cursor()
                
                # Manejar guardado de la foto del sello/firma
                destino_firma = user_editar.get("sello_firma", "") if user_editar else ""
                origen_firma = ruta_firma_act.get()
                if origen_firma and origen_firma != destino_firma and os.path.exists(origen_firma):
                    dir_firmas = os.path.join(self.app.datos.get("carpeta_datos_base", os.path.expanduser("~")), "Fotos_Firmas")
                    os.makedirs(dir_firmas, exist_ok=True)
                    extension = os.path.splitext(origen_firma)[1]
                    destino_firma = os.path.join(dir_firmas, f"firma_{usr}{extension}")
                    shutil.copy2(origen_firma, destino_firma)
                
                permisos_dict = {"can_delete": var_del.get(), "can_edit": var_edit.get()}
                permisos_json = psycopg2.extras.Json(permisos_dict)

                if user_editar:
                    # Modificar usuario
                    if psw:
                        h_pwd = hash_password(psw)
                        cur.execute("""
                            UPDATE usuarios 
                            SET nombre_completo=%s, password_hash=%s, rol=%s, permisos=%s, sello_firma=%s 
                            WHERE nombre_usuario=%s
                        """, (nom, h_pwd, rol, permisos_json, destino_firma, usr))
                    else:
                        cur.execute("""
                            UPDATE usuarios 
                            SET nombre_completo=%s, rol=%s, permisos=%s, sello_firma=%s 
                            WHERE nombre_usuario=%s
                        """, (nom, rol, permisos_json, destino_firma, usr))
                else:
                    # Crear nuevo usuario
                    if not psw:
                        messagebox.showerror("Error", "La contraseña es obligatoria para un usuario nuevo.")
                        cur.close(); conn.close()
                        return
                    
                    # Verificar duplicado
                    cur.execute("SELECT COUNT(*) FROM usuarios WHERE nombre_usuario=%s", (usr,))
                    if cur.fetchone()[0] > 0:
                        messagebox.showerror("Error", "El nombre de usuario ya está registrado.")
                        cur.close(); conn.close()
                        return
                        
                    h_pwd = hash_password(psw)
                    cur.execute("""
                        INSERT INTO usuarios (nombre_usuario, nombre_completo, password_hash, rol, permisos, sello_firma) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (usr, nom, h_pwd, rol, permisos_json, destino_firma))

                conn.commit()
                cur.close()
                conn.close()
                self.refrescar_datos()
                
                # Si el usuario modificado es el mismo que está logueado, refrescar la sesión en memoria
                if self.app.usuario_actual.get("nombre_usuario") == usr:
                    try:
                        from database import obtener_conexion as _oc
                        import psycopg2.extras as _pge
                        _c = _oc()
                        if _c:
                            _cur = _c.cursor(cursor_factory=_pge.DictCursor)
                            _cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (usr,))
                            _row = _cur.fetchone()
                            _cur.close(); _c.close()
                            if _row:
                                self.app.usuario_actual = dict(_row)
                    except:
                        pass
                
                vent.destroy()
                messagebox.showinfo("Éxito", "Usuario guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al guardar usuario:\n{e}")

        ctk.CTkButton(vent, text="Guardar Cambios", fg_color=C_BLUE, hover_color=C_BLUE_HOVER, height=45, font=ctk.CTkFont(weight="bold"), command=guardar_usuario).pack(pady=20, padx=20, fill="x")

    def modificar_usuario(self):
        sel = self.tabla_users.focus()
        if not sel:
            messagebox.showinfo("Selección", "Por favor, selecciona un usuario de la lista.")
            return
        valores = self.tabla_users.item(sel, "values")
        
        try:
            conn = obtener_conexion()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (valores[0],))
            usr = cur.fetchone()
            cur.close()
            conn.close()
            if usr:
                self.abrir_formulario_usuario(dict(usr))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_usuario(self):
        sel = self.tabla_users.focus()
        if not sel:
            messagebox.showinfo("Selección", "Por favor, selecciona un usuario de la lista.")
            return
        valores = self.tabla_users.item(sel, "values")
        
        if valores[0] == "admin" or valores[0] == self.app.usuario_actual.get("nombre_usuario"):
            messagebox.showerror("Error", "No puedes eliminar el usuario Administrador Maestro ni tu propio usuario activo.")
            return
            
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar permanentemente al usuario '{valores[1]}'?"):
            try:
                conn = obtener_conexion()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (valores[0],))
                usr = cur.fetchone()
                if usr:
                    mover_a_papelera(cur, "usuarios", str(usr["id"]), dict(usr), self.app.usuario_actual.get("nombre_usuario", "jefe"))
                    
                cur.execute("DELETE FROM usuarios WHERE nombre_usuario = %s", (valores[0],))
                conn.commit()
                cur.close()
                conn.close()
                self.tabla_users.delete(sel)
                messagebox.showinfo("Éxito", "Usuario eliminado de la base de datos.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{e}")
