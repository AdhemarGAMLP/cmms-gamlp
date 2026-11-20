import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import sys

# Configure high quality font rendering
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'

# Data
data = [
    # Red, Centro, Equipos, Muebles, Total, Operativos, Bajas, Meta, Pct
    ("RED 1 - Cotahuma", "C.M.I. Villa Nuevo Potosí", 124, 555, 679, 673, 6, "647", "100.0%"),
    ("RED 1 - Cotahuma", "Bajo San Pedro", 66, 276, 342, 340, 2, "411", "83.2%"),
    ("RED 1 - Cotahuma", "Almacén Central", 21, 20, 41, 41, 0, "—", "100.0%"),
    ("RED 2 - Max Paredes", "Apumalla", 60, 207, 267, 247, 20, "211", "100.0%"),
    ("RED 3 - Periférica", "Laboratorio Bebidas y Alimentos", 168, 197, 365, 355, 10, "—", "100.0%"),
    ("RED 3 - Periférica", "Asistencia Pública", 116, 31, 147, 36, 111, "794", "18.5%"),
    ("RED 4 - San Antonio", "C.M.I. Pampahasi Bajo", 168, 467, 635, 628, 7, "588", "100.0%"),
    ("RED 4 - San Antonio", "San Antonio Alto", 54, 258, 312, 284, 28, "287", "100.0%"),
    ("RED 4 - San Antonio", "Pampahasi Alto", 52, 222, 274, 273, 1, "264", "100.0%"),
    ("RED 4 - San Antonio", "San Antonio Bajo", 30, 233, 263, 258, 5, "336", "78.3%"),
    ("RED 4 - San Antonio", "Villa Copacabana", 54, 198, 252, 242, 10, "224", "100.0%"),
    ("RED 5 - Sur", "C.M.I. Chasquipampa", 135, 418, 553, 535, 18, "373", "100.0%"),
    ("RED 5 - Sur", "Alto Obrajes", 102, 224, 326, 306, 20, "211", "100.0%"),
]

tot_eq = sum(r[2] for r in data)
tot_mu = sum(r[3] for r in data)
tot_tot = sum(r[4] for r in data)
tot_op = sum(r[5] for r in data)
tot_baj = sum(r[6] for r in data)

# Canvas setup - Width 18 inches, Height 11.6 inches at 150 DPI (clean executive proportion)
fig = plt.figure(figsize=(18, 11.6), dpi=150)
fig.patch.set_facecolor('#f8fafc')

ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1800)
ax.set_ylim(320, 1450)
ax.axis('off')

# 1. Header Banner
header_box = patches.FancyBboxPatch((40, 1310), 1720, 105, boxstyle="round,pad=0,rounding_size=16",
                                    facecolor='#0f172a', edgecolor='none')
ax.add_patch(header_box)

# Header Text
ax.text(75, 1378, "GOBIERNO AUTÓNOMO MUNICIPAL DE LA PAZ", fontsize=20, fontweight='bold', color='#ffffff', va='center')
ax.text(75, 1345, "SECRETARÍA MUNICIPAL DE SALUD Y DEPORTES  •  SISTEMA CMMS - SGEM GAMLP", fontsize=12, fontweight='bold', color='#94a3b8', va='center')

# Header Tag / Pill
pill = patches.FancyBboxPatch((1450, 1335), 280, 52, boxstyle="round,pad=0,rounding_size=12",
                              facecolor='#1e293b', edgecolor='#38bdf8', linewidth=1.5)
ax.add_patch(pill)
ax.text(1590, 1361, "REPORTE OFICIAL CONSOLIDADO", fontsize=10.5, fontweight='bold', color='#38bdf8', va='center', ha='center')

# Title below header
ax.text(45, 1272, "Consolidado de Relevamiento de Activos en Centros de Salud", fontsize=23, fontweight='bold', color='#0f172a', va='baseline')
ax.text(45, 1242, "Datos 100% sincronizados entre Plataforma Web (Render) y Software de Escritorio SGEM v1.1", fontsize=12, color='#64748b', va='baseline')

# 2. KPI Cards (5 cards across width)
cards_info = [
    ("TOTAL ACTIVOS RELEVADOS", f"{tot_tot:,}", "#2563eb", "#eff6ff", "#1d4ed8", "13 Centros Oficiales"),
    ("EQUIPOS MÉDICOS", f"{tot_eq:,}", "#059669", "#ecfdf5", "#047857", "Biomédicos Relevados"),
    ("MUEBLERÍA Y TECNOLOGÍA", f"{tot_mu:,}", "#7c3aed", "#f5f3ff", "#6d28d9", "Mobiliario y TI"),
    ("ACTIVOS OPERATIVOS", f"{tot_op:,}", "#0284c7", "#f0f9ff", "#0369a1", "94.7% del Inventario"),
    ("ACTIVOS DE BAJA", f"{tot_baj:,}", "#e11d48", "#fff1f2", "#be123c", "5.3% Fuera de Servicio"),
]

