# migracion_gamlp_supabase.py
"""
Script de inicialización y migración a Supabase Cloud para CMMS GAMLP.
Crea la jerarquía territorial completa:
  - 9 Departamentos de Bolivia
  - Municipio de La Paz
  - 5 Redes de Salud (Macrodistritos)
  - 67 Centros de Salud Oficiales
  - Tablas del sistema (equipos, áreas, historial, usuarios, etc.)
  - Migración de datos locales desde el respaldo más reciente.
"""

import os
import sys
import json
import psycopg2
from psycopg2 import sql

# Compatibilidad de codificación para consolas Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Lista oficial de Redes y Centros de Salud GAMLP
JERARQUIA_DATOS = {
    "departamento": {"nombre": "La Paz", "codigo": "LP"},
    "departamentos_bolivia": [
        ("La Paz", "LP"),
        ("Cochabamba", "CB"),
        ("Santa Cruz", "SC"),
        ("Oruro", "OR"),
        ("Potosí", "PT"),
        ("Chuquisaca", "CH"),
        ("Tarija", "TJ"),
        ("Beni", "BN"),
        ("Pando", "PA")
    ],
    "municipio": {"nombre": "Municipio de La Paz", "codigo": "MUN-LPZ-01"},
    "redes": [
        {
            "codigo": "RED-01",
            "nombre": "RED 1 - SUR OESTE (Macrodistrito Cotahuma)",
            "macrodistrito": "Cotahuma",
            "centros": [
                {"nombre": "Niño Kollo", "nivel": "Primer Nivel", "direccion": "Cotahuma"},
                {"nombre": "Alcoreza", "nivel": "Primer Nivel", "direccion": "Cotahuma"},
                {"nombre": "C.M.I. Villa Nuevo Potosí (Segundo Nivel)", "nivel": "Segundo Nivel", "direccion": "Cotahuma"},
                {"nombre": "La Gruta", "nivel": "Primer Nivel", "direccion": "Cotahuma"},
                {"nombre": "Bajo San Pedro", "nivel": "Primer Nivel", "direccion": "San Pedro"},
                {"nombre": "El Rosal", "nivel": "Primer Nivel", "direccion": "Cotahuma"},
                {"nombre": "San Luis", "nivel": "Primer Nivel", "direccion": "Cotahuma"},
                {"nombre": "Biblioteca", "nivel": "Primer Nivel", "direccion": "Cotahuma"},
                {"nombre": "Bajo Tacagua", "nivel": "Primer Nivel", "direccion": "Tacagua"},
                {"nombre": "Tembladerani", "nivel": "Primer Nivel", "direccion": "Tembladerani"},
                {"nombre": "8 de Diciembre", "nivel": "Primer Nivel", "direccion": "Cotahuma"},
                {"nombre": "Llojeta El Vergel", "nivel": "Primer Nivel", "direccion": "Llojeta"},
                {"nombre": "Pasankery", "nivel": "Primer Nivel", "direccion": "Pasankery"},
                {"nombre": "Alto Tacagua", "nivel": "Primer Nivel", "direccion": "Alto Tacagua"}
            ]
        },
        {
            "codigo": "RED-02",
            "nombre": "RED 2 - NOR OESTE (Macrodistrito Max Paredes)",
            "macrodistrito": "Max Paredes",
            "centros": [
                {"nombre": "El Tejar", "nivel": "Primer Nivel", "direccion": "El Tejar"},
                {"nombre": "Chamoco Chico", "nivel": "Primer Nivel", "direccion": "Max Paredes"},
                {"nombre": "Alto Mcal. Santa Cruz", "nivel": "Primer Nivel", "direccion": "Max Paredes"},
                {"nombre": "Villa Victoria", "nivel": "Primer Nivel", "direccion": "Villa Victoria"},
                {"nombre": "La Portada", "nivel": "Primer Nivel", "direccion": "La Portada"},
                {"nombre": "Obispo Indaburo", "nivel": "Primer Nivel", "direccion": "Max Paredes"},
                {"nombre": "Apumalla", "nivel": "Primer Nivel", "direccion": "Apumalla"},
                {"nombre": "Munaypata", "nivel": "Primer Nivel", "direccion": "Munaypata"},
                {"nombre": "Panticirca", "nivel": "Primer Nivel", "direccion": "Max Paredes"},
                {"nombre": "Ciudadela Ferroviaria", "nivel": "Primer Nivel", "direccion": "Ciudadela Ferroviaria"},
                {"nombre": "Said", "nivel": "Primer Nivel", "direccion": "Max Paredes"},
                {"nombre": "Zongo Choro", "nivel": "Primer Nivel", "direccion": "Zongo"},
                {"nombre": "Zongo Camsique", "nivel": "Primer Nivel", "direccion": "Zongo"},
                {"nombre": "Bajo Tejar", "nivel": "Primer Nivel", "direccion": "Bajo Tejar"}
            ]
        },
        {
            "codigo": "RED-03",
            "nombre": "RED 3 - NORTE CENTRAL (Macrodistrito Periférica Central)",
            "macrodistrito": "Periférica Central",
            "centros": [
                {"nombre": "Alto Miraflores", "nivel": "Primer Nivel", "direccion": "Miraflores"},
                {"nombre": "El Calvario", "nivel": "Primer Nivel", "direccion": "Periférica"},
                {"nombre": "3 de Mayo", "nivel": "Primer Nivel", "direccion": "Periférica"},
                {"nombre": "San Juan de Lazareto", "nivel": "Primer Nivel", "direccion": "Periférica"},
                {"nombre": "Achachicala", "nivel": "Primer Nivel", "direccion": "Achachicala"},
                {"nombre": "San José de Natividad", "nivel": "Primer Nivel", "direccion": "Periférica"},
                {"nombre": "Juancito Pinto", "nivel": "Primer Nivel", "direccion": "Periférica"},
                {"nombre": "Villa Fátima", "nivel": "Primer Nivel", "direccion": "Villa Fátima"},
                {"nombre": "Asistencia Pública", "nivel": "Primer Nivel", "direccion": "Central"},
                {"nombre": "Agua de la Vida", "nivel": "Primer Nivel", "direccion": "Periférica"},
                {"nombre": "Vino Tinto", "nivel": "Primer Nivel", "direccion": "Vino Tinto"},
                {"nombre": "Las Delicias Central", "nivel": "Primer Nivel", "direccion": "Periférica"},
                {"nombre": "Plan Autopista", "nivel": "Primer Nivel", "direccion": "Autopista"},
                {"nombre": "Chuquiaguillo", "nivel": "Primer Nivel", "direccion": "Chuquiaguillo"},
                {"nombre": "18 de Mayo", "nivel": "Primer Nivel", "direccion": "Periférica"}
            ]
        },
        {
            "codigo": "RED-04",
            "nombre": "RED 4 - SAN ANTONIO (Macrodistrito San Antonio)",
            "macrodistrito": "San Antonio",
            "centros": [
                {"nombre": "San Isidro", "nivel": "Primer Nivel", "direccion": "San Isidro"},
                {"nombre": "Villa Armonía", "nivel": "Primer Nivel", "direccion": "Villa Armonía"},
                {"nombre": "Choquechihuani", "nivel": "Primer Nivel", "direccion": "San Antonio"},
                {"nombre": "San Antonio Alto", "nivel": "Primer Nivel", "direccion": "San Antonio"},
                {"nombre": "Pampahasi Bajo", "nivel": "Primer Nivel", "direccion": "Pampahasi"},
                {"nombre": "Pampahasi Alto", "nivel": "Primer Nivel", "direccion": "Pampahasi"},
                {"nombre": "Kupini", "nivel": "Primer Nivel", "direccion": "Kupini"},
                {"nombre": "San Antonio Bajo", "nivel": "Primer Nivel", "direccion": "San Antonio"},
                {"nombre": "Valle Hermoso", "nivel": "Primer Nivel", "direccion": "Valle Hermoso"},
                {"nombre": "Villa Copacabana", "nivel": "Primer Nivel", "direccion": "Villa Copacabana"},
                {"nombre": "Villa Salomé", "nivel": "Primer Nivel", "direccion": "Villa Salomé"},
                {"nombre": "Escobar Uria", "nivel": "Primer Nivel", "direccion": "Escobar Uria"}
            ]
        },
        {
            "codigo": "RED-05",
            "nombre": "RED 5 - SUR (Macrodistrito Sur)",
            "macrodistrito": "Sur",
            "centros": [
                {"nombre": "Mallasilla", "nivel": "Primer Nivel", "direccion": "Mallasilla"},
                {"nombre": "Alto Obrajes", "nivel": "Primer Nivel", "direccion": "Alto Obrajes"},
                {"nombre": "Achumani", "nivel": "Primer Nivel", "direccion": "Achumani"},
                {"nombre": "Mallasa", "nivel": "Primer Nivel", "direccion": "Mallasa"},
                {"nombre": "Obrajes", "nivel": "Primer Nivel", "direccion": "Obrajes"},
                {"nombre": "Alto Seguéncoma", "nivel": "Primer Nivel", "direccion": "Seguéncoma"},
                {"nombre": "Bolognia", "nivel": "Primer Nivel", "direccion": "Bolognia"},
                {"nombre": "C.M.I. Bella Vista (Segundo Nivel)", "nivel": "Segundo Nivel", "direccion": "Bella Vista"},
                {"nombre": "C.M.I. Chasquipampa (Segundo Nivel)", "nivel": "Segundo Nivel", "direccion": "Chasquipampa"},
                {"nombre": "Cota Cota - El Rosal", "nivel": "Primer Nivel", "direccion": "Cota Cota"},
                {"nombre": "Bajo Llojeta", "nivel": "Primer Nivel", "direccion": "Llojeta"},
                {"nombre": "Alto Irpavi", "nivel": "Primer Nivel", "direccion": "Irpavi"}
            ]
        }
    ]
}


