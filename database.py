# database.py
import os
import json
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from config import CONFIG

def obtener_conexion():
    """Establece y retorna la conexión a PostgreSQL usando los datos de config.py."""
    try:
        kwargs = {
            "dbname": CONFIG["db_name"],
            "user": CONFIG["db_user"],
            "password": CONFIG["db_password"],
            "host": CONFIG["db_host"],
            "port": CONFIG["db_port"],
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
        if CONFIG.get("db_sslmode") or ("supabase" in str(CONFIG.get("db_host", "")).lower()):
            kwargs["sslmode"] = CONFIG.get("db_sslmode", "require")
            
        conn = psycopg2.connect(**kwargs)
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        print(f"[ERROR] Error de conexión a la BD: {e}")
        return None

def inicializar_bd():
    """Sistema de control de versiones de base de datos."""
    conn = obtener_conexion()
    if not conn:
        return False
    cur = conn.cursor()
    
    # 1. Tabla: esquema de versiones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        );
    """)
    cur.execute("INSERT INTO schema_version (version) SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM schema_version);")

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
            nombre VARCHAR(255) NOT NULL,
            piso VARCHAR(100),
            contacto VARCHAR(100),
            encargado VARCHAR(255)
        );
    """)
    cur.execute("ALTER TABLE areas DROP CONSTRAINT IF EXISTS areas_nombre_key;")
    
    # Limpiar duplicados antes de aplicar la restricción UNIQUE
    try:
        cur.execute("""
            DELETE FROM areas a USING areas b
            WHERE a.id > b.id 
              AND a.nombre = b.nombre 
              AND COALESCE(a.piso, '') = COALESCE(b.piso, '');
        """)
        conn.commit()
    except Exception as e_dedup:
        conn.rollback()

    try:
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'unique_nombre_piso') THEN
                    ALTER TABLE areas ADD CONSTRAINT unique_nombre_piso UNIQUE (nombre, piso);
                END IF;
            END $$;
        """)
        conn.commit()
    except Exception as e_cst:
        conn.rollback()

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
            foto VARCHAR(255),
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

    cur.execute("SELECT COUNT(*) FROM areas;")
    if cur.fetchone()[0] == 0:
        areas_iniciales = [
            ("Bloque Quirurgico", "", ""),
            ("Braquioterapia", "", ""),
            ("Consulta Externa", "", ""),
            ("Emergencias", "", ""),
            ("Endoscopia", "", ""),
            ("Especialidades Clinicas", "", ""),
            ("Especialidades Quirurgicas", "", ""),
            ("Esterilizacion", "", ""),
            ("Gineco-Obstetricia", "", ""),
            ("Hemodialisis", "", ""),
            ("Imagenologia", "", ""),
            ("Laboratorio", "", ""),
            ("Muelle de almacen", "", ""),
            ("Neonatologia", "", ""),
            ("Oncologia", "", ""),
            ("Parqueo", "", ""),
            ("Partos", "", ""),
            ("Patologia", "", ""),
            ("Pediatria", "", ""),
            ("Tranfusional", "", ""),
            ("UCI-A", "", "")
        ]
        for name, phone, manager in areas_iniciales:
            cur.execute("""
                INSERT INTO areas (nombre, contacto, encargado)
                VALUES (%s, %s, %s)
                ON CONFLICT (nombre) DO NOTHING;
            """, (name, phone, manager))
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
    tablas_serial = ["departamentos", "municipios", "redes_salud", "centros_salud", "areas", "catalogo", "repuestos", "historial_intervenciones", "protocolos", "usuarios", "papelera"]
    for ts in tablas_serial:
        try:
            cur.execute(f"SELECT setval(pg_get_serial_sequence('{ts}', 'id'), COALESCE((SELECT MAX(id) FROM \"{ts}\"), 1));")
        except Exception as e_seq:
            pass
    conn.commit()

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
            "LLOJETA EL VERGEL", "PASANKERY", "ALTO TACAGUA"
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


def obtener_jerarquia_sedes_db():
    """Obtiene la jerarquía completa de Departamentos, Municipios, Redes y Centros de Salud."""
    conn = obtener_conexion()
    if not conn:
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
            "centros": [
                {"id": 1, "red_salud_id": 5, "nombre": "C.M.I. CHASQUIPAMPA", "nivel": "Primer Nivel"},
                {"id": 2, "red_salud_id": 5, "nombre": "BOLOGNIA", "nivel": "Primer Nivel"},
                {"id": 3, "red_salud_id": 5, "nombre": "ACHUMANI", "nivel": "Primer Nivel"},
                {"id": 4, "red_salud_id": 1, "nombre": "TEMBLADERANI", "nivel": "Primer Nivel"},
                {"id": 5, "red_salud_id": 2, "nombre": "LA PORTADA", "nivel": "Primer Nivel"},
                {"id": 6, "red_salud_id": 3, "nombre": "ACHACHICALA", "nivel": "Primer Nivel"},
                {"id": 7, "red_salud_id": 4, "nombre": "KUPINI", "nivel": "Primer Nivel"},
            ]
        }
    try:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT id, nombre, codigo FROM departamentos WHERE estado = 'Activo' ORDER BY CASE WHEN nombre='La Paz' THEN 0 ELSE 1 END, nombre ASC;")
        deptos = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT id, departamento_id, nombre, codigo FROM municipios WHERE estado = 'Activo' AND (nombre = 'GAMLP' OR nombre = 'La Paz (GAMLP)') ORDER BY id ASC;")
        muns = [dict(r) for r in cur.fetchall()]
        if not muns:
            muns = [{"id": 1, "departamento_id": 1, "nombre": "GAMLP", "codigo": "GAMLP"}]
        
        cur.execute("SELECT id, municipio_id, departamento_id, nombre, codigo, macrodistrito FROM redes_salud WHERE estado = 'Activo' ORDER BY codigo ASC;")
        redes = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT id, red_salud_id, nombre, nivel, direccion FROM centros_salud WHERE estado = 'Activo' ORDER BY nombre ASC;")
        centros = [dict(r) for r in cur.fetchall()]
        
        cur.close()
        conn.close()
        return {
            "departamentos": deptos,
            "municipios": muns,
            "redes": redes,
            "centros": centros
        }
    except Exception as e:
        print("[WARN] Error obteniendo jerarquía de sedes:", e)
        if conn:
            conn.close()
        return {
            "departamentos": [{"id": 1, "nombre": "La Paz"}],
            "municipios": [{"id": 1, "nombre": "GAMLP"}],
            "redes": [],
            "centros": []
        }

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
        tablas = ["areas", "catalogo", "equipos", "historial_intervenciones", "protocolos", "repuestos", "usuarios", "papelera"]
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
        tablas_con_serial = ["usuarios", "areas", "catalogo", "repuestos", "historial_intervenciones", "protocolos", "papelera"]
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
    return os.path.join(os.path.expanduser("~"), ".gamlp_data_cache.json")

def _obtener_ruta_cola_offline():
    return os.path.join(os.path.expanduser("~"), ".gamlp_offline_queue.json")

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
        return 0, str(e)


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
                (SELECT COUNT(*) FROM protocolos)::text;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except:
        return None


