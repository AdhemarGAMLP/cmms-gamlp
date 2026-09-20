# estilos.py
# Paleta de Colores Minimalista Neutral Premium (SaaS / Slate)

# Fondos y Superficies
C_BG = "#F8FAFC"             # Slate 50 (Fondo ultra limpio y nítido)
C_CARD = "#FFFFFF"           # Blanco puro para tarjetas y modales
C_CARD_HOVER = "#F1F5F9"     # Slate 100 (Hover sutil)
C_BORDER = "#E2E8F0"         # Slate 200 (Separador y borde fino)
C_BORDER_DARK = "#CBD5E1"    # Slate 300 para bordes de inputs

# Tipografía y Textos
C_TEXT = "#0F172A"           # Slate 900 (Texto primario 100% nítido)
C_SUBTEXT = "#64748B"        # Slate 500 (Texto secundario / hints)
C_GRAY = "#94A3B8"           # Slate 400

# Acentos y Acciones Semánticas (Azul Corporativo Vibrante GAMLP)
C_BLUE = "#007AFF"           # Azul Corporativo vibrante de alta visibilidad
C_BLUE_HOVER = "#0062CC"     # Azul corporativo hover
C_BLUE_LIGHT = "#E5F1FF"     # Tinte azul pastel suave para selección activa / badges

C_GREEN = "#10B981"          # Emerald 500 (Éxito / Operativo / Al Día)
C_GREEN_HOVER = "#059669"
C_GREEN_LIGHT = "#ECFDF5"

C_ORANGE = "#F59E0B"         # Amber 500 (Advertencia / En Garantía / Por Vencer)
C_ORANGE_LIGHT = "#FEF3C7"

C_RED = "#EF4444"            # Rose 500 (Destructivo / Eliminar / Baja / Vencido)
C_RED_HOVER = "#DC2626"
C_RED_LIGHT = "#FEE2E2"

C_YELLOW = "#FBBF24"
C_AMBER = "#F59E0B"

# Botones Secundarios / Tintes
C_SECONDARY_BTN = "#F8FAFC"
C_SECONDARY_BTN_HOVER = "#F1F5F9"

# Compatibilidad de transición (Unificado a Azul Corporativo)
C_PURPLE = "#007AFF"
C_PURPLE_HOVER = "#0062CC"
C_PURPLE_LIGHT = "#E5F1FF"

# Constantes de Curvatura y Estilo Minimalista
CORNER_CARD = 12
CORNER_BTN = 8
CORNER_INPUT = 8


def habilitar_autocompletado(combobox, todas_opciones):
    _debounce = [None]
    def on_key(event):
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"):
            return
        def _filtrar():
            try:
                typed = combobox.get().strip()
                if not typed:
                    combobox.configure(values=todas_opciones)
                else:
                    filtradas = [o for o in todas_opciones if typed.lower() in o.lower()]
                    combobox.configure(values=filtradas if filtradas else ["No hay coincidencias"])
            except Exception:
                pass
        if _debounce[0] is not None:
            try:
                combobox.after_cancel(_debounce[0])
            except Exception:
                pass
        _debounce[0] = combobox.after(120, _filtrar)
    
    if hasattr(combobox, "_entry"):
        combobox._entry.bind("<KeyRelease>", on_key)