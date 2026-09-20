# vistas/enlaces.py
import os
import socket
import webbrowser
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image
from estilos import *
from config import cargar_config

class VistaEnlaces(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=C_BG)
        self.app = app
        self.ip_local = self.obtener_ip_local()
        self.cfg = cargar_config()
        self.url_cloud = "https://cmms-gamlp.onrender.com/movil"
        self.url_hist = "https://cmms-gamlp.onrender.com/historico"
        self.url_web = "https://cmms-gamlp.onrender.com/"
        self.url_local = f"http://{self.ip_local}:5000/movil"
        self.url_supabase = "https://supabase.com/dashboard"
        self.url_render = "https://dashboard.render.com/"
        self.url_github = "https://github.com/AdhemarGAMLP/cmms-gamlp"
        self.construir_ui()

    def obtener_ip_local(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def copiar_al_portapapeles(self, texto, btn=None):
        self.clipboard_clear()
        self.clipboard_append(texto)
        if btn:
            txt_orig = btn.cget("text")
            btn.configure(text="✅ ¡Copiado!", fg_color="#16A34A")
            self.after(2000, lambda: btn.configure(text=txt_orig, fg_color=C_BLUE))
        else:
            messagebox.showinfo("Copiado", f"Enlace copiado al portapapeles:\n\n{texto}")

    def mostrar_qr_modal(self, url, titulo):
        win = ctk.CTkToplevel(self)
        win.title(titulo)
        win.geometry("420x540")
        win.configure(fg_color=C_BG)
        win.transient(self)
        win.grab_set()

        # Centrar ventana
        win.update_idletasks()
        w, h = 420, 540
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

        ctk.CTkLabel(win, text="📱 Código QR de Acceso", font=ctk.CTkFont(size=18, weight="bold"), text_color=C_BLUE).pack(pady=(20, 6))
        ctk.CTkLabel(win, text=titulo, font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack()
        ctk.CTkLabel(win, text="Escanea con la cámara de tu celular para ingresar directo:", font=ctk.CTkFont(size=11), text_color=C_SUBTEXT).pack(pady=(2, 10))

        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="#003B64", back_color="white").convert("RGB")
            qr_ctk = ctk.CTkImage(light_image=img_qr, dark_image=img_qr, size=(220, 220))
            lbl_qr = ctk.CTkLabel(win, image=qr_ctk, text="")
            lbl_qr.pack(pady=10)
        except Exception as e:
            ctk.CTkLabel(win, text=f"Error QR: {e}", text_color=C_RED).pack(pady=20)

        f_u = ctk.CTkFrame(win, fg_color=C_CARD, corner_radius=8, border_width=1, border_color=C_BORDER)
        f_u.pack(fill="x", padx=25, pady=8)
        ctk.CTkLabel(f_u, text=url, font=ctk.CTkFont(size=11, weight="bold"), text_color=C_BLUE).pack(padx=10, pady=8)

        ctk.CTkButton(win, text="Cerrar", width=120, height=36, fg_color=C_SUBTEXT, command=win.destroy).pack(pady=(8, 15))

    def construir_ui(self):
        # Cabecera
        f_cab = ctk.CTkFrame(self, fg_color="transparent")
        f_cab.pack(pady=(25, 12), padx=30, fill="x")
        ctk.CTkLabel(f_cab, text="🔗 Enlaces y Accesos del Sistema SGEM GAMLP", font=ctk.CTkFont(size=26, weight="bold"), text_color=C_TEXT).pack(side="left")

        # Contenedor scrollable
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # ----------------------------------------------------
        # TARJETA 1: SUITE MÓVIL EN LA NUBE (24/7)
        # ----------------------------------------------------
        self._crear_tarjeta_enlace(
            scroll,
            icono="📱",
            titulo="Suite Móvil para Celulares (Nube 24/7 Oficial)",
            badge="🟢 ACTIVO ONLINE",
            badge_color="#16A34A",
            descripcion="Acceso completo para celulares y tablets desde cualquier centro de salud con megas o Wi-Fi.\nFunciona las 24 horas del día aunque esta computadora esté apagada.",
            url=self.url_cloud,
            acciones=[
                ("📋 Copiar Enlace", lambda: self.copiar_al_portapapeles(self.url_cloud)),
                ("🌐 Abrir en Navegador", lambda: webbrowser.open(self.url_cloud)),
                ("📱 Ver Código QR", lambda: self.mostrar_qr_modal(self.url_cloud, "Suite Móvil 24/7 (Nube)"))
            ],
            destacada=True
        )

        # ----------------------------------------------------
        # TARJETA 2: CONSULTA HISTÓRICA GAMLP (SOLO LECTURA)
        # ----------------------------------------------------
        self._crear_tarjeta_enlace(
            scroll,
            icono="🏛️",
            titulo="Consulta Histórica GAMLP (Gestiones Anteriores - Solo Lectura)",
            badge="🏛️ 2.938 EQUIPOS • SOLO LECTURA",
            badge_color="#D97706",
            descripcion="Consulta y búsqueda de antecedentes de los 2.938 equipos médicos y mobiliario relevados en gestiones pasadas.\nFichas técnicas completas protegidas contra modificación o borrado accidental.",
            url=self.url_hist,
            acciones=[
                ("📋 Copiar Enlace", lambda: self.copiar_al_portapapeles(self.url_hist)),
                ("🌐 Abrir en Navegador", lambda: webbrowser.open(self.url_hist)),
                ("📱 Ver Código QR", lambda: self.mostrar_qr_modal(self.url_hist, "Consulta Histórica 24/7 (Nube)"))
            ]
        )

        # ----------------------------------------------------
        # TARJETA 3: PORTAL WEB GENERAL DE CONSULTA
        # ----------------------------------------------------
        self._crear_tarjeta_enlace(
            scroll,
            icono="💻",
            titulo="Portal Web General (Consulta de Inventario y Fichas)",
            badge="🌐 PÚBLICO",
            badge_color=C_BLUE,
            descripcion="Portal web para búsqueda rápida de equipos médicos, visualización de fichas técnicas y consulta de inventarios en centros de salud.",
            url=self.url_web,
            acciones=[
                ("📋 Copiar Enlace", lambda: self.copiar_al_portapapeles(self.url_web)),
                ("🌐 Abrir en Navegador", lambda: webbrowser.open(self.url_web))
            ]
        )

        # ----------------------------------------------------
        # TARJETA 3: ENLACE LOCAL EN RED WI-FI
        # ----------------------------------------------------
        self._crear_tarjeta_enlace(
            scroll,
            icono="📶",
            titulo="Servidor Local en Red Wi-Fi (Esta Computadora)",
            badge="🏢 RED LOCAL",
            badge_color="#D97706",
            descripcion=f"Conexión directa en la misma red Wi-Fi de esta sala o consultorio (IP: {self.ip_local}).\nÚtil para cuando se trabaja sin conexión a internet en modo local.",
            url=self.url_local,
            acciones=[
                ("📋 Copiar Enlace", lambda: self.copiar_al_portapapeles(self.url_local)),
                ("📱 Ver Código QR", lambda: self.mostrar_qr_modal(self.url_local, "Servidor Local Wi-Fi"))
            ]
        )


    def _crear_tarjeta_enlace(self, parent, icono, titulo, badge, badge_color, descripcion, url, acciones, destacada=False):
        borde_color = "#3B82F6" if destacada else C_BORDER
        borde_ancho = 2 if destacada else 1
        card = ctk.CTkFrame(parent, fg_color=C_CARD, corner_radius=CORNER_CARD, border_width=borde_ancho, border_color=borde_color)
        card.pack(fill="x", pady=(0, 15))

        f_inner = ctk.CTkFrame(card, fg_color="transparent")
        f_inner.pack(padx=20, pady=16, fill="x")

        # Fila superior: icono, título y badge
        f_top = ctk.CTkFrame(f_inner, fg_color="transparent")
        f_top.pack(fill="x", pady=(0, 6))

        f_t_left = ctk.CTkFrame(f_top, fg_color="transparent")
        f_t_left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(f_t_left, text=f"{icono} {titulo}", font=ctk.CTkFont(size=16, weight="bold"), text_color=C_TEXT).pack(side="left")

        # Badge
        f_badge = ctk.CTkFrame(f_top, fg_color="transparent")
        f_badge.pack(side="right")
        ctk.CTkLabel(f_badge, text=badge, font=ctk.CTkFont(size=11, weight="bold"), text_color=badge_color).pack()

        # Descripción
        ctk.CTkLabel(f_inner, text=descripcion, font=ctk.CTkFont(size=11), text_color=C_SUBTEXT, justify="left").pack(anchor="w", pady=(0, 10))

        # Campo con URL
        f_url = ctk.CTkFrame(f_inner, fg_color=C_BG, corner_radius=8, border_width=1, border_color=C_BORDER)
        f_url.pack(fill="x", pady=(0, 12))

        entry = ctk.CTkEntry(f_url, height=36, corner_radius=8, border_width=0, fg_color="transparent", font=ctk.CTkFont(size=12, weight="bold"), text_color=C_BLUE)
        entry.insert(0, url)
        entry.configure(state="readonly")
        entry.pack(side="left", fill="x", expand=True, padx=10, pady=4)

        # Botones de acción
        f_acc = ctk.CTkFrame(f_inner, fg_color="transparent")
        f_acc.pack(fill="x")

        for txt_acc, cmd_acc in acciones:
            btn = ctk.CTkButton(
                f_acc,
                text=txt_acc,
                height=34,
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=C_BLUE,
                hover_color=C_BLUE_HOVER
            )
            # Vincular para pasar el botón a la función si es copiar
            if "Copiar" in txt_acc:
                btn.configure(command=lambda u=url, b=btn: self.copiar_al_portapapeles(u, b))
            else:
                btn.configure(command=cmd_acc)
            btn.pack(side="left", padx=(0, 8))
