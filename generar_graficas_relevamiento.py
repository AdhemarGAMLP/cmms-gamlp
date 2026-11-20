import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import sys

# Configure high quality font rendering
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'

# Dimensions: 16:9 Presentation slide at high resolution (2400 x 1350 px)
fig = plt.figure(figsize=(24, 13.5), dpi=120)
fig.patch.set_facecolor('#f8fafc')

# Master background ax for banners, cards and containers
ax_bg = fig.add_axes([0, 0, 1, 1])
ax_bg.set_xlim(0, 2400)
ax_bg.set_ylim(0, 1350)
ax_bg.axis('off')

# ==========================================
# 1. HEADER BANNER
# ==========================================
header_box = patches.FancyBboxPatch((50, 1220), 2300, 100, boxstyle="round,pad=0,rounding_size=16",
                                    facecolor='#0f172a', edgecolor='none')
ax_bg.add_patch(header_box)

ax_bg.text(90, 1285, "GOBIERNO AUTÓNOMO MUNICIPAL DE LA PAZ", fontsize=22, fontweight='bold', color='#ffffff', va='center')
ax_bg.text(90, 1252, "SECRETARÍA MUNICIPAL DE SALUD Y DEPORTES  •  DIRECCIÓN DE SALUD  •  SISTEMA CMMS - SGEM GAMLP", fontsize=12, fontweight='bold', color='#94a3b8', va='center')

# Header Pill
pill = patches.FancyBboxPatch((2020, 1245), 300, 50, boxstyle="round,pad=0,rounding_size=12",
                              facecolor='#1e293b', edgecolor='#38bdf8', linewidth=1.5)
ax_bg.add_patch(pill)
ax_bg.text(2170, 1270, "PRESENTACIÓN EJECUTIVA 2026", fontsize=11, fontweight='bold', color='#38bdf8', va='center', ha='center')

# Main Title
ax_bg.text(55, 1180, "Diagnóstico y Avance del Relevamiento Municipal de Activos", fontsize=25, fontweight='bold', color='#0f172a', va='baseline')
ax_bg.text(55, 1150, "Censo global sobre los 67 Centros de Salud Oficiales (Meta esperada: 18,535 activos fijos) • Datos Web y Software SGEM v1.1", fontsize=13, color='#64748b', va='baseline')

# ==========================================
# 2. TOP KPI CARDS (3 Cards across width - Clean & Spacious)
# ==========================================
kpis = [
    ("TOTAL ACTIVOS RELEVADOS", "4,456", "24.0% de la Meta Municipal (18,535 Activos Fijos)", "#2563eb", "#eff6ff", "#1d4ed8"),
    ("COBERTURA DE ESTABLECIMIENTOS", "13 de 67", "10 al 100% de su Meta  •  3 en Proceso  •  56 Pendientes", "#059669", "#ecfdf5", "#047857"),
    ("ESTADO DE FUNCIONAMIENTO", "4,218 Operativos", "94.7% Operativos  •  238 Activos de Baja Oficiales (5.3%)", "#0284c7", "#f0f9ff", "#0369a1"),
]

card_w = 740
card_h = 100
card_y = 1030
gap = 40

for i, (title, val, sub, border_col, bg_col, text_col) in enumerate(kpis):
    cx = 50 + i * (card_w + gap)
    card_bg = patches.FancyBboxPatch((cx, card_y), card_w, card_h, boxstyle="round,pad=0,rounding_size=14",
                                     facecolor=bg_col, edgecolor=border_col, linewidth=2)
    ax_bg.add_patch(card_bg)
    ax_bg.text(cx + card_w/2, card_y + 75, title, fontsize=11.5, fontweight='bold', color=text_col, ha='center', va='center')
    ax_bg.text(cx + card_w/2, card_y + 42, val, fontsize=27, fontweight='bold', color='#0f172a', ha='center', va='center')
    ax_bg.text(cx + card_w/2, card_y + 16, sub, fontsize=11, fontweight='semibold', color='#64748b', ha='center', va='center')

# ==========================================
# 3. PANEL 1: AVANCE POR RED (Professional Grouped Bar Chart)
# ==========================================
p1_x = 50
p1_y = 530
p1_w = 1120
p1_h = 475

p1_bg = patches.FancyBboxPatch((p1_x, p1_y), p1_w, p1_h, boxstyle="round,pad=0,rounding_size=14",
                              facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.5)
ax_bg.add_patch(p1_bg)

# Panel 1 Title
ax_bg.text(p1_x + 35, p1_y + p1_h - 35, "Avance de Relevamiento por Red de Salud", fontsize=17, fontweight='bold', color='#0f172a', va='center')
ax_bg.text(p1_x + 35, p1_y + p1_h - 58, "Comparativa de Activos Relevados frente a la Meta Oficial en cada Red Municipal", fontsize=11, color='#64748b', va='center')

