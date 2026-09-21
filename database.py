# database.py
import os
import json
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from config import CONFIG, PERFILES_DB

def obtener_conexion(perfil=None):
    """Establece y retorna la conexión a PostgreSQL usando los datos de config.py o un perfil específico."""
    try:
        if perfil and perfil in PERFILES_DB:
            cfg_db = PERFILES_DB[perfil]
        else:
            cfg_db = CONFIG

        kwargs = {
            "dbname": cfg_db["db_name"],
            "user": cfg_db["db_user"],
            "password": cfg_db["db_password"],
            "host": cfg_db["db_host"],
            "port": cfg_db["db_port"],
            "connect_timeout": 6,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
        if cfg_db.get("db_sslmode") or ("supabase" in str(cfg_db.get("db_host", "")).lower()):
            kwargs["sslmode"] = cfg_db.get("db_sslmode", "require")
            
        conn = psycopg2.connect(**kwargs)
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        print(f"[ERROR] Error de conexión a la BD ({perfil or 'activo'}): {e}")
        return None

def inicializar_bd():
    """Sistema de control de versiones e inicialización segura de base de datos."""
    conn = obtener_conexion()
    if not conn:
        print("[WARN] No se pudo conectar a la BD PostgreSQL central. Operando en modo local/offline...")
        return False
    try:
        cur = conn.cursor()
        
        # 1. Tabla: esquema de versiones
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            );
        """)
        cur.execute("INSERT INTO schema_version (version) SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM schema_version);")
        cur.execute("SELECT MAX(version) FROM schema_version;")
        version_row = cur.fetchone()
        version_actual = version_row[0] if version_row and version_row[0] is not None else 0

        # Comprobar si las tablas principales ya existen
        cur.execute("SELECT to_regclass('public.equipos');")
        tablas_existen = cur.fetchone()[0] is not None

        if tablas_existen and version_actual >= 6:
            # El esquema ya está completamente inicializado y en la última versión.
            # Evita re-ejecutar docenas de ALTER TABLE / DDL en cada inicio, previniendo
            # bloqueos (AccessExclusiveLock) y caídas de conexión con Supabase pooler.
            cur.close()
            conn.close()
            return True

        return _ejecutar_migraciones_completas(conn, cur, version_actual)
    except Exception as e:
        print(f"[WARN] Error no crítico durante la inicialización de la BD: {e}")
        try:
            if conn:
                conn.rollback()
                conn.close()
        except:
            pass
        return False

def _ejecutar_migraciones_completas(conn, cur, version_actual):
    # 2. Catálogo de modelos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalogo (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            marca VARCHAR(100),
            modelo VARCHAR(100),
            area VARCHAR(255),
            piso VARCHAR(100)
        );
    """)

    # 3. Repuestos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS repuestos (
            id SERIAL PRIMARY KEY,
            tipo_equipo VARCHAR(150) NOT NULL,
            nombre_repuesto VARCHAR(150) NOT NULL,
            cantidad INTEGER DEFAULT 0,
            foto TEXT,
            estado_disponibilidad VARCHAR(50) DEFAULT 'En Stock',
            modelo_parte VARCHAR(100),
            costo NUMERIC(12, 2) DEFAULT 0.00,
            caracteristicas TEXT,
            observaciones TEXT,
            UNIQUE(tipo_equipo, nombre_repuesto)
        );
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS estado_disponibilidad VARCHAR(50) DEFAULT 'En Stock';
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS modelo_parte VARCHAR(100);
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS costo NUMERIC(12, 2) DEFAULT 0.00;
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS caracteristicas TEXT;
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS observaciones TEXT;
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS red_salud_nombre VARCHAR(150);
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS centro_salud_nombre VARCHAR(150);
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS area VARCHAR(150);
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS marca VARCHAR(100);
        ALTER TABLE repuestos ADD COLUMN IF NOT EXISTS modelo VARCHAR(100);
    """)

    # 4. Jerarquía Territorial GAMLP y Áreas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS departamentos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            codigo VARCHAR(10),
            estado VARCHAR(20) DEFAULT 'Activo'
        );
        CREATE TABLE IF NOT EXISTS municipios (
            id SERIAL PRIMARY KEY,
            departamento_id INTEGER REFERENCES departamentos(id) ON DELETE CASCADE,
            nombre VARCHAR(150) NOT NULL,
            codigo VARCHAR(20),
            estado VARCHAR(20) DEFAULT 'Activo',
            CONSTRAINT unq_mun_dep UNIQUE (departamento_id, nombre)
        );
        CREATE TABLE IF NOT EXISTS redes_salud (
            id SERIAL PRIMARY KEY,
            municipio_id INTEGER REFERENCES municipios(id) ON DELETE CASCADE,
            departamento_id INTEGER REFERENCES departamentos(id),
            nombre VARCHAR(150) NOT NULL,
            codigo VARCHAR(20) UNIQUE NOT NULL,
            macrodistrito VARCHAR(100),
            responsable VARCHAR(150),
            telefono VARCHAR(50),
            estado VARCHAR(20) DEFAULT 'Activo'
        );
        CREATE TABLE IF NOT EXISTS centros_salud (
            id SERIAL PRIMARY KEY,
            red_salud_id INTEGER REFERENCES redes_salud(id) ON DELETE CASCADE,
            nombre VARCHAR(150) NOT NULL,
            nivel VARCHAR(50) DEFAULT 'Primer Nivel',
            direccion TEXT,
            telefono VARCHAR(50),
            responsable VARCHAR(150),
            estado VARCHAR(20) DEFAULT 'Activo',
            CONSTRAINT unq_centro_red UNIQUE (red_salud_id, nombre)
        );
        CREATE TABLE IF NOT EXISTS areas (
            id SERIAL PRIMARY KEY,
            centro_salud_id INTEGER REFERENCES centros_salud(id) ON DELETE SET NULL,
            centro_salud_nombre VARCHAR(150),
            red_salud_nombre VARCHAR(150),
            nombre VARCHAR(255) NOT NULL,
            piso VARCHAR(100),
            contacto VARCHAR(100),
            encargado VARCHAR(255),
            cargo VARCHAR(150),
            ci_encargado VARCHAR(50)
        );
    """)
    cur.execute("ALTER TABLE areas ADD COLUMN IF NOT EXISTS centro_salud_id INTEGER REFERENCES centros_salud(id) ON DELETE SET NULL;")
    cur.execute("ALTER TABLE areas ADD COLUMN IF NOT EXISTS centro_salud_nombre VARCHAR(150);")
    cur.execute("ALTER TABLE areas ADD COLUMN IF NOT EXISTS red_salud_nombre VARCHAR(150);")
    cur.execute("ALTER TABLE areas ADD COLUMN IF NOT EXISTS cargo VARCHAR(150);")
    cur.execute("ALTER TABLE areas ADD COLUMN IF NOT EXISTS ci_encargado VARCHAR(50);")
    cur.execute("ALTER TABLE areas DROP CONSTRAINT IF EXISTS areas_nombre_key;")
    cur.execute("ALTER TABLE areas DROP CONSTRAINT IF EXISTS unique_nombre_piso;")
    conn.commit()

    # 5. Equipos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id VARCHAR(50) PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            marca VARCHAR(100),
            modelo VARCHAR(100),
            servicio VARCHAR(100),
            area VARCHAR(100),
            procedencia VARCHAR(100),
            fabricante VARCHAR(100),
            proveedor VARCHAR(100),
            anio_fab VARCHAR(20),
            numero_serie VARCHAR(100),
            t_elec VARCHAR(5),
            t_elco VARCHAR(5),
            t_mec VARCHAR(5),
            t_hid VARCHAR(5),
            t_neu VARCHAR(5),
            t_vap VARCHAR(5),
            a_comp VARCHAR(5),
            a_como VARCHAR(5),
            a_don VARCHAR(5),
            te_fijo VARCHAR(5),
            te_mov VARCHAR(5),
            te_por VARCHAR(5),
            garantia VARCHAR(50),
            fecha_inicio_garantia DATE,
            fecha_vencimiento_garantia DATE,
            criticidad VARCHAR(100),
            categorizacion_detalle JSONB,
            estado VARCHAR(50) DEFAULT 'Operativo',
            fecha_adquisicion DATE,
            fecha_registro DATE,
            foto TEXT,
            costo NUMERIC DEFAULT 0,
            voltaje VARCHAR(255),
            potencia VARCHAR(255),
            temperatura VARCHAR(255),
            humedad VARCHAR(255),
            corriente VARCHAR(255),
            peso VARCHAR(255),
            dimensiones VARCHAR(255),
            resolucion VARCHAR(255),
            contexto_operacional TEXT,
            funciones_equipo TEXT,
            acciones_preventivas TEXT,
            acciones_falla TEXT,
            fallas_funcionales TEXT,
            causas_fallo TEXT,
            efectos_fallo TEXT,
            efecto_entorno TEXT,
            observaciones TEXT
        );
        ALTER TABLE equipos ADD COLUMN IF NOT EXISTS vida_util VARCHAR(255);
        ALTER TABLE equipos ADD COLUMN IF NOT EXISTS bateria_respaldo VARCHAR(255);
        ALTER TABLE equipos ADD COLUMN IF NOT EXISTS version_software VARCHAR(255);
        ALTER TABLE equipos ADD COLUMN IF NOT EXISTS suministro_gases VARCHAR(255);
    """)

    # 6. Historial de intervenciones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historial_intervenciones (
            id SERIAL PRIMARY KEY,
            equipo_id VARCHAR(50) NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
            fecha DATE NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            detalle TEXT,
            condicion VARCHAR(50),
            estado_equipo VARCHAR(50),
            deficiencia TEXT,
            trabajo TEXT,
            observaciones TEXT,
            fecha_entrega DATE,
            servicio_ht VARCHAR(150),
            tipo_ht VARCHAR(100),
            realizado_por VARCHAR(150),
            hora_entrega VARCHAR(10),
            repuesto_usado BOOLEAN DEFAULT FALSE,
            repuesto_nombre VARCHAR(255),
            repuesto_cantidad INTEGER DEFAULT 0,
            fecha_programada DATE,
            tiempo_reparacion NUMERIC DEFAULT 0
        );
    """)

    # 7. Protocolos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS protocolos (
            id SERIAL PRIMARY KEY,
            fecha DATE NOT NULL,
            tipo_protocolo VARCHAR(100) NOT NULL,
            turno VARCHAR(20) NOT NULL,
            responsable VARCHAR(150),
            ruta_excel TEXT,
            UNIQUE (fecha, tipo_protocolo, turno)
        );
    """)

    # 8. Papelera
    cur.execute("""
        CREATE TABLE IF NOT EXISTS papelera (
            id SERIAL PRIMARY KEY,
            tabla_origen VARCHAR(100),
            id_original VARCHAR(100),
            datos JSONB,
            eliminado_por VARCHAR(100),
            fecha_eliminacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 9. Columnas adicionales de compatibilidad
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS fecha_vencimiento_garantia DATE;")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS fecha_inicio_garantia DATE;")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS numero_serie VARCHAR(100);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS costo NUMERIC DEFAULT 0;")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS centro_salud_id INTEGER REFERENCES centros_salud(id) ON DELETE SET NULL;")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS red_salud_id INTEGER REFERENCES redes_salud(id) ON DELETE SET NULL;")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS centro_salud_nombre VARCHAR(150);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS red_salud_nombre VARCHAR(150);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS municipio_nombre VARCHAR(150);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS departamento_nombre VARCHAR(100);")
    cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS repuesto_usado BOOLEAN DEFAULT FALSE;")
    cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS repuesto_nombre VARCHAR(255);")
    cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS repuesto_cantidad INTEGER DEFAULT 0;")
    cur.execute("ALTER TABLE catalogo ADD COLUMN IF NOT EXISTS area VARCHAR(255);")
    cur.execute("ALTER TABLE catalogo ADD COLUMN IF NOT EXISTS piso VARCHAR(100);")
    cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS fecha_programada DATE;")
    cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS realizado_por VARCHAR(150);")
    cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS hora_entrega VARCHAR(10);")
    cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS tiempo_reparacion NUMERIC DEFAULT 0;")

    # 9. Mueblería y Computadoras (Equipos de Computación, TI y Enseres)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS muebleria (
            id SERIAL PRIMARY KEY,
            sector_actual VARCHAR(100),
            direccion_administrativa VARCHAR(255),
            unidad_organizacional VARCHAR(255),
            fecha_asignacion VARCHAR(50),
            tecnico_inventareador VARCHAR(200),
            persona_asignada VARCHAR(200),
            cargo_asignado VARCHAR(150),
            ci_asignado VARCHAR(50),
            tipo_activo VARCHAR(150) NOT NULL,
            descripcion TEXT,
            marca VARCHAR(150),
            modelo VARCHAR(150),
            serie VARCHAR(150),
            detalle_transaccion VARCHAR(100),
            codigo_sispam VARCHAR(100),
            bertin VARCHAR(100),
            sapm VARCHAR(100),
            observaciones_de_asignacion TEXT,
            ubicacion VARCHAR(255),
            fecha_incorporacion VARCHAR(50),
            red_salud_id INTEGER REFERENCES redes_salud(id) ON DELETE SET NULL,
            centro_salud_id INTEGER REFERENCES centros_salud(id) ON DELETE SET NULL,
            estado VARCHAR(50) DEFAULT 'Activo',
            estado_conservacion VARCHAR(50) DEFAULT 'Bueno',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("ALTER TABLE muebleria ADD COLUMN IF NOT EXISTS estado_conservacion VARCHAR(50) DEFAULT 'Bueno';")
    cur.execute("ALTER TABLE muebleria ADD COLUMN IF NOT EXISTS marca VARCHAR(150);")
    cur.execute("ALTER TABLE muebleria ADD COLUMN IF NOT EXISTS cargo_asignado VARCHAR(150);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS sector_actual VARCHAR(100);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS persona_asignada VARCHAR(200);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS cargo_asignado VARCHAR(150);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS ci_asignado VARCHAR(50);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS codigo_sispam VARCHAR(100);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS bertin VARCHAR(100);")
    cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS sapm VARCHAR(100);")

    # 10. Índices de optimización en PostgreSQL
    cur.execute("CREATE INDEX IF NOT EXISTS idx_equipos_nombre ON equipos(nombre);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_equipos_servicio ON equipos(servicio);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_equipos_area ON equipos(area);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_equipos_criticidad ON equipos(criticidad);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_equipos_centro ON equipos(centro_salud_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_equipos_red ON equipos(red_salud_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_historial_equipo_id ON historial_intervenciones(equipo_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_intervenciones(fecha);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_repuestos_tipo_equipo ON repuestos(tipo_equipo);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_protocolos_fecha ON protocolos(fecha);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_papelera_tabla ON papelera(tabla_origen, fecha_eliminacion DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_muebleria_sispam ON muebleria(codigo_sispam);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_muebleria_bertin ON muebleria(bertin);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_muebleria_sapm ON muebleria(sapm);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_muebleria_unidad ON muebleria(unidad_organizacional);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_muebleria_tipo ON muebleria(tipo_activo);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_muebleria_red ON muebleria(red_salud_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_muebleria_centro ON muebleria(centro_salud_id);")
    conn.commit()

    
    # Limpiar nombres redundantes de áreas, equipos y catálogo existentes
    cur.execute(r"UPDATE areas SET nombre = trim(regexp_replace(nombre, '\s*\(Piso\s*[-0-9]+\)', '', 'g'));")
    try:
        cur.execute(r"UPDATE equipos SET ubicacion = trim(regexp_replace(ubicacion, '\s*\(Piso\s*[-0-9]+\)', '', 'g')) WHERE ubicacion IS NOT NULL;")
    except:
        pass
    try:
        cur.execute(r"UPDATE catalogo SET area = trim(regexp_replace(area, '\s*\(Piso\s*[-0-9]+\)', '', 'g')) WHERE area IS NOT NULL;")
    except:
        pass
    conn.commit()

    # Sembrar Departamentos, Municipios, Redes y Centros de Salud de GAMLP
    try:
        sembrar_datos_sedes_gamlp(cur, conn)
    except Exception as e_seed_sedes:
        print(f"[WARN] Error al sembrar sedes: {e_seed_sedes}")
        conn.rollback()
    
    # =========================================================
    # 🚀 MOTOR DE ACTUALIZACIÓN DE VERSIONES (MIGRACIONES)
    # =========================================================
    cur.execute("SELECT MAX(version) FROM schema_version;")
    version_actual = cur.fetchone()[0]

    # Versión 1.0 Original
    if version_actual < 1:
        cur.execute("DELETE FROM schema_version; INSERT INTO schema_version (version) VALUES (1);")
        conn.commit()
        print("[OK] Base de datos sincronizada en la Versión 1.0.")

    # Versión 1.1 (Esquema 2)
    if version_actual < 2:
        print("[INFO] Aplicando actualización a la Versión 1.1...")
        # AQUI AGREGAS TUS CAMBIOS DE LA VERSIÓN 1.1. Ejemplos:
        # cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS ip_equipo VARCHAR(50);")
        # cur.execute("CREATE TABLE IF NOT EXISTS nueva_tabla (id SERIAL PRIMARY KEY);")
        
        cur.execute("DELETE FROM schema_version; INSERT INTO schema_version (version) VALUES (2);")
        conn.commit()
        print("[INFO] ¡Software actualizado a la Versión 1.1 exitosamente!")

    # Versión 1.2 (Esquema 3)
    if version_actual < 3:
        print("[INFO] Aplicando actualización a la Versión 1.2...")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS costo NUMERIC DEFAULT 0;")
        cur.execute("ALTER TABLE historial_intervenciones ADD COLUMN IF NOT EXISTS tiempo_reparacion NUMERIC DEFAULT 0;")
        cur.execute("DELETE FROM schema_version; INSERT INTO schema_version (version) VALUES (3);")
        conn.commit()
        print("[INFO] ¡Software actualizado a la Versión 1.2 exitosamente!")

    # Versión 1.3 (Esquema 4)
    if version_actual < 4:
        print("[INFO] Aplicando actualización a la Versión 1.3...")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS costo NUMERIC DEFAULT 0;")
        cur.execute("DELETE FROM schema_version; INSERT INTO schema_version (version) VALUES (4);")
        conn.commit()
        print("[INFO] ¡Software actualizado a la Versión 1.3 exitosamente!")

    # Versión 1.4 (Esquema 5)
    if version_actual < 5:
        print("[INFO] Aplicando actualización a la Versión 1.4...")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS voltaje VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS potencia VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS temperatura VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS humedad VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS corriente VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS peso VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS dimensiones VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS resolucion VARCHAR(255);")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS contexto_operacional TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS funciones_equipo TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS acciones_preventivas TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS acciones_falla TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS fallas_funcionales TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS causas_fallo TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS efectos_fallo TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS efecto_entorno TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS observaciones TEXT;")
        cur.execute("DELETE FROM schema_version; INSERT INTO schema_version (version) VALUES (5);")
        conn.commit()
        print("[INFO] ¡Software actualizado a la Versión 1.4 exitosamente!")

    # Versión 1.5 (Esquema 6) - Migración de nombres de columnas correctos
    if version_actual < 6:
        print("[INFO] Aplicando actualización a la Versión 1.5...")
        # Asegurar columnas con nombres correctos existan
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS funciones_equipo TEXT;")
        cur.execute("ALTER TABLE equipos ADD COLUMN IF NOT EXISTS acciones_falla TEXT;")
        # Copiar datos de columnas antiguas solo si realmente existen en la tabla
        try:
            cur.execute("""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='equipos' AND column_name='funciones_medico') THEN
                        UPDATE equipos SET funciones_equipo = funciones_medico
                        WHERE funciones_equipo IS NULL AND funciones_medico IS NOT NULL;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='equipos' AND column_name='acciones_no_prevenir') THEN
                        UPDATE equipos SET acciones_falla = acciones_no_prevenir
                        WHERE acciones_falla IS NULL AND acciones_no_prevenir IS NOT NULL;
                    END IF;
                END $$;
            """)
        except Exception as e_mig:
            print(f"[WARN] Migración de nombres antiguos omitida: {e_mig}")
            
        cur.execute("DELETE FROM schema_version; INSERT INTO schema_version (version) VALUES (6);")
        conn.commit()
        print("[INFO] ¡Software actualizado a la Versión 1.5 exitosamente!")


    # 11. Sincronizar secuencias de auto-incremento (SERIAL) para evitar colisiones de ID
    tablas_serial = ["departamentos", "municipios", "redes_salud", "centros_salud", "areas", "catalogo", "repuestos", "historial_intervenciones", "protocolos", "usuarios", "papelera", "muebleria"]
    for ts in tablas_serial:
        try:
            cur.execute(f"SELECT setval(pg_get_serial_sequence('{ts}', 'id'), COALESCE((SELECT MAX(id) FROM \"{ts}\"), 1));")
        except Exception as e_seq:
            pass
    cur.close()
    conn.close()
    return True


