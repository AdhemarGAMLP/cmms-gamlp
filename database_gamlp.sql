-- ============================================================
-- CMMS GAMLP - Script Oficial de Base de Datos PostgreSQL
-- Gobierno Autónomo Municipal de La Paz - Tecnologías Médicas
-- ============================================================

-- 1. DEPARTAMENTOS
CREATE TABLE IF NOT EXISTS departamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(10),
    estado VARCHAR(20) DEFAULT 'Activo'
);

-- 2. MUNICIPIOS
CREATE TABLE IF NOT EXISTS municipios (
    id SERIAL PRIMARY KEY,
    departamento_id INTEGER REFERENCES departamentos(id) ON DELETE CASCADE,
    nombre VARCHAR(150) NOT NULL,
    codigo VARCHAR(20),
    estado VARCHAR(20) DEFAULT 'Activo',
    CONSTRAINT unq_mun_dep UNIQUE (departamento_id, nombre)
);

-- 3. REDES DE SALUD
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

-- 4. CENTROS DE SALUD
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

-- 5. ÁREAS
CREATE TABLE IF NOT EXISTS areas (
    id SERIAL PRIMARY KEY,
    centro_salud_id INTEGER REFERENCES centros_salud(id) ON DELETE SET NULL,
    nombre VARCHAR(150) NOT NULL,
    piso VARCHAR(100),
    contacto VARCHAR(100),
    encargado VARCHAR(255)
);

-- 6. CATÁLOGO DE MODELOS
CREATE TABLE IF NOT EXISTS catalogo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    area VARCHAR(255),
    piso VARCHAR(100)
);

-- 7. REPUESTOS
CREATE TABLE IF NOT EXISTS repuestos (
    id SERIAL PRIMARY KEY,
    tipo_equipo VARCHAR(150) NOT NULL,
    nombre_repuesto VARCHAR(150) NOT NULL,
    cantidad INTEGER DEFAULT 0,
    foto TEXT,
    UNIQUE(tipo_equipo, nombre_repuesto)
);

-- 8. EQUIPOS MÉDICOS
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

-- 9. HISTORIAL DE INTERVENCIONES
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

-- 10. PROTOCOLOS (Conservada en BD pero desacoplada de la UI)
CREATE TABLE IF NOT EXISTS protocolos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo_protocolo VARCHAR(100) NOT NULL,
    turno VARCHAR(20) NOT NULL,
    responsable VARCHAR(150),
    ruta_excel TEXT,
    UNIQUE (fecha, tipo_protocolo, turno)
);

-- 11. PAPELERA
CREATE TABLE IF NOT EXISTS papelera (
    id SERIAL PRIMARY KEY,
    tabla_origen VARCHAR(50) NOT NULL,
    id_original VARCHAR(100) NOT NULL,
    datos JSONB NOT NULL,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP DEFAULT NOW()
);

-- 12. USUARIOS
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

-- ============================================================
-- POBLACIÓN INICIAL DE LA JERARQUÍA GAMLP
-- ============================================================

-- Departamentos
INSERT INTO departamentos (nombre, codigo) VALUES
('La Paz', 'LP'),
('Cochabamba', 'CB'),
('Santa Cruz', 'SC'),
('Oruro', 'OR'),
('Potosí', 'PT'),
('Chuquisaca', 'CH'),
('Tarija', 'TJ'),
('Beni', 'BN'),
('Pando', 'PA')
ON CONFLICT (nombre) DO NOTHING;

-- Municipio de La Paz
INSERT INTO municipios (departamento_id, nombre, codigo)
SELECT id, 'Municipio de La Paz', 'MUN-LPZ-01' FROM departamentos WHERE nombre = 'La Paz'
ON CONFLICT (departamento_id, nombre) DO NOTHING;

-- 5 Redes de Salud
DO $$
DECLARE
    mun_id INT;
    dep_id INT;
