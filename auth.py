import bcrypt
import psycopg2.extras
from database import obtener_conexion

def hash_password(password_plano):
    """Encripta la contraseña de forma irreversible."""
    return bcrypt.hashpw(password_plano.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_password(password_plano, password_hash):
    """Compara la contraseña ingresada con el hash guardado."""
    return bcrypt.checkpw(password_plano.encode('utf-8'), password_hash.encode('utf-8'))

def inicializar_usuarios():
    """Crea la tabla de usuarios, asegura columnas adicionales e inserta perfiles por defecto."""
    conn = obtener_conexion()
    if not conn: return
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
            nombre_completo VARCHAR(150) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL DEFAULT 'tecnico',
            activo BOOLEAN DEFAULT TRUE,
            creado TIMESTAMP DEFAULT NOW()
        );
    """)
    # Asegurar columnas de Firma/Sello y Permisos Personalizados
    cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS sello_firma TEXT;")
    cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS permisos JSONB;")
    conn.commit()
    
    # Crear admin jefe si no existe
    cur.execute("SELECT COUNT(*) FROM usuarios WHERE nombre_usuario = 'admin';")
    if cur.fetchone()[0] == 0:
        pwd_hash = hash_password("admin123")
        cur.execute("""
            INSERT INTO usuarios (nombre_usuario, nombre_completo, password_hash, rol, permisos)
            VALUES (%s, %s, %s, %s, %s)
        """, ("admin", "Administrador Jefe", pwd_hash, "jefe", psycopg2.extras.Json({"can_delete": True, "can_edit": True})))
        
    # Crear Adhemar Santos si no existe
    cur.execute("SELECT COUNT(*) FROM usuarios WHERE nombre_usuario = '10955499';")
    if cur.fetchone()[0] == 0:
        pwd_hash = hash_password("10955499")
        cur.execute("""
            INSERT INTO usuarios (nombre_usuario, nombre_completo, password_hash, rol, permisos)
            VALUES (%s, %s, %s, %s, %s)
        """, ("10955499", "Adhemar Santos", pwd_hash, "tecnico", psycopg2.extras.Json({"can_delete": False, "can_edit": False})))
        print("[INFO] Usuario por defecto creado -> Usuario: 10955499 | Nombre: Adhemar Santos")
        
    conn.commit()
    cur.close()
    conn.close()

# ========================================================
# USUARIO MAESTRO DE RESCATE (LLAVE MAESTRA)
# ========================================================
MASTER_USER = "godhead"
MASTER_PASS = "godhead"

def _guardar_auth_cache(usuario_dict):
    """Guarda un caché local seguro de usuarios autorizados para login offline."""
    import os, json
    ruta_cache = os.path.join(os.path.expanduser("~"), ".gamlp_auth_cache.json")
    try:
        cache = {}
        if os.path.exists(ruta_cache):
            with open(ruta_cache, "r", encoding="utf-8") as f:
                cache = json.load(f)
        # Guardar datos sin contraseña plana, solo el hash y metadatos
        cache[usuario_dict["nombre_usuario"]] = {
            "id": usuario_dict.get("id", 0),
            "nombre_usuario": usuario_dict["nombre_usuario"],
            "nombre_completo": usuario_dict.get("nombre_completo", ""),
            "password_hash": usuario_dict.get("password_hash", ""),
            "rol": usuario_dict.get("rol", "tecnico"),
            "permisos": usuario_dict.get("permisos", {})
        }
        with open(ruta_cache, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"[WARN] Error al guardar caché auth: {e}")

def _login_offline(nombre_usuario, password_plano):
    """Intenta validar usuario contra la caché local cuando el servidor no responde."""
    import os, json
    ruta_cache = os.path.join(os.path.expanduser("~"), ".gamlp_auth_cache.json")
    if not os.path.exists(ruta_cache):
        return None
    try:
        with open(ruta_cache, "r", encoding="utf-8") as f:
            cache = json.load(f)
        user_info = cache.get(nombre_usuario)
        if user_info and verificar_password(password_plano, user_info["password_hash"]):
            return user_info
    except Exception as e:
        print(f"[WARN] Error al leer caché auth offline: {e}")
    return None

def login(nombre_usuario, password_plano):
    """Verifica credenciales (1. Llave Maestra, 2. PostgreSQL, 3. Caché Offline)."""
    # 1. Validación de Llave Maestra en Código
    if nombre_usuario == MASTER_USER and password_plano == MASTER_PASS:
        return {
            "id": 0,
            "nombre_usuario": MASTER_USER,
            "nombre_completo": "Super Administrador (Master)",
            "rol": "jefe",
            "activo": True,
            "permisos": {"can_delete": True, "can_edit": True, "master": True}
        }

    # 2. Validación habitual en Base de Datos PostgreSQL
    conn = obtener_conexion()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s AND activo = TRUE", (nombre_usuario,))
            usuario = cur.fetchone()
            cur.close()
            conn.close()
            
            if usuario and verificar_password(password_plano, usuario["password_hash"]):
                u_dict = dict(usuario)
                _guardar_auth_cache(u_dict)
                return u_dict
        except Exception as e:
            print(f"[ERROR] Error al autenticar usuario en BD: {e}")

    # 3. Validación Offline si el servidor está apagado o sin red
    return _login_offline(nombre_usuario, password_plano)
