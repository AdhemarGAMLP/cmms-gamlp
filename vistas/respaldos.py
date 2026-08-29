# vistas/respaldos.py
import os
import json
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from estilos import *
from config import CARPETAS
from database import (
    crear_backup_json, 
    restaurar_backup_json, 
    crear_paquete_migracion, 
    restaurar_paquete_migracion
)

class VistaRespaldos(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.ruta_respaldos = CARPETAS["respaldos"]
        os.makedirs(self.ruta_respaldos, exist_ok=True)
        self.construir_ui()


    def construir_ui(self):
        # Cabecera
        f_cab = ctk.CTkFrame(self, fg_color="transparent")
        f_cab.pack(pady=(30, 20), padx=30, fill="x")
        ctk.CTkLabel(f_cab, text="Copias de Seguridad (Backup) y Restauración", font=ctk.CTkFont(size=28, weight="bold"), text_color=C_TEXT).pack(side="left")

        # Contenedor Principal (Dos Columnas)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.main_container.columnconfigure(0, weight=1, uniform="col")
        self.main_container.columnconfigure(1, weight=1, uniform="col")

        # ----------------------------------------------------
        # COLUMNA 1: OPERACIONES MANUALES
        # ----------------------------------------------------
        f_manual = ctk.CTkFrame(self.main_container, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)
        f_manual.grid(row=0, column=0, padx=12, pady=10, sticky="nsew")

        ctk.CTkLabel(f_manual, text="Copias Manuales y Migración", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(20, 10), padx=20, anchor="w")
        
        desc_manual = (
            "Permite salvaguardar el estado actual de toda la base de datos o exportar un paquete "
            "completo con todas las fotos de equipos, manuales y fichas técnicas para migrar a otra computadora."
        )
        lbl_desc = ctk.CTkLabel(f_manual, text=desc_manual, font=ctk.CTkFont(size=12), text_color=C_SUBTEXT, justify="left", wraplength=380)
        lbl_desc.pack(pady=(0, 20), padx=20, anchor="w")

        # Botón Exportar Paquete Completo
        self.btn_paquete_exp = ctk.CTkButton(
            f_manual, text="📦 Exportar Paquete Completo (BD + Fotos + Docs)", height=42, corner_radius=10,
            fg_color=C_GREEN, hover_color=C_GREEN_HOVER, font=ctk.CTkFont(size=13, weight="bold"),
            command=self.ejecutar_exportar_paquete
        )
        self.btn_paquete_exp.pack(pady=(4, 4), padx=20, fill="x")

        # Botón Importar Paquete Completo
        self.btn_paquete_imp = ctk.CTkButton(
            f_manual, text="📥 Importar Paquete Completo en esta PC", height=42, corner_radius=10,
            fg_color=C_PURPLE, hover_color=C_PURPLE_HOVER, font=ctk.CTkFont(size=13, weight="bold"),
            command=self.ejecutar_importar_paquete
        )
        self.btn_paquete_imp.pack(pady=(4, 15), padx=20, fill="x")

        # Botón Generar Copia BD
        self.btn_generar = ctk.CTkButton(
            f_manual, text="💾 Generar Respaldo BD (Solo JSON)", height=38, corner_radius=10,
            fg_color=C_BLUE, hover_color=C_BLUE_HOVER, font=ctk.CTkFont(size=13, weight="bold"),
            command=self.ejecutar_backup_manual
        )
        self.btn_generar.pack(pady=4, padx=20, fill="x")

        # Botón Restaurar Copia BD
        self.btn_restaurar = ctk.CTkButton(
            f_manual, text="🔄 Restaurar Respaldo BD (Solo JSON)", height=38, corner_radius=10,
            fg_color=C_RED, hover_color=C_RED_HOVER, font=ctk.CTkFont(size=13, weight="bold"),
            command=self.ejecutar_restore_manual
        )
        self.btn_restaurar.pack(pady=4, padx=20, fill="x")


        # ----------------------------------------------------
        # COLUMNA 2: RESPALDOS AUTOMÁTICOS
        # ----------------------------------------------------
        f_auto = ctk.CTkFrame(self.main_container, fg_color=C_CARD, corner_radius=16, border_width=1, border_color=C_BORDER)

        f_auto.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")

        ctk.CTkLabel(f_auto, text="Copias de Seguridad Automáticas", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_TEXT).pack(pady=(20, 5), padx=20, anchor="w")
        ctk.CTkLabel(f_auto, text="Respaldos automáticos semanales generados por el sistema:", font=ctk.CTkFont(size=13), text_color=C_SUBTEXT).pack(pady=(0, 15), padx=20, anchor="w")

        # Contenedor de la lista de archivos
        self.scroll_list = ctk.CTkScrollableFrame(f_auto, fg_color=C_BG, height=220, corner_radius=10)
        self.scroll_list.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Botón Restaurar Selección
        self.btn_restaurar_sel = ctk.CTkButton(
            f_auto, text="🔄 Restaurar Respaldo Seleccionado", height=45, corner_radius=10,
            fg_color=C_RED, hover_color=C_RED_HOVER, font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled", command=self.ejecutar_restore_seleccionado
        )
        self.btn_restaurar_sel.pack(pady=(0, 20), padx=20, fill="x")

        self.seleccionado = None
        self.seleccionado_filepath = None
        self.items_list = []
        self.cargar_lista_respaldos()

    def obtener_directorios_respaldos(self):
        """Retorna todas las ubicaciones posibles donde se almacenan respaldos."""
        import sys
        directorios = [self.ruta_respaldos]
        dir_local = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "respaldos")
        if dir_local not in directorios:
            directorios.append(dir_local)
        if hasattr(sys, 'frozen'):
            dir_exe = os.path.dirname(sys.executable)
            dirs_frozen = [
                os.path.join(dir_exe, "_internal", "respaldos"),
                os.path.join(dir_exe, "respaldos")
            ]
            for df in dirs_frozen:
                if df not in directorios:
                    directorios.append(df)
        return [d for d in directorios if os.path.exists(d)]

    def cargar_lista_respaldos(self):
        # Limpiar lista anterior
        for widget in self.items_list:
            widget.destroy()
        self.items_list.clear()
        self.seleccionado = None
        self.seleccionado_filepath = None
        self.btn_restaurar_sel.configure(state="disabled")

        dirs = self.obtener_directorios_respaldos()
        archivos_dict = {}  # nombre -> (full_path, fecha_m, tamano_kb, timestamp)

        for d in dirs:
            try:
                for file in os.listdir(d):
                    if file.endswith(".json") and file != "metadata.json":
                        full_path = os.path.join(d, file)
                        try:
                            stat = os.stat(full_path)
                            ts = stat.st_mtime
                            # Si ya existe en otro directorio, conservar el de fecha más reciente
                            if file not in archivos_dict or ts > archivos_dict[file][3]:
                                fecha_m = datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
                                tamano_kb = round(stat.st_size / 1024, 1)
                                archivos_dict[file] = (full_path, fecha_m, tamano_kb, ts)
                        except:
                            pass
            except:
                pass

        archivos = [(nombre, info[0], info[1], info[2], info[3]) for nombre, info in archivos_dict.items()]
        # Ordenar por fecha de modificación descendente
        archivos.sort(key=lambda x: x[4], reverse=True)

        if not archivos:
            lbl = ctk.CTkLabel(self.scroll_list, text="No hay copias de seguridad registradas aún.", font=ctk.CTkFont(size=13), text_color=C_SUBTEXT)
            lbl.pack(pady=30)
            self.items_list.append(lbl)
            return

        for index, (file, f_path, fecha, tam, ts) in enumerate(archivos):
            f_item = ctk.CTkFrame(self.scroll_list, fg_color=C_CARD, corner_radius=6)
            f_item.pack(fill="x", pady=4, padx=5)
            self.items_list.append(f_item)

            txt_info = f"{file}\nModificado: {fecha} | Tamaño: {tam} KB"
            lbl_info = ctk.CTkLabel(f_item, text=txt_info, font=ctk.CTkFont(size=12), text_color=C_TEXT, justify="left")
            lbl_info.pack(side="left", padx=10, pady=8)

            # Botón de radio virtual / Selección
            btn_sel = ctk.CTkButton(
                f_item, text="Seleccionar", width=80, height=26, corner_radius=6,
                fg_color="transparent", border_width=1, border_color=C_BORDER, text_color=C_TEXT,
                command=lambda f=file, fp=f_path, fi=f_item: self.seleccionar_archivo_auto(f, fp, fi)
            )
            btn_sel.pack(side="right", padx=10)

    def seleccionar_archivo_auto(self, filename, filepath, frame_widget):
        # Deseleccionar anteriores
        for item in self.items_list:
            if isinstance(item, ctk.CTkFrame):
                item.configure(fg_color=C_CARD)
        
        # Seleccionar actual
        frame_widget.configure(fg_color=C_BORDER)
        self.seleccionado = filename
        self.seleccionado_filepath = filepath
        self.btn_restaurar_sel.configure(state="normal")

    def verificar_permiso_jefe(self):
        if not self.app.es_jefe:
            from customtkinter import CTkInputDialog
            dialog = CTkInputDialog(
                text="La restauración de base de datos sobrescribirá todos los datos.\nSe requiere autorización del Jefe.\nIngrese la contraseña del Jefe/Administrador:",
                title="Autorización Requerida"
            )
            pwd_val = dialog.get_input()
            if not pwd_val:
                return False
            if not self.app.verificar_autorizacion_jefe(pwd_val):
                messagebox.showerror("Error de Autorización", "Contraseña del Jefe incorrecta. Operación cancelada.")
                return False
            else:
                messagebox.showinfo("Autorizado", "Operación autorizada por el Jefe correctamente.")
                return True
        return True

    def ejecutar_backup_manual(self):
        import shutil
        hoy_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"respaldo_manual_{hoy_str}.json"

        # Guardar por defecto en la carpeta respaldos/ para que aparezca en la lista
        os.makedirs(self.ruta_respaldos, exist_ok=True)
        ruta_guardar = filedialog.asksaveasfilename(
            initialdir=self.ruta_respaldos,
            initialfile=filename,
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Guardar Copia de Seguridad"
        )
        if not ruta_guardar:
            return

        if crear_backup_json(ruta_guardar):
            # Replicar también en los otros directorios locales
            for d in self.obtener_directorios_respaldos():
                if os.path.abspath(d) != os.path.abspath(os.path.dirname(ruta_guardar)):
                    try:
                        shutil.copy2(ruta_guardar, os.path.join(d, os.path.basename(ruta_guardar)))
                    except:
                        pass
            messagebox.showinfo("Éxito", f"Copia de seguridad guardada con éxito en:\n{os.path.basename(ruta_guardar)}")
            self.cargar_lista_respaldos()
        else:
            messagebox.showerror("Error", "No se pudo generar la copia de seguridad de la base de datos.")

    def ejecutar_exportar_paquete(self):
        hoy_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Paquete_Completo_GAMLP_{hoy_str}.zip"

        ruta_guardar = filedialog.asksaveasfilename(
            initialdir=self.ruta_respaldos,
            initialfile=filename,
            defaultextension=".zip",
            filetypes=[("Paquete GAMLP CMMS", "*.zip"), ("Todos los Archivos", "*.*")],
            title="Exportar Paquete Completo para otra Computadora"
        )
        if not ruta_guardar:
            return

        exito, msg = crear_paquete_migracion(ruta_guardar)
        if exito:
            messagebox.showinfo(
                "Paquete Generado",
                f"✅ ¡Paquete completo generado con éxito!\n\n"
                f"Archivo: {os.path.basename(ruta_guardar)}\n\n"
                f"Este archivo incluye toda la Base de Datos + Fotos de Equipos/Repuestos + Manuales + Documentos.\n"
                f"Puedes copiarlo a una memoria USB y usar 'Importar Paquete' en cualquier otra computadora."
            )
            self.cargar_lista_respaldos()
        else:
            messagebox.showerror("Error al Exportar", f"No se pudo generar el paquete:\n{msg}")

    def ejecutar_importar_paquete(self):
        if not self.verificar_permiso_jefe():
            return

        if not messagebox.askyesno(
            "Confirmar Importación de Paquete",
            "¿Está seguro de que desea importar un Paquete Completo?\n\n"
            "Esta operación reemplazará la base de datos actual y copiará todas las fotos y documentos del paquete a esta computadora."
        ):
            return

        filepath = filedialog.askopenfilename(
            filetypes=[("Paquete GAMLP CMMS", "*.zip"), ("Todos los Archivos", "*.*")],
            title="Seleccionar Paquete Completo (.zip)"
        )
        if not filepath:
            return

        exito, msg = restaurar_paquete_migracion(filepath)
        if exito:
            self.app.cargar_datos_memoria()
            self.app._calendario_sucio = True
            messagebox.showinfo("Importación Exitosa", f"✅ ¡Paquete importado con éxito!\n\n{msg}\n\nTodas las fotos, documentos y datos de la base de datos están ahora sincronizados en esta computadora.")
            self.app.mostrar_vista("Inventario")
        else:
            messagebox.showerror("Error de Importación", f"No se pudo importar el paquete:\n{msg}")

    def aplicar_restauracion(self, filepath):
        exito, msg = restaurar_backup_json(filepath)
        if exito:
            # Recargar memoria de la aplicación
            self.app.cargar_datos_memoria()
            # Forzar actualización de todas las vistas
            self.app._calendario_sucio = True
            
            messagebox.showinfo("Restauración Completada", f"✅ Base de datos restaurada correctamente.\n\n{msg}")
            self.app.mostrar_vista("Inventario")
        else:
            messagebox.showerror("Error de Restauración", f"Ocurrió un error al restaurar la base de datos:\n{msg}")


    def ejecutar_restore_manual(self):
        if not self.verificar_permiso_jefe():
            return

        if not messagebox.askyesno("Confirmar Restauración", "¿Está seguro de que desea restaurar la base de datos?\n\nEsta operación borrará permanentemente todos los datos actuales del sistema y cargará los del respaldo."):
            return

        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Seleccionar Archivo de Respaldo"
        )
        if not filepath:
            return

        self.aplicar_restauracion(filepath)

    def ejecutar_restore_seleccionado(self):
        if not self.seleccionado_filepath or not os.path.exists(self.seleccionado_filepath):
            messagebox.showerror("Error", "El archivo de respaldo seleccionado no se encuentra disponible.")
            return

        if not self.verificar_permiso_jefe():
            return

        if not messagebox.askyesno("Confirmar Restauración", f"¿Está seguro de que desea restaurar el respaldo '{self.seleccionado}'?\n\nEsta operación sobrescribirá todos los datos actuales del sistema."):
            return

        self.aplicar_restauracion(self.seleccionado_filepath)

    def refrescar_datos(self):
        self.cargar_lista_respaldos()

