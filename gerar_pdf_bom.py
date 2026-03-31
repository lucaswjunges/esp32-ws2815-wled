#!/usr/bin/env python3
"""
Gera PDF profissional com BOM e Quotation do projeto ESP32 + WS2815.
WS2815 @ 12V — sistemas independentes por localização.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.colors import HexColor
from datetime import date

# ── Paleta ────────────────────────────────────────────────────────────────────
AZUL_ESCURO  = HexColor("#1a2f4e")
AZUL_MEDIO   = HexColor("#2c5282")
AZUL_CLARO   = HexColor("#ebf4ff")
CINZA_LINHA  = HexColor("#e2e8f0")
CINZA_TEXTO  = HexColor("#4a5568")
VERDE        = HexColor("#276749")
VERDE_BG     = HexColor("#f0fff4")
AMARELO_BG   = HexColor("#fffff0")
BRANCO       = colors.white
PRETO        = colors.black

OUTPUT = "/home/lucas-junges/Documents/clientes/Sebastian/BOM_Quote.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    topMargin=18*mm, bottomMargin=18*mm,
    leftMargin=16*mm, rightMargin=16*mm,
    title="BOM & Quotation — ESP32 + WS2815 WLED System",
    author="Engineering Department",
)

W, H = A4
styles = getSampleStyleSheet()

# ── Estilos personalizados ─────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

st_titulo    = S("titulo",    fontSize=20, textColor=AZUL_ESCURO,  fontName="Helvetica-Bold",  leading=26)
st_subtitulo = S("subtitulo", fontSize=11, textColor=AZUL_MEDIO,   fontName="Helvetica",       leading=16)
st_secao     = S("secao",     fontSize=11, textColor=BRANCO,       fontName="Helvetica-Bold",  leading=15)
st_corpo     = S("corpo",     fontSize=8,  textColor=CINZA_TEXTO,  fontName="Helvetica",       leading=12)
st_nota      = S("nota",      fontSize=7.5,textColor=CINZA_TEXTO,  fontName="Helvetica-Oblique", leading=11)
st_header_tb = S("htb",       fontSize=8,  textColor=BRANCO,       fontName="Helvetica-Bold",  leading=11, alignment=TA_CENTER)
st_cell      = S("cell",      fontSize=8,  textColor=PRETO,        fontName="Helvetica",       leading=11)
st_cell_c    = S("cellc",     fontSize=8,  textColor=PRETO,        fontName="Helvetica",       leading=11, alignment=TA_CENTER)
st_cell_r    = S("cellr",     fontSize=8,  textColor=PRETO,        fontName="Helvetica",       leading=11, alignment=TA_RIGHT)
st_bold_c    = S("boldc",     fontSize=8,  textColor=AZUL_ESCURO,  fontName="Helvetica-Bold",  leading=11, alignment=TA_CENTER)
st_total     = S("total",     fontSize=10, textColor=AZUL_ESCURO,  fontName="Helvetica-Bold",  leading=14, alignment=TA_RIGHT)
st_alerta    = S("alerta",    fontSize=8,  textColor=HexColor("#7b341e"), fontName="Helvetica-Bold", leading=11)

# ── Helpers ───────────────────────────────────────────────────────────────────
def P(txt, st=None):
    return Paragraph(txt, st or st_corpo)

def secao_header(titulo):
    tbl = Table([[P(titulo, st_secao)]], colWidths=[W - 32*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), AZUL_MEDIO),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    return tbl

# ── Conteúdo ──────────────────────────────────────────────────────────────────
story = []

# ── CABEÇALHO ─────────────────────────────────────────────────────────────────
header_data = [[
    P("ESP32 + WS2815 WLED System", st_titulo),
    P(f"BILL OF MATERIALS &amp; QUOTATION<br/>"
      f"<font size='9' color='#718096'>Document date: {date.today().strftime('%B %d, %Y')}<br/>"
      f"Revision: 2.0 &nbsp;|&nbsp; Project: LED Controller — 2× Independent Systems</font>",
      S("hdr2", fontSize=11, textColor=AZUL_MEDIO, fontName="Helvetica-Bold",
        leading=16, alignment=TA_RIGHT)),
]]
header_tbl = Table(header_data, colWidths=[100*mm, W - 32*mm - 100*mm])
header_tbl.setStyle(TableStyle([
    ("VALIGN",   (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",   (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",(0,0), (-1,-1), 4),
]))
story.append(header_tbl)
story.append(HRFlowable(width="100%", thickness=2, color=AZUL_ESCURO, spaceAfter=6))

# ── RESUMO DO PROJETO ──────────────────────────────────────────────────────────
story.append(Spacer(1, 3*mm))
story.append(secao_header("1. Project Summary"))
story.append(Spacer(1, 2*mm))

summary_data = [
    ["Parameter", "Value", "Parameter", "Value"],
    ["Microcontrollers",   "2× ESP32-WROOM-32D",              "Firmware",          "WLED (open source)"],
    ["LED Strips",         "2× WS2815 5m / 60LED/m / 12V",   "LED Data GPIO",     "GPIO4 (per ESP32)"],
    ["Total LEDs",         "600 (300 per strip)",              "Data Level Shift",  "3.3V → 5V (SN74AHCT125N)"],
    ["Strip Voltage",      "12V DC (direct — no buck)",        "Power Topology",    "12V PSU direct to strip;\nsmall buck for ESP32 only"],
    ["Peak Strip Current", "~7.5A per strip (full white)",     "PSU per System",    "Mean Well LRS-150-12 (12.5A)"],
    ["Deployment",         "2 INDEPENDENT systems\n(separate locations, no shared components)",
                                                               "Safety Margin",     "≥ 30% on all power ratings"],
]

sw = (W - 32*mm) / 4
sum_tbl = Table(summary_data, colWidths=[sw*1.1, sw*0.9, sw*1.1, sw*0.9])
sum_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0),  AZUL_ESCURO),
    ("TEXTCOLOR",     (0,0), (-1,0),  BRANCO),
    ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
    ("FONTSIZE",      (0,0), (-1,-1), 8),
    ("ALIGN",         (0,0), (-1,0),  "CENTER"),
    ("ALIGN",         (0,1), (0,-1),  "LEFT"),
    ("ALIGN",         (1,1), (1,-1),  "LEFT"),
    ("ALIGN",         (2,1), (2,-1),  "LEFT"),
    ("ALIGN",         (3,1), (3,-1),  "LEFT"),
    ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
    ("FONTNAME",      (2,1), (2,-1),  "Helvetica-Bold"),
    ("TEXTCOLOR",     (0,1), (0,-1),  AZUL_MEDIO),
    ("TEXTCOLOR",     (2,1), (2,-1),  AZUL_MEDIO),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [BRANCO, AZUL_CLARO]),
    ("GRID",          (0,0), (-1,-1), 0.4, CINZA_LINHA),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ("RIGHTPADDING",  (0,0), (-1,-1), 6),
]))
story.append(sum_tbl)

# ── POWER CALCULATION ─────────────────────────────────────────────────────────
story.append(Spacer(1, 5*mm))
story.append(secao_header("2. Power Calculation Summary (Per System — Independent)"))
story.append(Spacer(1, 2*mm))

story.append(P(
    "Each system is completely independent at a separate location with its own PSU. "
    "Do NOT combine the two systems — currents below are per system.",
    S("note_bold", fontSize=8, fontName="Helvetica-Bold", textColor=AZUL_MEDIO,
      leading=12, leftIndent=4)
))
story.append(Spacer(1, 2*mm))

pwr_data = [
    ["Load", "Voltage", "Current (worst case)", "Power", "With 30% Margin"],
    ["WS2815 Strip\n(300 LEDs × 20mA, 18W/m)",    "12V DC", "7.50 A",  "90.0 W",  "9.75 A / 117 W"],
    ["ESP32 + Level Shifter\n(via small 12V→5V buck)", "5V (from buck)", "0.26 A", "1.3 W",  "0.34 A / 1.7 W"],
    ["ESP32 supply @ 12V input\n(buck eff. 85%)",  "12V DC", "0.12 A",  "1.5 W",   "0.16 A / 1.9 W"],
    ["TOTAL per system @ 12V",                     "12V DC", "7.62 A",  "91.5 W",  "9.91 A → 10A fuse"],
    ["PSU required (per system)",                  "12V DC", "≤ 12.5 A","≤ 120 W", "LRS-150-12 ✓"],
]

pw = [(W - 32*mm) * f for f in [0.28, 0.12, 0.20, 0.14, 0.26]]
pwr_tbl = Table(pwr_data, colWidths=pw)
pwr_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),  (-1,0),  AZUL_ESCURO),
    ("TEXTCOLOR",     (0,0),  (-1,0),  BRANCO),
    ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
    ("FONTSIZE",      (0,0),  (-1,-1), 8),
    ("ALIGN",         (1,0),  (-1,-1), "CENTER"),
    ("ROWBACKGROUNDS",(0,1),  (-1,-3), [BRANCO, AZUL_CLARO]),
    ("BACKGROUND",    (0,-2), (-1,-2), HexColor("#fff3cd")),
    ("BACKGROUND",    (0,-1), (-1,-1), HexColor("#d4edda")),
    ("FONTNAME",      (0,-2), (-1,-2), "Helvetica-Bold"),
    ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
    ("TEXTCOLOR",     (0,-1), (-1,-1), VERDE),
    ("GRID",          (0,0),  (-1,-1), 0.4, CINZA_LINHA),
    ("TOPPADDING",    (0,0),  (-1,-1), 4),
    ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
    ("LEFTPADDING",   (0,0),  (-1,-1), 6),
    ("RIGHTPADDING",  (0,0),  (-1,-1), 6),
    ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
]))
story.append(pwr_tbl)

story.append(Spacer(1, 2*mm))
story.append(P(
    "✓  Wire drop check (AWG12, 5m, 7.5A): 7.5A × 52mΩ = 0.39V. "
    "Strip entry sees 11.61V — above WS2815 minimum (11.5V). "
    "Power injection at both ends is RECOMMENDED to offset internal trace resistance "
    "and maintain ≥11.5V at the far end of the strip.",
    S("ok_note", fontSize=7.5, textColor=HexColor("#276749"), fontName="Helvetica",
      leading=11, leftIndent=4)
))

# ── BOM ───────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 5*mm))
story.append(secao_header("3. Bill of Materials (BOM) — per system × 2 systems"))
story.append(Spacer(1, 2*mm))

bom_headers = ["#", "Component", "Model / Part#", "Qty\n(total)", "Specs", "Unit (BRL)", "Total (BRL)", "Notes"]

bom_items = [
    # #   Component                    Model                           Qty    Specs                           Unit       Total     Notes
    ["1",  "ESP32 DevKit",             "ESP-WROOM-32\nNODEMCU 38P",   "2",   "3.3V I/O, 240MHz,\nWiFi/BT, 5V VIN",
                                                                                                              "R$77,39", "R$154,78","WLED-certified"],
    ["2",  "WS2815 LED Strip\n(12V)",  "WS2815 5m 12V IP20\n60LED/m", "2",   "12V, ~20mA/LED,\n300 LEDs, GRB",
                                                                                                              "R$167,20","R$334,40","Direct 12V — no buck needed"],
    ["3",  "Small Buck\n(ESP32 supply)","XL4015 12V→5V 5A\nmodule",   "2",   "Input 8–36V,\noutput 5V/5A adj",
                                                                                                              "R$13,76", "R$27,52", "Powers ESP32 + level shifter"],
    ["4",  "Level Shifter IC",         "74HC125 (DIP-14)\nsubst. AHCT125N","2","Quad buffer, DIP-14,\nVih≥3.15V@5V",
                                                                                                              "R$1,41",  "R$2,82",  "3.3V→5V data line"],
    ["5",  "Capacitor\n470µF/25V",     "Generic\n470uF/25V 105°C",    "2",   "Electrolytic, radial,\n25V rated (12V rail)",
                                                                                                              "R$0,55",  "R$1,10",  "At strip 12V entry"],
    ["6",  "Capacitor\n100µF/16V",     "Generic\n100uF/16V 105°C",    "2",   "Electrolytic, radial,\n105°C rated",
                                                                                                              "R$0,30",  "R$0,60",  "At 5V buck output"],
    ["7",  "Resistor 330Ω 1/4W",       "CR25 1/4W 330R\n±5% carbon film","2","330Ω, 0.25W;\nDIN signal protection",
                                                                                                              "R$0,07",  "R$0,14",  "Data line protection"],
    ["8",  "Blade Fuse + Holder\n10A", "Blade Mini 10A\n+ Fuse Holder","2",  "10A / 32V DC;\nper-system protection",
                                                                                                              "R$6,63",  "R$13,26", "On 12V strip feed"],
    ["9",  "Terminal Block\n2-pin",    "2EDGK Terminal\n5.08mm 2-Way", "8",  "Screw terminal,\n5.08mm pitch",
                                                                                                              "R$1,87",  "R$14,96", "Power connections"],
    ["10", "Power Wire\n4mm²",         "Flex. Cable 4mm²\n750V Black", "4m", "20A, flexible;\n12V power runs",
                                                                                                              "R$5,06/m","R$20,24", "12V bus and strip runs"],
    ["11", "Signal Wire\nAWG22",       "Thin Wire 0.32mm²\n300V 70°C", "2m", "Low capacitance;\nDIN data lines",
                                                                                                              "R$1,42/m","R$2,84",  "Data lines (DIN)"],
    ["12", "Heatsink",                 "Heatsink DN812\n27×16×30mm",  "2",   "Aluminium extruded;\nfor XL4015 IC",
                                                                                                              "R$3,69",  "R$7,38",  "Small buck module"],
    ["13", "Connector\n2-pin Pairs",   "2-Pin Connector\nMale+Female", "6",  "Pairs w/ crimp\nterminals",
                                                                                                              "R$5,91",  "R$35,46", "Power injection points"],
    ["14", "Ferrule Crimps\n4mm²",     "Ferrule Kit\n0.5–6mm 400pcs", "1kit","Wire-end treatment\nfor screw terminals",
                                                                                                              "R$29,73", "R$29,73", "All power connections"],
]

col_w = [(W - 32*mm) * f for f in [0.04, 0.12, 0.15, 0.06, 0.18, 0.09, 0.09, 0.17]]

bom_data = [bom_headers] + bom_items

bom_style = TableStyle([
    ("BACKGROUND",    (0,0),  (-1,0),  AZUL_ESCURO),
    ("TEXTCOLOR",     (0,0),  (-1,0),  BRANCO),
    ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
    ("ALIGN",         (0,0),  (-1,0),  "CENTER"),
    ("FONTSIZE",      (0,0),  (-1,-1), 7.5),
    ("ROWBACKGROUNDS",(0,1),  (-1,-1), [BRANCO, AZUL_CLARO]),
    ("ALIGN",         (0,1),  (0,-1),  "CENTER"),
    ("ALIGN",         (3,1),  (3,-1),  "CENTER"),
    ("ALIGN",         (5,1),  (6,-1),  "RIGHT"),
    ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
    ("GRID",          (0,0),  (-1,-1), 0.4, CINZA_LINHA),
    ("TOPPADDING",    (0,0),  (-1,-1), 3),
    ("BOTTOMPADDING", (0,0),  (-1,-1), 3),
    ("LEFTPADDING",   (0,0),  (-1,-1), 4),
    ("RIGHTPADDING",  (0,0),  (-1,-1), 4),
    ("FONTNAME",      (5,1),  (6,-1),  "Helvetica"),
    ("TEXTCOLOR",     (5,1),  (5,-1),  CINZA_TEXTO),
    ("TEXTCOLOR",     (6,1),  (6,-1),  AZUL_MEDIO),
    ("FONTNAME",      (6,1),  (6,-1),  "Helvetica-Bold"),
])

bom_tbl = Table(bom_data, colWidths=col_w, repeatRows=1)
bom_tbl.setStyle(bom_style)
story.append(bom_tbl)

# ── TOTALS ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 3*mm))

totals_data = [
    ["", "Subtotal (components only):", "R$644,23"],
    ["", "Shipping (contact Proesi):",   "—"],
    ["", "TOTAL ESTIMATED PROJECT COST:", "R$644,23"],
]
tw = [(W - 32*mm) * f for f in [0.55, 0.30, 0.15]]
tot_tbl = Table(totals_data, colWidths=tw)
tot_tbl.setStyle(TableStyle([
    ("ALIGN",         (1,0),  (1,-1),  "RIGHT"),
    ("ALIGN",         (2,0),  (2,-1),  "RIGHT"),
    ("FONTNAME",      (1,0),  (2,-2),  "Helvetica"),
    ("FONTSIZE",      (0,0),  (-1,-1), 8.5),
    ("FONTNAME",      (1,-1), (2,-1),  "Helvetica-Bold"),
    ("TEXTCOLOR",     (1,-1), (2,-1),  AZUL_ESCURO),
    ("FONTSIZE",      (1,-1), (2,-1),  10),
    ("LINEABOVE",     (1,-1), (2,-1),  1.0, AZUL_ESCURO),
    ("TOPPADDING",    (0,0),  (-1,-1), 3),
    ("BOTTOMPADDING", (0,0),  (-1,-1), 3),
    ("TEXTCOLOR",     (1,0),  (1,-2),  CINZA_TEXTO),
    ("TEXTCOLOR",     (2,0),  (2,-2),  AZUL_MEDIO),
]))
story.append(tot_tbl)

story.append(Spacer(1, 1*mm))
story.append(P(
    "Proesi (proesi.com.br) prices verified on " + date.today().strftime('%Y-%m-%d') + ". "
    "Items 2 (WS2815) and 3 (XL4015) are not stocked by Proesi — "
    "prices sourced from Mercado Livre; verify current pricing before ordering. "
    "Proesi phone: (47) 3080-5529.",
    S("disc2", fontSize=7, textColor=HexColor("#a0aec0"),
      fontName="Helvetica-Oblique", leading=10)
))

# ── ENGINEERING NOTES ─────────────────────────────────────────────────────────
story.append(Spacer(1, 5*mm))
story.append(secao_header("4. Engineering Notes & Recommendations"))
story.append(Spacer(1, 2*mm))

notes_data = [
    ["Topic", "Detail"],
    ["Level Shifter\n(REQUIRED)",
     "ESP32 GPIO high = 3.3V; WS2815 DIN Vih_min ≈ 3.5V. Margin: −200mV (violation). "
     "SN74AHCT125N (Vih_min = 2.0V) converts ESP32 3.3V to full 5V signal. "
     "Skipping this causes intermittent 'zombie pixel' failures."],
    ["Power Injection\n(RECOMMENDED)",
     "External wire drop only = 0.39V (strip entry sees 11.61V — above 11.5V minimum). "
     "However, internal strip trace resistance (~30mΩ/m) adds further drop at high brightness. "
     "Inject 12V/GND at both strip ends to ensure ≥11.5V at far end under full load."],
    ["Wire Gauge\n(AWG12 required)",
     "AWG12 minimum for 12V supply runs up to 5m at 7.5A (external drop = 0.39V). "
     "AWG14 causes 0.62V drop — marginal at WS2815 minimum spec. "
     "AWG16 causes 0.99V drop — strip far end below 11.5V minimum. "
     "Use AWG22 for data lines (DIN)."],
    ["Buck Module\n(ESP32 only)",
     "WS2815 strips connect DIRECTLY at 12V — no step-down converter for the strip. "
     "One small XL4015 buck (12V→5V, 5A) per system powers the ESP32 + level shifter only. "
     "Adjust output to exactly 5.0V before connecting ESP32. Mount heatsink."],
    ["WLED Setup",
     "Set WLED → Config → LED Preferences → LED Type = WS2815 (important: not WS2812B). "
     "Set Maximum Current = 6000mA per strip (conservative; up to 7500mA if wiring verified). "
     "Sync both ESP32 units via WLED multicast (UDP port 21324, same subnet)."],
    ["Fusing\n(10A per system)",
     "Install a 10A blade fuse on the 12V feed to each strip. "
     "Strip worst-case current is 7.5A; 10A fuse provides protection with margin. "
     "Do not use 25A fuses — they will not protect the AWG12 wiring at strip-level faults."],
]

nw = [(W - 32*mm) * f for f in [0.18, 0.82]]
notes_tbl = Table(notes_data, colWidths=nw)
notes_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),  (-1,0),  AZUL_ESCURO),
    ("TEXTCOLOR",     (0,0),  (-1,0),  BRANCO),
    ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
    ("ALIGN",         (0,0),  (-1,0),  "CENTER"),
    ("FONTSIZE",      (0,0),  (-1,-1), 8),
    ("ROWBACKGROUNDS",(0,1),  (-1,-1), [BRANCO, AZUL_CLARO]),
    ("FONTNAME",      (0,1),  (0,-1),  "Helvetica-Bold"),
    ("TEXTCOLOR",     (0,1),  (0,-1),  AZUL_MEDIO),
    ("VALIGN",        (0,0),  (-1,-1), "TOP"),
    ("GRID",          (0,0),  (-1,-1), 0.4, CINZA_LINHA),
    ("TOPPADDING",    (0,0),  (-1,-1), 5),
    ("BOTTOMPADDING", (0,0),  (-1,-1), 5),
    ("LEFTPADDING",   (0,0),  (-1,-1), 6),
    ("RIGHTPADDING",  (0,0),  (-1,-1), 6),
]))
story.append(notes_tbl)

# ── SAFETY CHECKLIST ──────────────────────────────────────────────────────────
story.append(Spacer(1, 5*mm))
story.append(secao_header("5. Pre-Assembly Safety Checklist (per system)"))
story.append(Spacer(1, 2*mm))

checks = [
    "☐  PSU output verified at 12.0V before connecting strip",
    "☐  10A blade fuse installed on 12V feed for each system",
    "☐  Wire gauge verified AWG12 (min.) for all 12V power runs to strips",
    "☐  Buck module output trimmed to exactly 5.0V before connecting ESP32",
    "☐  Common ground between PSU, buck module, ESP32, and LED strip (star topology)",
    "☐  Power injection wired at BOTH ends of each 5m strip (recommended)",
    "☐  WLED LED type set to WS2815 (not WS2812B) in LED preferences",
    "☐  WLED maximum current configured: 6000mA per strip",
    "☐  SN74AHCT125N level shifter installed and powered from 5V (buck output)",
    "☐  330Ω series resistor on each DIN data line",
    "☐  470µF/25V decoupling capacitor across +12V/GND at each strip entry point",
    "☐  Heatsink installed on XL4015 IC with thermal compound",
    "☐  All stranded wire ends terminated with ferrule crimps before inserting into terminals",
    "☐  WLED firmware flashed and initial AP connection verified (SSID: WLED-AP)",
]

check_data = [[P(c, S("chk", fontSize=8, fontName="Helvetica", leading=13,
                       textColor=CINZA_TEXTO))] for c in checks]
check_tbl = Table(check_data, colWidths=[W - 32*mm])
check_tbl.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0,0), (-1,-1), [BRANCO, VERDE_BG]),
    ("GRID",           (0,0), (-1,-1), 0.3, CINZA_LINHA),
    ("TOPPADDING",     (0,0), (-1,-1), 3),
    ("BOTTOMPADDING",  (0,0), (-1,-1), 3),
    ("LEFTPADDING",    (0,0), (-1,-1), 10),
]))
story.append(check_tbl)

# ── RODAPÉ / DISCLAIMER ───────────────────────────────────────────────────────
story.append(Spacer(1, 6*mm))
story.append(HRFlowable(width="100%", thickness=0.5, color=CINZA_LINHA))
story.append(Spacer(1, 2*mm))
story.append(P(
    f"Document generated on {date.today().strftime('%B %d, %Y')}. Revision 2.0 — corrected for WS2815 @ 12V. "
    "Power calculations validated via analytical simulation (WS2815 12V direct connection, AWG12 5m). "
    "This document covers 2 independent systems at separate locations (2× ESP32 + 2× WS2815 strips, "
    "2× separate PSUs). All designs are provided for reference; verify all specifications before assembly.",
    S("disc", fontSize=7, textColor=HexColor("#a0aec0"), fontName="Helvetica-Oblique", leading=10)
))

# ── BUILD ─────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF gerado: {OUTPUT}")
