# Power Calculation — ESP32 + WS2815 WLED System

## WS2815 vs WS2812B — Fundamental Difference

| Parameter | WS2812B | WS2815 |
|-----------|---------|--------|
| Operating voltage | 5V | **12V** |
| Current per LED (full white) | 60 mA | **~20 mA** |
| Peak current (300 LEDs) | 18.0 A | **6.0 A** |
| Buck converter for strip | Required | **Not required** |

WS2815 operates natively at 12V. The strip connects directly to the PSU output.
No step-down converter is needed for the LED supply.

---

## Per Strip — WS2815 (5m, 60 LEDs/m)

```
LEDs per strip:          5 m × 60 LEDs/m = 300 LEDs
Supply voltage:          12V DC  (direct from PSU — no buck)
Current per LED:         ~20 mA at full white (worst case)
Strip peak current:      300 × 0.020 A = 6.0 A  (typical)
Strip peak current:      18 W/m × 5 m / 12V  = 7.5 A  (worst case)
Strip peak power:        7.5 A × 12V = 90 W  (worst case)
```

---

## ESP32 Supply (via small 12V → 5V buck module, per system)

```
Buck module:             12V → 5V, 2A rated (e.g. MP1584EN-based)
ESP32 + level shifter:   ~250 mA @ 5V
Buck efficiency:         ~85%
Input current:           0.250 × 5 / (12 × 0.85) ≈ 0.12 A @ 12V
```

---

## Per System (1× strip + 1× ESP32) — Each System is Independent

```
Strip worst-case current:   7.5 A  @ 12V
ESP32 supply current:       0.12 A @ 12V
─────────────────────────────────────────
Total:                      7.62 A @ 12V

Safety margin (30%):        7.62 × 1.30 = 9.9 A
Required fuse:              10A blade
Required PSU:               ≥ 10A @ 12V → 120W minimum → use 150W PSU
```

**Both systems are fully independent — each at a separate location with its own PSU.**
No components are shared between System 1 and System 2.

---

## Summary Table

| Parameter | Value |
|-----------|-------|
| LED strip model | WS2815 (12V native) |
| LEDs per strip | 300 |
| Strip voltage | **12V DC (direct)** |
| Strip peak current — typical | 6.0 A @ 12V |
| Strip peak current — worst case | **7.5 A @ 12V** |
| ESP32 supply input current | 0.12 A @ 12V |
| Per-system total (with 30% margin) | **9.9 A @ 12V** |
| Per-system fuse | **10A blade** |
| PSU per system | **Mean Well LRS-150-12 (12V / 12.5A / 150W)** |
| Number of independent systems | **2 (different locations, no shared components)** |

---

## Voltage Drop at Strip End (AWG12, 5m)

```
AWG12 resistance:         5.211 mΩ/m
5m round-trip:            5.211 × 5 × 2 = 52.11 mΩ
External drop @ 7.5 A:    7.5 A × 0.05211 Ω = 0.39V

Strip far-end (external only):  12.0V − 0.39V = 11.61V  ✓
WS2815 operating range:         11.5V – 12.5V

Note: internal strip trace resistance adds further drop at high brightness.
Power injection at both ends is recommended to stay within 11.5V minimum.
```

### Wire Gauge Comparison (12V bus, 7.5A worst case)

| AWG | R (mΩ/m) | External Vdrop (5m round trip) | Far-end voltage | Safe continuous |
|-----|----------|-------------------------------|-----------------|-----------------|
| 12  | 5.211    | **0.39V** ✓                  | 11.61V ✓        | 20A |
| 14  | 8.286    | **0.62V** ✓                  | 11.38V ⚠ marginal | 15A |
| 16  | 13.17    | **0.99V** ✗                  | 11.01V ✗ below spec | 13A |

**Use AWG12 minimum for 12V strip power runs.**
AWG14 is borderline — only acceptable with injection at both ends to offset internal trace drop.

---

## Power Injection

With injection at both ends (start + end of strip):
```
Max current per half:   3.75 A (each end feeds half the strip)
External drop per half: 3.75 A × 0.05211 Ω = 0.20V
Far-end each half:      12.0V − 0.20V = 11.80V  ✓

Even with internal trace resistance (~30 mΩ/m per conductor):
Internal drop per half:  1.875 A avg × 0.030 Ω/m × 2.5 m = 0.14V
Total far-end:           12.0V − 0.20V − 0.14V = 11.66V  ✓
```
Power injection at both ends is the recommended configuration.
