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

#include <SD.h>
#include <SPI.h>
#include "FS.h"

SPIClass sdspi = SPIClass();

// A buffer holding the last 200 sets of 3-channel values
const int RING_BUFFER_SIZE = 1920;
float save_data[RING_BUFFER_SIZE] = {0.0};
// Most recent position in the save_data buffer
int begin_index = 0;
// True if there is not yet enough data to run inference
bool pending_initial_data = true;

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

  // sdcard
  pinMode(SD_ENABLE,OUTPUT);
  digitalWrite(SD_ENABLE,LOW);
  sdspi.begin(VSPI_SCLK,VSPI_MISO,VSPI_MOSI,VSPI_SS);
  SD.begin(VSPI_SS,sdspi);
  
  File file = SD.open("/Data.txt");
  if(!file){
      Serial.println("Failed to open file for reading");
      return;
  }

  Serial.print("Read from file: ");
  while(file.available()){
    String line = file.readStringUntil('\n');
    bool got_data =
      ReadVL53L8CX(model_input->data.f, input_length, false, line);
    // If there was no new data, wait until next time.
    if (got_data) RecognizeManeuvers();
  }
  file.close();
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
    File file = SD.open("/Output.txt", FILE_APPEND);
    if(!file){
        Serial.println("Failed to open file for writing");
        return;
    }
    file.println(prediction_scores[0]);
    file.close();
    Serial.println(prediction_scores[0]);
}
long currentTime = 0;
void loop() { 

}

bool ReadVL53L8CX(float* input,
                       int length, bool reset_buffer, String line) {
                        // Clear the buffer if required, e.g. after a successful prediction
  if (reset_buffer) {
    memset(save_data, 0, RING_BUFFER_SIZE * sizeof(float)*64);
    begin_index = 0;
    pending_initial_data = true;
  }
    
  // Parse the line and extract integers
  int index = 0;
  char *token = strtok(const_cast<char*>(line.c_str()), ",");
  while (token != NULL && index < 64) {
    save_data[begin_index++] = atoi(token);
    token = strtok(NULL, ",");
  }

  if (begin_index >= (1400)) {
    begin_index = 0;
    // Check if we are ready for prediction or still pending more initial data
    if (pending_initial_data) {
      pending_initial_data = false;
    }
  }

  // Return if we don't have enough data
  if (pending_initial_data) {
    return false;
  }

  // Copy the requested number of bytes to the provided input tensor
  for (int i = 0; i < length; ++i) {
    int ring_array_index = begin_index + i - length;
    if (ring_array_index < 0) {
      ring_array_index += (1400);
    }
    input[i] = save_data[ring_array_index];
    // Serial.print(input[i]);
    // Serial.print(",");
  }
  // Serial.print("\n");
  return true;

  
  return false;
}