# Add real Matplotlib sub-axes inside Panel 1
# Normalized coordinates in [0, 1] range:
chart_left = (p1_x + 75) / 2400.0
chart_bottom = (p1_y + 60) / 1350.0
chart_width = (p1_w - 110) / 2400.0
chart_height = (p1_h - 130) / 1350.0

ax_bar = fig.add_axes([chart_left, chart_bottom, chart_width, chart_height])
ax_bar.set_facecolor('#ffffff')

redes_labels = [
    "RED 1\nCotahuma\n(3 centros)",
    "RED 2\nMax Paredes\n(1 centro)",
    "RED 3\nPeriférica\n(2 centros)",
    "RED 4\nSan Antonio\n(5 centros)",
    "RED 5\nSur\n(2 centros)"
]
relevados = [1062, 267, 512, 1736, 879]
metas = [4335, 4268, 3626, 3216, 3090]
porcentajes = ["24.5%", "6.3%", "14.1%", "54.0%", "28.4%"]
pct_colors = ["#3b82f6", "#ef4444", "#f59e0b", "#10b981", "#0284c7"]

x = np.arange(len(redes_labels))
b_width = 0.32

# Plot Bars
rects_meta = ax_bar.bar(x + b_width/2, metas, b_width, label='Meta Oficial (Censo)', color='#e2e8f0', edgecolor='#cbd5e1', linewidth=1, zorder=3)
rects_rel = ax_bar.bar(x - b_width/2, relevados, b_width, label='Activos Relevados', color='#2563eb', edgecolor='none', zorder=4)

# Color special bars
rects_rel[3].set_color('#10b981') # Red 4 leader in green

# Custom styling for axes
ax_bar.set_ylim(0, 5200)
ax_bar.set_xticks(x)
ax_bar.set_xticklabels(redes_labels, fontsize=11, fontweight='bold', color='#1e293b')
ax_bar.yaxis.grid(True, linestyle='--', alpha=0.6, color='#cbd5e1', zorder=1)
ax_bar.set_axisbelow(True)

# Format y-ticks
ax_bar.set_yticks([0, 1000, 2000, 3000, 4000, 5000])
ax_bar.set_yticklabels(['0', '1,000', '2,000', '3,000', '4,000', '5,000'], fontsize=10.5, color='#64748b')

# Hide top and right spines
ax_bar.spines['top'].set_visible(False)
ax_bar.spines['right'].set_visible(False)
ax_bar.spines['left'].set_color('#cbd5e1')
ax_bar.spines['bottom'].set_color('#94a3b8')

