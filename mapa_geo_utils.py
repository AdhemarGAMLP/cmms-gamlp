# -*- coding: utf-8 -*-
"""
UTILIDADES GEOESPACIALES Y GENERADOR DE MAPA SATELITAL / CALOR GAMLP (100% $0 COSTO)
====================================================================================
Contiene:
1. Catálogo de Coordenadas GPS Reales de Centros de Salud y Hospitales del GAMLP.
2. Generador de Mapa Interactivo HTML (Leaflet.js + ESRI Satellite + Heatmap).
"""

import json

# Coordenadas geográficas aproximadas oficiales de centros y hospitales de La Paz
COORDENADAS_CENTROS_GAMLP = {
    # RED 1 - SUR OESTE (COTAHUMA)
    "HOSPITAL MUNICIPAL COTAHUMA": {"lat": -16.5167, "lon": -68.1481, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Segundo Nivel"},
    "C.M.I. TEMBLADERANI": {"lat": -16.5160, "lon": -68.1485, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Centro de Salud Integral"},
    "CENTRO DE SALUD PASANKERI": {"lat": -16.5125, "lon": -68.1630, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD ALPACOMA": {"lat": -16.5290, "lon": -68.1680, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD LLOJETA": {"lat": -16.5240, "lon": -68.1510, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD BAJO SAN PEDRO": {"lat": -16.5050, "lon": -68.1410, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD TACAGUA": {"lat": -16.5080, "lon": -68.1580, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD FARO MURILLO": {"lat": -16.5110, "lon": -68.1640, "red": "RED 1-SUR OESTE (MACRODISTRITO COTAHUMA)", "nivel": "Primer Nivel"},

    # RED 2 - NOR OESTE (MAX PAREDES)
    "HOSPITAL MUNICIPAL LA PORTADA": {"lat": -16.4895, "lon": -68.1652, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Segundo Nivel"},
    "ALTO MCAL. SANTA CRUZ": {"lat": -16.4950, "lon": -68.1620, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Centro de Salud Integral"},
    "C.M.I. ALTO MCAL. SANTA CRUZ": {"lat": -16.4950, "lon": -68.1620, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Centro de Salud Integral"},
    "CENTRO DE SALUD CHAMOCO CHICO": {"lat": -16.4920, "lon": -68.1550, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD MUNAYPATA": {"lat": -16.4850, "lon": -68.1610, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD VILLA VICTORIA": {"lat": -16.4880, "lon": -68.1490, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD PURA PURA": {"lat": -16.4780, "lon": -68.1540, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD SAGRADO CORAZON DE JESUS": {"lat": -16.4980, "lon": -68.1470, "red": "RED 2-NOR OESTE (MACRODISTRITO MAX PAREDES)", "nivel": "Primer Nivel"},

    # RED 3 - NORTE CENTRAL (PERIFÉRICA / CENTRO)
    "HOSPITAL MUNICIPAL LA MERCED": {"lat": -16.4740, "lon": -68.1180, "red": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "nivel": "Segundo Nivel"},
    "CENTRO DE SALUD ACHACHICALA": {"lat": -16.4670, "lon": -68.1420, "red": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD VILLA FATIMA": {"lat": -16.4790, "lon": -68.1210, "red": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD 18 DE MAYO": {"lat": -16.4710, "lon": -68.1290, "red": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD EL TEJAR": {"lat": -16.4940, "lon": -68.1440, "red": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD ASISTENCIA PUBLICA": {"lat": -16.4985, "lon": -68.1325, "red": "RED 3-NORTE CENTRAL (MACRODISTRITO PERIFERICA CENTRAL)", "nivel": "Centro de Salud Integral"},

    # RED 4 - SAN ANTONIO
    "HOSPITAL MUNICIPAL SAN ANTONIO": {"lat": -16.4990, "lon": -68.1080, "red": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "nivel": "Segundo Nivel"},
    "CENTRO DE SALUD KUPINI": {"lat": -16.5080, "lon": -68.1010, "red": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD VILLA ARMONIA": {"lat": -16.5020, "lon": -68.1150, "red": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD PAMPAHASI": {"lat": -16.4920, "lon": -68.0980, "red": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD SAN ISIDRO": {"lat": -16.5120, "lon": -68.1100, "red": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD ESCOBAR URIA": {"lat": -16.4860, "lon": -68.0930, "red": "RED 4-SAN ANTONIO (MACRODISTRITO SAN ANTONIO)", "nivel": "Primer Nivel"},

    # RED 5 - SUR (MACRODISTRITO SUR / MALLASA)
    "HOSPITAL MUNICIPAL LOS PINOS": {"lat": -16.5410, "lon": -68.0770, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Segundo Nivel"},
    "C.M.I. CHASQUIPAMPA": {"lat": -16.5360, "lon": -68.0580, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Centro de Salud Integral"},
    "CENTRO DE SALUD CHASQUIPAMPA": {"lat": -16.5360, "lon": -68.0580, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Centro de Salud Integral"},
    "CENTRO DE SALUD OVEJUYO": {"lat": -16.5390, "lon": -68.0430, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD BELLA VISTA": {"lat": -16.5290, "lon": -68.0900, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD OBRAJES": {"lat": -16.5230, "lon": -68.1070, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD BOLOGNIA": {"lat": -16.5270, "lon": -68.0810, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD COTA COTA": {"lat": -16.5340, "lon": -68.0700, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD MALLASA": {"lat": -16.5640, "lon": -68.0890, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Primer Nivel"},
    "CENTRO DE SALUD ACHUMANI": {"lat": -16.5220, "lon": -68.0640, "red": "RED 5-SUR (MACRODISTRITO SUR)", "nivel": "Primer Nivel"},

    # RED RURAL (ZONGO / HAMPATURI)
    "CENTRO DE SALUD ZONGO": {"lat": -16.1150, "lon": -68.0120, "red": "RED 6-RURAL (ZONGO/HAMPATURI)", "nivel": "Puesto de Salud"},
    "CENTRO DE SALUD HAMPATURI": {"lat": -16.4350, "lon": -68.0350, "red": "RED 6-RURAL (ZONGO/HAMPATURI)", "nivel": "Puesto de Salud"}
}

def obtener_coordenada_centro(nombre_centro, red_nombre=""):
    """Busca o aproxima la coordenada GPS de un centro de salud del GAMLP."""
    if not nombre_centro:
        return None
    
    nom_clean = nombre_centro.strip().upper()
    if nom_clean in COORDENADAS_CENTROS_GAMLP:
        return COORDENADAS_CENTROS_GAMLP[nom_clean]
        
    for k, v in COORDENADAS_CENTROS_GAMLP.items():
        if k in nom_clean or nom_clean in k:
            return v
            
    # Coordenadas de contingencia por Red
    red_upper = str(red_nombre).upper()
    if "RED 1" in red_upper or "COTAHUMA" in red_upper:
        return {"lat": -16.5130, "lon": -68.1520, "red": red_nombre, "nivel": "Primer Nivel"}
    elif "RED 2" in red_upper or "MAX PAREDES" in red_upper:
        return {"lat": -16.4910, "lon": -68.1580, "red": red_nombre, "nivel": "Primer Nivel"}
    elif "RED 3" in red_upper or "PERIFERICA" in red_upper:
        return {"lat": -16.4750, "lon": -68.1250, "red": red_nombre, "nivel": "Primer Nivel"}
    elif "RED 4" in red_upper or "SAN ANTONIO" in red_upper:
        return {"lat": -16.5010, "lon": -68.1050, "red": red_nombre, "nivel": "Primer Nivel"}
    elif "RED 5" in red_upper or "SUR" in red_upper:
        return {"lat": -16.5350, "lon": -68.0720, "red": red_nombre, "nivel": "Primer Nivel"}
        
    # Centro geográfico de La Paz por defecto
    return {"lat": -16.5010, "lon": -68.1400, "red": red_nombre or "GAMLP", "nivel": "Primer Nivel"}


def consolidar_datos_geoespaciales(equipos, sedes_data=None):
    """
    Agrupa los equipos por Centro de Salud y calcula métricas para el mapa:
    Total equipos, % operatividad, desglose de criticidad y coordenadas.
    """
    centros_map = {}

    for eq in equipos:
        cen_nom = str(eq.get("centro_salud_nombre") or eq.get("centro_salud") or "Centro General").strip()
        red_nom = str(eq.get("red_salud_nombre") or eq.get("red_salud") or "GAMLP").strip()
        
        if cen_nom not in centros_map:
            coords = obtener_coordenada_centro(cen_nom, red_nom)
            centros_map[cen_nom] = {
                "nombre": cen_nom,
                "red": red_nom,
                "lat": coords["lat"] if coords else -16.5010,
                "lon": coords["lon"] if coords else -16.1400,
                "nivel": coords.get("nivel", "Primer Nivel") if coords else "Primer Nivel",
                "total_equipos": 0,
                "operativos": 0,
                "baja_falla": 0,
                "riesgo_alto": 0,
                "riesgo_medio": 0,
                "riesgo_bajo": 0,
                "equipos_lista": []
            }

        c_data = centros_map[cen_nom]
        c_data["total_equipos"] += 1
        
        estado = str(eq.get("estado", "Operativo")).lower()
        if "baja" in estado or "inoperante" in estado:
            c_data["baja_falla"] += 1
        else:
            c_data["operativos"] += 1

        criticidad = str(eq.get("criticidad", "Riesgo Medio")).lower()
        if "alto" in criticidad:
            c_data["riesgo_alto"] += 1
        elif "medio" in criticidad:
            c_data["riesgo_medio"] += 1
        else:
            c_data["riesgo_bajo"] += 1

        if len(c_data["equipos_lista"]) < 8:
            c_data["equipos_lista"].append({
                "af": eq.get("id"),
                "nombre": eq.get("nombre"),
                "area": eq.get("area") or eq.get("servicio") or "General",
                "estado": eq.get("estado", "Operativo"),
                "criticidad": eq.get("criticidad", "Medio")
            })

    # Calcular porcentajes
    lista_centros = list(centros_map.values())
    for c in lista_centros:
        tot = max(1, c["total_equipos"])
        c["porcentaje_operatividad"] = round((c["operativos"] / tot) * 100, 1)

    return lista_centros


def generar_html_mapa_gamlp(centros_geo, red_filtro=None):
    """
    Genera el archivo HTML interactivo autónomo con Leaflet.js,
    capas satelitales ESRI, mapa de calor y popups con métricas biomédicas.
    """
    centros_filtrados = centros_geo
    if red_filtro and not str(red_filtro).startswith("[ Todas"):
        centros_filtrados = [c for c in centros_geo if c.get("red") == red_filtro]

    # Datos para mapa de calor: [lat, lon, intensidad]
    puntos_calor = []
    max_eq = max([c["total_equipos"] for c in centros_filtrados] + [1])
    for c in centros_filtrados:
        intensidad = min(1.0, max(0.2, c["total_equipos"] / max_eq))
        puntos_calor.append([c["lat"], c["lon"], intensidad])

    centros_json = json.dumps(centros_filtrados, ensure_ascii=False)
    puntos_calor_json = json.dumps(puntos_calor)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Satelital y de Calor de Equipos GAMLP</title>
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
        html, body {{ height: 100%; width: 100%; overflow: hidden; background: #0F172A; }}
        #map {{ height: 100%; width: 100%; position: absolute; top: 0; left: 0; }}
        
        /* Panel Superior Flotante */
        .top-panel {{
            position: absolute;
            top: 16px;
            left: 16px;
            z-index: 1000;
            background: rgba(15, 23, 42, 0.90);
            backdrop-filter: blur(10px);
            padding: 14px 18px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #F8FAFC;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            max-width: 380px;
        }}
        .top-panel h1 {{ font-size: 16px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 8px; }}
        .top-panel p {{ font-size: 12px; color: #94A3B8; margin-top: 4px; }}
        
        /* Botones de Control de Capas */
        .controls-row {{
            margin-top: 12px;
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .btn-layer {{
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid #334155;
            color: #E2E8F0;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-layer:hover, .btn-layer.active {{
            background: #2563EB;
            color: #FFFFFF;
            border-color: #3B82F6;
        }}

        /* Tarjetas de Estadísticas Inferiores */
        .bottom-stats {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: rgba(15, 23, 42, 0.90);
            backdrop-filter: blur(10px);
            padding: 10px 20px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #F8FAFC;
            display: flex;
            gap: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }}
        .stat-item {{ display: flex; align-items: center; gap: 8px; font-size: 13px; }}
        .stat-num {{ font-weight: 700; font-size: 15px; color: #38BDF8; }}

        /* Popups Estilizados */
        .leaflet-popup-content-wrapper {{
            background: #1E293B;
            color: #F8FAFC;
            border-radius: 12px;
            border: 1px solid #334155;
            padding: 4px;
            box-shadow: 0 12px 28px rgba(0,0,0,0.5);
        }}
        .leaflet-popup-tip {{ background: #1E293B; }}
        .popup-header {{
            border-bottom: 1px solid #334155;
            padding-bottom: 8px;
            margin-bottom: 8px;
        }}
        .popup-title {{ font-size: 14px; font-weight: 700; color: #FFFFFF; }}
        .popup-sub {{ font-size: 11px; color: #94A3B8; }}
        .popup-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            margin-top: 4px;
        }}
        .badge-op {{ background: #059669; color: #ECFDF5; }}
        .badge-baja {{ background: #DC2626; color: #FEF2F2; }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin: 8px 0;
            font-size: 12px;
        }}
        .stat-box {{
            background: #0F172A;
            padding: 6px 8px;
            border-radius: 6px;
            border: 1px solid #334155;
        }}
        .stat-box-lbl {{ font-size: 10px; color: #64748B; }}
        .stat-box-val {{ font-weight: 700; color: #E2E8F0; }}
        
        .eq-mini-list {{
            max-height: 100px;
            overflow-y: auto;
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px dashed #334155;
            font-size: 11px;
        }}
        .eq-mini-item {{
            display: flex;
            justify-content: space-between;
            padding: 2px 0;
            color: #CBD5E1;
        }}
    </style>
</head>
<body>
    <div id="map"></div>

    <!-- Panel Superior -->
    <div class="top-panel">
        <h1>🛰️ GIS GAMLP: Mapa Satelital</h1>
        <p>Censo Territorial y Densidad de Equipamiento Biomédico</p>
        <div class="controls-row">
            <button class="btn-layer active" id="btn-sat" onclick="cambiarCapa('sat')">🛰️ Satelital</button>
            <button class="btn-layer" id="btn-osm" onclick="cambiarCapa('osm')">🗺️ Calles</button>
            <button class="btn-layer" id="btn-dark" onclick="cambiarCapa('dark')">🌙 Oscuro</button>
            <button class="btn-layer active" id="btn-heat" onclick="toggleCalor()">🔥 Mapa de Calor</button>
            <button class="btn-layer active" id="btn-markers" onclick="toggleMarcadores()">🏥 Hospitales</button>
        </div>
    </div>

    <!-- Barra Inferior de Métricas -->
    <div class="bottom-stats">
        <div class="stat-item">
            <span>🏥 Centros Mapeados:</span>
            <span class="stat-num" id="stat-centros">{len(centros_filtrados)}</span>
        </div>
        <div class="stat-item">
            <span>📦 Total Equipos:</span>
            <span class="stat-num" id="stat-equipos">{sum(c["total_equipos"] for c in centros_filtrados)}</span>
        </div>
        <div class="stat-item">
            <span>🟢 Operatividad Global:</span>
            <span class="stat-num" id="stat-op" style="color: #4ADE80;">{round((sum(c["operativos"] for c in centros_filtrados) / max(1, sum(c["total_equipos"] for c in centros_filtrados))) * 100, 1)}%</span>
        </div>
    </div>

    <!-- Scripts de Leaflet y Plugins -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    
    <script>
        const centrosData = {centros_json};
        const heatData = {puntos_calor_json};

        // 1. Inicializar Mapa centrado en La Paz (-16.501, -68.140)
        const map = L.map('map', {{
            center: [-16.5010, -68.1400],
            zoom: 13,
            zoomControl: false
        }});
        L.control.zoom({{ position: 'topright' }}).addTo(map);

        // 2. Capas Base Satelitales y de Mapa
        const satLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            attribution: 'Tiles &copy; Esri &mdash; GAMLP',
            maxZoom: 19
        }});

        const osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}.{{y}}.png', {{
            attribution: '&copy; OpenStreetMap &mdash; GAMLP',
            maxZoom: 19
        }});

        const darkLayer = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; CartoDB &mdash; GAMLP',
            maxZoom: 19
        }});

        satLayer.addTo(map);
        let capaActual = satLayer;

        function cambiarCapa(tipo) {{
            map.removeLayer(capaActual);
            document.querySelectorAll('.controls-row .btn-layer').forEach(b => {{
                if (['btn-sat', 'btn-osm', 'btn-dark'].includes(b.id)) b.classList.remove('active');
            }});

            if (tipo === 'sat') {{
                satLayer.addTo(map);
                capaActual = satLayer;
                document.getElementById('btn-sat').classList.add('active');
            }} else if (tipo === 'osm') {{
                osmLayer.addTo(map);
                capaActual = osmLayer;
                document.getElementById('btn-osm').classList.add('active');
            }} else {{
                darkLayer.addTo(map);
                capaActual = darkLayer;
                document.getElementById('btn-dark').classList.add('active');
            }}
        }}

        // 3. Capa de Mapa de Calor (Heatmap)
        let heatLayer = L.heatLayer(heatData, {{
            radius: 35,
            blur: 20,
            maxZoom: 16,
            max: 1.0,
            gradient: {{ 0.2: '#3B82F6', 0.4: '#10B981', 0.6: '#FBBF24', 0.8: '#F97316', 1.0: '#EF4444' }}
        }}).addTo(map);

        let calorVisible = true;
        function toggleCalor() {{
            const btn = document.getElementById('btn-heat');
            if (calorVisible) {{
                map.removeLayer(heatLayer);
                btn.classList.remove('active');
                calorVisible = false;
            }} else {{
                heatLayer.addTo(map);
                btn.classList.add('active');
                calorVisible = true;
            }}
        }}

        // 4. Capa de Marcadores de Centros de Salud
        const markersGroup = L.markerClusterGroup({{
            maxClusterRadius: 35,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false
        }});

        function crearIconoCentro(nivel, totalEq) {{
            let color = '#3B82F6';
            if (nivel.includes('Segundo') || nivel.includes('Hospital')) color = '#8B5CF6';
            else if (nivel.includes('Integral')) color = '#06B6D4';
            else if (nivel.includes('Puesto')) color = '#10B981';

            return L.divIcon({{
                className: 'custom-pin',
                html: `<div style="
                    background: ${{color}};
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 11px;
                    border: 2px solid white;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
                ">${{totalEq}}</div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            }});
        }}

        centrosData.forEach(c => {{
            const marker = L.marker([c.lat, c.lon], {{
                icon: crearIconoCentro(c.nivel, c.total_equipos)
            }});

            let listaHtml = '';
            if (c.equipos_lista && c.equipos_lista.length > 0) {{
                listaHtml = '<div class="eq-mini-list">' + 
                    c.equipos_lista.map(eq => `<div class="eq-mini-item"><span>• ${{eq.nombre}}</span><span style="color:#38BDF8;">${{eq.area}}</span></div>`).join('') +
                    '</div>';
            }}

            const popupContent = `
                <div class="popup-header">
                    <div class="popup-title">🏥 ${{c.nombre}}</div>
                    <div class="popup-sub">${{c.red}} | ${{c.nivel}}</div>
                    <span class="popup-badge badge-op">Operatividad: ${{c.porcentaje_operatividad}}%</span>
                </div>
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-box-lbl">Total Equipos:</div>
                        <div class="stat-box-val">${{c.total_equipos}}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-lbl">Operativos:</div>
                        <div class="stat-box-val" style="color: #4ADE80;">${{c.operativos}}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-lbl">Riesgo Alto (IA):</div>
                        <div class="stat-box-val" style="color: #F87171;">${{c.riesgo_alto}}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-lbl">Riesgo Medio:</div>
                        <div class="stat-box-val" style="color: #FBBF24;">${{c.riesgo_medio}}</div>
                    </div>
                </div>
                ${{listaHtml}}
            `;

            marker.bindPopup(popupContent, {{ maxWidth: 300 }});
            markersGroup.addLayer(marker);
        }});

        map.addLayer(markersGroup);
        let marcadoresVisibles = true;

        function toggleMarcadores() {{
            const btn = document.getElementById('btn-markers');
            if (marcadoresVisibles) {{
                map.removeLayer(markersGroup);
                btn.classList.remove('active');
                marcadoresVisibles = false;
            }} else {{
                map.addLayer(markersGroup);
                btn.classList.add('active');
                marcadoresVisibles = true;
            }}
        }}
    </script>
</body>
</html>
"""
    return html
