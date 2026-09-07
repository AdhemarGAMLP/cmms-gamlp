import os
import json

PERFILES_DB = {
    "relevamiento_2026": {
        "nombre": "🟢 Nueva Base (Relevamiento 2026)",
        "descripcion": "Base de datos limpia en Supabase para el relevamiento 2026.",
        "db_host": "aws-0-us-east-2.pooler.supabase.com",
        "db_port": "5432",
        "db_name": "postgres",
        "db_user": "postgres.stdcxbwhxvezocdnwvnx",
        "db_password": "Ademarz123$",
        "db_sslmode": "require"
    },
    "historica": {
        "nombre": "🔵 Base Histórica (Producción Anterior)",
        "descripcion": "Base de datos con todo el historial de equipos y mantenimientos anteriores.",
        "db_host": "aws-0-us-west-2.pooler.supabase.com",
        "db_port": "5432",
        "db_name": "postgres",
        "db_user": "postgres.ieunrjlkdwikabfscudt",
        "db_password": "Adhemarz123",
        "db_sslmode": "require"
    }
}

PERFILES_BD = PERFILES_DB

def cambiar_perfil_activo(clave_o_nombre):
    """Cambia el perfil activo de base de datos y guarda la configuración."""
    cfg = cargar_config()
    perfil = None
    clave = "relevamiento_2026"
    if clave_o_nombre in PERFILES_DB:
        perfil = PERFILES_DB[clave_o_nombre]
        clave = clave_o_nombre
    else:
        for k, v in PERFILES_DB.items():
            if v["nombre"] == clave_o_nombre:
                perfil = v
                clave = k
                break
    if perfil:
        cfg["perfil_activo"] = clave
        cfg["perfil_nombre"] = perfil["nombre"]
        cfg["db_host"] = perfil["db_host"]
        cfg["db_port"] = perfil["db_port"]
        cfg["db_name"] = perfil["db_name"]
        cfg["db_user"] = perfil["db_user"]
        cfg["db_password"] = perfil["db_password"]
        cfg["db_sslmode"] = perfil.get("db_sslmode", "require")
        return guardar_config(cfg)
    return False

def _obtener_ruta_config():
    return os.path.join(os.path.expanduser("~"), "GAMLP_config.json")

def cargar_config():
    """Lee el archivo JSON de configuración en la carpeta del usuario."""
    ruta_config = _obtener_ruta_config()
    
    # Valores por defecto (por defecto apunta a la nueva base 2026)
    default = {
        "carpeta_datos_base": os.path.join(os.path.expanduser("~"), "Desktop", "Datos_De_Gestion_GAMLP"),
        "db_host": "aws-0-us-east-2.pooler.supabase.com",
        "db_port": "5432",
        "db_name": "postgres",
        "db_user": "postgres.stdcxbwhxvezocdnwvnx",
        "db_password": "Ademarz123$",
        "db_sslmode": "require",
        "url_base_web": "https://cmms-gamlp.onrender.com",
        "perfil_activo": "🟢 Nueva Base (Relevamiento 2026)"
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