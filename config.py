import os
import json

def _obtener_ruta_config():
    ruta_gamlp = os.path.join(os.path.expanduser("~"), "GAMLP_config.json")
    if os.path.exists(ruta_gamlp):
        return ruta_gamlp
    ruta_heas = os.path.join(os.path.expanduser("~"), "HEAS_config.json")
    if os.path.exists(ruta_heas):
        return ruta_heas
    return ruta_gamlp

def cargar_config():
    """Lee el archivo JSON de configuración en la carpeta del usuario."""
    ruta_config = _obtener_ruta_config()
    
    # Valores por defecto en caso de emergencia
    default = {
        "carpeta_datos_base": os.path.join(os.path.expanduser("~"), "Desktop", "Datos_De_Gestion_GAMLP"),
        "db_host": "aws-0-us-west-2.pooler.supabase.com",
        "db_port": "5432",
        "db_name": "postgres",
        "db_user": "postgres.ieunrjlkdwikabfscudt",
        "db_password": "Adhemarz123",
        "db_sslmode": "require",
        "url_base_web": "https://cmms-gamlp.onrender.com"
    }
    
    if os.environ.get("DB_HOST"): default["db_host"] = os.environ["DB_HOST"]
    if os.environ.get("DB_PORT"): default["db_port"] = os.environ["DB_PORT"]
    if os.environ.get("DB_NAME"): default["db_name"] = os.environ["DB_NAME"]
    if os.environ.get("DB_USER"): default["db_user"] = os.environ["DB_USER"]
    if os.environ.get("DB_PASSWORD"): default["db_password"] = os.environ["DB_PASSWORD"]
    
    if os.path.exists(ruta_config):
        try:
            with open(ruta_config, "r", encoding="utf-8") as f:
                config_usuario = json.load(f)
                default.update(config_usuario)
        except Exception as e:
            print(f"[WARN] Error al leer config existente: {e}")
            
    return default

def guardar_config(nueva_config):
    """Guarda la configuración en el archivo JSON del usuario y actualiza CONFIG."""
    global CONFIG, BASE_DIR, CARPETAS
    ruta_config = os.path.join(os.path.expanduser("~"), "GAMLP_config.json")
    try:
        with open(ruta_config, "w", encoding="utf-8") as f:
            json.dump(nueva_config, f, indent=4)
        CONFIG.update(nueva_config)
        BASE_DIR = CONFIG["carpeta_datos_base"]
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar config: {e}")
        return False


# Variables globales que importaremos desde otros archivos

CONFIG = cargar_config()
BASE_DIR = CONFIG["carpeta_datos_base"]

# Diccionario con las rutas exactas a cada carpeta de trabajo según el requerimiento
CARPETAS = {
    "areas": os.path.join(BASE_DIR, "Areas"),
    "fichas": os.path.join(BASE_DIR, "Areas"),  # Fallback/Retrocompatibilidad
    "hojas": os.path.join(BASE_DIR, "Areas"),   # Fallback/Retrocompatibilidad
    "cronogramas": os.path.join(BASE_DIR, "Cronogramas"),
    "fotos_repuestos": os.path.join(BASE_DIR, "Fotos_Repuestos"),
    "protocolos_gases": os.path.join(BASE_DIR, "Protocolos_Gases_Medicinales"),
    "protocolos_mri": os.path.join(BASE_DIR, "Protocolos_Resonancia_Magnetica"),
    "respaldos": os.path.join(BASE_DIR, "Respaldos_BD"),
    "fotos_equipos": os.path.join(BASE_DIR, "Fotos_Equipos"),
    "manuales": os.path.join(BASE_DIR, "Manuales"),
    "videos": os.path.join(BASE_DIR, "Videos")
}