def crear_tablas_gamlp(conn):
    """Crea o actualiza el esquema jerárquico GAMLP en PostgreSQL."""
    cur = conn.cursor()
    
    print("[1/5] Creando tablas de Jerarquía Territorial...")
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
            nombre VARCHAR(150) NOT NULL,
            piso VARCHAR(100),
            contacto VARCHAR(100),
            encargado VARCHAR(255)
        );
    """)

    print("[2/5] Creando tablas principales de CMMS...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            aplicado TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS catalogo (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            marca VARCHAR(100),
            modelo VARCHAR(100),
            area VARCHAR(255),
            piso VARCHAR(100)
        );

        CREATE TABLE IF NOT EXISTS repuestos (
            id SERIAL PRIMARY KEY,
            tipo_equipo VARCHAR(150) NOT NULL,
            nombre_repuesto VARCHAR(150) NOT NULL,
            cantidad INTEGER DEFAULT 0,
            foto TEXT,
            UNIQUE(tipo_equipo, nombre_repuesto)
        );

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
            observaciones TEXT,
            centro_salud_id INTEGER REFERENCES centros_salud(id) ON DELETE SET NULL,
            red_salud_id INTEGER REFERENCES redes_salud(id) ON DELETE SET NULL
        );

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

        CREATE TABLE IF NOT EXISTS protocolos (
            id SERIAL PRIMARY KEY,
            fecha DATE NOT NULL,
            tipo_protocolo VARCHAR(100) NOT NULL,
            turno VARCHAR(20) NOT NULL,
            responsable VARCHAR(150),
            ruta_excel TEXT,
            UNIQUE (fecha, tipo_protocolo, turno)
        );

        CREATE TABLE IF NOT EXISTS papelera (
            id SERIAL PRIMARY KEY,
            tabla_origen VARCHAR(50) NOT NULL,
            id_original VARCHAR(100) NOT NULL,
            datos JSONB NOT NULL,
            eliminado_por VARCHAR(100),
            fecha_eliminacion TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
            nombre_completo VARCHAR(150) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL DEFAULT 'tecnico',
            permisos JSONB,
            sello_firma VARCHAR(255),
            activo BOOLEAN DEFAULT TRUE,
            creado TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()

    print("[3/5] Poblando Departamentos de Bolivia...")
    for dep_nom, dep_cod in JERARQUIA_DATOS["departamentos_bolivia"]:
        cur.execute("""
            INSERT INTO departamentos (nombre, codigo, estado)
            VALUES (%s, %s, 'Activo')
            ON CONFLICT (nombre) DO NOTHING;
        """, (dep_nom, dep_cod))
    conn.commit()

    cur.execute("SELECT id FROM departamentos WHERE nombre = 'La Paz';")
    dep_lp_id = cur.fetchone()[0]

    print("[4/5] Poblando Municipio de La Paz...")
    cur.execute("""
        INSERT INTO municipios (departamento_id, nombre, codigo, estado)
        VALUES (%s, %s, %s, 'Activo')
        ON CONFLICT (departamento_id, nombre) DO NOTHING;
    """, (dep_lp_id, JERARQUIA_DATOS["municipio"]["nombre"], JERARQUIA_DATOS["municipio"]["codigo"]))
    conn.commit()

    cur.execute("SELECT id FROM municipios WHERE nombre = %s AND departamento_id = %s;", (JERARQUIA_DATOS["municipio"]["nombre"], dep_lp_id))
    mun_lp_id = cur.fetchone()[0]

    print("[5/5] Poblando las 5 Redes de Salud y 67 Centros de Salud Oficiales...")
    total_centros = 0
    for red in JERARQUIA_DATOS["redes"]:
        cur.execute("""
            INSERT INTO redes_salud (municipio_id, departamento_id, nombre, codigo, macrodistrito, estado)
            VALUES (%s, %s, %s, %s, %s, 'Activo')
            ON CONFLICT (codigo) DO UPDATE 
            SET nombre = EXCLUDED.nombre, macrodistrito = EXCLUDED.macrodistrito;
        """, (mun_lp_id, dep_lp_id, red["nombre"], red["codigo"], red["macrodistrito"]))
        conn.commit()

        cur.execute("SELECT id FROM redes_salud WHERE codigo = %s;", (red["codigo"],))
        red_id = cur.fetchone()[0]

        for centro in red["centros"]:
            cur.execute("""
                INSERT INTO centros_salud (red_salud_id, nombre, nivel, direccion, estado)
                VALUES (%s, %s, %s, %s, 'Activo')
                ON CONFLICT (red_salud_id, nombre) DO UPDATE 
                SET nivel = EXCLUDED.nivel, direccion = EXCLUDED.direccion;
            """, (red_id, centro["nombre"], centro["nivel"], centro["direccion"]))
            total_centros += 1

    conn.commit()
    print(f"✅ ¡Estructura GAMLP creada con éxito! (5 Redes, {total_centros} Centros de Salud registrados).")
    cur.close()


def migrar_desde_respaldo(conn, ruta_json):
    """Restaura los datos existentes del JSON en la nueva base de datos."""
    if not os.path.exists(ruta_json):
        print(f"[WARN] No se encontró el archivo de respaldo en {ruta_json}")
        return

    print(f"\n📦 Restaurando datos desde {os.path.basename(ruta_json)}...")
    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    cur = conn.cursor()
    tablas = data.get("tablas", {})

    # Usuarios
    if "usuarios" in tablas:
        for u in tablas["usuarios"]:
            cur.execute("""
                INSERT INTO usuarios (id, nombre_usuario, nombre_completo, password_hash, rol, permisos, sello_firma, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (nombre_usuario) DO NOTHING;
            """, (u.get("id"), u.get("nombre_usuario"), u.get("nombre_completo"), u.get("password_hash"), u.get("rol"), json.dumps(u.get("permisos")), u.get("sello_firma"), u.get("activo", True)))
        conn.commit()
        print(f" - Usuarios restaurados: {len(tablas['usuarios'])}")

    # Áreas
    if "areas" in tablas:
        for a in tablas["areas"]:
            cur.execute("""
                INSERT INTO areas (nombre, piso, contacto, encargado)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (a.get("nombre"), a.get("piso"), a.get("contacto"), a.get("encargado")))
        conn.commit()
        print(f" - Áreas restauradas: {len(tablas['areas'])}")

    # Equipos
    if "equipos" in tablas:
        for eq in tablas["equipos"]:
            campos = [
                eq.get("id"), eq.get("nombre"), eq.get("marca"), eq.get("modelo"), eq.get("servicio"),
                eq.get("area"), eq.get("procedencia"), eq.get("fabricante"), eq.get("proveedor"),
                eq.get("anio_fab"), eq.get("numero_serie"), eq.get("t_elec"), eq.get("t_elco"),
                eq.get("t_mec"), eq.get("t_hid"), eq.get("t_neu"), eq.get("t_vap"),
                eq.get("a_comp"), eq.get("a_como"), eq.get("a_don"), eq.get("te_fijo"),
                eq.get("te_mov"), eq.get("te_por"), eq.get("garantia"), eq.get("fecha_inicio_garantia"),
                eq.get("fecha_vencimiento_garantia"), eq.get("criticidad"),
                json.dumps(eq.get("categorizacion_detalle")) if eq.get("categorizacion_detalle") else None,
                eq.get("estado", "Operativo"), eq.get("fecha_adquisicion"), eq.get("fecha_registro"),
                eq.get("foto"), eq.get("costo", 0), eq.get("voltaje"), eq.get("potencia"),
                eq.get("temperatura"), eq.get("humedad"), eq.get("corriente"), eq.get("peso"),
                eq.get("dimensiones"), eq.get("resolucion"), eq.get("contexto_operacional"),
                eq.get("funciones_equipo"), eq.get("acciones_preventivas"), eq.get("acciones_falla"),
                eq.get("fallas_funcionales"), eq.get("causas_fallo"), eq.get("efectos_fallo"),
                eq.get("efecto_entorno"), eq.get("observaciones")
            ]
            cur.execute("""
                INSERT INTO equipos (
                    id, nombre, marca, modelo, servicio, area, procedencia, fabricante, proveedor,
                    anio_fab, numero_serie, t_elec, t_elco, t_mec, t_hid, t_neu, t_vap,
                    a_comp, a_como, a_don, te_fijo, te_mov, te_por, garantia, fecha_inicio_garantia,
                    fecha_vencimiento_garantia, criticidad, categorizacion_detalle, estado,
                    fecha_adquisicion, fecha_registro, foto, costo, voltaje, potencia,
                    temperatura, humedad, corriente, peso, dimensiones, resolucion,
                    contexto_operacional, funciones_equipo, acciones_preventivas, acciones_falla,
                    fallas_funcionales, causas_fallo, efectos_fallo, efecto_entorno, observaciones
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (id) DO NOTHING;
            """, campos)
        conn.commit()
        print(f" - Equipos restaurados: {len(tablas['equipos'])}")

    # Historial de intervenciones
    if "historial_intervenciones" in tablas and tablas["historial_intervenciones"]:
        for h in tablas["historial_intervenciones"]:
            cur.execute("""
                INSERT INTO historial_intervenciones (
                    equipo_id, fecha, tipo, detalle, condicion, estado_equipo,
                    deficiencia, trabajo, observaciones, fecha_entrega, servicio_ht,
                    tipo_ht, realizado_por, hora_entrega, repuesto_usado, repuesto_nombre,
                    repuesto_cantidad, fecha_programada, tiempo_reparacion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT DO NOTHING;
            """, (
                h.get("equipo_id"), h.get("fecha"), h.get("tipo"), h.get("detalle"), h.get("condicion"),
                h.get("estado_equipo"), h.get("deficiencia"), h.get("trabajo"), h.get("observaciones"),
                h.get("fecha_entrega"), h.get("servicio_ht"), h.get("tipo_ht"), h.get("realizado_por"),
                h.get("hora_entrega"), h.get("repuesto_usado", False), h.get("repuesto_nombre"),
                h.get("repuesto_cantidad", 0), h.get("fecha_programada"), h.get("tiempo_reparacion", 0)
            ))
        conn.commit()
        print(f" - Intervenciones restauradas: {len(tablas['historial_intervenciones'])}")

    cur.close()
    print("✨ Restauración completada exitosamente.")


def ejecutar(host, port, user, password, dbname="postgres"):
    print(f"🔌 Conectando a Supabase PostgreSQL ({host}:{port})...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password,
            sslmode="require",
            connect_timeout=15
        )
        print("✅ ¡Conexión exitosa a Supabase Cloud!")
        crear_tablas_gamlp(conn)
        
        # Restaurar último respaldo local
        ruta_respaldo = os.path.join(os.path.dirname(__file__), "respaldos", "respaldo_cierre_2026-08-29_13-06-05.json")
        migrar_desde_respaldo(conn, ruta_respaldo)
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al conectar o migrar a Supabase: {e}")
        return False


if __name__ == "__main__":
    import sys
    pwd = sys.argv[1] if len(sys.argv) > 1 else "Adhemarz123$"
    user = sys.argv[2] if len(sys.argv) > 2 else "postgres.jqjegedcuafscqvzlnco"
    host = sys.argv[3] if len(sys.argv) > 3 else "aws-0-us-east-2.pooler.supabase.com"
    port = sys.argv[4] if len(sys.argv) > 4 else "5432"
    ejecutar(host, port, user, pwd)