BEGIN
    SELECT id INTO dep_id FROM departamentos WHERE nombre = 'La Paz';
    SELECT id INTO mun_id FROM municipios WHERE nombre = 'Municipio de La Paz' AND departamento_id = dep_id;

    INSERT INTO redes_salud (municipio_id, departamento_id, nombre, codigo, macrodistrito) VALUES
    (mun_id, dep_id, 'RED 1 - SUR OESTE (Macrodistrito Cotahuma)', 'RED-01', 'Cotahuma'),
    (mun_id, dep_id, 'RED 2 - NOR OESTE (Macrodistrito Max Paredes)', 'RED-02', 'Max Paredes'),
    (mun_id, dep_id, 'RED 3 - NORTE CENTRAL (Macrodistrito Periférica Central)', 'RED-03', 'Periférica Central'),
    (mun_id, dep_id, 'RED 4 - SAN ANTONIO (Macrodistrito San Antonio)', 'RED-04', 'San Antonio'),
    (mun_id, dep_id, 'RED 5 - SUR (Macrodistrito Sur)', 'RED-05', 'Sur')
    ON CONFLICT (codigo) DO UPDATE 
    SET nombre = EXCLUDED.nombre, macrodistrito = EXCLUDED.macrodistrito;
END $$;

-- 67 Centros de Salud Oficiales
DO $$
DECLARE
    r1 INT; r2 INT; r3 INT; r4 INT; r5 INT;