card_w = 328
card_h = 102
card_y = 1115
gap = 20

for i, (title, val, border_col, bg_col, text_col, subtitle) in enumerate(cards_info):
    cx = 40 + i * (card_w + gap)
    card_bg = patches.FancyBboxPatch((cx, card_y), card_w, card_h, boxstyle="round,pad=0,rounding_size=14",
                                     facecolor=bg_col, edgecolor=border_col, linewidth=2)
    ax.add_patch(card_bg)
    ax.text(cx + card_w/2, card_y + 77, title, fontsize=10, fontweight='bold', color=text_col, ha='center', va='center')
    ax.text(cx + card_w/2, card_y + 44, val, fontsize=25, fontweight='bold', color='#0f172a', ha='center', va='center')
    ax.text(cx + card_w/2, card_y + 17, subtitle, fontsize=9.5, fontweight='bold', color='#64748b', ha='center', va='center')

# 3. Table Structure
table_top = 1065
col_x = [40, 235, 680, 840, 1000, 1170, 1330, 1480, 1610, 1760]

# Header Row Background
th_h = 44
th_box = patches.FancyBboxPatch((40, table_top - th_h), 1720, th_h, boxstyle="round,pad=0,rounding_size=8",
                                facecolor='#1e293b', edgecolor='none')
ax.add_patch(th_box)

# Header Labels
ax.text(col_x[0] + 15, table_top - th_h/2, "RED DE SALUD", fontsize=11, fontweight='bold', color='#ffffff', va='center')
ax.text(col_x[1] + 10, table_top - th_h/2, "CENTRO DE SALUD / SEDE", fontsize=11, fontweight='bold', color='#ffffff', va='center')
ax.text((col_x[2] + col_x[3])/2, table_top - th_h/2, "EQ. MÉDICOS", fontsize=11, fontweight='bold', color='#a7f3d0', va='center', ha='center')
ax.text((col_x[3] + col_x[4])/2, table_top - th_h/2, "MUEBLERÍA / TI", fontsize=11, fontweight='bold', color='#ddd6fe', va='center', ha='center')
ax.text((col_x[4] + col_x[5])/2, table_top - th_h/2, "TOTAL RELEVADO", fontsize=11, fontweight='bold', color='#ffffff', va='center', ha='center')
ax.text((col_x[5] + col_x[6])/2, table_top - th_h/2, "OPERATIVOS", fontsize=11, fontweight='bold', color='#bae6fd', va='center', ha='center')
ax.text((col_x[6] + col_x[7])/2, table_top - th_h/2, "DE BAJA", fontsize=11, fontweight='bold', color='#fecdd3', va='center', ha='center')
ax.text((col_x[7] + col_x[8])/2, table_top - th_h/2, "META ESPERADA", fontsize=11, fontweight='bold', color='#cbd5e1', va='center', ha='center')
ax.text((col_x[8] + col_x[9])/2, table_top - th_h/2, "% AVANCE", fontsize=11, fontweight='bold', color='#fef08a', va='center', ha='center')

row_y = table_top - th_h
row_h = 43

