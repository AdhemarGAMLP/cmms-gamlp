# vistas_web_movil.py
# Aplicación Web Móvil y Tablet Completa (SPA) para Técnicos y Administradores GAMLP
# 10 Módulos Operativos Adaptables con Control de Permisos por Rol:
# Inventario, Catálogo, Mueblería/TI, Áreas, Repuestos, Historial, Cronograma, Análisis, Sedes y Usuarios.
# Con soporte completo para Crear, Visualizar, Modificar y Eliminar (con respaldo en Papelera).

HTML_MOVIL_LOGIN = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SGEM GAMLP • Acceso Móvil</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0F172A;
            --primary-dark: #020617;
            --accent: #0284C7;
            --bg: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --danger: #EF4444;
            --radius: 14px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0F172A;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            -webkit-font-smoothing: antialiased;
        }
        .login-card {
            background: var(--card-bg);
            border-radius: var(--radius);
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            width: 100%;
            max-width: 420px;
            padding: 35px 25px;
            text-align: center;
        }
        .escudo-badge {
            display: inline-block;
            background: #F1F5F9;
            color: #0F172A;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            border: 1px solid #E2E8F0;
        }
        .login-card h1 {
            color: var(--text-main);
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 6px;
        }
        .login-card p {
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 25px;
            line-height: 1.4;
        }
        .form-group {
            text-align: left;
            margin-bottom: 18px;
        }
        .form-label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 6px;
        }
        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }
        .input-icon {
            position: absolute;
            left: 14px;
            font-size: 18px;
            color: #94A3B8;
            pointer-events: none;
        }
        .form-control {
            width: 100%;
            height: 48px;
            padding: 10px 14px 10px 44px;
            font-size: 16px;
            border: 1.5px solid var(--border);
            border-radius: 12px;
            background: #F8FAFC;
            color: var(--text-main);
            transition: all 0.2s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: var(--accent);
            background: #FFFFFF;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
        }
        .btn-submit {
            width: 100%;
            height: 50px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s ease;
            margin-top: 10px;
            box-shadow: 0 4px 12px rgba(0, 86, 145, 0.3);
        }
        .btn-submit:active {
            background: var(--primary-dark);
            transform: scale(0.98);
        }
        .alert-error {
            background: #FEF2F2;
            border: 1.5px solid #FCA5A5;
            color: var(--danger);
            padding: 12px;
            border-radius: 10px;
            font-size: 13px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            text-align: left;
        }
        .footer-note {
            margin-top: 25px;
            font-size: 11px;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="escudo-badge">🏥 SISTEMA SGEM GAMLP</div>
        <h1>Acceso Institucional</h1>
        <p>Control y Relevamiento Biomédico en Redes de Salud del Municipio de La Paz</p>

        {% if error %}
        <div class="alert-error">
            <span>⚠️</span>
            <span>{{ error }}</span>
        </div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label class="form-label" for="usuario">Usuario:</label>
                <div class="input-wrapper">
                    <span class="input-icon">👤</span>
                    <input type="text" id="usuario" name="usuario" class="form-control" placeholder="Usuario" required autofocus autocomplete="username">
                </div>
            </div>

            <div class="form-group">
                <label class="form-label" for="password">Contraseña:</label>
                <div class="input-wrapper">
                    <span class="input-icon">🔒</span>
                    <input type="password" id="password" name="password" class="form-control" placeholder="••••••••" required autocomplete="current-password">
                </div>
            </div>

            <button type="submit" class="btn-submit">Ingresar al Sistema</button>
        </form>

        <div class="footer-note">
            Gobierno Autónomo Municipal de La Paz &copy; 2026<br>Dirección de Salud
        </div>
    </div>
</body>
</html>
"""

HTML_MOVIL_REGISTRO = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SGEM GAMLP • Suite Móvil y Tablet</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0F172A;
            --primary-dark: #020617;
            --accent: #0284C7;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --bg: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --border-hover: #CBD5E1;
            --radius-card: 12px;
            --radius-btn: 8px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 70px;
            -webkit-font-smoothing: antialiased;
        }

        /* BARRA SUPERIOR BASE */
        .top-navbar {
            background: #0F172A;
            border-bottom: 1px solid #1E293B;
            color: white;
            padding: 12px 20px;
            position: sticky;
            top: 0;
            z-index: 200;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            gap: 12px;
        }
        .top-navbar-main {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex: 1;
        }
        .brand-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .brand-title-wrap {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .brand-title {
            font-size: 17px;
            font-weight: 800;
            letter-spacing: 0.3px;
            color: #FFFFFF;
            line-height: 1.2;
        }
        .badge-suite-movil {
            background: #0284C7;
            color: #FFFFFF;
            font-size: 10px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .brand-sub {
            font-size: 11px;
            color: #94A3B8;
            line-height: 1.2;
        }
        .user-profile-actions, .user-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .user-badge {
            background: rgba(255, 255, 255, 0.15);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            max-width: 180px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #F8FAFC;
        }
        .btn-nav-action {
            background: rgba(239, 68, 68, 0.9);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            transition: background 0.15s ease;
        }
        .btn-nav-action:hover { background: #DC2626; }
        .top-navbar-links {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-nav-quick {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            text-decoration: none;
            color: #FFFFFF;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            transition: opacity 0.15s ease;
            white-space: nowrap;
        }
        .btn-nav-quick:hover { opacity: 0.9; }
        .btn-quick-portal { background: #0284C7; }
        .btn-quick-analisis { background: #4F46E5; }

        /* SELECTOR TERRITORIAL PERMANENTE (RED Y CENTRO) */
        .selector-sede-bar {
            background: #FFFFFF;
            border-bottom: 1px solid var(--border);
            padding: 10px 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }
        .sede-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            max-width: 1100px;
            margin: 0 auto;
            width: 100%;
        }
        .sede-sel-group label {
            display: block;
            font-size: 11px;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 3px;
            text-transform: uppercase;
        }
        .sede-select {
            width: 100%;
            height: 38px;
            padding: 4px 10px;
            border-radius: 8px;
            border: 1.5px solid var(--border);
            background: #F8FAFC;
            font-size: 13px;
            font-weight: 600;
            color: var(--primary-dark);
            outline: none;
        }

        /* BARRA DE PESTAÑAS RESPONSIVA */
        .tab-bar-nav {
            display: flex;
            background: #E2E8F0;
            padding: 6px 12px;
            overflow-x: auto;
            white-space: nowrap;
            gap: 6px;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
            border-bottom: 1px solid #CBD5E1;
        }
        .tab-bar-nav::-webkit-scrollbar { display: none; }
        .tab-btn {
            flex: 0 0 auto;
            min-width: 90px;
            text-align: center;
            padding: 8px 14px;
            font-size: 12.5px;
            font-weight: 700;
            border-radius: 8px;
            border: none;
            background: transparent;
            color: #475569;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .tab-btn.active {
            background: #FFFFFF;
            color: var(--primary);
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }

        /* CONTENEDORES Y GRID RESPONSIVO */
        .container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            padding: 12px 14px;
            transition: max-width 0.2s ease;
        }

        /* MEDIA QUERIES PARA TABLETS (>= 768px) */
        @media (min-width: 768px) {
            .container {
                max-width: 1100px;
                padding: 20px 24px;
            }
            .cards-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 14px;
            }
            .cards-grid-3 {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 14px;
            }
            .modal-content-sheet {
                border-radius: 20px !important;
                margin: auto !important;
                max-height: 85vh !important;
                max-width: 680px !important;
                animation: zoomIn 0.2s ease-out !important;
            }
            .modal-overlay {
                align-items: center !important;
                padding: 20px;
            }
            .tab-btn {
                padding: 9px 16px;
                font-size: 13px;
            }
        }

        /* MEDIA QUERIES PARA ESCRITORIO / PANTALLA GRANDE (>= 1024px) */
        @media (min-width: 1024px) {
            .container {
                max-width: 96% !important;
                padding: 16px 24px;
            }
            .cards-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            .cards-grid-3 {
                grid-template-columns: repeat(4, 1fr);
            }
        }

        /* TABLA DE DATOS ESTILO SOFTWARE DE ESCRITORIO */
        .table-responsive {
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            background: #FFFFFF;
            border-radius: var(--radius-card);
            border: 1px solid var(--border);
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            text-align: left;
            white-space: nowrap;
        }
        .data-table th {
            background: #F1F5F9;
            color: #1E293B;
            font-weight: 700;
            padding: 11px 14px;
            border-bottom: 2px solid #CBD5E1;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.4px;
        }
        .data-table td {
            padding: 9px 14px;
            border-bottom: 1px solid #E2E8F0;
            color: #1E293B;
            vertical-align: middle;
        }
        .data-table tbody tr:nth-child(even) {
            background: #F8FAFC;
        }
        .data-table tbody tr:hover {
            background: #F0F9FF;
        }
        .btn-table-action {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 9px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            text-decoration: none;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s ease;
        }
        .btn-table-view {
            background: #E0F2FE;
            color: #0369A1;
            border-color: #BAE6FD;
        }
        .btn-table-view:hover { background: #BAE6FD; }
        .btn-table-edit {
            background: #FEF3C7;
            color: #B45309;
            border-color: #FDE68A;
        }
        .btn-table-edit:hover { background: #FDE68A; }
        .btn-table-del {
            background: #FEE2E2;
            color: #B91C1C;
            border-color: #FECACA;
        }
        .btn-table-del:hover { background: #FECACA; }

        .tab-pane { display: none; }
        .tab-pane.active {
            display: block;
            animation: fadeIn 0.2s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes zoomIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }

        /* BARRA DE BÚSQUEDA Y ACCIÓN */
        .tab-tools-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 14px;
            align-items: center;
        }
        .search-input {
            flex: 1;
            height: 42px;
            padding: 6px 12px 6px 36px;
            border-radius: var(--radius-btn);
            border: 1.5px solid var(--border);
            background: #FFFFFF url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="%2394A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>') no-repeat 12px center;
            font-size: 14px;
            outline: none;
        }
        .search-input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
        }
        .btn-add-action {
            height: 42px;
            padding: 0 16px;
            border-radius: var(--radius-btn);
            border: none;
            background: var(--primary);
            color: white;
            font-size: 13.5px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(0,86,145,0.25);
        }
        .btn-add-action:active { transform: scale(0.97); }

        /* FILTRO RÁPIDO DE ACTIVOS (TODO / EQUIPOS / MUEBLES) */
        .asset-filters-bar {
            display: flex;
            gap: 8px;
            margin: 10px 0 14px 0;
            overflow-x: auto;
            padding-bottom: 4px;
            -webkit-overflow-scrolling: touch;
        }
        .asset-filters-bar::-webkit-scrollbar { display: none; }
        .btn-filter-pill {
            padding: 7px 14px;
            border-radius: 20px;
            border: 1.5px solid var(--border);
            background: #FFFFFF;
            color: var(--text-muted);
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn-filter-pill:hover {
            border-color: #94A3B8;
            color: var(--text-main);
            background: #F8FAFC;
        }
        .btn-filter-pill.active {
            background: var(--primary);
            color: #FFFFFF;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(0,59,100,0.25);
        }
        .pill-count {
            background: rgba(0,0,0,0.08);
            padding: 1px 7px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 800;
        }
        .btn-filter-pill.active .pill-count {
            background: rgba(255,255,255,0.25);
            color: #FFFFFF;
        }

        /* TARJETAS DE CONTENIDO */
        .card-item {
            background: var(--card-bg);
            border-radius: var(--radius-card);
            padding: 14px 16px;
            margin-bottom: 10px;
            border: 1px solid var(--border);
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .card-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }
        .card-item-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .item-title {
            font-size: 15px;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.3;
        }
        .badge-af {
            font-family: monospace;
            font-size: 11px;
            font-weight: 800;
            background: #EFF6FF;
            color: var(--primary);
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid #BFDBFE;
            white-space: nowrap;
        }
        .badge-status {
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 12px;
            text-transform: uppercase;
        }
        .status-bueno { background: #DCFCE7; color: #166534; }
        .status-regular { background: #FEF3C7; color: #92400E; }
        .status-malo { background: #FEE2E2; color: #991B1B; }
        .status-crit-alta { background: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5; }
        .status-crit-media { background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; }
        .status-crit-baja { background: #DCFCE7; color: #16A34A; border: 1px solid #86EFAC; }

        .item-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }
        .item-detail-row {
            font-size: 12px;
            color: #334155;
            background: #F8FAFC;
            padding: 6px 10px;
            border-radius: 8px;
            margin-top: 4px;
            line-height: 1.4;
        }
        .item-actions {
            display: flex;
            gap: 6px;
            margin-top: 8px;
            justify-content: flex-end;
            flex-wrap: wrap;
        }
        .btn-card-view {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            background: #EFF6FF;
            color: var(--primary);
            border: 1px solid #BFDBFE;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
        }
        .btn-card-edit {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            background: #FEF3C7;
            color: #B45309;
            border: 1px solid #FDE68A;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .btn-card-edit:hover { background: #FDE68A; }
        .btn-card-del {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            background: #FEE2E2;
            color: #DC2626;
            border: 1px solid #FCA5A5;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .btn-card-del:hover { background: #FCA5A5; }
        .btn-restore-action {
            padding: 7px 14px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 700;
            background: #ECFDF5;
            color: #059669;
            border: 1px solid #A7F3D0;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .btn-restore-action:hover {
            background: #10B981;
            color: #FFFFFF;
            border-color: #059669;
            box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
        }
        .btn-purge-action {
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            background: #FEF2F2;
            color: #B91C1C;
            border: 1px solid #FECACA;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .btn-purge-action:hover {
            background: #DC2626;
            color: #FFFFFF;
        }

        /* MODALES */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(3px);
            z-index: 500;
            display: none;
            align-items: flex-end;
            justify-content: center;
        }
        .modal-content-sheet {
            background: #FFFFFF;
            width: 100%;
            max-width: 600px;
            max-height: 90vh;
            border-radius: 20px 20px 0 0;
            padding: 20px 18px 30px 18px;
            overflow-y: auto;
            box-shadow: 0 -8px 30px rgba(0,0,0,0.25);
            animation: slideUp 0.25s ease-out;
        }
        @keyframes slideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
        }
        .modal-header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1.5px solid #F1F5F9;
        }
        .modal-header-bar h2 {
            font-size: 17px;
            font-weight: 800;
            color: var(--primary-dark);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn-close-modal {
            background: #F1F5F9;
            border: none;
            font-size: 16px;
            font-weight: 800;
            color: var(--text-muted);
            width: 32px;
            height: 32px;
            border-radius: 16px;
            cursor: pointer;
        }

        /* FORMULARIOS */
        .form-group { margin-bottom: 14px; text-align: left; }
        .form-label { display: block; font-size: 12px; font-weight: 700; color: var(--text-main); margin-bottom: 5px; }
        .form-control {
            width: 100%;
            height: 44px;
            padding: 8px 12px;
            font-size: 15px;
            border: 1.5px solid var(--border);
            border-radius: 10px;
            background: #F8FAFC;
            color: var(--text-main);
            outline: none;
        }
        .form-control:focus {
            border-color: var(--accent);
            background: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
        }
        .form-control::placeholder {
            color: #94A3B8;
            opacity: 0.7;
            font-style: italic;
        }
        textarea.form-control {
            min-height: 80px !important;
            height: auto;
            resize: vertical;
            padding: 10px 12px;
            line-height: 1.4;
            box-sizing: border-box;
        }
        .row-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .row-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
        }
        @media (max-width: 600px) {
            .row-3 {
                grid-template-columns: 1fr;
            }
        }
        .form-section-banner {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #EFF6FF;
            color: var(--primary);
            font-size: 13px;
            font-weight: 800;
            padding: 8px 12px;
            border-radius: 10px;
            margin: 16px 0 10px 0;
            border-left: 4px solid var(--accent);
        }
        .radio-pill-group {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-top: 4px;
        }
        .pill-radio {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: #F8FAFC;
            border: 1.5px solid var(--border);
            border-radius: 20px;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .pill-radio:hover {
            background: #F1F5F9;
        }
        .btn-toggle-accordion {
            background: #F1F5F9;
            border: 1.5px solid #CBD5E1;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 700;
            color: var(--primary-dark);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 12px;
            cursor: pointer;
        }
        .btn-toggle-accordion:hover {
            background: #E2E8F0;
        }
        .btn-toggle-accordion-inline {
            background: #FFFFFF;
            border: 1px solid #BFDBFE;
            color: var(--accent);
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            cursor: pointer;
        }
        .crit-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 4px;
            border-bottom: 1px solid #E2E8F0;
            font-size: 12px;
        }
        .crit-row:last-child {
            border-bottom: none;
        }
        .crit-radios {
            display: flex;
            gap: 10px;
        }
        .crit-radios label {
            font-size: 11px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 3px;
            cursor: pointer;
        }
        .btn-modal-submit {
            width: 100%;
            height: 48px;
            background: var(--success);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            margin-top: 10px;
            box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
        }
        .btn-modal-submit:active { transform: scale(0.98); }

        /* AUTOCOMPLETADO Y SUGERENCIAS PREDICTIVAS INTELIGENTES */
        .predictive-wrapper {
            position: relative;
            width: 100%;
        }
        .predictive-box {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #FFFFFF;
            border: 1.5px solid #CBD5E1;
            border-top: none;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.14);
            max-height: 220px;
            overflow-y: auto;
            z-index: 2000;
            display: none;
        }
        .predictive-item {
            padding: 9px 12px;
            cursor: pointer;
            border-bottom: 1px solid #F1F5F9;
            display: flex;
            flex-direction: column;
            gap: 2px;
            transition: background 0.15s ease;
            text-align: left;
        }
        .predictive-item:last-child {
            border-bottom: none;
        }
        .predictive-item:hover, .predictive-item.active {
            background: #EFF6FF;
        }
        .predictive-title {
            font-size: 13.5px;
            font-weight: 800;
            color: #0F172A;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .predictive-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            background: #E2E8F0;
            color: #334155;
            font-weight: 700;
        }
        .predictive-subtitle {
            font-size: 11.5px;
            color: #64748B;
        }

        /* DETALLES DE AF Y CHIPS */
        .af-box {
            background: #EFF6FF;
            border: 1.5px solid #BFDBFE;
            border-radius: 10px;
            padding: 10px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
        }
        .af-label { font-size: 11px; font-weight: 700; color: var(--primary); }
        .af-code { font-family: monospace; font-size: 15px; font-weight: 900; color: var(--primary-dark); }
        .chips-container { display: flex; flex-wrap: wrap; gap: 6px; }
        .chip-btn {
            padding: 7px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: #F1F5F9;
            color: #475569;
            border: 1px solid var(--border);
            cursor: pointer;
        }
        .chip-btn.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        /* SELECTOR DUAL DE FOTOGRAFÍA (CÁMARA VS ALMACENAMIENTO) */
        .foto-dual-box {
            border: 1.5px dashed var(--border);
            border-radius: 12px;
            padding: 14px;
            background: #F8FAFC;
            margin-bottom: 14px;
        }
        .foto-options-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .btn-foto-opt {
            background: #FFFFFF;
            border: 1.5px solid var(--border);
            border-radius: 10px;
            padding: 12px 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .btn-foto-opt:hover {
            border-color: var(--accent);
            background: #EFF6FF;
        }
        .btn-foto-opt .foto-ico { font-size: 24px; }
        .btn-foto-opt strong { font-size: 12px; color: var(--primary-dark); }
        .btn-foto-opt small { font-size: 10px; color: var(--text-muted); }

        .foto-preview-box {
            position: relative;
            margin-top: 12px;
            display: none;
            text-align: center;
        }
        .foto-preview-img {
            max-height: 160px;
            border-radius: 8px;
            border: 1px solid var(--border);
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }
        .btn-del-foto {
            position: absolute;
            top: -8px; right: 20px;
            background: var(--danger);
            color: white;
            border: none;
            width: 28px; height: 28px;
            border-radius: 14px;
            font-weight: 900;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(220,38,38,0.4);
        }

        /* TARJETAS KPI PARA ANÁLISIS */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 16px;
        }
        @media (min-width: 768px) {
            .kpi-grid { grid-template-columns: repeat(4, 1fr); gap: 14px; }
        }
        .kpi-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 14px;
            border: 1px solid var(--border);
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }
        .kpi-value {
            font-size: 26px;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 4px;
        }
        .kpi-label { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }

        /* MATRIZ DE PERMISOS DE USUARIOS */
        .matriz-permisos-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
            font-size: 12px;
        }
        .matriz-permisos-table th {
            background: #F1F5F9;
            padding: 8px 6px;
            text-align: center;
            font-weight: 700;
            color: #475569;
            border-bottom: 2px solid var(--border);
        }
        .matriz-permisos-table td {
            padding: 8px 6px;
            border-bottom: 1px solid #E2E8F0;
            text-align: center;
        }
        .matriz-permisos-table td:first-child {
            text-align: left;
            font-weight: 600;
        }
        .matriz-permisos-table input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: var(--primary);
            cursor: pointer;
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
            grid-column: 1 / -1;
        }
        .empty-state span { font-size: 38px; display: block; margin-bottom: 8px; }

        /* ===================================================================== */
        /* RESPONSIVE DESIGN INTELIGENTE PARA CELULARES Y DISPOSITIVOS MÓVILES   */
        /* (PANTALLAS <= 767px: SMARTPHONES VERTICALES Y HORIZONTALES)          */
        /* ===================================================================== */
        @media (max-width: 767px) {
            body {
                padding-bottom: 85px;
            }

            /* 1. Barra Superior Adaptativa */
            .top-navbar {
                padding: 10px 12px;
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
            }
            .top-navbar-main {
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 100%;
                gap: 6px;
            }
            .brand-title {
                font-size: 15.5px;
            }
            .badge-suite-movil {
                font-size: 9.5px;
                padding: 2px 5px;
            }
            .brand-sub {
                font-size: 10.5px;
                max-width: 150px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .user-profile-actions, .user-actions {
                display: flex;
                align-items: center;
                gap: 6px;
                flex-shrink: 0;
            }
            .user-badge {
                font-size: 11px;
                padding: 4px 8px;
                max-width: 105px;
                border-radius: 16px;
            }
            .btn-nav-action {
                padding: 5px 9px;
                font-size: 11.5px;
                border-radius: 6px;
            }
            .top-navbar-links {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 6px;
                width: 100%;
            }
            .btn-nav-quick {
                height: 34px;
                font-size: 11.5px;
                padding: 0 6px;
                border-radius: 6px;
            }

            /* 2. Selector Territorial Permanente (Red y Centro) */
            .selector-sede-bar {
                padding: 8px 12px;
                gap: 6px;
            }
            .sede-grid {
                grid-template-columns: 1fr !important;
                gap: 8px;
            }
            .sede-sel-group label {
                font-size: 11px;
                margin-bottom: 2px;
            }
            .sede-select {
                height: 42px;
                font-size: 13.5px;
                padding: 6px 10px;
                border-radius: 8px;
            }

            /* 3. Navegación por Pestañas Táctil */
            .tab-bar-nav {
                padding: 5px 8px;
                gap: 4px;
            }
            .tab-btn {
                min-width: auto;
                padding: 6px 11px;
                font-size: 12px;
                gap: 4px;
                border-radius: 6px;
            }

            /* 4. Contenedor y Herramientas (Búsqueda + Botón Nuevo) */
            .container {
                padding: 8px 10px;
                max-width: 100%;
            }
            .tab-tools-bar {
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
                margin-bottom: 10px;
            }
            .search-input {
                width: 100%;
                height: 44px;
                font-size: 14.5px;
                border-radius: 8px;
            }
            .btn-add-action {
                width: 100%;
                height: 44px;
                justify-content: center;
                font-size: 14px;
                border-radius: 8px;
            }

            /* 5. Filtros Rápidos de Activos (Píldoras) */
            .asset-filters-bar {
                gap: 6px;
                margin: 6px 0 10px 0;
                padding-bottom: 6px;
                flex-wrap: nowrap;
            }
            .btn-filter-pill {
                flex-shrink: 0;
                padding: 6px 11px;
                font-size: 11.5px;
                border-radius: 20px;
            }
            .pill-count {
                padding: 1px 5px;
                font-size: 10px;
            }

            /* 6. Tarjetas de Activos y Acciones Táctiles */
            .cards-grid, .cards-grid-3 {
                grid-template-columns: 1fr !important;
                gap: 10px;
            }
            .card-item {
                padding: 12px 12px;
                margin-bottom: 8px;
                border-radius: 12px;
            }
            .card-item-header {
                flex-wrap: wrap;
                gap: 4px;
            }
            .item-title {
                font-size: 14px;
            }
            .item-subtitle {
                font-size: 11.5px;
                gap: 4px;
            }
            .item-detail-row {
                font-size: 11.5px;
                padding: 6px 8px;
            }
            .item-actions {
                display: flex;
                width: 100%;
                gap: 5px;
                justify-content: stretch;
                margin-top: 8px;
            }
            .btn-card-view, .btn-card-edit, .btn-card-del {
                flex: 1;
                justify-content: center;
                text-align: center;
                height: 38px;
                padding: 0 4px;
                font-size: 11.5px;
                border-radius: 7px;
            }

            /* 7. Modales Móviles (Bottom Sheet Táctil) */
            .modal-overlay {
                padding: 0;
                align-items: flex-end;
            }
            .modal-content-sheet {
                border-radius: 20px 20px 0 0;
                max-height: 92vh;
                width: 100%;
                max-width: 100%;
                padding: 16px 14px 34px 14px;
            }
            .modal-header-bar h2 {
                font-size: 15.5px;
            }
            .row-2, .row-3 {
                grid-template-columns: 1fr !important;
                gap: 8px !important;
            }
            .form-group {
                margin-bottom: 10px;
            }
            .form-label {
                font-size: 11.5px;
                margin-bottom: 4px;
            }
            .form-control, select.form-control {
                font-size: 16px !important; /* Previene auto-zoom molesto en iPhone Safari */
                height: 46px;
                border-radius: 8px;
            }
            textarea.form-control {
                font-size: 16px !important;
                min-height: 85px !important;
            }
            .btn-modal-submit {
                height: 48px;
                font-size: 15px;
                border-radius: 10px;
            }
            .af-box {
                padding: 8px 12px;
                flex-wrap: wrap;
                gap: 6px;
            }
            .af-label {
                font-size: 10.5px;
            }
            .af-code {
                font-size: 14px;
            }
        }

        /* 8. Ajustes para Celulares Pequeños (<= 380px) */
        @media (max-width: 380px) {
            .brand-title {
                font-size: 14px;
            }
            .user-badge {
                max-width: 80px;
                font-size: 10px;
                padding: 3px 6px;
            }
            .btn-nav-action {
                padding: 4px 7px;
                font-size: 11px;
            }
            .tab-btn {
                padding: 5px 9px;
                font-size: 11px;
            }
            .btn-filter-pill {
                padding: 5px 9px;
                font-size: 11px;
            }
            .btn-card-view, .btn-card-edit, .btn-card-del {
                font-size: 10.5px;
                height: 36px;
            }
        }
    </style>
</head>
<body>

    {% set rol_clean = (usuario.get('rol', '') or 'tecnico') | lower %}
    {% set es_admin = (rol_clean in ['administrador', 'admin', 'jefe']) or (usuario.get('nombre_usuario') == 'godhead') %}
    {% set perms = usuario.get('permisos') or {} %}

    <!-- BARRA SUPERIOR RESPONSIVA -->
    <header class="top-navbar">
        <div class="top-navbar-main">
            <div class="brand-info">
                <div class="brand-title-wrap">
                    <span class="brand-title">SGEM GAMLP</span>
                    <span class="badge-suite-movil">MÓVIL</span>
                </div>
                <span class="brand-sub">{% if es_admin %}Panel de Administración y Control{% else %}Gestión en Centros de Salud{% endif %}</span>
            </div>
            <div class="user-profile-actions">
                <span class="user-badge" title="{{ usuario.get('nombre_completo', '') }}">
                    👤 {{ usuario.get('nombre_completo', usuario.get('nombre_usuario', 'Técnico')) }}
                </span>
                <a href="/movil/logout" class="btn-nav-action" title="Cerrar sesión">Salir 🚪</a>
            </div>
        </div>
        <div class="top-navbar-links">
            <a href="/" class="btn-nav-quick btn-quick-portal" title="Ir al Portal Web Principal">🌐 Portal Web</a>
            <a href="/analisis" class="btn-nav-quick btn-quick-analisis" title="Ir a Análisis y Censo Territorial Oficial">📊 Análisis y Censo</a>
        </div>
    </header>

    <!-- SELECTOR DE SEDE ACTIVA (RED Y CENTRO) -->
    <div class="selector-sede-bar">
        <div class="sede-grid">
            <div class="sede-sel-group">
                <label for="top_red">🌐 Red de Salud:</label>
                <select id="top_red" class="sede-select" onchange="alCambiarRedGlobal()">
                    <option value="">-- Todas las Redes (GAMLP) --</option>
                    {% for r in sedes.get('redes', []) %}
                    <option value="{{ r['nombre'] }}" data-id="{{ r['id'] }}">{{ r['nombre'] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="sede-sel-group">
                <label for="top_centro">🏥 Centro de Salud:</label>
                <select id="top_centro" class="sede-select" onchange="alCambiarCentroGlobal()">
                    <option value="">-- Todos los Centros --</option>
                </select>
            </div>
        </div>
    </div>

    <!-- PESTAÑAS DE NAVEGACIÓN -->
    <nav class="tab-bar-nav" id="main_tab_nav">
        {% if es_admin or perms.get('Inventario', {}).get('ver', True) %}
        <button class="tab-btn active" data-tab="inventario" onclick="cambiarPestana('inventario')">📦 Inventario</button>
        {% endif %}

        {% if es_admin or perms.get('Catalogo', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="catalogo" onclick="cambiarPestana('catalogo')">🩺 Catálogo</button>
        {% endif %}

        {% if es_admin or perms.get('Muebleria', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="muebles" onclick="cambiarPestana('muebles')">🛋️ Muebles</button>
        {% endif %}

        {% if es_admin or perms.get('Areas', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="areas" onclick="cambiarPestana('areas')">📍 Áreas</button>
        {% endif %}

        {% if es_admin or perms.get('Repuestos', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="repuestos" onclick="cambiarPestana('repuestos')">🔧 Repuestos</button>
        {% endif %}

        {% if es_admin or perms.get('Historial', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="historial" onclick="cambiarPestana('historial')">📋 Historial</button>
        {% endif %}

        {% if es_admin or perms.get('Analisis', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="analisis" onclick="cambiarPestana('analisis')">📊 Análisis</button>
        {% endif %}

        {% if es_admin or perms.get('Cronograma', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="cronograma" onclick="cambiarPestana('cronograma')">📅 Cronograma</button>
        {% endif %}

        {% if es_admin or perms.get('Sedes', {}).get('ver', False) %}
        <button class="tab-btn" data-tab="sedes" onclick="cambiarPestana('sedes')">🏥 Sedes</button>
        {% endif %}

        {% if es_admin %}
        <button class="tab-btn" data-tab="usuarios" onclick="cambiarPestana('usuarios')">👥 Usuarios</button>
        <button class="tab-btn" data-tab="papelera" onclick="cambiarPestana('papelera')">🗑️ Papelera (<span id="cnt_papelera_badge">0</span>)</button>
        {% endif %}

        <button class="tab-btn" data-tab="links" onclick="cambiarPestana('links')">🔗 Enlaces</button>
    </nav>

    <!-- CONTENEDOR PRINCIPAL -->
    <main class="container">

        <!-- 1. PESTAÑA: INVENTARIO -->
        {% if es_admin or perms.get('Inventario', {}).get('ver', True) %}
        <section id="pane_inventario" class="tab-pane active">
            <div class="tab-tools-bar">
                <input type="text" id="busq_inventario" class="search-input" placeholder="Buscar equipo o mueble por AF, nombre, marca, serie, área..." oninput="filtrarListaInventario()">
                {% if es_admin or perms.get('Inventario', {}).get('agregar', True) %}
                <button class="btn-add-action" onclick="abrirModalRegistroEquipo()">✚ Registrar Equipo</button>
                {% endif %}
            </div>
            <!-- FILTRO UNIFICADO DE ACTIVOS -->
            <div class="asset-filters-bar">
                <button type="button" class="btn-filter-pill active" id="pill_inv_todo" onclick="setFiltroTipoActivo('todo')">
                    🌐 Ver Todo <span id="cnt_inv_todo" class="pill-count">0</span>
                </button>
                <button type="button" class="btn-filter-pill" id="pill_inv_equipos" onclick="setFiltroTipoActivo('equipos')">
                    🩺 Solo Equipos Médicos <span id="cnt_inv_equipos" class="pill-count">0</span>
                </button>
                <button type="button" class="btn-filter-pill" id="pill_inv_muebles" onclick="setFiltroTipoActivo('muebles')">
                    🛋️ Solo Muebles y TI <span id="cnt_inv_muebles" class="pill-count">0</span>
                </button>
            </div>
            <div id="lista_inventario" class="cards-grid">
                <div class="empty-state"><span>⏳</span>Cargando activos del centro...</div>
            </div>
        </section>
        {% endif %}

        <!-- 2. PESTAÑA: CATÁLOGO -->
        {% if es_admin or perms.get('Catalogo', {}).get('ver', False) %}
        <section id="pane_catalogo" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_catalogo" class="search-input" placeholder="Buscar modelo en catálogo..." oninput="filtrarListaCatalogo()">
                {% if es_admin or perms.get('Catalogo', {}).get('agregar', False) %}
                <button class="btn-add-action" onclick="abrirModalCatalogo()">✚ Añadir Modelo</button>
                {% endif %}
            </div>
            <div id="lista_catalogo" class="cards-grid">
                <div class="empty-state"><span>⏳</span>Cargando catálogo central...</div>
            </div>
        </section>
        {% endif %}

        <!-- 3. PESTAÑA: MUEBLES -->
        {% if es_admin or perms.get('Muebleria', {}).get('ver', False) %}
        <section id="pane_muebles" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_muebles" class="search-input" placeholder="Buscar mueble, PC, serie, SISPAM..." oninput="filtrarListaMuebles()">
                {% if es_admin or perms.get('Muebleria', {}).get('agregar', False) %}
                <button class="btn-add-action" onclick="abrirModalMueble()">✚ Registrar Mueble</button>
                {% endif %}
            </div>
            <div id="lista_muebles" class="cards-grid">
                <div class="empty-state"><span>⏳</span>Cargando activos de mueblería y TI...</div>
            </div>
        </section>
        {% endif %}

        <!-- 4. PESTAÑA: ÁREAS -->
        {% if es_admin or perms.get('Areas', {}).get('ver', False) %}
        <section id="pane_areas" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_areas" class="search-input" placeholder="Buscar área, encargado, cargo..." oninput="filtrarListaAreas()">
                {% if es_admin or perms.get('Areas', {}).get('agregar', False) %}
                <button class="btn-add-action" onclick="abrirModalArea()">✚ Nueva Área</button>
                {% endif %}
            </div>
            <div id="lista_areas" class="cards-grid">
                <div class="empty-state"><span>⏳</span>Cargando áreas del centro...</div>
            </div>
        </section>
        {% endif %}

        <!-- 5. PESTAÑA: REPUESTOS -->
        {% if es_admin or perms.get('Repuestos', {}).get('ver', False) %}
        <section id="pane_repuestos" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_repuestos" class="search-input" placeholder="Buscar repuesto, P/N, modelo..." oninput="filtrarListaRepuestos()">
                {% if es_admin or perms.get('Repuestos', {}).get('agregar', False) %}
                <button class="btn-add-action" onclick="abrirModalRepuesto()">✚ Añadir Repuesto</button>
                {% endif %}
            </div>
            <div id="lista_repuestos" class="cards-grid">
                <div class="empty-state"><span>⏳</span>Cargando repuestos del centro...</div>
            </div>
        </section>
        {% endif %}

        <!-- 6. PESTAÑA: HISTORIAL DE INTERVENCIONES -->
        {% if es_admin or perms.get('Historial', {}).get('ver', False) %}
        <section id="pane_historial" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_historial" class="search-input" placeholder="Buscar por equipo, técnico o trabajo..." oninput="filtrarListaHistorial()">
                {% if es_admin or perms.get('Historial', {}).get('agregar', False) %}
                <button class="btn-add-action" onclick="abrirModalIntervencion()">✚ Intervención</button>
                {% endif %}
            </div>
            <div id="lista_historial" class="cards-grid">
                <div class="empty-state"><span>⏳</span>Cargando intervenciones del centro...</div>
            </div>
        </section>
        {% endif %}

        <!-- 7. PESTAÑA: ANÁLISIS ESTADÍSTICO -->
        {% if es_admin or perms.get('Analisis', {}).get('ver', False) %}
        <section id="pane_analisis" class="tab-pane">
            <div style="background: linear-gradient(135deg, #003B64 0%, #0284C7 100%); color: white; padding: 14px 16px; border-radius: var(--radius-sm); margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div>
                    <div style="font-size: 15px; font-weight: 800;">📊 Tablero Oficial de Análisis y Censo Territorial</div>
                    <div style="font-size: 12px; opacity: 0.92;">Navegación territorial completa por Red, Centro, Áreas y gráficos de censo en vivo.</div>
                </div>
                <a href="/analisis" target="_blank" style="background: white; color: #003B64; font-weight: 800; font-size: 12.5px; padding: 8px 16px; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                    🚀 Abrir Tablero Completo ➔
                </a>
            </div>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div id="kpi_total_eq" class="kpi-value" style="color: var(--primary);">0</div>
                    <div class="kpi-label">Equipos Médicos</div>
                </div>
                <div class="kpi-card">
                    <div id="kpi_operativos" class="kpi-value" style="color: var(--success);">0</div>
                    <div class="kpi-label">Operativos</div>
                </div>
                <div class="kpi-card">
                    <div id="kpi_mantenimiento" class="kpi-value" style="color: var(--warning);">0</div>
                    <div class="kpi-label">En Mantenimiento</div>
                </div>
                <div class="kpi-card">
                    <div id="kpi_baja" class="kpi-value" style="color: var(--danger);">0</div>
                    <div class="kpi-label">Fuera de Servicio</div>
                </div>
            </div>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div id="kpi_crit_alta" class="kpi-value" style="color: #DC2626;">0</div>
                    <div class="kpi-label">Criticidad Alta</div>
                </div>
                <div class="kpi-card">
                    <div id="kpi_tot_muebles" class="kpi-value" style="color: #6366F1;">0</div>
                    <div class="kpi-label">Mueblería y TI</div>
                </div>
                <div class="kpi-card">
                    <div id="kpi_tot_repuestos" class="kpi-value" style="color: #0D9488;">0</div>
                    <div class="kpi-label">Repuestos Stock</div>
                </div>
                <div class="kpi-card">
                    <div id="kpi_tot_intervenciones" class="kpi-value" style="color: #7C3AED;">0</div>
                    <div class="kpi-label">Intervenciones</div>
                </div>
            </div>

            <div class="card-item" style="margin-top: 10px;">
                <h3 style="font-size: 14px; font-weight: 800; margin-bottom: 10px; color: var(--primary-dark);">📍 Distribución de Equipos por Áreas</h3>
                <div id="distribucion_areas_box">
                    <div class="empty-state" style="padding: 20px;"><span>📊</span>Calculando distribución...</div>
                </div>
            </div>
        </section>
        {% endif %}

        <!-- 8. PESTAÑA: CRONOGRAMA -->
        {% if es_admin or perms.get('Cronograma', {}).get('ver', False) %}
        <section id="pane_cronograma" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_cronograma" class="search-input" placeholder="Buscar en cronograma..." oninput="filtrarListaCronograma()">
            </div>
            <div id="lista_cronograma" class="cards-grid">
                <div class="empty-state"><span>📅</span>Cargando programación técnica...</div>
            </div>
        </section>
        {% endif %}

        <!-- 9. PESTAÑA: SEDES Y CENTROS -->
        {% if es_admin or perms.get('Sedes', {}).get('ver', False) %}
        <section id="pane_sedes" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_sedes" class="search-input" placeholder="Buscar red o centro..." oninput="filtrarListaSedes()">
            </div>
            <div id="lista_sedes" class="cards-grid">
                <div class="empty-state"><span>🏥</span>Cargando directorio de sedes...</div>
            </div>
        </section>
        {% endif %}

        <!-- 10. PESTAÑA: GESTIÓN DE USUARIOS Y PERMISOS (SOLO ADMINISTRADOR) -->
        {% if es_admin %}
        <section id="pane_usuarios" class="tab-pane">
            <div class="tab-tools-bar">
                <input type="text" id="busq_usuarios" class="search-input" placeholder="Buscar usuario por nombre o C.I...." oninput="filtrarListaUsuarios()">
                <button class="btn-add-action" onclick="abrirModalCrearUsuario()">✚ Nuevo Usuario</button>
            </div>
            <div id="lista_usuarios" class="cards-grid">
                <div class="empty-state"><span>👥</span>Cargando usuarios y permisos...</div>
            </div>
        </section>
        {% endif %}

        <!-- 10.B PESTAÑA: PAPELERA DE SEGURIDAD Y RECUPERACIÓN (SOLO ADMINISTRADOR Y GODHEAD) -->
        {% if es_admin %}
        <section id="pane_papelera" class="tab-pane">
            <div style="background: linear-gradient(135deg, #1E293B, #334155); color: #ffffff; padding: 18px 20px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(30,41,59,0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="font-size: 19px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                            <span>🛡️</span> Papelera de Seguridad del Sistema
                            <span class="badge" style="background: #F59E0B; color: #78350F; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 800;">ADMIN & GODHEAD</span>
                        </div>
                        <div style="font-size: 13px; opacity: 0.92; margin-top: 4px;">
                            Elementos borrados de inventario, mueblería, áreas, catálogo y repuestos. Puedes restaurarlos a su estado operativo con un solo clic.
                        </div>
                    </div>
                    <button type="button" class="btn-table-action" onclick="cargarPapeleraGlobal()" style="background: rgba(255,255,255,0.15); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.3); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                        <span>🔄</span> Actualizar Papelera
                    </button>
                </div>
            </div>

            <!-- FILTROS POR MÓDULO -->
            <div class="asset-filters-bar">
                <button type="button" class="btn-filter-pill active" id="pill_pap_todo" onclick="setFiltroPapelera('todos')">
                    🌐 Ver Todos <span id="cnt_pap_todo" class="pill-count">0</span>
                </button>
                <button type="button" class="btn-filter-pill" id="pill_pap_equipos" onclick="setFiltroPapelera('equipos')">
                    🩺 Equipos Médicos <span id="cnt_pap_equipos" class="pill-count">0</span>
                </button>
                <button type="button" class="btn-filter-pill" id="pill_pap_muebles" onclick="setFiltroPapelera('muebleria')">
                    🛋️ Mueblería y TI <span id="cnt_pap_muebles" class="pill-count">0</span>
                </button>
                <button type="button" class="btn-filter-pill" id="pill_pap_areas" onclick="setFiltroPapelera('areas')">
                    📍 Áreas <span id="cnt_pap_areas" class="pill-count">0</span>
                </button>
                <button type="button" class="btn-filter-pill" id="pill_pap_catalogo" onclick="setFiltroPapelera('catalogo')">
                    📋 Catálogo <span id="cnt_pap_catalogo" class="pill-count">0</span>
                </button>
                <button type="button" class="btn-filter-pill" id="pill_pap_repuestos" onclick="setFiltroPapelera('repuestos')">
                    🔧 Repuestos <span id="cnt_pap_repuestos" class="pill-count">0</span>
                </button>
            </div>

            <div class="tab-tools-bar">
                <input type="text" id="busq_papelera" class="search-input" placeholder="Buscar elemento borrado por título, código AF, serie, usuario o sede..." oninput="filtrarListaPapelera()">
            </div>

            <div id="lista_papelera" class="cards-grid">
                <div class="empty-state"><span>🗑️</span>Cargando elementos borrados...</div>
            </div>
        </section>
        {% endif %}

        <!-- 11. PESTAÑA: DIRECTORIO DE ENLACES Y ACCESOS DEL SISTEMA -->
        <section id="pane_links" class="tab-pane">
            <div style="background: linear-gradient(135deg, #003B64, #005691); color: #ffffff; padding: 18px 20px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,59,100,0.15);">
                <div style="font-size: 19px; font-weight: 800; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                    <span>🔗</span> Directorio de Enlaces y Accesos
                </div>
                <div style="font-size: 13px; opacity: 0.92; line-height: 1.4;">
                    Accesos oficiales del sistema en la nube 24/7, red interna, bases de datos y herramientas de soporte. Copia con un clic o comparte directamente por WhatsApp.
                </div>
            </div>

            <!-- ENLACE 1: SUITE MÓVIL EN LA NUBE (OFICIAL 24/7) -->
            <div class="card-item" style="border-left: 5px solid #16A34A; background: #FFFFFF; padding: 16px; margin-bottom: 14px;">
                <div class="card-item-header" style="margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 26px;">📱</span>
                        <div>
                            <div class="item-title" style="color: #003B64; font-size: 15px; font-weight: 800;">Suite Móvil para Celulares (Nube 24/7)</div>
                            <span class="badge" style="background: #DCFCE7; color: #166534; font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">🟢 ACTIVO ONLINE OFICIAL</span>
                        </div>
                    </div>
                </div>
                <div style="font-size: 12.5px; color: var(--text-muted); line-height: 1.4;">
                    Para técnicos y personal de campo desde cualquier celular o tablet con internet (no requiere computadoras encendidas).
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin: 10px 0; font-family: monospace; font-size: 13px; font-weight: 700; color: #0284C7; word-break: break-all;">
                    https://cmms-gamlp.onrender.com/movil
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
                    <button type="button" class="btn-sm" style="flex: 1; min-width: 125px; background: #2563EB; color: white; padding: 9px 12px; border: none; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;" onclick="copiarTexto('https://cmms-gamlp.onrender.com/movil', this)">
                        📋 Copiar Enlace
                    </button>
                    <a href="https://api.whatsapp.com/send?text=Acceso%20Suite%20M%C3%B3vil%20SGEM%20GAMLP%3A%20https%3A%2F%2Fcmms-gamlp.onrender.com%2Fmovil" target="_blank" class="btn-sm" style="flex: 1; min-width: 145px; background: #22C55E; color: white; padding: 9px 12px; border: none; border-radius: 6px; font-weight: 700; font-size: 12px; text-decoration: none; text-align: center; display: inline-flex; align-items: center; justify-content: center; gap: 4px;">
                        📲 Enviar por WhatsApp
                    </a>
                    <a href="https://cmms-gamlp.onrender.com/movil" target="_blank" class="btn-sm" style="background: #F1F5F9; color: #003B64; padding: 9px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 700; font-size: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🚀 Abrir
                    </a>
                </div>
            </div>

            <!-- ENLACE 2: CONSULTA HISTÓRICA (GESTIONES ANTERIORES - SOLO LECTURA) -->
            <div class="card-item" style="border-left: 5px solid #D97706; background: #FFFFFF; padding: 16px; margin-bottom: 14px;">
                <div class="card-item-header" style="margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 26px;">🏛️</span>
                        <div>
                            <div class="item-title" style="color: #92400E; font-size: 15px; font-weight: 800;">Consulta Histórica GAMLP (Solo Lectura)</div>
                            <span class="badge" style="background: #FEF3C7; color: #92400E; font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">🏛️ 2.938 EQUIPOS • SOLO LECTURA</span>
                        </div>
                    </div>
                </div>
                <div style="font-size: 12.5px; color: var(--text-muted); line-height: 1.4;">
                    Consulta y búsqueda de antecedentes de los 2.938 equipos y muebles de gestiones pasadas en modo Solo Lectura (sin modificación ni eliminación).
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin: 10px 0; font-family: monospace; font-size: 13px; font-weight: 700; color: #D97706; word-break: break-all;">
                    https://cmms-gamlp.onrender.com/historico
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
                    <button type="button" class="btn-sm" style="flex: 1; min-width: 125px; background: #D97706; color: white; padding: 9px 12px; border: none; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;" onclick="copiarTexto('https://cmms-gamlp.onrender.com/historico', this)">
                        📋 Copiar Enlace
                    </button>
                    <a href="https://api.whatsapp.com/send?text=Consulta%20Hist%C3%B3rica%20SGEM%20GAMLP%3A%20https%3A%2F%2Fcmms-gamlp.onrender.com%2Fhistorico" target="_blank" class="btn-sm" style="flex: 1; min-width: 145px; background: #22C55E; color: white; padding: 9px 12px; border: none; border-radius: 6px; font-weight: 700; font-size: 12px; text-decoration: none; text-align: center; display: inline-flex; align-items: center; justify-content: center; gap: 4px;">
                        📲 Enviar por WhatsApp
                    </a>
                    <a href="https://cmms-gamlp.onrender.com/historico" target="_blank" class="btn-sm" style="background: #FEF3C7; color: #92400E; padding: 9px 14px; border: 1px solid #FDE68A; border-radius: 6px; font-weight: 700; font-size: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🚀 Abrir Histórico
                    </a>
                </div>
            </div>

            <!-- ENLACE 3: PORTAL WEB GENERAL (NUBE 24/7) -->
            <div class="card-item" style="border-left: 5px solid #005691; background: #FFFFFF; padding: 16px; margin-bottom: 14px;">
                <div class="card-item-header" style="margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 26px;">🌐</span>
                        <div>
                            <div class="item-title" style="color: #003B64; font-size: 15px; font-weight: 800;">Portal Web General GAMLP (Nube 24/7)</div>
                            <span class="badge" style="background: #E0F2FE; color: #075985; font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">🌐 PÁGINA PRINCIPAL</span>
                        </div>
                    </div>
                </div>
                <div style="font-size: 12.5px; color: var(--text-muted); line-height: 1.4;">
                    Portal de bienvenida, documentación general y accesos administrativos del sistema institucional.
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin: 10px 0; font-family: monospace; font-size: 13px; font-weight: 700; color: #0284C7; word-break: break-all;">
                    https://cmms-gamlp.onrender.com/
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
                    <button type="button" class="btn-sm" style="flex: 1; min-width: 125px; background: #2563EB; color: white; padding: 9px 12px; border: none; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;" onclick="copiarTexto('https://cmms-gamlp.onrender.com/', this)">
                        📋 Copiar Enlace
                    </button>
                    <a href="https://cmms-gamlp.onrender.com/" target="_blank" class="btn-sm" style="background: #F1F5F9; color: #003B64; padding: 9px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 700; font-size: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🚀 Abrir Portal
                    </a>
                </div>
            </div>

            <!-- ENLACE 3: RED LOCAL WI-FI -->
            <div class="card-item" style="border-left: 5px solid #F59E0B; background: #FFFFFF; padding: 16px; margin-bottom: 14px;">
                <div class="card-item-header" style="margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 26px;">📶</span>
                        <div>
                            <div class="item-title" style="color: #003B64; font-size: 15px; font-weight: 800;">Conexión Red Local Wi-Fi (Servidor Oficina)</div>
                            <span class="badge" style="background: #FEF3C7; color: #92400E; font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">🏢 RED LOCAL INTERNA</span>
                        </div>
                    </div>
                </div>
                <div style="font-size: 12.5px; color: var(--text-muted); line-height: 1.4;">
                    Para acceder cuando estés conectado a la misma red Wi-Fi de la oficina donde la PC principal tiene el software de escritorio encendido.
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin: 10px 0; font-family: monospace; font-size: 13px; font-weight: 700; color: #D97706; word-break: break-all;" id="lbl_enlace_local">
                    http://&lt;IP_DE_TU_PC&gt;:5000/movil
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
                    <button type="button" class="btn-sm" style="flex: 1; min-width: 125px; background: #D97706; color: white; padding: 9px 12px; border: none; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;" onclick="copiarTexto(document.getElementById('lbl_enlace_local').innerText.trim(), this)">
                        📋 Copiar Formato
                    </button>
                    <button type="button" class="btn-sm" style="background: #F1F5F9; color: #003B64; padding: 9px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;" onclick="detectarIpHostLocal()">
                        🔍 Ver Dirección Actual
                    </button>
                </div>
            </div>

        </section>
    </main>

    <!-- ========================================================================= -->
    <!-- MODALES DE REGISTRO / EDICIÓN -->
    <!-- ========================================================================= -->

    <!-- MODAL 1: REGISTRO / MODIFICACIÓN DE EQUIPO MÉDICO -->
    <div id="modal_equipo" class="modal-overlay">
        <div class="modal-content-sheet">
            <div class="modal-header-bar">
                <h2 id="modal_eq_title">✚ Registrar Equipo Médico</h2>
                <button class="btn-close-modal" onclick="cerrarModal('modal_equipo')">✕</button>
            </div>

            <form id="form_equipo_movil" onsubmit="guardarEquipoMovil(event)">
                <input type="hidden" id="modal_eq_es_edicion" value="0">
                <div class="af-box">
                    <span class="af-label">🔒 CÓDIGO ACTIVO FIJO (AF):</span>
                    <span id="display_af_modal" class="af-code">CALCULANDO...</span>
                    <input type="hidden" id="modal_eq_id_af">
                </div>

                <!-- SECCIÓN 1: IDENTIFICACIÓN Y UBICACIÓN -->
                <div class="form-section-banner">📍 1. Identificación y Ubicación</div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_red">Dirección Administrativa (Red de Salud) (*):</label>
                        <select id="modal_eq_red" class="form-control" onchange="alCambiarRedModalEquipo()" style="font-weight:700; color:#003B64;" required>
                            <option value="">-- Seleccionar Red de Salud --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_centro">Unidad Organizacional (Centro de Salud) (*):</label>
                        <select id="modal_eq_centro" class="form-control" onchange="alCambiarCentroModalEquipo()" style="font-weight:700; color:#003B64;" required>
                            <option value="">-- Seleccionar Centro de Salud --</option>
                        </select>
                    </div>
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_sector">Sector Actual:</label>
                        <select id="modal_eq_sector" class="form-control">
                            <option value="SALUD" selected>SALUD</option>
                            <option value="G.A.M.L.P.">G.A.M.L.P.</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_servicio">Servicio:</label>
                        <input type="text" id="modal_eq_servicio" class="form-control" placeholder="Ej: Consulta Externa, Emergencias">
                    </div>
                </div>

                <!-- MODELO DE CATÁLOGO CON BÚSQUEDA PREDICTIVA -->
                <div class="form-group predictive-wrapper">
                    <label class="form-label" for="modal_eq_catalogo_input">Modelo de Catálogo (Búsqueda Predictiva Inteligente):</label>
                    <input type="text" id="modal_eq_catalogo_input" class="form-control" placeholder="🔍 Escribe para buscar modelo (ej. Des, Monitor, Bomba, Electro...)" autocomplete="off" oninput="buscarSugerenciasCatalogo(this.value)" onfocus="buscarSugerenciasCatalogo(this.value)" onblur="cerrarSugerenciaRetraso(this)">
                    <div id="modal_eq_catalogo_predictive" class="predictive-box"></div>
                </div>

                <!-- NOMBRE DEL EQUIPO CON RECOMENDACIONES DE ESCRITURA -->
                <div class="form-group predictive-wrapper">
                    <label class="form-label" for="modal_eq_nombre">Nombre del Equipo (*):</label>
                    <input type="text" id="modal_eq_nombre" class="form-control" placeholder="Ej: Desfibrilador, Monitor Multiparámetro" autocomplete="off" required oninput="buscarSugerenciasNombreEquipo(this.value)" onfocus="buscarSugerenciasNombreEquipo(this.value)" onblur="cerrarSugerenciaRetraso(this)">
                    <div id="modal_eq_nombre_predictive" class="predictive-box"></div>
                </div>

                <div class="row-2">
                    <div class="form-group predictive-wrapper">
                        <label class="form-label" for="modal_eq_marca">Marca:</label>
                        <input type="text" id="modal_eq_marca" class="form-control" placeholder="Ej: Mindray, Bionet, GE" autocomplete="off" oninput="buscarSugerenciasMarca(this.value, 'modal_eq_marca_predictive', 'modal_eq_marca')" onfocus="buscarSugerenciasMarca(this.value, 'modal_eq_marca_predictive', 'modal_eq_marca')" onblur="cerrarSugerenciaRetraso(this)">
                        <div id="modal_eq_marca_predictive" class="predictive-box"></div>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_modelo">Modelo:</label>
                        <input type="text" id="modal_eq_modelo" class="form-control" placeholder="Ej: BeneHeart D6, uMEC 10">
                    </div>
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_area">Ubicación Física (Piso - Área) (*):</label>
                        <select id="modal_eq_area" class="form-control" onchange="alCambiarAreaModal()" required>
                            <option value="">Cargando áreas...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_piso">Piso:</label>
                        <input type="text" id="modal_eq_piso" class="form-control" placeholder="Piso (se llena solo)" readonly style="background:#F8FAFC;">
                    </div>
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_persona">Doctor(a) / Responsable Asignado:</label>
                        <input type="text" id="modal_eq_persona" class="form-control" placeholder="Nombre de la responsable...">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_ci">C.I.:</label>
                        <input type="text" id="modal_eq_ci" class="form-control" placeholder="Ej: 10954587">
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label" for="modal_eq_cargo">Cargo:</label>
                    <input type="text" id="modal_eq_cargo" class="form-control" placeholder="Ej: Médico General / Responsable">
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_serie">N° Serie (Por defecto S/C):</label>
                        <input type="text" id="modal_eq_serie" class="form-control" placeholder="S/C">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_estado">Estado:</label>
                        <select id="modal_eq_estado" class="form-control">
                            <option value="Operativo">Operativo</option>
                            <option value="Bueno" selected>Bueno</option>
                            <option value="Regular">Regular</option>
                            <option value="Malo">Malo</option>
                            <option value="Baja">Baja</option>
                        </select>
                    </div>
                </div>

                <div class="row-3">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_sispam">Cód. SISPAM:</label>
                        <input type="text" id="modal_eq_sispam" class="form-control" placeholder="S/C">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_bertin">Cód. BERTIN:</label>
                        <input type="text" id="modal_eq_bertin" class="form-control" placeholder="S/C">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_sapm">Cód. SAPM:</label>
                        <input type="text" id="modal_eq_sapm" class="form-control" placeholder="S/C">
                    </div>
                </div>

                <!-- SECCIÓN 2: ADQUISICIÓN Y COSTOS -->
                <div class="form-section-banner">💰 2. Adquisición y Costos</div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_procedencia">Procedencia:</label>
                        <input type="text" id="modal_eq_procedencia" class="form-control" placeholder="Ej: Alemania, EE.UU., China...">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_fabricante">Fabricante Original:</label>
                        <input type="text" id="modal_eq_fabricante" class="form-control" placeholder="Ej: Mindray Bio-Medical">
                    </div>
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_proveedor">Proveedor Local:</label>
                        <input type="text" id="modal_eq_proveedor" class="form-control" placeholder="Ej: Droguería INTI, Promed...">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_anio_fab">Año Fabricación:</label>
                        <input type="text" id="modal_eq_anio_fab" class="form-control" placeholder="Ej: 2022">
                    </div>
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_fecha_instalacion">Fecha Instalación / Adquisición:</label>
                        <input type="date" id="modal_eq_fecha_instalacion" class="form-control">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Modalidad de Adquisición:</label>
                        <div class="radio-pill-group">
                            <label class="pill-radio"><input type="radio" name="modalidad_adq" value="Compra" checked onchange="toggleModalidadAdq(this.value)"> Compra</label>
                            <label class="pill-radio"><input type="radio" name="modalidad_adq" value="Comodato" onchange="toggleModalidadAdq(this.value)"> Comodato</label>
                            <label class="pill-radio"><input type="radio" name="modalidad_adq" value="Donación" onchange="toggleModalidadAdq(this.value)"> Donación</label>
                        </div>
                    </div>
                </div>

                <div class="form-group" id="box_costo_equipo">
                    <label class="form-label" for="modal_eq_costo">Costo del Equipo (Bs.):</label>
                    <input type="number" step="0.01" id="modal_eq_costo" class="form-control" placeholder="0.00" value="0">
                </div>

                <!-- SECCIÓN 3: ESPECIFICACIONES Y GARANTÍA -->
                <div class="form-section-banner">⚡ 3. Especificaciones y Garantía</div>

                <div class="form-group">
                    <label class="form-label">Tecnología (Tipo de Energía):</label>
                    <div class="chips-container">
                        <span class="chip-btn active" data-f="t_elec" onclick="toggleChip(this)">⚡ Eléctrica</span>
                        <span class="chip-btn" data-f="t_elco" onclick="toggleChip(this)">🔌 Electrónica</span>
                        <span class="chip-btn" data-f="t_mec" onclick="toggleChip(this)">⚙️ Mecánica</span>
                        <span class="chip-btn" data-f="t_hid" onclick="toggleChip(this)">💧 Hidráulica</span>
                        <span class="chip-btn" data-f="t_neu" onclick="toggleChip(this)">💨 Neumática</span>
                        <span class="chip-btn" data-f="t_vap" onclick="toggleChip(this)">♨️ Vapor</span>
                    </div>
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label">Tipo de Movilidad:</label>
                        <div class="radio-pill-group">
                            <label class="pill-radio"><input type="radio" name="tipo_movilidad" value="Fijo" checked> Fijo</label>
                            <label class="pill-radio"><input type="radio" name="tipo_movilidad" value="Móvil"> Móvil</label>
                            <label class="pill-radio"><input type="radio" name="tipo_movilidad" value="Portátil"> Portátil</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Garantía:</label>
                        <div class="radio-pill-group">
                            <label class="pill-radio"><input type="radio" name="tiene_garantia" value="Sin Garantía" checked onchange="toggleGarantia(this.value)"> Sin Garantía</label>
                            <label class="pill-radio"><input type="radio" name="tiene_garantia" value="Con Garantía" onchange="toggleGarantia(this.value)"> Con Garantía</label>
                        </div>
                    </div>
                </div>

                <div id="box_fechas_garantia" style="display:none; background:#F8FAFC; padding:12px; border-radius:12px; border:1.5px dashed #CBD5E1; margin-bottom:14px;">
                    <div class="row-2">
                        <div class="form-group" style="margin-bottom:6px;">
                            <label class="form-label" for="modal_eq_gar_inicio">Fecha Inicio Garantía:</label>
                            <input type="date" id="modal_eq_gar_inicio" class="form-control" onchange="actualizarRestanteGarantia()">
                        </div>
                        <div class="form-group" style="margin-bottom:6px;">
                            <label class="form-label" for="modal_eq_gar_fin">Fecha Vencimiento Garantía:</label>
                            <input type="date" id="modal_eq_gar_fin" class="form-control" onchange="actualizarRestanteGarantia()">
                        </div>
                    </div>
                    <div id="badge_restante_garantia" style="font-size:12px; font-weight:700; margin-top:4px;"></div>
                </div>

                <!-- SECCIÓN 4: CRITICIDAD Y CATEGORIZACIÓN -->
                <div class="form-section-banner">
                    <span>📊 4. Criticidad y Categorización (Evaluación Oficial GAMLP)</span>
                </div>

                <div id="box_13_criterios" style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:12px; padding:12px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:11px; font-weight:700; color:#475569;">Puntaje: 1 (Bajo) / 2 (Medio) / 3 (Alto)</span>
                        <span style="font-size:11px; color:#64748B;">Total &ge;30: Alta | &ge;20: Media | &lt;20: Baja</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-weight:800; font-size:11px; color:#1E293B; border-bottom:1.5px solid #CBD5E1; padding-bottom:5px; margin-bottom:6px;">
                        <span>Parámetro de Evaluación</span>
                        <span style="display:flex; gap:20px; margin-right:12px;">
                            <span>1</span><span>2</span><span>3</span>
                        </span>
                    </div>
                    <div id="contenedor_filas_criterios"></div>

                    <!-- LÍNEA FINAL DE RESULTADO DE CRITICIDAD AUTO-CALCULADA -->
                    <div id="linea_nivel_criticidad" style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; border:2px solid #CBD5E1; border-radius:10px; padding:10px 14px; margin-top:12px; box-shadow:0 2px 5px rgba(0,0,0,0.04);">
                        <div>
                            <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;">Nivel de Criticidad (Auto-calculado):</div>
                            <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                                <span id="badge_criticidad_calculada" style="font-size:15px; font-weight:800; padding:4px 14px; border-radius:8px; background:#FEF3C7; color:#D97706; border:1.5px solid #FCD34D;">Media</span>
                                <span id="lbl_puntaje_criterios" style="font-size:12px; font-weight:700; color:#334155;">Puntaje: 0 / 39 pts</span>
                            </div>
                        </div>
                        <input type="hidden" id="modal_eq_criticidad" value="Media">
                        <div style="text-align:right;">
                            <span style="font-size:10px; font-weight:700; color:#94A3B8; display:block;">Evaluados</span>
                            <span id="lbl_conteo_evaluados" style="font-size:12px; font-weight:800; color:#475569;">0 / 13</span>
                        </div>
                    </div>
                </div>

                <!-- SECCIÓN 5: FOTOGRAFÍA DEL EQUIPO -->
                <div class="form-section-banner">📷 5. Fotografía del Equipo</div>

                <div class="form-group">
                    <div class="foto-dual-box">
                        <div class="foto-options-grid">
                            <button type="button" class="btn-foto-opt" onclick="document.getElementById('input_camara').click()">
                                <span class="foto-ico">📸</span>
                                <strong>Tomar Foto con Cámara</strong>
                                <small>Abre la cámara del celular</small>
                            </button>
                            <button type="button" class="btn-foto-opt" onclick="document.getElementById('input_galeria').click()">
                                <span class="foto-ico">📁</span>
                                <strong>Elegir de Galería</strong>
                                <small>Foto ya guardada en archivos</small>
                            </button>
                        </div>
                        <input type="file" id="input_camara" accept="image/*" capture="environment" style="display:none;" onchange="procesarFotoMovil(this)">
                        <input type="file" id="input_galeria" accept="image/*" style="display:none;" onchange="procesarFotoMovil(this)">

                        <div id="foto_preview_box" class="foto-preview-box">
                            <img id="img_preview" class="foto-preview-img" src="" alt="Foto">
                            <button type="button" class="btn-del-foto" onclick="quitarFotoMovil()">✕</button>
                        </div>
                        <input type="hidden" id="foto_base64" value="">
                    </div>
                </div>

                <!-- SECCIÓN 6: DATOS TÉCNICOS Y CONTEXTO OPERACIONAL (EXCEL) -->
                <div class="form-section-banner">
                    <span>🔬 6. Datos Técnicos y Contexto (Excel)</span>
                    <button type="button" class="btn-toggle-accordion-inline" onclick="toggleSeccion('box_datos_adicionales', this)">
                        <span class="lbl-btn-acc">Mostrar Detalles (Excel)</span> <span class="arrow-indicator">▼</span>
                    </button>
                </div>

                <div id="box_datos_adicionales" style="display:none; background:#F8FAFC; padding:14px; border-radius:12px; border:1.5px solid #E2E8F0; margin-bottom:14px;">
                    <div class="row-3">
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_voltaje">Voltaje:</label>
                            <input type="text" id="modal_eq_voltaje" class="form-control" placeholder="ej: 220V">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_corriente">Corriente:</label>
                            <input type="text" id="modal_eq_corriente" class="form-control" placeholder="ej: 5A">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_potencia">Potencia Consumida:</label>
                            <input type="text" id="modal_eq_potencia" class="form-control" placeholder="ej: 500W">
                        </div>
                    </div>
                    <div class="row-3">
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_vida_util">Vida Útil Estimada:</label>
                            <input type="text" id="modal_eq_vida_util" class="form-control" placeholder="ej: 10 años">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_peso">Peso:</label>
                            <input type="text" id="modal_eq_peso" class="form-control" placeholder="ej: 50 kg">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_dimensiones">Dimensiones:</label>
                            <input type="text" id="modal_eq_dimensiones" class="form-control" placeholder="ej: 120x80x90 cm">
                        </div>
                    </div>
                    <div class="row-3">
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_bateria">Batería de Respaldo:</label>
                            <input type="text" id="modal_eq_bateria" class="form-control" placeholder="ej: 12V 7Ah / Sí">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_software">Versión Software:</label>
                            <input type="text" id="modal_eq_software" class="form-control" placeholder="ej: v2.4.1">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="modal_eq_gases">Suministro de Gases:</label>
                            <input type="text" id="modal_eq_gases" class="form-control" placeholder="ej: O2 / Aire / Vacío">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label" for="modal_eq_contexto">Contexto Operacional:</label>
                        <textarea id="modal_eq_contexto" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa el contexto operacional..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_funciones">Funciones del Equipo Médico:</label>
                        <textarea id="modal_eq_funciones" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa las funciones del equipo..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_acciones_prev">Acciones Preventivas:</label>
                        <textarea id="modal_eq_acciones_prev" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa las acciones preventivas..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_insumos">Insumos / Accesorios:</label>
                        <textarea id="modal_eq_insumos" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa insumos y accesorios..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_fallas_comunes">Fallas Comunes:</label>
                        <textarea id="modal_eq_fallas_comunes" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa las fallas comunes..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_causas_fallo">Causas de Fallo en el Equipo:</label>
                        <textarea id="modal_eq_causas_fallo" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa las causas de fallo..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_efectos_fallo">Consecuencias de Fallo en el Equipo:</label>
                        <textarea id="modal_eq_efectos_fallo" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa las consecuencias de fallo..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="modal_eq_acciones_corr">Acciones Correctivas Comunes:</label>
                        <textarea id="modal_eq_acciones_corr" class="form-control" rows="3" style="min-height:80px;" placeholder="Describa las acciones correctivas comunes..."></textarea>
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label" for="modal_eq_obs">Observaciones Generales:</label>
                    <textarea id="modal_eq_obs" class="form-control" rows="3" style="min-height:80px;" placeholder="Detalles de conservación o inventario..."></textarea>
                </div>

                <button type="submit" id="btn_guardar_eq" class="btn-modal-submit">💾 Guardar Equipo Médico</button>
            </form>
        </div>
    </div>

    <!-- MODAL 2: AÑADIR / MODIFICAR MODELO AL CATÁLOGO -->
    <div id="modal_catalogo" class="modal-overlay">
        <div class="modal-content-sheet">
            <div class="modal-header-bar">
                <h2 id="modal_cat_title">🩺 Añadir Modelo al Catálogo</h2>
                <button class="btn-close-modal" onclick="cerrarModal('modal_catalogo')">✕</button>
            </div>
            <form onsubmit="guardarNuevoCatalogo(event)">
                <input type="hidden" id="cat_id" value="">
                <div class="form-group predictive-wrapper">
                    <label class="form-label" for="cat_nombre">Nombre del Equipo (*):</label>
                    <input type="text" id="cat_nombre" class="form-control" placeholder="Ej: Electrocardiógrafo, Centrífuga" required autocomplete="off" oninput="buscarSugerenciasNombreEquipo(this.value, 'cat_nombre_predictive', 'cat_nombre')" onfocus="buscarSugerenciasNombreEquipo(this.value, 'cat_nombre_predictive', 'cat_nombre')" onblur="cerrarSugerenciaRetraso(this)">
                    <div id="cat_nombre_predictive" class="predictive-box"></div>
                </div>
                <div class="row-2">
                    <div class="form-group predictive-wrapper">
                        <label class="form-label" for="cat_marca">Marca:</label>
                        <input type="text" id="cat_marca" class="form-control" placeholder="Ej: Bionet, Mindray" autocomplete="off" oninput="buscarSugerenciasMarca(this.value, 'cat_marca_predictive', 'cat_marca')" onfocus="buscarSugerenciasMarca(this.value, 'cat_marca_predictive', 'cat_marca')" onblur="cerrarSugerenciaRetraso(this)">
                        <div id="cat_marca_predictive" class="predictive-box"></div>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="cat_modelo">Modelo:</label>
                        <input type="text" id="cat_modelo" class="form-control" placeholder="Ej: CardioTouch 3000">
                    </div>
                </div>
                <div class="row-2">
                    <div class="form-group">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                            <label class="form-label" for="cat_area" style="margin-bottom:0;">Área Sugerida (*):</label>
                            <button type="button" id="btn_toggle_cat_area" onclick="toggleModoAreaCatalogo()" style="background:none; border:none; color:var(--accent); font-size:11.5px; font-weight:700; cursor:pointer; text-decoration:underline;">
                                ✏️ Escribir manual
                            </button>
                        </div>
                        <select id="cat_area" class="form-control" onchange="alCambiarAreaCatalogo()">
                            <option value="">-- Seleccionar Área Creada --</option>
                            <option value="__NUEVA__">➕ Escribir otra área personalizada...</option>
                        </select>
                        <input type="text" id="cat_area_manual" class="form-control" placeholder="Escribe el nombre del área..." style="display:none; margin-top:6px;">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="cat_piso">Piso:</label>
                        <input type="text" id="cat_piso" class="form-control" placeholder="Piso (se llena solo al elegir área)">
                    </div>
                </div>
                <button type="submit" id="btn_guardar_cat" class="btn-modal-submit">💾 Guardar en Catálogo Central</button>
            </form>
        </div>
    </div>

    <!-- MODAL 3: REGISTRO / MODIFICACIÓN DE MUEBLE / TI -->
    <div id="modal_mueble" class="modal-overlay">
        <div class="modal-content-sheet">
            <div class="modal-header-bar">
                <h2 id="modal_mue_title">🛋️ Registrar Activo Fijo (Mueblería / TI)</h2>
                <button class="btn-close-modal" onclick="cerrarModal('modal_mueble')">✕</button>
            </div>
            <form onsubmit="guardarNuevoMueble(event)">
                <input type="hidden" id="mue_id" value="">

                <!-- FILA 1: RED Y CENTRO DE SALUD -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_red">Dirección Administrativa (Red de Salud) (*):</label>
                        <select id="mue_red" class="form-control" onchange="alCambiarRedModalMueble()" style="font-weight:700; color:#003B64;" required>
                            <option value="">-- Seleccionar Red de Salud --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_centro">Unidad Organizacional (Centro de Salud) (*):</label>
                        <select id="mue_centro" class="form-control" onchange="alCambiarCentroModalMueble()" style="font-weight:700; color:#003B64;" required>
                            <option value="">-- Seleccionar Centro de Salud --</option>
                        </select>
                    </div>
                </div>

                <!-- FILA 2: UBICACIÓN FÍSICA Y SECTOR -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_area">Ubicación Física (Piso - Área):</label>
                        <select id="mue_area" class="form-control" onchange="alCambiarAreaMuebleModal()">
                            <option value="">-- Seleccionar Ubicación (Piso - Área) --</option>
                            <option value="General">General</option>
                            <option value="Piso 1 - Consulta Externa">Piso 1 - Consulta Externa</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_sector">Sector Actual:</label>
                        <select id="mue_sector" class="form-control">
                            <option value="SALUD" selected>SALUD</option>
                            <option value="G.A.M.L.P.">G.A.M.L.P.</option>
                        </select>
                    </div>
                </div>

                <!-- FILA 3: PERSONA Y CI ASIGNADOS (SE LLENA SOLO POR ÁREA) -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_persona">Persona Asignada (Doctora / Custodio):</label>
                        <input type="text" id="mue_persona" class="form-control" placeholder="Nombre completo del custodio...">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_ci">C.I. Asignado:</label>
                        <input type="text" id="mue_ci" class="form-control" placeholder="Ej: 10954587">
                    </div>
                </div>

                <!-- FILA 4: TIPO DE ACTIVO LLENABLE CON RECOMENDACIONES Y MARCA -->
                <div class="row-2">
                    <div class="form-group predictive-wrapper">
                        <label class="form-label" for="mue_tipo">Tipo de Activo (*) (Editable / Sugerencias):</label>
                        <input type="text" id="mue_tipo" class="form-control" placeholder="Ej: COMPUTADORA DE ESCRITORIO, SILLA, ESCRITORIO..." autocomplete="off" required oninput="buscarSugerenciasTipoMueble(this.value)" onfocus="buscarSugerenciasTipoMueble(this.value)" onblur="cerrarSugerenciaRetraso(this)">
                        <div id="mue_tipo_predictive" class="predictive-box"></div>
                    </div>
                    <div class="form-group predictive-wrapper">
                        <label class="form-label" for="mue_marca">Marca:</label>
                        <input type="text" id="mue_marca" class="form-control" placeholder="Ej: HP, Lenovo, Melamina" autocomplete="off" oninput="buscarSugerenciasMarca(this.value, 'mue_marca_predictive', 'mue_marca')" onfocus="buscarSugerenciasMarca(this.value, 'mue_marca_predictive', 'mue_marca')" onblur="cerrarSugerenciaRetraso(this)">
                        <div id="mue_marca_predictive" class="predictive-box"></div>
                    </div>
                </div>

                <!-- FILA 5: MODELO Y SERIE -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_modelo">Modelo:</label>
                        <input type="text" id="mue_modelo" class="form-control" placeholder="Ej: ProDesk 400">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_serie">Serie:</label>
                        <input type="text" id="mue_serie" class="form-control" placeholder="S/C">
                    </div>
                </div>

                <!-- FILA 6: CÓD. SISPAM Y BERTIN -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_sispam">Cód. SISPAM:</label>
                        <input type="text" id="mue_sispam" class="form-control" placeholder="S/C">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_bertin">Cód. BERTIN:</label>
                        <input type="text" id="mue_bertin" class="form-control" placeholder="S/C">
                    </div>
                </div>

                <!-- FILA 7: SAPM Y TRANSACCIÓN -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_sapm">Cód. SAPM:</label>
                        <input type="text" id="mue_sapm" class="form-control" placeholder="S/C">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_transaccion">Detalle Transacción:</label>
                        <input type="text" id="mue_transaccion" class="form-control" value="Asignacion 2026">
                    </div>
                </div>

                <!-- FILA 8: ESTADO Y FECHA DE ASIGNACIÓN -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_estado">Estado Conservación:</label>
                        <select id="mue_estado" class="form-control">
                            <option value="Bueno" selected>Bueno</option>
                            <option value="Regular">Regular</option>
                            <option value="Malo">Malo</option>
                            <option value="Baja">Baja</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_fecha_asig">Fecha Asignación:</label>
                        <input type="date" id="mue_fecha_asig" class="form-control">
                    </div>
                </div>

                <!-- FILA 9: CARGO Y DESCRIPCIÓN DEL BIEN -->
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="mue_cargo">Cargo Asignado:</label>
                        <input type="text" id="mue_cargo" class="form-control" placeholder="Ej: Biomedico, Médico General">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="mue_desc">Descripción del Bien (Opcional / Auto-rellenable):</label>
                        <input type="text" id="mue_desc" class="form-control" placeholder="Ej: CPU Lenovo ThinkCentre Core i5">
                    </div>
                </div>

                <!-- FILA 10: TÉCNICO INVENTARIADOR (LLENADO AUTOMÁTICO) -->
                <div class="form-group">
                    <label class="form-label" for="mue_tecnico">Técnico Inventariador (Llenado automático):</label>
                    <input type="text" id="mue_tecnico" class="form-control" placeholder="Nombre del técnico inventariador...">
                </div>

                <!-- FILA 11: OBSERVACIONES DE ASIGNACIÓN -->
                <div class="form-group">
                    <label class="form-label" for="mue_obs">Observaciones de Asignación:</label>
                    <textarea id="mue_obs" class="form-control" placeholder="Observaciones del bien mueble o TI..."></textarea>
                </div>

                <button type="submit" id="btn_guardar_mue" class="btn-modal-submit">💾 Guardar Activo Fijo</button>
            </form>
        </div>
    </div>

    <!-- MODAL 4: AÑADIR / MODIFICAR ÁREA DEL CENTRO -->
    <div id="modal_area" class="modal-overlay">
        <div class="modal-content-sheet">
            <div class="modal-header-bar">
                <h2 id="modal_area_title">📍 Añadir Nueva Área al Centro</h2>
                <button class="btn-close-modal" onclick="cerrarModal('modal_area')">✕</button>
            </div>
            <form onsubmit="guardarNuevaArea(event)">
                <input type="hidden" id="area_id" value="">
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="area_red">Red de Salud (*):</label>
                        <select id="area_red" class="form-control" onchange="alCambiarRedModalArea()" required>
                            <option value="">-- Seleccionar Red --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="area_centro">Centro de Salud (*):</label>
                        <select id="area_centro" class="form-control" required>
                            <option value="">-- Seleccionar Centro --</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="area_nom">Nombre del Área (*):</label>
                    <input type="text" id="area_nom" class="form-control" placeholder="Ej: Laboratorio Clínico, Vacunatorio 1" required>
                </div>
                <div class="form-group">
                    <label class="form-label" for="area_piso">Piso / Ubicación en el Centro:</label>
                    <input type="text" id="area_piso" class="form-control" placeholder="Ej: Planta Baja, Piso 1, Sótano">
                </div>
                <div class="form-group">
                    <label class="form-label" for="area_encargado">Encargado / Doctor(a) a Cargo:</label>
                    <input type="text" id="area_encargado" class="form-control" placeholder="Nombre completo del responsable">
                </div>
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="area_cargo">Cargo Oficial:</label>
                        <input type="text" id="area_cargo" class="form-control" placeholder="Ej: Médico General, Odontólogo">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="area_ci">C.I. Encargado:</label>
                        <input type="text" id="area_ci" class="form-control" placeholder="Ej: 4892114 LP">
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="area_contacto">Teléfono / Interno:</label>
                    <input type="text" id="area_contacto" class="form-control" placeholder="Ej: Int. 104 o Cel. 70123456">
                </div>
                <button type="submit" id="btn_guardar_area" class="btn-modal-submit">💾 Guardar Área en este Centro</button>
            </form>
        </div>
    </div>

    <!-- MODAL 5: REGISTRAR / MODIFICAR REPUESTO EN STOCK -->
    <div id="modal_repuesto" class="modal-overlay">
        <div class="modal-content-sheet">
            <div class="modal-header-bar">
                <h2 id="modal_rep_title">🔧 Registrar Repuesto en Stock</h2>
                <button class="btn-close-modal" onclick="cerrarModal('modal_repuesto')">✕</button>
            </div>
            <form onsubmit="guardarNuevoRepuesto(event)">
                <input type="hidden" id="rep_id" value="">
                <div class="row-2" style="background:#f8fafc; padding:8px; border-radius:8px; border:1px dashed #cbd5e1; margin-bottom:12px;">
                    <div class="form-group" style="margin-bottom:0;">
                        <label class="form-label" for="rep_red" style="font-size:0.75rem; color:#475569;">Red de Salud (*):</label>
                        <select id="rep_red" class="form-control" style="font-size:0.8rem; height:34px; padding:2px 8px;" onchange="alCambiarRedModalRepuesto()" required>
                            <option value="">-- Seleccionar Red --</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label class="form-label" for="rep_centro" style="font-size:0.75rem; color:#475569;">Centro de Salud (*):</label>
                        <select id="rep_centro" class="form-control" style="font-size:0.8rem; height:34px; padding:2px 8px;" required>
                            <option value="">-- Seleccionar Centro --</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="rep_nombre">Nombre del Repuesto / Accesorio (*):</label>
                    <input type="text" id="rep_nombre" class="form-control" placeholder="Ej: Sensor SpO2 Adulto, Batería Li-ion" required>
                </div>
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="rep_marca">Marca Compatible:</label>
                        <input type="text" id="rep_marca" class="form-control" placeholder="Ej: Mindray, Philips">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="rep_modelo">Modelo / P/N:</label>
                        <input type="text" id="rep_modelo" class="form-control" placeholder="Ej: 512F-30-28263">
                    </div>
                </div>
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="rep_cantidad">Cantidad en Stock (*):</label>
                        <input type="number" id="rep_cantidad" class="form-control" value="1" min="1" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="rep_costo">Costo Unitario (Bs.):</label>
                        <input type="number" step="0.5" id="rep_costo" class="form-control" value="0.0">
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="rep_area">Área / Almacén:</label>
                    <input type="text" id="rep_area" class="form-control" placeholder="Ej: Almacén de Biomédica, Farmacia">
                </div>
                <div class="form-group">
                    <label class="form-label" for="rep_obs">Observaciones:</label>
                    <textarea id="rep_obs" class="form-control" placeholder="Características técnicas o detalles..."></textarea>
                </div>
                <button type="submit" id="btn_guardar_rep" class="btn-modal-submit">💾 Guardar Repuesto en Stock</button>
            </form>
        </div>
    </div>

    <!-- MODAL 6: REGISTRAR / MODIFICAR INTERVENCIÓN TÉCNICA -->
    <div id="modal_intervencion" class="modal-overlay">
        <div class="modal-content-sheet">
            <div class="modal-header-bar">
                <h2 id="modal_inter_title">📋 Registrar Intervención Técnica</h2>
                <button class="btn-close-modal" onclick="cerrarModal('modal_intervencion')">✕</button>
            </div>
            <form onsubmit="guardarNuevaIntervencion(event)">
                <input type="hidden" id="inter_id" value="">
                <div class="form-group">
                    <label class="form-label" for="inter_equipo">Equipo Médico (*):</label>
                    <select id="inter_equipo" class="form-control" required>
                        <option value="">-- Seleccionar Equipo del Centro --</option>
                    </select>
                </div>
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="inter_tipo">Tipo de Intervención (*):</label>
                        <select id="inter_tipo" class="form-control">
                            <option value="Mantenimiento Preventivo">Preventivo</option>
                            <option value="Mantenimiento Correctivo">Correctivo</option>
                            <option value="Calibración / Inspección">Calibración</option>
                            <option value="Instalación / Puesta en Marcha">Instalación</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="inter_estado">Estado Resultante:</label>
                        <select id="inter_estado" class="form-control">
                            <option value="Bueno" selected>Bueno / Operativo</option>
                            <option value="Regular">Regular / Observado</option>
                            <option value="Malo">Malo / Fuera de Servicio</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="inter_trabajo">Trabajo Realizado (*):</label>
                    <textarea id="inter_trabajo" class="form-control" placeholder="Describa el trabajo técnico efectuado..." required></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label" for="inter_obs">Observaciones / Recomendaciones:</label>
                    <textarea id="inter_obs" class="form-control" placeholder="Recomendaciones de uso o pendientes..."></textarea>
                </div>
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="inter_repuesto">¿Usó Repuesto?</label>
                        <select id="inter_repuesto" class="form-control" onchange="toggleRepuestoIntervencion(this.value)">
                            <option value="NO">No</option>
                            <option value="SI">Sí</option>
                        </select>
                    </div>
                    <div class="form-group" id="box_rep_nom" style="display:none;">
                        <label class="form-label" for="inter_rep_nombre">Nombre del Repuesto:</label>
                        <input type="text" id="inter_rep_nombre" class="form-control" placeholder="Pieza sustituida">
                    </div>
                </div>
                <button type="submit" id="btn_guardar_inter" class="btn-modal-submit">💾 Guardar Intervención Técnica</button>
            </form>
        </div>
    </div>

    <!-- MODAL 7: GESTIÓN DE USUARIO Y PERMISOS (SOLO ADMIN) -->
    {% if es_admin %}
    <div id="modal_usuario_permisos" class="modal-overlay">
        <div class="modal-content-sheet" style="max-width: 720px;">
            <div class="modal-header-bar">
                <h2 id="modal_user_title">👥 Modificar Usuario y Permisos</h2>
                <button class="btn-close-modal" onclick="cerrarModal('modal_usuario_permisos')">✕</button>
            </div>
            <form onsubmit="guardarUsuarioPermisosSubmit(event)">
                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="u_ci">C.I. / Usuario (*):</label>
                        <input type="text" id="u_ci" class="form-control" placeholder="Ej: 10955499" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="u_nombre">Nombre Completo (*):</label>
                        <input type="text" id="u_nombre" class="form-control" placeholder="Ej: Ing. Adhemar Santos" required>
                    </div>
                </div>

                <div class="row-2">
                    <div class="form-group">
                        <label class="form-label" for="u_rol">Rol Institucional (*):</label>
                        <select id="u_rol" class="form-control" onchange="alCambiarRolEnModal(this.value)">
                            <option value="tecnico">Técnico Biomédico</option>
                            <option value="relevamiento">Técnico Relevamiento</option>
                            <option value="jefe">Administrador / Jefe</option>
                            <option value="visita">Visita / Solo Consulta</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="u_password">Contraseña (Dejar en blanco si no cambia):</label>
                        <input type="password" id="u_password" class="form-control" placeholder="••••••••">
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">Permisos de Acceso a Pestañas y Módulos:</label>
                    <div style="overflow-x: auto; background: #FFFFFF; border: 1px solid var(--border); border-radius: 10px; padding: 4px;">
                        <table class="matriz-permisos-table">
                            <thead>
                                <tr>
                                    <th>Módulo</th>
                                    <th>👁️ Ver</th>
                                    <th>➕ Agregar</th>
                                    <th>✎ Cambiar</th>
                                    <th>🗑️ Eliminar</th>
                                </tr>
                            </thead>
                            <tbody id="tbody_matriz_permisos">
                                <!-- Filas generadas dinámicamente -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <button type="submit" class="btn-modal-submit">💾 Guardar Permisos de Usuario</button>
            </form>
        </div>
    </div>
    {% endif %}

    <!-- JAVASCRIPT GLOBAL -->
    <script>
        const SEDES_DATA = {{ sedes | tojson }};
        const USUARIO_ACTUAL = {{ usuario | tojson }};
        const ES_ADMIN = {{ 'true' if es_admin else 'false' }};
        const USUARIO_PERMISOS = {{ usuario.get('permisos', {}) | tojson }};

        // Función de chequeo de permisos en cliente
        function puede(modulo, accion) {
            if (ES_ADMIN) return true;
            if (!USUARIO_PERMISOS || !USUARIO_PERMISOS[modulo]) return false;
            return !!USUARIO_PERMISOS[modulo][accion];
        }

        const MODULOS_SISTEMA = [
            ["Inventario", "📦 Inventario de Equipos"],
            ["Catalogo", "🩺 Catálogo de Equipos"],
            ["Muebleria", "🛋️ Mueblería y Computación"],
            ["Repuestos", "🔧 Gestión de Repuestos"],
            ["Areas", "📍 Áreas del Centro"],
            ["Historial", "📋 Mantenimientos / Historial"],
            ["Cronograma", "📅 Cronograma"],
            ["Analisis", "📊 Análisis Estadístico"],
            ["Sedes", "🏥 Sedes y Centros"],
            ["Usuarios", "👥 Gestión de Usuarios"]
        ];

        let LISTA_AREAS = [];
        let LISTA_CATALOGO = [];
        let LISTA_EQUIPOS = [];
        let LISTA_MUEBLES = [];
        let LISTA_REPUESTOS = [];
        let LISTA_HISTORIAL = [];
        let LISTA_USUARIOS = [];
        let LISTA_PAPELERA = [];
        let FILTRO_TIPO_ACTIVO = 'todo'; // 'todo' | 'equipos' | 'muebles'
        let FILTRO_PAPELERA_TABLA = 'todos';

        window.addEventListener('DOMContentLoaded', () => {
            let redGuardada = '';
            let cenGuardado = '';
            try {
                redGuardada = localStorage.getItem('cmms_top_red') || '';
                cenGuardado = localStorage.getItem('cmms_top_centro') || '';
            } catch(e){}

            if (redGuardada && document.getElementById('top_red')) {
                const optR = Array.from(document.getElementById('top_red').options).find(o => o.value === redGuardada);
                if (optR) document.getElementById('top_red').value = redGuardada;
            }
            alCambiarRedGlobal(cenGuardado);
            cargarCatalogoGlobal();
            if (ES_ADMIN) {
                cargarUsuariosGlobal();
                cargarPapeleraGlobal();
            }
            const activePane = document.querySelector('.tab-pane.active');
            if (!activePane) {
                const primerBtn = document.querySelector('.tab-btn');
                if (primerBtn) {
                    const tabKey = primerBtn.getAttribute('data-tab');
                    if (tabKey) cambiarPestana(tabKey);
                }
            }
        });

        // 1. Selector Territorial
        function alCambiarRedGlobal(centroPreseleccionado = '') {
            const redSel = document.getElementById('top_red').value;
            try { localStorage.setItem('cmms_top_red', redSel); } catch(e){}

            const redes = SEDES_DATA.redes || [];
            const rObj = redes.find(r => r.nombre === redSel);
            const rId = rObj ? rObj.id : null;

            const centros = (SEDES_DATA.centros || []).filter(c => !rId || c.red_salud_id === rId);
            const selCen = document.getElementById('top_centro');
            const valorPrevio = centroPreseleccionado || selCen.value;

            selCen.innerHTML = '<option value="">-- Todos los Centros --</option>';

            centros.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.nombre;
                opt.textContent = c.nombre;
                selCen.appendChild(opt);
            });

            if (valorPrevio && centros.some(c => c.nombre === valorPrevio)) {
                selCen.value = valorPrevio;
            } else if (centros.length > 0) {
                const preferido = centros.find(c => c.nombre.toUpperCase().includes('BAJO SAN PEDRO')) || centros[0];
                selCen.value = preferido.nombre;
            }

            alCambiarCentroGlobal();
        }

        async function alCambiarCentroGlobal() {
            const redSel = document.getElementById('top_red').value;
            const cenSel = document.getElementById('top_centro').value;
            try { localStorage.setItem('cmms_top_centro', cenSel); } catch(e){}

            await cargarAreasGlobal(cenSel, redSel);
            cargarInventarioCentro(cenSel, redSel);
            cargarMueblesCentro(cenSel, redSel);
            cargarRepuestosCentro(cenSel, redSel);
            cargarHistorialCentro(cenSel, redSel);
            cargarEstadisticasCentro(cenSel, redSel);
            renderizarSedesDirectorio();
        }

        // =====================================================================
        // SINCRONIZACIÓN Y SELECCIÓN DE RED Y CENTRO DENTRO DE LOS MODALES
        // =====================================================================

        function inicializarSelectoresSedesModal(redSelectId, centroSelectId, redDefault = '', centroDefault = '') {
            const selRed = document.getElementById(redSelectId);
            const selCen = document.getElementById(centroSelectId);
            if (!selRed || !selCen) return;

            const redes = SEDES_DATA.redes || [];
            selRed.innerHTML = '<option value="">-- Seleccionar Red de Salud --</option>';
            redes.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.nombre;
                opt.textContent = r.nombre;
                selRed.appendChild(opt);
            });

            let rActiva = redDefault;
            if (!rActiva || !redes.some(r => r.nombre === rActiva)) {
                rActiva = redes.length > 0 ? redes[0].nombre : '';
            }
            selRed.value = rActiva;

            poblarCentrosEnSelect(centroSelectId, rActiva, centroDefault);
        }

        function poblarCentrosEnSelect(centroSelectId, redNombre, centroDefault = '') {
            const selCen = document.getElementById(centroSelectId);
            if (!selCen) return;

            const redes = SEDES_DATA.redes || [];
            const rObj = redes.find(r => r.nombre === redNombre);
            const rId = rObj ? rObj.id : null;
            const centros = (SEDES_DATA.centros || []).filter(c => !rId || c.red_salud_id === rId);

            selCen.innerHTML = '<option value="">-- Seleccionar Centro de Salud --</option>';
            centros.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.nombre;
                opt.textContent = c.nombre;
                selCen.appendChild(opt);
            });

            if (centroDefault && centros.some(c => c.nombre === centroDefault)) {
                selCen.value = centroDefault;
            } else if (centros.length > 0) {
                selCen.value = centros[0].nombre;
            }
        }

        function alCambiarRedModalEquipo() {
            const redSel = document.getElementById('modal_eq_red').value;
            poblarCentrosEnSelect('modal_eq_centro', redSel);
            alCambiarCentroModalEquipo();
        }

        async function alCambiarCentroModalEquipo() {
            const redSel = document.getElementById('modal_eq_red') ? document.getElementById('modal_eq_red').value : '';
            const cenSel = document.getElementById('modal_eq_centro') ? document.getElementById('modal_eq_centro').value : '';

            // 1. Actualizar código AF correlativo si es nuevo registro
            const esEdicion = document.getElementById('modal_eq_es_edicion') && document.getElementById('modal_eq_es_edicion').value === '1';
            if (!esEdicion) {
                if (redSel && cenSel) {
                    document.getElementById('display_af_modal').textContent = 'CALCULANDO...';
                    try {
                        const res = await fetch(`/api/siguiente_af?red=${encodeURIComponent(redSel)}&centro=${encodeURIComponent(cenSel)}`);
                        const data = await res.json();
                        if (data.codigo_af) {
                            document.getElementById('display_af_modal').textContent = data.codigo_af;
                            document.getElementById('modal_eq_id_af').value = data.codigo_af;
                        }
                    } catch(e) {}
                } else {
                    document.getElementById('display_af_modal').textContent = 'SELECCIONE RED Y CENTRO';
                    document.getElementById('modal_eq_id_af').value = '';
                }
            }

            // 2. Cargar áreas del centro seleccionado
            await cargarAreasGlobal(cenSel, redSel);

            // 3. Autollenar datos de custodio/doctor
            alCambiarAreaModal();
        }

        function alCambiarRedModalMueble() {
            const redSel = document.getElementById('mue_red').value;
            poblarCentrosEnSelect('mue_centro', redSel);
            alCambiarCentroModalMueble();
        }

        async function alCambiarCentroModalMueble() {
            const redSel = document.getElementById('mue_red') ? document.getElementById('mue_red').value : '';
            const cenSel = document.getElementById('mue_centro') ? document.getElementById('mue_centro').value : '';
            await cargarAreasGlobal(cenSel, redSel);
            alCambiarAreaMuebleModal();
        }

        function alCambiarRedModalArea() {
            const redSel = document.getElementById('area_red').value;
            poblarCentrosEnSelect('area_centro', redSel);
        }

        function alCambiarRedModalRepuesto() {
            const redSel = document.getElementById('rep_red').value;
            poblarCentrosEnSelect('rep_centro', redSel);
        }

        // 2. Control de Pestañas
        function cambiarPestana(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => {
                if (btn.getAttribute('data-tab') === tabName) btn.classList.add('active');
                else btn.classList.remove('active');
            });
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            const pane = document.getElementById(`pane_${tabName}`);
            if (pane) pane.classList.add('active');
            if (tabName === 'papelera') {
                cargarPapeleraGlobal();
            }
        }

        // 3. Modales
        function abrirModal(id) { document.getElementById(id).style.display = 'flex'; }
        function cerrarModal(id) { document.getElementById(id).style.display = 'none'; }

        // 4. Copiar enlaces y utilidades de links
        function copiarTexto(texto, btnElement) {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(texto).then(() => {
                    mostrarFeedbackCopiado(btnElement);
                }).catch(() => fallbackCopiarTexto(texto, btnElement));
            } else {
                fallbackCopiarTexto(texto, btnElement);
            }
        }

        function fallbackCopiarTexto(texto, btnElement) {
            const temp = document.createElement("input");
            temp.value = texto;
            document.body.appendChild(temp);
            temp.select();
            try {
                document.execCommand("copy");
                mostrarFeedbackCopiado(btnElement);
            } catch (err) {
                prompt("Copia el enlace manualmente con Ctrl+C:", texto);
            }
            document.body.removeChild(temp);
        }

        function mostrarFeedbackCopiado(btn) {
            if (!btn) return;
            const orig = btn.innerHTML;
            btn.innerHTML = '✅ ¡Copiado!';
            const origBg = btn.style.backgroundColor;
            btn.style.backgroundColor = '#16A34A';
            setTimeout(() => {
                btn.innerHTML = orig;
                btn.style.backgroundColor = origBg;
            }, 2000);
        }

        function detectarIpHostLocal() {
            const loc = window.location;
            const urlActual = loc.origin + '/movil';
            const lbl = document.getElementById('lbl_enlace_local');
            if (lbl) {
                lbl.innerText = urlActual;
                alert(`Dirección web actual detectada:\n${urlActual}`);
            }
        }

        // =====================================================================
        // CARGAS DE DATOS DE LA API
        // =====================================================================

        // =====================================================================
        // UTILIDADES DE ÁREAS Y UBICACIÓN FÍSICA
        // =====================================================================

        function formatearAreaNombre(a) {
            if (!a) return '';
            const nom = (a.nombre || '').trim();
            let piso = (a.piso || '').trim();
            if (!piso || piso === '-') return nom;
            const low = piso.toLowerCase();
            if (!low.startsWith('piso') && !low.startsWith('planta') && !low.startsWith('pb')) {
                piso = 'Piso ' + piso;
            }
            return `${piso} - ${nom}`;
        }

        function obtenerAreaObj(val) {
            if (!val) return null;
            const v = String(val).toLowerCase().trim();
            // 1. Coincidencia exacta por ID
            let match = (LISTA_AREAS || []).find(a => String(a.id) === v);
            if (match) return match;

            // 2. Coincidencia exacta por nombre formateado (ej: "Piso 1 - Consultorio 3")
            match = (LISTA_AREAS || []).find(a => formatearAreaNombre(a).toLowerCase().trim() === v);
            if (match) return match;

            // 3. Coincidencia exacta por nombre de área (ej: "Consultorio 3")
            match = (LISTA_AREAS || []).find(a => (a.nombre || '').toLowerCase().trim() === v);
            if (match) return match;

            // 4. Coincidencia limpia por sufijo " - <nombre>"
            match = (LISTA_AREAS || []).find(a => {
                const nom = (a.nombre || '').toLowerCase().trim();
                return nom && (v.endsWith(' - ' + nom) || v === nom);
            });
            if (match) return match;

            return null;
        }

        // =====================================================================
        // MOTOR PREDICTIVO DE ESCRITURA Y AUTOCOMPLETADO INTELIGENTE
        // =====================================================================

        function calcularSimilitud(s1, s2) {
            if (!s1 || !s2) return 0;
            const str1 = s1.toLowerCase().trim();
            const str2 = s2.toLowerCase().trim();
            if (str1 === str2) return 1.0;
            if (str2.startsWith(str1) || str1.startsWith(str2)) return 0.95;
            if (str2.includes(str1) || str1.includes(str2)) return 0.85;

            // Levenshtein para tolerancia a errores ortográficos y variaciones
            const m = str1.length, n = str2.length;
            const d = [];
            for (let i = 0; i <= m; i++) d[i] = [i];
            for (let j = 0; j <= n; j++) d[0][j] = j;
            for (let i = 1; i <= m; i++) {
                for (let j = 1; j <= n; j++) {
                    const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
                    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost);
                }
            }
            const dist = d[m][n];
            const maxLen = Math.max(m, n);
            return maxLen === 0 ? 1 : (1 - dist / maxLen);
        }

        function cerrarCajasPredictivas() {
            document.querySelectorAll('.predictive-box').forEach(b => {
                b.style.display = 'none';
                b.innerHTML = '';
            });
        }

        function cerrarSugerenciaRetraso(inputElem) {
            setTimeout(() => {
                const wrapper = inputElem ? inputElem.closest('.predictive-wrapper') : null;
                if (wrapper) {
                    const box = wrapper.querySelector('.predictive-box');
                    if (box && (!document.activeElement || !wrapper.contains(document.activeElement))) {
                        box.style.display = 'none';
                        box.innerHTML = '';
                    }
                }
            }, 250);
        }

        // Si el usuario pasa a otro campo donde escribir (focusin), cerrar recomendaciones del anterior
        document.addEventListener('focusin', function(e) {
            document.querySelectorAll('.predictive-wrapper').forEach(wrapper => {
                if (!wrapper.contains(e.target)) {
                    const b = wrapper.querySelector('.predictive-box');
                    if (b) {
                        b.style.display = 'none';
                        b.innerHTML = '';
                    }
                }
            });
        });

        // Si hace clic fuera del wrapper activo, cerrar sugerencias
        document.addEventListener('click', function(e) {
            document.querySelectorAll('.predictive-wrapper').forEach(wrapper => {
                if (!wrapper.contains(e.target)) {
                    const b = wrapper.querySelector('.predictive-box');
                    if (b) {
                        b.style.display = 'none';
                        b.innerHTML = '';
                    }
                }
            });
        });

        // Cerrar sugerencias al presionar Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                cerrarCajasPredictivas();
            }
        });

        const NOMBRES_EQUIPOS_ESTANDAR = [
            "Desfibrilador", "Desfibrilador Bifásico", "Desfibrilador Monofásico",
            "Monitor Multiparámetro", "Monitor de Signos Vitales", "Electrocardiógrafo",
            "Bomba de Infusión", "Bomba de Jeringa", "Incubadora Neonatal", "Incubadora de Transporte",
            "Aspirador de Secreciones", "Esterilizador Autoclave", "Autoclave a Vapor",
            "Centrífuga de Laboratorio", "Microscopio Binocular", "Ecógrafo Portátil", "Ecógrafo Doppler",
            "Lámpara Cialítica", "Mesa de Operaciones", "Oxímetro de Pulso", "Tensiómetro Digital",
            "Tensiómetro Aneroide", "Termómetro Infrarrojo", "Laringoscopio", "Negatoscopio",
            "Balanza con Altimetro", "Glucómetro", "Ambulancia Móvil", "Equipo de Rayos X Portátil",
            "Equipo de Rayos X Dental", "Sillón Odontológico", "Doppler Fetal", "Fototerapia Neonatal",
            "Concentrador de Oxígeno", "Ventilador Mecánico / Respirador"
        ];

        const TIPOS_MUEBLES_BASE = [
            "COMPUTADORA DE ESCRITORIO",
            "COMPUTADORA PORTÁTIL / LAPTOP",
            "IMPRESORA LÁSER / MULTIFUNCIONAL",
            "ESCÁNER DOCUMENTAL",
            "MONITOR / PANTALLA LED",
            "ESTABILIZADOR DE VOLTAJE",
            "UPS / SISTEMA DE RESPALDO",
            "ESCRITORIO METÁLICO / MELAMINA",
            "SILLA GIRATORIA ERGONÓMICA",
            "SILLA TANDEM / ESPERA",
            "SILLÓN EJECUTIVO",
            "VITRINA MÉDICA DE VIDRIO",
            "ESTANTE METÁLICO",
            "GAVETERO / ARCHIVADOR",
            "MESA DE CURACIONES / EXAMEN",
            "PORTASUERO METÁLICO",
            "BIOMBO CLÍNICO",
            "CAMILLA DE TRANSPORTE",
            "REFRIGERADOR DE BIOLÓGICOS / VACUNAS",
            "AIRE ACONDICIONADO"
        ];

        const MARCAS_BASE = [
            "Mindray", "GE Healthcare", "Philips", "Nihon Kohden", "Bionet",
            "Welch Allyn", "Contec", "Edan", "Dräger", "Siemens", "HP", "Lenovo",
            "Dell", "Epson", "Canon", "Brother", "Samsung", "LG", "AOC",
            "Kingston", "APC", "Melamina GAMLP", "Metálica GAMLP"
        ];

        function buscarSugerenciasCatalogo(query) {
            const box = document.getElementById('modal_eq_catalogo_predictive');
            if (!box) return;
            const q = (query || '').trim();
            const items = (LISTA_CATALOGO || []).map(c => {
                const fullStr = `${c.nombre || ''} ${c.marca || ''} ${c.modelo || ''}`.trim();
                const score = q ? Math.max(
                    calcularSimilitud(q, c.nombre || ''),
                    calcularSimilitud(q, c.marca || ''),
                    calcularSimilitud(q, c.modelo || ''),
                    calcularSimilitud(q, fullStr)
                ) : 1;
                return { item: c, score: score, fullStr: fullStr };
            }).filter(x => !q || x.score >= 0.38 || x.fullStr.toLowerCase().includes(q.toLowerCase()))
              .sort((a, b) => b.score - a.score)
              .slice(0, 8);

            if (items.length === 0) {
                box.innerHTML = `<div class="predictive-item" style="cursor:default; color:#94A3B8;">Sin coincidencias en catálogo. Escribe el nombre abajo.</div>`;
                box.style.display = 'block';
                return;
            }

            let html = '';
            items.forEach(it => {
                const c = it.item;
                html += `
                <div class="predictive-item" onclick="seleccionarCatalogoSugerido(${c.id})">
                    <div class="predictive-title">
                        <span>${c.nombre}</span>
                        <span class="predictive-badge">Catálogo</span>
                    </div>
                    <div class="predictive-subtitle">
                        ${c.marca ? `<strong>Marca:</strong> ${c.marca}` : ''} 
                        ${c.modelo ? `| <strong>Modelo:</strong> ${c.modelo}` : ''}
                        ${c.area ? `| <strong>Área sugerida:</strong> ${c.area}` : ''}
                    </div>
                </div>`;
            });
            box.innerHTML = html;
            box.style.display = 'block';
        }

        function seleccionarCatalogoSugerido(catId) {
            const c = (LISTA_CATALOGO || []).find(it => String(it.id) === String(catId));
            if (!c) return;
            const inpCat = document.getElementById('modal_eq_catalogo_input');
            if (inpCat) inpCat.value = `${c.nombre} (${c.marca || ''} ${c.modelo || ''})`.replace(/\\(\\s*\\)/g, '').trim();

            document.getElementById('modal_eq_nombre').value = c.nombre || '';
            if (c.marca) document.getElementById('modal_eq_marca').value = c.marca;
            if (c.modelo) document.getElementById('modal_eq_modelo').value = c.modelo;

            if (c.area) {
                const matchArea = obtenerAreaObj(c.area);
                if (matchArea) {
                    document.getElementById('modal_eq_area').value = formatearAreaNombre(matchArea);
                    alCambiarAreaModal();
                }
            }
            cerrarCajasPredictivas();
        }

        function buscarSugerenciasNombreEquipo(query, boxId = 'modal_eq_nombre_predictive', inputId = 'modal_eq_nombre') {
            const box = document.getElementById(boxId);
            if (!box) return;
            const q = (query || '').trim();

            const poolNombres = new Set();
            NOMBRES_EQUIPOS_ESTANDAR.forEach(n => poolNombres.add(n));
            (LISTA_CATALOGO || []).forEach(c => { if (c.nombre) poolNombres.add(c.nombre); });
            (LISTA_EQUIPOS || []).forEach(e => { if (e.nombre) poolNombres.add(e.nombre); });

            const lista = Array.from(poolNombres).map(n => ({
                nombre: n,
                score: q ? calcularSimilitud(q, n) : 1
            })).filter(x => !q || x.score >= 0.4 || x.nombre.toLowerCase().includes(q.toLowerCase()))
              .sort((a, b) => b.score - a.score)
              .slice(0, 8);

            if (lista.length === 0) {
                box.style.display = 'none';
                return;
            }

            let html = '';
            lista.forEach(item => {
                html += `
                <div class="predictive-item" onclick="seleccionarNombreEquipoSugerido('${item.nombre.replace(/'/g, "\\'")}', '${inputId}')">
                    <div class="predictive-title">
                        <span>${item.nombre}</span>
                        <span class="predictive-badge">Equipo</span>
                    </div>
                </div>`;
            });
            box.innerHTML = html;
            box.style.display = 'block';
        }

        function seleccionarNombreEquipoSugerido(nombre, inputId = 'modal_eq_nombre') {
            const inp = document.getElementById(inputId);
            if (inp) inp.value = nombre;
            if (inputId === 'modal_eq_nombre') {
                const cat = (LISTA_CATALOGO || []).find(c => (c.nombre || '').toLowerCase() === nombre.toLowerCase());
                if (cat) {
                    const eMarca = document.getElementById('modal_eq_marca');
                    const eModelo = document.getElementById('modal_eq_modelo');
                    if (eMarca && !eMarca.value && cat.marca) eMarca.value = cat.marca;
                    if (eModelo && !eModelo.value && cat.modelo) eModelo.value = cat.modelo;
                }
            } else if (inputId === 'cat_nombre') {
                const cat = (LISTA_CATALOGO || []).find(c => (c.nombre || '').toLowerCase() === nombre.toLowerCase());
                if (cat) {
                    const eMarca = document.getElementById('cat_marca');
                    const eModelo = document.getElementById('cat_modelo');
                    if (eMarca && !eMarca.value && cat.marca) eMarca.value = cat.marca;
                    if (eModelo && !eModelo.value && cat.modelo) eModelo.value = cat.modelo;
                    if (cat.area) poblarSelectorAreasCatalogo(cat.area, cat.piso);
                }
            }
            cerrarCajasPredictivas();
        }

        function buscarSugerenciasTipoMueble(query) {
            const box = document.getElementById('mue_tipo_predictive');
            if (!box) return;
            const q = (query || '').trim();

            const pool = new Set();
            TIPOS_MUEBLES_BASE.forEach(t => pool.add(t));
            (LISTA_MUEBLES || []).forEach(m => { if (m.tipo_activo) pool.add(m.tipo_activo.toUpperCase()); });

            const lista = Array.from(pool).map(t => ({
                tipo: t,
                score: q ? calcularSimilitud(q, t) : 1
            })).filter(x => !q || x.score >= 0.38 || x.tipo.toLowerCase().includes(q.toLowerCase()))
              .sort((a, b) => b.score - a.score)
              .slice(0, 8);

            if (lista.length === 0) {
                box.style.display = 'none';
                return;
            }

            let html = '';
            lista.forEach(it => {
                html += `
                <div class="predictive-item" onclick="seleccionarTipoMuebleSugerido('${it.tipo.replace(/'/g, "\\'")}')">
                    <div class="predictive-title">
                        <span>${it.tipo}</span>
                        <span class="predictive-badge">Tipo Activo</span>
                    </div>
                </div>`;
            });
            box.innerHTML = html;
            box.style.display = 'block';
        }

        function seleccionarTipoMuebleSugerido(tipo) {
            document.getElementById('mue_tipo').value = tipo;
            cerrarCajasPredictivas();
        }

        function buscarSugerenciasMarca(query, boxId, inputId) {
            const box = document.getElementById(boxId);
            if (!box) return;
            const q = (query || '').trim();

            const pool = new Set();
            MARCAS_BASE.forEach(m => pool.add(m));
            (LISTA_CATALOGO || []).forEach(c => { if (c.marca) pool.add(c.marca); });
            (LISTA_EQUIPOS || []).forEach(e => { if (e.marca) pool.add(e.marca); });
            (LISTA_MUEBLES || []).forEach(m => { if (m.marca) pool.add(m.marca); });

            const lista = Array.from(pool).map(m => ({
                marca: m,
                score: q ? calcularSimilitud(q, m) : 1
            })).filter(x => !q || x.score >= 0.4 || x.marca.toLowerCase().includes(q.toLowerCase()))
              .sort((a, b) => b.score - a.score)
              .slice(0, 8);

            if (lista.length === 0) {
                box.style.display = 'none';
                return;
            }

            let html = '';
            lista.forEach(it => {
                html += `
                <div class="predictive-item" onclick="seleccionarMarcaSugerida('${it.marca.replace(/'/g, "\\'")}', '${inputId}')">
                    <div class="predictive-title">
                        <span>${it.marca}</span>
                        <span class="predictive-badge">Marca</span>
                    </div>
                </div>`;
            });
            box.innerHTML = html;
            box.style.display = 'block';
        }

        function seleccionarMarcaSugerida(marca, inputId) {
            const inp = document.getElementById(inputId);
            if (inp) inp.value = marca;
            cerrarCajasPredictivas();
        }

        // =====================================================================
        // CARGA DE ÁREAS VINCULADAS AL CENTRO SELECCIONADO
        // =====================================================================

        async function cargarAreasGlobal(centro, red = '', areaPrevia = '') {
            try {
                let url = `/api/areas?centro=${encodeURIComponent(centro || '')}`;
                if (red) url += `&red=${encodeURIComponent(red)}`;
                const res = await fetch(url);
                LISTA_AREAS = await res.json();
                renderizarListaAreas(LISTA_AREAS);

                const selEqArea = document.getElementById('modal_eq_area');
                const selMueArea = document.getElementById('mue_area');
                if (selEqArea) selEqArea.innerHTML = '<option value="">-- Seleccionar Ubicación (Piso - Área) --</option>';
                if (selMueArea) selMueArea.innerHTML = '<option value="">-- Seleccionar Ubicación (Piso - Área) --</option>';

                if (Array.isArray(LISTA_AREAS) && LISTA_AREAS.length > 0) {
                    LISTA_AREAS.forEach(a => {
                        const fmt = formatearAreaNombre(a);
                        if (selEqArea) {
                            const o1 = document.createElement('option');
                            o1.value = fmt; 
                            o1.textContent = fmt;
                            o1.setAttribute('data-id', a.id);
                            o1.setAttribute('data-encargado', a.encargado || '');
                            o1.setAttribute('data-cargo', a.cargo || '');
                            o1.setAttribute('data-ci', a.ci_encargado || '');
                            o1.setAttribute('data-piso', a.piso || '');
                            selEqArea.appendChild(o1);
                        }
                        if (selMueArea) {
                            const o2 = document.createElement('option');
                            o2.value = fmt; 
                            o2.textContent = fmt;
                            o2.setAttribute('data-id', a.id);
                            o2.setAttribute('data-encargado', a.encargado || '');
                            o2.setAttribute('data-cargo', a.cargo || '');
                            o2.setAttribute('data-ci', a.ci_encargado || '');
                            o2.setAttribute('data-piso', a.piso || '');
                            selMueArea.appendChild(o2);
                        }
                    });
                } else {
                    const defAreas = ['General', 'Piso 1 - Consulta Externa', 'Piso 1 - Emergencias', 'Piso 1 - Administración', 'Piso 1 - Farmacia', 'Piso 1 - Odontología'];
                    defAreas.forEach(fmt => {
                        if (selEqArea) {
                            const o1 = document.createElement('option');
                            o1.value = fmt; o1.textContent = fmt;
                            selEqArea.appendChild(o1);
                        }
                        if (selMueArea) {
                            const o2 = document.createElement('option');
                            o2.value = fmt; o2.textContent = fmt;
                            selMueArea.appendChild(o2);
                        }
                    });
                }

                if (areaPrevia) {
                    if (selEqArea) {
                        selEqArea.value = areaPrevia;
                        alCambiarAreaModal();
                    }
                    if (selMueArea) {
                        selMueArea.value = areaPrevia;
                        alCambiarAreaMuebleModal();
                    }
                }

                // Mantener sincronizado el selector de áreas del catálogo
                await poblarSelectorAreasCatalogo();
            } catch (e) { console.error(e); }
        }

        async function poblarSelectorAreasCatalogo(areaPrevia = '', pisoPrevio = '') {
            const selCatArea = document.getElementById('cat_area');
            if (!selCatArea) return;

            let areasDisponibles = Array.isArray(LISTA_AREAS) && LISTA_AREAS.length > 0 ? [...LISTA_AREAS] : [];
            if (areasDisponibles.length === 0) {
                try {
                    const cenSel = document.getElementById('top_centro') ? document.getElementById('top_centro').value : '';
                    const redSel = document.getElementById('top_red') ? document.getElementById('top_red').value : '';
                    let url = `/api/areas?centro=${encodeURIComponent(cenSel || '')}`;
                    if (redSel) url += `&red=${encodeURIComponent(redSel)}`;
                    let res = await fetch(url);
                    let datos = await res.json();
                    if (Array.isArray(datos) && datos.length > 0) {
                        areasDisponibles = datos;
                        LISTA_AREAS = datos;
                    } else {
                        const resGlobal = await fetch('/api/areas');
                        const datosGlobal = await resGlobal.json();
                        if (Array.isArray(datosGlobal)) areasDisponibles = datosGlobal;
                    }
                } catch (e) {
                    console.error('Error cargando áreas para catálogo:', e);
                }
            }

            selCatArea.innerHTML = `
                <option value="">-- Seleccionar Área Creada --</option>
                <option value="__NUEVA__">➕ Escribir otra área personalizada...</option>
            `;

            const mapaAreas = new Map();
            areasDisponibles.forEach(a => {
                const nom = (a.nombre || '').trim();
                if (nom && !mapaAreas.has(nom.toLowerCase())) {
                    mapaAreas.set(nom.toLowerCase(), a);
                }
            });

            let encontrada = false;
            mapaAreas.forEach((a) => {
                const opt = document.createElement('option');
                opt.value = a.nombre;
                opt.dataset.piso = a.piso || '';
                const txtPiso = a.piso ? `(${a.piso})` : '';
                const txtCentro = a.centro_salud_nombre ? `• ${a.centro_salud_nombre}` : '';
                const strCompleta = `${a.nombre} ${txtPiso} ${txtCentro}`.trim();
                opt.textContent = strCompleta.split(' ').filter(Boolean).join(' ');
                if (areaPrevia && (a.nombre.toLowerCase() === areaPrevia.toLowerCase() || opt.value.toLowerCase() === areaPrevia.toLowerCase())) {
                    opt.selected = true;
                    encontrada = true;
                }
                selCatArea.appendChild(opt);
            });

            if (areaPrevia && !encontrada && areaPrevia !== '__NUEVA__') {
                const optCustom = document.createElement('option');
                optCustom.value = areaPrevia;
                optCustom.dataset.piso = pisoPrevio || '';
                optCustom.textContent = `${areaPrevia} ${pisoPrevio ? `(${pisoPrevio})` : ''}`.trim();
                optCustom.selected = true;
                selCatArea.appendChild(optCustom);
            }

            if (pisoPrevio && document.getElementById('cat_piso')) {
                document.getElementById('cat_piso').value = pisoPrevio;
            }
        }

        function alCambiarAreaCatalogo() {
            const sel = document.getElementById('cat_area');
            const inpManual = document.getElementById('cat_area_manual');
            const inpPiso = document.getElementById('cat_piso');
            const btnToggle = document.getElementById('btn_toggle_cat_area');
            if (!sel) return;

            if (sel.value === '__NUEVA__') {
                sel.style.display = 'none';
                if (inpManual) {
                    inpManual.style.display = 'block';
                    inpManual.focus();
                }
                if (btnToggle) btnToggle.textContent = '📋 Elegir de lista';
                if (inpPiso) inpPiso.value = '';
                return;
            }

            const optSel = sel.options[sel.selectedIndex];
            if (optSel && optSel.dataset && optSel.dataset.piso) {
                if (inpPiso) inpPiso.value = optSel.dataset.piso;
            } else if (!sel.value) {
                if (inpPiso) inpPiso.value = '';
            }
        }

        function toggleModoAreaCatalogo() {
            const sel = document.getElementById('cat_area');
            const inpManual = document.getElementById('cat_area_manual');
            const btnToggle = document.getElementById('btn_toggle_cat_area');
            if (!sel || !inpManual) return;

            if (inpManual.style.display === 'none') {
                sel.style.display = 'none';
                inpManual.style.display = 'block';
                inpManual.value = sel.value && sel.value !== '__NUEVA__' ? sel.value : '';
                inpManual.focus();
                if (btnToggle) btnToggle.textContent = '📋 Elegir de lista';
            } else {
                inpManual.style.display = 'none';
                sel.style.display = 'block';
                if (btnToggle) btnToggle.textContent = '✏️ Escribir manual';
                if (sel.value === '__NUEVA__') sel.value = '';
                alCambiarAreaCatalogo();
            }
        }

        async function cargarCatalogoGlobal() {
            try {
                const res = await fetch('/api/catalogo');
                LISTA_CATALOGO = await res.json();
                renderizarListaCatalogo(LISTA_CATALOGO);

                const selCat = document.getElementById('modal_eq_catalogo');
                if (selCat) {
                    selCat.innerHTML = '<option value="">-- Seleccionar del Catálogo --</option>';
                    LISTA_CATALOGO.forEach(c => {
                        const opt = document.createElement('option');
                        opt.value = c.id;
                        opt.textContent = `${c.nombre} - ${c.marca || ''} - ${c.modelo || ''}`.replace(/ - $/g, '');
                        selCat.appendChild(opt);
                    });
                }
            } catch (e) { console.error(e); }
        }

        async function cargarInventarioCentro(centro, red = '') {
            const cont = document.getElementById('lista_inventario');
            if (!cont) return;
            cont.innerHTML = '<div class="empty-state"><span>⏳</span>Cargando equipos...</div>';
            try {
                let url = `/api/equipos?centro=${encodeURIComponent(centro || '')}`;
                if (red) url += `&red=${encodeURIComponent(red)}`;
                const res = await fetch(url);
                LISTA_EQUIPOS = await res.json();
                actualizarContadoresInventario();
                aplicarFiltroInventario();

                const selInter = document.getElementById('inter_equipo');
                if (selInter) {
                    selInter.innerHTML = '<option value="">-- Seleccionar Equipo del Centro --</option>';
                    LISTA_EQUIPOS.forEach(e => {
                        const opt = document.createElement('option');
                        opt.value = e.id;
                        opt.textContent = `[${e.id}] ${e.nombre} (${e.area || 'Sin Área'})`;
                        selInter.appendChild(opt);
                    });
                }
            } catch (e) {
                cont.innerHTML = '<div class="empty-state"><span>⚠️</span>Error al cargar inventario</div>';
            }
        }

        async function cargarMueblesCentro(centro, red = '') {
            const cont = document.getElementById('lista_muebles');
            if (cont) cont.innerHTML = '<div class="empty-state"><span>⏳</span>Cargando muebles...</div>';
            try {
                let url = `/api/muebles?centro=${encodeURIComponent(centro || '')}`;
                if (red) url += `&red=${encodeURIComponent(red)}`;
                const res = await fetch(url);
                LISTA_MUEBLES = await res.json();
                if (cont) renderizarListaMuebles(LISTA_MUEBLES);
                actualizarContadoresInventario();
                aplicarFiltroInventario();
            } catch (e) {
                if (cont) cont.innerHTML = '<div class="empty-state"><span>⚠️</span>Error al cargar muebles</div>';
            }
        }

        async function cargarRepuestosCentro(centro, red = '') {
            const cont = document.getElementById('lista_repuestos');
            if (!cont) return;
            cont.innerHTML = '<div class="empty-state"><span>⏳</span>Cargando repuestos...</div>';
            try {
                let url = `/api/repuestos?centro=${encodeURIComponent(centro || '')}`;
                if (red) url += `&red=${encodeURIComponent(red)}`;
                const res = await fetch(url);
                LISTA_REPUESTOS = await res.json();
                renderizarListaRepuestos(LISTA_REPUESTOS);
            } catch (e) {
                cont.innerHTML = '<div class="empty-state"><span>⚠️</span>Error al cargar repuestos</div>';
            }
        }

        async function cargarHistorialCentro(centro, red = '') {
            const cont = document.getElementById('lista_historial');
            if (!cont) return;
            cont.innerHTML = '<div class="empty-state"><span>⏳</span>Cargando intervenciones...</div>';
            try {
                let url = `/api/intervenciones?centro=${encodeURIComponent(centro || '')}`;
                if (red) url += `&red=${encodeURIComponent(red)}`;
                const res = await fetch(url);
                LISTA_HISTORIAL = await res.json();
                renderizarListaHistorial(LISTA_HISTORIAL);
                renderizarListaCronograma(LISTA_HISTORIAL);
            } catch (e) {
                cont.innerHTML = '<div class="empty-state"><span>⚠️</span>Error al cargar intervenciones</div>';
            }
        }

        async function cargarEstadisticasCentro(centro, red = '') {
            if (!document.getElementById('pane_analisis')) return;
            try {
                let url = `/api/estadisticas?centro=${encodeURIComponent(centro || '')}`;
                if (red) url += `&red=${encodeURIComponent(red)}`;
                const res = await fetch(url);
                const st = await res.json();
                document.getElementById('kpi_total_eq').textContent = st.total_equipos || 0;
                document.getElementById('kpi_operativos').textContent = st.operativos || 0;
                document.getElementById('kpi_mantenimiento').textContent = st.mantenimiento || 0;
                document.getElementById('kpi_baja').textContent = st.baja || 0;
                document.getElementById('kpi_crit_alta').textContent = st.criticidad_alta || 0;
                document.getElementById('kpi_tot_muebles').textContent = st.total_muebles || 0;
                document.getElementById('kpi_tot_repuestos').textContent = st.total_repuestos || 0;
                document.getElementById('kpi_tot_intervenciones').textContent = st.total_intervenciones || 0;

                const box = document.getElementById('distribucion_areas_box');
                const areas = st.areas_distribucion || [];
                if (areas.length === 0) {
                    box.innerHTML = '<div class="empty-state" style="padding:15px;"><span>📋</span>No hay datos de áreas aún</div>';
                    return;
                }
                let h = '';
                const max = areas[0].cantidad || 1;
                areas.forEach(a => {
                    const pct = Math.round((a.cantidad / max) * 100);
                    h += `
                    <div style="margin-bottom: 8px;">
                        <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700; margin-bottom:2px;">
                            <span>${a.area_nombre}</span>
                            <span>${a.cantidad} equipos</span>
                        </div>
                        <div style="background:#E2E8F0; border-radius:6px; height:8px; overflow:hidden;">
                            <div style="background:var(--primary); width:${pct}%; height:100%;"></div>
                        </div>
                    </div>`;
                });
                box.innerHTML = h;
            } catch (e) {}
        }

        async function cargarUsuariosGlobal() {
            const cont = document.getElementById('lista_usuarios');
            if (!cont) return;
            cont.innerHTML = '<div class="empty-state"><span>⏳</span>Cargando usuarios...</div>';
            try {
                const res = await fetch('/api/usuarios');
                if (res.ok) {
                    LISTA_USUARIOS = await res.json();
                    renderizarListaUsuarios(LISTA_USUARIOS);
                } else {
                    cont.innerHTML = '<div class="empty-state"><span>🔒</span>Acceso solo para administradores</div>';
                }
            } catch (e) {
                cont.innerHTML = '<div class="empty-state"><span>⚠️</span>Error al cargar usuarios</div>';
            }
        }

        // =====================================================================
        // RENDERIZADO DE VISTAS EN TARJETAS (CON ACCIONES EDITAR / ELIMINAR)
        // =====================================================================

        function escaparJs(str) {
            if (!str) return '';
            return String(str).split("'").join("\\'").split('"').join('&quot;');
        }

        function renderizarListaInventario(items) {
            const cont = document.getElementById('lista_inventario');
            if (!cont) return;
            if (!items || items.length === 0) {
                let msg = 'No hay activos registrados en este centro';
                if (FILTRO_TIPO_ACTIVO === 'equipos') msg = 'No hay equipos médicos registrados en este centro';
                if (FILTRO_TIPO_ACTIVO === 'muebles') msg = 'No hay muebles o activos de TI registrados en este centro';
                cont.innerHTML = `<div class="empty-state"><span>📦</span>${msg}</div>`;
                return;
            }

            let html = '';
            items.forEach(it => {
                const esEquipo = it._tipo !== 'MUEBLE';
                if (esEquipo) {
                    const st = (it.estado || 'Bueno').toLowerCase();
                    const badgeCls = st === 'bueno' ? 'status-bueno' : (st === 'regular' ? 'status-regular' : 'status-malo');
                    const cr = (it.criticidad || 'Media').toLowerCase();
                    const critCls = cr === 'alta' ? 'status-crit-alta' : (cr === 'media' ? 'status-crit-media' : 'status-crit-baja');

                    let actionsHtml = `<a href="/equipo/${encodeURIComponent(it.id)}" class="btn-card-view">📋 Ficha</a>`;
                    if (puede('Inventario', 'cambiar')) {
                        actionsHtml += `<button type="button" class="btn-card-edit" onclick="editarEquipo('${it.id}')">✎ Editar</button>`;
                    }
                    if (puede('Inventario', 'eliminar')) {
                        actionsHtml += `<button type="button" class="btn-card-del" onclick="eliminarRegistro('equipos', '${it.id}', '${escaparJs(it.nombre || it.id)}')">🗑️ Eliminar</button>`;
                    }

                    html += `
                    <div class="card-item" style="border-top: 3px solid #0284C7;">
                        <div class="card-item-header">
                            <span class="badge-af">${it.id}</span>
                            <div style="display:flex; gap:4px; align-items:center;">
                                <span class="badge-status" style="background:#E0F2FE; color:#0284C7; font-size:10px; font-weight:800;">🩺 EQUIPO</span>
                                <span class="badge-status ${critCls}">Crit: ${it.criticidad || 'Media'}</span>
                                <span class="badge-status ${badgeCls}">${it.estado || 'Bueno'}</span>
                            </div>
                        </div>
                        <div class="item-title">${it.nombre}</div>
                        <div class="item-subtitle">
                            <span>🏷️ ${it.marca || 'S/M'} ${it.modelo || ''}</span>
                            <span>•</span>
                            <span>📍 ${it.area || 'Sin Área'}</span>
                        </div>
                        ${it.persona_asignada ? `<div class="item-detail-row">👤 <strong>Responsable:</strong> ${it.persona_asignada} ${it.cargo_asignado ? `(${it.cargo_asignado})` : ''}</div>` : ''}
                        <div class="item-actions">
                            ${actionsHtml}
                        </div>
                    </div>`;
                } else {
                    let actionsHtml = '';
                    if (puede('Muebleria', 'cambiar')) {
                        actionsHtml += `<button type="button" class="btn-card-edit" onclick="editarMueble(${it.id})">✎ Editar</button>`;
                    }
                    if (puede('Muebleria', 'eliminar')) {
                        actionsHtml += `<button type="button" class="btn-card-del" onclick="eliminarRegistro('muebleria', ${it.id}, '${escaparJs(it.descripcion || it.tipo_activo)}')">🗑️ Eliminar</button>`;
                    }

                    html += `
                    <div class="card-item" style="border-top: 3px solid #D97706;">
                        <div class="card-item-header">
                            <span class="badge-af" style="color:#B45309; background:#FEF3C7; border-color:#FDE68A;">${it.codigo_sispam || it.id || 'MUEBLE'}</span>
                            <div style="display:flex; gap:4px; align-items:center;">
                                <span class="badge-status" style="background:#FEF3C7; color:#B45309; font-size:10px; font-weight:800;">🛋️ MUEBLE/TI</span>
                                <span class="badge-status status-bueno">${it.estado_conservacion || 'Bueno'}</span>
                            </div>
                        </div>
                        <div class="item-title">${it.descripcion || it.tipo_activo}</div>
                        <div class="item-subtitle">
                            <span>🏷️ ${it.marca || 'S/M'} ${it.modelo || ''}</span>
                            <span>•</span>
                            <span>Serie: ${it.serie || 'S/S'}</span>
                        </div>
                        <div class="item-detail-row">
                            📍 <strong>Ubicación:</strong> ${it.ubicacion || 'General'}
                            ${it.persona_asignada ? `<br>👤 <strong>Asignado:</strong> ${it.persona_asignada}` : ''}
                        </div>
                        ${actionsHtml ? `<div class="item-actions">${actionsHtml}</div>` : ''}
                    </div>`;
                }
            });
            cont.innerHTML = html;
        }

        function renderizarListaCatalogo(items) {
            const cont = document.getElementById('lista_catalogo');
            if (!cont) return;
            if (!items || items.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>🩺</span>No hay modelos en el catálogo</div>';
                return;
            }
            let html = '';
            items.forEach(c => {
                let actionsHtml = '';
                if (puede('Catalogo', 'cambiar')) {
                    actionsHtml += `<button type="button" class="btn-card-edit" onclick="editarCatalogo(${c.id})">✎ Editar</button>`;
                }
                if (puede('Catalogo', 'eliminar')) {
                    actionsHtml += `<button type="button" class="btn-card-del" onclick="eliminarRegistro('catalogo', ${c.id}, '${c.nombre}')">🗑️ Eliminar</button>`;
                }

                html += `
                <div class="card-item">
                    <div class="item-title">${c.nombre}</div>
                    <div class="item-subtitle">
                        <span>🏷️ ${c.marca || 'Genérico'} - ${c.modelo || 'Estándar'}</span>
                    </div>
                    ${c.area ? `<div class="item-detail-row">📍 <strong>Área Sugerida:</strong> ${c.area} ${c.piso ? `(${c.piso})` : ''}</div>` : ''}
                    ${actionsHtml ? `<div class="item-actions">${actionsHtml}</div>` : ''}
                </div>`;
            });
            cont.innerHTML = html;
        }

        function renderizarListaMuebles(items) {
            const cont = document.getElementById('lista_muebles');
            if (!cont) return;
            if (!items || items.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>🛋️</span>No hay activos de mueblería o TI</div>';
                return;
            }
            let html = '';
            items.forEach(m => {
                let actionsHtml = '';
                if (puede('Muebleria', 'cambiar')) {
                    actionsHtml += `<button type="button" class="btn-card-edit" onclick="editarMueble(${m.id})">✎ Editar</button>`;
                }
                if (puede('Muebleria', 'eliminar')) {
                    actionsHtml += `<button type="button" class="btn-card-del" onclick="eliminarRegistro('muebleria', ${m.id}, '${escaparJs(m.descripcion || m.tipo_activo)}')">🗑️ Eliminar</button>`;
                }

                const st = (m.estado_conservacion || m.estado || 'Bueno').toLowerCase();
                const badgeCls = st === 'bueno' ? 'status-bueno' : (st === 'regular' ? 'status-regular' : 'status-malo');

                html += `
                <div class="card-item">
                    <div class="card-item-header">
                        <span class="badge-af">${m.tipo_activo || 'ACTIVO'}</span>
                        <span class="badge-status ${badgeCls}">${m.estado_conservacion || 'Bueno'}</span>
                    </div>
                    <div class="item-title">${m.descripcion || m.tipo_activo}</div>
                    <div class="item-subtitle">
                        <span>🏷️ ${m.marca || ''} ${m.modelo || ''}</span>
                        <span>•</span>
                        <span>Serie: ${m.serie || 'S/C'}</span>
                    </div>
                    <div class="item-detail-row">
                        📍 <strong>Ubicación:</strong> ${m.ubicacion || 'General'}
                        ${m.persona_asignada ? `<br>👤 <strong>Asignado a:</strong> ${m.persona_asignada}` : ''}
                    </div>
                    ${actionsHtml ? `<div class="item-actions">${actionsHtml}</div>` : ''}
                </div>`;
            });
            cont.innerHTML = html;
        }

        function renderizarListaAreas(items) {
            const cont = document.getElementById('lista_areas');
            if (!cont) return;
            if (!items || items.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>📍</span>No hay áreas registradas en este centro</div>';
                return;
            }
            let html = '';
            items.forEach(a => {
                let actionsHtml = '';
                if (puede('Areas', 'cambiar')) {
                    actionsHtml += `<button type="button" class="btn-card-edit" onclick="editarArea(${a.id})">✎ Editar</button>`;
                }
                if (puede('Areas', 'eliminar')) {
                    actionsHtml += `<button type="button" class="btn-card-del" onclick="eliminarRegistro('areas', ${a.id}, '${a.nombre}')">🗑️ Eliminar</button>`;
                }

                html += `
                <div class="card-item">
                    <div class="card-item-header">
                        <div class="item-title">📍 ${a.nombre}</div>
                        ${a.piso ? `<span class="badge-af">${a.piso}</span>` : ''}
                    </div>
                    <div class="item-detail-row">
                        👤 <strong>Responsable:</strong> ${a.encargado || 'No asignado'}
                        ${a.cargo ? `<br>💼 <strong>Cargo:</strong> ${a.cargo}` : ''}
                        ${a.ci_encargado ? `<br>🆔 <strong>C.I.:</strong> ${a.ci_encargado}` : ''}
                        ${a.contacto ? `<br>📞 <strong>Contacto:</strong> ${a.contacto}` : ''}
                    </div>
                    ${actionsHtml ? `<div class="item-actions">${actionsHtml}</div>` : ''}
                </div>`;
            });
            cont.innerHTML = html;
        }

        function renderizarListaRepuestos(items) {
            const cont = document.getElementById('lista_repuestos');
            if (!cont) return;
            if (!items || items.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>🔧</span>No hay repuestos registrados</div>';
                return;
            }
            let html = '';
            items.forEach(r => {
                let actionsHtml = '';
                if (puede('Repuestos', 'cambiar')) {
                    actionsHtml += `<button type="button" class="btn-card-edit" onclick="editarRepuesto(${r.id})">✎ Editar</button>`;
                }
                if (puede('Repuestos', 'eliminar')) {
                    actionsHtml += `<button type="button" class="btn-card-del" onclick="eliminarRegistro('repuestos', ${r.id}, '${r.nombre_repuesto}')">🗑️ Eliminar</button>`;
                }

                html += `
                <div class="card-item">
                    <div class="card-item-header">
                        <span class="item-title">🔧 ${r.nombre_repuesto}</span>
                        <span class="badge-status status-bueno">${r.cantidad || 0} en Stock</span>
                    </div>
                    <div class="item-subtitle">
                        <span>🏷️ P/N: ${r.modelo_parte || 'S/C'}</span>
                        <span>•</span>
                        <span>Compatible: ${r.marca || ''} ${r.modelo || ''}</span>
                    </div>
                    <div class="item-detail-row">
                        📍 <strong>Ubicación:</strong> ${r.area || 'Almacén'} | <strong>Costo:</strong> ${parseFloat(r.costo || 0).toFixed(2)} Bs.
                    </div>
                    ${actionsHtml ? `<div class="item-actions">${actionsHtml}</div>` : ''}
                </div>`;
            });
            cont.innerHTML = html;
        }

        function renderizarListaHistorial(items) {
            const cont = document.getElementById('lista_historial');
            if (!cont) return;
            if (!items || items.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>📋</span>No hay intervenciones registradas</div>';
                return;
            }
            let html = '';
            items.forEach(h => {
                let actionsHtml = '';
                if (puede('Historial', 'cambiar')) {
                    actionsHtml += `<button type="button" class="btn-card-edit" onclick="editarIntervencion(${h.id})">✎ Editar</button>`;
                }
                if (puede('Historial', 'eliminar')) {
                    actionsHtml += `<button type="button" class="btn-card-del" onclick="eliminarRegistro('historial_intervenciones', ${h.id}, 'Intervención #${h.id}')">🗑️ Eliminar</button>`;
                }

                html += `
                <div class="card-item">
                    <div class="card-item-header">
                        <span class="badge-af">${h.equipo_id}</span>
                        <span class="badge-status status-bueno">${h.tipo || 'Mantenimiento'}</span>
                    </div>
                    <div class="item-title">${h.equipo_nombre || 'Equipo Médico'}</div>
                    <div class="item-subtitle">
                        <span>📅 ${h.fecha || ''}</span>
                        <span>•</span>
                        <span>👤 ${h.realizado_por || 'Técnico'}</span>
                    </div>
                    <div class="item-detail-row">
                        🛠️ <strong>Trabajo:</strong> ${h.trabajo || h.detalle || 'Sin detalle'}
                        ${h.repuesto_usado ? `<br>⚙️ <strong>Repuesto:</strong> ${h.repuesto_nombre} (${h.repuesto_cantidad || 1} un.)` : ''}
                    </div>
                    ${actionsHtml ? `<div class="item-actions">${actionsHtml}</div>` : ''}
                </div>`;
            });
            cont.innerHTML = html;
        }

        function renderizarListaCronograma(items) {
            const cont = document.getElementById('lista_cronograma');
            if (!cont) return;
            const prevs = (items || []).filter(i => (i.tipo || '').toLowerCase().includes('preventivo'));
            if (prevs.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>📅</span>No hay mantenimientos preventivos programados</div>';
                return;
            }
            let html = '';
            prevs.forEach(p => {
                html += `
                <div class="card-item">
                    <div class="card-item-header">
                        <span class="badge-af">${p.equipo_id}</span>
                        <span class="badge-status status-regular">Preventivo</span>
                    </div>
                    <div class="item-title">${p.equipo_nombre || 'Equipo Médico'}</div>
                    <div class="item-subtitle"><span>📅 Fecha: ${p.fecha || ''}</span></div>
                    <div class="item-detail-row">
                        📍 <strong>Área:</strong> ${p.equipo_area || 'General'}
                        <br>👤 <strong>Responsable:</strong> ${p.realizado_por || 'Técnico Asignado'}
                    </div>
                </div>`;
            });
            cont.innerHTML = html;
        }

        function renderizarSedesDirectorio() {
            const cont = document.getElementById('lista_sedes');
            if (!cont) return;
            const redes = SEDES_DATA.redes || [];
            const centros = SEDES_DATA.centros || [];
            if (centros.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>🏥</span>No hay centros cargados</div>';
                return;
            }
            let html = '';
            centros.forEach(c => {
                const rObj = redes.find(r => r.id === c.red_salud_id);
                html += `
                <div class="card-item">
                    <div class="card-item-header">
                        <span class="badge-af">CENTRO</span>
                        <span class="badge-status status-bueno">${rObj ? rObj.nombre : 'Red GAMLP'}</span>
                    </div>
                    <div class="item-title">${c.nombre}</div>
                    <div class="item-detail-row">
                        🏥 <strong>Nivel:</strong> ${c.nivel || 'Primer Nivel'}
                        ${c.direccion ? `<br>📍 <strong>Dirección:</strong> ${c.direccion}` : ''}
                        ${c.telefono ? `<br>📞 <strong>Tel:</strong> ${c.telefono}` : ''}
                    </div>
                </div>`;
            });
            cont.innerHTML = html;
        }

        function renderizarListaUsuarios(items) {
            const cont = document.getElementById('lista_usuarios');
            if (!cont) return;
            if (!items || items.length === 0) {
                cont.innerHTML = '<div class="empty-state"><span>👥</span>No hay usuarios registrados</div>';
                return;
            }
            let html = '';
            items.forEach(u => {
                const p = u.permisos || {};
                let countVer = 0;
                MODULOS_SISTEMA.forEach(([k]) => {
                    if (p[k] && p[k].ver) countVer++;
                });
                const rolDisplay = (u.rol === 'jefe' || u.rol === 'administrador') ? 'Administrador / Jefe' : (u.rol || 'Técnico');
                const badgeCls = (u.rol === 'jefe' || u.rol === 'administrador') ? 'status-bueno' : 'status-regular';

                let actionsHtml = `<button class="btn-card-edit" onclick="abrirModalEditarUsuario('${u.nombre_usuario}')">⚙️ Permisos</button>`;
                if (u.nombre_usuario !== 'admin' && u.nombre_usuario !== 'godhead') {
                    actionsHtml += `<button class="btn-card-del" onclick="eliminarRegistro('usuarios', '${u.nombre_usuario}', '${u.nombre_completo || u.nombre_usuario}')">🗑️ Eliminar</button>`;
                }

                html += `
                <div class="card-item">
                    <div class="card-item-header">
                        <span class="badge-af">${u.nombre_usuario}</span>
                        <span class="badge-status ${badgeCls}">${rolDisplay}</span>
                    </div>
                    <div class="item-title">${u.nombre_completo || u.nombre_usuario}</div>
                    <div class="item-subtitle">
                        <span>Pestañas activas: ${countVer} / ${MODULOS_SISTEMA.length}</span>
                    </div>
                    <div class="item-actions">
                        ${actionsHtml}
                    </div>
                </div>`;
            });
            cont.innerHTML = html;
        }

        // =====================================================================
        // FILTROS EN TIEMPO REAL
        // =====================================================================

        function setFiltroTipoActivo(tipo) {
            FILTRO_TIPO_ACTIVO = tipo;
            ['todo', 'equipos', 'muebles'].forEach(t => {
                const btn = document.getElementById(`pill_inv_${t}`);
                if (btn) {
                    if (t === tipo) btn.classList.add('active');
                    else btn.classList.remove('active');
                }
            });
            aplicarFiltroInventario();
        }

        function actualizarContadoresInventario() {
            const numEq = (LISTA_EQUIPOS || []).length;
            const numMu = (LISTA_MUEBLES || []).length;
            const numTodo = numEq + numMu;

            const cTodo = document.getElementById('cnt_inv_todo');
            const cEq = document.getElementById('cnt_inv_equipos');
            const cMu = document.getElementById('cnt_inv_muebles');

            if (cTodo) cTodo.textContent = numTodo;
            if (cEq) cEq.textContent = numEq;
            if (cMu) cMu.textContent = numMu;
        }

        function aplicarFiltroInventario() {
            const q = (document.getElementById('busq_inventario') ? document.getElementById('busq_inventario').value : '').toLowerCase().trim();
            let items = [];

            if (FILTRO_TIPO_ACTIVO === 'todo' || FILTRO_TIPO_ACTIVO === 'equipos') {
                const eqs = (LISTA_EQUIPOS || []).map(e => ({ ...e, _tipo: 'EQUIPO' }));
                items = items.concat(eqs);
            }
            if (FILTRO_TIPO_ACTIVO === 'todo' || FILTRO_TIPO_ACTIVO === 'muebles') {
                const mus = (LISTA_MUEBLES || []).map(m => ({ ...m, _tipo: 'MUEBLE' }));
                items = items.concat(mus);
            }

            if (q) {
                items = items.filter(it => {
                    const idStr = String(it.id || it.codigo_sispam || '').toLowerCase();
                    const nomStr = String(it.nombre || it.descripcion || it.tipo_activo || '').toLowerCase();
                    const marStr = String(it.marca || '').toLowerCase();
                    const modStr = String(it.modelo || '').toLowerCase();
                    const areStr = String(it.area || it.ubicacion || '').toLowerCase();
                    const serStr = String(it.numero_serie || it.serie || '').toLowerCase();
                    const perStr = String(it.persona_asignada || '').toLowerCase();
                    return idStr.includes(q) || nomStr.includes(q) || marStr.includes(q) || modStr.includes(q) || areStr.includes(q) || serStr.includes(q) || perStr.includes(q);
                });
            }

            renderizarListaInventario(items);
        }

        function filtrarListaInventario() {
            aplicarFiltroInventario();
        }

        function filtrarListaCatalogo() {
            const q = document.getElementById('busq_catalogo').value.toLowerCase().trim();
            const filt = LISTA_CATALOGO.filter(c => 
                (c.nombre || '').toLowerCase().includes(q) ||
                (c.marca || '').toLowerCase().includes(q) ||
                (c.modelo || '').toLowerCase().includes(q)
            );
            renderizarListaCatalogo(filt);
        }

        function filtrarListaMuebles() {
            const q = (document.getElementById('busq_muebles') ? document.getElementById('busq_muebles').value : '').toLowerCase().trim();
            const filt = (LISTA_MUEBLES || []).filter(m => {
                const descStr = String(m.descripcion || m.tipo_activo || '').toLowerCase();
                const marStr = String(m.marca || '').toLowerCase();
                const modStr = String(m.modelo || '').toLowerCase();
                const serStr = String(m.serie || '').toLowerCase();
                const ubiStr = String(m.ubicacion || '').toLowerCase();
                const perStr = String(m.persona_asignada || '').toLowerCase();
                const sisStr = String(m.codigo_sispam || '').toLowerCase();
                const berStr = String(m.bertin || '').toLowerCase();
                const sapStr = String(m.sapm || '').toLowerCase();
                return descStr.includes(q) || marStr.includes(q) || modStr.includes(q) ||
                       serStr.includes(q) || ubiStr.includes(q) || perStr.includes(q) ||
                       sisStr.includes(q) || berStr.includes(q) || sapStr.includes(q);
            });
            renderizarListaMuebles(filt);
        }

        function filtrarListaAreas() {
            const q = document.getElementById('busq_areas').value.toLowerCase().trim();
            const filt = LISTA_AREAS.filter(a => 
                (a.nombre || '').toLowerCase().includes(q) ||
                (a.encargado || '').toLowerCase().includes(q) ||
                (a.cargo || '').toLowerCase().includes(q)
            );
            renderizarListaAreas(filt);
        }

        function filtrarListaRepuestos() {
            const q = document.getElementById('busq_repuestos').value.toLowerCase().trim();
            const filt = LISTA_REPUESTOS.filter(r => 
                (r.nombre_repuesto || '').toLowerCase().includes(q) ||
                (r.modelo_parte || '').toLowerCase().includes(q) ||
                (r.marca || '').toLowerCase().includes(q)
            );
            renderizarListaRepuestos(filt);
        }

        function filtrarListaHistorial() {
            const q = document.getElementById('busq_historial').value.toLowerCase().trim();
            const filt = LISTA_HISTORIAL.filter(h => 
                (h.equipo_id || '').toLowerCase().includes(q) ||
                (h.equipo_nombre || '').toLowerCase().includes(q) ||
                (h.trabajo || '').toLowerCase().includes(q) ||
                (h.realizado_por || '').toLowerCase().includes(q)
            );
            renderizarListaHistorial(filt);
        }

        function filtrarListaCronograma() {
            const q = document.getElementById('busq_cronograma').value.toLowerCase().trim();
            const filt = LISTA_HISTORIAL.filter(h => 
                (h.equipo_id || '').toLowerCase().includes(q) ||
                (h.equipo_nombre || '').toLowerCase().includes(q)
            );
            renderizarListaCronograma(filt);
        }

        function filtrarListaSedes() {
            const q = document.getElementById('busq_sedes').value.toLowerCase().trim();
            const centros = (SEDES_DATA.centros || []).filter(c => 
                (c.nombre || '').toLowerCase().includes(q) ||
                (c.direccion || '').toLowerCase().includes(q)
            );
            renderizarSedesDirectorio();
        }

        function filtrarListaUsuarios() {
            const q = document.getElementById('busq_usuarios').value.toLowerCase().trim();
            const filt = LISTA_USUARIOS.filter(u => 
                (u.nombre_usuario || '').toLowerCase().includes(q) ||
                (u.nombre_completo || '').toLowerCase().includes(q) ||
                (u.rol || '').toLowerCase().includes(q)
            );
            renderizarListaUsuarios(filt);
        }

        // =====================================================================
        // DISPARADORES DE CREACIÓN / EDICIÓN EN MODALES
        // =====================================================================

        const CRITERIOS_GAMLP = [
            "Intercambiabilidad",
            "Función Clínica",
            "Frecuencia de Uso",
            "Impacto en el Servicio",
            "Mantenibilidad",
            "Historial de Fallas",
            "Complejidad Tecnológica",
            "Valor de Compra",
            "Exigencia Normativa",
            "Seguridad Operacional",
            "Vulnerabilidad Ambiental",
            "Riesgo a Explosiones",
            "Edad del Equipo"
        ];

        function inicializarCriteriosUI() {
            const cont = document.getElementById('contenedor_filas_criterios');
            if (!cont || cont.children.length > 0) return;
            let html = '';
            CRITERIOS_GAMLP.forEach((crit, i) => {
                html += `
                <div class="crit-row">
                    <span>${i + 1}. ${crit}</span>
                    <div class="crit-radios">
                        <label><input type="radio" name="crit_${i}" value="1" onchange="recalcularCriticidad()"> 1</label>
                        <label><input type="radio" name="crit_${i}" value="2" onchange="recalcularCriticidad()"> 2</label>
                        <label><input type="radio" name="crit_${i}" value="3" onchange="recalcularCriticidad()"> 3</label>
                    </div>
                </div>`;
            });
            cont.innerHTML = html;
        }

        function recalcularCriticidad() {
            let total = 0;
            let count = 0;
            for (let i = 0; i < 13; i++) {
                const radios = document.getElementsByName('crit_' + i);
                for (let r of radios) {
                    if (r.checked) {
                        total += parseInt(r.value);
                        count++;
                        break;
                    }
                }
            }
            const lbl = document.getElementById('lbl_puntaje_criterios');
            const badge = document.getElementById('badge_criticidad_calculada');
            const hiddenInp = document.getElementById('modal_eq_criticidad');
            const lblConteo = document.getElementById('lbl_conteo_evaluados');

            let crit = 'Media';
            if (count > 0) {
                if (total >= 30) {
                    crit = 'Alta';
                } else if (total >= 20) {
                    crit = 'Media';
                } else {
                    crit = 'Baja';
                }
            } else if (hiddenInp && hiddenInp.value) {
                crit = hiddenInp.value;
            }

            if (hiddenInp) hiddenInp.value = crit;

            if (badge) {
                badge.textContent = crit;
                if (crit === 'Alta') {
                    badge.style.background = '#FEE2E2';
                    badge.style.color = '#DC2626';
                    badge.style.borderColor = '#FCA5A5';
                } else if (crit === 'Media') {
                    badge.style.background = '#FEF3C7';
                    badge.style.color = '#D97706';
                    badge.style.borderColor = '#FCD34D';
                } else {
                    badge.style.background = '#DCFCE7';
                    badge.style.color = '#16A34A';
                    badge.style.borderColor = '#86EFAC';
                }
            }

            if (lbl) {
                lbl.textContent = count > 0 ? `Puntaje: ${total} / 39 pts` : `Puntaje: 0 / 39 pts`;
            }
            if (lblConteo) {
                lblConteo.textContent = `${count} / 13`;
                lblConteo.style.color = count === 13 ? '#16A34A' : '#475569';
            }
        }

        function toggleModalidadAdq(val) {
            const box = document.getElementById('box_costo_equipo');
            if (!box) return;
            if (val === 'Compra') {
                box.style.display = 'block';
            } else {
                box.style.display = 'none';
                const inp = document.getElementById('modal_eq_costo');
                if (inp) inp.value = '0';
            }
        }

        function toggleGarantia(val) {
            const box = document.getElementById('box_fechas_garantia');
            if (!box) return;
            if (val === 'Con Garantía') {
                box.style.display = 'block';
                actualizarRestanteGarantia();
            } else {
                box.style.display = 'none';
                const badge = document.getElementById('badge_restante_garantia');
                if (badge) badge.textContent = '';
            }
        }

        function actualizarRestanteGarantia() {
            const rCon = document.querySelector('input[name="tiene_garantia"][value="Con Garantía"]');
            const badge = document.getElementById('badge_restante_garantia');
            if (!badge || !rCon || !rCon.checked) return;
            const finVal = document.getElementById('modal_eq_gar_fin').value;
            if (!finVal) {
                badge.textContent = '';
                return;
            }
            const hoy = new Date();
            hoy.setHours(0,0,0,0);
            const dFin = new Date(finVal + 'T00:00:00');
            if (dFin < hoy) {
                badge.innerHTML = '<span style="color:#EF4444;">⚠️ Garantía Vencida</span>';
            } else {
                const diffMs = dFin - hoy;
                const dias = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
                const meses = Math.floor(dias / 30);
                const diasRest = dias % 30;
                let txt = 'Vigente: ';
                if (meses > 0) txt += `${meses} mes(es) y `;
                txt += `${diasRest} día(s) restante(s)`;
                badge.innerHTML = `<span style="color:#16A34A;">✅ ${txt}</span>`;
            }
        }

        function toggleSeccion(boxId, btn) {
            const box = document.getElementById(boxId);
            if (!box) return;
            const isHidden = box.style.display === 'none' || !box.style.display;
            if (isHidden) {
                box.style.display = 'block';
                if (btn) {
                    const arr = btn.querySelector('.arrow-indicator');
                    if (arr) arr.textContent = '▲';
                    const lbl = btn.querySelector('.lbl-btn-acc');
                    if (lbl) lbl.textContent = 'Ocultar Detalles';
                }
            } else {
                box.style.display = 'none';
                if (btn) {
                    const arr = btn.querySelector('.arrow-indicator');
                    if (arr) arr.textContent = '▼';
                    const lbl = btn.querySelector('.lbl-btn-acc');
                    if (lbl) lbl.textContent = 'Mostrar Detalles (Excel)';
                }
            }
        }

        async function abrirModalRegistroEquipo() {
            inicializarCriteriosUI();
            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            document.getElementById('modal_eq_title').textContent = '✚ Registrar Equipo Médico';
            document.getElementById('display_af_modal').textContent = 'CALCULANDO...';
            document.getElementById('modal_eq_id_af').value = '';
            document.getElementById('modal_eq_es_edicion').value = "0";

            // Sede context y modelo
            inicializarSelectoresSedesModal('modal_eq_red', 'modal_eq_centro', red, centro);
            if (document.getElementById('modal_eq_catalogo_input')) document.getElementById('modal_eq_catalogo_input').value = '';
            if (document.getElementById('modal_eq_catalogo')) document.getElementById('modal_eq_catalogo').value = '';

            // Limpiar campos Sección 1
            document.getElementById('modal_eq_sector').value = 'SALUD';
            document.getElementById('modal_eq_servicio').value = '';
            document.getElementById('modal_eq_persona').value = '';
            document.getElementById('modal_eq_cargo').value = '';
            document.getElementById('modal_eq_ci').value = '';
            document.getElementById('modal_eq_nombre').value = '';
            document.getElementById('modal_eq_marca').value = '';
            document.getElementById('modal_eq_modelo').value = '';
            document.getElementById('modal_eq_serie').value = '';
            document.getElementById('modal_eq_estado').value = 'Bueno';
            document.getElementById('modal_eq_sispam').value = '';
            document.getElementById('modal_eq_bertin').value = '';
            document.getElementById('modal_eq_sapm').value = '';

            // Auto-llenar datos del área seleccionada
            alCambiarAreaModal();

            // Limpiar campos Sección 2
            document.getElementById('modal_eq_procedencia').value = '';
            document.getElementById('modal_eq_fabricante').value = '';
            document.getElementById('modal_eq_proveedor').value = '';
            document.getElementById('modal_eq_anio_fab').value = '';
            document.getElementById('modal_eq_fecha_instalacion').value = new Date().toISOString().slice(0, 10);
            const rCompra = document.querySelector('input[name="modalidad_adq"][value="Compra"]');
            if (rCompra) rCompra.checked = true;
            toggleModalidadAdq('Compra');
            document.getElementById('modal_eq_costo').value = '0';

            // Limpiar campos Sección 3
            const rFijo = document.querySelector('input[name="tipo_movilidad"][value="Fijo"]');
            if (rFijo) rFijo.checked = true;
            const rSinGar = document.querySelector('input[name="tiene_garantia"][value="Sin Garantía"]');
            if (rSinGar) rSinGar.checked = true;
            toggleGarantia('Sin Garantía');
            document.getElementById('modal_eq_gar_inicio').value = '';
            document.getElementById('modal_eq_gar_fin').value = '';
            document.getElementById('badge_restante_garantia').textContent = '';

            // Reset chips de energía: Eléctrica por defecto activa
            document.querySelectorAll('#form_equipo_movil .chip-btn').forEach(ch => {
                if (ch.getAttribute('data-f') === 't_elec') ch.classList.add('active');
                else ch.classList.remove('active');
            });

            // Limpiar campos Sección 4
            document.getElementById('modal_eq_criticidad').value = 'Media';
            for (let i = 0; i < 13; i++) {
                const radios = document.getElementsByName('crit_' + i);
                for (let r of radios) r.checked = false;
            }
            recalcularCriticidad();

            // Limpiar foto
            quitarFotoMovil();

            // Limpiar campos Sección 6
            document.getElementById('modal_eq_voltaje').value = '';
            document.getElementById('modal_eq_corriente').value = '';
            document.getElementById('modal_eq_potencia').value = '';
            document.getElementById('modal_eq_vida_util').value = '';
            document.getElementById('modal_eq_peso').value = '';
            document.getElementById('modal_eq_dimensiones').value = '';
            document.getElementById('modal_eq_bateria').value = '';
            document.getElementById('modal_eq_software').value = '';
            document.getElementById('modal_eq_gases').value = '';
            document.getElementById('modal_eq_contexto').value = '';
            document.getElementById('modal_eq_funciones').value = '';
            document.getElementById('modal_eq_acciones_prev').value = '';
            document.getElementById('modal_eq_insumos').value = '';
            document.getElementById('modal_eq_fallas_comunes').value = '';
            document.getElementById('modal_eq_causas_fallo').value = '';
            document.getElementById('modal_eq_efectos_fallo').value = '';
            document.getElementById('modal_eq_acciones_corr').value = '';
            document.getElementById('box_datos_adicionales').style.display = 'none';

            // Observaciones
            document.getElementById('modal_eq_obs').value = '';
            document.getElementById('btn_guardar_eq').textContent = '💾 Guardar Equipo Médico';

            abrirModal('modal_equipo');

            // Calcular código AF y cargar áreas del centro seleccionado
            await alCambiarCentroModalEquipo();
        }

        async function editarEquipo(id) {
            inicializarCriteriosUI();
            const eq = LISTA_EQUIPOS.find(e => String(e.id) === String(id));
            if (!eq) return;

            document.getElementById('modal_eq_title').textContent = `✎ Modificar Equipo [${eq.id}]`;
            document.getElementById('display_af_modal').textContent = eq.id;
            document.getElementById('modal_eq_id_af').value = eq.id;
            document.getElementById('modal_eq_es_edicion').value = "1";

            // Sección 1: Identificación y Ubicación
            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            inicializarSelectoresSedesModal('modal_eq_red', 'modal_eq_centro', eq.red_salud_nombre || red, eq.centro_salud_nombre || centro);
            await cargarAreasGlobal(eq.centro_salud_nombre || centro, eq.red_salud_nombre || red);
            if (document.getElementById('modal_eq_catalogo_input')) document.getElementById('modal_eq_catalogo_input').value = '';
            if (document.getElementById('modal_eq_catalogo')) document.getElementById('modal_eq_catalogo').value = '';

            document.getElementById('modal_eq_sector').value = eq.sector_actual || 'SALUD';
            document.getElementById('modal_eq_servicio').value = eq.servicio || '';
            const selArea = document.getElementById('modal_eq_area');
            if (eq.area) {
                const match = obtenerAreaObj(eq.area);
                if (match) {
                    selArea.value = formatearAreaNombre(match);
                    if (document.getElementById('modal_eq_piso')) document.getElementById('modal_eq_piso').value = match.piso || '';
                } else {
                    selArea.value = eq.area;
                }
            }
            document.getElementById('modal_eq_persona').value = eq.persona_asignada || '';
            document.getElementById('modal_eq_cargo').value = eq.cargo_asignado || '';
            document.getElementById('modal_eq_ci').value = eq.ci_asignado || '';
            document.getElementById('modal_eq_nombre').value = eq.nombre || '';
            document.getElementById('modal_eq_marca').value = eq.marca || '';
            document.getElementById('modal_eq_modelo').value = eq.modelo || '';
            document.getElementById('modal_eq_serie').value = (eq.numero_serie && eq.numero_serie !== 'S/C') ? eq.numero_serie : '';
            document.getElementById('modal_eq_estado').value = eq.estado || 'Bueno';
            document.getElementById('modal_eq_sispam').value = (eq.codigo_sispam && eq.codigo_sispam !== 'S/C') ? eq.codigo_sispam : '';
            document.getElementById('modal_eq_bertin').value = (eq.bertin && eq.bertin !== 'S/C') ? eq.bertin : '';
            document.getElementById('modal_eq_sapm').value = (eq.sapm && eq.sapm !== 'S/C') ? eq.sapm : '';

            // Sección 2: Adquisición
            document.getElementById('modal_eq_procedencia').value = eq.procedencia || '';
            document.getElementById('modal_eq_fabricante').value = eq.fabricante || '';
            document.getElementById('modal_eq_proveedor').value = eq.proveedor || '';
            document.getElementById('modal_eq_anio_fab').value = eq.anio_fab || '';
            document.getElementById('modal_eq_fecha_instalacion').value = (eq.fecha_adquisicion || eq.fecha_instalacion || '').slice(0, 10);
            
            let modAdq = 'Compra';
            if (eq.a_como) modAdq = 'Comodato';
            else if (eq.a_don) modAdq = 'Donación';
            const radMod = document.querySelector(`input[name="modalidad_adq"][value="${modAdq}"]`);
            if (radMod) radMod.checked = true;
            toggleModalidadAdq(modAdq);
            document.getElementById('modal_eq_costo').value = eq.costo || '0';

            // Sección 3: Especificaciones y Garantía
            const chipsMap = {
                't_elec': eq.t_elec,
                't_elco': eq.t_elco,
                't_mec': eq.t_mec,
                't_hid': eq.t_hid,
                't_neu': eq.t_neu,
                't_vap': eq.t_vap
            };
            for (let k in chipsMap) {
                const btn = document.querySelector(`.chip-btn[data-f="${k}"]`);
                if (btn) {
                    if (chipsMap[k]) btn.classList.add('active');
                    else btn.classList.remove('active');
                }
            }

            let mov = 'Fijo';
            if (eq.te_mov) mov = 'Móvil';
            else if (eq.te_por) mov = 'Portátil';
            const radMov = document.querySelector(`input[name="tipo_movilidad"][value="${mov}"]`);
            if (radMov) radMov.checked = true;

            const esGar = (eq.garantia === 'Con Garantía' || eq.garantia === 'Sí');
            const valGar = esGar ? 'Con Garantía' : 'Sin Garantía';
            const radGar = document.querySelector(`input[name="tiene_garantia"][value="${valGar}"]`);
            if (radGar) radGar.checked = true;
            toggleGarantia(valGar);
            if (esGar) {
                document.getElementById('modal_eq_gar_inicio').value = (eq.fecha_inicio_garantia || '').slice(0, 10);
                document.getElementById('modal_eq_gar_fin').value = (eq.fecha_vencimiento_garantia || '').slice(0, 10);
                actualizarRestanteGarantia();
            }

            // Sección 4: Criticidad y Criterios
            document.getElementById('modal_eq_criticidad').value = eq.criticidad || 'Media';
            for (let i = 0; i < 13; i++) {
                const radios = document.getElementsByName('crit_' + i);
                for (let r of radios) r.checked = false;
            }
            let catDet = eq.categorizacion_detalle;
            if (typeof catDet === 'string' && catDet.trim()) {
                try { catDet = JSON.parse(catDet); } catch(e) { catDet = []; }
            }
            if (Array.isArray(catDet) && catDet.length > 0) {
                catDet.forEach((val, i) => {
                    if (i < 13 && val) {
                        const r = document.querySelector(`input[name="crit_${i}"][value="${val}"]`);
                        if (r) r.checked = true;
                    }
                });
            }
            recalcularCriticidad();

            // Sección 5: Foto
            if (eq.foto) {
                document.getElementById('foto_base64').value = eq.foto;
                document.getElementById('img_preview').src = eq.foto;
                document.getElementById('foto_preview_box').style.display = 'block';
            } else {
                quitarFotoMovil();
            }

            // Sección 6: Datos Técnicos y Contexto
            document.getElementById('modal_eq_voltaje').value = eq.voltaje || '';
            document.getElementById('modal_eq_corriente').value = eq.corriente || '';
            document.getElementById('modal_eq_potencia').value = eq.potencia || '';
            document.getElementById('modal_eq_vida_util').value = eq.vida_util || eq.temperatura || '';
            document.getElementById('modal_eq_peso').value = eq.peso || '';
            document.getElementById('modal_eq_dimensiones').value = eq.dimensiones || '';
            document.getElementById('modal_eq_bateria').value = eq.bateria_respaldo || eq.resolucion || '';
            document.getElementById('modal_eq_software').value = eq.version_software || eq.humedad || '';
            document.getElementById('modal_eq_gases').value = eq.suministro_gases || '';
            document.getElementById('modal_eq_contexto').value = eq.contexto_operacional || '';
            document.getElementById('modal_eq_funciones').value = eq.funciones_equipo || '';
            document.getElementById('modal_eq_acciones_prev').value = eq.acciones_preventivas || '';
            document.getElementById('modal_eq_insumos').value = eq.acciones_falla || '';
            document.getElementById('modal_eq_fallas_comunes').value = eq.fallas_funcionales || '';
            document.getElementById('modal_eq_causas_fallo').value = eq.causas_fallo || '';
            document.getElementById('modal_eq_efectos_fallo').value = eq.efectos_fallo || '';
            document.getElementById('modal_eq_acciones_corr').value = eq.efecto_entorno || '';

            // Observaciones
            document.getElementById('modal_eq_obs').value = eq.observaciones || '';

            document.getElementById('btn_guardar_eq').textContent = '💾 Actualizar Equipo Médico';
            abrirModal('modal_equipo');
        }

        async function abrirModalCatalogo() {
            document.getElementById('modal_cat_title').textContent = '🩺 Añadir Modelo al Catálogo';
            document.getElementById('cat_id').value = '';
            document.getElementById('cat_nombre').value = '';
            document.getElementById('cat_marca').value = '';
            document.getElementById('cat_modelo').value = '';
            document.getElementById('cat_piso').value = '';
            document.getElementById('btn_guardar_cat').textContent = '💾 Guardar en Catálogo Central';

            const inpManual = document.getElementById('cat_area_manual');
            const selArea = document.getElementById('cat_area');
            const btnToggle = document.getElementById('btn_toggle_cat_area');
            if (inpManual) { inpManual.style.display = 'none'; inpManual.value = ''; }
            if (selArea) selArea.style.display = 'block';
            if (btnToggle) btnToggle.textContent = '✏️ Escribir manual';

            await poblarSelectorAreasCatalogo();
            abrirModal('modal_catalogo');
        }

        async function editarCatalogo(id) {
            const c = LISTA_CATALOGO.find(item => String(item.id) === String(id));
            if (!c) return;
            document.getElementById('modal_cat_title').textContent = `✎ Modificar Modelo [${c.nombre}]`;
            document.getElementById('cat_id').value = c.id;
            document.getElementById('cat_nombre').value = c.nombre || '';
            document.getElementById('cat_marca').value = c.marca || '';
            document.getElementById('cat_modelo').value = c.modelo || '';
            document.getElementById('btn_guardar_cat').textContent = '💾 Actualizar Modelo';

            const inpManual = document.getElementById('cat_area_manual');
            const selArea = document.getElementById('cat_area');
            const btnToggle = document.getElementById('btn_toggle_cat_area');
            if (inpManual) { inpManual.style.display = 'none'; inpManual.value = ''; }
            if (selArea) selArea.style.display = 'block';
            if (btnToggle) btnToggle.textContent = '✏️ Escribir manual';

            await poblarSelectorAreasCatalogo(c.area || '', c.piso || '');
            abrirModal('modal_catalogo');
        }

        function abrirModalMueble() {
            document.getElementById('modal_mue_title').textContent = '🛋️ Registrar Activo Fijo (Mueblería / TI)';
            document.getElementById('mue_id').value = '';

            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            inicializarSelectoresSedesModal('mue_red', 'mue_centro', red, centro);

            document.getElementById('mue_tipo').value = '';
            document.getElementById('mue_desc').value = '';
            document.getElementById('mue_marca').value = '';
            document.getElementById('mue_modelo').value = '';
            document.getElementById('mue_serie').value = '';
            document.getElementById('mue_sispam').value = '';
            document.getElementById('mue_bertin').value = '';
            document.getElementById('mue_sapm').value = '';
            document.getElementById('mue_transaccion').value = 'Asignacion 2026';
            document.getElementById('mue_fecha_asig').value = new Date().toISOString().slice(0, 10);
            document.getElementById('mue_persona').value = '';
            document.getElementById('mue_cargo').value = '';
            document.getElementById('mue_ci').value = '';
            document.getElementById('mue_estado').value = 'Bueno';
            document.getElementById('mue_obs').value = '';
            const nomUser = (USUARIO_ACTUAL.nombre_completo || USUARIO_ACTUAL.nombre_usuario || '').trim();
            if (document.getElementById('mue_tecnico')) document.getElementById('mue_tecnico').value = nomUser;
            document.getElementById('btn_guardar_mue').textContent = '💾 Guardar Activo Fijo';

            abrirModal('modal_mueble');

            // Auto-llenar datos del área seleccionada
            alCambiarCentroModalMueble();
        }

        async function editarMueble(id) {
            const m = LISTA_MUEBLES.find(item => String(item.id) === String(id));
            if (!m) return;
            document.getElementById('modal_mue_title').textContent = `✎ Modificar Activo [${m.descripcion || m.tipo_activo}]`;
            document.getElementById('mue_id').value = m.id;

            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            inicializarSelectoresSedesModal('mue_red', 'mue_centro', m.direccion_administrativa || red, m.unidad_organizacional || centro);
            await cargarAreasGlobal(m.unidad_organizacional || centro, m.direccion_administrativa || red);

            document.getElementById('mue_tipo').value = m.tipo_activo || '';
            document.getElementById('mue_sector').value = m.sector_actual || 'SALUD';
            document.getElementById('mue_desc').value = m.descripcion || '';
            document.getElementById('mue_marca').value = m.marca || '';
            document.getElementById('mue_modelo').value = m.modelo || '';
            document.getElementById('mue_serie').value = (m.serie && m.serie !== 'S/C') ? m.serie : '';
            document.getElementById('mue_sispam').value = (m.codigo_sispam && m.codigo_sispam !== 'S/C') ? m.codigo_sispam : '';
            document.getElementById('mue_bertin').value = (m.bertin && m.bertin !== 'S/C') ? m.bertin : '';
            document.getElementById('mue_sapm').value = (m.sapm && m.sapm !== 'S/C') ? m.sapm : '';
            document.getElementById('mue_transaccion').value = m.detalle_transaccion || 'Asignacion 2026';
            document.getElementById('mue_fecha_asig').value = (m.fecha_asignacion || '').slice(0, 10);
            
            if (m.ubicacion) {
                const match = obtenerAreaObj(m.ubicacion);
                if (match) {
                    document.getElementById('mue_area').value = formatearAreaNombre(match);
                } else {
                    document.getElementById('mue_area').value = m.ubicacion;
                }
            }
            document.getElementById('mue_persona').value = m.persona_asignada || '';
            document.getElementById('mue_cargo').value = m.cargo_asignado || '';
            document.getElementById('mue_ci').value = m.ci_asignado || '';
            document.getElementById('mue_estado').value = m.estado_conservacion || 'Bueno';
            document.getElementById('mue_obs').value = m.observaciones_de_asignacion || '';
            const nomUserEdit = (USUARIO_ACTUAL.nombre_completo || USUARIO_ACTUAL.nombre_usuario || '').trim();
            if (document.getElementById('mue_tecnico')) {
                document.getElementById('mue_tecnico').value = m.tecnico_inventareador || m.tecnico || nomUserEdit;
            }
            document.getElementById('btn_guardar_mue').textContent = '💾 Actualizar Activo Fijo';
            abrirModal('modal_mueble');
        }

        function abrirModalArea() {
            document.getElementById('modal_area_title').textContent = '📍 Añadir Nueva Área al Centro';
            document.getElementById('area_id').value = '';
            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            inicializarSelectoresSedesModal('area_red', 'area_centro', red, centro);
            document.getElementById('area_nom').value = '';
            document.getElementById('area_piso').value = '';
            document.getElementById('area_encargado').value = '';
            document.getElementById('area_cargo').value = '';
            document.getElementById('area_ci').value = '';
            document.getElementById('area_contacto').value = '';
            document.getElementById('btn_guardar_area').textContent = '💾 Guardar Área en este Centro';
            abrirModal('modal_area');
        }

        function editarArea(id) {
            const a = LISTA_AREAS.find(item => String(item.id) === String(id));
            if (!a) return;
            document.getElementById('modal_area_title').textContent = `✎ Modificar Área [${a.nombre}]`;
            document.getElementById('area_id').value = a.id;
            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            inicializarSelectoresSedesModal('area_red', 'area_centro', a.red_salud_nombre || red, a.centro_salud_nombre || centro);
            document.getElementById('area_nom').value = a.nombre || '';
            document.getElementById('area_piso').value = a.piso || '';
            document.getElementById('area_encargado').value = a.encargado || '';
            document.getElementById('area_cargo').value = a.cargo || '';
            document.getElementById('area_ci').value = a.ci_encargado || '';
            document.getElementById('area_contacto').value = a.contacto || '';
            document.getElementById('btn_guardar_area').textContent = '💾 Actualizar Área';
            abrirModal('modal_area');
        }

        function abrirModalRepuesto() {
            document.getElementById('modal_rep_title').textContent = '🔧 Registrar Repuesto en Stock';
            document.getElementById('rep_id').value = '';
            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            inicializarSelectoresSedesModal('rep_red', 'rep_centro', red, centro);
            document.getElementById('rep_nombre').value = '';
            document.getElementById('rep_marca').value = '';
            document.getElementById('rep_modelo').value = '';
            document.getElementById('rep_cantidad').value = 1;
            document.getElementById('rep_costo').value = 0.0;
            document.getElementById('rep_area').value = '';
            document.getElementById('rep_obs').value = '';
            document.getElementById('btn_guardar_rep').textContent = '💾 Guardar Repuesto en Stock';
            abrirModal('modal_repuesto');
        }

        function editarRepuesto(id) {
            const r = LISTA_REPUESTOS.find(item => String(item.id) === String(id));
            if (!r) return;
            document.getElementById('modal_rep_title').textContent = `✎ Modificar Repuesto [${r.nombre_repuesto}]`;
            document.getElementById('rep_id').value = r.id;
            const red = document.getElementById('top_red').value;
            const centro = document.getElementById('top_centro').value;
            inicializarSelectoresSedesModal('rep_red', 'rep_centro', r.red_salud_nombre || red, r.centro_salud_nombre || centro);
            document.getElementById('rep_nombre').value = r.nombre_repuesto || '';
            document.getElementById('rep_marca').value = r.marca || '';
            document.getElementById('rep_modelo').value = r.modelo || r.modelo_parte || '';
            document.getElementById('rep_cantidad').value = r.cantidad || 1;
            document.getElementById('rep_costo').value = r.costo || 0.0;
            document.getElementById('rep_area').value = r.area || '';
            document.getElementById('rep_obs').value = r.observaciones || '';
            document.getElementById('btn_guardar_rep').textContent = '💾 Actualizar Repuesto';
            abrirModal('modal_repuesto');
        }

        function abrirModalIntervencion() {
            document.getElementById('modal_inter_title').textContent = '📋 Registrar Intervención Técnica';
            document.getElementById('inter_id').value = '';
            document.getElementById('inter_trabajo').value = '';
            document.getElementById('inter_obs').value = '';
            document.getElementById('inter_repuesto').value = 'NO';
            document.getElementById('box_rep_nom').style.display = 'none';
            document.getElementById('inter_rep_nombre').value = '';
            document.getElementById('btn_guardar_inter').textContent = '💾 Guardar Intervención Técnica';
            abrirModal('modal_intervencion');
        }

        function editarIntervencion(id) {
            const h = LISTA_HISTORIAL.find(item => String(item.id) === String(id));
            if (!h) return;
            document.getElementById('modal_inter_title').textContent = `✎ Modificar Intervención #${h.id}`;
            document.getElementById('inter_id').value = h.id;
            document.getElementById('inter_equipo').value = h.equipo_id || '';
            document.getElementById('inter_tipo').value = h.tipo || 'Mantenimiento Preventivo';
            document.getElementById('inter_estado').value = h.estado_equipo || 'Bueno';
            document.getElementById('inter_trabajo').value = h.trabajo || h.detalle || '';
            document.getElementById('inter_obs').value = h.observaciones || '';
            if (h.repuesto_usado) {
                document.getElementById('inter_repuesto').value = 'SI';
                document.getElementById('box_rep_nom').style.display = 'block';
                document.getElementById('inter_rep_nombre').value = h.repuesto_nombre || '';
            } else {
                document.getElementById('inter_repuesto').value = 'NO';
                document.getElementById('box_rep_nom').style.display = 'none';
                document.getElementById('inter_rep_nombre').value = '';
            }
            document.getElementById('btn_guardar_inter').textContent = '💾 Actualizar Intervención';
            abrirModal('modal_intervencion');
        }

        // =====================================================================
        // ELIMINACIÓN SEGURA UNIVERSAL (CON RESPALDO EN PAPELERA)
        // =====================================================================

        async function eliminarRegistro(tabla, id, nombreItem) {
            const confirmMsg = `¿Está seguro de eliminar ${nombreItem || 'este registro'}?\n\nEl registro se moverá de forma segura a la papelera de respaldo.`;
            if (!confirm(confirmMsg)) return;

            try {
                const res = await fetch('/api/eliminar_registro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tabla: tabla, id: id })
                });
                const data = await res.json();
                if (data.ok) {
                    alert('🗑️ ' + data.mensaje);
                    const redSel = document.getElementById('top_red').value;
                    const cenSel = document.getElementById('top_centro').value;
                    if (tabla === 'equipos' || tabla === 'muebleria') {
                        cargarInventarioCentro(cenSel, redSel);
                        cargarMueblesCentro(cenSel, redSel);
                        cargarEstadisticasCentro(cenSel, redSel);
                    } else if (tabla === 'catalogo') {
                        cargarCatalogoGlobal();
                    } else if (tabla === 'areas') {
                        cargarAreasGlobal(cenSel, redSel);
                    } else if (tabla === 'repuestos') {
                        cargarRepuestosCentro(cenSel, redSel);
                        cargarEstadisticasCentro(cenSel, redSel);
                    } else if (tabla === 'historial_intervenciones') {
                        cargarHistorialCentro(cenSel, redSel);
                        cargarEstadisticasCentro(cenSel, redSel);
                    } else if (tabla === 'usuarios') {
                        cargarUsuariosGlobal();
                    }
                    if (ES_ADMIN) {
                        cargarPapeleraGlobal();
                    }
                } else {
                    alert('Error al eliminar: ' + (data.error || data.mensaje));
                }
            } catch (e) {
                alert('Fallo de conexión al eliminar: ' + e.message);
            }
        }

        // =====================================================================
        // FOTOGRAFÍA DUAL (CÁMARA / GALERÍA) CON COMPRESIÓN CLIENTE
        // =====================================================================

        function procesarFotoMovil(input) {
            if (!input.files || !input.files[0]) return;
            const file = input.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    let w = img.width, h = img.height;
                    const max = 1024;
                    if (w > h && w > max) { h = Math.round(h * (max / w)); w = max; }
                    else if (h > max) { w = Math.round(w * (max / h)); h = max; }
                    canvas.width = w; canvas.height = h;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, w, h);
                    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                    document.getElementById('foto_base64').value = dataUrl;
                    document.getElementById('img_preview').src = dataUrl;
                    document.getElementById('foto_preview_box').style.display = 'block';
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function quitarFotoMovil() {
            const inCam = document.getElementById('input_camara');
            const inGal = document.getElementById('input_galeria');
            if (inCam) inCam.value = '';
            if (inGal) inGal.value = '';
            document.getElementById('foto_base64').value = '';
            document.getElementById('img_preview').src = '';
            document.getElementById('foto_preview_box').style.display = 'none';
        }

        function toggleChip(el) { el.classList.toggle('active'); }
        function toggleRepuestoIntervencion(val) {
            document.getElementById('box_rep_nom').style.display = (val === 'SI') ? 'block' : 'none';
        }

        function alCambiarAreaModal() {
            const sel = document.getElementById('modal_eq_area');
            if (!sel) return;
            const aNom = sel.value;
            const opt = sel.options && sel.selectedIndex >= 0 ? sel.options[sel.selectedIndex] : null;
            const areaId = opt ? opt.getAttribute('data-id') : null;

            let match = null;
            if (areaId) {
                match = (LISTA_AREAS || []).find(a => String(a.id) === String(areaId));
            }
            if (!match && aNom) {
                match = obtenerAreaObj(aNom);
            }

            if (match) {
                document.getElementById('modal_eq_persona').value = match.encargado || '';
                document.getElementById('modal_eq_cargo').value = match.cargo || '';
                document.getElementById('modal_eq_ci').value = match.ci_encargado || '';
                if (document.getElementById('modal_eq_piso')) {
                    document.getElementById('modal_eq_piso').value = match.piso || '';
                }
            } else {
                document.getElementById('modal_eq_persona').value = '';
                document.getElementById('modal_eq_cargo').value = '';
                document.getElementById('modal_eq_ci').value = '';
                if (document.getElementById('modal_eq_piso')) {
                    document.getElementById('modal_eq_piso').value = '';
                }
            }
        }

        function alCambiarAreaMuebleModal() {
            const sel = document.getElementById('mue_area');
            if (!sel) return;
            const aNom = sel.value;
            const opt = sel.options && sel.selectedIndex >= 0 ? sel.options[sel.selectedIndex] : null;
            const areaId = opt ? opt.getAttribute('data-id') : null;

            let match = null;
            if (areaId) {
                match = (LISTA_AREAS || []).find(a => String(a.id) === String(areaId));
            }
            if (!match && aNom) {
                match = obtenerAreaObj(aNom);
            }

            if (match) {
                document.getElementById('mue_persona').value = match.encargado || '';
                document.getElementById('mue_cargo').value = match.cargo || '';
                document.getElementById('mue_ci').value = match.ci_encargado || '';
            } else {
                document.getElementById('mue_persona').value = '';
                document.getElementById('mue_cargo').value = '';
                document.getElementById('mue_ci').value = '';
            }
        }

        function alSeleccionarCatalogoModal(catId) {
            if (!catId) return;
            const it = LISTA_CATALOGO.find(c => String(c.id) === String(catId));
            if (!it) return;
            if (it.nombre) document.getElementById('modal_eq_nombre').value = it.nombre;
            if (it.marca) document.getElementById('modal_eq_marca').value = it.marca;
            if (it.modelo) document.getElementById('modal_eq_modelo').value = it.modelo;

            if (it.area && LISTA_AREAS.length > 0) {
                const matchArea = obtenerAreaObj(it.area);
                if (matchArea) {
                    document.getElementById('modal_eq_area').value = formatearAreaNombre(matchArea);
                    alCambiarAreaModal();
                }
            }
        }

        // =====================================================================
        // GESTIÓN DE USUARIOS Y PERMISOS (MODAL ADMIN)
        // =====================================================================

        function construirMatrizPermisosHTML(permisosActuales = {}) {
            const tbody = document.getElementById('tbody_matriz_permisos');
            if (!tbody) return;
            tbody.innerHTML = '';

            MODULOS_SISTEMA.forEach(([modKey, modLabel]) => {
                const p = permisosActuales[modKey] || {};
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${modLabel}</td>
                    <td><input type="checkbox" id="p_${modKey}_ver" ${p.ver ? 'checked' : ''} onchange="alCambiarVer('${modKey}')"></td>
                    <td><input type="checkbox" id="p_${modKey}_agregar" ${p.agregar ? 'checked' : ''}></td>
                    <td><input type="checkbox" id="p_${modKey}_cambiar" ${p.cambiar ? 'checked' : ''}></td>
                    <td><input type="checkbox" id="p_${modKey}_eliminar" ${p.eliminar ? 'checked' : ''}></td>
                `;
                tbody.appendChild(tr);
            });
        }

        function alCambiarVer(modKey) {
            const chkVer = document.getElementById(`p_${modKey}_ver`);
            if (!chkVer.checked) {
                document.getElementById(`p_${modKey}_agregar`).checked = false;
                document.getElementById(`p_${modKey}_cambiar`).checked = false;
                document.getElementById(`p_${modKey}_eliminar`).checked = false;
            }
        }

        function alCambiarRolEnModal(rolVal) {
            const defaults = {
                'jefe': { ver: true, agregar: true, cambiar: true, eliminar: true },
                'tecnico': { ver: true, agregar: true, cambiar: true, eliminar: false },
                'relevamiento': { ver: true, agregar: true, cambiar: true, eliminar: false },
                'visita': { ver: true, agregar: false, cambiar: false, eliminar: false }
            };
            const def = defaults[rolVal] || defaults['tecnico'];

            MODULOS_SISTEMA.forEach(([modKey]) => {
                let v = def.ver;
                let a = def.agregar;
                let c = def.cambiar;
                let e = def.eliminar;

                if (rolVal === 'tecnico' && (modKey === 'Usuarios' || modKey === 'Sedes')) {
                    v = false; a = false; c = false; e = false;
                }
                if (rolVal === 'relevamiento' && !['Inventario', 'Catalogo', 'Muebleria', 'Areas'].includes(modKey)) {
                    v = false; a = false; c = false; e = false;
                }

                const chkV = document.getElementById(`p_${modKey}_ver`);
                const chkA = document.getElementById(`p_${modKey}_agregar`);
                const chkC = document.getElementById(`p_${modKey}_cambiar`);
                const chkE = document.getElementById(`p_${modKey}_eliminar`);
                if (chkV) chkV.checked = v;
                if (chkA) chkA.checked = a;
                if (chkC) chkC.checked = c;
                if (chkE) chkE.checked = e;
            });
        }

        function abrirModalCrearUsuario() {
            document.getElementById('modal_user_title').textContent = '✚ Registrar Nuevo Usuario';
            document.getElementById('u_ci').value = '';
            document.getElementById('u_ci').disabled = false;
            document.getElementById('u_nombre').value = '';
            document.getElementById('u_rol').value = 'tecnico';
            document.getElementById('u_password').value = '';
            document.getElementById('u_password').required = true;

            construirMatrizPermisosHTML();
            alCambiarRolEnModal('tecnico');
            abrirModal('modal_usuario_permisos');
        }

        function abrirModalEditarUsuario(ci) {
            const u = LISTA_USUARIOS.find(usr => usr.nombre_usuario === ci);
            if (!u) return;

            document.getElementById('modal_user_title').textContent = `⚙️ Permisos de ${u.nombre_completo || ci}`;
            document.getElementById('u_ci').value = u.nombre_usuario;
            document.getElementById('u_ci').disabled = true;
            document.getElementById('u_nombre').value = u.nombre_completo || '';
            document.getElementById('u_rol').value = (u.rol === 'administrador') ? 'jefe' : (u.rol || 'tecnico');
            document.getElementById('u_password').value = '';
            document.getElementById('u_password').required = false;

            construirMatrizPermisosHTML(u.permisos || {});
            abrirModal('modal_usuario_permisos');
        }

        async function guardarUsuarioPermisosSubmit(event) {
            event.preventDefault();
            const permisosDict = {};
            let canDel = false, canEdt = false;

            MODULOS_SISTEMA.forEach(([modKey]) => {
                const v = document.getElementById(`p_${modKey}_ver`).checked;
                const a = document.getElementById(`p_${modKey}_agregar`).checked;
                const c = document.getElementById(`p_${modKey}_cambiar`).checked;
                const e = document.getElementById(`p_${modKey}_eliminar`).checked;

                permisosDict[modKey] = { ver: v, agregar: a, cambiar: c, eliminar: e };
                if (e) canDel = true;
                if (a || c) canEdt = true;
            });
            permisosDict["can_delete"] = canDel;
            permisosDict["can_edit"] = canEdt;

            const payload = {
                nombre_usuario: document.getElementById('u_ci').value.trim(),
                nombre_completo: document.getElementById('u_nombre').value.trim(),
                rol: document.getElementById('u_rol').value,
                password: document.getElementById('u_password').value.trim(),
                permisos: permisosDict,
                activo: true
            };

            try {
                const res = await fetch('/api/guardar_usuario_permisos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok) {
                    alert('✅ Usuario y permisos actualizados correctamente');
                    cerrarModal('modal_usuario_permisos');
                    cargarUsuariosGlobal();
                } else {
                    alert('Error: ' + (data.error || data.mensaje));
                }
            } catch (err) {
                alert('Fallo de conexión: ' + err.message);
            }
        }

        // =====================================================================
        // SUBMITS A LA API (EQUIPOS, CATÁLOGO, MUEBLES, ÁREAS, REPUESTOS, INTERVENCIONES)
        // =====================================================================

        async function guardarEquipoMovil(event) {
            event.preventDefault();
            const btn = document.getElementById('btn_guardar_eq');
            btn.disabled = true;
            btn.textContent = 'Guardando en Servidor...';

            // Recoger los 13 criterios de evaluación
            const detallesCat = [];
            for (let i = 0; i < 13; i++) {
                const radios = document.getElementsByName('crit_' + i);
                let v = "";
                for (let r of radios) {
                    if (r.checked) { v = r.value; break; }
                }
                detallesCat.push(v);
            }

            const modAdqRad = document.querySelector('input[name="modalidad_adq"]:checked');
            const modAdqVal = modAdqRad ? modAdqRad.value : 'Compra';

            const tipoMovRad = document.querySelector('input[name="tipo_movilidad"]:checked');
            const tipoMovVal = tipoMovRad ? tipoMovRad.value : 'Fijo';

            const garRad = document.querySelector('input[name="tiene_garantia"]:checked');
            const garVal = garRad ? garRad.value : 'Sin Garantía';

            const redVal = (document.getElementById('modal_eq_red') ? document.getElementById('modal_eq_red').value : '') || document.getElementById('top_red').value;
            const cenVal = (document.getElementById('modal_eq_centro') ? document.getElementById('modal_eq_centro').value : '') || document.getElementById('top_centro').value;

            const payload = {
                id: document.getElementById('modal_eq_id_af').value,
                _es_edicion: document.getElementById('modal_eq_es_edicion').value === '1',
                red_salud_nombre: redVal,
                centro_salud_nombre: cenVal,
                sector_actual: document.getElementById('modal_eq_sector').value || "SALUD",
                servicio: document.getElementById('modal_eq_servicio').value || "",
                area: document.getElementById('modal_eq_area').value,
                persona_asignada: document.getElementById('modal_eq_persona').value,
                cargo_asignado: document.getElementById('modal_eq_cargo').value,
                ci_asignado: document.getElementById('modal_eq_ci').value,
                nombre: document.getElementById('modal_eq_nombre').value,
                marca: document.getElementById('modal_eq_marca').value,
                modelo: document.getElementById('modal_eq_modelo').value,
                numero_serie: document.getElementById('modal_eq_serie').value.trim() || "S/C",
                codigo_sispam: document.getElementById('modal_eq_sispam').value.trim() || "S/C",
                bertin: document.getElementById('modal_eq_bertin').value.trim() || "S/C",
                sapm: document.getElementById('modal_eq_sapm').value.trim() || "S/C",
                estado: document.getElementById('modal_eq_estado').value,
                criticidad: document.getElementById('modal_eq_criticidad').value,
                categorizacion_detalle: JSON.stringify(detallesCat),
                procedencia: document.getElementById('modal_eq_procedencia').value,
                fabricante: document.getElementById('modal_eq_fabricante').value,
                proveedor: document.getElementById('modal_eq_proveedor').value,
                anio_fab: document.getElementById('modal_eq_anio_fab').value,
                fecha_adquisicion: document.getElementById('modal_eq_fecha_instalacion').value,
                a_comp: modAdqVal === 'Compra',
                a_como: modAdqVal === 'Comodato',
                a_don: modAdqVal === 'Donación',
                costo: document.getElementById('modal_eq_costo').value || '0',
                te_fijo: tipoMovVal === 'Fijo',
                te_mov: tipoMovVal === 'Móvil',
                te_por: tipoMovVal === 'Portátil',
                garantia: garVal,
                fecha_inicio_garantia: document.getElementById('modal_eq_gar_inicio').value || null,
                fecha_vencimiento_garantia: document.getElementById('modal_eq_gar_fin').value || null,
                foto: document.getElementById('foto_base64').value,
                t_elec: document.querySelector('.chip-btn[data-f="t_elec"]').classList.contains('active'),
                t_elco: document.querySelector('.chip-btn[data-f="t_elco"]').classList.contains('active'),
                t_mec: document.querySelector('.chip-btn[data-f="t_mec"]').classList.contains('active'),
                t_hid: document.querySelector('.chip-btn[data-f="t_hid"]').classList.contains('active'),
                t_neu: document.querySelector('.chip-btn[data-f="t_neu"]').classList.contains('active'),
                t_vap: document.querySelector('.chip-btn[data-f="t_vap"]').classList.contains('active'),
                voltaje: document.getElementById('modal_eq_voltaje').value,
                corriente: document.getElementById('modal_eq_corriente').value,
                potencia: document.getElementById('modal_eq_potencia').value,
                vida_util: document.getElementById('modal_eq_vida_util').value,
                temperatura: document.getElementById('modal_eq_vida_util').value,
                peso: document.getElementById('modal_eq_peso').value,
                dimensiones: document.getElementById('modal_eq_dimensiones').value,
                bateria_respaldo: document.getElementById('modal_eq_bateria').value,
                resolucion: document.getElementById('modal_eq_bateria').value,
                version_software: document.getElementById('modal_eq_software').value,
                humedad: document.getElementById('modal_eq_software').value,
                suministro_gases: document.getElementById('modal_eq_gases').value,
                contexto_operacional: document.getElementById('modal_eq_contexto').value,
                funciones_equipo: document.getElementById('modal_eq_funciones').value,
                acciones_preventivas: document.getElementById('modal_eq_acciones_prev').value,
                acciones_falla: document.getElementById('modal_eq_insumos').value,
                fallas_funcionales: document.getElementById('modal_eq_fallas_comunes').value,
                causas_fallo: document.getElementById('modal_eq_causas_fallo').value,
                efectos_fallo: document.getElementById('modal_eq_efectos_fallo').value,
                efecto_entorno: document.getElementById('modal_eq_acciones_corr').value,
                observaciones: document.getElementById('modal_eq_obs').value
            };

            try {
                const res = await fetch('/api/guardar_equipo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok) {
                    alert(`✅ ¡Equipo guardado con éxito!\nCódigo AF: ${data.id}`);
                    cerrarModal('modal_equipo');
                    if (redVal && document.getElementById('top_red') && document.getElementById('top_red').value !== redVal) {
                        document.getElementById('top_red').value = redVal;
                        alCambiarRedGlobal();
                        if (document.getElementById('top_centro')) document.getElementById('top_centro').value = cenVal;
                        alCambiarCentroGlobal();
                    } else if (cenVal && document.getElementById('top_centro') && document.getElementById('top_centro').value !== cenVal) {
                        document.getElementById('top_centro').value = cenVal;
                        alCambiarCentroGlobal();
                    } else {
                        cargarInventarioCentro(cenVal, redVal);
                        cargarMueblesCentro(cenVal, redVal);
                        cargarEstadisticasCentro(cenVal, redVal);
                    }
                } else {
                    alert('Error: ' + (data.error || 'No se pudo guardar'));
                }
            } catch (err) {
                alert('Fallo de conexión: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.textContent = '💾 Guardar Equipo Médico';
            }
        }

        async function guardarNuevoCatalogo(event) {
            event.preventDefault();
            const idVal = document.getElementById('cat_id').value;

            let areaVal = '';
            const selArea = document.getElementById('cat_area');
            const inpManual = document.getElementById('cat_area_manual');
            if (inpManual && inpManual.style.display !== 'none' && inpManual.value.trim()) {
                areaVal = inpManual.value.trim();
            } else if (selArea && selArea.value && selArea.value !== '__NUEVA__') {
                areaVal = selArea.value.trim();
            } else if (inpManual && inpManual.value.trim()) {
                areaVal = inpManual.value.trim();
            }

            const payload = {
                id: idVal ? parseInt(idVal) : null,
                nombre: (document.getElementById('cat_nombre').value || '').trim(),
                marca: (document.getElementById('cat_marca').value || '').trim(),
                modelo: (document.getElementById('cat_modelo').value || '').trim(),
                area: areaVal,
                piso: (document.getElementById('cat_piso').value || '').trim()
            };
            try {
                const res = await fetch('/api/guardar_catalogo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok) {
                    alert('✅ Modelo guardado en catálogo');
                    cerrarModal('modal_catalogo');
                    cargarCatalogoGlobal();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (e) { alert('Fallo de conexión: ' + e.message); }
        }

        async function guardarNuevoMueble(event) {
            event.preventDefault();
            const idVal = document.getElementById('mue_id').value;
            const redSel = (document.getElementById('mue_red') ? document.getElementById('mue_red').value : '') || (document.getElementById('top_red') ? document.getElementById('top_red').value : '');
            const cenSel = (document.getElementById('mue_centro') ? document.getElementById('mue_centro').value : '') || (document.getElementById('top_centro') ? document.getElementById('top_centro').value : '');
            const redes = SEDES_DATA.redes || [];
            const rObj = redes.find(r => r.nombre === redSel);
            const rId = rObj ? rObj.id : null;
            const centros = SEDES_DATA.centros || [];
            const cObj = centros.find(c => c.nombre === cenSel);
            const cId = cObj ? cObj.id : null;

            const tipoAct = (document.getElementById('mue_tipo') ? document.getElementById('mue_tipo').value.trim() : '') || 'COMPUTADORA DE ESCRITORIO';
            let descAct = (document.getElementById('mue_desc') ? document.getElementById('mue_desc').value.trim() : '');
            if (!descAct) descAct = tipoAct;

            const areaAct = (document.getElementById('mue_area') ? document.getElementById('mue_area').value : '') || 'General';

            const payload = {
                id: idVal ? parseInt(idVal) : null,
                m_id: idVal ? parseInt(idVal) : null,
                direccion_administrativa: redSel,
                unidad_organizacional: cenSel,
                red_salud_id: rId,
                centro_salud_id: cId,
                sector_actual: (document.getElementById('mue_sector') ? document.getElementById('mue_sector').value : '') || 'SALUD',
                tipo_activo: tipoAct,
                descripcion: descAct,
                marca: document.getElementById('mue_marca') ? document.getElementById('mue_marca').value.trim() : '',
                modelo: document.getElementById('mue_modelo') ? document.getElementById('mue_modelo').value.trim() : '',
                serie: (document.getElementById('mue_serie') ? document.getElementById('mue_serie').value.trim() : '') || 'S/C',
                codigo_sispam: (document.getElementById('mue_sispam') ? document.getElementById('mue_sispam').value.trim() : '') || 'S/C',
                bertin: (document.getElementById('mue_bertin') ? document.getElementById('mue_bertin').value.trim() : '') || 'S/C',
                sapm: (document.getElementById('mue_sapm') ? document.getElementById('mue_sapm').value.trim() : '') || 'S/C',
                detalle_transaccion: (document.getElementById('mue_transaccion') ? document.getElementById('mue_transaccion').value.trim() : '') || 'Asignacion 2026',
                fecha_asignacion: (document.getElementById('mue_fecha_asig') ? document.getElementById('mue_fecha_asig').value : '') || new Date().toISOString().slice(0, 10),
                ubicacion: areaAct,
                persona_asignada: document.getElementById('mue_persona') ? document.getElementById('mue_persona').value.trim() : '',
                cargo_asignado: document.getElementById('mue_cargo') ? document.getElementById('mue_cargo').value.trim() : '',
                ci_asignado: document.getElementById('mue_ci') ? document.getElementById('mue_ci').value.trim() : '',
                estado_conservacion: (document.getElementById('mue_estado') ? document.getElementById('mue_estado').value : '') || 'Bueno',
                tecnico_inventareador: (document.getElementById('mue_tecnico') ? document.getElementById('mue_tecnico').value.trim() : '') || (USUARIO_ACTUAL.nombre_completo || USUARIO_ACTUAL.nombre_usuario || '').trim(),
                observaciones_de_asignacion: document.getElementById('mue_obs') ? document.getElementById('mue_obs').value.trim() : '',
                estado: "Activo"
            };
            try {
                const res = await fetch('/api/guardar_mueble', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok) {
                    alert('✅ Activo de mueblería / TI guardado con éxito');
                    cerrarModal('modal_mueble');
                    if (redSel && document.getElementById('top_red')) {
                        document.getElementById('top_red').value = redSel;
                        alCambiarRedGlobal(cenSel);
                    } else if (cenSel && document.getElementById('top_centro')) {
                        document.getElementById('top_centro').value = cenSel;
                        alCambiarCentroGlobal();
                    } else {
                        cargarMueblesCentro(cenSel, redSel);
                        cargarInventarioCentro(cenSel, redSel);
                        cargarEstadisticasCentro(cenSel, redSel);
                    }
                } else {
                    alert('Error al guardar activo: ' + (data.error || data.id || 'Consulte al administrador'));
                }
            } catch (e) { alert('Fallo de conexión al servidor: ' + e.message); }
        }

        async function guardarNuevaArea(event) {
            event.preventDefault();
            const idVal = document.getElementById('area_id').value;
            const redVal = (document.getElementById('area_red') ? document.getElementById('area_red').value : '') || document.getElementById('top_red').value;
            const cenVal = (document.getElementById('area_centro') ? document.getElementById('area_centro').value : '') || document.getElementById('top_centro').value;
            const payload = {
                id: idVal ? parseInt(idVal) : null,
                red_salud_nombre: redVal,
                centro_salud_nombre: cenVal,
                nombre: document.getElementById('area_nom').value,
                piso: document.getElementById('area_piso').value,
                encargado: document.getElementById('area_encargado').value,
                cargo: document.getElementById('area_cargo').value,
                ci_encargado: document.getElementById('area_ci').value,
                contacto: document.getElementById('area_contacto').value
            };
            try {
                const res = await fetch('/api/guardar_area', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok) {
                    alert('✅ Área guardada exitosamente');
                    cerrarModal('modal_area');
                    if (redVal && document.getElementById('top_red') && document.getElementById('top_red').value !== redVal) {
                        document.getElementById('top_red').value = redVal;
                        alCambiarRedGlobal();
                        if (document.getElementById('top_centro')) document.getElementById('top_centro').value = cenVal;
                        alCambiarCentroGlobal();
                    } else if (cenVal && document.getElementById('top_centro') && document.getElementById('top_centro').value !== cenVal) {
                        document.getElementById('top_centro').value = cenVal;
                        alCambiarCentroGlobal();
                    } else {
                        cargarAreasGlobal(cenVal, redVal);
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (e) { alert('Fallo de conexión: ' + e.message); }
        }

        async function guardarNuevoRepuesto(event) {
            event.preventDefault();
            const idVal = document.getElementById('rep_id').value;
            const redVal = (document.getElementById('rep_red') ? document.getElementById('rep_red').value : '') || document.getElementById('top_red').value;
            const cenVal = (document.getElementById('rep_centro') ? document.getElementById('rep_centro').value : '') || document.getElementById('top_centro').value;
            const payload = {
                id: idVal ? parseInt(idVal) : null,
                red_salud_nombre: redVal,
                centro_salud_nombre: cenVal,
                nombre_repuesto: document.getElementById('rep_nombre').value,
                marca: document.getElementById('rep_marca').value,
                modelo: document.getElementById('rep_modelo').value,
                modelo_parte: document.getElementById('rep_modelo').value,
                cantidad: document.getElementById('rep_cantidad').value,
                costo: document.getElementById('rep_costo').value,
                area: document.getElementById('rep_area').value,
                observaciones: document.getElementById('rep_obs').value,
                estado_disponibilidad: "En Stock"
            };
            try {
                const res = await fetch('/api/guardar_repuesto', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok) {
                    alert('✅ Repuesto guardado en stock');
                    cerrarModal('modal_repuesto');
                    if (redVal && document.getElementById('top_red') && document.getElementById('top_red').value !== redVal) {
                        document.getElementById('top_red').value = redVal;
                        alCambiarRedGlobal();
                        if (document.getElementById('top_centro')) document.getElementById('top_centro').value = cenVal;
                        alCambiarCentroGlobal();
                    } else if (cenVal && document.getElementById('top_centro') && document.getElementById('top_centro').value !== cenVal) {
                        document.getElementById('top_centro').value = cenVal;
                        alCambiarCentroGlobal();
                    } else {
                        cargarRepuestosCentro(cenVal, redVal);
                        cargarEstadisticasCentro(cenVal, redVal);
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (e) { alert('Fallo de conexión: ' + e.message); }
        }

        async function guardarNuevaIntervencion(event) {
            event.preventDefault();
            const idVal = document.getElementById('inter_id').value;
            const payload = {
                id: idVal ? parseInt(idVal) : null,
                equipo_id: document.getElementById('inter_equipo').value,
                tipo: document.getElementById('inter_tipo').value,
                estado_equipo: document.getElementById('inter_estado').value,
                trabajo: document.getElementById('inter_trabajo').value,
                observaciones: document.getElementById('inter_obs').value,
                repuesto_usado: document.getElementById('inter_repuesto').value === 'SI',
                repuesto_nombre: document.getElementById('inter_rep_nombre').value,
                repuesto_cantidad: 1
            };
            try {
                const res = await fetch('/api/guardar_intervencion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok) {
                    alert('✅ Intervención técnica guardada');
                    cerrarModal('modal_intervencion');
                    cargarHistorialCentro(document.getElementById('top_centro').value);
                    cargarEstadisticasCentro(document.getElementById('top_centro').value);
                } else {
                    alert('Error: ' + (data.error || data.mensaje));
                }
            } catch (e) { alert('Fallo de conexión: ' + e.message); }
        }

        // =====================================================================
        // GESTIÓN Y RECUPERACIÓN DE PAPELERA DE SEGURIDAD (SOLO ADMIN Y GODHEAD)
        // =====================================================================

        function setFiltroPapelera(tabla) {
            FILTRO_PAPELERA_TABLA = tabla;
            document.querySelectorAll('#pane_papelera .btn-filter-pill').forEach(btn => btn.classList.remove('active'));
            const pillId = tabla === 'todos' ? 'pill_pap_todo' : `pill_pap_${tabla}`;
            const targetPill = document.getElementById(pillId);
            if (targetPill) targetPill.classList.add('active');
            filtrarListaPapelera();
        }

        async function cargarPapeleraGlobal() {
            if (!ES_ADMIN) return;
            const cont = document.getElementById('lista_papelera');
            if (cont) cont.innerHTML = '<div class="empty-state"><span>⏳</span>Cargando elementos borrados...</div>';
            try {
                const res = await fetch('/api/papelera');
                if (res.ok) {
                    LISTA_PAPELERA = await res.json();
                    actualizarContadoresPapelera();
                    filtrarListaPapelera();
                } else {
                    if (cont) cont.innerHTML = '<div class="empty-state"><span>🔒</span>Acceso exclusivo para modo Administrador y Godhead</div>';
                }
            } catch (e) {
                if (cont) cont.innerHTML = `<div class="empty-state"><span>⚠️</span>Error al cargar papelera: ${e.message}</div>`;
            }
        }

        function actualizarContadoresPapelera() {
            const tot = LISTA_PAPELERA.length;
            const cntEq = LISTA_PAPELERA.filter(it => it.tabla_origen === 'equipos').length;
            const cntMu = LISTA_PAPELERA.filter(it => it.tabla_origen === 'muebleria').length;
            const cntAr = LISTA_PAPELERA.filter(it => it.tabla_origen === 'areas').length;
            const cntCat = LISTA_PAPELERA.filter(it => it.tabla_origen === 'catalogo').length;
            const cntRep = LISTA_PAPELERA.filter(it => it.tabla_origen === 'repuestos').length;

            const elBadge = document.getElementById('cnt_papelera_badge');
            if (elBadge) elBadge.textContent = tot;
            const elTodo = document.getElementById('cnt_pap_todo');
            if (elTodo) elTodo.textContent = tot;
            const elEq = document.getElementById('cnt_pap_equipos');
            if (elEq) elEq.textContent = cntEq;
            const elMu = document.getElementById('cnt_pap_muebles');
            if (elMu) elMu.textContent = cntMu;
            const elAr = document.getElementById('cnt_pap_areas');
            if (elAr) elAr.textContent = cntAr;
            const elCat = document.getElementById('cnt_pap_catalogo');
            if (elCat) elCat.textContent = cntCat;
            const elRep = document.getElementById('cnt_pap_repuestos');
            if (elRep) elRep.textContent = cntRep;
        }

        function filtrarListaPapelera() {
            const q = (document.getElementById('busq_papelera') ? document.getElementById('busq_papelera').value.toLowerCase().trim() : '');
            let filtrados = [...LISTA_PAPELERA];

            if (FILTRO_PAPELERA_TABLA && FILTRO_PAPELERA_TABLA !== 'todos') {
                filtrados = filtrados.filter(it => it.tabla_origen === FILTRO_PAPELERA_TABLA);
            }

            if (q) {
                filtrados = filtrados.filter(it => {
                    const tit = (it.titulo || '').toLowerCase();
                    const cod = (it.codigo || '').toLowerCase();
                    const sed = (it.sede || '').toLowerCase();
                    const ubi = (it.ubicacion || '').toLowerCase();
                    const por = (it.eliminado_por || '').toLowerCase();
                    const idO = String(it.id_original || '').toLowerCase();
                    return tit.includes(q) || cod.includes(q) || sed.includes(q) || ubi.includes(q) || por.includes(q) || idO.includes(q);
                });
            }

            renderizarListaPapelera(filtrados);
        }

        function renderizarListaPapelera(items) {
            const cont = document.getElementById('lista_papelera');
            if (!cont) return;

            if (!items || items.length === 0) {
                cont.innerHTML = `
                <div class="empty-state" style="padding: 40px 20px;">
                    <span style="font-size: 38px;">✨</span>
                    <strong style="color: #10B981; font-size: 15px;">La papelera está vacía</strong>
                    <div style="font-size: 12.5px; color: var(--text-muted); margin-top: 4px;">
                        No hay elementos borrados con este criterio. Cuando elimines un registro de inventario, muebles, áreas o catálogo, aparecerá aquí con la opción de restaurarlo.
                    </div>
                </div>`;
                return;
            }

            let html = '';
            items.forEach(it => {
                let badgeColor = '#64748B';
                let badgeBg = '#F1F5F9';
                if (it.tabla_origen === 'equipos') { badgeColor = '#0284C7'; badgeBg = '#E0F2FE'; }
                else if (it.tabla_origen === 'muebleria') { badgeColor = '#7C3AED'; badgeBg = '#EDE9FE'; }
                else if (it.tabla_origen === 'areas') { badgeColor = '#059669'; badgeBg = '#D1FAE5'; }
                else if (it.tabla_origen === 'catalogo') { badgeColor = '#D97706'; badgeBg = '#FEF3C7'; }
                else if (it.tabla_origen === 'repuestos') { badgeColor = '#EA580C'; badgeBg = '#FFEDD5'; }

                const fElim = it.fecha_eliminacion ? new Date(it.fecha_eliminacion).toLocaleString('es-BO') : 'Fecha no registrada';

                html += `
                <div class="card-item" style="border-left: 5px solid ${badgeColor}; background: #FFFFFF;">
                    <div class="card-item-header">
                        <span class="badge" style="background: ${badgeBg}; color: ${badgeColor}; font-weight: 800; font-size: 11px;">
                            ${it.tipo_icono} ${it.tipo_label.toUpperCase()}
                        </span>
                        <span class="badge-status status-regular" style="font-size: 10px;">ID Orig: ${it.id_original}</span>
                    </div>
                    <div class="item-title" style="font-size: 15px; font-weight: 800; color: #0F172A; margin: 4px 0;">
                        ${it.titulo}
                    </div>
                    <div class="item-subtitle" style="font-size: 12px; margin-bottom: 6px;">
                        <span>🏷️ <strong>Cód / Serie:</strong> ${it.codigo}</span>
                        <span>•</span>
                        <span>🏥 <strong>Sede:</strong> ${it.sede}</span>
                        ${it.ubicacion && it.ubicacion !== '-' ? '<span>•</span><span>📍 ' + it.ubicacion + '</span>' : ''}
                    </div>
                    <div class="item-detail-row" style="background: #F8FAFC; border: 1px dashed #CBD5E1; padding: 6px 10px; border-radius: 6px; font-size: 11.5px; color: #475569;">
                        🗑️ <strong>Eliminado por:</strong> ${it.eliminado_por || 'Sistema'} &nbsp;|&nbsp; 🕒 <strong>Fecha:</strong> ${fElim}
                    </div>
                    <div class="item-actions" style="margin-top: 10px; display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap;">
                        <button type="button" class="btn-restore-action" onclick="recuperarElementoPapelera(${it.id}, '${escaparJs(it.titulo)}')">
                            <span>♻️</span> Recuperar Registro
                        </button>
                        <button type="button" class="btn-purge-action" onclick="purgarElementoPapelera(${it.id}, '${escaparJs(it.titulo)}')">
                            <span>❌</span> Purgar
                        </button>
                    </div>
                </div>`;
            });
            cont.innerHTML = html;
        }

        async function recuperarElementoPapelera(papeleraId, titulo) {
            const ok = confirm(`¿Deseas RECUPERAR este registro y devolverlo al inventario activo?\n\n"${titulo}"\n\nEl registro volverá a estar 100% operativo en su módulo correspondiente.`);
            if (!ok) return;

            try {
                const res = await fetch('/api/papelera/recuperar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: papeleraId })
                });
                const data = await res.json();
                if (data.ok) {
                    alert(data.mensaje || '✅ Registro recuperado exitosamente.');
                    await cargarPapeleraGlobal();
                    const redSel = document.getElementById('top_red') ? document.getElementById('top_red').value : '';
                    const cenSel = document.getElementById('top_centro') ? document.getElementById('top_centro').value : '';
                    cargarInventarioCentro(cenSel, redSel);
                    cargarMueblesCentro(cenSel, redSel);
                    cargarAreasGlobal(cenSel, redSel);
                    cargarCatalogoGlobal();
                    cargarRepuestosCentro(cenSel, redSel);
                    cargarEstadisticasCentro(cenSel, redSel);
                } else {
                    alert('Error al recuperar: ' + (data.error || 'No se pudo procesar'));
                }
            } catch (e) {
                alert('Fallo de conexión al recuperar: ' + e.message);
            }
        }

        async function purgarElementoPapelera(papeleraId, titulo) {
            const ok = confirm(`⚠️ ATENCIÓN: Esta acción eliminará permanentemente de la papelera este registro:\n\n"${titulo}"\n\nEsta acción NO se puede deshacer. ¿Deseas purgar definitivamente?`);
            if (!ok) return;

            try {
                const res = await fetch('/api/papelera/eliminar_definitivo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: papeleraId })
                });
                const data = await res.json();
                if (data.ok) {
                    alert(data.mensaje || 'Registro purgado permanentemente.');
                    await cargarPapeleraGlobal();
                } else {
                    alert('Error: ' + (data.error || 'No se pudo purgar'));
                }
            } catch (e) {
                alert('Fallo de conexión: ' + e.message);
            }
        }
    </script>
</body>
</html>
"""
