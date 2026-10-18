# compilar.py
import os
import sys
import PyInstaller.__main__

# Asegurar que el directorio de trabajo actual sea la carpeta del proyecto
directorio_proyecto = os.path.dirname(os.path.abspath(__file__))
os.chdir(directorio_proyecto)

print(f"Iniciando compilacion de SGEM GAMLP desde: {directorio_proyecto}")

PyInstaller.__main__.run([
    os.path.join(directorio_proyecto, 'main.py'),
    '--name=SGEM_GAMLP_v1.2',
    '--noconsole',
    '--onefile',
    f'--add-data={os.path.join(directorio_proyecto, "plantillas")};plantillas',
    f'--add-data={os.path.join(directorio_proyecto, "vistas")};vistas',
    '--collect-all=customtkinter',
    '--collect-all=PIL',
    '--hidden-import=psycopg2',
    '--hidden-import=psycopg2.extras',
    '--hidden-import=bcrypt',
    '--hidden-import=openpyxl',
    '--hidden-import=qrcode',
    '--hidden-import=flask',
    '--hidden-import=config',
    '--hidden-import=database',
    '--hidden-import=auth',
    '--hidden-import=estilos',
    '--hidden-import=excel_utils',
    '--hidden-import=generador_muebleria_excel',
    '--hidden-import=generador_repuestos_excel',
    '--hidden-import=ia_biomedica',
    '--hidden-import=mapa_geo_utils',
    '--hidden-import=web_server',
    '--hidden-import=vistas_web_movil',
    '--noconfirm',
])

print("\n[OK] Compilacion finalizada con exito! El archivo ejecutable esta en: dist/SGEM_GAMLP_v1.2.exe")
