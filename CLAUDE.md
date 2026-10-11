# CLAUDE.md — CMMS GAMLP (Contexto Integral de Desarrollo)

Este archivo proporciona el contexto técnico, arquitectónico y operativo completo del proyecto **CMMS GAMLP** para que cualquier instancia de Claude (Claude Code, Claude Projects o Claude Desktop) pueda trabajar de forma inmediata sin necesidad de explicaciones adicionales.

---

## 🏥 Descripción del Proyecto
**CMMS GAMLP** (Sistema de Gestión de Mantenimiento y Relevamiento de Equipamiento Médico y Mueblería / TI) para el **Gobierno Autónomo Municipal de La Paz (Bolivia)**.
- **Objetivo Principal:** Control patrimonial, censo en campo, gestión de intervenciones técnicas y relevamiento de activos de salud en tiempo real.
- **Alcance Operativo:** 5 Redes de Salud (Macrodistritos de La Paz) y 68 Centros de Salud de 1er y 2do Nivel.
- **Ritmo de Campo:** Registro intensivo de ~400 activos diarios por técnicos biomédicos en celulares y laptops.

---

## 🏛️ Arquitectura del Sistema y Módulos

```
CMMS_GAMLP/
├── web_server.py           # Servidor Web Flask, APIs REST JSON y motor de vistas web públicas y administrativas
├── vistas_web_movil.py     # Aplicación Web Móvil PWA (/movil/registro): Formulario táctil, inventario móvil, offline
├── database.py             # Capa de datos PostgreSQL (Supabase), pooling, migraciones, CRUD blindado y cola offline
├── config.py               # Configuración de perfiles de base de datos (relevamiento_2026 e historica)
├── main.py                 # Aplicación de escritorio CustomTkinter (Admin Suite)
├── vistas/                 # Módulos gráficos de escritorio:
│   ├── inventario.py       # Gestión de equipos médicos (Desktop)
│   ├── muebleria.py        # Gestión de activos de mueblería y computación (Desktop)
│   ├── areas.py            # Áreas y pisos por centro de salud (Desktop)
│   ├── catalogo.py         # Catálogo maestro de equipos (Desktop)
│   ├── mantenimientos.py   # Registro de fichas técnicas e intervenciones (Desktop)
│   └── repuestos.py        # Inventario de repuestos y piezas (Desktop)
├── respaldos/              # Respaldos JSON de cierres periódicos y emergencias
└── assets/ o static/       # Iconos, estilos y recursos gráficos
```

---

## 💻 Stack Tecnológico
- **Backend Servidor:** Python 3.12+ / Flask. Desplegado en **Render** (`https://cmms-gamlp.onrender.com`).
- **Base de Datos:** PostgreSQL en la nube en **Supabase** (Transaction Connection Pooler en puerto `6543` host `aws-0-us-east-2.pooler.supabase.com`).
- **Frontend Móvil:** HTML5 / CSS3 responsivo táctil / Vanilla JavaScript integrado en `vistas_web_movil.py`.
- **Frontend Escritorio:** Python con `customtkinter` y `tkinter`.
- **Hosting / CI-CD:** Render conectado al repositorio GitHub `AdhemarGAMLP/cmms-gamlp` rama `main`. Cada push a `main` despliega automáticamente en producción.

---

## 📋 Reglas de Negocio y Convenciones Críticas

### 1. Jerarquía Territorial
- **5 Redes de Salud:**
  - `RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)`
  - `RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)`
  - `RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)`
  - `RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)`
  - `RED 5-SUR (MACRODISTRITO SUR)`
- **68 Centros de Salud:**
  - El centro `ALMACEN` pertenece a la Red 1 y tiene el **ID 2118** (anteriormente se llamaba *167 AUXILIO*). Siempre usar el nombre `"ALMACEN"`.

### 2. Tablas Principales en PostgreSQL
- `equipos`: Equipos médicos con código AF, marca, modelo, serie, fotos, estado operativo (Operativo, En Mantenimiento, Baja), criticidad, área, custodio y llaves foráneas (`centro_salud_id`, `red_salud_id`).
- `muebleria`: Mueblería y computación/TI (`tipo_activo`, `descripcion`, `marca`, `modelo`, `serie`, `codigo_sispam`, `bertin`, `sapm`, `ubicacion`, `persona_asignada`, `ci_asignado`, `cargo_asignado`, `centro_salud_id`, `red_salud_id`).
- `centros_salud`: `id`, `nombre`, `red_salud_id`, `nivel`, `estado`.
- `redes_salud`: `id`, `nombre`, `codigo`.
- `areas`: Áreas físicas por centro (`nombre`, `piso`, `encargado`, `cargo`, `ci_encargado`, `centro_salud_id`).
- `catalogo_equipos`: Catálogo estándar genérico de tecnologías médicas (sin piso ni centro preasignado).

### 3. Blindaje de Llaves Foráneas (Regla de Oro en `database.py`)
- Antes de insertar o actualizar en `equipos` o `muebleria`, **SIEMPRE** verificar que `centro_salud_id` y `red_salud_id` existan en sus respectivas tablas.
- Si vienen nulos o con IDs inexistentes (por desincronización de caché del celular), resolver el ID numérico por coincidencia de nombre (`nombre ILIKE %s`). Si no existe, permitir que sea `NULL`. Nunca dejar que PostgreSQL lance un `ForeignKeyViolation`.

### 4. Paginación y Rendimiento HTTP
- En móviles y web pública, los inventarios cargan los **últimos 100 activos** registrados con botón "Ver más / Cargar más" para evitar saturar el ancho de banda 4G de los técnicos.
- Las fotos pesadas no se envían en el listado masivo (`/api/equipos`), sino bajo demanda individual (`/api/equipo/<id>`).

---

## 🛠️ Comandos Frecuentes

### Ejecutar Localmente
```powershell
# Iniciar servidor web local (puerto 5000)
py -3 web_server.py

# Iniciar aplicación de escritorio CustomTkinter
py -3 main.py
```

### Validar y Compilar Sintaxis (Sin romper producción)
```powershell
py -3 -m py_compile database.py web_server.py vistas_web_movil.py vistas/areas.py vistas/muebleria.py main.py
```

### Despliegue en Render (Git Push)
En este entorno Windows con resolución DNS restringida, **siempre usar este comando para subir cambios:**
```powershell
git -c http.curloptResolve="github.com:443:140.82.112.3" push origin main
```

---

## 🩺 Endpoints de Salud y Monitoreo
- **Ping / Keep-Alive:** `GET /ping` o `GET /api/health`
  - Retorna `200 OK` con JSON `{"status": "ok", "service": "...", "database": "Supabase PostgreSQL (Activo)"}`.
  - Diseñado para UptimeRobot / cron de monitoreo cada 10 minutos.
