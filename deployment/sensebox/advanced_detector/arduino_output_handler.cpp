/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#include "output_handler.h"

#include "Arduino.h"

// #include "Freenove_WS2812_Lib_for_ESP32.h"
// #define LED_PIN 1
// Freenove_ESP32_WS2812 led = Freenove_ESP32_WS2812(1, LED_PIN, 0, TYPE_GRB);
// void setLED(uint8_t r,uint8_t g,uint8_t b) {
//   led.setLedColorData(0, r, g, b);
//   led.show();
// }

void HandleOutput(int kind) {
  // The first time this method runs, set up our LED
  static bool is_initialized = false;
  if (!is_initialized) {
    // led.begin();
    // led.setBrightness(15);  
    // setLED(60,0,0);
    is_initialized = true;
  }

  // Print some ASCII art for each maneuver and control the LED.
  if (kind == 0) {
    Serial.println("step");
    // TF_LITE_REPORT_ERROR(
    //     error_reporter,
    //     "step");
  } else if (kind == 1) {
    Serial.println("step");
    // setLED(0,60,0);
    // TF_LITE_REPORT_ERROR(
    //     error_reporter,
    //     "not a step");
  }
}