def sembrar_datos_sedes_gamlp(cur, conn):
    """Siembra los 9 Departamentos de Bolivia, Municipio GAMLP, las 5 Redes Oficiales y sus Centros de Salud."""
    # 1. Departamentos
    deptos = [
        ("La Paz", "LPZ"),
        ("Santa Cruz", "SCZ"),
        ("Cochabamba", "CBB"),
        ("Chuquisaca", "CHQ"),
        ("Oruro", "ORU"),
        ("Potosí", "POT"),
        ("Tarija", "TJA"),
        ("Beni", "BEN"),
        ("Pando", "PND")
    ]
    for nom, cod in deptos:
        cur.execute("INSERT INTO departamentos (nombre, codigo) VALUES (%s, %s) ON CONFLICT (nombre) DO NOTHING;", (nom, cod))
    conn.commit()

    # Obtener ID de La Paz
    cur.execute("SELECT id FROM departamentos WHERE nombre = 'La Paz';")
    row_lpz = cur.fetchone()
    id_lpz = row_lpz[0] if row_lpz else 1

    # 2. Limpiar municipios no deseados y dejar únicamente GAMLP
    cur.execute("DELETE FROM municipios WHERE departamento_id = %s AND nombre != 'GAMLP' AND nombre != 'La Paz (GAMLP)';", (id_lpz,))
    cur.execute("""
        INSERT INTO municipios (departamento_id, nombre, codigo)
        VALUES (%s, 'GAMLP', 'GAMLP')
        ON CONFLICT (departamento_id, nombre) DO UPDATE SET codigo = 'GAMLP';
    """, (id_lpz,))
    conn.commit()

    # Obtener ID de GAMLP
    cur.execute("SELECT id FROM municipios WHERE nombre = 'GAMLP' OR nombre = 'La Paz (GAMLP)' ORDER BY id ASC LIMIT 1;")
    row_gamlp = cur.fetchone()
    id_gamlp = row_gamlp[0] if row_gamlp else 1

    # 3. Las 5 Redes Oficiales de GAMLP
    redes = [
        ("RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "RED-1", "Macrodistrito Cotahuma"),
        ("RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "RED-2", "Macrodistrito Max Paredes"),
        ("RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "RED-3", "Macrodistrito Periférica Central"),
        ("RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "RED-4", "Macrodistrito San Antonio"),
        ("RED 5-SUR (MACRODISTRITO SUR)", "RED-5", "Macrodistrito Sur")
    ]
    
    # Limpiar redes antiguas que no coincidan con las 5 oficiales
    cur.execute("DELETE FROM redes_salud WHERE codigo NOT IN ('RED-1', 'RED-2', 'RED-3', 'RED-4', 'RED-5');")
    
    for nom, cod, macro in redes:
        cur.execute("""
            INSERT INTO redes_salud (municipio_id, departamento_id, nombre, codigo, macrodistrito)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre, macrodistrito = EXCLUDED.macrodistrito, municipio_id = EXCLUDED.municipio_id;
        """, (id_gamlp, id_lpz, nom, cod, macro))
    conn.commit()

    # Mapear IDs de Redes
    cur.execute("SELECT id, codigo FROM redes_salud;")
    red_map = {r[1]: r[0] for r in cur.fetchall()}

    # 4. Limpiar centros_salud antiguos y sembrar ÚNICAMENTE los oficiales
    cur.execute("DELETE FROM centros_salud;")
    conn.commit()

    centros_por_red = {
        "RED-1": [
            "NIÑO KOLLO", "ALCOREZA", "C.M.I VILLA NUEVO POTOSI", "LA GRUTA", 
            "BAJO SAN PEDRO", "EL ROSAL", "SANN LUIS", "BIBLIOTECA", 
            "BAJO TACAGUA", "TEMBLADERANI", "8 DE DICIEMBRE", 
            "LLOJETA EL VERGEL", "PASANKERY", "ALTO TACAGUA", "167 AUXILIO"
        ],
        "RED-2": [
            "EL TEJAR", "CHAMOCO CHICO", "ALTO MCAL. SANTA CRUZ", "VILLA VICTORIA", 
            "LA PORTADA", "OBISPO INDABURO", "APUMALLA", "MUNAYPATA", 
            "PANTICIRCA", "CIUDADEL FERROVIARIA", "SAID", "ZONGO CHORO", 
            "ZONGO CAMSIQUE", "BAJO TEJAR"
        ],
        "RED-3": [
            "ALTO MIRAFLORES", "EL CALVARIO", "3 DE MAYO", "SAN JUAN DE LAZARETO", 
            "ACHACHICALA", "SAN JOSE DE NATIVIDAD", "JUANCITO PINTO", "VILLA FATIMA", 
            "ASISTENCIA PUBLICA", "AGUA DE LA VIDA", "VINO TINTO", "LAS DELICIAS CENTRAL", 
            "PLAN AUTOPISTA", "CHUQUIAGUILLO", "18 DE MAYO"
        ],
        "RED-4": [
            "SAN ISIDRO", "VILLA ARMONIA", "CHOQUECHIHUANI", "SAN ANTONIO ALTO", 
            "PAMPAHASI BAJO", "PAMPAHASI ALTO", "KUPINI", "SAN ANTONIO BAJO", 
            "VALLE HERMOSO", "VILLA COPACABANA", "VILLA SALOME", "ESCOBAR URIA"
        ],
        "RED-5": [
            "MALLASILLA", "ALTO OBRAJES", "ACHUMANI", "MALLASA", "OBRAJES", 
            "ALTO SEGUENCOMA", "BOLOGNIA", "C.M.I. BELLA VISTA", "C.M.I. CHASQUIPAMPA", 
            "COTA COTA - EL ROSAL", "BAJO LLOJETA", "ALTO IRPAVI"
        ]
    }

    for red_cod, lista_centros in centros_por_red.items():
        r_id = red_map.get(red_cod)
        if r_id:
            for nom_c in lista_centros:
                cur.execute("""
                    INSERT INTO centros_salud (red_salud_id, nombre, nivel, estado)
                    VALUES (%s, %s, 'Primer Nivel', 'Activo')
                    ON CONFLICT (red_salud_id, nombre) DO NOTHING;
                """, (r_id, nom_c.strip()))
    conn.commit()


_CACHE_JERARQUIA_SEDES = None

def _obtener_ruta_cache_sedes():
    db_host_key = str(CONFIG.get("db_host", "default")).replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(os.path.expanduser("~"), f".gamlp_sedes_cache_{db_host_key}.json")

def obtener_jerarquia_sedes_db(forzar_recarga=False, perfil=None):
    """Obtiene la jerarquía completa de Departamentos, Municipios, Redes y Centros de Salud (con caché en memoria y disco persistente)."""
    global _CACHE_JERARQUIA_SEDES
    if not perfil and _CACHE_JERARQUIA_SEDES and not forzar_recarga:
        return _CACHE_JERARQUIA_SEDES

    conn = obtener_conexion(perfil=perfil)
    if not conn:
        if not perfil and _CACHE_JERARQUIA_SEDES:
            return _CACHE_JERARQUIA_SEDES
        # Intentar cargar desde el archivo de caché persistente en disco
        ruta_s = _obtener_ruta_cache_sedes()
        if os.path.exists(ruta_s):
            try:
                with open(ruta_s, "r", encoding="utf-8") as f:
                    _CACHE_JERARQUIA_SEDES = json.load(f)
                    if _CACHE_JERARQUIA_SEDES and _CACHE_JERARQUIA_SEDES.get("centros"):
                        return _CACHE_JERARQUIA_SEDES
            except Exception as e:
                print(f"[WARN] Error al leer caché persistente de sedes: {e}")

        # Fallback local desde centros_limpios.json si existe
        try:
            ruta_cj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centros_limpios.json")
            if os.path.exists(ruta_cj):
                with open(ruta_cj, "r", encoding="utf-8") as f:
                    cl_data = json.load(f)
                mapa_redes = {
                    "RED 1": {"id": 1, "nombre": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "codigo": "RED-1"},
                    "RED 2": {"id": 2, "nombre": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "codigo": "RED-2"},
                    "RED 3": {"id": 3, "nombre": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "codigo": "RED-3"},
                    "RED 4": {"id": 4, "nombre": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "codigo": "RED-4"},
                    "RED 5": {"id": 5, "nombre": "RED 5-SUR (MACRODISTRITO SUR)", "codigo": "RED-5"}
                }
                c_list = []
                for idx_c, (c_nom, c_info) in enumerate(cl_data.items(), start=1):
                    r_str = str(c_info.get("red", "RED 1")).strip().upper()
                    r_id = 1
                    for rk, robj in mapa_redes.items():
                        if rk in r_str:
                            r_id = robj["id"]
                            break
                    nom_limpio = c_nom.replace("C.S.", "").replace("C.S ", "").strip()
                    c_list.append({
                        "id": idx_c,
                        "red_salud_id": r_id,
                        "nombre": nom_limpio if nom_limpio else c_nom,
                        "nivel": "Primer Nivel",
                        "direccion": "",
                        "telefono": "",
                        "responsable": "",
                        "estado": "Activo"
                    })
                _CACHE_JERARQUIA_SEDES = {
                    "departamentos": [{"id": 1, "nombre": "La Paz", "codigo": "LPZ", "estado": "Activo"}],
                    "municipios": [{"id": 1, "departamento_id": 1, "nombre": "GAMLP", "codigo": "GAMLP", "estado": "Activo"}],
                    "redes": list(mapa_redes.values()),
                    "centros": c_list
                }
                return _CACHE_JERARQUIA_SEDES
        except Exception as e_fallback:
            print(f"[WARN] Error en fallback de sedes locales: {e_fallback}")

        return {
            "departamentos": [{"id": 1, "nombre": "La Paz", "codigo": "LPZ"}],
            "municipios": [{"id": 1, "departamento_id": 1, "nombre": "GAMLP", "codigo": "GAMLP"}],
            "redes": [
                {"id": 1, "municipio_id": 1, "nombre": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "codigo": "RED-1"},
                {"id": 2, "municipio_id": 1, "nombre": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "codigo": "RED-2"},
                {"id": 3, "municipio_id": 1, "nombre": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "codigo": "RED-3"},
                {"id": 4, "municipio_id": 1, "nombre": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "codigo": "RED-4"},
                {"id": 5, "municipio_id": 1, "nombre": "RED 5-SUR (MACRODISTRITO SUR)", "codigo": "RED-5"},
            ],
            "centros": []
        }
    try:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT id, nombre, codigo, estado FROM departamentos WHERE estado = 'Activo' ORDER BY CASE WHEN nombre='La Paz' THEN 0 ELSE 1 END, nombre ASC;")
        deptos = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT id, departamento_id, nombre, codigo, estado FROM municipios WHERE estado = 'Activo' ORDER BY id ASC;")
        muns = [dict(r) for r in cur.fetchall()]
        if not muns:
            muns = [{"id": 1, "departamento_id": 1, "nombre": "GAMLP", "codigo": "GAMLP", "estado": "Activo"}]
        
        cur.execute("SELECT id, municipio_id, departamento_id, nombre, codigo, macrodistrito, responsable, telefono, estado FROM redes_salud WHERE estado = 'Activo' ORDER BY codigo ASC;")
        redes = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT id, red_salud_id, nombre, nivel, direccion, telefono, responsable, estado FROM centros_salud WHERE estado = 'Activo' ORDER BY nombre ASC;")
        centros = [dict(r) for r in cur.fetchall()]

        if perfil == 'historica':
            try:
                cur.execute("SELECT UPPER(TRIM(centro_salud_nombre)), COUNT(*) FROM equipos GROUP BY UPPER(TRIM(centro_salud_nombre));")
                conteo_map = {r[0]: r[1] for r in cur.fetchall() if r[0]}
                for c in centros:
                    c_nom = c['nombre'].strip().upper()
                    c['total_equipos'] = conteo_map.get(c_nom, 0)
            except Exception as ec:
                print(f"[WARN] Error calculando conteo por centro histórico: {ec}")
        
        cur.close()
        conn.close()
        if perfil:
            return {
                "departamentos": deptos,
                "municipios": muns,
                "redes": redes,
                "centros": centros
            }
        _CACHE_JERARQUIA_SEDES = {
            "departamentos": deptos,
            "municipios": muns,
            "redes": redes,
            "centros": centros
        }
        # Guardar en archivo local para uso offline
        try:
            with open(_obtener_ruta_cache_sedes(), "w", encoding="utf-8") as f:
                json.dump(_CACHE_JERARQUIA_SEDES, f, indent=2)
        except Exception as fe:
            print(f"[WARN] No se pudo guardar caché persistente de sedes: {fe}")
            
        return _CACHE_JERARQUIA_SEDES
    except Exception as e:
        print("[WARN] Error obteniendo jerarquía de sedes:", e)
        if conn:
            conn.close()
        if _CACHE_JERARQUIA_SEDES:
            return _CACHE_JERARQUIA_SEDES
        return {
            "departamentos": [{"id": 1, "nombre": "La Paz", "codigo": "LPZ", "estado": "Activo"}],
            "municipios": [{"id": 1, "departamento_id": 1, "nombre": "GAMLP", "codigo": "GAMLP", "estado": "Activo"}],
            "redes": [],
            "centros": []
        }

def invalidar_cache_jerarquia():
    global _CACHE_JERARQUIA_SEDES
    _CACHE_JERARQUIA_SEDES = None

def guardar_centro_salud_db(datos):
    """Inserta o actualiza un Centro de Salud / Hospital en la base de datos."""
    invalidar_cache_jerarquia()
    conn = obtener_conexion()
    if not conn:
        return False, "Error al conectar con la base de datos"
    try:
        cur = conn.cursor()
        c_id = datos.get("id")
        red_id = datos.get("red_salud_id")
        nombre = datos.get("nombre", "").strip()
        nivel = datos.get("nivel", "Primer Nivel").strip()
        direccion = datos.get("direccion", "").strip()
        telefono = datos.get("telefono", "").strip()
        responsable = datos.get("responsable", "").strip()
        estado = datos.get("estado", "Activo").strip()

        if not nombre:
            conn.close()
            return False, "El nombre del centro de salud es obligatorio."

        if c_id:
            cur.execute("""
                UPDATE centros_salud 
                SET red_salud_id = %s, nombre = %s, nivel = %s, direccion = %s, telefono = %s, responsable = %s, estado = %s
                WHERE id = %s;
            """, (red_id, nombre, nivel, direccion, telefono, responsable, estado, c_id))
            ret_id = c_id
        else:
            cur.execute("""
                INSERT INTO centros_salud (red_salud_id, nombre, nivel, direccion, telefono, responsable, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (red_id, nombre, nivel, direccion, telefono, responsable, estado))
            ret_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()
        return True, ret_id
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def eliminar_centro_salud_db(centro_id, eliminacion_fisica=False):
    """Elimina o desactiva un Centro de Salud."""
    invalidar_cache_jerarquia()
    conn = obtener_conexion()
    if not conn:
        return False, "Error al conectar con la base de datos"
    try:
        cur = conn.cursor()
        if eliminacion_fisica:
            cur.execute("DELETE FROM centros_salud WHERE id = %s;", (centro_id,))
        else:
            cur.execute("UPDATE centros_salud SET estado = 'Inactivo' WHERE id = %s;", (centro_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Centro de Salud eliminado correctamente"
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def guardar_red_salud_db(datos):
    """Inserta o actualiza una Red de Salud en la base de datos."""
    invalidar_cache_jerarquia()
    conn = obtener_conexion()
    if not conn:
        return False, "Error al conectar con la base de datos"
    try:
        cur = conn.cursor()
        r_id = datos.get("id")
        mun_id = datos.get("municipio_id", 1)
        dep_id = datos.get("departamento_id", 1)
        nombre = datos.get("nombre", "").strip()
        codigo = datos.get("codigo", "").strip()
        macrodistrito = datos.get("macrodistrito", "").strip()
        responsable = datos.get("responsable", "").strip()
        telefono = datos.get("telefono", "").strip()
        estado = datos.get("estado", "Activo").strip()

        if not nombre or not codigo:
            conn.close()
            return False, "El nombre y código de la Red son obligatorios."

        if r_id:
            cur.execute("""
                UPDATE redes_salud 
                SET municipio_id = %s, departamento_id = %s, nombre = %s, codigo = %s, macrodistrito = %s, responsable = %s, telefono = %s, estado = %s
                WHERE id = %s;
            """, (mun_id, dep_id, nombre, codigo, macrodistrito, responsable, telefono, estado, r_id))
            ret_id = r_id
        else:
            cur.execute("""
                INSERT INTO redes_salud (municipio_id, departamento_id, nombre, codigo, macrodistrito, responsable, telefono, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (mun_id, dep_id, nombre, codigo, macrodistrito, responsable, telefono, estado))
            ret_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()
        return True, ret_id
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def eliminar_red_salud_db(red_id):
    """Desactiva una Red de Salud."""
    invalidar_cache_jerarquia()
    conn = obtener_conexion()
    if not conn:
        return False, "Error al conectar con la base de datos"
    try:
        cur = conn.cursor()
        cur.execute("UPDATE redes_salud SET estado = 'Inactivo' WHERE id = %s;", (red_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Red de Salud desactivada correctamente"
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def guardar_municipio_db(datos):
    """Inserta o actualiza un Municipio."""
    invalidar_cache_jerarquia()
    conn = obtener_conexion()
    if not conn:
        return False, "Error de conexión"
    try:
        cur = conn.cursor()
        m_id = datos.get("id")
        dep_id = datos.get("departamento_id", 1)
        nombre = datos.get("nombre", "").strip()
        codigo = datos.get("codigo", "").strip()
        estado = datos.get("estado", "Activo").strip()

        if m_id:
            cur.execute("UPDATE municipios SET departamento_id = %s, nombre = %s, codigo = %s, estado = %s WHERE id = %s;", (dep_id, nombre, codigo, estado, m_id))
            ret_id = m_id
        else:
            cur.execute("INSERT INTO municipios (departamento_id, nombre, codigo, estado) VALUES (%s, %s, %s, %s) RETURNING id;", (dep_id, nombre, codigo, estado))
            ret_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()
        return True, ret_id
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def guardar_departamento_db(datos):
    """Inserta o actualiza un Departamento."""
    invalidar_cache_jerarquia()
    conn = obtener_conexion()
    if not conn:
        return False, "Error de conexión"
    try:
        cur = conn.cursor()
        d_id = datos.get("id")
        nombre = datos.get("nombre", "").strip()
        codigo = datos.get("codigo", "").strip()
        estado = datos.get("estado", "Activo").strip()

        if d_id:
            cur.execute("UPDATE departamentos SET nombre = %s, codigo = %s, estado = %s WHERE id = %s;", (nombre, codigo, estado, d_id))
            ret_id = d_id
        else:
            cur.execute("INSERT INTO departamentos (nombre, codigo, estado) VALUES (%s, %s, %s) RETURNING id;", (nombre, codigo, estado))
            ret_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()
        return True, ret_id
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def guardar_mueble_db(datos):
    """Inserta o actualiza un activo de Mueblería / Computación en la base de datos."""
    conn = obtener_conexion()
    if not conn:
        return False, "Error al conectar con la base de datos"
    try:
        cur = conn.cursor()
        m_id = datos.get("id")
        sector_actual = str(datos.get("sector_actual") or "SALUD").strip()
        direccion_administrativa = str(datos.get("direccion_administrativa") or "").strip()
        unidad_organizacional = str(datos.get("unidad_organizacional") or "").strip()
        fecha_asignacion = str(datos.get("fecha_asignacion") or "").strip()
        tecnico_inventareador = str(datos.get("tecnico_inventareador") or "").strip()
        persona_asignada = str(datos.get("persona_asignada") or "").strip()
        ci_asignado = str(datos.get("ci_asignado") or "").strip()
        tipo_activo = str(datos.get("tipo_activo") or "COMPUTADORA").strip()
        descripcion = str(datos.get("descripcion") or "").strip()
        marca = str(datos.get("marca") or "").strip()
        modelo = str(datos.get("modelo") or "").strip()
        serie = str(datos.get("serie") or "S/C").strip()
        detalle_transaccion = str(datos.get("detalle_transaccion") or "Asignacion 2026").strip()
        codigo_sispam = str(datos.get("codigo_sispam") or "S/C").strip()
        bertin = str(datos.get("bertin") or "S/C").strip()
        sapm = str(datos.get("sapm") or "S/C").strip()
        observaciones_de_asignacion = str(datos.get("observaciones_de_asignacion") or "").strip()
        ubicacion = str(datos.get("ubicacion") or "").strip()
        fecha_incorporacion = str(datos.get("fecha_incorporacion") or "").strip()
        red_salud_id = datos.get("red_salud_id")
        centro_salud_id = datos.get("centro_salud_id")
        cargo_asignado = str(datos.get("cargo_asignado") or "").strip()
        estado = str(datos.get("estado") or "Activo").strip()
        estado_conservacion = str(datos.get("estado_conservacion") or datos.get("estado_bien") or "Bueno").strip()

        if m_id:
            cur.execute("""
                UPDATE muebleria
                SET sector_actual = %s, direccion_administrativa = %s, unidad_organizacional = %s,
                    fecha_asignacion = %s, tecnico_inventareador = %s, persona_asignada = %s,
                    cargo_asignado = %s, ci_asignado = %s, tipo_activo = %s, descripcion = %s, marca = %s, modelo = %s,
                    serie = %s, detalle_transaccion = %s, codigo_sispam = %s, bertin = %s,
                    sapm = %s, observaciones_de_asignacion = %s, ubicacion = %s,
                    fecha_incorporacion = %s, red_salud_id = %s, centro_salud_id = %s, estado = %s,
                    estado_conservacion = %s
                WHERE id = %s;
            """, (
                sector_actual, direccion_administrativa, unidad_organizacional,
                fecha_asignacion, tecnico_inventareador, persona_asignada,
                cargo_asignado, ci_asignado, tipo_activo, descripcion, marca, modelo,
                serie, detalle_transaccion, codigo_sispam, bertin,
                sapm, observaciones_de_asignacion, ubicacion,
                fecha_incorporacion, red_salud_id, centro_salud_id, estado,
                estado_conservacion, m_id
            ))
            ret_id = m_id
        else:
            cur.execute("""
                INSERT INTO muebleria (
                    sector_actual, direccion_administrativa, unidad_organizacional,
                    fecha_asignacion, tecnico_inventareador, persona_asignada,
                    cargo_asignado, ci_asignado, tipo_activo, descripcion, marca, modelo,
                    serie, detalle_transaccion, codigo_sispam, bertin,
                    sapm, observaciones_de_asignacion, ubicacion,
                    fecha_incorporacion, red_salud_id, centro_salud_id, estado,
                    estado_conservacion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
            """, (
                sector_actual, direccion_administrativa, unidad_organizacional,
                fecha_asignacion, tecnico_inventareador, persona_asignada,
                cargo_asignado, ci_asignado, tipo_activo, descripcion, marca, modelo,
                serie, detalle_transaccion, codigo_sispam, bertin,
                sapm, observaciones_de_asignacion, ubicacion,
                fecha_incorporacion, red_salud_id, centro_salud_id, estado,
                estado_conservacion
            ))
            ret_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()
        return True, ret_id
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def eliminar_mueble_db(mueble_id, usuario="Sistema", eliminacion_fisica=False):
    """Elimina o mueve a papelera un activo de mueblería / computación."""
    conn = obtener_conexion()
    if not conn:
        return False, "Error al conectar con la base de datos"
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM muebleria WHERE id = %s;", (mueble_id,))
        mueble_row = cur.fetchone()
        if not mueble_row:
            cur.close()
            conn.close()
            return False, "El activo no fue encontrado."

        mueble_dict = dict(mueble_row)
        mover_a_papelera(cur, "muebleria", mueble_id, mueble_dict, usuario=usuario)

        if eliminacion_fisica:
            cur.execute("DELETE FROM muebleria WHERE id = %s;", (mueble_id,))
        else:
            cur.execute("UPDATE muebleria SET estado = 'Inactivo' WHERE id = %s;", (mueble_id,))

        conn.commit()
        cur.close()
        conn.close()
        return True, "Activo eliminado correctamente"
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)

def importar_muebleria_db(lista_muebles):
    """Inserta en bloque una lista de activos importados desde Excel."""
    if not lista_muebles:
        return 0, "No hay registros para importar."
    conn = obtener_conexion()
    if not conn:
        return 0, "Error de conexión a la base de datos."
    try:
        cur = conn.cursor()
        insertados = 0
        for m in lista_muebles:
            cur.execute("""
                INSERT INTO muebleria (
                    sector_actual, direccion_administrativa, unidad_organizacional,
                    fecha_asignacion, tecnico_inventareador, persona_asignada,
                    ci_asignado, tipo_activo, descripcion, marca, modelo,
                    serie, detalle_transaccion, codigo_sispam, bertin,
                    sapm, observaciones_de_asignacion, ubicacion,
                    fecha_incorporacion, red_salud_id, centro_salud_id, estado,
                    estado_conservacion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """, (
                m.get("sector_actual", "SALUD"),
                m.get("direccion_administrativa", ""),
                m.get("unidad_organizacional", ""),
                m.get("fecha_asignacion", ""),
                m.get("tecnico_inventareador", ""),
                m.get("persona_asignada", ""),
                m.get("ci_asignado", ""),
                m.get("tipo_activo", "COMPUTADORA"),
                m.get("descripcion", ""),
                m.get("marca", ""),
                m.get("modelo", ""),
                m.get("serie", "S/C") or "S/C",
                m.get("detalle_transaccion", "Asignacion 2026") or "Asignacion 2026",
                m.get("codigo_sispam", "S/C") or "S/C",
                m.get("bertin", "S/C") or "S/C",
                m.get("sapm", "S/C") or "S/C",
                m.get("observaciones_de_asignacion", ""),
                m.get("ubicacion", ""),
                m.get("fecha_incorporacion", ""),
                m.get("red_salud_id"),
                m.get("centro_salud_id"),
                m.get("estado", "Activo"),
                m.get("estado_conservacion") or m.get("estado_bien") or "Bueno"
            ))
            insertados += 1
        conn.commit()
        cur.close()
        conn.close()
        return insertados, f"Se importaron {insertados} registros de muebles y computación exitosamente."
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return 0, str(e)

def mover_a_papelera(cur, tabla_origen, id_original, datos_dict, usuario="desconocido"):
    """
    Guarda una copia del registro como snapshot JSON antes de ser eliminado de la BD.
    Operación silenciosa dentro de la misma transacción abierta con auto-recuperación de secuencia.
    """
    try:
        cur.execute("""
            INSERT INTO papelera (tabla_origen, id_original, datos, eliminado_por) 
            VALUES (%s, %s, %s, %s)
        """, (tabla_origen, str(id_original), json.dumps(datos_dict, default=str), usuario))
    except psycopg2.IntegrityError:
        # Si la secuencia de PostgreSQL quedó desfasada, reajustarla y reintentar
        try:
            cur.execute("SELECT setval(pg_get_serial_sequence('papelera', 'id'), COALESCE((SELECT MAX(id) FROM papelera), 1));")
            cur.execute("""
                INSERT INTO papelera (tabla_origen, id_original, datos, eliminado_por) 
                VALUES (%s, %s, %s, %s)
            """, (tabla_origen, str(id_original), json.dumps(datos_dict, default=str), usuario))
        except Exception as e_retry:
            print(f"[WARN] No se pudo guardar en papelera al reintentar: {e_retry}")
    except Exception as e:
        print(f"[WARN] Error no crítico al mover a papelera: {e}")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        from decimal import Decimal
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def crear_backup_json(destino_path):
    from datetime import datetime
    conn = obtener_conexion()
    if not conn:
        return False
    try:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        tablas = ["areas", "catalogo", "equipos", "historial_intervenciones", "protocolos", "repuestos", "usuarios", "papelera", "muebleria"]
        datos = {}
        for t in tablas:
            cur.execute(f'SELECT * FROM "{t}"')
            datos[t] = cur.fetchall()
        
        backup_obj = {
            "version": 1,
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tablas": datos
        }
        
        with open(destino_path, "w", encoding="utf-8") as f:
            json.dump(backup_obj, f, cls=DateTimeEncoder, indent=2)
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Error al crear backup:", e)
        if conn:
            conn.close()
        return False

def restaurar_backup_json(filepath):
    """
    Restaura de forma robusta y atómica la base de datos a partir de un archivo JSON.
    - Asegura que el esquema de tablas e índices exista.
    - Usa SAVEPOINTS para que errores individuales no anulen la transacción completa.
    - Filtra dinámicamente las columnas para tolerar diferencias de esquemas entre versiones.
    """
    import psycopg2.extras
    
    # 1. Asegurar que las tablas existan antes de insertar
    inicializar_bd()
    try:
        from auth import inicializar_usuarios
        inicializar_usuarios()
    except:
        pass

    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo conectar a la base de datos PostgreSQL."
    
    cur = conn.cursor()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            backup_obj = json.load(f)

        tablas_data = backup_obj.get("tablas", {})
        if not tablas_data:
            return False, "El archivo de respaldo no contiene datos de tablas."

        # 2. Orden correcto de vaciado: primero tablas dependientes/secundarias
        tablas_orden_borrado = [
            "papelera",
            "muebleria",
            "historial_intervenciones",
            "protocolos",
            "equipos",
            "repuestos",
            "catalogo",
            "areas",
            "usuarios",
        ]
        for t in tablas_orden_borrado:
            try:
                cur.execute(f'TRUNCATE TABLE "{t}" RESTART IDENTITY CASCADE;')
            except Exception as te:
                print(f"[WARN] No se pudo truncar {t}: {te}")

        # 3. Orden de inserción
        tablas_orden_insercion = [
            "usuarios",
            "areas",
            "catalogo",
            "repuestos",
            "equipos",
            "historial_intervenciones",
            "protocolos",
            "muebleria",
            "papelera",
        ]

        total_filas_restauradas = 0
        conteo_por_tabla = {}

        for t in tablas_orden_insercion:
            rows = tablas_data.get(t)
            if not rows:
                continue

            # Obtener las columnas reales existentes en la tabla destino
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s;
            """, (t,))
            cols_db_info = {r[0]: r[1] for r in cur.fetchall()}
            if not cols_db_info:
                print(f"[WARN] La tabla {t} no existe en la base de datos destino.")
                continue

            filas_insertadas_tabla = 0
            for r in rows:
                # Filtrar solo columnas que existen en la BD destino
                cols_filtradas = [c for c in r.keys() if c in cols_db_info]
                if not cols_filtradas:
                    continue

                col_str = ", ".join([f'"{c}"' for c in cols_filtradas])
                val_placeholders = ", ".join(["%s"] * len(cols_filtradas))
                insert_sql = f'INSERT INTO "{t}" ({col_str}) VALUES ({val_placeholders}) ON CONFLICT DO NOTHING;'

                vals = []
                for c in cols_filtradas:
                    val = r[c]
                    # Manejo de JSONB
                    if cols_db_info.get(c) == 'jsonb' or isinstance(val, (dict, list)):
                        if isinstance(val, (dict, list)):
                            vals.append(psycopg2.extras.Json(val))
                        elif isinstance(val, str) and len(val) > 0 and val[0] in ('{', '['):
                            try:
                                vals.append(psycopg2.extras.Json(json.loads(val)))
                            except:
                                vals.append(psycopg2.extras.Json(val))
                        else:
                            vals.append(psycopg2.extras.Json(val) if val is not None else None)
                    else:
                        vals.append(val)

                # Usar SAVEPOINT por fila para evitar abortar la transacción completa si una fila falla
                cur.execute("SAVEPOINT fila_sp;")
                try:
                    cur.execute(insert_sql, vals)
                    cur.execute("RELEASE SAVEPOINT fila_sp;")
                    filas_insertadas_tabla += 1
                except Exception as row_err:
                    cur.execute("ROLLBACK TO SAVEPOINT fila_sp;")
                    print(f"[WARN] Error insertando fila en {t}: {row_err}")

            conteo_por_tabla[t] = filas_insertadas_tabla
            total_filas_restauradas += filas_insertadas_tabla

        # 4. Resetear y sincronizar secuencias de auto-incremento
        tablas_con_serial = ["usuarios", "areas", "catalogo", "repuestos", "historial_intervenciones", "protocolos", "papelera", "muebleria"]
        for t in tablas_con_serial:
            try:
                cur.execute(f"SELECT setval(pg_get_serial_sequence('{t}', 'id'), COALESCE((SELECT MAX(id) FROM \"{t}\"), 1));")
            except Exception as seq_err:
                pass

        conn.commit()
        cur.close()
        conn.close()

        resumen = ", ".join([f"{k}: {v}" for k, v in conteo_por_tabla.items() if v > 0])
        return True, f"Se restauraron exitosamente {total_filas_restauradas} registros ({resumen})."

    except Exception as e:
        print("[ERROR] Error general al restaurar backup:", e)
        import traceback; traceback.print_exc()
        try:
            conn.rollback()
            cur.close()
            conn.close()
        except:
            pass
        return False, str(e)


def crear_paquete_migracion(destino_zip):
    """
    Empaqueta en un único archivo ZIP comprimido:
      1. La base de datos completa exportada en JSON.
      2. Todas las carpetas del sistema (Fotos_Equipos, Fotos_Repuestos, Areas, Manuales, Videos, Cronogramas, Protocolos).
    """
    import os
    import zipfile
    import tempfile
    import shutil
    from config import BASE_DIR
    
    # 1. Crear backup temporal de base de datos
    temp_dir = tempfile.mkdtemp()
    temp_json = os.path.join(temp_dir, "backup_base_datos.json")
    if not crear_backup_json(temp_json):
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False, "No se pudo generar el respaldo de la base de datos."

    try:
        with zipfile.ZipFile(destino_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            # Añadir el archivo JSON principal
            zf.write(temp_json, "backup_base_datos.json")

            # Añadir las carpetas de Datos_De_Gestion_GAMLP
            if os.path.exists(BASE_DIR):
                for root, dirs, files in os.walk(BASE_DIR):
                    # No incluir la carpeta de respaldos dentro del paquete
                    if "Respaldos_BD" in root:
                        continue
                    for file in files:
                        filepath = os.path.join(root, file)
                        rel_path = os.path.relpath(filepath, BASE_DIR)
                        arcname = os.path.join("archivos_gestion", rel_path)
                        zf.write(filepath, arcname)

        shutil.rmtree(temp_dir, ignore_errors=True)
        return True, "Paquete completo generado exitosamente."
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False, f"Error al crear paquete: {e}"


def restaurar_paquete_migracion(origen_zip):
    """
    Descomprime un paquete ZIP en la nueva computadora:
      1. Extrae todas las fotos, manuales y documentos a Datos_De_Gestion_GAMLP.
      2. Restaura toda la base de datos PostgreSQL usando el backup_base_datos.json incluido.
    """
    import os
    import zipfile
    import tempfile
    import shutil
    from config import BASE_DIR

    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(origen_zip, "r") as zf:
            zf.extractall(temp_dir)

        # 1. Descomprimir archivos_gestion en BASE_DIR
        origen_archivos = os.path.join(temp_dir, "archivos_gestion")
        if os.path.exists(origen_archivos):
            os.makedirs(BASE_DIR, exist_ok=True)
            for item in os.listdir(origen_archivos):
                s = os.path.join(origen_archivos, item)
                d = os.path.join(BASE_DIR, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        # 2. Restaurar la base de datos
        json_path = os.path.join(temp_dir, "backup_base_datos.json")
        if not os.path.exists(json_path):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False, "El archivo del paquete no contiene 'backup_base_datos.json'."

        exito, msg = restaurar_backup_json(json_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return exito, msg

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False, f"Error al procesar paquete: {e}"


def calcular_proximos_mantenimientos(eq, cantidad=1, hoy=None):
    """
    Función centralizada para calcular las próximas fechas de mantenimiento preventivo de un equipo.
    Parámetros:
      - eq: dict con datos del equipo (criticidad, garantia, fecha_adquisicion, etc.)
      - cantidad: número de fechas futuras deseadas (por ej. 1 para f_prox, 3 para la ficha técnica)
      - hoy: fecha de referencia (por defecto date.today())
    Retorna:
      - Lista de objetos datetime.date con las próximas fechas programadas no completadas.
    """
    from datetime import date, datetime
    from dateutil.relativedelta import relativedelta

    if hoy is None:
        hoy = date.today()

    if eq.get("estado") == "Baja":
        return []

    crit = str(eq.get("criticidad") or "Riesgo Medio")
    meses = 3 if "Alto" in crit else (4 if "Medio" in crit else 6)

    # 1. Determinar fecha de inicio del ciclo
    f_reg = eq.get("fecha_adquisicion") or eq.get("fecha_registro", hoy)
    if isinstance(f_reg, str):
        try:
            f_reg = datetime.strptime(f_reg, "%Y-%m-%d").date()
        except:
            f_reg = hoy
    elif isinstance(f_reg, datetime):
        f_reg = f_reg.date()
    elif not f_reg:
        f_reg = hoy

    # 2. Considerar garantía si aplica
    if eq.get("garantia") == "Con Garantía" and eq.get("fecha_vencimiento_garantia"):
        f_venc_g = eq.get("fecha_vencimiento_garantia")
        if isinstance(f_venc_g, str):
            try:
                f_venc_g = datetime.strptime(f_venc_g, "%Y-%m-%d").date()
            except:
                f_venc_g = None
        elif isinstance(f_venc_g, datetime):
            f_venc_g = f_venc_g.date()
        if f_venc_g:
            f_reg = f_venc_g + relativedelta(days=+1)

    # 3. Iterar por slots mensuales y verificar si ya fue completado
    resultados = []
    f_check = f_reg
    iter_count = 0
    historial = eq.get("historial_intervenciones", [])

    while len(resultados) < cantidad and iter_count < 60:
        iter_count += 1
        f_check = f_check + relativedelta(months=+meses)

        slot_is_completed = False
        for m in historial:
            if m.get("tipo") == "Preventivo":
                m_prog = m.get("fecha_programada")
                if m_prog:
                    if isinstance(m_prog, str):
                        try:
                            m_prog_d = datetime.strptime(m_prog, "%Y-%m-%d").date()
                        except:
                            m_prog_d = None
                    elif isinstance(m_prog, datetime):
                        m_prog_d = m_prog.date()
                    else:
                        m_prog_d = m_prog
                    if m_prog_d == f_check:
                        slot_is_completed = True
                        break
                else:
                    m_f = m.get("fecha")
                    if isinstance(m_f, str):
                        try:
                            m_f_d = datetime.strptime(m_f, "%Y-%m-%d").date()
                        except:
                            m_f_d = None
                    elif isinstance(m_f, datetime):
                        m_f_d = m_f.date()
                    else:
                        m_f_d = m_f
                    if m_f_d and m_f_d.year == f_check.year and m_f_d.month == f_check.month:
                        slot_is_completed = True
                        break

        if not slot_is_completed:
            resultados.append(f_check)

    return resultados


# ========================================================
# 🚀 MOTOR DE ALTA VELOCIDAD: CACHÉ LOCAL + HILOS ASÍNCRONOS
# ========================================================
import threading

def ejecutar_en_segundo_plano(func, *args, **kwargs):
    """Ejecuta operaciones SQL en segundo plano sin congelar la interfaz de usuario."""
    t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t

def _obtener_ruta_cache_datos():
    db_host_key = str(CONFIG.get("db_host", "default")).replace(":", "_").replace("/", "_").replace(".", "_")
    db_user_key = str(CONFIG.get("db_user", "postgres")).replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(os.path.expanduser("~"), f".gamlp_data_cache_{db_host_key}_{db_user_key}.json")

def _obtener_ruta_cola_offline():
    db_host_key = str(CONFIG.get("db_host", "default")).replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(os.path.expanduser("~"), f".gamlp_offline_queue_{db_host_key}.json")

def guardar_cache_local_datos(datos_dict):
    """Guarda una copia de respaldo de lectura de todos los datos en el disco local."""
    import os, json
    ruta = _obtener_ruta_cache_datos()
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos_dict, f, cls=DateTimeEncoder, indent=2)
    except Exception as e:
        print(f"[WARN] No se pudo guardar caché local de datos: {e}")

def cargar_cache_local_datos():
    """Recupera la última versión en caché de forma ultrarrápida."""
    import os, json
    ruta = _obtener_ruta_cache_datos()
    if not os.path.exists(ruta):
        return None
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Error al leer caché local de datos: {e}")
        return None

def guardar_mantenimiento_offline_cola(intervencion):
    """Almacena una intervención realizada en la cola local para sincronización."""
    import os, json
    ruta = _obtener_ruta_cola_offline()
    try:
        cola = []
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                cola = json.load(f)
        cola.append(intervencion)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(cola, f, cls=DateTimeEncoder, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar en cola offline: {e}")
        return False

def sincronizar_mantenimientos_offline_cola():
    """Sube a PostgreSQL todas las intervenciones pendientes guardadas en cola."""
    import os, json
    ruta = _obtener_ruta_cola_offline()
    if not os.path.exists(ruta):
        return 0, "No hay pendientes."
    
    conn = obtener_conexion()
    if not conn:
        return 0, "Sin conexión al servidor."

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            cola = json.load(f)
        if not cola:
            return 0, "Cola vacía."

        cur = conn.cursor()
        sincronizados = 0
        pendientes_restantes = []

        for item in cola:
            try:
                cur.execute("""
                    INSERT INTO historial_intervenciones 
                    (equipo_id, fecha, tipo, detalle, condicion, estado_equipo, deficiencia, trabajo, observaciones, fecha_entrega, servicio_ht, tipo_ht, repuesto_usado, repuesto_nombre, repuesto_cantidad, fecha_programada, realizado_por, hora_entrega, tiempo_reparacion) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    item.get('equipo_id'), item.get('fecha'), item.get('tipo'), item.get('detalle'), item.get('condicion'), item.get('estado_equipo'),
                    item.get('deficiencia'), item.get('trabajo'), item.get('observaciones'), item.get('fecha_entrega'), item.get('servicio_ht'), item.get('tipo_ht'),
                    item.get('repuesto_usado', False), item.get('repuesto_nombre', ''), item.get('repuesto_cantidad', 0), item.get('fecha_programada'), item.get('realizado_por'), item.get('hora_entrega'), item.get('tiempo_reparacion', 0.0)
                ))

                if item.get('repuesto_usado') and item.get('repuesto_nombre'):
                    cur.execute("""
                        UPDATE repuestos 
                        SET cantidad = GREATEST(0, cantidad - %s) 
                        WHERE nombre_repuesto = %s
                    """, (item.get('repuesto_cantidad', 0), item.get('repuesto_nombre')))

                sincronizados += 1
            except Exception as item_err:
                print(f"[WARN] Error al sincronizar item offline: {item_err}")
                pendientes_restantes.append(item)

        conn.commit()
        cur.close()
        conn.close()

        if pendientes_restantes:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(pendientes_restantes, f, cls=DateTimeEncoder, indent=2)
        else:
            try:
                os.remove(ruta)
            except:
                pass

        return sincronizados, f"Se sincronizaron {sincronizados} reportes pendientes."
    except Exception as e:
        print(f"[ERROR] Error durante sincronización offline: {e}")

def _obtener_ruta_cola_equipos():
    db_host_key = str(CONFIG.get("db_host", "default")).replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(os.path.expanduser("~"), f".gamlp_offline_equipos_{db_host_key}.json")

def _obtener_ruta_cola_muebles():
    db_host_key = str(CONFIG.get("db_host", "default")).replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(os.path.expanduser("~"), f".gamlp_offline_muebles_{db_host_key}.json")

def _obtener_ruta_cola_areas():
    db_host_key = str(CONFIG.get("db_host", "default")).replace(":", "_").replace("/", "_").replace(".", "_")
    return os.path.join(os.path.expanduser("~"), f".gamlp_offline_areas_{db_host_key}.json")

# =========================================================================
# GENERADOR INTELIGENTE DE CÓDIGOS DE ACTIVO FIJO (AF)
# Formato GAMLP: GAMLP-{RED}-{CENTRO}-{CORRELATIVO 6 DÍGITOS}
# Ejemplo: GAMLP-R1-BSP-000001
# =========================================================================

def generar_codigo_red(nombre_red):
    """Extrae el identificador de red en formato R1, R2, etc."""
    if not nombre_red:
        return "R1"
    import re
    m = re.search(r'RED\s*(\d+)', str(nombre_red), re.IGNORECASE)
    if m:
        return f"R{m.group(1)}"
    m2 = re.search(r'(\d+)', str(nombre_red))
    if m2:
        return f"R{m2.group(1)}"
    return "R1"

def generar_sigla_centro(nombre_centro):
    """
    Genera las iniciales representativas del centro de salud.
    Ejemplos:
      'Bajo San Pedro' -> 'BSP'
      'C.S. Bajo Tacagua' -> 'BT'
      'C.S. 8 de Diciembre' -> '8D'
      'Asistencia Publica' -> 'AP'
      'Bolognia' -> 'BOL'
    """
    if not nombre_centro:
        return "GEN"
    import re
    s = str(nombre_centro).upper().strip()
    s = re.sub(r'^(C\.?S\.?M\.?I\.?|C\.?M\.?I\.?|C\.?S\.?|POSTA|HOSPITAL)\s*', '', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    stopwords = {'DE', 'DEL', 'LA', 'EL', 'LOS', 'LAS', 'Y', 'EN', 'AL'}
    palabras = [p for p in s.split() if p not in stopwords]
    if not palabras:
        palabras = [p for p in s.split() if p]
    if not palabras:
        return "GEN"
    if len(palabras) == 1:
        p = palabras[0]
        return p[:3] if len(p) >= 3 else p
    else:
        return ''.join(p[0] for p in palabras)

def generar_siguiente_codigo_af(red_nom, cen_nom, equipos_existentes=None, cola_offline=None):
    """
    Calcula el siguiente código de Activo Fijo (AF) asegurando que no colisione
    con los equipos existentes en memoria local, en cola offline ni en la base central.
    """
    rcod = generar_codigo_red(red_nom)
    csig = generar_sigla_centro(cen_nom)
    prefijo = f"GAMLP-{rcod}-{csig}-"
    numeros = []

    # 1. Revisar equipos locales en memoria
    if equipos_existentes:
        for eq in equipos_existentes:
            eq_id = str(eq.get("id") or "").strip().upper()
            if eq_id.startswith(prefijo.upper()):
                sufijo = eq_id[len(prefijo):]
                if sufijo.isdigit():
                    numeros.append(int(sufijo))

    # 2. Revisar cola offline de equipos pendientes
    if cola_offline is None:
        cola_offline = obtener_cola_equipos_offline()
    if cola_offline:
        for eq in cola_offline:
            eq_id = str(eq.get("id") or "").strip().upper()
            if eq_id.startswith(prefijo.upper()):
                sufijo = eq_id[len(prefijo):]
                if sufijo.isdigit():
                    numeros.append(int(sufijo))

    # 3. Si hay conexión directa a PostgreSQL, consultar correlativo más alto
    try:
        conn = obtener_conexion()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM equipos WHERE id LIKE %s;", (f"{prefijo}%",))
            for row in cur.fetchall():
                eq_id = str(row[0] or "").strip().upper()
                if eq_id.startswith(prefijo.upper()):
                    sufijo = eq_id[len(prefijo):]
                    if sufijo.isdigit():
                        numeros.append(int(sufijo))
            cur.close()
            conn.close()
    except Exception:
        pass

    siguiente = max(numeros, default=0) + 1
    return f"{prefijo}{siguiente:06d}"

def obtener_areas_db(centro_nombre=None, perfil=None):
    """Retorna las áreas registradas en el sistema, opcionalmente filtradas por centro de salud."""
    conn = obtener_conexion(perfil=perfil)
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if centro_nombre:
                cur.execute("""
                    SELECT id, nombre, piso, encargado, cargo, ci_encargado, contacto, centro_salud_nombre, red_salud_nombre 
                    FROM areas 
                    WHERE centro_salud_nombre = %s OR centro_salud_nombre ILIKE %s 
                    ORDER BY piso DESC, nombre ASC;
                """, (centro_nombre, f"%{centro_nombre}%"))
            else:
                cur.execute("""
                    SELECT id, nombre, piso, encargado, cargo, ci_encargado, contacto, centro_salud_nombre, red_salud_nombre 
                    FROM areas 
                    ORDER BY piso DESC, nombre ASC;
                """)
            areas = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return areas
        except Exception as e:
            print(f"[WARN] Error al obtener áreas desde BD ({perfil}): {e}")
            try: conn.close()
            except: pass
    return []

def obtener_catalogo_equipos_db(perfil=None):
    """Retorna los modelos de equipos médicos configurados en el catálogo central."""
    conn = obtener_conexion(perfil=perfil)
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM catalogo ORDER BY nombre ASC;")
            cats = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return cats
        except Exception as e:
            print(f"[WARN] Error al obtener catálogo de BD ({perfil}): {e}")
            try: conn.close()
            except: pass
    return []

def obtener_equipos_db(centro_nombre=None, limite=300, perfil=None, red_nombre=None):
    """Retorna equipos médicos con todos sus campos para inventario y edición web."""
    conn = obtener_conexion(perfil=perfil)
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            conds = ["COALESCE(estado, 'Operativo') NOT IN ('Inactivo', 'Eliminado')"]
            params = []
            if centro_nombre and not str(centro_nombre).startswith("["):
                conds.append("(centro_salud_nombre = %s OR centro_salud_nombre ILIKE %s)")
                params.extend([centro_nombre, f"%{centro_nombre}%"])
            if red_nombre and not str(red_nombre).startswith("["):
                conds.append("(red_salud_nombre = %s OR red_salud_nombre ILIKE %s)")
                params.extend([red_nombre, f"%{red_nombre}%"])

            where_clause = ("WHERE " + " AND ".join(conds)) if conds else ""
            query = f"SELECT * FROM equipos {where_clause} ORDER BY id DESC LIMIT %s;"
            params.append(limite)

            cur.execute(query, tuple(params))
            filas = cur.fetchall()
            res = []
            for r in filas:
                d = dict(r)
                for k, v in d.items():
                    if hasattr(v, "isoformat"):
                        d[k] = v.isoformat()
                res.append(d)
            cur.close()
            conn.close()
            return res
        except Exception as e:
            print(f"[WARN] Error al obtener equipos desde BD ({perfil}): {e}")
            try: conn.close()
            except: pass
    return []

def obtener_muebles_db(centro_nombre=None, limite=300, perfil=None, red_nombre=None):
    """Retorna los activos de mueblería y computación con todos sus campos."""
    conn = obtener_conexion(perfil=perfil)
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            conds = ["COALESCE(estado, 'Activo') NOT IN ('Inactivo', 'Eliminado')"]
            params = []
            if centro_nombre and not str(centro_nombre).startswith("["):
                conds.append("(ubicacion ILIKE %s OR descripcion ILIKE %s OR unidad_organizacional ILIKE %s)")
                params.extend([f"%{centro_nombre}%", f"%{centro_nombre}%", f"%{centro_nombre}%"])
            if red_nombre and not str(red_nombre).startswith("["):
                conds.append("(ubicacion ILIKE %s OR descripcion ILIKE %s OR unidad_organizacional ILIKE %s)")
                params.extend([f"%{red_nombre}%", f"%{red_nombre}%", f"%{red_nombre}%"])

            where_clause = ("WHERE " + " AND ".join(conds)) if conds else ""
            query = f"SELECT * FROM muebleria {where_clause} ORDER BY id DESC LIMIT %s;"
            params.append(limite)

            cur.execute(query, tuple(params))
            filas = cur.fetchall()
            res = []
            for r in filas:
                d = dict(r)
                for k, v in d.items():
                    if hasattr(v, "isoformat"):
                        d[k] = v.isoformat()
                res.append(d)
            cur.close()
            conn.close()
            return res
        except Exception as e:
            print(f"[WARN] Error al obtener muebles desde BD ({perfil}): {e}")
            try: conn.close()
            except: pass
    return []

def guardar_area_db(datos):
    """Inserta o actualiza un área en la base de datos PostgreSQL."""
    conn = obtener_conexion()
    a_dict = dict(datos)
    if not conn:
        guardar_area_offline_cola(a_dict)
        return True, "Guardado en cola offline (sin conexión)"
    try:
        cur = conn.cursor()
        cen_id = a_dict.get("centro_salud_id")
        cen_nom = str(a_dict.get("centro_salud_nombre") or "").strip()
        red_nom = str(a_dict.get("red_salud_nombre") or "").strip()
        nom = str(a_dict.get("nombre") or "").strip()
        piso = str(a_dict.get("piso") or "").strip()
        contacto = str(a_dict.get("contacto") or "").strip()
        encargado = str(a_dict.get("encargado") or "").strip()
        cargo = str(a_dict.get("cargo") or "").strip()
        ci_enc = str(a_dict.get("ci_encargado") or "").strip()

        if not cen_id and cen_nom:
            cur.execute("SELECT id FROM centros_salud WHERE nombre = %s OR nombre ILIKE %s LIMIT 1;", (cen_nom, f"%{cen_nom}%"))
            c_row = cur.fetchone()
            if c_row: cen_id = c_row[0]

        a_id = a_dict.get("id")
        if a_id:
            cur.execute("""
                UPDATE areas 
                SET centro_salud_id=%s, centro_salud_nombre=%s, red_salud_nombre=%s,
                    nombre=%s, piso=%s, contacto=%s, encargado=%s, cargo=%s, ci_encargado=%s 
                WHERE id=%s;
            """, (cen_id, cen_nom, red_nom, nom, piso, contacto, encargado, cargo, ci_enc, a_id))
        else:
            cur.execute("""
                INSERT INTO areas (centro_salud_id, centro_salud_nombre, red_salud_nombre, nombre, piso, contacto, encargado, cargo, ci_encargado) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (cen_id, cen_nom, red_nom, nom, piso, contacto, encargado, cargo, ci_enc))
            new_id = cur.fetchone()[0]
            a_dict["id"] = new_id

        conn.commit()
        cur.close()
        conn.close()
        return True, "Área guardada exitosamente"
    except Exception as e:
        if conn:
            try: conn.rollback(); conn.close()
            except: pass
        guardar_area_offline_cola(a_dict)
        return True, f"Guardado en cola offline: {e}"

def guardar_catalogo_db(datos):
    """Inserta o actualiza un modelo en el catálogo central."""
    conn = obtener_conexion()
    if not conn:
        return False, "Sin conexión a la base de datos"
    try:
        cur = conn.cursor()
        nom = str(datos.get("nombre") or "").strip()
        mar = str(datos.get("marca") or "").strip()
        mdl = str(datos.get("modelo") or "").strip()
        ar = str(datos.get("area") or "").strip()
        ps = str(datos.get("piso") or "").strip()

        c_id = datos.get("id")
        if c_id:
            cur.execute("""
                UPDATE catalogo 
                SET nombre = %s, marca = %s, modelo = %s, area = %s, piso = %s 
                WHERE id = %s;
            """, (nom, mar, mdl, ar, ps, c_id))
        else:
            cur.execute("""
                INSERT INTO catalogo (nombre, marca, modelo, area, piso) 
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (nom, mar, mdl, ar, ps))
            c_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return True, c_id
    except Exception as e:
        if conn:
            try: conn.rollback(); conn.close()
            except: pass
        return False, str(e)

def obtener_repuestos_db(centro_nombre=None, limite=300):
    """Retorna la lista de repuestos en stock."""
    conn = obtener_conexion()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if centro_nombre and not str(centro_nombre).startswith("["):
                cur.execute("""
                    SELECT id, tipo_equipo, nombre_repuesto, red_salud_nombre, centro_salud_nombre,
                           area, marca, modelo, modelo_parte, cantidad, costo, estado_disponibilidad,
                           caracteristicas, observaciones, foto
                    FROM repuestos 
                    WHERE centro_salud_nombre = %s OR centro_salud_nombre ILIKE %s 
                    ORDER BY nombre_repuesto ASC LIMIT %s;
                """, (centro_nombre, f"%{centro_nombre}%", limite))
            else:
                cur.execute("""
                    SELECT id, tipo_equipo, nombre_repuesto, red_salud_nombre, centro_salud_nombre,
                           area, marca, modelo, modelo_parte, cantidad, costo, estado_disponibilidad,
                           caracteristicas, observaciones, foto
                    FROM repuestos 
                    ORDER BY nombre_repuesto ASC LIMIT %s;
                """, (limite,))
            res = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return res
        except Exception as e:
            print(f"[WARN] Error al obtener repuestos desde BD: {e}")
            try: conn.close()
            except: pass
    return []

def guardar_repuesto_db(datos):
    """Inserta o actualiza un repuesto en la base de datos."""
    conn = obtener_conexion()
    if not conn:
        return False, "Sin conexión a la base de datos"
    try:
        cur = conn.cursor()
        r = dict(datos)
        t_eq = str(r.get("tipo_equipo") or "Médico").strip()
        n_rep = str(r.get("nombre_repuesto") or "").strip()
        red_r = str(r.get("red_salud_nombre") or "").strip()
        cen_r = str(r.get("centro_salud_nombre") or "").strip()
        area_r = str(r.get("area") or "").strip()
        marca_r = str(r.get("marca") or "").strip()
        mod_r = str(r.get("modelo") or "").strip()
        mod_p = str(r.get("modelo_parte") or mod_r).strip()
        cant_r = int(r.get("cantidad") or 1)
        cos_r = float(r.get("costo") or 0.0)
        est_r = str(r.get("estado_disponibilidad") or "En Stock").strip()
        car_r = str(r.get("caracteristicas") or "").strip()
        obs_r = str(r.get("observaciones") or "").strip()
        fot_r = str(r.get("foto") or "").strip()

        r_id = r.get("id")
        if r_id:
            cur.execute("""
                UPDATE repuestos 
                SET tipo_equipo=%s, nombre_repuesto=%s, red_salud_nombre=%s, centro_salud_nombre=%s, 
                    area=%s, marca=%s, modelo=%s, modelo_parte=%s, cantidad=%s, 
                    costo=%s, estado_disponibilidad=%s, caracteristicas=%s, observaciones=%s, foto=%s 
                WHERE id=%s;
            """, (t_eq, n_rep, red_r, cen_r, area_r, marca_r, mod_r, mod_p, cant_r, cos_r, est_r, car_r, obs_r, fot_r, r_id))
        else:
            cur.execute("""
                INSERT INTO repuestos (tipo_equipo, nombre_repuesto, red_salud_nombre, centro_salud_nombre, area, marca, modelo, modelo_parte, cantidad, costo, estado_disponibilidad, caracteristicas, observaciones, foto) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (t_eq, n_rep, red_r, cen_r, area_r, marca_r, mod_r, mod_p, cant_r, cos_r, est_r, car_r, obs_r, fot_r))
            new_id = cur.fetchone()[0]
            r["id"] = new_id

        conn.commit()
        cur.close()
        conn.close()
        return True, "Repuesto guardado exitosamente"
    except Exception as e:
        if conn:
            try: conn.rollback(); conn.close()
            except: pass
        return False, str(e)

def obtener_usuarios_db():
    """Retorna la lista de usuarios registrados con sus roles, permisos y estado."""
    conn = obtener_conexion()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT id, nombre_usuario, nombre_completo, rol, activo, permisos, sello_firma
            FROM usuarios
            ORDER BY CASE WHEN rol='jefe' OR rol='administrador' OR rol='Administrador' THEN 0 ELSE 1 END, nombre_completo ASC
        """)
        filas = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        for f in filas:
            if isinstance(f.get("permisos"), str):
                try: f["permisos"] = json.loads(f["permisos"])
                except: f["permisos"] = {}
            elif not f.get("permisos"):
                f["permisos"] = {}
        return filas
    except Exception as e:
        print(f"[ERROR] Error en obtener_usuarios_db: {e}")
        try: conn.close()
        except: pass
        return []

def guardar_usuario_permisos_db(datos):
    """Crea o actualiza los datos, rol y matriz de permisos JSONB de un usuario."""
    ci = str(datos.get("nombre_usuario") or "").strip()
    nombre = str(datos.get("nombre_completo") or "").strip()
    rol_raw = str(datos.get("rol") or "tecnico").strip()
    rol = "jefe" if rol_raw.lower() in ["administrador", "admin", "jefe"] else rol_raw.lower()
    password = str(datos.get("password") or "").strip()
    permisos = datos.get("permisos") or {}
    activo = bool(datos.get("activo", True))

    if not ci or not nombre:
        return False, "C.I. y Nombre Completo son requeridos."

    conn = obtener_conexion()
    if not conn:
        return False, "Error conectando a la base de datos."

    try:
        from auth import hash_password
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM usuarios WHERE nombre_usuario = %s", (ci,))
        row = cur.fetchone()

        permisos_json = psycopg2.extras.Json(permisos)

        if row:
            if password:
                pwd_h = hash_password(password)
                cur.execute("""
                    UPDATE usuarios
                    SET nombre_completo = %s, rol = %s, permisos = %s, activo = %s, password_hash = %s
                    WHERE nombre_usuario = %s
                """, (nombre, rol, permisos_json, activo, pwd_h, ci))
            else:
                cur.execute("""
                    UPDATE usuarios
                    SET nombre_completo = %s, rol = %s, permisos = %s, activo = %s
                    WHERE nombre_usuario = %s
                """, (nombre, rol, permisos_json, activo, ci))
        else:
            if not password:
                cur.close()
                conn.close()
                return False, "Debe proporcionar una contraseña para un nuevo usuario."
            pwd_h = hash_password(password)
            cur.execute("""
                INSERT INTO usuarios (nombre_usuario, nombre_completo, password_hash, rol, permisos, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (ci, nombre, pwd_h, rol, permisos_json, activo))

        conn.commit()
        cur.close()
        conn.close()
        return True, "Usuario y permisos guardados exitosamente."
    except Exception as e:
        print(f"[ERROR] Error al guardar usuario/permisos: {e}")
        try: conn.rollback(); conn.close()
        except: pass
        return False, str(e)

def obtener_intervenciones_db(centro_nombre=None, equipo_id=None, limite=100):
    """Retorna historial de intervenciones y mantenimientos técnicos."""
    conn = obtener_conexion()
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        params = []
        where_clauses = []

        if equipo_id:
            where_clauses.append("h.equipo_id = %s")
            params.append(str(equipo_id).strip())

        if centro_nombre and not str(centro_nombre).startswith("["):
            where_clauses.append("(e.centro_salud_nombre = %s OR e.centro_salud_nombre ILIKE %s)")
            params.extend([centro_nombre, f"%{centro_nombre}%"])

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        query = f"""
            SELECT h.id, h.equipo_id, h.fecha, h.tipo, h.detalle, h.condicion, 
                   h.estado_equipo, h.deficiencia, h.trabajo, h.observaciones, 
                   h.fecha_entrega, h.hora_entrega, h.realizado_por, h.servicio_ht,
                   h.repuesto_usado, h.repuesto_nombre, h.repuesto_cantidad,
                   e.nombre as equipo_nombre, e.area as equipo_area, e.marca as equipo_marca, 
                   e.modelo as equipo_modelo, e.centro_salud_nombre, e.red_salud_nombre
            FROM historial_intervenciones h
            LEFT JOIN equipos e ON h.equipo_id = e.id
            {where_sql}
            ORDER BY COALESCE(h.fecha_entrega, h.fecha) DESC, h.id DESC
            LIMIT %s;
        """
        params.append(limite)
        cur.execute(query, tuple(params))
        filas = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()

        for f in filas:
            for k in ["fecha", "fecha_entrega"]:
                if f.get(k) and hasattr(f[k], "strftime"):
                    f[k] = f[k].strftime("%Y-%m-%d")
        return filas
    except Exception as e:
        print(f"[ERROR] Error en obtener_intervenciones_db: {e}")
        try: conn.close()
        except: pass
        return []

def guardar_intervencion_db(datos):
    """Guarda un registro de intervención / mantenimiento técnico en la BD."""
    eq_id = str(datos.get("equipo_id") or "").strip()
    if not eq_id:
        return False, "Código de equipo médico es obligatorio."

    conn = obtener_conexion()
    if not conn:
        return False, "Error conectando a la base de datos."

    try:
        cur = conn.cursor()
        fec = datos.get("fecha") or date.today().strftime("%Y-%m-%d")
        tip = str(datos.get("tipo") or "Mantenimiento Preventivo").strip()
        det = str(datos.get("detalle") or "").strip()
        con = str(datos.get("condicion") or "Operativo").strip()
        est = str(datos.get("estado_equipo") or "Bueno").strip()
        tra = str(datos.get("trabajo") or det).strip()
        obs = str(datos.get("observaciones") or "").strip()
        rea = str(datos.get("realizado_por") or "Técnico").strip()
        hor = str(datos.get("hora_entrega") or datetime.now().strftime("%H:%M")).strip()
        f_ent = datos.get("fecha_entrega") or fec
        rep_u = bool(datos.get("repuesto_usado", False))
        rep_n = str(datos.get("repuesto_nombre") or "").strip()
        rep_c = int(datos.get("repuesto_cantidad") or 0)

        i_id = datos.get("id")
        if i_id:
            cur.execute("""
                UPDATE historial_intervenciones 
                SET equipo_id = %s, fecha = %s, tipo = %s, detalle = %s, condicion = %s, 
                    estado_equipo = %s, trabajo = %s, observaciones = %s, realizado_por = %s, 
                    hora_entrega = %s, fecha_entrega = %s, repuesto_usado = %s, 
                    repuesto_nombre = %s, repuesto_cantidad = %s
                WHERE id = %s;
            """, (eq_id, fec, tip, det, con, est, tra, obs, rea, hor, f_ent, rep_u, rep_n, rep_c, i_id))
            new_id = i_id
        else:
            cur.execute("""
                INSERT INTO historial_intervenciones (
                    equipo_id, fecha, tipo, detalle, condicion, estado_equipo, trabajo,
                    observaciones, realizado_por, hora_entrega, fecha_entrega,
                    repuesto_usado, repuesto_nombre, repuesto_cantidad
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (eq_id, fec, tip, det, con, est, tra, obs, rea, hor, f_ent, rep_u, rep_n, rep_c))
            new_id = cur.fetchone()[0]

        # Actualizar estado del equipo si se especificó
        if est:
            cur.execute("UPDATE equipos SET estado = %s WHERE id = %s", (est, eq_id))

        conn.commit()
        cur.close()
        conn.close()
        return True, new_id
    except Exception as e:
        print(f"[ERROR] Error al guardar intervención: {e}")
        try: conn.rollback(); conn.close()
        except: pass
        return False, str(e)

def eliminar_registro_db(tabla, id_registro, usuario="web_user"):
    """
    Elimina de forma segura un registro de cualquier módulo autorizado,
    guardando un snapshot completo de respaldo en la tabla papelera.
    """
    tablas_validas = {
        "equipos": "id",
        "catalogo": "id",
        "muebleria": "id",
        "areas": "id",
        "repuestos": "id",
        "historial_intervenciones": "id",
        "usuarios": "nombre_usuario"
    }
    t_clean = str(tabla).strip().lower()
    if t_clean not in tablas_validas:
        return False, f"La tabla '{tabla}' no está autorizada para eliminación segura."

    campo_id = tablas_validas[t_clean]

    conn = obtener_conexion()
    if not conn:
        return False, "Error de conexión con la base de datos central."

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"SELECT * FROM {t_clean} WHERE {campo_id} = %s;", (id_registro,))
        fila = cur.fetchone()
        if not fila:
            cur.close()
            conn.close()
            return False, f"El registro con ID '{id_registro}' no existe en {t_clean}."

        fila_dict = dict(fila)
        mover_a_papelera(cur, t_clean, id_registro, fila_dict, usuario=usuario)
        cur.execute(f"DELETE FROM {t_clean} WHERE {campo_id} = %s;", (id_registro,))
        conn.commit()
        cur.close()
        conn.close()
        return True, f"Registro eliminado y respaldado en papelera de seguridad."
    except Exception as e:
        print(f"[ERROR] Error al eliminar en {t_clean}: {e}")
        if conn:
            try: conn.rollback(); conn.close()
            except: pass
        return False, str(e)

def obtener_estadisticas_censo_db(centro_nombre=None, perfil=None, red_nombre=None):
    """Calcula indicadores y métricas en vivo para la pestaña de Análisis."""
    conn = obtener_conexion(perfil=perfil)
    if not conn:
        return {
            "total_equipos": 0, "operativos": 0, "mantenimiento": 0, "baja": 0,
            "criticidad_alta": 0, "criticidad_media": 0, "criticidad_baja": 0,
            "total_muebles": 0, "total_repuestos": 0, "total_intervenciones": 0,
            "areas_distribucion": []
        }
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        conds_eq = ["COALESCE(estado, 'Operativo') NOT IN ('Inactivo', 'Eliminado')"]
        params_eq = []
        if centro_nombre and not str(centro_nombre).startswith("["):
            conds_eq.append("(centro_salud_nombre = %s OR centro_salud_nombre ILIKE %s)")
            params_eq.extend([centro_nombre, f"%{centro_nombre}%"])
        if red_nombre and not str(red_nombre).startswith("["):
            conds_eq.append("(red_salud_nombre = %s OR red_salud_nombre ILIKE %s)")
            params_eq.extend([red_nombre, f"%{red_nombre}%"])

        filtro_eq = "WHERE " + " AND ".join(conds_eq)

        # Equipos por estado y criticidad
        sql_eq = f"""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado ILIKE 'Bueno' OR estado ILIKE 'Operativo') as operativos,
                COUNT(*) FILTER (WHERE estado ILIKE 'Regular' OR estado ILIKE '%%Mantenimiento%%') as mantenimiento,
                COUNT(*) FILTER (WHERE estado ILIKE 'Malo' OR estado ILIKE '%%Baja%%' OR estado ILIKE '%%Inoperativo%%') as baja,
                COUNT(*) FILTER (WHERE criticidad ILIKE 'Alta') as crit_alta,
                COUNT(*) FILTER (WHERE criticidad ILIKE 'Media') as crit_media,
                COUNT(*) FILTER (WHERE criticidad ILIKE 'Baja') as crit_baja
            FROM equipos {filtro_eq};
        """
        cur.execute(sql_eq, tuple(params_eq))
        row_eq = cur.fetchone() or {}

        # Muebles
        conds_mu = ["COALESCE(estado, 'Activo') NOT IN ('Inactivo', 'Eliminado')"]
        params_mu = []
        if centro_nombre and not str(centro_nombre).startswith("["):
            conds_mu.append("(ubicacion ILIKE %s OR descripcion ILIKE %s OR unidad_organizacional ILIKE %s)")
            params_mu.extend([f"%{centro_nombre}%", f"%{centro_nombre}%", f"%{centro_nombre}%"])
        if red_nombre and not str(red_nombre).startswith("["):
            conds_mu.append("(ubicacion ILIKE %s OR descripcion ILIKE %s OR unidad_organizacional ILIKE %s)")
            params_mu.extend([f"%{red_nombre}%", f"%{red_nombre}%", f"%{red_nombre}%"])
        filtro_mu = "WHERE " + " AND ".join(conds_mu)
        sql_mu = f"SELECT COUNT(*) FROM muebleria {filtro_mu};"
        cur.execute(sql_mu, tuple(params_mu))
        tot_muebles = cur.fetchone()[0] or 0

        # Repuestos
        conds_rep = []
        params_rep = []
        if centro_nombre and not str(centro_nombre).startswith("["):
            conds_rep.append("(centro_salud_nombre = %s OR centro_salud_nombre ILIKE %s)")
            params_rep.extend([centro_nombre, f"%{centro_nombre}%"])
        if red_nombre and not str(red_nombre).startswith("["):
            conds_rep.append("(centro_salud_nombre ILIKE %s)")
            params_rep.append(f"%{red_nombre}%")
        filtro_rep = ("WHERE " + " AND ".join(conds_rep)) if conds_rep else ""
        sql_rep = f"SELECT COUNT(*) FROM repuestos {filtro_rep};"
        if params_rep:
            cur.execute(sql_rep, tuple(params_rep))
        else:
            cur.execute(sql_rep)
        tot_repuestos = cur.fetchone()[0] or 0

        # Intervenciones
        sql_inter = f"""
            SELECT COUNT(*) FROM historial_intervenciones h
            LEFT JOIN equipos e ON h.equipo_id = e.id
            {filtro_eq.replace('centro_salud_nombre', 'e.centro_salud_nombre')};
        """
        if params_eq:
            cur.execute(sql_inter, tuple(params_eq))
        else:
            cur.execute(sql_inter)
        tot_intervenciones = cur.fetchone()[0] or 0

        # Distribución de equipos por área
        sql_dist = f"""
            SELECT COALESCE(area, 'Sin Área') as area_nombre, COUNT(*) as cantidad
            FROM equipos {filtro_eq}
            GROUP BY COALESCE(area, 'Sin Área')
            ORDER BY cantidad DESC LIMIT 8;
        """
        if params_eq:
            cur.execute(sql_dist, tuple(params_eq))
        else:
            cur.execute(sql_dist)
        dist_areas = [dict(r) for r in cur.fetchall()]

        cur.close()
        conn.close()

        return {
            "total_equipos": row_eq.get("total", 0) or 0,
            "operativos": row_eq.get("operativos", 0) or 0,
            "mantenimiento": row_eq.get("mantenimiento", 0) or 0,
            "baja": row_eq.get("baja", 0) or 0,
            "criticidad_alta": row_eq.get("crit_alta", 0) or 0,
            "criticidad_media": row_eq.get("crit_media", 0) or 0,
            "criticidad_baja": row_eq.get("crit_baja", 0) or 0,
            "total_muebles": tot_muebles,
            "total_repuestos": tot_repuestos,
            "total_intervenciones": tot_intervenciones,
            "areas_distribucion": dist_areas
        }
    except Exception as e:
        print(f"[ERROR] Error en obtener_estadisticas_censo_db: {e}")
        try: conn.close()
        except: pass
        return {
            "total_equipos": 0, "operativos": 0, "mantenimiento": 0, "baja": 0,
            "criticidad_alta": 0, "criticidad_media": 0, "criticidad_baja": 0,
            "total_muebles": 0, "total_repuestos": 0, "total_intervenciones": 0,
            "areas_distribucion": []
        }

def guardar_equipo_db(eq_data):
    """
    Inserta o actualiza un equipo médico en la base de datos PostgreSQL.
    Si el equipo es nuevo y el código AF colisiona con uno existente, calcula automáticamente
    el siguiente correlativo libre (evitando sobrescribir registros creados por otros técnicos).
    Si no hay conexión a la base de datos, guarda el registro en la cola offline local.
    Retorna: (exito: bool, id_guardado: str, mensaje: str)
    """
    from datetime import date
    eq = dict(eq_data)
    r_nom = str(eq.get("red_salud_nombre") or "").strip()
    c_nom = str(eq.get("centro_salud_nombre") or "").strip()
    eq_id = str(eq.get("id") or "").strip()

    # Si la imagen viene en base64 y es grande, comprimirla
    foto = eq.get("foto") or ""
    if foto and len(foto) > 50000:
        foto = comprimir_imagen_base64(foto)
        eq["foto"] = foto

    conn = obtener_conexion()
    if not conn:
        # Modo Offline
        if not eq_id and r_nom and c_nom:
            eq_id = generar_siguiente_codigo_af(r_nom, c_nom)
            eq["id"] = eq_id
        guardar_equipo_offline_cola(eq)
        return True, eq_id, "Guardado en cola offline del dispositivo (sin conexión a servidor central)"

    try:
        cur = conn.cursor()
        red_id = eq.get("red_salud_id")
        cen_id = eq.get("centro_salud_id")

        if not red_id and r_nom:
            cur.execute("SELECT id FROM redes_salud WHERE nombre = %s OR codigo = %s OR nombre ILIKE %s LIMIT 1;", 
                        (r_nom, eq.get("red_salud_nombre", ""), f"%{r_nom}%"))
            r_row = cur.fetchone()
            if r_row: red_id = r_row[0]

        if not cen_id and c_nom:
            cur.execute("SELECT id FROM centros_salud WHERE nombre = %s OR nombre ILIKE %s LIMIT 1;", 
                        (c_nom, f"%{c_nom}%"))
            c_row = cur.fetchone()
            if c_row: cen_id = c_row[0]

        # Anticolisión: si es un nuevo registro y el ID ya existe en BD, autoincrementar correlativo
        es_edicion = bool(eq.get("_es_edicion", False))
        if not es_edicion:
            if eq_id:
                cur.execute("SELECT 1 FROM equipos WHERE id = %s;", (eq_id,))
                if cur.fetchone():
                    eq_id = generar_siguiente_codigo_af(r_nom, c_nom)
                    eq["id"] = eq_id
            elif r_nom and c_nom:
                eq_id = generar_siguiente_codigo_af(r_nom, c_nom)
                eq["id"] = eq_id
        hoy_str = date.today().strftime('%Y-%m-%d')
        cat_det = eq.get("categorizacion_detalle")
        if not cat_det:
            cat_det_val = psycopg2.extras.Json({})
        elif isinstance(cat_det, (dict, list)):
            cat_det_val = psycopg2.extras.Json(cat_det)
        elif isinstance(cat_det, str) and cat_det.strip():
            try:
                cat_det_val = psycopg2.extras.Json(json.loads(cat_det))
            except Exception:
                cat_det_val = psycopg2.extras.Json({})
        else:
            cat_det_val = psycopg2.extras.Json({})

        f_venc_gar = str(eq.get("fecha_vencimiento_garantia") or "").strip() or None
        f_ini_gar = str(eq.get("fecha_inicio_garantia") or "").strip() or None

        campos = {
            "id": eq_id,
            "nombre": str(eq.get("nombre") or "").strip(),
            "marca": str(eq.get("marca") or "").strip(),
            "modelo": str(eq.get("modelo") or "").strip(),
            "servicio": str(eq.get("servicio") or "").strip(),
            "area": str(eq.get("area") or "").strip(),
            "procedencia": str(eq.get("procedencia") or "").strip(),
            "fabricante": str(eq.get("fabricante") or "").strip(),
            "proveedor": str(eq.get("proveedor") or "").strip(),
            "anio_fab": str(eq.get("anio_fab") or "").strip(),
            "t_elec": bool(eq.get("t_elec")),
            "t_elco": bool(eq.get("t_elco")),
            "t_mec": bool(eq.get("t_mec")),
            "t_hid": bool(eq.get("t_hid")),
            "t_neu": bool(eq.get("t_neu")),
            "t_vap": bool(eq.get("t_vap")),
            "a_comp": bool(eq.get("a_comp")),
            "a_como": bool(eq.get("a_como")),
            "a_don": bool(eq.get("a_don")),
            "te_fijo": bool(eq.get("te_fijo")),
            "te_mov": bool(eq.get("te_mov")),
            "te_por": bool(eq.get("te_por")),
            "garantia": str(eq.get("garantia") or "No").strip(),
            "criticidad": str(eq.get("criticidad") or "Media").strip(),
            "categorizacion_detalle": cat_det_val,
            "estado": str(eq.get("estado") or "Bueno").strip(),
            "fecha_adquisicion": str(eq.get("fecha_adquisicion") or hoy_str).strip(),
            "fecha_registro": str(eq.get("fecha_registro") or hoy_str).strip(),
            "foto": foto,
            "fecha_vencimiento_garantia": f_venc_gar,
            "numero_serie": str(eq.get("numero_serie") or "S/C").strip(),
            "fecha_inicio_garantia": f_ini_gar,
            "costo": str(eq.get("costo") or "0").strip(),
            "voltaje": str(eq.get("voltaje") or "").strip(),
            "corriente": str(eq.get("corriente") or "").strip(),
            "potencia": str(eq.get("potencia") or "").strip(),
            "vida_util": str(eq.get("vida_util") or "").strip(),
            "temperatura": str(eq.get("temperatura") or "").strip(),
            "peso": str(eq.get("peso") or "").strip(),
            "dimensiones": str(eq.get("dimensiones") or "").strip(),
            "bateria_respaldo": str(eq.get("bateria_respaldo") or "").strip(),
            "resolucion": str(eq.get("resolucion") or "").strip(),
            "version_software": str(eq.get("version_software") or "").strip(),
            "humedad": str(eq.get("humedad") or "").strip(),
            "suministro_gases": str(eq.get("suministro_gases") or "").strip(),
            "contexto_operacional": str(eq.get("contexto_operacional") or "").strip(),
            "funciones_equipo": str(eq.get("funciones_equipo") or "").strip(),
            "acciones_preventivas": str(eq.get("acciones_preventivas") or "").strip(),
            "acciones_falla": str(eq.get("acciones_falla") or "").strip(),
            "fallas_funcionales": str(eq.get("fallas_funcionales") or "").strip(),
            "causas_fallo": str(eq.get("causas_fallo") or "").strip(),
            "efectos_fallo": str(eq.get("efectos_fallo") or "").strip(),
            "efecto_entorno": str(eq.get("efecto_entorno") or "").strip(),
            "observaciones": str(eq.get("observaciones") or "").strip(),
            "red_salud_id": red_id,
            "red_salud_nombre": r_nom,
            "centro_salud_id": cen_id,
            "centro_salud_nombre": c_nom,
            "municipio_nombre": str(eq.get("municipio_nombre") or "La Paz").strip(),
            "departamento_nombre": str(eq.get("departamento_nombre") or "La Paz").strip(),
            "sector_actual": str(eq.get("sector_actual") or "SALUD").strip(),
            "persona_asignada": str(eq.get("persona_asignada") or "").strip(),
            "cargo_asignado": str(eq.get("cargo_asignado") or "").strip(),
            "ci_asignado": str(eq.get("ci_asignado") or "").strip(),
            "codigo_sispam": str(eq.get("codigo_sispam") or "S/C").strip(),
            "bertin": str(eq.get("bertin") or "S/C").strip(),
            "sapm": str(eq.get("sapm") or "S/C").strip(),
        }

        sql_ins = """
            INSERT INTO equipos (
                id, nombre, marca, modelo, servicio, area, procedencia, fabricante, proveedor, anio_fab,
                t_elec, t_elco, t_mec, t_hid, t_neu, t_vap, a_comp, a_como, a_don, te_fijo, te_mov, te_por, garantia, criticidad, categorizacion_detalle, estado, fecha_adquisicion, fecha_registro, foto, fecha_vencimiento_garantia, numero_serie, fecha_inicio_garantia, costo,
                voltaje, corriente, potencia, vida_util, temperatura, peso, dimensiones, bateria_respaldo, resolucion, version_software, humedad, suministro_gases, contexto_operacional, funciones_equipo, acciones_preventivas, acciones_falla, fallas_funcionales, causas_fallo, efectos_fallo, efecto_entorno, observaciones,
                red_salud_id, red_salud_nombre, centro_salud_id, centro_salud_nombre, municipio_nombre, departamento_nombre,
                sector_actual, persona_asignada, cargo_asignado, ci_asignado, codigo_sispam, bertin, sapm
            )
            VALUES (
                %(id)s, %(nombre)s, %(marca)s, %(modelo)s, %(servicio)s, %(area)s, %(procedencia)s, %(fabricante)s, %(proveedor)s, %(anio_fab)s,
                %(t_elec)s, %(t_elco)s, %(t_mec)s, %(t_hid)s, %(t_neu)s, %(t_vap)s, %(a_comp)s, %(a_como)s, %(a_don)s, %(te_fijo)s, %(te_mov)s, %(te_por)s, %(garantia)s, %(criticidad)s, %(categorizacion_detalle)s, %(estado)s, %(fecha_adquisicion)s, %(fecha_registro)s, %(foto)s, %(fecha_vencimiento_garantia)s, %(numero_serie)s, %(fecha_inicio_garantia)s, %(costo)s,
                %(voltaje)s, %(corriente)s, %(potencia)s, %(vida_util)s, %(temperatura)s, %(peso)s, %(dimensiones)s, %(bateria_respaldo)s, %(resolucion)s, %(version_software)s, %(humedad)s, %(suministro_gases)s, %(contexto_operacional)s, %(funciones_equipo)s, %(acciones_preventivas)s, %(acciones_falla)s, %(fallas_funcionales)s, %(causas_fallo)s, %(efectos_fallo)s, %(efecto_entorno)s, %(observaciones)s,
                %(red_salud_id)s, %(red_salud_nombre)s, %(centro_salud_id)s, %(centro_salud_nombre)s, %(municipio_nombre)s, %(departamento_nombre)s,
                %(sector_actual)s, %(persona_asignada)s, %(cargo_asignado)s, %(ci_asignado)s, %(codigo_sispam)s, %(bertin)s, %(sapm)s
            )
            ON CONFLICT (id) DO UPDATE SET
                nombre=EXCLUDED.nombre, marca=EXCLUDED.marca, modelo=EXCLUDED.modelo, servicio=EXCLUDED.servicio, area=EXCLUDED.area, procedencia=EXCLUDED.procedencia, fabricante=EXCLUDED.fabricante, proveedor=EXCLUDED.proveedor, anio_fab=EXCLUDED.anio_fab,
                t_elec=EXCLUDED.t_elec, t_elco=EXCLUDED.t_elco, t_mec=EXCLUDED.t_mec, t_hid=EXCLUDED.t_hid, t_neu=EXCLUDED.t_neu, t_vap=EXCLUDED.t_vap, a_comp=EXCLUDED.a_comp, a_como=EXCLUDED.a_como, a_don=EXCLUDED.a_don,
                te_fijo=EXCLUDED.te_fijo, te_mov=EXCLUDED.te_mov, te_por=EXCLUDED.te_por, garantia=EXCLUDED.garantia, criticidad=EXCLUDED.criticidad, categorizacion_detalle=EXCLUDED.categorizacion_detalle, estado=EXCLUDED.estado, fecha_adquisicion=EXCLUDED.fecha_adquisicion, foto=EXCLUDED.foto, fecha_vencimiento_garantia=EXCLUDED.fecha_vencimiento_garantia, numero_serie=EXCLUDED.numero_serie, fecha_inicio_garantia=EXCLUDED.fecha_inicio_garantia, costo=EXCLUDED.costo,
                voltaje=EXCLUDED.voltaje, corriente=EXCLUDED.corriente, potencia=EXCLUDED.potencia, vida_util=EXCLUDED.vida_util, temperatura=EXCLUDED.temperatura, peso=EXCLUDED.peso, dimensiones=EXCLUDED.dimensiones, bateria_respaldo=EXCLUDED.bateria_respaldo, resolucion=EXCLUDED.resolucion, version_software=EXCLUDED.version_software, humedad=EXCLUDED.humedad, suministro_gases=EXCLUDED.suministro_gases, contexto_operacional=EXCLUDED.contexto_operacional, funciones_equipo=EXCLUDED.funciones_equipo, acciones_preventivas=EXCLUDED.acciones_preventivas, acciones_falla=EXCLUDED.acciones_falla, fallas_funcionales=EXCLUDED.fallas_funcionales, causas_fallo=EXCLUDED.causas_fallo, efectos_fallo=EXCLUDED.efectos_fallo, efecto_entorno=EXCLUDED.efecto_entorno, observaciones=EXCLUDED.observaciones,
                red_salud_id=EXCLUDED.red_salud_id, red_salud_nombre=EXCLUDED.red_salud_nombre, centro_salud_id=EXCLUDED.centro_salud_id, centro_salud_nombre=EXCLUDED.centro_salud_nombre, municipio_nombre=EXCLUDED.municipio_nombre, departamento_nombre=EXCLUDED.departamento_nombre,
                sector_actual=EXCLUDED.sector_actual, persona_asignada=EXCLUDED.persona_asignada, cargo_asignado=EXCLUDED.cargo_asignado, ci_asignado=EXCLUDED.ci_asignado, codigo_sispam=EXCLUDED.codigo_sispam, bertin=EXCLUDED.bertin, sapm=EXCLUDED.sapm;
        """
        cur.execute(sql_ins, campos)
        conn.commit()
        cur.close()
        conn.close()
        return True, eq_id, "Equipo guardado y sincronizado exitosamente con la base de datos central"
    except Exception as err:
        print(f"[WARN] Error al guardar equipo en PostgreSQL: {err}. Guardando en cola offline...")
        if conn:
            try:
                conn.rollback()
                conn.close()
            except: pass
        guardar_equipo_offline_cola(eq)
        return True, eq_id, f"Guardado en cola offline: {err}"

# =========================================================================
# COLAS DE SINCRONIZACIÓN OFFLINE (EQUIPOS, MUEBLERÍA, ÁREAS)
# =========================================================================

def guardar_equipo_offline_cola(equipo_dict):
    """Almacena un equipo registrado o editado offline en la cola de sincronización."""
    import os, json
    ruta = _obtener_ruta_cola_equipos()
    try:
        cola = []
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                cola = json.load(f)
        idx_existente = next((i for i, item in enumerate(cola) if str(item.get("id")) == str(equipo_dict.get("id"))), None)
        if idx_existente is not None:
            cola[idx_existente] = equipo_dict
        else:
            cola.append(equipo_dict)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(cola, f, cls=DateTimeEncoder, indent=2)
        print(f"[OFFLINE] Equipo {equipo_dict.get('id')} guardado en cola local.")
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar equipo en cola offline: {e}")
        return False

def obtener_cola_equipos_offline():
    """Retorna la lista de equipos pendientes en la cola offline."""
    import os, json
    ruta = _obtener_ruta_cola_equipos()
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def sincronizar_equipos_offline_cola(callback_actualizar_local=None):
    """
    Sube a PostgreSQL todos los equipos registrados o editados offline.
    Si se detecta que un ID ya fue ocupado en línea, ajusta sumando +1 automáticamente
    hasta encontrar uno libre para garantizar que NUNCA ocurra error de duplicidad.
    """
    import os, json
    ruta = _obtener_ruta_cola_equipos()
    if not os.path.exists(ruta):
        return 0, "No hay equipos pendientes."
    
    conn = obtener_conexion()
    if not conn:
        return 0, "Sin conexión al servidor."

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            cola = json.load(f)
        if not cola:
            return 0, "Cola vacía."

        cur = conn.cursor()
        sincronizados = 0
        pendientes_restantes = []
        cambios_id = {}

        for eq_data in cola:
            try:
                id_actual = eq_data.get("id")
                # Verificar colisión en base de datos central
                cur.execute("SELECT id FROM equipos WHERE id = %s;", (id_actual,))
                existe_en_db = cur.fetchone()
                
                if existe_en_db and eq_data.get("_es_nuevo", True):
                    r_nom = eq_data.get("red_salud_nombre")
                    c_nom = eq_data.get("centro_salud_nombre")
                    rcod = generar_codigo_red(r_nom)
                    csig = generar_sigla_centro(c_nom)
                    prefijo = f"GAMLP-{rcod}-{csig}-"
                    
                    cur.execute("SELECT id FROM equipos WHERE id LIKE %s;", (f"{prefijo}%",))
                    nums_bd = []
                    for row in cur.fetchall():
                        suf = str(row[0])[len(prefijo):]
                        if suf.isdigit():
                            nums_bd.append(int(suf))
                    siguiente_num = max(nums_bd, default=0) + 1
                    nuevo_id = f"{prefijo}{siguiente_num:06d}"
                    while True:
                        cur.execute("SELECT id FROM equipos WHERE id = %s;", (nuevo_id,))
                        if not cur.fetchone():
                            break
                        siguiente_num += 1
                        nuevo_id = f"{prefijo}{siguiente_num:06d}"

                    print(f"[RESOLUCION COLISION] Equipo {id_actual} reasignado a {nuevo_id} para evitar duplicidad.")
                    cambios_id[id_actual] = nuevo_id
                    eq_data["id"] = nuevo_id

                red_id = None
                cen_id = None
                if eq_data.get("red_salud_nombre"):
                    cur.execute("SELECT id FROM redes_salud WHERE nombre = %s OR codigo = %s OR nombre ILIKE %s LIMIT 1;", 
                                (eq_data["red_salud_nombre"], eq_data.get("red_salud_nombre", ""), f"%{eq_data['red_salud_nombre']}%"))
                    r_row = cur.fetchone()
                    if r_row: red_id = r_row[0]
                    
                if eq_data.get("centro_salud_nombre"):
                    cur.execute("SELECT id FROM centros_salud WHERE nombre = %s OR nombre ILIKE %s LIMIT 1;", 
                                (eq_data["centro_salud_nombre"], f"%{eq_data['centro_salud_nombre']}%"))
                    c_row = cur.fetchone()
                    if c_row: cen_id = c_row[0]

                sql_ins = """
                    INSERT INTO equipos (
                        id, nombre, marca, modelo, servicio, area, procedencia, fabricante, proveedor, anio_fab,
                        t_elec, t_elco, t_mec, t_hid, t_neu, t_vap, a_comp, a_como, a_don, te_fijo, te_mov, te_por, garantia, criticidad, categorizacion_detalle, estado, fecha_adquisicion, fecha_registro, foto, fecha_vencimiento_garantia, numero_serie, fecha_inicio_garantia, costo,
                        voltaje, corriente, potencia, vida_util, temperatura, peso, dimensiones, bateria_respaldo, resolucion, version_software, humedad, suministro_gases, contexto_operacional, funciones_equipo, acciones_preventivas, acciones_falla, fallas_funcionales, causas_fallo, efectos_fallo, efecto_entorno, observaciones,
                        red_salud_id, red_salud_nombre, centro_salud_id, centro_salud_nombre, municipio_nombre, departamento_nombre,
                        sector_actual, persona_asignada, cargo_asignado, ci_asignado, codigo_sispam, bertin, sapm
                    )
                    VALUES (
                        %(id)s, %(nombre)s, %(marca)s, %(modelo)s, %(servicio)s, %(area)s, %(procedencia)s, %(fabricante)s, %(proveedor)s, %(anio_fab)s,
                        %(t_elec)s, %(t_elco)s, %(t_mec)s, %(t_hid)s, %(t_neu)s, %(t_vap)s, %(a_comp)s, %(a_como)s, %(a_don)s, %(te_fijo)s, %(te_mov)s, %(te_por)s, %(garantia)s, %(criticidad)s, %(categorizacion_detalle)s, %(estado)s, %(fecha_adquisicion)s, %(fecha_registro)s, %(foto)s, %(fecha_vencimiento_garantia)s, %(numero_serie)s, %(fecha_inicio_garantia)s, %(costo)s,
                        %(voltaje)s, %(corriente)s, %(potencia)s, %(vida_util)s, %(temperatura)s, %(peso)s, %(dimensiones)s, %(bateria_respaldo)s, %(resolucion)s, %(version_software)s, %(humedad)s, %(suministro_gases)s, %(contexto_operacional)s, %(funciones_equipo)s, %(acciones_preventivas)s, %(acciones_falla)s, %(fallas_funcionales)s, %(causas_fallo)s, %(efectos_fallo)s, %(efecto_entorno)s, %(observaciones)s,
                        %(red_salud_id)s, %(red_salud_nombre)s, %(centro_salud_id)s, %(centro_salud_nombre)s, %(municipio_nombre)s, %(departamento_nombre)s,
                        %(sector_actual)s, %(persona_asignada)s, %(cargo_asignado)s, %(ci_asignado)s, %(codigo_sispam)s, %(bertin)s, %(sapm)s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        nombre=EXCLUDED.nombre, marca=EXCLUDED.marca, modelo=EXCLUDED.modelo, servicio=EXCLUDED.servicio, area=EXCLUDED.area, procedencia=EXCLUDED.procedencia, fabricante=EXCLUDED.fabricante, proveedor=EXCLUDED.proveedor, anio_fab=EXCLUDED.anio_fab,
                        t_elec=EXCLUDED.t_elec, t_elco=EXCLUDED.t_elco, t_mec=EXCLUDED.t_mec, t_hid=EXCLUDED.t_hid, t_neu=EXCLUDED.t_neu, t_vap=EXCLUDED.t_vap, a_comp=EXCLUDED.a_comp, a_como=EXCLUDED.a_como, a_don=EXCLUDED.a_don,
                        te_fijo=EXCLUDED.te_fijo, te_mov=EXCLUDED.te_mov, te_por=EXCLUDED.te_por, garantia=EXCLUDED.garantia, criticidad=EXCLUDED.criticidad, categorizacion_detalle=EXCLUDED.categorizacion_detalle, estado=EXCLUDED.estado, fecha_adquisicion=EXCLUDED.fecha_adquisicion, foto=EXCLUDED.foto, fecha_vencimiento_garantia=EXCLUDED.fecha_vencimiento_garantia, numero_serie=EXCLUDED.numero_serie, fecha_inicio_garantia=EXCLUDED.fecha_inicio_garantia, costo=EXCLUDED.costo,
                        voltaje=EXCLUDED.voltaje, corriente=EXCLUDED.corriente, potencia=EXCLUDED.potencia, vida_util=EXCLUDED.vida_util, temperatura=EXCLUDED.temperatura, peso=EXCLUDED.peso, dimensiones=EXCLUDED.dimensiones, bateria_respaldo=EXCLUDED.bateria_respaldo, resolucion=EXCLUDED.resolucion, version_software=EXCLUDED.version_software, humedad=EXCLUDED.humedad, suministro_gases=EXCLUDED.suministro_gases, contexto_operacional=EXCLUDED.contexto_operacional, funciones_equipo=EXCLUDED.funciones_equipo, acciones_preventivas=EXCLUDED.acciones_preventivas, acciones_falla=EXCLUDED.acciones_falla, fallas_funcionales=EXCLUDED.fallas_funcionales, causas_fallo=EXCLUDED.causas_fallo, efectos_fallo=EXCLUDED.efectos_fallo, efecto_entorno=EXCLUDED.efecto_entorno, observaciones=EXCLUDED.observaciones,
                        red_salud_id=EXCLUDED.red_salud_id, red_salud_nombre=EXCLUDED.red_salud_nombre, centro_salud_id=EXCLUDED.centro_salud_id, centro_salud_nombre=EXCLUDED.centro_salud_nombre, municipio_nombre=EXCLUDED.municipio_nombre, departamento_nombre=EXCLUDED.departamento_nombre,
                        sector_actual=EXCLUDED.sector_actual, persona_asignada=EXCLUDED.persona_asignada, cargo_asignado=EXCLUDED.cargo_asignado, ci_asignado=EXCLUDED.ci_asignado, codigo_sispam=EXCLUDED.codigo_sispam, bertin=EXCLUDED.bertin, sapm=EXCLUDED.sapm;
                """
                cur.execute(sql_ins, {**eq_data, "red_salud_id": red_id, "centro_salud_id": cen_id})
                sincronizados += 1
            except Exception as item_err:
                print(f"[WARN] Error al sincronizar equipo offline: {item_err}")
                pendientes_restantes.append(eq_data)

        conn.commit()
        cur.close()
        conn.close()

        if pendientes_restantes:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(pendientes_restantes, f, cls=DateTimeEncoder, indent=2)
        else:
            try: os.remove(ruta)
            except: pass

        if callback_actualizar_local and cambios_id:
            callback_actualizar_local(cambios_id)

        return sincronizados, f"Se sincronizaron {sincronizados} equipos pendientes."
    except Exception as e:
        print(f"[ERROR] Error durante sincronización offline de equipos: {e}")
        return 0, str(e)

def guardar_mueble_offline_cola(mueble_dict):
    """Guarda un registro de mueblería/computación en la cola offline."""
    import os, json
    ruta = _obtener_ruta_cola_muebles()
    try:
        cola = []
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                cola = json.load(f)
        cola.append(mueble_dict)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(cola, f, cls=DateTimeEncoder, indent=2)
        print(f"[OFFLINE] Mueblería guardada en cola local.")
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar mueblería en cola offline: {e}")
        return False

def sincronizar_muebleria_offline_cola():
    """Sincroniza activos de mueblería pendientes hacia PostgreSQL."""
    import os, json
    ruta = _obtener_ruta_cola_muebles()
    if not os.path.exists(ruta):
        return 0, "No hay pendientes."
    conn = obtener_conexion()
    if not conn:
        return 0, "Sin conexión al servidor."
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            cola = json.load(f)
        if not cola:
            return 0, "Cola vacía."
        
        sincronizados = 0
        pendientes_restantes = []
        for m_data in cola:
            try:
                exito, _ = guardar_mueble_db(m_data)
                if exito:
                    sincronizados += 1
                else:
                    pendientes_restantes.append(m_data)
            except Exception:
                pendientes_restantes.append(m_data)

        if pendientes_restantes:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(pendientes_restantes, f, cls=DateTimeEncoder, indent=2)
        else:
            try: os.remove(ruta)
            except: pass
        return sincronizados, f"Se sincronizaron {sincronizados} activos de mueblería."
    except Exception as e:
        return 0, str(e)

def guardar_area_offline_cola(area_dict):
    """Guarda un área creada o editada offline en la cola de sincronización."""
    import os, json
    ruta = _obtener_ruta_cola_areas()
    try:
        cola = []
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                cola = json.load(f)
        cola.append(area_dict)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(cola, f, cls=DateTimeEncoder, indent=2)
        print(f"[OFFLINE] Área guardada en cola local.")
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar área en cola offline: {e}")
        return False

def sincronizar_areas_offline_cola():
    """Sincroniza áreas pendientes hacia PostgreSQL."""
    import os, json
    ruta = _obtener_ruta_cola_areas()
    if not os.path.exists(ruta):
        return 0, "No hay pendientes."
    conn = obtener_conexion()
    if not conn:
        return 0, "Sin conexión al servidor."
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            cola = json.load(f)
        if not cola:
            return 0, "Cola vacía."
        cur = conn.cursor()
        sincronizados = 0
        pendientes_restantes = []
        for a_data in cola:
            try:
                if a_data.get("id"):
                    cur.execute("""
                        UPDATE areas 
                        SET centro_salud_id=%s, centro_salud_nombre=%s, red_salud_nombre=%s,
                            nombre=%s, piso=%s, contacto=%s, encargado=%s, cargo=%s, ci_encargado=%s 
                        WHERE id=%s
                    """, (
                        a_data.get("centro_salud_id"), a_data.get("centro_salud_nombre"), a_data.get("red_salud_nombre"),
                        a_data.get("nombre"), a_data.get("piso"), a_data.get("contacto"),
                        a_data.get("encargado"), a_data.get("cargo"), a_data.get("ci_encargado"), a_data["id"]
                    ))
                else:
                    cur.execute("""
                        INSERT INTO areas (centro_salud_id, centro_salud_nombre, red_salud_nombre, nombre, piso, contacto, encargado, cargo, ci_encargado)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        a_data.get("centro_salud_id"), a_data.get("centro_salud_nombre"), a_data.get("red_salud_nombre"),
                        a_data.get("nombre"), a_data.get("piso"), a_data.get("contacto"),
                        a_data.get("encargado"), a_data.get("cargo"), a_data.get("ci_encargado")
                    ))
                sincronizados += 1
            except Exception as ae:
                print(f"[WARN] Error al sincronizar área: {ae}")
                pendientes_restantes.append(a_data)
        conn.commit()
        cur.close()
        conn.close()

        if pendientes_restantes:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(pendientes_restantes, f, cls=DateTimeEncoder, indent=2)
        else:
            try: os.remove(ruta)
            except: pass
        return sincronizados, f"Se sincronizaron {sincronizados} áreas."
    except Exception as e:
        return 0, str(e)

def sincronizar_todo_offline(app=None):
    """Ejecuta la sincronización integral de todas las colas offline hacia PostgreSQL."""
    total = 0
    def _actualizar_local(cambios):
        if app and hasattr(app, "datos") and "equipos" in app.datos:
            for eq in app.datos["equipos"]:
                if eq.get("id") in cambios:
                    eq["id"] = cambios[eq["id"]]
            guardar_cache_local_datos(app.datos)
            if "Inventario" in getattr(app, "vistas", {}):
                try: app.vistas["Inventario"].refrescar_datos()
                except: pass

    try:
        s_ar, _ = sincronizar_areas_offline_cola()
        total += s_ar
    except: pass
    try:
        s_eq, _ = sincronizar_equipos_offline_cola(callback_actualizar_local=_actualizar_local)
        total += s_eq
    except: pass
    try:
        s_mu, _ = sincronizar_muebleria_offline_cola()
        total += s_mu
    except: pass
    try:
        s_ma, _ = sincronizar_mantenimientos_offline_cola()
        total += s_ma
    except: pass
    return total

def obtener_firma_datos_db():
    """
    Retorna una firma ultrarrápida (<1ms) del estado de la base de datos
    para sincronización en tiempo real entre múltiples PCs y laptops.
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return None
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM equipos)::text || ':' ||
                (SELECT COALESCE(MAX(fecha_registro), '1970-01-01') FROM equipos)::text || ':' ||
                (SELECT COUNT(*) FROM historial_intervenciones)::text || ':' ||
                (SELECT COALESCE(MAX(id), 0) FROM historial_intervenciones)::text || ':' ||
                (SELECT COUNT(*) FROM repuestos)::text || ':' ||
                (SELECT COALESCE(SUM(cantidad), 0) FROM repuestos)::text || ':' ||
                (SELECT COUNT(*) FROM catalogo)::text || ':' ||
                (SELECT COUNT(*) FROM areas)::text || ':' ||
                (SELECT COUNT(*) FROM protocolos)::text || ':' ||
                (SELECT COUNT(*) FROM muebleria)::text;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except:
        return None


# =========================================================================
# COMPRESIÓN Y SINCRONIZACIÓN UNIVERSAL DE IMÁGENES (BASE64 OPTIMIZADO)
# =========================================================================
def comprimir_imagen_base64(ruta_or_bytes, max_size=(1200, 1200), quality=90):
    """
    Comprime una imagen a formato JPEG optimizado con alta nitidez (max 1200x1200 px, 90% calidad)
    y fondo blanco para transparencias PNG.
    """
    if not ruta_or_bytes:
        return ""
    import base64
    import io
    from PIL import Image
    try:
        if isinstance(ruta_or_bytes, str):
            if ruta_or_bytes.startswith("data:image"):
                return ruta_or_bytes
            if not os.path.exists(ruta_or_bytes):
                return ""
            img = Image.open(ruta_or_bytes)
        else:
            img = Image.open(ruta_or_bytes)
            
        # Convertir a RGB respetando fondo blanco si tiene canal alfa / transparencia
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if "A" in img.getbands() else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
            
        img.thumbnail(max_size, Image.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        img_bytes = buffer.getvalue()
        
        b64_str = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"
    except Exception as e:
        print(f"[WARN] Error al comprimir imagen a Base64: {e}")
        return ""

def cargar_imagen_pil(foto_str):
    """
    Decodifica y retorna un objeto PIL.Image tanto si foto_str es data:image/base64
    como si es una ruta física de archivo local.
    """
    if not foto_str:
        return None
    import base64
    import io
    from PIL import Image
    try:
        if isinstance(foto_str, str) and foto_str.startswith("data:image"):
            header, b64_data = foto_str.split(",", 1)
            raw_bytes = base64.b64decode(b64_data)
            return Image.open(io.BytesIO(raw_bytes))
        elif isinstance(foto_str, str) and os.path.exists(foto_str):
            return Image.open(foto_str)
    except Exception as e:
        print(f"[WARN] No se pudo cargar imagen PIL: {e}")
    return None