BEGIN
    SELECT id INTO r1 FROM redes_salud WHERE codigo = 'RED-01';
    SELECT id INTO r2 FROM redes_salud WHERE codigo = 'RED-02';
    SELECT id INTO r3 FROM redes_salud WHERE codigo = 'RED-03';
    SELECT id INTO r4 FROM redes_salud WHERE codigo = 'RED-04';
    SELECT id INTO r5 FROM redes_salud WHERE codigo = 'RED-05';

    -- RED 1
    INSERT INTO centros_salud (red_salud_id, nombre, nivel, direccion) VALUES
    (r1, 'Niño Kollo', 'Primer Nivel', 'Cotahuma'),
    (r1, 'Alcoreza', 'Primer Nivel', 'Cotahuma'),
    (r1, 'C.M.I. Villa Nuevo Potosí (Segundo Nivel)', 'Segundo Nivel', 'Cotahuma'),
    (r1, 'La Gruta', 'Primer Nivel', 'Cotahuma'),
    (r1, 'Bajo San Pedro', 'Primer Nivel', 'San Pedro'),
    (r1, 'El Rosal', 'Primer Nivel', 'Cotahuma'),
    (r1, 'San Luis', 'Primer Nivel', 'Cotahuma'),
    (r1, 'Biblioteca', 'Primer Nivel', 'Cotahuma'),
    (r1, 'Bajo Tacagua', 'Primer Nivel', 'Tacagua'),
    (r1, 'Tembladerani', 'Primer Nivel', 'Tembladerani'),
    (r1, '8 de Diciembre', 'Primer Nivel', 'Cotahuma'),
    (r1, 'Llojeta El Vergel', 'Primer Nivel', 'Llojeta'),
    (r1, 'Pasankery', 'Primer Nivel', 'Pasankery'),
    (r1, 'Alto Tacagua', 'Primer Nivel', 'Alto Tacagua'),

    -- RED 2
    (r2, 'El Tejar', 'Primer Nivel', 'El Tejar'),
    (r2, 'Chamoco Chico', 'Primer Nivel', 'Max Paredes'),
    (r2, 'Alto Mcal. Santa Cruz', 'Primer Nivel', 'Max Paredes'),
    (r2, 'Villa Victoria', 'Primer Nivel', 'Villa Victoria'),
    (r2, 'La Portada', 'Primer Nivel', 'La Portada'),
    (r2, 'Obispo Indaburo', 'Primer Nivel', 'Max Paredes'),
    (r2, 'Apumalla', 'Primer Nivel', 'Apumalla'),
    (r2, 'Munaypata', 'Primer Nivel', 'Munaypata'),
    (r2, 'Panticirca', 'Primer Nivel', 'Max Paredes'),
    (r2, 'Ciudadela Ferroviaria', 'Primer Nivel', 'Ciudadela Ferroviaria'),
    (r2, 'Said', 'Primer Nivel', 'Max Paredes'),
    (r2, 'Zongo Choro', 'Primer Nivel', 'Zongo'),
    (r2, 'Zongo Camsique', 'Primer Nivel', 'Zongo'),
    (r2, 'Bajo Tejar', 'Primer Nivel', 'Bajo Tejar'),

    -- RED 3
    (r3, 'Alto Miraflores', 'Primer Nivel', 'Miraflores'),
    (r3, 'El Calvario', 'Primer Nivel', 'Periférica'),
    (r3, '3 de Mayo', 'Primer Nivel', 'Periférica'),
    (r3, 'San Juan de Lazareto', 'Primer Nivel', 'Periférica'),
    (r3, 'Achachicala', 'Primer Nivel', 'Achachicala'),
    (r3, 'San José de Natividad', 'Primer Nivel', 'Periférica'),
    (r3, 'Juancito Pinto', 'Primer Nivel', 'Periférica'),
    (r3, 'Villa Fátima', 'Primer Nivel', 'Villa Fátima'),
    (r3, 'Asistencia Pública', 'Primer Nivel', 'Central'),
    (r3, 'Agua de la Vida', 'Primer Nivel', 'Periférica'),
    (r3, 'Vino Tinto', 'Primer Nivel', 'Vino Tinto'),
    (r3, 'Las Delicias Central', 'Primer Nivel', 'Periférica'),
    (r3, 'Plan Autopista', 'Primer Nivel', 'Autopista'),
    (r3, 'Chuquiaguillo', 'Primer Nivel', 'Chuquiaguillo'),
    (r3, '18 de Mayo', 'Primer Nivel', 'Periférica'),

    -- RED 4
    (r4, 'San Isidro', 'Primer Nivel', 'San Isidro'),
    (r4, 'Villa Armonía', 'Primer Nivel', 'Villa Armonía'),
    (r4, 'Choquechihuani', 'Primer Nivel', 'San Antonio'),
    (r4, 'San Antonio Alto', 'Primer Nivel', 'San Antonio'),
    (r4, 'Pampahasi Bajo', 'Primer Nivel', 'Pampahasi'),
    (r4, 'Pampahasi Alto', 'Primer Nivel', 'Pampahasi'),
    (r4, 'Kupini', 'Primer Nivel', 'Kupini'),
    (r4, 'San Antonio Bajo', 'Primer Nivel', 'San Antonio'),
    (r4, 'Valle Hermoso', 'Primer Nivel', 'Valle Hermoso'),
    (r4, 'Villa Copacabana', 'Primer Nivel', 'Villa Copacabana'),
    (r4, 'Villa Salomé', 'Primer Nivel', 'Villa Salomé'),
    (r4, 'Escobar Uria', 'Primer Nivel', 'Escobar Uria'),

    -- RED 5
    (r5, 'Mallasilla', 'Primer Nivel', 'Mallasilla'),
    (r5, 'Alto Obrajes', 'Primer Nivel', 'Alto Obrajes'),
    (r5, 'Achumani', 'Primer Nivel', 'Achumani'),
    (r5, 'Mallasa', 'Primer Nivel', 'Mallasa'),
    (r5, 'Obrajes', 'Primer Nivel', 'Obrajes'),
    (r5, 'Alto Seguéncoma', 'Primer Nivel', 'Seguéncoma'),
    (r5, 'Bolognia', 'Primer Nivel', 'Bolognia'),
    (r5, 'C.M.I. Bella Vista (Segundo Nivel)', 'Segundo Nivel', 'Bella Vista'),
    (r5, 'C.M.I. Chasquipampa (Segundo Nivel)', 'Segundo Nivel', 'Chasquipampa'),
    (r5, 'Cota Cota - El Rosal', 'Primer Nivel', 'Cota Cota'),
    (r5, 'Bajo Llojeta', 'Primer Nivel', 'Llojeta'),
    (r5, 'Alto Irpavi', 'Primer Nivel', 'Irpavi')
    ON CONFLICT (red_salud_id, nombre) DO UPDATE
    SET nivel = EXCLUDED.nivel, direccion = EXCLUDED.direccion;
END $$;