# Bar Labels on Top of Bars
for r in rects_rel:
    h = r.get_height()
    ax_bar.annotate(f"{int(h):,}",
                    xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold', color='#1e293b')

for r in rects_meta:
    h = r.get_height()
    ax_bar.annotate(f"{int(h):,}",
                    xy=(r.get_x() + r.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='semibold', color='#64748b')

# Percentage badges above each pair
for i in range(len(x)):
    y_top = max(relevados[i], metas[i]) + 420
    # Add badge patch
    badge = patches.FancyBboxPatch((x[i] - 0.22, y_top - 120), 0.44, 260,
                                  boxstyle="round,pad=0.04,rounding_size=0.1",
                                  facecolor='#f8fafc', edgecolor=pct_colors[i], linewidth=1.5, zorder=5)
    ax_bar.add_patch(badge)
    ax_bar.text(x[i], y_top + 10, porcentajes[i], fontsize=11, fontweight='bold', color=pct_colors[i], ha='center', va='center', zorder=6)

# Legend at top right
ax_bar.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=10.5, framealpha=0.95)

# ==========================================
# 4. PANEL 2: DONUTS (Avance Global & Cobertura)
# ==========================================
p2_x = 1200
p2_y = 530
p2_w = 1150
p2_h = 475

p2_bg = patches.FancyBboxPatch((p2_x, p2_y), p2_w, p2_h, boxstyle="round,pad=0,rounding_size=14",
                              facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.5)
ax_bg.add_patch(p2_bg)

# Panel 2 Title
ax_bg.text(p2_x + 35, p2_y + p2_h - 35, "Distribución y Cobertura Territorial de Activos", fontsize=17, fontweight='bold', color='#0f172a', va='center')
ax_bg.text(p2_x + 35, p2_y + p2_h - 58, "Censo global consolidado sobre los 67 establecimientos de salud municipales", fontsize=11, color='#64748b', va='center')

# Left Donut: Activos Relevados vs Pendientes
donut1_center = (p2_x + 280, p2_y + 225)
d_radius = 120
d_width = 38

theta_rel = (4456 / 18535) * 360
w1 = patches.Wedge(donut1_center, d_radius, 90, 90 + theta_rel, width=d_width, facecolor='#2563eb', edgecolor='none')
w2 = patches.Wedge(donut1_center, d_radius, 90 + theta_rel, 90 + 360, width=d_width, facecolor='#e2e8f0', edgecolor='none')
ax_bg.add_patch(w1)
ax_bg.add_patch(w2)

ax_bg.text(donut1_center[0], donut1_center[1] + 12, "24.0%", fontsize=27, fontweight='bold', color='#0f172a', ha='center', va='center')
ax_bg.text(donut1_center[0], donut1_center[1] - 18, "RELEVADO", fontsize=10.5, fontweight='bold', color='#2563eb', ha='center', va='center')

# Legend Donut 1
ax_bg.text(donut1_center[0], p2_y + 55, "Meta Municipal (18,535 Activos)", fontsize=12, fontweight='bold', color='#1e293b', ha='center')
ax_bg.text(donut1_center[0], p2_y + 30, "• Relevado: 4,456 (24.0%)   • Pendiente: 14,079 (76.0%)", fontsize=10.5, color='#64748b', ha='center')

# Right Donut: Centros de Salud (13 Relevados vs 56 Pendientes)
donut2_center = (p2_x + 850, p2_y + 225)
theta_cen = (13 / 67) * 360
w3 = patches.Wedge(donut2_center, d_radius, 90, 90 + theta_cen, width=d_width, facecolor='#10b981', edgecolor='none')
w4 = patches.Wedge(donut2_center, d_radius, 90 + theta_cen, 90 + 360, width=d_width, facecolor='#e2e8f0', edgecolor='none')
ax_bg.add_patch(w3)
ax_bg.add_patch(w4)

ax_bg.text(donut2_center[0], donut2_center[1] + 12, "13 / 67", fontsize=26, fontweight='bold', color='#0f172a', ha='center', va='center')
ax_bg.text(donut2_center[0], donut2_center[1] - 18, "CENTROS", fontsize=10.5, fontweight='bold', color='#059669', ha='center', va='center')

# Legend Donut 2
ax_bg.text(donut2_center[0], p2_y + 55, "Cobertura de Establecimientos", fontsize=12, fontweight='bold', color='#1e293b', ha='center')
ax_bg.text(donut2_center[0], p2_y + 30, "• Relevados: 13 (19.4%)   • Pendientes: 56 Centros (80.6%)", fontsize=10.5, color='#64748b', ha='center')

# ==========================================
# 5. PANEL 3: RANKING Y DETALLE DE LOS 13 CENTROS RELEVADOS
# ==========================================
p3_x = 50
p3_y = 80
p3_w = 2300
p3_h = 425

p3_bg = patches.FancyBboxPatch((p3_x, p3_y), p3_w, p3_h, boxstyle="round,pad=0,rounding_size=14",
                              facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.5)
ax_bg.add_patch(p3_bg)

ax_bg.text(p3_x + 35, p3_y + p3_h - 30, "Ranking y Detalle de los 13 Establecimientos con Relevamiento Activo", fontsize=16, fontweight='bold', color='#0f172a', va='center')
ax_bg.text(p3_x + 35, p3_y + p3_h - 52, "Cifras oficiales de inventario físico verificado en campo (1,150 Equipos Médicos + 3,306 Mueblería/TI)", fontsize=11, color='#64748b', va='center')

# Table of 13 Centers in 2 Columns (7 left, 6 right)
centros_ordered = [
    # Centro, Red, Eq, Mu, Tot, Op, Baj, Meta, Pct, Status
    ("C.M.I. Villa Nuevo Potosí", "RED 1", 124, 555, 679, 673, 6, "647", "100.0%", "#10b981", "Completo"),
    ("C.M.I. Pampahasi Bajo", "RED 4", 168, 467, 635, 628, 7, "588", "100.0%", "#10b981", "Completo"),
    ("C.M.I. Chasquipampa", "RED 5", 135, 418, 553, 535, 18, "373", "100.0%", "#10b981", "Completo"),
    ("Lab. Bebidas y Alimentos", "RED 3", 168, 197, 365, 355, 10, "—", "100.0%", "#10b981", "Especializado"),
    ("Bajo San Pedro", "RED 1", 66, 276, 342, 340, 2, "411", "83.2%", "#f59e0b", "En Proceso"),
    ("Alto Obrajes", "RED 5", 102, 224, 326, 306, 20, "211", "100.0%", "#10b981", "Completo"),
    ("San Antonio Alto", "RED 4", 54, 258, 312, 284, 28, "287", "100.0%", "#10b981", "Completo"),
    ("Pampahasi Alto", "RED 4", 52, 222, 274, 273, 1, "264", "100.0%", "#10b981", "Completo"),
    ("Apumalla", "RED 2", 60, 207, 267, 247, 20, "211", "100.0%", "#10b981", "Completo"),
    ("San Antonio Bajo", "RED 4", 30, 233, 263, 258, 5, "336", "78.3%", "#f59e0b", "En Proceso"),
    ("Villa Copacabana", "RED 4", 54, 198, 252, 242, 10, "224", "100.0%", "#10b981", "Completo"),
    ("Asistencia Pública", "RED 3", 116, 31, 147, 36, 111, "794", "18.5%", "#ef4444", "En Proceso"),
    ("Almacén Central", "RED 1", 21, 20, 41, 41, 0, "—", "100.0%", "#10b981", "Especializado"),
]

col1_x = p3_x + 30
col2_x = p3_x + 1160
c_w = 1080
row_h_card = 42

for idx, c in enumerate(centros_ordered):
    col = col1_x if idx < 7 else col2_x
    row_idx = idx if idx < 7 else idx - 7
    card_top = p3_y + p3_h - 95 - row_idx * (row_h_card + 6)
    
    bg_s = patches.FancyBboxPatch((col, card_top), c_w, row_h_card, boxstyle="round,pad=0,rounding_size=8",
                                 facecolor='#f8fafc' if row_idx % 2 == 0 else '#ffffff',
                                 edgecolor='#e2e8f0', linewidth=1)
    ax_bg.add_patch(bg_s)
    
    mid_y = card_top + row_h_card/2
    
    # Status Dot
    s_dot = patches.Circle((col + 20, mid_y), 6, facecolor=c[9], edgecolor='none')
    ax_bg.add_patch(s_dot)
    
    # Red Badge
    ax_bg.text(col + 40, mid_y, c[1], fontsize=10.5, fontweight='bold', color='#475569', va='center')
    
    # Center Name
    ax_bg.text(col + 115, mid_y, c[0], fontsize=11.5, fontweight='bold', color='#0f172a', va='center')
    
    # Counts
    ax_bg.text(col + 450, mid_y, f"Eq: {c[2]}", fontsize=10.5, fontweight='semibold', color='#059669', va='center')
    ax_bg.text(col + 540, mid_y, f"Mu: {c[3]}", fontsize=10.5, fontweight='semibold', color='#7c3aed', va='center')
    ax_bg.text(col + 640, mid_y, f"Total: {c[4]}", fontsize=11, fontweight='bold', color='#0f172a', va='center')
    ax_bg.text(col + 750, mid_y, f"Op: {c[5]}", fontsize=10.5, fontweight='semibold', color='#0284c7', va='center')
    ax_bg.text(col + 840, mid_y, f"Baj: {c[6]}", fontsize=10.5, fontweight='bold', color='#e11d48' if c[6]>0 else '#94a3b8', va='center')
    
    # Pct and Badge
    pct_badge = patches.FancyBboxPatch((col + 920, mid_y - 12), 70, 24, boxstyle="round,pad=0,rounding_size=6",
                                      facecolor='#ecfdf5' if '100' in c[8] else ('#fffbeb' if '83' in c[8] or '78' in c[8] else '#fef2f2'),
                                      edgecolor=c[9], linewidth=1)
    ax_bg.add_patch(pct_badge)
    ax_bg.text(col + 955, mid_y, c[8], fontsize=10, fontweight='bold', color=c[9], va='center', ha='center')
    
    ax_bg.text(col + 1010, mid_y, c[10], fontsize=9.5, fontweight='bold', color='#64748b', va='center')

# ==========================================
# 6. FOOTER BAR
# ==========================================
footer_y = 35
ax_bg.text(55, footer_y, "Gobierno Autónomo Municipal de La Paz  •  Secretaría Municipal de Salud y Deportes  •  CMMS GAMLP", fontsize=11, fontweight='semibold', color='#64748b', va='center')
ax_bg.text(2345, footer_y, "Plataforma Web Oficial: cmms-gamlp.onrender.com  |  Sincronización Cloud Supabase 2026", fontsize=11, fontweight='bold', color='#0284c7', va='center', ha='right')

# Save outputs cleanly
art_dir = r"C:\Users\HP\.gemini\antigravity\brain\0c6675d6-b69a-432b-b916-1594bb22a06c"
out_art = os.path.join(art_dir, "graficas_relevamiento_gamlp.png")
out_local = os.path.join(os.getcwd(), "graficas_relevamiento_gamlp.png")

plt.savefig(out_art, dpi=160, bbox_inches='tight', pad_inches=0.2)
plt.close()

import shutil
shutil.copyfile(out_art, out_local)

print(f"Presentation slide regenerated successfully!")
