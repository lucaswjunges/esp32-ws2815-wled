#!/usr/bin/env python3
"""
ESP32 + WS2815 Power Supply Simulation — Analytical Plot
Generates simulated waveforms for WS2815 @ 12V (direct connection).

Key difference from WS2812B design:
  - WS2815 is 12V native — no step-down buck for strip
  - Strip peak current: ~7.5A @ 12V (not 18A @ 5V)
  - Small buck module powers ESP32 + level shifter only
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")           # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# ── Circuit parameters ────────────────────────────────────────────────────────
V_PSU      = 12.0          # PSU nominal voltage (V)
I_STRIP    = 7.5           # Strip worst-case current, A (300 LEDs × 20mA, 18W/m)
R_FUSE     = 0.001         # Fuse series resistance, Ω
R_WIRE_LEG = 0.02606       # Wire resistance per leg — AWG12, 5m (Ω)
R_WIRE_RT  = 2 * R_WIRE_LEG   # Round-trip wire resistance
R_ESP32    = 94.5          # ESP32 supply equivalent load, Ω (12V/0.127A)

WS2815_VMIN = 11.5         # WS2815 minimum operating voltage (V)

# ── Steady-state analytical results ──────────────────────────────────────────
I_ESP32_IN = V_PSU / R_ESP32                  # ≈ 0.127 A @ 12V (ESP32 via buck)
I_TOTAL    = I_STRIP + I_ESP32_IN             # ≈ 7.627 A total @ 12V
V_VIN_F    = V_PSU - I_TOTAL * R_FUSE        # ≈ 11.992 V (fuse drop negligible)
V_STRIP_SS = V_VIN_F - I_STRIP * R_WIRE_LEG  # ≈ 11.805 V at strip +terminal
V_GNDS_SS  = I_STRIP * R_WIRE_LEG            # ≈ 0.195 V GND return rise
V_DIFF_SS  = V_STRIP_SS - V_GNDS_SS          # ≈ 11.61 V differential (strip sees this)
V_DROP_EXT = V_VIN_F - V_STRIP_SS + V_GNDS_SS  # ≈ 0.39 V external wire drop
P_WIRE     = V_DROP_EXT * I_STRIP
P_STRIP    = V_DIFF_SS * I_STRIP

# ── Synthetic time-domain waveforms ──────────────────────────────────────────
t    = np.linspace(0, 0.1, 10000)   # 0 to 100 ms
t_ms = t * 1e3

tau_v        = 0.0015   # voltage ramp time constant
tau_settle   = 0.003    # current settling time constant
tau_inrush   = 0.0006   # inrush decay constant
inrush_onset = 0.0002   # inrush onset (soft-start ramp)
inrush_amp   = 17.5     # extra inrush current above steady-state

# Voltage waveforms
v_vin_t    = V_PSU    * (1 - np.exp(-t / tau_v))
v_strip_t  = V_STRIP_SS * (1 - np.exp(-t / (tau_v * 1.6)))
v_gnds_t   = V_GNDS_SS  * (1 - np.exp(-t / (tau_v * 1.6)))
v_diff_t   = v_strip_t - v_gnds_t

# Current waveform: settling ramp + startup inrush spike
i_settle = I_STRIP * (1 - np.exp(-t / tau_settle))
i_inrush = (inrush_amp
            * np.exp(-t / tau_inrush)
            * (1 - np.exp(-t / inrush_onset)))
i_wire   = i_settle + i_inrush

# ── Print results ─────────────────────────────────────────────────────────────
print("\n" + "=" * 62)
print("  ESP32 + WS2815 — Power Supply Simulation  (12V Direct)")
print("=" * 62)
print(f"  V(12V_BUS) steady-state             = {V_VIN_F:.4f} V")
print(f"  V(V_STRIP_IN) at strip +terminal    = {V_STRIP_SS:.4f} V")
print(f"  V(GND_STRIP)  return wire rise      = {V_GNDS_SS:.4f} V")
print(f"  Strip differential voltage          = {V_DIFF_SS:.4f} V")
print(f"  Wire current (strip leg)            = {I_STRIP:.3f} A")
print(f"  Total 12V current (strip + ESP32)   = {I_TOTAL:.3f} A")
print(f"  External wire drop (round-trip)     = {V_DROP_EXT:.4f} V")
print(f"  Wire power dissipation              = {P_WIRE:.2f} W")
print(f"  Strip input power                   = {P_STRIP:.2f} W")
print("-" * 62)
if V_DIFF_SS >= WS2815_VMIN:
    print(f"  [PASS] Strip sees {V_DIFF_SS:.2f}V ≥ {WS2815_VMIN}V WS2815 minimum")
    print("  NOTE: Injection at both ends still recommended")
    print("        (internal trace resistance adds further drop)")
else:
    print(f"  [FAIL] Strip sees {V_DIFF_SS:.2f}V — below WS2815 min {WS2815_VMIN}V")
print(f"  PSU load factor: {I_TOTAL:.2f}A / 12.5A = {I_TOTAL/12.5*100:.0f}%  ✓")
print("=" * 62)

# ── Plot ──────────────────────────────────────────────────────────────────────
STYLE = {
    "v_vin":   {"color": "#2196F3", "label": "V(12V_BUS) — PSU output"},
    "v_strip": {"color": "#FF9800", "label": "V(V_STRIP_IN) — At strip entry (re GND)"},
    "v_gnds":  {"color": "#9E9E9E", "label": "V(GND_STRIP) — GND return wire rise"},
    "v_diff":  {"color": "#4CAF50", "label": "V_diff — Differential voltage across strip"},
    "i_wire":  {"color": "#E91E63", "label": "Wire current (A)"},
}

fig = plt.figure(figsize=(14, 9), facecolor="#1a1a2e")
fig.suptitle(
    "ESP32 + WS2815  |  Power Supply Simulation  |  300 LEDs @ 12V, full white (7.5A)",
    color="white", fontsize=13, fontweight="bold", y=0.98
)

gs = gridspec.GridSpec(3, 1, hspace=0.45, figure=fig,
                        top=0.93, bottom=0.07, left=0.08, right=0.97)

def style_ax(ax, title, ylabel, ylim=None):
    ax.set_facecolor("#0f0f23")
    ax.tick_params(colors="white", labelsize=9)
    ax.set_title(title, color="#aaaaff", fontsize=10, pad=4)
    ax.set_ylabel(ylabel, color="white", fontsize=9)
    ax.set_xlabel("Time (ms)", color="white", fontsize=9)
    ax.spines["bottom"].set_color("#444")
    ax.spines["top"].set_color("#444")
    ax.spines["left"].set_color("#444")
    ax.spines["right"].set_color("#444")
    ax.grid(True, color="#333", linestyle="--", linewidth=0.5)
    if ylim:
        ax.set_ylim(ylim)
    ax.legend(fontsize=8, framealpha=0.3, labelcolor="white",
               facecolor="#111", edgecolor="#555")

# ── Plot 1: Node Voltages ─────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0])
ax1.plot(t_ms, v_vin_t,   **STYLE["v_vin"],   linewidth=1.8)
ax1.plot(t_ms, v_strip_t, **STYLE["v_strip"], linewidth=1.8)
ax1.plot(t_ms, v_gnds_t,  **STYLE["v_gnds"],  linewidth=1.2, linestyle="--")

ax1.axhline(WS2815_VMIN, color="#ff4444", linewidth=1.2, linestyle=":",
            label=f"WS2815 V_min = {WS2815_VMIN}V")
ax1.axhline(V_PSU, color="#ffffff", linewidth=0.8, linestyle=":",
            label=f"Target {V_PSU:.0f}V")

ax1.annotate(f"{V_VIN_F:.3f}V", xy=(t_ms[-1], V_VIN_F),
             xytext=(-65, 6), textcoords="offset points",
             color=STYLE["v_vin"]["color"], fontsize=8, fontweight="bold")
ax1.annotate(f"{V_STRIP_SS:.3f}V", xy=(t_ms[-1], V_STRIP_SS),
             xytext=(-65, -14), textcoords="offset points",
             color=STYLE["v_strip"]["color"], fontsize=8, fontweight="bold")

style_ax(ax1,
    "Node Voltages — 12V Bus vs Strip Entry vs GND Return",
    "Voltage (V)", ylim=(-0.5, 13.5))

# ── Plot 2: Differential strip voltage ───────────────────────────────────────
ax2 = fig.add_subplot(gs[1])
ax2.plot(t_ms, v_diff_t, **STYLE["v_diff"], linewidth=1.8)
ax2.axhline(WS2815_VMIN, color="#ff4444", linewidth=1.4, linestyle=":",
            label=f"WS2815 minimum = {WS2815_VMIN}V  ← must be above this")
ax2.fill_between(t_ms, v_diff_t, WS2815_VMIN,
                  where=(v_diff_t < WS2815_VMIN), color="#ff4444", alpha=0.15,
                  label="Under-voltage zone")

ax2.annotate(f"Steady: {V_DIFF_SS:.3f}V", xy=(t_ms[-1] * 0.6, V_DIFF_SS),
             xytext=(0, 10), textcoords="offset points",
             color=STYLE["v_diff"]["color"], fontsize=9, fontweight="bold")

style_ax(ax2,
    "Differential Voltage Seen by LED Strip  (V_STRIP_IN − GND_STRIP)",
    "Voltage (V)", ylim=(9.5, 13.0))

# ── Plot 3: Wire current ──────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2])
ax3.plot(t_ms, i_wire, **STYLE["i_wire"], linewidth=1.8)
ax3.axhline(I_STRIP, color="#ffcc00", linewidth=1.0, linestyle="--",
            label=f"Expected {I_STRIP}A (300 LEDs, full white, worst case)")

ax3.annotate(f"Steady: {I_STRIP:.2f}A", xy=(t_ms[-1] * 0.6, I_STRIP),
             xytext=(0, 10), textcoords="offset points",
             color=STYLE["i_wire"]["color"], fontsize=9, fontweight="bold")

style_ax(ax3,
    "Wire Current — AWG12 Supply Run (12V bus, Ammeter on Positive Leg)",
    "Current (A)")

# ── Info box ─────────────────────────────────────────────────────────────────
verdict_color = "#4CAF50" if V_DIFF_SS >= WS2815_VMIN else "#ff4444"
verdict_text  = (
    f"PASS — Strip entry sees {V_DIFF_SS:.2f}V ≥ {WS2815_VMIN}V  |  "
    f"External wire drop: {V_DROP_EXT:.2f}V (AWG12, 5m, {I_STRIP}A)  |  "
    f"Injection at both ends recommended (internal trace drop)"
    if V_DIFF_SS >= WS2815_VMIN
    else f"FAIL — Strip entry sees {V_DIFF_SS:.2f}V < {WS2815_VMIN}V WS2815 minimum"
)

summary = (
    f"V(12V_BUS)={V_VIN_F:.3f}V   V(STRIP_DIFF)={V_DIFF_SS:.3f}V   "
    f"I={I_STRIP:.1f}A   ΔV_wire={V_DROP_EXT:.3f}V   "
    f"P_wire={P_WIRE:.1f}W   P_strip={P_STRIP:.1f}W"
)

fig.text(0.5, 0.005, summary, ha="center", va="bottom",
         color="#aaaaaa", fontsize=8)
fig.text(0.5, 0.025, verdict_text, ha="center", va="bottom",
         color=verdict_color, fontsize=8.5, fontweight="bold")

# ── Save ─────────────────────────────────────────────────────────────────────
out = Path(__file__).parent / "Figure_1.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"\nFigure saved: {out}")
