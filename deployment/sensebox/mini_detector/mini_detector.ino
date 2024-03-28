#include <TensorFlowLite.h>

#include "tensorflow/lite/micro/kernels/micro_ops.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include <Arduino.h>
#include <Wire.h>
#include <vl53l8cx_class.h>

#define kChannelNumber 64
#define kFrameNumber 20

// Globals, used for compatibility with Arduino-style sketches.
namespace {
const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* model_input = nullptr;
int input_length;

// Create an area of memory to use for input, output, and intermediate arrays.
// The size of this will depend on the model you're using, and may need to be
// determined by experimentation.
constexpr int kTensorArenaSize = 7 * 1024 + 1008 ;
uint8_t tensor_arena[kTensorArenaSize];
}  // namespace

// The name of this function is important for Arduino compatibility.
void setup() {
  Serial.begin(115200);
  delay(2000);

  // Map the model into a usable data structure. This doesn't involve any
  // copying or parsing, it's a very lightweight operation.
  model = tflite::GetModel(get_model_data());
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.printf("Model provided is schema version %d not equal "
                         "to supported version %d.",
                         model->version(), TFLITE_SCHEMA_VERSION);
    return;
  }

  // This imports all operations, which is more intensive, than just importing the ones we need.
  // If we ever run out of storage with a model, we can check here to free some space
  static tflite::AllOpsResolver resolver;

  // Build an interpreter to run the model with.
  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, kTensorArenaSize);
  interpreter = &static_interpreter;

  // Allocate memory from the tensor_arena for the model's tensors.
  interpreter->AllocateTensors();

  // Obtain pointer to the model's input tensor.
  model_input = interpreter->input(0);
  if ((model_input->dims->size != 3) || (model_input->dims->data[0] != 1) ||
      (model_input->dims->data[1] != kFrameNumber) ||
      (model_input->dims->data[2] != kChannelNumber) || 
      (model_input->type != kTfLiteFloat32)) {
    Serial.println(model_input->dims->size);
    Serial.println(model_input->dims->data[0]);
    Serial.println(model_input->dims->data[1]);
    Serial.println(model_input->dims->data[2]);
    Serial.println(model_input->type);
    Serial.println("Bad input tensor parameters in model");
    return;
  }

  input_length = model_input->bytes / sizeof(float);
  Serial.printf("input_length: %i \n", input_length);

  bool setup_status = SetupVL53L8CX();
  if (!setup_status) {
    Serial.println("Setting up sensor failed\n");
  }
}

// This is the regular function we run to recognize Maneuvers from a pretrained
// model.
void RecognizeManeuvers() {
    // Run inference, and report any error.
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        Serial.printf("Invoke failed");
        return;
    }
    const float* prediction_scores = interpreter->output(0)->data.f;
    Serial.println(prediction_scores[0]);
}

void loop() { 
  // Attempt to read new data from the VL53L8CX.
  bool got_data =
      ReadVL53L8CX(model_input->data.f, input_length, false);
  // If there was no new data, wait until next time.
  if (!got_data) return;

  RecognizeManeuvers();

}
