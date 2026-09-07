# estilos.py
# Paleta de Colores Apple Human Interface Guidelines (HIG)

# Fondos y Superficies
C_BG = "#F2F2F7"             # Apple System Grouped Background (Gris ultra suave y limpio)
C_CARD = "#FFFFFF"           # Blanco puro para tarjetas y modales
C_CARD_HOVER = "#E5E5EA"     # Apple System Gray 5 (Hover sutil)
C_BORDER = "#E5E5EA"         # Separador y borde fino Apple
C_BORDER_DARK = "#D1D1D6"    # Apple System Gray 4 para bordes de inputs

# Tipografía y Textos
C_TEXT = "#1C1C1E"           # Apple System Gray 6 Dark (Texto primario 100% nítido)
C_SUBTEXT = "#8E8E93"        # Apple System Gray (Texto secundario / hints)
C_GRAY = "#C7C7CC"           # Apple System Gray 4

# Acentos y Acciones Semánticas
C_BLUE = "#007AFF"           # Apple System Corporate Blue (Acción principal)
C_BLUE_HOVER = "#0062CC"     # Azul corporativo hover
C_BLUE_LIGHT = "#E5F1FF"     # Tinte azul pastel suave para selección activa / badges

C_GREEN = "#34C759"          # Apple System Green (Éxito / Al Día)
C_GREEN_HOVER = "#28A745"
C_GREEN_LIGHT = "#EAF9EE"

C_ORANGE = "#FF9500"         # Apple System Orange (Advertencia / Riesgo Medio / Por Vencer)
C_ORANGE_LIGHT = "#FFF5E5"

C_RED = "#FF3B30"            # Apple System Red (Destructivo / Eliminar / Riesgo Alto / Vencido)
C_RED_HOVER = "#D70015"
C_RED_LIGHT = "#FFEBEA"

C_YELLOW = "#FFCC00"         # Apple System Yellow
C_AMBER = "#FF9500"

# Botones Secundarios / Tintes
C_SECONDARY_BTN = "#E5E5EA"
C_SECONDARY_BTN_HOVER = "#D1D1D6"

# Compatibilidad de transición (Unificado a Azul Corporativo)
C_PURPLE = "#007AFF"
C_PURPLE_HOVER = "#0062CC"
C_PURPLE_LIGHT = "#E5F1FF"

# Constantes de Curvatura y Estilo Apple
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