# Wiring Diagram — ESP32 + WS2815 WLED System

## Overview

Two fully independent systems at separate locations. No shared components.
WS2815 strips connect directly to 12V — no step-down buck for strip power.
Only the ESP32 + level shifter require a small 12V→5V buck module.

---

## System 1 — Full Diagram (System 2 is identical at a different location)

```
┌───────────────────────────────────────────────────────────────────────────┐
│           MEAN WELL LRS-150-12  (12V DC, 12.5A, 150W)  — System 1        │
│                  L   N   PE   +V   -V                                     │
│                               │     │                                     │
│        ┌──────────────────────┘     └──── GND BUS ─────────────────────┐ │
│        │                                                                │ │
│        │  +12V                                                          │ │
│        │                                                                │ │
│        ├──[F1: 10A blade]────────────────────────────────────────────┐ │ │
│        │                                                              │ │ │
│        │     ┌────────────────────┐                                  │ │ │
│        ├─────┤ MP1584EN Buck      │                                  │ │ │
│        │     │  12V → 5V, 3A      ├── +5V ──┬─── ESP32 VIN          │ │ │
│        │     │  (adjust to 5.0V)  │         ├─── SN74AHCT125N VCC   │ │ │
│        │     └────────────────────┘         │                        │ │ │
│        │  GND ──────────────────────────────┼─── ESP32 GND          │ │ │
│        │                                    └─── SN74AHCT125N GND   │ │ │
│        │                                                              │ │ │
│        │              ESP32 GPIO4 ──[330Ω]──→ SN74AHCT125N pin A    │ │ │
│        │                                       SN74AHCT125N pin Y ──┐│ │ │
│        │                                                             ││ │ │
│        │  +12V ─[AWG12]──── C_IN (470µF/25V) ────── Strip +12V ────┘│ │ │
│        │                                        DIN ← (signal above)  │ │ │
│        │  GND  ─[AWG12]───────────────────────── Strip GND           │ │ │
│        │                                                              │ │ │
│        │         ┌─────────────────────────────────────────────┐     │ │ │
│        │         │  WS2815 Strip  (300 LEDs / 5m / 12V)        │     │ │ │
│        │         │                                              │     │ │ │
│        │   +12V ─┤[LED 0]                         [LED 299]─── ┼─+12V┘ │ │
│        │    GND ─┤ ●─●─●─●─●─●─●─...─●─●─●─●─●─●─●─●─●─●─●  ┼─GND──┘ │
│        │    DIN ─┤                                      DOUT   │         │
│        │         └─────────────────────────────────────────────┘         │
│        │                  ↑                          ↑                    │
│        │           Inject at start              Inject at end             │
│        │           (AWG12)                      (AWG12, recommended)      │
│        └────────────────────────────────────────────────────────────────  │
└──────────────────────────────────────────────────────────────────────────  ┘
```

System 2 is identical — installed at a different location with its own LRS-150-12.

---

## Signal Path Detail (Data Line)

```
ESP32 GPIO4  (3.3V logic HIGH)
     │
   [330Ω]  ← series resistor (ringing/reflection suppression)
     │
  SN74AHCT125N pin A  (Vih_min = 2.0V → accepts 3.3V ✓)
  SN74AHCT125N VCC  = 5V (from small buck output)
     │
  SN74AHCT125N pin Y  (output = 5V logic HIGH)
     │
  WS2815 Strip DIN  (Vih_min ≈ 3.5V → satisfied ✓)
```

**Note:** The WS2815 has a backup data line (BI line). If DIN is cut or broken,
data passes through the previous LED's BI output. This is a WS2815 reliability feature
not present in WS2812B.

---

## Power Injection Diagram (per strip)

```
PSU +12V
     │
     ├──── Strip START (+12V, GND) ← AWG12, injection point A
     │
     │     Strip[0]──[1]──...──[149]──[150]──...──[299]
     │
     └──── Strip END (+12V, GND) ← AWG12, injection point B (recommended)
```

With injection at both ends:
- Each end feeds half the strip (150 LEDs)
- Max current per feed: ~3.75A
- Far-end voltage per half: 12V − 0.20V (external) − 0.14V (internal) = 11.66V ✓

---

## Pin Assignment — ESP32

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO4 | LED Data Out | → 330Ω → SN74AHCT125N → Strip DIN |
| GPIO2 | Status LED (built-in) | WLED uses this for AP mode indicator |
| GPIO0 | Boot button | Do not use for LED data |
| VIN (5V) | Power input | From MP1584EN buck output |
| GND | Ground | Common with strip GND |

---

## Small Buck Module Connections (per system — ESP32 supply only)

```
INPUT
  +12V_IN  →  VIN+  (MP1584EN module)
  GND      →  VIN-

OUTPUT (adjust to 5.00V before connecting ESP32)
  VOUT+ ──→ ESP32 VIN  +  SN74AHCT125N VCC
  VOUT- ──→ GND (common)
```

---

## Comparison with Previous WS2812B Design

| Aspect | WS2812B (old) | WS2815 (current) |
|--------|--------------|-----------------|
| Strip supply | 5V (via XL4016 buck) | **12V direct from PSU** |
| Buck converter for strip | 2× XL4016 8A in parallel | **None** |
| Buck for ESP32 | Shared with strip | **Small MP1584EN (12V→5V)** |
| Strip peak current | 18A @ 5V | **7.5A @ 12V** |
| Fuse rating | 25A | **10A** |
| PSU | 1× LRS-350-12 (shared) | **2× LRS-150-12 (independent)** |
| Backup data line | No | **Yes (WS2815 BI pin)** |
