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

#include "maneuver_predictor.h"

#include "constants.h"

// Return the result of the last prediction
// 0: step, 1: no step
int PredictManeuver(const float* prediction_scores) {
  int max_prediction_index = -1;
  float max_prediction_score = 0.0f;
  for (int i = 0; i < kManeuverCount; i++) {
    const float prediction_score = prediction_scores[i];
    //Serial.println(prediction_score);
    if ((max_prediction_index == -1) ||
        (prediction_score > max_prediction_score)) {
      max_prediction_score = prediction_score;
      max_prediction_index = i;
    }
  }

  int found_maneuver;
  if ((max_prediction_index == kNoStep) ||
      (max_prediction_score < kDetectionThreshold)) {
    found_maneuver = kNoStep;
  } else {
    found_maneuver = max_prediction_index;
  }

  return found_maneuver;
}
