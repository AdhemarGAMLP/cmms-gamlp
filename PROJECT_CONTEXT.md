# PROJECT_CONTEXT.md — CMMS GAMLP

Documento maestro de transferencia técnica, estado del proyecto y memoria operativa.

---

## 📌 Datos Generales
- **Sistema:** CMMS GAMLP (Sistema de Gestión de Equipamiento Médico y Mueblería/TI).
- **Entidad:** Gobierno Autónomo Municipal de La Paz (GAMLP), Dirección de Salud, Bolivia.
- **Entorno de Producción:** [https://cmms-gamlp.onrender.com](https://cmms-gamlp.onrender.com)
- **Repositorio Git:** `https://github.com/AdhemarGAMLP/cmms-gamlp.git` (Rama `main`).
- **Base de Datos Activa:** PostgreSQL en Supabase (`aws-0-us-east-2.pooler.supabase.com:6543/postgres`, base `relevamiento_2026`).

---

## 📂 Mapa Rápido del Repositorio
| Archivo / Carpeta | Propósito |
|---|---|
| `web_server.py` | Servidor Flask central: rutas web públicas, autenticación de sesión, APIs REST y puente a base de datos. |
| `vistas_web_movil.py` | Módulo PWA completo para técnicos en campo: registro táctil, búsqueda rápida, escaneo de código, autollenado de área/piso y cola offline. |
| `database.py` | Conexión Supabase, lógica de transacciones, antiduplicados, normalización territorial y funciones de guardado / lectura. |
| `config.py` | Perfiles de conexión a bases de datos (`relevamiento_2026` y base `historica`). |
| `main.py` | Launcher de la suite de escritorio CustomTkinter para supervisores y biomédicos de base. |
| `vistas/` | Pantallas de escritorio: `inventario.py`, `muebleria.py`, `areas.py`, `catalogo.py`, `mantenimientos.py`, `repuestos.py`. |
| `respaldos/` | Snapshots JSON de seguridad del censo. |
| `CLAUDE.md` | Guía de referencia directa para agentes Claude. |

---

## 🔑 Decisiones de Diseño y Lecciones Aprendidas Recientes

1. **Catálogo Maestro Desacoplado:**
   - El catálogo de equipos es 100% genérico. No tiene área ni piso asignados de fábrica.
   - Al registrar un equipo en un centro, el técnico selecciona el centro y el área, y el sistema autocompleta el piso y responsable correspondientes a ese centro.

2. **Resolución de "ALMACEN" (ID 2118):**
   - El centro `ALMACEN` en la Red 1 (ID 2118) anteriormente se denominaba "167 AUXILIO".
   - Todo el sistema, las tablas `centros_salud`, `equipos`, `muebleria` y `areas` han sido unificados formalmente a `ALMACEN`.

3. **Blindaje de Llaves Foráneas (`centro_salud_id` / `red_salud_id`):**
   - En `database.py`, las funciones `guardar_mueble_db`, `guardar_equipo_db` y `guardar_area_db` validan estrictamente que cualquier ID enviado por los formularios exista en la tabla referenciada antes de ejecutar el SQL. Si no existe, se resuelve automáticamente por nombre para impedir caídas por `ForeignKeyViolation`.

4. **Optimización de Ancho de Banda Móvil:**
   - Carga inicial limitada a los últimos 100 activos con paginación diferida.
   - Las fotos no viajan en el payload masivo de `/api/equipos`, reduciendo transferencias de megabytes a kilobytes.

5. **Comando de Push Obligatorio:**
   - Debido a la resolución DNS de GitHub en el host local de Windows, siempre hacer push con:
     `git -c http.curloptResolve="github.com:443:140.82.112.3" push origin main`

---

## 🎯 Instrucciones para Nuevos Agentes o Sesiones de IA
Si estás leyendo esto como una nueva sesión de IA (Antigravity, Claude, Cursor o similar):
- **NO necesitas pedir credenciales ni reconstruir la arquitectura:** ya están especificadas en `config.py` y `database.py`.
- **Antes de modificar código:** verifica la sintaxis con `py -3 -m py_compile <archivos>`.
- **Al finalizar cualquier tarea:** haz commit y push a `main` con el flag de resolución DNS para que Render actualice producción automáticamente.
