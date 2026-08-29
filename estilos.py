# estilos.py
# Paleta de Colores Moderna (Slate & Royal Medical Blue)

C_BG = "#F8FAFC"             # Slate 50 ultra suave
C_CARD = "#FFFFFF"           # Blanco puro para tarjetas
C_CARD_HOVER = "#F1F5F9"     # Slate 100
C_TEXT = "#0F172A"           # Slate 900 (ultra legible y nítido)
C_SUBTEXT = "#64748B"        # Slate 500
C_GRAY = "#94A3B8"           # Slate 400
C_BORDER = "#E2E8F0"         # Slate 200 (borde sutil y fino)

# Acentos Principales
C_BLUE = "#2563EB"           # Royal Blue Médico
C_BLUE_HOVER = "#1D4ED8"
C_BLUE_LIGHT = "#EFF6FF"     # Azul pastel suave para selección activa

C_GREEN = "#10B981"          # Esmeralda
C_GREEN_HOVER = "#059669"
C_GREEN_LIGHT = "#ECFDF5"

C_ORANGE = "#F59E0B"         # Ámbar
C_ORANGE_LIGHT = "#FFFBEB"

C_RED = "#EF4444"            # Carmesí
C_RED_HOVER = "#DC2626"
C_RED_LIGHT = "#FEF2F2"

C_PURPLE = "#8B5CF6"         # Violeta
C_PURPLE_HOVER = "#7C3AED"
C_PURPLE_LIGHT = "#F5F3FF"

C_YELLOW = "#FBBF24"

# Constantes de Curvatura y Tipografía
CORNER_CARD = 14
CORNER_BTN = 10
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