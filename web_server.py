import threading
import os
import psycopg2.extras
import openpyxl
from openpyxl.styles import Font, Alignment
try:
    import pythoncom
    import win32com.client
except ImportError:
    pythoncom = None
    win32com = None
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from database import obtener_conexion
from datetime import date, datetime
from auth import login
from excel_utils import obtener_ruta_plantilla, escribir_en_celda_segura, marcar_x, escribir_texto_largo, exportar_excel_a_pdf
from config import CARPETAS, CONFIG

app_web = Flask(__name__)
app = app_web  # Alias para servidores WSGI de producción (Gunicorn / Render / Vercel)
app_gui = None  # Referencia global de la GUI de Tkinter para sincronización

# Pantalla de éxito responsiva con enlaces de descarga
HTML_EXITO = """
<!DOCTYPE html><html lang="es"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Éxito</title>
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F2F2F7; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; height: 100vh; text-align: center; }
    .tarjeta { background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); max-width: 450px; width: 100%; box-sizing: border-box; }
    .icono { font-size: 50px; color: #34C759; margin-bottom: 15px; }
    .btn { display: block; background: #007AFF; color: white; text-decoration: none; padding: 14px 25px; border-radius: 10px; font-weight: bold; margin-top: 12px; font-size: 15px; text-align: center; }
    .btn-download-xlsx { background: #34C759; }
    .btn-download-xlsx:active { background: #2eaf4e; }
    .btn-download-pdf { background: #FF9500; }
    .btn-download-pdf:active { background: #e08200; }
    .btn-back { background: #8E8E93; }
    .btn-back:active { background: #7a7a7d; }
</style></head><body>
    <div class="tarjeta">
        <div class="icono">✓</div>
        <h2 style="margin-top:0;">¡Registro Guardado!</h2>
        <p style="color: #666; font-size: 14px; margin-bottom: 25px;">El mantenimiento se ha registrado correctamente en la base de datos y se sincronizó con el software del hospital.</p>
        
        {% if pdf_file %}
        <a href="/descargar/{{ pdf_file }}" class="btn btn-download-pdf">⬇ Descargar Hoja de Trabajo (PDF)</a>
        {% endif %}
        <a href="/equipo/{{ id_equipo }}" class="btn btn-back">Volver al Equipo</a>
    </div>
</body></html>
"""

def generar_excel_ht_web(eq_data, form_data, realizado_por, sello_firma_path=None):
    ruta_plantilla_ht = obtener_ruta_plantilla("plantilla_trabajo.xlsx")
    if not os.path.exists(ruta_plantilla_ht):
        print(f"[ERROR] No se encontró la plantilla en: {ruta_plantilla_ht}")
        return None, None
        
    try:
        wb = openpyxl.load_workbook(ruta_plantilla_ht)
        ws = wb.active
        
        # Escribir campos de cabecera y equipo
        escribir_en_celda_segura(ws, 'F11', eq_data.get('area', ''))
        escribir_en_celda_segura(ws, 'AA11', eq_data.get('servicio', ''))
        escribir_en_celda_segura(ws, 'S21', form_data.get('tipo_ht', '1'))
        escribir_en_celda_segura(ws, 'J15', eq_data.get('nombre', ''))
        escribir_en_celda_segura(ws, 'AE15', str(eq_data.get('id', '')))
        escribir_en_celda_segura(ws, 'E17', eq_data.get('procedencia', ''))
        escribir_en_celda_segura(ws, 'AB17', str(eq_data.get('anio_fab', '')))
        escribir_en_celda_segura(ws, 'E19', eq_data.get('marca', ''))
        escribir_en_celda_segura(ws, 'AB19', eq_data.get('fabricante', ''))
        escribir_en_celda_segura(ws, 'F21', eq_data.get('modelo', ''))
        escribir_en_celda_segura(ws, 'AG21', eq_data.get('numero_serie', ''))
        
        # Fechas
        f_rec_raw = form_data.get('fecha_recepcion', date.today().strftime('%Y-%m-%d'))
        f_ent_raw = form_data.get('fecha_entrega', date.today().strftime('%Y-%m-%d'))
        h_ejec = form_data.get('hora_ejecucion', datetime.now().strftime('%H:%M'))
        try:
            f_rec_dt = datetime.strptime(f_rec_raw, '%Y-%m-%d').date()
            f_rec_str = f_rec_dt.strftime('%d / %m / %Y')
        except:
            f_rec_str = datetime.now().strftime('%d / %m / %Y')
            
        try:
            f_ent_dt = datetime.strptime(f_ent_raw, '%Y-%m-%d').date()
            f_ent_str = f_ent_dt.strftime('%d / %m / %Y')
        except:
            f_ent_str = datetime.now().strftime('%d / %m / %Y')
            
        escribir_en_celda_segura(ws, 'M23', f_rec_str)
        escribir_en_celda_segura(ws, 'I62', f"{f_ent_str}  {h_ejec}")
        
        # Nombre del técnico firmante responsable
        escribir_en_celda_segura(ws, 'J64', realizado_por)
        
        # Condición
        cond = form_data.get('condicion')
        if cond == "Óptimo": marcar_x(ws, 'P26')
        elif cond == "Aceptable": marcar_x(ws, 'W26')
        elif cond == "Crítica": marcar_x(ws, 'AC26')
        elif cond == "Inoperante": marcar_x(ws, 'AJ26')
        elif cond == "F/Servicio": marcar_x(ws, 'AP26')

        # Estado Físico
        est = form_data.get('estado_equipo')
        if est == "Óptimo": marcar_x(ws, 'O29')
        elif est == "Bueno": marcar_x(ws, 'U29')
        elif est == "Regular": marcar_x(ws, 'AB29')
        elif est == "Malo": marcar_x(ws, 'AH29')
        elif est == "Obsoleto": marcar_x(ws, 'AO29')

        # Tipo Mantenimiento
        tipo = form_data.get('tipo')
        if tipo == "Preventivo": marcar_x(ws, 'Q43')
        else: marcar_x(ws, 'AL43')

        # Textos largos
        escribir_texto_largo(ws, 'B33', form_data.get('deficiencia', ''))
        escribir_texto_largo(ws, 'B47', form_data.get('trabajo', ''))
        escribir_texto_largo(ws, 'B53', form_data.get('observaciones', ''))
        
        # Inyectar sello/firma (Imagen) si existe
        if sello_firma_path and os.path.exists(sello_firma_path):
            try:
                from openpyxl.drawing.image import Image as ExcelImage
                img = ExcelImage(sello_firma_path)
                img.width = 145
                img.height = 65
                ws.add_image(img, 'AD60')
            except Exception as ex:
                print(f"[ERROR] No se pudo insertar la firma en Excel: {ex}")
        
        # Nombres de salida
        try:
            f_rec_dt = datetime.strptime(f_rec_raw, '%Y-%m-%d').date()
            fecha_compacta = f_rec_dt.strftime('%Y%m%d')
        except:
            fecha_compacta = datetime.now().strftime('%Y%m%d')
            
        timestamp_seguro = datetime.now().strftime('%H%M%S')
        nombre_base = f"HT_{eq_data['id']}_{fecha_compacta}_{timestamp_seguro}"
        filename_xlsx = f"{nombre_base}.xlsx"
        filename_pdf = f"{nombre_base}.pdf"
        
        area_name = eq_data.get("area", "General")
        area_folder = "".join([c for c in area_name if c.isalnum() or c==' ']).strip()
        dir_mantenimiento = os.path.join(CARPETAS["areas"], area_folder, "mantenimientos")
        os.makedirs(dir_mantenimiento, exist_ok=True)
        
        ruta_xlsx = os.path.join(dir_mantenimiento, filename_xlsx)
        ruta_pdf = os.path.join(dir_mantenimiento, filename_pdf)
        
        wb.save(ruta_xlsx)
        
        # Intentar renderizar a PDF
        exportar_excel_a_pdf(ruta_xlsx, ruta_pdf, rango_impresion="$A$1:$AR$67")
        
        return filename_xlsx, filename_pdf
    except Exception as e:
        print(f"[ERROR] Fallo al generar archivos de Hoja de Trabajo: {e}")
        return None, None

