# generador_repuestos_excel.py
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.drawing.image import Image as OpenpyxlImage
from PIL import Image as PILImage
import io, base64, os, tempfile
from datetime import datetime

def obtener_ruta_plantilla_repuestos():
    posibles = [
        os.path.join(os.path.dirname(__file__), "plantillas", "plantilla_repuestos.xlsx"),
        os.path.join("plantillas", "plantilla_repuestos.xlsx"),
        "c:/Users/HP/Desktop/CMMS_GAMLP/plantillas/plantilla_repuestos.xlsx"
    ]
    for p in posibles:
        if os.path.exists(p):
            return p
    return "plantillas/plantilla_repuestos.xlsx"

def generar_excel_repuestos_wb(lista_repuestos, tipo="Stock"):
    """
    Genera el workbook de openpyxl con la plantilla plantilla_repuestos.xlsx llena.
    tipo: 'Stock' / 'Inventario' o 'Requerido' / 'Necesario'
    Retorna: (wb, temp_img_files)
    """
    ruta_plantilla = obtener_ruta_plantilla_repuestos()
    wb = openpyxl.load_workbook(ruta_plantilla)
    ws = wb.active

    # 1. Título y Año en E4 (E4:J5 combinado)
    anio_act = datetime.now().year
    tipo_str = str(tipo).strip().lower()
    if tipo_str in ["stock", "inventario", "en stock"]:
        titulo = f"Lista de Repuestos en Inventario - {anio_act}"
    else:
        titulo = f"Lista de Repuestos Requeridos - {anio_act}"
        
    ws["E4"].value = titulo

    # Eliminar filas predeterminadas (8 a 11) si existen
    if ws.max_row >= 8:
        cant_a_borrar = ws.max_row - 7
        ws.delete_rows(8, cant_a_borrar)

    # Estilos
    font_datos = Font(name="Segoe UI", size=9)
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center")
    
    thin = Side(border_style="thin", color="000000")
    borde_datos = Border(top=thin, left=thin, right=thin, bottom=thin)

    fill_par = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_impar = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    temp_img_files = []

    # 2. Llenar filas dinámicamente
    for idx, r in enumerate(lista_repuestos, start=1):
        fila_idx = 7 + idx
        
        # Combinar K{r}:N{r} (Costo Total) y O{r}:V{r} (Fotografía)
        ws.merge_cells(start_row=fila_idx, start_column=11, end_row=fila_idx, end_column=14)
        ws.merge_cells(start_row=fila_idx, start_column=15, end_row=fila_idx, end_column=22)

        # Valores
        cant = int(r.get("cantidad", 0) or 0)
        costo_u = float(r.get("costo", 0) or 0)
        costo_tot = cant * costo_u

        # Datos
        ws.cell(row=fila_idx, column=2, value=idx)                                          # B: N°
        ws.cell(row=fila_idx, column=3, value=r.get("red_salud_nombre") or "")              # C: RED
        ws.cell(row=fila_idx, column=4, value=r.get("centro_salud_nombre") or "")           # D: CENTRO DE SALUD
        ws.cell(row=fila_idx, column=5, value=r.get("area") or "")                          # E: AREA
        ws.cell(row=fila_idx, column=6, value=r.get("nombre_repuesto") or "")               # F: NOMBRE DEL REPUESTO
        ws.cell(row=fila_idx, column=7, value=cant)                                         # G: CANTIDAD
        ws.cell(row=fila_idx, column=8, value=r.get("marca") or "")                         # H: MARCA
        ws.cell(row=fila_idx, column=9, value=r.get("modelo") or r.get("modelo_parte") or "") # I: MODELO
        ws.cell(row=fila_idx, column=10, value=costo_u)                                     # J: COSTO UNITARIO
        ws.cell(row=fila_idx, column=11, value=costo_tot)                                   # K (K:N): COSTO TOTAL

        # Formatos de moneda
        ws.cell(row=fila_idx, column=10).number_format = '#,##0.00'
        ws.cell(row=fila_idx, column=11).number_format = '#,##0.00'

        # Bordes, fuentes y alineaciones
        fill_row = fill_impar if idx % 2 == 1 else fill_par
        for c in range(2, 23):
            cell = ws.cell(row=fila_idx, column=c)
            cell.border = borde_datos
            cell.fill = fill_row
            cell.font = font_datos
            if c in [2, 3, 4, 5, 7, 8, 9]:
                cell.alignment = align_center
            elif c == 6:
                cell.alignment = align_left
            elif c in [10, 11]:
                cell.alignment = align_right

        # 3. Procesamiento de Fotografía en O{r}
        foto_data = r.get("foto")
        img_insertada = False

        if foto_data and str(foto_data).strip():
            try:
                pil_img = None
                foto_str = str(foto_data).strip()
                if foto_str.startswith("data:image") and "base64," in foto_str:
                    b64_clean = foto_str.split("base64,")[1]
                    img_bytes = base64.b64decode(b64_clean)
                    pil_img = PILImage.open(io.BytesIO(img_bytes))
                elif os.path.exists(foto_str):
                    pil_img = PILImage.open(foto_str)

                if pil_img:
                    if pil_img.mode != "RGB":
                        pil_img = pil_img.convert("RGB")
                    
                    # Escalar manteniendo proporción: max 130x65 px
                    max_w, max_h = 130, 65
                    orig_w, orig_h = pil_img.size
                    ratio = min(max_w / orig_w, max_h / orig_h)
                    new_w, new_h = max(1, int(orig_w * ratio)), max(1, int(orig_h * ratio))
                    
                    pil_img_resized = pil_img.resize((new_w, new_h), PILImage.Resampling.LANCZOS)
                    
                    tf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    pil_img_resized.save(tf.name, format="PNG")
                    tf.close()
                    temp_img_files.append(tf.name)

                    openpyxl_img = OpenpyxlImage(tf.name)
                    openpyxl_img.anchor = f"O{fila_idx}"
                    ws.add_image(openpyxl_img)
                    
                    # Ajustar altura de la fila según la imagen
                    ws.row_dimensions[fila_idx].height = 58
                    img_insertada = True
            except Exception as ex:
                print(f"[WARN] Error insertando foto en fila {fila_idx}: {ex}")

        if not img_insertada:
            ws.cell(row=fila_idx, column=15, value="-")
            ws.cell(row=fila_idx, column=15).alignment = align_center
            ws.row_dimensions[fila_idx].height = 24

    return wb, temp_img_files

def guardar_excel_repuestos(lista_repuestos, tipo="Stock", ruta_salida="repuestos.xlsx"):
    wb, temp_files = generar_excel_repuestos_wb(lista_repuestos, tipo=tipo)
    wb.save(ruta_salida)
    for tf in temp_files:
        try: os.remove(tf)
        except: pass
    return ruta_salida
