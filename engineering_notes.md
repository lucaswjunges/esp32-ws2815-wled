# Engineering Notes — ESP32 + WS2815 WLED System

## 0. WS2815 vs WS2812B — Key Differences

| Feature | WS2812B | WS2815 |
|---------|---------|--------|
| Supply voltage | 5V | **12V** |
| Buck converter needed | Yes (12V→5V) | **No** |
| Strip current (300 LEDs, full white) | 18A | **~6–7.5A** |
| Backup data line | No | **Yes (BI pin)** |
| Signal voltage threshold | 3.5V | **3.5V (same)** |

The WS2815 runs directly on 12V. The PSU output connects straight to the strip.
Only the ESP32 + level shifter need a separate small 12V→5V buck module.

---

## 1. Level Shifter — Still Required

**Short answer: Yes, still required for WS2815.**

Although WS2815 runs at 12V for power, the data input uses the same ~3.5V threshold:
```
WS2815 DIN Vih_min ≈ 3.5V
ESP32 GPIO output HIGH = 3.3V
Margin: 3.3V − 3.5V = −200mV  → VIOLATION (same as WS2812B)
```

**Recommended: SN74AHCT125N** (same as WS2812B design)
- Accepts 3.3V input (Vih_min = 2.0V)
- Drives output to 5V (from small buck output)
- Cost: ~$0.25 per IC

**Backup data line (WS2815 advantage):**
WS2815 includes a BI (backup input) pin. If the DIN line is broken or a pixel fails,
data propagates through the previous LED's BI output. This means a single failed pixel
does not kill all downstream LEDs — an important reliability improvement over WS2812B.

---

## 2. Wire Gauge Considerations (12V, 7.5A)

| AWG | mΩ/m | External Vdrop (5m, 7.5A, round trip) | Max continuous | Use case |
|-----|------|---------------------------------------|----------------|----------|
| 12  | 5.21 | **0.39V** ✓                          | 20A | **12V strip power** ← recommended |
| 14  | 8.29 | **0.62V** ⚠ marginal                 | 15A | Acceptable with injection at both ends |
| 16  | 13.2 | **0.99V** ✗                          | 13A | Below WS2815 voltage spec |
| 22  | 53.5 | —                                     | 0.9A | Data lines (DIN, BI) |

**Rules:**
- 12V strip power runs: **AWG12** (ensures far-end ≥ 11.61V)
- ESP32 supply (12V→buck→5V): AWG18 or AWG20 (current: ~0.15A)
- Data lines (DIN, BI): AWG22, keep under 50cm from level shifter to strip DIN

---

## 3. Voltage Drop at Strip Far End

WS2815 internal copper trace resistance: ~30 mΩ/m per power conductor.

### Single injection point (start only):
```
External wire drop (AWG12, 5m round trip, 7.5A):    7.5A × 0.052Ω  = 0.39V
Internal trace drop (tapered 7.5A→0, avg 3.75A):    3.75A × 0.03Ω/m × 5m × 2 = 1.13V
─────────────────────────────────────────────────────────────────────────────
Far-end voltage:   12V − 0.39V − 1.13V = 10.48V  ✗  (below 11.5V minimum)
```

→ Single injection is **not sufficient** at full brightness.

### Injection at both ends (start + end):
```
Each end feeds 150 LEDs (2.5m, max 3.75A per feed)

External drop per feed (AWG12, 2.5m round trip):    3.75A × 0.026Ω = 0.10V
Internal trace per half (avg 1.875A, 2.5m):         1.875A × 0.03Ω/m × 2.5m × 2 = 0.28V
─────────────────────────────────────────────────────────────────────────────
Far-end of each half:   12V − 0.10V − 0.28V = 11.62V  ✓
```

**Power injection at both ends (start + end) is mandatory at full brightness.**

**WLED current limiter setting:**
```
WLED → Config → LED Preferences → Maximum Current = 6000 mA
```
This caps strip current at 6A, keeping the typical operating point well within spec.

---

## 4. WLED Firmware Configuration

### Flash WLED via Web (easiest)
1. Connect ESP32 to PC via USB
2. Open: https://install.wled.me
3. Select firmware version (latest stable)
4. Click Install → browser flashes ESP32 directly

### Initial Setup
```
Default AP:       WLED-AP
Default password: wled1234
Default IP:       4.3.2.1 (when connected to AP)
```

### Key Settings (per strip — WS2815 at 12V)
```
LED GPIO:         4
LED Count:        300
LED Type:         WS2815  (select WS2815 in WLED, not WS2812B)
Color Order:      GRB
Max Current:      6000 mA  (conservative; or 7500 mA if PSU/wiring verified)
Brightness Cap:   180 / 255  (70%) for safe continuous operation
```

**Important:** Select **WS2815** (not WS2812B) in WLED LED preferences.
WLED adjusts timing and recognizes the backup data line when WS2815 is selected.

### Two-ESP32 Setup (independent systems, WiFi sync)
Each ESP32 runs an independent WLED instance on the same WiFi network.
Synchronize using WLED's Sync feature:
```
WLED → Config → Sync → Enable Broadcast  (on main unit)
WLED → Config → Sync → Enable Receive    (on follower unit)
Both set to same multicast group (default: 239.0.0.1)
```

---

## 5. Recommended Improvements for Reliability

### Electrical

| Problem | Symptom | Solution |
|---------|---------|----------|
| Far-end LEDs dim or wrong color | Visible brightness gradient along strip | Power injection at both ends (mandatory) |
| Data line noise | Random pixels wrong color | 330Ω resistor + SN74AHCT125N level shifter |
| Buck module (ESP32) hot | Module > 60°C to touch | Add small heatsink; load is light (~0.15A in, 0.25A out) |
| ESP32 resets during WiFi Tx | Device reboots randomly | 100µF cap directly on ESP32 VIN/GND pins |
| Inrush at power-on | Fuse blows on startup | 470µF cap at strip entry; WLED soft-start |
| Single broken pixel kills strip | LEDs dark from break onward | WS2815 BI line — solder backup data wire at strip break point |

### Mechanical

- Use **JST SM connectors** for strip power injection points (waterproof, polarized)
- Use **ferrules** on all stranded wire terminal connections
- Keep data wire (DIN, BI) away from 12V power wires (radiated EMI)
- Strain relief on all wiring at enclosure entry points

### Software / WLED

- Enable **automatic crash recovery** in WLED
- Set **static IP** for each ESP32 (avoids DHCP-dependent WLED discovery)
- Use **OTA updates** (WLED supports over-the-air firmware update via web UI)
- Consider **MQTT integration** for home automation (WLED has native MQTT support)

---

## 6. Safety Checklist (per system)

- [ ] PSU output verified at 12.0V before connecting strip
- [ ] 10A blade fuse installed on 12V feed to strip
- [ ] Wire gauge verified AWG12 for all 12V strip power runs
- [ ] Common ground between PSU, small buck module, ESP32, and strip
- [ ] Power injection wired at strip start AND end
- [ ] WLED LED type set to **WS2815** (not WS2812B)
- [ ] WLED current limit configured (6000 mA recommended)
- [ ] Level shifter (SN74AHCT125N) installed and powered from 5V (buck output)
- [ ] 330Ω resistor on data line between level shifter and strip DIN
- [ ] 470µF/25V capacitor across strip +12V/GND at entry point
- [ ] Small buck output set to 5.0V before connecting ESP32
- [ ] Enclosure or strain relief on all wiring