HTML_INVENTARIO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventario Biomédico | GAMLP</title>
    <style>
        :root {
            --primary: #007AFF;
            --primary-dark: #0056b3;
            --bg: #F8FAFC;
            --card: #FFFFFF;
            --text: #1E293B;
            --muted: #64748B;
            --border: #E2E8F0;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--bg); color: var(--text); padding-bottom: 40px; }
        
        .header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            color: white;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; letter-spacing: -0.5px; }
        .header p { font-size: 13px; color: #94A3B8; }
        .badge-gamlp { display: inline-block; background: rgba(255,255,255,0.15); padding: 3px 10px; border-radius: 20px; font-size: 11px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; }

        .container { max-width: 900px; margin: -15px auto 0; padding: 0 16px; }
        
        .search-card {
            background: var(--card);
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            border: 1px solid var(--border);
            margin-bottom: 20px;
        }
        .search-input {
            width: 100%;
            padding: 14px 16px;
            border-radius: 12px;
            border: 1.5px solid var(--border);
            font-size: 15px;
            outline: none;
            transition: all 0.2s;
            background: #F1F5F9;
        }
        .search-input:focus { border-color: var(--primary); background: #FFFFFF; box-shadow: 0 0 0 3px rgba(0,122,255,0.15); }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        @media (min-width: 600px) {
            .stats-grid { grid-template-columns: repeat(4, 1fr); }
        }
        .stat-card {
            background: var(--card);
            padding: 14px 16px;
            border-radius: 14px;
            border: 1px solid var(--border);
            text-align: center;
        }
        .stat-num { font-size: 24px; font-weight: 700; color: var(--primary); }
        .stat-lbl { font-size: 12px; color: var(--muted); font-weight: 500; margin-top: 2px; }

        .equipment-list { display: flex; flex-direction: column; gap: 12px; }
        .equipment-card {
            background: var(--card);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid var(--border);
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            transition: transform 0.15s, box-shadow 0.15s;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .equipment-card:active { transform: scale(0.99); }
        
        .eq-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 8px; }
        .eq-title { font-size: 16px; font-weight: 700; color: var(--text); }
        .eq-code { background: #EEF2FF; color: #4338CA; font-size: 12px; font-weight: 700; padding: 4px 8px; border-radius: 8px; white-space: nowrap; }
        
        .eq-detail { font-size: 13px; color: var(--muted); margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
        .eq-badges { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
        .badge { font-size: 11px; font-weight: 600; padding: 4px 8px; border-radius: 6px; }
        .badge-area { background: #F1F5F9; color: #475569; }
        .badge-garantia { background: #ECFDF5; color: #065F46; }
        .badge-mtto { background: #FEF3C7; color: #92400E; }
        .badge-danger { background: #FEE2E2; color: #991B1B; }

        .btn-view {
            display: inline-block;
            margin-top: 10px;
            font-size: 13px;
            font-weight: 600;
            color: var(--primary);
        }
    </style>
</head>
<body>
    <div class="header">
        <span class="badge-gamlp">GAMLP • Tecnologías Médicas</span>
        <h1>Inventario de Equipos Médicos</h1>
        <p>Gobierno Autónomo Municipal de La Paz</p>
    </div>

    <div class="container">
        <div class="search-card">
            <input type="text" id="busqueda" class="search-input" placeholder="🔍 Buscar por nombre, serie, código o área..." onkeyup="filtrar()">
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-num">{{ total }}</div>
                <div class="stat-lbl">Total Equipos</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color: var(--success);">{{ operativos }}</div>
                <div class="stat-lbl">Operativos</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color: var(--warning);">{{ garantia }}</div>
                <div class="stat-lbl">En Garantía</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color: var(--danger);">{{ bajas }}</div>
                <div class="stat-lbl">Bajas</div>
            </div>
        </div>

        <div class="equipment-list" id="lista-equipos">
            {% for eq in equipos %}
            <a href="/equipo/{{ eq['id'] }}" class="equipment-card" data-texto="{{ eq['nombre'] }} {{ eq['marca'] }} {{ eq['modelo'] }} {{ eq['id'] }} {{ eq['numero_serie'] }} {{ eq['servicio'] }} {{ eq['area'] }}">
                <div class="eq-header">
                    <div class="eq-title">{{ eq['nombre'] }}</div>
                    <span class="eq-code">{{ eq['id'] }}</span>
                </div>
                <div class="eq-detail">🏷️ <strong>{{ eq['marca'] }}</strong> - {{ eq['modelo'] }}</div>
                <div class="eq-detail">📍 {{ eq['servicio'] or eq['area'] }}</div>
                <div class="eq-badges">
                    <span class="badge badge-area">Área: {{ eq['area'] }}</span>
                    {% if eq['garantia'] == 'Con Garantía' %}
                        <span class="badge badge-garantia">🛡️ Con Garantía</span>
                    {% endif %}
                    {% if eq['f_prox'] %}
                        <span class="badge badge-mtto">📅 Próx. Mtto: {{ eq['f_prox'] }}</span>
                    {% endif %}
                    {% if eq['estado'] == 'Baja' %}
                        <span class="badge badge-danger">Dado de Baja</span>
                    {% endif %}
                </div>
                <div class="btn-view">Ver Ficha Técnica Completa →</div>
            </a>
            {% endfor %}
        </div>
    </div>

    <script>
        function filtrar() {
            const input = document.getElementById('busqueda').value.toLowerCase();
            const tarjetas = document.querySelectorAll('.equipment-card');
            tarjetas.forEach(t => {
                const texto = t.getAttribute('data-texto').toLowerCase();
                t.style.display = texto.includes(input) ? 'block' : 'none';
            });
        }
    </script>
</body>
</html>
"""

@app_web.route('/')
@app_web.route('/inventario')
def vista_inventario_web():
    from database import calcular_proximos_mantenimientos
    try:
        conn = obtener_conexion()
        if not conn:
            return "Error al conectar con la base de datos", 500
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM equipos ORDER BY nombre ASC")
        equipos_db = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()

        total = len(equipos_db)
        operativos = sum(1 for e in equipos_db if e.get('estado') != 'Baja')
        garantia = sum(1 for e in equipos_db if e.get('garantia') == 'Con Garantía')
        bajas = sum(1 for e in equipos_db if e.get('estado') == 'Baja')

        hoy = date.today()
        for eq in equipos_db:
            if eq.get('estado') != 'Baja':
                proximos = calcular_proximos_mantenimientos(eq, cantidad=1, hoy=hoy)
                if proximos:
                    eq['f_prox'] = proximos[0].strftime("%d/%m/%Y")

        return render_template_string(HTML_INVENTARIO, equipos=equipos_db, total=total, operativos=operativos, garantia=garantia, bajas=bajas)
    except Exception as e:
        return f"Error cargando inventario: {e}", 500

@app_web.route('/descargar/<filename>')
def descargar_archivo(filename):
    # Si es PDF, se sirve inline (para abrir directamente en navegador móvil sin bloquear descargas)
    attachment_flag = not filename.lower().endswith('.pdf')
    # Buscar el archivo de forma recursiva en las carpetas de las Áreas
    for root, dirs, files in os.walk(CARPETAS["areas"]):
        if filename in files:
            return send_from_directory(root, filename, as_attachment=attachment_flag)
    # Fallback
    return send_from_directory(CARPETAS["areas"], filename, as_attachment=attachment_flag)

@app_web.route('/equipo/<id_equipo>/descargar_qr')
def descargar_qr_web(id_equipo):
    try:
        conn = obtener_conexion()
        if not conn:
            return "Error de conexión", 500
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM equipos WHERE id = %s", (id_equipo,))
        eq = cur.fetchone()
        cur.close()
        conn.close()
        
        if not eq:
            return "Equipo no encontrado", 404
            
        import qrcode
        from PIL import Image, ImageDraw, ImageFont
        import io
        from flask import send_file
        
        url_base = os.environ.get("RENDER_EXTERNAL_URL") or CONFIG.get("url_base_web", "https://cmms-gamlp.onrender.com")
        enl = f"{url_base}/equipo/{id_equipo}"
        
        qr_base = qrcode.QRCode(version=1, box_size=12, border=1)
        qr_base.add_data(enl)
        qr_base.make(fit=True)
        img_qr_pil = qr_base.make_image(fill_color="black", back_color="white").convert("RGB")
        
        qr_w, qr_h = img_qr_pil.size
        extra_h = 100
        total_w = qr_w
        total_h = qr_h + extra_h
        
        sticker = Image.new("RGB", (total_w, total_h), "white")
        sticker.paste(img_qr_pil, (0, 0))
        
        draw = ImageDraw.Draw(sticker)
        
        try:
            font_nom = ImageFont.truetype("arial.ttf", 15)
            font_id = ImageFont.truetype("arialbd.ttf", 16)
            font_loc = ImageFont.truetype("arial.ttf", 14)
        except:
            font_nom = ImageFont.load_default()
            font_id = ImageFont.load_default()
            font_loc = ImageFont.load_default()
            
        txt_nombre = eq['nombre']
        txt_id = eq['id']
        txt_area = eq.get('area', 'General')
        
        def draw_centered_text(text, y_pos, font, color="black"):
            try:
                w = draw.textlength(text, font=font)
            except:
                try:
                    w = draw.textsize(text, font=font)[0]
                except:
                    w = len(text) * 8
            x_pos = (total_w - w) / 2
            draw.text((x_pos, y_pos), text, fill=color, font=font)
            
        draw_centered_text(txt_nombre, qr_h + 10, font_nom)
        draw_centered_text(txt_id, qr_h + 35, font_id)
        draw_centered_text(txt_area, qr_h + 60, font_loc)
        
        img_io = io.BytesIO()
        sticker.save(img_io, 'PNG')
        img_io.seek(0)
        
        id_sanitizado = "".join([c for c in id_equipo if c.isalnum() or c in ('-', '_')]).strip()
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f"QR_{id_sanitizado}.png")
    except Exception as e:
        return f"Error al generar QR: {e}", 500

@app_web.route('/equipo/<id_equipo>')
def ver_equipo(id_equipo):
    try:
        conn = obtener_conexion()
        if not conn:
            return "<h1>❌ Error de conexión a Base de Datos</h1>", 500
            
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM equipos WHERE id = %s", (id_equipo,))
        eq = cur.fetchone()
        
        if not eq:
            cur.close()
            conn.close()
            return "<h1>❌ Equipo no encontrado</h1>", 404
            
        cur.execute("SELECT * FROM historial_intervenciones WHERE equipo_id = %s ORDER BY fecha DESC", (id_equipo,))
        historial = cur.fetchall()
        cur.close()
        conn.close()

        # Mapear archivos locales de hojas de trabajo existentes
        historial_list = []
        area_name = eq.get("area", "General")
        area_folder = "".join([c for c in area_name if c.isalnum() or c==' ']).strip()
        dir_mantenimiento = os.path.join(CARPETAS["areas"], area_folder, "mantenimientos")
        
        archivos_locales = []
        if os.path.exists(dir_mantenimiento):
            try:
                archivos_locales = os.listdir(dir_mantenimiento)
            except:
                pass
                
        for row in historial:
            d = dict(row)
            fecha_str = str(d['fecha'])
            fecha_compacta = fecha_str.replace('-', '')
            
            xlsx_match = None
            pdf_match = None
            prefix_1 = f"HT_{id_equipo}_{fecha_compacta}"
            
            for filename in archivos_locales:
                if filename.startswith(prefix_1):
                    if filename.endswith(".xlsx"):
                        xlsx_match = filename
                    elif filename.endswith(".pdf"):
                        pdf_match = filename
            
            d['xlsx_file'] = xlsx_match
            d['pdf_file'] = pdf_match
            historial_list.append(d)

        # Calcular tiempo de garantía restante
        hoy = date.today()
        garantia_str = "Sin Garantía"
        if eq.get('garantia') == "Con Garantía" and eq.get('fecha_vencimiento_garantia'):
            f_venc = eq['fecha_vencimiento_garantia']
            if isinstance(f_venc, str):
                try:
                    f_venc = datetime.strptime(f_venc, "%Y-%m-%d").date()
                except:
                    f_venc = None
            if f_venc:
                if f_venc < hoy:
                    garantia_str = f"Vencida (Venció el {f_venc})"
                else:
                    from dateutil.relativedelta import relativedelta
                    diff = relativedelta(f_venc, hoy)
                    parts = []
                    if diff.years > 0:
                        parts.append(f"{diff.years} {'año' if diff.years == 1 else 'años'}")
                    if diff.months > 0:
                        parts.append(f"{diff.months} {'mes' if diff.months == 1 else 'meses'}")
                    if diff.days > 0:
                        parts.append(f"{diff.days} {'día' if diff.days == 1 else 'días'}")
                    duracion = ", ".join(parts) if parts else "Vence hoy"
                    garantia_str = f"Activa (Vence el {f_venc} - Resta: {duracion})"

        html_web = """
        <!DOCTYPE html><html lang="es"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Hoja de Vida</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F2F2F7; margin: 0; padding: 15px; color: #1C1C1E;}
            .tarjeta { background: #fff; border-radius: 16px; padding: 25px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); max-width: 600px; margin: auto; }
            .cabecera { background: #007AFF; color: white; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
            .estado { display: inline-block; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; background: #34C759; color: white; margin-right: 5px; }
            .estado.baja { background: #FF3B30; }
            .estado.espera { background: #FF9500; }
            .estado.inoperante { background: #8E8E93; }
            .btn-action { display: block; text-align: center; background: #007AFF; color: white; text-decoration: none; padding: 14px; border-radius: 10px; font-weight: bold; margin-top: 20px; font-size: 15px; }
            .btn-action:active { background: #0056B3; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px;}
            th, td { border-bottom: 1px solid #E5E5EA; padding: 12px; text-align: left; } th { color: #8E8E93;}
        </style></head><body>
            <div id="sync-banner" style="display:none; background: #FF9500; color: white; padding: 12px; text-align: center; font-weight: bold; font-size: 14px; border-radius: 8px; margin: 10px auto; max-width: 600px;">
                ⚠️ Tienes <span id="sync-count">0</span> reporte(s) guardado(s) offline. 
                <a href="#" onclick="intentarSincronizarAhora(); return false;" style="color: white; text-decoration: underline; margin-left: 10px;">Sincronizar ahora</a>
            </div>
            <div class="tarjeta"><div class="cabecera"><h3 style="margin:0;">CMMS GAMLP - Tecnologías Médicas</h3></div>
                <h2 style="margin:0;">{{ eq['nombre'] }}</h2>
                <div style="margin-top: 5px;">
                    <div class="estado {% if eq['estado'] == 'Baja' %}baja{% elif eq['estado'] == 'En Espera de Repuesto' %}espera{% elif eq['estado'] == 'Fuera de Servicio' %}inoperante{% endif %}">{{ eq['estado'] }}</div>
                </div>
                <div style="margin-top: 20px; font-size: 15px; line-height: 1.6;">
                    <p><strong>ID:</strong> {{ eq['id'] }}</p>
                    <p><strong>S/N:</strong> {{ eq['numero_serie'] or 'Sin Serie' }}</p>
                    <p><strong>Modelo:</strong> {{ eq['marca'] }} / {{ eq['modelo'] }}</p>
                    <p><strong>Área:</strong> {{ eq['servicio'] }} - {{ eq['area'] }}</p>
                    <p><strong>Garantía:</strong> {{ garantia_str }}</p>
                    <p style="color: #FF9500;"><strong>Criticidad:</strong> {{ eq['criticidad'] }}</p>
                </div>
                
                <a href="/equipo/{{ eq['id'] }}/mantenimiento" class="btn-action">🛠️ Registrar Mantenimiento</a>
                <a href="/equipo/{{ eq['id'] }}/descargar_qr" class="btn-action" style="background: #34C759; margin-top: 10px;">📥 Descargar Código QR (Etiqueta)</a>
                
                <h3 style="margin-top:25px; border-bottom: 2px solid #F2F2F7; padding-bottom: 5px;">Historial</h3>
                <table><tr><th>Fecha</th><th>Tipo</th><th>Realizado Por</th><th>Trabajo Realizado</th><th>Fichas</th></tr>
                {% for m in hist %}<tr>
                    <td>{{ m['fecha'] }}</td>
                    <td><strong>{{ m['tipo'] }}</strong></td>
                    <td>{{ m['realizado_por'] or 'Técnico' }}</td>
                    <td>{{ m['trabajo'] or m['detalle'] or 'Sin detalle' }}</td>
                    <td>
                        {% if m['pdf_file'] %}
                        <a href="/descargar/{{ m['pdf_file'] }}" style="text-decoration:none; color:#FF9500; font-weight:bold;" title="Descargar PDF">📕 PDF</a>
                        {% else %}
                        <span style="color:#8E8E93;">-</span>
                        {% endif %}
                    </td>
                </tr>
                {% else %}<tr><td colspan="5" style="text-align:center; color:#8E8E93;">Sin intervenciones registradas</td></tr>{% endfor %}
                </table></div>
            <script>
                function intentarSincronizarAhora() {
                    var pendientes = JSON.parse(localStorage.getItem("mantenimientos_pendientes") || "[]");
                    if (pendientes.length === 0) return;
                    
                    var banner = document.getElementById("sync-banner");
                    if (banner) banner.innerHTML = "🔄 Sincronizando reportes offline... (" + pendientes.length + " restantes)";
                    
                    var item = pendientes[0];
                    var passVal = item.web_pass;
                    if (!passVal) {
                        passVal = prompt("Introduce tu contraseña (" + (item.web_user || "usuario") + ") para sincronizar el reporte de " + (item.nombre_equipo || "mantenimiento") + ":");
                        if (!passVal) {
                            if (banner) banner.innerHTML = "⚠️ Sincronización pausada. Se requiere contraseña.";
                            return;
                        }
                    }

                    var params = new URLSearchParams();
                    for (var key in item) {
                        if (key !== "web_pass") {
                            params.append(key, item[key]);
                        }
                    }
                    params.append("web_pass", passVal);
                    
                    fetch(item.url_sincronizacion, {
                        method: "POST",
                        body: params
                    })
                    .then(response => {
                        if (response.ok) {
                            pendientes.shift();
                            localStorage.setItem("mantenimientos_pendientes", JSON.stringify(pendientes));
                            if (pendientes.length > 0) {
                                intentarSincronizarAhora();
                            } else {
                                if (banner) {
                                    banner.style.background = "#34C759";
                                    banner.innerHTML = "✅ ¡Todos los reportes sincronizados correctamente!";
                                }
                                setTimeout(() => {
                                    window.location.reload();
                                }, 1500);
                            }
                        } else {
                            if (banner) banner.innerHTML = "⚠️ Error de credenciales al sincronizar. Verifica tu usuario y contraseña.";
                        }
                    })
                    .catch(err => {
                        if (banner) banner.innerHTML = "⚠️ Servidor no responde. Sincronización pendiente (se enviará al conectar).";
                    });
                }


                window.addEventListener("load", function() {
                    var pendientes = JSON.parse(localStorage.getItem("mantenimientos_pendientes") || "[]");
                    if (pendientes.length > 0) {
                        var banner = document.getElementById("sync-banner");
                        var count = document.getElementById("sync-count");
                        if (banner && count) {
                            count.innerText = pendientes.length;
                            banner.style.display = "block";
                        }
                        intentarSincronizarAhora();
                    }
                });
            </script>
        </body></html>
        """
        return render_template_string(html_web, eq=eq, hist=historial_list, garantia_str=garantia_str)
    except Exception as e:
        return f"Error en el servidor web: {e}"

@app_web.route('/equipo/<id_equipo>/mantenimiento', methods=['GET', 'POST'])
def registrar_mantenimiento(id_equipo):
    error_msg = None
    try:
        conn = obtener_conexion()
        if not conn:
            return "<h1>❌ Error de conexión a Base de Datos</h1>", 500
            
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM equipos WHERE id = %s", (id_equipo,))
        eq = cur.fetchone()
        
        if not eq:
            cur.close()
            conn.close()
            return "<h1>❌ Equipo no encontrado</h1>", 404

        # Cargar los repuestos disponibles con stock mayor a cero y compatibles con el tipo de equipo
        cat_str = f"{eq['nombre']} - {eq.get('marca') or ''} - {eq.get('modelo') or ''}"
        eq_nom = eq.get('nombre') or ''
        cur.execute("""
            SELECT nombre_repuesto, cantidad, tipo_equipo 
            FROM repuestos 
            WHERE cantidad > 0 
              AND COALESCE(estado_disponibilidad, 'En Stock') = 'En Stock'
              AND (tipo_equipo = %s OR tipo_equipo = %s OR tipo_equipo ILIKE %s)
            ORDER BY nombre_repuesto ASC
        """, (cat_str, eq_nom, f"%{eq_nom}%"))
        repuestos_list = [dict(r) for r in cur.fetchall()]
        if not repuestos_list:
            cur.execute("""
                SELECT nombre_repuesto, cantidad, tipo_equipo 
                FROM repuestos 
                WHERE cantidad > 0 AND COALESCE(estado_disponibilidad, 'En Stock') = 'En Stock'
                ORDER BY nombre_repuesto ASC
            """)
            repuestos_list = [dict(r) for r in cur.fetchall()]


        if request.method == 'POST':
            web_user = request.form.get('web_user', '').strip()
            web_pass = request.form.get('web_pass', '').strip()
            
            # Validar credenciales
            usuario_valido = login(web_user, web_pass)
            if not usuario_valido:
                error_msg = "Usuario o contraseña incorrectos."
            else:
                tipo = request.form.get('tipo')
                tipo_ht = request.form.get('tipo_ht', '1')
                condicion = request.form.get('condicion')
                estado_equipo = request.form.get('estado_equipo')
                deficiencia = request.form.get('deficiencia', '').strip()
                trabajo = request.form.get('trabajo', '').strip()
                observaciones = request.form.get('observaciones', '').strip()
                
                fecha_recepcion = request.form.get('fecha_recepcion')
                if not fecha_recepcion:
                    fecha_recepcion = date.today().strftime('%Y-%m-%d')
                fecha_entrega = request.form.get('fecha_entrega')
                if not fecha_entrega:
                    fecha_entrega = date.today().strftime('%Y-%m-%d')
                hora_ejecucion = request.form.get('hora_ejecucion', '12:00').strip()
                
                try:
                    tiempo_reparacion = float(request.form.get('tiempo_reparacion', '0').strip().replace(',', '.'))
                    if tiempo_reparacion < 0:
                        tiempo_reparacion = 0.0
                except:
                    tiempo_reparacion = 0.0
                
                repuesto_usado = request.form.get('repuesto_usado') == 'on'
                repuesto_nombre = request.form.get('repuesto_nombre', '').strip() if repuesto_usado else ''
                repuesto_cantidad_str = request.form.get('repuesto_cantidad', '0') if repuesto_usado else '0'
                repuesto_cantidad = int(repuesto_cantidad_str) if repuesto_cantidad_str.isdigit() else 0

                # Si el repuesto viene de la lista autocompletada, limpiar el sufijo de stock
                if repuesto_usado and " (Disponible:" in repuesto_nombre:
                    repuesto_nombre = repuesto_nombre.split(" (Disponible:")[0].strip()

                estado_final = request.form.get('estado_final', 'Operativo')

                detalle_final = f"Trabajo: {trabajo}."
                if deficiencia:
                    detalle_final = f"Deficiencia: {deficiencia}. " + detalle_final

                # 1. Registrar la intervención
                cur.execute("""
                    INSERT INTO historial_intervenciones (
                        equipo_id, fecha, tipo, detalle, condicion, estado_equipo,
                        deficiencia, trabajo, observaciones, fecha_entrega,
                        servicio_ht, tipo_ht, repuesto_usado, repuesto_nombre, repuesto_cantidad, realizado_por, hora_entrega, tiempo_reparacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_equipo, fecha_recepcion, tipo, detalle_final, condicion, estado_equipo,
                    deficiencia, trabajo, observaciones, fecha_entrega,
                    eq['servicio'], tipo_ht, repuesto_usado, repuesto_nombre, repuesto_cantidad, usuario_valido['nombre_completo'], hora_ejecucion, tiempo_reparacion
                ))


                # 2. Descontar stock del repuesto si corresponde
                if repuesto_usado and repuesto_nombre:
                    cur.execute("""
                        UPDATE repuestos 
                        SET cantidad = GREATEST(0, cantidad - %s) 
                        WHERE nombre_repuesto = %s
                    """, (repuesto_cantidad, repuesto_nombre))

                # 3. Actualizar el estado del equipo
                cur.execute("UPDATE equipos SET estado = %s WHERE id = %s", (estado_final, id_equipo))
                
                conn.commit()
                cur.close()
                conn.close()

                # Generar archivos Excel y PDF de la Hoja de Trabajo
                form_data = {
                    'tipo': tipo, 'condicion': condicion, 'estado_equipo': estado_equipo,
                    'deficiencia': deficiencia, 'trabajo': trabajo, 'observaciones': observaciones,
                    'tipo_ht': tipo_ht, 'fecha_recepcion': fecha_recepcion, 'hora_ejecucion': hora_ejecucion
                }
                sello_firma_path = usuario_valido.get("sello_firma")
                
                xlsx_file, pdf_file = generar_excel_ht_web(dict(eq), form_data, usuario_valido['nombre_completo'], sello_firma_path)

                # Marcar los datos como sucios para sincronizar en tiempo real con la GUI del software
                global app_gui
                if app_gui:
                    app_gui.datos_sucios = True

                return render_template_string(HTML_EXITO, id_equipo=id_equipo, xlsx_file=xlsx_file, pdf_file=pdf_file)

        cur.close()
        conn.close()

        html_formulario = """
        <!DOCTYPE html><html lang="es"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Registrar Mantenimiento</title>
        <style>
            *, *:before, *:after {
                box-sizing: border-box;
            }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F2F2F7; margin: 0; padding: 15px; color: #1C1C1E; }
            .tarjeta { background: #fff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); max-width: 600px; margin: auto; }
            .cabecera { background: #007AFF; color: white; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
            .campo { margin-bottom: 16px; }
            label { display: block; font-weight: bold; margin-bottom: 6px; font-size: 14px; color: #3A3A3C; }
            select, input[type="text"], input[type="password"], input[type="date"], input[type="time"], input[type="number"], textarea { 
                display: block;
                width: 100%; 
                padding: 12px; 
                border: 1px solid #C7C7CC; 
                border-radius: 8px; 
                font-size: 15px; 
                background: #FFF; 
                color: #1C1C1E; 
                margin: 0;
            }
            select:focus, input[type="text"]:focus, input[type="password"]:focus, input[type="date"]:focus, input[type="time"]:focus, input[type="number"]:focus, textarea:focus { outline: none; border-color: #007AFF; }
            .check-group { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
            .check-group input { width: 20px; height: 20px; }
            .repuesto-caja { background: #F2F2F7; padding: 15px; border-radius: 10px; margin-top: 10px; display: none; }
            .btn-save { background: #34C759; color: white; font-weight: bold; border: none; width: 100%; padding: 15px; border-radius: 10px; font-size: 16px; margin-top: 10px; cursor: pointer; }
            .btn-save:active { background: #30B34F; }
            .btn-cancel { display: block; text-align: center; margin-top: 15px; color: #FF3B30; text-decoration: none; font-size: 15px; font-weight: bold; }
        </style>
        <script>
            function toggleRepuestos() {
                var checked = document.getElementById("repuesto_usado").checked;
                document.getElementById("caja-repuestos").style.display = checked ? "block" : "none";
            }

            function intentarSincronizarAhora() {
                var pendientes = JSON.parse(localStorage.getItem("mantenimientos_pendientes") || "[]");
                if (pendientes.length === 0) return;
                
                var status = document.getElementById("offline-sync-status");
                if (status) status.innerHTML = "🔄 Sincronizando reporte offline con el servidor... (" + pendientes.length + " restantes)";
                
                var item = pendientes[0];
                var passVal = item.web_pass;
                if (!passVal) {
                    passVal = prompt("Introduce tu contraseña (" + (item.web_user || "usuario") + ") para sincronizar:");
                    if (!passVal) {
                        if (status) status.innerHTML = "<span style='color:#FF9500;'>⚠️ Sincronización pausada: contraseña requerida.</span>";
                        return;
                    }
                }

                var params = new URLSearchParams();
                for (var key in item) {
                    if (key !== "web_pass") {
                        params.append(key, item[key]);
                    }
                }
                params.append("web_pass", passVal);
                
                fetch(item.url_sincronizacion, {
                    method: "POST",
                    body: params
                })
                .then(response => {
                    if (response.ok) {
                        pendientes.shift();
                        localStorage.setItem("mantenimientos_pendientes", JSON.stringify(pendientes));
                        if (pendientes.length > 0) {
                            intentarSincronizarAhora();
                        } else {
                            if (status) status.innerHTML = "<span style='color:#34C759;font-weight:bold;'>✅ ¡Reporte guardado y sincronizado con éxito!</span>";
                            response.text().then(html => {
                                setTimeout(() => {
                                    document.body.innerHTML = html;
                                    window.scrollTo(0, 0);
                                }, 1000);
                            });
                        }
                    } else {
                        response.text().then(txt => {
                            if (txt.includes("Usuario o contraseña incorrectos")) {
                                if (status) status.innerHTML = "<span style='color:#FF3B30;'>⚠️ Error: Credenciales incorrectas.</span>";
                            } else {
                                if (status) status.innerHTML = "<span style='color:#FF3B30;'>⚠️ El servidor rechazó la sincronización.</span>";
                            }
                        });
                    }
                })
                .catch(err => {
                    if (status) status.innerHTML = "⚠️ El servidor sigue fuera de línea. Reintentando al recuperar señal...";
                });
            }

            function guardarMantenimientoLocal(data) {
                // Por seguridad hospitalaria: NUNCA persistir la contraseña en localStorage
                delete data.web_pass;
                
                var pendientes = JSON.parse(localStorage.getItem("mantenimientos_pendientes") || "[]");
                data.id_equipo = "{{ eq['id'] }}";
                data.nombre_equipo = "{{ eq['nombre'] }}";
                data.fecha_registro_offline = new Date().toISOString();
                data.url_sincronizacion = window.location.href;
                pendientes.push(data);
                localStorage.setItem("mantenimientos_pendientes", JSON.stringify(pendientes));

                
                // Mostrar pantalla de éxito offline
                document.body.innerHTML = `
                <div class="tarjeta" style="max-width: 450px; text-align: center; padding: 30px; margin: 40px auto;">
                    <div style="font-size: 50px; color: #FF9500; margin-bottom: 15px;">⚠️</div>
                    <h2 style="margin-top:0; color: #E08200;">Registro Guardado Offline</h2>
                    <p style="color: #666; font-size: 14px; margin-bottom: 25px;">
                        No hay señal o conexión al servidor del hospital. El reporte de mantenimiento para <strong>${data.nombre_equipo}</strong> se ha guardado localmente en tu celular.
                    </p>
                    <div style="background: #FFF9E6; border: 1px solid #FFE0B2; padding: 12px; border-radius: 8px; font-size: 13px; color: #B78103; margin-bottom: 20px; text-align: left;">
                        💡 <strong>¿Qué hacer ahora?</strong><br>
                        En cuanto recuperes la red o Wi-Fi del hospital, mantén esta pestaña del navegador abierta. El celular enviará de forma automática el reporte de manera directa.
                    </div>
                    <button class="btn-save" onclick="intentarSincronizarAhora()" style="background: #007AFF;">🔄 Intentar Sincronizar Ahora</button>
                    <div id="offline-sync-status" style="margin-top: 15px; font-size: 13px; font-weight: bold; color: #666;"></div>
                </div>
                `;
            }

            window.addEventListener("load", function() {
                var pendientes = JSON.parse(localStorage.getItem("mantenimientos_pendientes") || "[]");
                if (pendientes.length > 0) {
                    intentarSincronizarAhora();
                }

                // Interceptar envío del formulario para soportar modo sin conexión
                var form = document.querySelector("form");
                if (form) {
                    form.addEventListener("submit", function(e) {
                        e.preventDefault();
                        
                        var btn = document.querySelector(".btn-save");
                        btn.disabled = true;
                        btn.innerText = "Procesando...";

                        var formData = new FormData(form);
                        var data = {};
                        formData.forEach((value, key) => { data[key] = value });
                        
                        // Asegurar checkboxes
                        if (!data.repuesto_usado) data.repuesto_usado = "";
                        else data.repuesto_usado = "on";

                        var params = new URLSearchParams(formData);

                        fetch(window.location.href, {
                            method: "POST",
                            body: params
                        })
                        .then(response => {
                            if (response.ok) {
                                response.text().then(html => {
                                    document.body.innerHTML = html;
                                    window.scrollTo(0, 0);
                                });
                            } else {
                                response.text().then(html => {
                                    document.body.innerHTML = html;
                                    window.scrollTo(0, 0);
                                });
                            }
                        })
                        .catch(err => {
                            // Falla de red/conexión, almacenar offline
                            guardarMantenimientoLocal(data);
                        });
                    });
                }
            });
        </script></head><body>
            <div class="tarjeta">
                <div class="cabecera">
                    <h3 style="margin:0;">Nueva Intervención</h3>
                    <span style="font-size:12px;">{{ eq['nombre'] }} (ID: {{ eq['id'] }})</span>
                </div>
                <form method="POST">
                    <!-- Sección de seguridad requerida -->
                    <div class="campo" style="background: #FFF9E6; padding: 15px; border-radius: 10px; border: 1px solid #FFE0B2; margin-bottom: 20px;">
                        <label style="color: #FF9500; font-size: 13px;">🔒 Validar Credenciales (Seguridad)</label>
                        <div style="margin-bottom: 10px;">
                            <input type="text" name="web_user" required placeholder="Usuario (Ej. 10955499)">
                        </div>
                        <div>
                            <input type="password" name="web_pass" required placeholder="Contraseña">
                        </div>
                        {% if error %}
                        <div style="color: #FF3B30; font-size: 13px; font-weight: bold; margin-top: 10px;">⚠️ {{ error }}</div>
                        {% endif %}
                    </div>

                    <div class="campo">
                        <label>Tipo de Mantenimiento</label>
                        <select name="tipo">
                            <option value="Preventivo">🔧 Preventivo</option>
                            <option value="Correctivo">🚨 Correctivo</option>
                        </select>
                    </div>
                    <div class="campo">
                        <label>Turno / Tipo</label>
                        <select name="tipo_ht">
                            <option value="1">1</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                        </select>
                    </div>
                    <div class="campo">
                        <label>Fecha de Recepción</label>
                        <input type="date" name="fecha_recepcion" value="{{ hoy_str }}" required>
                    </div>
                    <div class="campo">
                        <label>Fecha de Entrega</label>
                        <input type="date" name="fecha_entrega" value="{{ hoy_str }}" required>
                    </div>
                    <div class="campo">
                        <label>Hora de Entrega</label>
                        <input type="time" name="hora_ejecucion" value="{{ hora_str }}" required>
                    </div>
                    <div class="campo">
                        <label>Tiempo de Reparación (Horas)</label>
                        <input type="number" name="tiempo_reparacion" step="0.1" min="0" value="0" required placeholder="0">
                    </div>
                    <div class="campo">
                        <label>Condición de Entrega</label>
                        <select name="condicion">
                            <option value="Óptimo">Óptimo</option>
                            <option value="Aceptable">Aceptable</option>
                            <option value="Crítica">Crítica</option>
                            <option value="Inoperante">Inoperante</option>
                            <option value="F/Servicio">Fuera de Servicio</option>
                        </select>
                    </div>
                    <div class="campo">
                        <label>Estado Físico del Equipo</label>
                        <select name="estado_equipo">
                            <option value="Óptimo">Óptimo</option>
                            <option value="Bueno">Bueno</option>
                            <option value="Regular">Regular</option>
                            <option value="Malo">Malo</option>
                            <option value="Obsoleto">Obsoleto</option>
                        </select>
                    </div>
                    <div class="campo">
                        <label>Estado Operativo Final (Para el Catálogo)</label>
                        <select name="estado_final">
                            <option value="Operativo">Operativo</option>
                            <option value="En Espera de Repuesto">En Espera de Repuesto</option>
                            <option value="Fuera de Servicio">Fuera de Servicio</option>
                            <option value="Baja">Dado de Baja</option>
                        </select>
                    </div>
                    <div class="campo">
                        <label>Deficiencia Reportada</label>
                        <textarea name="deficiencia" rows="2" placeholder="Describa el problema reportado..."></textarea>
                    </div>
                    <div class="campo">
                        <label>Trabajo Realizado</label>
                        <textarea name="trabajo" rows="3" required placeholder="Detalle las pruebas o reparaciones hechas..."></textarea>
                    </div>
                    <div class="campo">
                        <label>Observaciones</label>
                        <textarea name="observaciones" rows="2" placeholder="Notas adicionales..."></textarea>
                    </div>
                    
                    <div class="campo check-group">
                        <input type="checkbox" id="repuesto_usado" name="repuesto_usado" onchange="toggleRepuestos()">
                        <label for="repuesto_usado" style="margin:0;">¿Se utilizó repuesto?</label>
                    </div>
                    
                    <div id="caja-repuestos" class="repuesto-caja">
                        <div class="campo">
                            <label>Nombre del Repuesto</label>
                            <input type="text" list="repuestos_list" name="repuesto_nombre" placeholder="Busca o escribe el repuesto...">
                            <datalist id="repuestos_list">
                                {% for r in repuestos %}
                                <option value="{{ r['nombre_repuesto'] }} (Disponible: {{ r['cantidad'] }})">
                                {% endfor %}
                            </datalist>
                        </div>
                        <div class="campo">
                            <label>Cantidad Utilizada</label>
                            <input type="number" name="repuesto_cantidad" min="1" value="1">
                        </div>
                    </div>
                    
                    <button type="submit" class="btn-save">Guardar Registro</button>
                    <a href="/equipo/{{ eq['id'] }}" class="btn-cancel">Cancelar</a>
                </form>
            </div>
        </body></html>
        """
        hoy_str = date.today().strftime('%Y-%m-%d')
        hora_str = datetime.now().strftime('%H:%M')
        return render_template_string(html_formulario, eq=eq, error=error_msg, repuestos=repuestos_list, hoy_str=hoy_str, hora_str=hora_str)
    except Exception as e:
        return f"Error en el servidor web: {e}"

def iniciar_servidor_web():
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app_web.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)


def arrancar_hilo_web(gui_instance=None):
    """Función para ser llamada desde el archivo principal que levanta el servidor en segundo plano."""
    global app_gui
    if gui_instance:
        app_gui = gui_instance
    hilo_web = threading.Thread(target=iniciar_servidor_web, daemon=True)
    hilo_web.start()
    return hilo_web

if __name__ == '__main__':
    import socket as _sock

    def obtener_ip_local():
        try:
            s = _sock.socket(_sock.AF_INET, _sock.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def puerto_en_uso(puerto):
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', puerto)) == 0

    ip = obtener_ip_local()
    print("="*60)
    print("     CMMS GAMLP - SERVIDOR WEB INDEPENDIENTE (v1.5)")
    print(f" Servidor activo en: http://{ip}:5000")
    print(" Mantén esta ventana abierta para que los códigos QR funcionen")
    print(" incluso cuando el programa principal esté cerrado.")
    print("="*60)

    if puerto_en_uso(5000):
        print("\n[AVISO] El puerto 5000 ya está en uso (probablemente el software principal ya arrancó el servidor).")
        print(" El servidor web ya está funcionando correctamente.")
        input("\nPresiona Enter para cerrar esta ventana...")
    else:
        iniciar_servidor_web()
