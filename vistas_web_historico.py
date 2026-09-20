# vistas_web_historico.py
# Interfaz Web de Consulta Histórica GAMLP (Gestiones Anteriores - Solo Lectura)
# Permite consultar y buscar los 2.938 equipos y activos históricos sin alterarlos.

HTML_HISTORICO_WEB = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SGEM GAMLP • Consulta Histórica (Solo Lectura)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #1E293B;
            --primary-dark: #0F172A;
            --accent: #0284C7;
            --gold: #D97706;
            --gold-bg: #FEF3C7;
            --bg: #F1F5F9;
            --card-bg: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --radius-card: 12px;
            --radius-btn: 8px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: var(--bg); color: var(--text-main); min-height: 100vh; padding-bottom: 60px; }

        /* HEADER HISTÓRICO */
        .header-historico {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
            color: #FFFFFF;
            padding: 16px 20px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }
        .header-left { display: flex; align-items: center; gap: 12px; }
        .badge-historico {
            background: linear-gradient(135deg, #D97706, #B45309);
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 4px 10px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .header-title { font-size: 18px; font-weight: 800; }
        .header-sub { font-size: 12px; color: #94A3B8; }

        .btn-ir-actual {
            background: #2563EB;
            color: #FFFFFF;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: var(--radius-btn);
            font-size: 12.5px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(37,99,235,0.3);
        }
        .btn-ir-actual:hover { background: #1D4ED8; }

        /* CONTENEDOR PRINCIPAL */
        .container { max-width: 1200px; margin: 18px auto 0; padding: 0 16px; }

        /* BANNER DE AVISO SOLO LECTURA */
        .banner-readonly {
            background: #FEF3C7;
            border: 1.5px solid #FDE68A;
            color: #92400E;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 13px;
            line-height: 1.4;
        }

        /* SELECTOR TERRITORIAL */
        .card-filtros {
            background: var(--card-bg);
            border-radius: var(--radius-card);
            border: 1px solid var(--border);
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }
        .grid-selectores {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }
        @media (min-width: 768px) {
            .grid-selectores { grid-template-columns: 1fr 1fr; }
        }
        .sel-group label {
            display: block;
            font-size: 11.5px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .sel-control {
            width: 100%;
            height: 42px;
            padding: 0 12px;
            border-radius: var(--radius-btn);
            border: 1.5px solid var(--border);
            background: #F8FAFC;
            font-size: 13.5px;
            font-weight: 600;
            color: var(--text-main);
            outline: none;
            transition: all 0.2s;
        }
        .sel-control:focus { border-color: var(--accent); background: #FFFFFF; }

        /* BOTONES DE FILTRO DE TIPO DE ACTIVO (VER TODO / EQUIPOS / MUEBLES) */
        .asset-type-bar {
            display: flex;
            gap: 8px;
            margin-top: 14px;
            flex-wrap: wrap;
        }
        .asset-btn {
            flex: 1;
            min-width: 130px;
            padding: 10px 14px;
            border-radius: var(--radius-btn);
            border: 1.5px solid var(--border);
            background: #F8FAFC;
            color: var(--text-muted);
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s;
        }
        .asset-btn.active {
            background: var(--primary);
            color: #FFFFFF;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(30,41,59,0.25);
        }

        /* BARRA DE BÚSQUEDA Y TOTALES */
        .search-stats-bar {
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        .search-box {
            flex: 1;
            min-width: 250px;
            position: relative;
        }
        .search-input {
            width: 100%;
            height: 44px;
            padding: 0 14px 0 40px;
            border-radius: var(--radius-btn);
            border: 1.5px solid var(--border);
            background: #FFFFFF;
            font-size: 14px;
            outline: none;
            transition: all 0.2s;
        }
        .search-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(2,132,199,0.12); }
        .search-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: #94A3B8;
            font-size: 16px;
        }

        .stats-badge {
            background: #FFFFFF;
            border: 1px solid var(--border);
            padding: 10px 16px;
            border-radius: var(--radius-btn);
            font-size: 13px;
            font-weight: 800;
            color: var(--primary);
            white-space: nowrap;
        }

        /* GRID DE TARJETAS DE ACTIVOS */
        .cards-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }
        @media (min-width: 640px) {
            .cards-grid { grid-template-columns: repeat(2, 1fr); }
        }
        @media (min-width: 1024px) {
            .cards-grid { grid-template-columns: repeat(3, 1fr); }
        }

        .card-asset {
            background: var(--card-bg);
            border-radius: var(--radius-card);
            border: 1px solid var(--border);
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            cursor: pointer;
            position: relative;
        }
        .card-asset:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.06);
            border-color: #CBD5E1;
        }

        .card-asset-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 8px;
        }
        .asset-icon-title { display: flex; align-items: center; gap: 8px; }
        .asset-icon { font-size: 22px; }
        .asset-title {
            font-size: 14px;
            font-weight: 800;
            color: var(--primary);
            line-height: 1.3;
        }

        .badge-af {
            background: #F1F5F9;
            color: #334155;
            font-family: monospace;
            font-size: 11px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid #CBD5E1;
            white-space: nowrap;
        }

        .asset-meta {
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.5;
            margin: 6px 0 12px;
        }
        .asset-meta span { color: var(--text-main); font-weight: 600; }

        .card-asset-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 10px;
            border-top: 1px dashed var(--border);
        }
        .badge-estado {
            font-size: 10.5px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        .st-bueno { background: #DCFCE7; color: #166534; }
        .st-regular { background: #FEF3C7; color: #92400E; }
        .st-malo { background: #FEE2E2; color: #991B1B; }

        .btn-ver-detalle {
            background: #F1F5F9;
            color: var(--primary);
            border: 1px solid #CBD5E1;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        /* MODAL DE FICHA TÉCNICA HISTÓRICA (SOLO LECTURA) */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15,23,42,0.65);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 16px;
        }
        .modal-sheet {
            background: #FFFFFF;
            border-radius: 16px;
            width: 100%;
            max-width: 680px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.25);
            display: flex;
            flex-direction: column;
        }
        .modal-header {
            background: linear-gradient(135deg, #0F172A, #1E293B);
            color: #FFFFFF;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .modal-title { font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 8px; }
        .btn-close {
            background: rgba(255,255,255,0.15);
            border: none;
            color: #FFFFFF;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .modal-body { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
        .det-section-title {
            font-size: 12.5px;
            font-weight: 800;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1.5px solid #E2E8F0;
            padding-bottom: 4px;
            margin-top: 6px;
        }
        .det-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .det-item { display: flex; flex-direction: column; gap: 2px; }
        .det-label { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
        .det-value { font-size: 13px; font-weight: 600; color: var(--text-main); word-break: break-word; }
        .det-box {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 13px;
            line-height: 1.4;
            color: #334155;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
            grid-column: 1 / -1;
        }
        .empty-state span { font-size: 48px; display: block; margin-bottom: 12px; }
    </style>
</head>
<body>

    <!-- CABECERA DE CONSULTA HISTÓRICA -->
    <header class="header-historico">
        <div class="header-content">
            <div class="header-left">
                <span class="badge-historico">🏛️ GESTIONES ANTERIORES</span>
                <div>
                    <h1 class="header-title">Consulta Histórica GAMLP</h1>
                    <p class="header-sub">Base de datos de 2.938 equipos y activos anteriores (Solo Lectura)</p>
                </div>
            </div>
            <a href="/movil" class="btn-ir-actual">
                <span>🚀</span> Ir al Relevamiento 2026 Actual
            </a>
        </div>
    </header>

    <main class="container">
        <!-- AVISO DE SOLO LECTURA -->
        <div class="banner-readonly">
            <span style="font-size: 22px;">🔒</span>
            <div>
                <strong>Modo Histórico de Solo Lectura:</strong> Esta vista consulta el archivo de producción anterior para verificar datos, modelos y antecedentes. Los nuevos registros deben realizarse en la <a href="/movil" style="color: #92400E; font-weight: 800; text-decoration: underline;">Suite Relevamiento 2026</a>.
            </div>
        </div>

        <!-- SELECTORES Y FILTROS -->
        <div class="card-filtros">
            <div class="grid-selectores">
                <div class="sel-group">
                    <label for="sel_red">🌐 Red de Salud:</label>
                    <select id="sel_red" class="sel-control" onchange="alCambiarRed()">
                        <option value="">Cargando redes...</option>
                    </select>
                </div>
                <div class="sel-group">
                    <label for="sel_centro">🏥 Centro de Salud:</label>
                    <select id="sel_centro" class="sel-control" onchange="alCambiarCentro()">
                        <option value="">Cargando centros...</option>
                    </select>
                </div>
            </div>

            <!-- BOTONES DE FILTRO DE TIPO DE ACTIVO -->
            <div class="asset-type-bar">
                <button type="button" class="asset-btn active" id="btn_tipo_todo" onclick="filtrarTipoActivo('TODO')">
                    <span>🌐</span> Ver Todo (<span id="cnt_todo">0</span>)
                </button>
                <button type="button" class="asset-btn" id="btn_tipo_equipos" onclick="filtrarTipoActivo('EQUIPOS')">
                    <span>🩺</span> Solo Equipos Médicos (<span id="cnt_equipos">0</span>)
                </button>
                <button type="button" class="asset-btn" id="btn_tipo_muebles" onclick="filtrarTipoActivo('MUEBLES')">
                    <span>🛋️</span> Solo Muebles y TI (<span id="cnt_muebles">0</span>)
                </button>
            </div>
        </div>

        <!-- BÚSQUEDA Y TOTALES -->
        <div class="search-stats-bar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="busq_activos" class="search-input" placeholder="Buscar por código AF, nombre, modelo, serie o área..." oninput="filtrarListaActivos()">
            </div>
            <div class="stats-badge">
                Activos visibles: <span id="lbl_visibles" style="color: #0284C7;">0</span>
            </div>
        </div>

        <!-- GRID DE TARJETAS -->
        <div id="grid_activos" class="cards-grid">
            <div class="empty-state">
                <span>⏳</span>
                Cargando registros históricos...
            </div>
        </div>
    </main>

    <!-- MODAL DE FICHA TÉCNICA (SOLO LECTURA) -->
    <div id="modal_detalle" class="modal-overlay" onclick="if(event.target === this) cerrarModalDetalle()">
        <div class="modal-sheet">
            <div class="modal-header">
                <div class="modal-title">
                    <span id="mod_tipo_icon">🩺</span>
                    <span id="mod_titulo">Ficha Técnica Histórica</span>
                </div>
                <button class="btn-close" onclick="cerrarModalDetalle()">✕</button>
            </div>
            <div class="modal-body" id="mod_contenido">
                <!-- Se llena dinámicamente con JavaScript -->
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT GLOBAL HISTÓRICO -->
    <script>
        let SEDES_HISTORICAS = { redes: [], centros: [] };
        let LISTA_TOTAL_EQUIPOS = [];
        let LISTA_TOTAL_MUEBLES = [];
        let TIPO_ACTIVO_FILTRO = 'TODO'; // 'TODO', 'EQUIPOS', 'MUEBLES'
        let LIMITE_MOSTRAR = 60;
        let ULTIMA_LISTA_FILTRADA = [];

        window.addEventListener('DOMContentLoaded', async () => {
            await cargarSedesHistoricas();
        });

        // 1. Cargar Redes y Centros Históricos
        async function cargarSedesHistoricas() {
            try {
                const res = await fetch('/api/historico/sedes');
                SEDES_HISTORICAS = await res.json();

                const selRed = document.getElementById('sel_red');
                selRed.innerHTML = '<option value="">-- Todas las Redes de Salud (GAMLP - 2.938 Equipos) --</option>';

                (SEDES_HISTORICAS.redes || []).forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r.nombre;
                    opt.textContent = r.nombre;
                    opt.setAttribute('data-id', r.id);
                    selRed.appendChild(opt);
                });

                selRed.selectedIndex = 0;
                actualizarSelectorCentros();
                await alCambiarCentro();
            } catch (e) {
                console.error("Error cargando sedes:", e);
                document.getElementById('grid_activos').innerHTML = `
                    <div class="empty-state">
                        <span>⚠️</span>
                        Error conectando con la base histórica: ${e.message}
                    </div>
                `;
            }
        }

        // 2. Actualizar lista de centros según red seleccionada
        function actualizarSelectorCentros() {
            const redSel = document.getElementById('sel_red').value;
            const redes = SEDES_HISTORICAS.redes || [];
            const rObj = redes.find(r => r.nombre === redSel);
            const rId = rObj ? rObj.id : null;

            const centros = (SEDES_HISTORICAS.centros || []).filter(c => !rId || c.red_salud_id === rId);
            const selCen = document.getElementById('sel_centro');
            selCen.innerHTML = '<option value="">-- Todos los Centros de Salud (Ver Todo) --</option>';

            centros.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.nombre;
                const cnt = (c.total_equipos !== undefined) ? ` (${c.total_equipos} equipos)` : '';
                opt.textContent = `${c.nombre}${cnt}`;
                selCen.appendChild(opt);
            });

            selCen.selectedIndex = 0;
        }

        function alCambiarRed() {
            actualizarSelectorCentros();
            alCambiarCentro();
        }

        // 3. Al cambiar Centro de Salud -> Cargar Equipos y Muebles
        async function alCambiarCentro() {
            const redSel = document.getElementById('sel_red').value;
            const cenSel = document.getElementById('sel_centro').value;
            const grid = document.getElementById('grid_activos');
            grid.innerHTML = `
                <div class="empty-state">
                    <span>⏳</span>
                    Cargando activos históricos de ${cenSel || redSel || 'toda la red GAMLP'}...
                </div>
            `;

            try {
                // Cargar equipos históricos
                const urlEq = `/api/historico/equipos?centro=${encodeURIComponent(cenSel)}&red=${encodeURIComponent(redSel)}`;
                const resEq = await fetch(urlEq);
                LISTA_TOTAL_EQUIPOS = await resEq.json();

                // Cargar muebles históricos
                const urlMu = `/api/historico/muebles?centro=${encodeURIComponent(cenSel)}&red=${encodeURIComponent(redSel)}`;
                const resMu = await fetch(urlMu);
                LISTA_TOTAL_MUEBLES = await resMu.json();

                actualizarContadores();
                LIMITE_MOSTRAR = 60;
                filtrarListaActivos();
            } catch (e) {
                console.error("Error cargando activos:", e);
                grid.innerHTML = `
                    <div class="empty-state">
                        <span>⚠️</span>
                        Error al consultar datos históricos: ${e.message}
                    </div>
                `;
            }
        }

        // 4. Actualizar contadores de botones
        function actualizarContadores() {
            const numEq = LISTA_TOTAL_EQUIPOS.length;
            const numMu = LISTA_TOTAL_MUEBLES.length;
            const numTodo = numEq + numMu;

            document.getElementById('cnt_todo').textContent = numTodo;
            document.getElementById('cnt_equipos').textContent = numEq;
            document.getElementById('cnt_muebles').textContent = numMu;
        }

        // 5. Cambiar tipo de activo activo
        function filtrarTipoActivo(tipo) {
            TIPO_ACTIVO_FILTRO = tipo;
            document.querySelectorAll('.asset-btn').forEach(b => b.classList.remove('active'));
            if (tipo === 'TODO') document.getElementById('btn_tipo_todo').classList.add('active');
            if (tipo === 'EQUIPOS') document.getElementById('btn_tipo_equipos').classList.add('active');
            if (tipo === 'MUEBLES') document.getElementById('btn_tipo_muebles').classList.add('active');
            LIMITE_MOSTRAR = 60;
            filtrarListaActivos();
        }

        // 6. Filtrar y Renderizar
        function filtrarListaActivos() {
            const q = (document.getElementById('busq_activos').value || '').trim().toLowerCase();
            let lista = [];

            if (TIPO_ACTIVO_FILTRO === 'TODO' || TIPO_ACTIVO_FILTRO === 'EQUIPOS') {
                const eqs = LISTA_TOTAL_EQUIPOS.map(e => ({ ...e, _tipo: 'EQUIPO' }));
                lista = lista.concat(eqs);
            }
            if (TIPO_ACTIVO_FILTRO === 'TODO' || TIPO_ACTIVO_FILTRO === 'MUEBLES') {
                const mus = LISTA_TOTAL_MUEBLES.map(m => ({ ...m, _tipo: 'MUEBLE' }));
                lista = lista.concat(mus);
            }

            if (q) {
                lista = lista.filter(item => {
                    const idStr = String(item.id || item.codigo_sispam || '').toLowerCase();
                    const nomStr = String(item.nombre || item.descripcion || item.tipo_activo || '').toLowerCase();
                    const modStr = String(item.modelo || '').toLowerCase();
                    const marStr = String(item.marca || '').toLowerCase();
                    const serStr = String(item.numero_serie || item.serie || '').toLowerCase();
                    const areStr = String(item.area || item.ubicacion || '').toLowerCase();
                    const cenStr = String(item.centro_salud_nombre || '').toLowerCase();
                    return idStr.includes(q) || nomStr.includes(q) || modStr.includes(q) || marStr.includes(q) || serStr.includes(q) || areStr.includes(q) || cenStr.includes(q);
                });
            }

            renderizarTarjetas(lista);
        }

        function renderizarTarjetas(lista) {
            ULTIMA_LISTA_FILTRADA = lista;
            const grid = document.getElementById('grid_activos');
            document.getElementById('lbl_visibles').textContent = lista.length;

            if (lista.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <span>🔍</span>
                        No se encontraron activos históricos con los filtros seleccionados.
                    </div>
                `;
                return;
            }

            const rebanada = lista.slice(0, LIMITE_MOSTRAR);
            grid.innerHTML = '';
            rebanada.forEach((item) => {
                const esEquipo = item._tipo === 'EQUIPO';
                const icono = esEquipo ? '🩺' : '🛋️';
                const titulo = esEquipo ? (item.nombre || 'Equipo Médico') : (item.descripcion || item.tipo_activo || 'Mueble / TI');
                const codigoAF = esEquipo ? item.id : (item.codigo_sispam || `MUE-${item.id}`);
                const area = esEquipo ? (item.area || 'General') : (item.ubicacion || 'General');
                const centroNom = item.centro_salud_nombre || item.ubicacion || 'Centro de Salud';
                const marca = item.marca || 'S/M';
                const modelo = item.modelo || 'S/M';
                const serie = item.numero_serie || item.serie || 'S/N';
                const estado = item.estado || item.estado_conservacion || 'Operativo';

                let claseEstado = 'st-bueno';
                const estLower = estado.toLowerCase();
                if (estLower.includes('reg') || estLower.includes('man')) claseEstado = 'st-regular';
                else if (estLower.includes('mal') || estLower.includes('baja') || estLower.includes('inop')) claseEstado = 'st-malo';

                const card = document.createElement('div');
                card.className = 'card-asset';
                card.onclick = () => abrirModalDetalle(item);

                card.innerHTML = `
                    <div>
                        <div class="card-asset-header">
                            <div class="asset-icon-title">
                                <span class="asset-icon">${icono}</span>
                                <div class="asset-title">${escaparHtml(titulo)}</div>
                            </div>
                            <span class="badge-af">${escaparHtml(codigoAF)}</span>
                        </div>
                        <div class="asset-meta">
                            <div>🏥 Centro: <strong>${escaparHtml(centroNom)}</strong></div>
                            <div>📍 Área: <span>${escaparHtml(area)}</span></div>
                            <div>🏷️ Marca/Mod: <span>${escaparHtml(marca)} / ${escaparHtml(modelo)}</span></div>
                            <div>🔢 Serie: <span>${escaparHtml(serie)}</span></div>
                        </div>
                    </div>
                    <div class="card-asset-footer">
                        <span class="badge-estado ${claseEstado}">${escaparHtml(estado)}</span>
                        <span class="btn-ver-detalle">👁️ Ver Ficha</span>
                    </div>
                `;
                grid.appendChild(card);
            });

            if (lista.length > LIMITE_MOSTRAR) {
                const btnMas = document.createElement('div');
                btnMas.style.gridColumn = '1 / -1';
                btnMas.style.textAlign = 'center';
                btnMas.style.marginTop = '15px';
                btnMas.innerHTML = `
                    <button type="button" class="btn-ir-actual" style="background:#0284C7; font-size:13.5px; padding:12px 28px; cursor:pointer;" onclick="cargarMasTarjetas()">
                        ⬇️ Cargar más activos (mostrando ${rebanada.length} de ${lista.length})
                    </button>
                `;
                grid.appendChild(btnMas);
            }
        }

        function cargarMasTarjetas() {
            LIMITE_MOSTRAR += 60;
            renderizarTarjetas(ULTIMA_LISTA_FILTRADA);
        }

        // 7. Modal de Ficha Técnica
        function abrirModalDetalle(item) {
            const esEquipo = item._tipo === 'EQUIPO';
            document.getElementById('mod_tipo_icon').textContent = esEquipo ? '🩺' : '🛋️';
            document.getElementById('mod_titulo').textContent = esEquipo ? 'Ficha de Equipo Médico Histórico' : 'Ficha de Mueble / TI Histórico';

            const cont = document.getElementById('mod_contenido');
            if (esEquipo) {
                cont.innerHTML = `
                    <div class="det-section-title">📋 Identificación General</div>
                    <div class="det-grid">
                        <div class="det-item"><span class="det-label">Código Activo Fijo (AF):</span><span class="det-value" style="font-family:monospace; color:#0284C7; font-weight:800;">${escaparHtml(item.id || 'S/C')}</span></div>
                        <div class="det-item"><span class="det-label">Estado Operativo:</span><span class="det-value">${escaparHtml(item.estado || 'No especificado')}</span></div>
                        <div class="det-item"><span class="det-label">Centro de Salud:</span><span class="det-value">${escaparHtml(item.centro_salud_nombre || 'No asignado')}</span></div>
                        <div class="det-item"><span class="det-label">Red de Salud:</span><span class="det-value">${escaparHtml(item.red_salud_nombre || 'No asignada')}</span></div>
                        <div class="det-item"><span class="det-label">Área / Servicio:</span><span class="det-value">${escaparHtml(item.area || 'General')}</span></div>
                        <div class="det-item"><span class="det-label">Piso:</span><span class="det-value">${escaparHtml(item.piso || 'PB')}</span></div>
                    </div>

                    <div class="det-section-title">⚙️ Especificaciones Técnicas</div>
                    <div class="det-grid">
                        <div class="det-item"><span class="det-label">Nombre Oficial:</span><span class="det-value">${escaparHtml(item.nombre || 'S/N')}</span></div>
                        <div class="det-item"><span class="det-label">Marca:</span><span class="det-value">${escaparHtml(item.marca || 'S/M')}</span></div>
                        <div class="det-item"><span class="det-label">Modelo:</span><span class="det-value">${escaparHtml(item.modelo || 'S/M')}</span></div>
                        <div class="det-item"><span class="det-label">Número de Serie:</span><span class="det-value">${escaparHtml(item.numero_serie || 'S/N')}</span></div>
                        <div class="det-item"><span class="det-label">Nivel de Criticidad:</span><span class="det-value" style="font-weight:800; color:#B45309;">${escaparHtml(item.criticidad || 'No evaluada')}</span></div>
                        <div class="det-item"><span class="det-label">Garantía:</span><span class="det-value">${escaparHtml(item.garantia || 'Sin Garantía')}</span></div>
                    </div>

                    <div class="det-section-title">📝 Contexto y Funciones Operacionales</div>
                    <div class="det-item"><span class="det-label">Contexto Operacional:</span><div class="det-box">${escaparHtml(item.contexto_operacional || 'No especificado.')}</div></div>
                    <div class="det-item"><span class="det-label">Funciones del Equipo:</span><div class="det-box">${escaparHtml(item.funciones_equipo || 'No especificadas.')}</div></div>

                    <div class="det-section-title">🔧 Mantenimiento y Fallas Comunes</div>
                    <div class="det-item"><span class="det-label">Causas de Fallo:</span><div class="det-box">${escaparHtml(item.causas_fallo || 'No especificadas.')}</div></div>
                    <div class="det-item"><span class="det-label">Acciones Preventivas:</span><div class="det-box">${escaparHtml(item.acciones_preventivas || 'No especificadas.')}</div></div>
                    <div class="det-item"><span class="det-label">Observaciones Generales:</span><div class="det-box">${escaparHtml(item.observaciones || 'Sin observaciones registradas.')}</div></div>
                `;
            } else {
                cont.innerHTML = `
                    <div class="det-section-title">📋 Identificación del Mueble / TI</div>
                    <div class="det-grid">
                        <div class="det-item"><span class="det-label">Código SISPAM / AF:</span><span class="det-value" style="font-family:monospace; color:#0284C7; font-weight:800;">${escaparHtml(item.codigo_sispam || item.id || 'S/C')}</span></div>
                        <div class="det-item"><span class="det-label">Tipo de Activo:</span><span class="det-value">${escaparHtml(item.tipo_activo || 'Mueble')}</span></div>
                        <div class="det-item"><span class="det-label">Ubicación / Centro:</span><span class="det-value">${escaparHtml(item.ubicacion || 'General')}</span></div>
                        <div class="det-item"><span class="det-label">Estado de Conservación:</span><span class="det-value">${escaparHtml(item.estado_conservacion || 'Bueno')}</span></div>
                        <div class="det-item"><span class="det-label">Marca:</span><span class="det-value">${escaparHtml(item.marca || 'S/M')}</span></div>
                        <div class="det-item"><span class="det-label">Modelo / Serie:</span><span class="det-value">${escaparHtml(item.modelo || 'S/M')} - ${escaparHtml(item.serie || 'S/N')}</span></div>
                    </div>
                    <div class="det-section-title">👤 Asignación y Custodio</div>
                    <div class="det-grid">
                        <div class="det-item"><span class="det-label">Persona Asignada:</span><span class="det-value">${escaparHtml(item.persona_asignada || 'No asignada')}</span></div>
                        <div class="det-item"><span class="det-label">Cargo / C.I.:</span><span class="det-value">${escaparHtml(item.cargo_asignado || 'N/A')} - ${escaparHtml(item.ci_asignado || 'N/A')}</span></div>
                    </div>
                    <div class="det-section-title">📝 Descripción y Observaciones</div>
                    <div class="det-item"><div class="det-box">${escaparHtml(item.descripcion || item.observaciones_de_asignacion || 'Sin detalle adicional.')}</div></div>
                `;
            }

            document.getElementById('modal_detalle').style.display = 'flex';
        }

        function cerrarModalDetalle() {
            document.getElementById('modal_detalle').style.display = 'none';
        }

        function escaparHtml(str) {
            if (!str) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
    </script>
</body>
</html>
"""