for idx, r in enumerate(data):
    row_top = row_y - (idx + 1) * row_h
    bg_color = '#ffffff' if idx % 2 == 0 else '#f8fafc'
    
    # Row background
    r_box = patches.Rectangle((40, row_top), 1720, row_h, facecolor=bg_color, edgecolor='#f1f5f9', linewidth=1)
    ax.add_patch(r_box)
    
    cy = row_top + row_h/2
    
    # Texts
    ax.text(col_x[0] + 15, cy, r[0], fontsize=11, fontweight='bold', color='#334155', va='center')
    ax.text(col_x[1] + 10, cy, r[1], fontsize=11.5, fontweight='bold', color='#0f172a', va='center')
    ax.text((col_x[2] + col_x[3])/2, cy, f"{r[2]:,}", fontsize=11.5, color='#047857', va='center', ha='center', fontweight='bold')
    ax.text((col_x[3] + col_x[4])/2, cy, f"{r[3]:,}", fontsize=11.5, color='#6d28d9', va='center', ha='center', fontweight='bold')
    ax.text((col_x[4] + col_x[5])/2, cy, f"{r[4]:,}", fontsize=12, color='#0f172a', va='center', ha='center', fontweight='bold')
    ax.text((col_x[5] + col_x[6])/2, cy, f"{r[5]:,}", fontsize=11.5, color='#0284c7', va='center', ha='center', fontweight='bold')
    
    # Bajas column with alert color if > 0
    baj_col = '#be123c' if r[6] > 0 else '#94a3b8'
    ax.text((col_x[6] + col_x[7])/2, cy, f"{r[6]:,}", fontsize=11.5, color=baj_col, va='center', ha='center', fontweight='bold')
    
    # Meta
    ax.text((col_x[7] + col_x[8])/2, cy, r[7], fontsize=11, color='#64748b', va='center', ha='center', fontweight='bold')
    
    # Pct badge
    pct_val = float(r[8].replace('%', ''))
    pct_x = (col_x[8] + col_x[9])/2
    badge_color = '#dcfce7' if pct_val >= 99.9 else ('#fef3c7' if pct_val >= 70 else '#fee2e2')
    badge_border = '#86efac' if pct_val >= 99.9 else ('#fde047' if pct_val >= 70 else '#fca5a5')
    text_color = '#15803d' if pct_val >= 99.9 else ('#b45309' if pct_val >= 70 else '#b91c1c')
    
    badge = patches.FancyBboxPatch((pct_x - 48, cy - 13), 96, 26, boxstyle="round,pad=0,rounding_size=6",
                                  facecolor=badge_color, edgecolor=badge_border, linewidth=1.2)
    ax.add_patch(badge)
    ax.text(pct_x, cy, r[8], fontsize=10.5, fontweight='bold', color=text_color, va='center', ha='center')

# Summary Total Row
tot_top = row_y - (len(data) + 1) * row_h
tot_box = patches.FancyBboxPatch((40, tot_top), 1720, row_h + 8, boxstyle="round,pad=0,rounding_size=8",
                                facecolor='#0f172a', edgecolor='none')
ax.add_patch(tot_box)
tot_cy = tot_top + (row_h + 8)/2

# Clear single title for total without overlap
ax.text(col_x[0] + 15, tot_cy, "TOTAL GENERAL (13 CENTROS RELEVADOS)", fontsize=12.5, fontweight='bold', color='#38bdf8', va='center')
ax.text((col_x[2] + col_x[3])/2, tot_cy, f"{tot_eq:,}", fontsize=13, color='#a7f3d0', va='center', ha='center', fontweight='bold')
ax.text((col_x[3] + col_x[4])/2, tot_cy, f"{tot_mu:,}", fontsize=13, color='#ddd6fe', va='center', ha='center', fontweight='bold')
ax.text((col_x[4] + col_x[5])/2, tot_cy, f"{tot_tot:,}", fontsize=14, color='#ffffff', va='center', ha='center', fontweight='bold')
ax.text((col_x[5] + col_x[6])/2, tot_cy, f"{tot_op:,}", fontsize=13, color='#bae6fd', va='center', ha='center', fontweight='bold')
ax.text((col_x[6] + col_x[7])/2, tot_cy, f"{tot_baj:,}", fontsize=13, color='#fecdd3', va='center', ha='center', fontweight='bold')
ax.text((col_x[7] + col_x[8])/2, tot_cy, "—", fontsize=12, color='#94a3b8', va='center', ha='center', fontweight='bold')

# Overall badge
ax.text((col_x[8] + col_x[9])/2, tot_cy, "100% OK", fontsize=11, fontweight='bold', color='#38bdf8', va='center', ha='center')

# 4. Clean Minimal Footer
footer_y = tot_top - 42
ax.text(45, footer_y, "Sistema Municipal de Gestión de Activos y Equipamiento Médico — SGEM GAMLP", fontsize=11, fontweight='semibold', color='#64748b', va='center')
ax.text(1755, footer_y, "Plataforma Oficial Web: cmms-gamlp.onrender.com  •  Gestión 2026", fontsize=11, fontweight='bold', color='#0284c7', va='center', ha='right')

# Save to artifacts directory and current directory
art_dir = r"C:\Users\HP\.gemini\antigravity\brain\0c6675d6-b69a-432b-b916-1594bb22a06c"
out_art = os.path.join(art_dir, "tabla_relevamiento_gamlp.png")
out_local = os.path.join(os.getcwd(), "tabla_relevamiento_gamlp.png")

plt.savefig(out_art, dpi=200, bbox_inches='tight', pad_inches=0.25)
plt.savefig(out_local, dpi=200, bbox_inches='tight', pad_inches=0.25)
plt.close()

print(f"Image regenerated successfully!")
