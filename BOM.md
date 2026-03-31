# Bill of Materials — ESP32 + WS2815 WLED System

## System Overview
- 2× independent systems at separate locations (no shared components)
- Each system: 1× ESP32 + 1× WS2815 5m LED strip + 1× 12V PSU
- WS2815 strips connect directly to 12V — no step-down converter for strip power
- Small 12V→5V buck module per system powers only the ESP32 + level shifter

---

| # | Component | Model / Part# | Qty | Specs | Max Current | Notes |
|---|-----------|--------------|-----|-------|-------------|-------|
| 1 | ESP32 DevKit | ESP32-DevKitC-32D (WROOM-32D) | 2 | 3.3V I/O, 5V tolerant VIN, 240MHz dual-core | 240 mA peak | Official Espressif board; WLED-certified |
| 2 | WS2815 LED Strip | BTF-LIGHTING WS2815 60LED/m IP30 5m | 2 | **12V**, ~20 mA/LED, 300 LEDs total | **7.5 A each** | 12V native — connects directly to PSU; backup data line (WS2815 feature) |
| 3 | PSU per system | Mean Well LRS-150-12 | **2** | 12V DC, 12.5A, 150W | 12.5 A | One PSU per location; UL/CE listed |
| 4 | ESP32 Buck Module | MP1584EN 12V→5V 3A | 2 | Input: 4.5–28V / Output: 5V adj, 3A | 3 A | Powers ESP32 + level shifter only; adjust output to 5.0V before connecting |
| 5 | Level Shifter | Texas Instruments SN74AHCT125N | 2 | VCC: 5V; Vih_min: 2V (accepts 3.3V input) | ~8 mA | Converts ESP32 3.3V data → 5V for WS2815 DIN |
| 6 | Bulk Capacitor (strip entry) | Nichicon 470µF/25V electrolytic | 2 | 470 µF / 25V | — | At strip 12V entry point; suppresses inrush transients |
| 7 | Filter Capacitor (buck output) | Nichicon 100µF/10V electrolytic | 2 | 100 µF / 10V | — | At 5V buck output; stabilizes ESP32 supply |
| 8 | Data Resistor | Generic metal film 330Ω 1/4W | 2 | 330 Ω ±1% | — | Series on DIN; protects against ringing & signal reflection |
| 9 | Blade Fuse + Holder | Littelfuse FBLPF **10A** | 2 | **10A** / 32V DC | — | Per-system overcurrent protection on 12V strip feed |
| 10 | Terminal Blocks | WAGO 2-conductor 5mm pitch (20A) | 8 | 20A / 450V | — | Power connections (PSU output + strip entry per system) |
| 11 | Power Wire | Silicone AWG12 red + black | 4 m | 600V, 20A rated | — | 12V bus and strip power runs |
| 12 | Signal Wire | AWG22 stranded | 2 m | Low capacitance | — | Data line: ESP32 → level shifter → strip DIN |
| 13 | Heatsink | Aluminum 20×20×10mm | 2 | Rθ ≈ 15°C/W | — | For MP1584EN module if needed at sustained load |
| 14 | PCB / Protoboard | 100×100mm double-sided | 2 | — | — | Per-system component mounting |

---

## Estimated Cost (USD, approximate)

| Item | Unit Price | Qty | Total |
|------|-----------|-----|-------|
| ESP32-DevKitC-32D | $5.00 | 2 | $10.00 |
| WS2815 5m strip (12V) | $14.00 | 2 | $28.00 |
| Mean Well LRS-150-12 | $22.00 | 2 | $44.00 |
| MP1584EN buck module (12V→5V) | $1.00 | 2 | $2.00 |
| SN74AHCT125N level shifter | $0.50 | 2 | $1.00 |
| Capacitors + resistors | — | — | $2.00 |
| Fuses + holders (10A) | $1.50 | 2 | $3.00 |
| Wire, terminals, hardware | — | — | $8.00 |
| **Total** | | | **~$98.00** |

---

## Removed from Previous Design (WS2812B → WS2815 Migration)

| Removed Item | Reason |
|-------------|--------|
| XL4016 8A buck modules ×4 | WS2815 is 12V native — no strip step-down needed |
| Mean Well LRS-350-12 ×1 (shared PSU) | Replaced by 2× independent LRS-150-12 |
| 25A blade fuses | Replaced by 10A (strip current is 6–7.5A, not 18A) |
| 470µF/10V capacitors | Replaced by 470µF/25V (12V rail needs higher voltage rating) |
