# Reglas de Espacio de Trabajo — CMMS GAMLP

## Identidad del Proyecto
Este espacio de trabajo contiene **CMMS GAMLP**, la plataforma oficial de gestión de equipamiento médico y mueblería/TI del Gobierno Autónomo Municipal de La Paz (Bolivia).

## Directrices de Desarrollo
1. **Lectura de Memoria:** Al iniciar cualquier tarea en este repositorio, consulta `CLAUDE.md` y `PROJECT_CONTEXT.md` para conocer el estado actual de los módulos y bases de datos.
2. **Entorno de Ejecución:** Usar `py -3` para comandos de Python en Windows.
3. **Verificación de Sintaxis:** Siempre compilar archivos modificados antes de hacer commit:
   `py -3 -m py_compile database.py web_server.py vistas_web_movil.py vistas/areas.py vistas/muebleria.py main.py`
4. **Git Push hacia Render:** Para desplegar cambios en producción, usar:
   `git -c http.curloptResolve="github.com:443:140.82.112.3" push origin main`
5. **Integridad de Base de Datos:**
   - La base de datos es PostgreSQL en Supabase (`relevamiento_2026`).
   - El centro `ALMACEN` en Red 1 tiene el ID `2118` (nunca usar '167 AUXILIO').
   - Validar siempre `centro_salud_id` y `red_salud_id` contra las tablas maestras antes de inserciones o actualizaciones en `database.py`.
