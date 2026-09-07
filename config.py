import os
import json

PERFILES_DB = {
    "relevamiento_2026": {
        "clave": "relevamiento_2026",
        "nombre": "🟢 Relevamiento 2026 (Nueva Base de Datos)",
        "descripcion": "Base de datos limpia y oficial para el nuevo relevamiento institucional.",
        "db_host": "aws-0-us-east-2.pooler.supabase.com",
        "db_port": "5432",
        "db_name": "postgres",
        "db_user": "postgres.stdcxbwhxvezocdnwvnx",
        "db_password": "Ademarz123$",
        "db_sslmode": "require",
        "url_base_web": "https://cmms-gamlp.onrender.com"
    },
    "historica": {
        "clave": "historica",
        "nombre": "🔵 Base Histórica / Anterior",
        "descripcion": "Base de datos con el histórico de registros previos.",
        "db_host": "aws-0-us-west-2.pooler.supabase.com",
        "db_port": "5432",
        "db_name": "postgres",
        "db_user": "postgres.ieunrjlkdwikabfscudt",
        "db_password": "Adhemarz123",
        "db_sslmode": "require",
        "url_base_web": "https://cmms-gamlp.onrender.com"
    }
}

def _obtener_ruta_config():
    return os.path.join(os.path.expanduser("~"), "GAMLP_config.json")

def cargar_config():
    """Lee el archivo JSON de configuración en la carpeta del usuario."""
    ruta_config = _obtener_ruta_config()
    
    perfil_defecto = PERFILES_DB["relevamiento_2026"]
    default = {
        "carpeta_datos_base": os.path.join(os.path.expanduser("~"), "Desktop", "Datos_De_Gestion_GAMLP"),
        "perfil_activo": "relevamiento_2026",
        "db_host": perfil_defecto["db_host"],
        "db_port": perfil_defecto["db_port"],
        "db_name": perfil_defecto["db_name"],
        "db_user": perfil_defecto["db_user"],
        "db_password": perfil_defecto["db_password"],
        "db_sslmode": perfil_defecto["db_sslmode"],
        "url_base_web": perfil_defecto["url_base_web"]
    }
    
    if os.path.exists(ruta_config):
        try:
            with open(ruta_config, "r", encoding="utf-8") as f:
                config_usuario = json.load(f)
                default.update(config_usuario)
        except Exception as e:
            print(f"[WARN] Error al leer config existente: {e}")
            
    p_act = default.get("perfil_activo", "relevamiento_2026")
    if p_act in PERFILES_DB:
        p_info = PERFILES_DB[p_act]
        for k in ["db_host", "db_port", "db_name", "db_user", "db_password", "db_sslmode", "url_base_web"]:
            default[k] = p_info[k]

    if os.environ.get("DB_HOST"): default["db_host"] = os.environ["DB_HOST"]
    if os.environ.get("DB_PORT"): default["db_port"] = os.environ["DB_PORT"]
    if os.environ.get("DB_NAME"): default["db_name"] = os.environ["DB_NAME"]
    if os.environ.get("DB_USER"): default["db_user"] = os.environ["DB_USER"]
    if os.environ.get("DB_PASSWORD"): default["db_password"] = os.environ["DB_PASSWORD"]
            
    return default

def guardar_config(nueva_config):
    """Guarda la configuración en el archivo JSON del usuario y actualiza CONFIG."""
    global CONFIG, BASE_DIR, CARPETAS
    ruta_config = _obtener_ruta_config()
    try:
        with open(ruta_config, "w", encoding="utf-8") as f:
            json.dump(nueva_config, f, indent=4)
        CONFIG.update(nueva_config)
        BASE_DIR = CONFIG["carpeta_datos_base"]
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar config: {e}")
        return False

def cambiar_perfil_activo(nombre_perfil):
    """Cambia el perfil activo de base de datos y guarda en GAMLP_config.json."""
    if nombre_perfil not in PERFILES_DB:
        return False
    conf = cargar_config()
    conf["perfil_activo"] = nombre_perfil
    p_info = PERFILES_DB[nombre_perfil]
    for k in ["db_host", "db_port", "db_name", "db_user", "db_password", "db_sslmode", "url_base_web"]:
        conf[k] = p_info[k]
    return guardar_config(conf)


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