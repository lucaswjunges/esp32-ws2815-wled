/*
 * ================================================================
 * ESP32 + WS2812B LED Strip — Animation Test
 * ================================================================
 *
 * Compatible with:
 *   - Wokwi simulator (wokwi.com)
 *   - Real ESP32 hardware with WLED-compatible wiring
 *
 * Library required: Adafruit NeoPixel
 *
 * Wiring:
 *   ESP32 GPIO4 → [330Ω] → SN74AHCT125N A → SN74AHCT125N Y → Strip DIN
 *   ESP32 5V    → Strip VCC
 *   ESP32 GND   → Strip GND  (common ground with buck converter)
 *
 * Configuration:
 *   NUM_LEDS = 30  for Wokwi simulation (browser performance limit)
 *   NUM_LEDS = 300 for real 5m WS2812B strip (60 LEDs/m × 5m)
 *
 * Power warning:
 *   300 LEDs at full white = 18A @ 5V.
 *   NEVER run at full brightness without proper PSU + power injection.
 *   BRIGHTNESS is set to 60/255 (~24%) for safe simulation.
 * ================================================================
 */

#include <Adafruit_NeoPixel.h>

// ─── Configuration ─────────────────────────────────────────────────
#define LED_PIN        4          // GPIO4 → 330Ω → SN74AHCT125N → DIN
#define NUM_LEDS       30         // ← Change to 300 for real hardware
#define BRIGHTNESS     60         // 0–255 (60 = ~24%,  safe for testing)
#define LED_TYPE       (NEO_GRB + NEO_KHZ800)
// ────────────────────────────────────────────────────────────────────

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, LED_TYPE);

// ─── Color Wheel Helper ──────────────────────────────────────────────
// Input: 0–255 position on color wheel
// Output: packed 32-bit RGB value cycling R→G→B
uint32_t colorWheel(byte pos) {
  pos = 255 - pos;
  if (pos < 85)  return strip.Color(255 - pos * 3, 0,             pos * 3);
  if (pos < 170) return strip.Color(0,             (pos - 85) * 3, 255 - (pos - 85) * 3);
  return               strip.Color((pos - 170) * 3, 255 - (pos - 170) * 3, 0);
}

// ─── Animation: Color Wipe ──────────────────────────────────────────
// Fills LEDs one by one with a solid color, then clears them
void colorWipe(uint32_t color, uint16_t wait_ms) {
  for (uint16_t i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, color);
    strip.show();
    delay(wait_ms);
  }
  strip.clear();
  strip.show();
  delay(200);
}

// ─── Animation: Theater Chase ───────────────────────────────────────
// Alternating pixel blink in groups of 3 (classic marquee effect)
void theaterChase(uint32_t color, uint8_t wait_ms, uint8_t cycles) {
  for (uint8_t c = 0; c < cycles; c++) {
    for (uint8_t q = 0; q < 3; q++) {
      strip.clear();
      for (uint16_t i = 0; i < strip.numPixels(); i += 3) {
        strip.setPixelColor(i + q, color);
      }
      strip.show();
      delay(wait_ms);
    }
  }
  strip.clear();
  strip.show();
}

// ─── Animation: Rainbow Cycle ───────────────────────────────────────
// Full color wheel distributed across all LEDs, cycling continuously
void rainbowCycle(uint8_t wait_ms, uint8_t cycles) {
  for (uint16_t j = 0; j < 256 * cycles; j++) {
    for (uint16_t i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, colorWheel(((i * 256 / strip.numPixels()) + j) & 255));
    }
    strip.show();
    delay(wait_ms);
  }
}

// ─── Animation: Rainbow Theater Chase ──────────────────────────────
void theaterChaseRainbow(uint8_t wait_ms) {
  for (uint16_t j = 0; j < 256; j++) {
    for (uint8_t q = 0; q < 3; q++) {
      strip.clear();
      for (uint16_t i = 0; i < strip.numPixels(); i += 3) {
        strip.setPixelColor(i + q, colorWheel((i + j) % 255));
      }
      strip.show();
      delay(wait_ms);
    }
  }
}

// ─── Animation: Breathe ─────────────────────────────────────────────
// Gentle fade in/out with a single color
void breathe(uint32_t color, uint16_t period_ms) {
  uint16_t step_delay = period_ms / (255 * 2);
  strip.fill(color);

  // Fade in
  for (int b = 0; b <= 255; b++) {
    strip.setBrightness(b);
    strip.show();
    delay(step_delay);
  }
  // Fade out
  for (int b = 255; b >= 0; b--) {
    strip.setBrightness(b);
    strip.show();
    delay(step_delay);
  }

  strip.setBrightness(BRIGHTNESS);  // restore configured brightness
  strip.clear();
  strip.show();
  delay(300);
}

// ─── Animation: Scanner (Larson scanner / KITT effect) ──────────────
void scanner(uint32_t color, uint8_t wait_ms, uint8_t cycles) {
  for (uint8_t c = 0; c < cycles; c++) {
    // Forward
    for (int i = 0; i < (int)strip.numPixels(); i++) {
      strip.clear();
      strip.setPixelColor(i, color);
      if (i > 0) strip.setPixelColor(i - 1, strip.Color(
        (color >> 16 & 0xFF) / 4,
        (color >>  8 & 0xFF) / 4,
        (color       & 0xFF) / 4));
      strip.show();
      delay(wait_ms);
    }
    // Backward
    for (int i = strip.numPixels() - 1; i >= 0; i--) {
      strip.clear();
      strip.setPixelColor(i, color);
      if (i < (int)strip.numPixels() - 1) strip.setPixelColor(i + 1, strip.Color(
        (color >> 16 & 0xFF) / 4,
        (color >>  8 & 0xFF) / 4,
        (color       & 0xFF) / 4));
      strip.show();
      delay(wait_ms);
    }
  }
}

// ─── Setup ───────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.println("==============================================");
  Serial.println(" WS2812B Animation Test — ESP32 + WLED HW");
  Serial.println("==============================================");
  Serial.printf(" GPIO Pin  : %d\n", LED_PIN);
  Serial.printf(" LED Count : %d\n", NUM_LEDS);
  Serial.printf(" Brightness: %d / 255 (%.0f%%)\n", BRIGHTNESS, BRIGHTNESS / 255.0 * 100);
  Serial.println("----------------------------------------------");

  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.clear();
  strip.show();

  delay(300);
  Serial.println("Strip initialized. Starting animations...\n");
}

// ─── Main Loop ───────────────────────────────────────────────────────
void loop() {
  Serial.println("[1/7] Color Wipe — Red");
  colorWipe(strip.Color(255, 0, 0), 25);

  Serial.println("[2/7] Color Wipe — Green");
  colorWipe(strip.Color(0, 255, 0), 25);

  Serial.println("[3/7] Color Wipe — Blue");
  colorWipe(strip.Color(0, 0, 255), 25);

  Serial.println("[4/7] Theater Chase — White");
  theaterChase(strip.Color(180, 180, 180), 50, 10);

  Serial.println("[5/7] Rainbow Cycle");
  rainbowCycle(5, 3);

  Serial.println("[6/7] Scanner — Red (KITT)");
  scanner(strip.Color(255, 0, 0), 30, 3);

  Serial.println("[7/7] Breathe — Cyan");
  breathe(strip.Color(0, 200, 200), 2000);

  Serial.println("Loop complete. Repeating...\n");
}
