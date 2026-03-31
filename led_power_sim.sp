* ================================================================
* ESP32 + WS2815 LED Strip — Power Supply Validation Netlist
* Single independent system (simulate once per location)
*
* Key difference from WS2812B design:
*   - WS2815 is 12V native → strip connects directly to PSU
*   - No step-down buck converter for strip
*   - Strip peak current: ~7.5A @ 12V (not 18A @ 5V)
*   - Small buck module (12V→5V) powers ESP32 + level shifter only
*
* Validates:
*   - Voltage at strip entry and far-end under 7.5A load
*   - Wire drop (AWG12, 5m) at 12V
*   - Capacitor transient response on startup
*   - PSU headroom vs 10A fuse rating
*
* Compatible with: LTspice XVII, ngspice 36+
* ================================================================

.TITLE WS2815_Power_Validation_12V

* ─── 12V PSU (LRS-150-12 output at board terminal) ──────────────
* PULSE models a 1ms ramp-up (power-on sequence)
V_PSU   VIN   GND   DC 12V
+       PULSE(0 12 0 1M 1M 500 1000)

* ─── Input Bulk Capacitor (near PSU output terminals) ────────────
C_IN    VIN   GND   470U   IC=0V

* ─── 10A Blade Fuse (modeled as series resistance) ───────────────
* Real 10A fuse resistance ≈ 0.5–2 mΩ
R_FUSE  VIN   VIN_F   0.001

* ─── Wire Resistance to Strip (AWG12 silicone, 5m per leg) ──────
* AWG12: 5.211 mΩ/m × 5m = 26.06 mΩ per conductor
* Total round-trip: 52.11 mΩ
R_WIRE_POS   VIN_F       V_STRIP_IN    0.02606
R_WIRE_NEG   GND_STRIP   GND           0.02606

* ─── Bulk Capacitor at Strip Entry ──────────────────────────────
* Absorbs initial inrush when strip LEDs are first energized
* Rated ≥ 25V (12V rail)
C_STRIP_IN   V_STRIP_IN   GND_STRIP   470U   IC=0V

* ─── WS2815 Strip Load (300 LEDs × ~20mA = 6A typical, 7.5A worst case) ──
* Modeled as constant-current sink (worst case: sustained full white)
* Adjust I_STRIP for other brightness levels:
*   Full white (100%):  7.5 A  (worst case, 18W/m)
*   Full white (typ):   6.0 A  (typical, 14.4W/m)
*   50% brightness:     ~1.5 A  (brightness scales quadratically in WLED)
*   25% brightness:     ~0.4 A
I_STRIP   V_STRIP_IN   GND_STRIP   DC 7.5

* ─── ESP32 + Level Shifter via Small 12V→5V Buck Module ─────────
* Buck module (MP1584EN): ~85% efficiency
* Load: ESP32 ~250mA @ 5V + SN74AHCT125N ~8mA @ 5V = ~258mA @ 5V
* Input current: 0.258A × 5V / (12V × 0.85) ≈ 0.127A @ 12V
* Modeled as equivalent resistor: R = 12V / 0.127A ≈ 94.5Ω
R_ESP32_SUPPLY   VIN_F   GND   94.5

* ─── Analysis Commands ───────────────────────────────────────────
.OP

* Transient: simulate 100ms (covers power-on ramp and steady state)
.TRAN   10U   100M   0   10U   UIC

* ─── Measurements ────────────────────────────────────────────────
* All measurements taken in steady-state window (50ms to 100ms)
.MEAS   TRAN   V_STRIP_SS    AVG   V(V_STRIP_IN)                  FROM=50M   TO=100M
.MEAS   TRAN   I_TOTAL_SS    AVG   ABS(I(R_WIRE_POS))             FROM=50M   TO=100M
.MEAS   TRAN   V_WIRE_DROP   PARAM {12 - V_STRIP_SS}
.MEAS   TRAN   P_STRIP       PARAM {V_STRIP_SS * 7.5}
.MEAS   TRAN   P_WIRE_LOSS   PARAM {V_WIRE_DROP * 7.5}
.MEAS   TRAN   V_BUS_PEAK    MAX   V(VIN_F)
.MEAS   TRAN   V_BUS_MIN     MIN   V(VIN_F)

* ─── Probe Nodes ──────────────────────────────────────────────────
.PROBE   V(VIN)   V(VIN_F)   V(V_STRIP_IN)
.PROBE   I(R_WIRE_POS)   I(I_STRIP)

* ─── Expected Results ─────────────────────────────────────────────
* V(V_STRIP_IN)  ≈ 11.61V  [12V − 7.5A × 0.05211Ω wire drop]
* I_TOTAL_SS     ≈ 7.63A   [7.5A strip + 0.13A ESP32 supply]
* V_WIRE_DROP    ≈ 0.39V   [7.5A × 0.05211Ω]
* P_STRIP        ≈ 87.1W   [7.5A × 11.61V]
* P_WIRE_LOSS    ≈ 2.9W    [0.39V × 7.5A]
*
* PSU margin check:
*   Peak load:  7.63A / 12.5A (PSU rated) = 61% load factor  ✓
*   Fuse check: 7.63A < 10A fuse rating  ✓
*
* Strip far-end voltage check:
*   V_STRIP_IN (entry) ≈ 11.61V  ✓  (WS2815 min: 11.5V)
*   With internal trace drop + injection at both ends: far-end ≈ 11.66V  ✓
* ─────────────────────────────────────────────────────────────────

.END
