
#include <Arduino.h>
#include <Wire.h>
#include <vl53l8cx_class.h>

#define DEV_I2C Wire
#define LPN_PIN 4
#define I2C_RST_PIN -1
#define PWREN_PIN 2
VL53L8CX sensor_VL53L8CX_top(&DEV_I2C, LPN_PIN, I2C_RST_PIN);

void measure(void);

VL53L8CX_DetectionThresholds thresholds[VL53L8CX_NB_THRESHOLDS];
const int res = VL53L8CX_RESOLUTION_8X8;

bool EnableAmbient = false;
bool EnableSignal = false;
char report[256];
volatile int interruptCount = 0;

// A buffer holding the last 200 sets of 3-channel values
const int RING_BUFFER_SIZE = 1280;
float save_data[RING_BUFFER_SIZE] = {0.0};
// Most recent position in the save_data buffer
int begin_index = 0;
// True if there is not yet enough data to run inference
bool pending_initial_data = true;
// How often we should save a measurement during downsampling
int sample_every_n;
// The number of measurements since we last saved one
int sample_skip_counter = 1;

bool SetupVL53L8CX() {
  // Enable PWREN pin if present
  if (PWREN_PIN >= 0) {
    pinMode(PWREN_PIN, OUTPUT);
    digitalWrite(PWREN_PIN, HIGH);
    delay(10);
  }

  // Initialize I2C bus.
  DEV_I2C.begin(39,40);
  DEV_I2C.setClock(1000000); //Sensor has max I2C freq of 1MHz

  
  // Configure VL53L8CX component.
  sensor_VL53L8CX_top.begin();
  sensor_VL53L8CX_top.init_sensor();
  sensor_VL53L8CX_top.vl53l8cx_set_ranging_frequency_hz(30);
  sensor_VL53L8CX_top.vl53l8cx_set_resolution(res);

  Serial.println("starting to measure");
  // Start Measurements.
  sensor_VL53L8CX_top.vl53l8cx_start_ranging(); 

  return true;
}

VL53L8CX_ResultsData Results;
uint8_t NewDataReady = 0;
uint8_t status;
int lastReading = 0;
bool ReadVL53L8CX(float* input,
                       int length, bool reset_buffer) {
                        // Clear the buffer if required, e.g. after a successful prediction

  int8_t i, j, k, l;
  uint8_t zones_per_line;
  uint8_t number_of_zones = res;

  zones_per_line = (number_of_zones == 16) ? 4 : 8;
  if (reset_buffer) {
    memset(save_data, 0, RING_BUFFER_SIZE * sizeof(float)*64);
    begin_index = 0;
    pending_initial_data = true;
  }
  status = sensor_VL53L8CX_top.vl53l8cx_check_data_ready(&NewDataReady);
  if ((!status) && (NewDataReady != 0)) {

    status = sensor_VL53L8CX_top.vl53l8cx_get_ranging_data(&Results);
// #if BLUETOOTH
//     int index = 0;
//     int characteristic = 0;
// #endif
    for (j = 0; j < number_of_zones; j += zones_per_line)
    {
      for (l = 0; l < VL53L8CX_NB_TARGET_PER_ZONE; l++)
      {
        for (k = (zones_per_line - 1); k >= 0; k--)
        {
          if((float)(&Results)->target_status[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l] == 255.0 || (float)(&Results)->distance_mm[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l] > 2000.0){
            save_data[begin_index++] = 0.0;
          } else {
            save_data[begin_index++] = (float)(&Results)->distance_mm[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l];
          }
// #if BLUETOOTH
//           index = index+1;
//           if(index>=4) {
//             bool isConnected = SenseBoxBLE::write(distanceCharacteristics[characteristic++], save_data[begin_index], save_data[begin_index-1], save_data[begin_index-2], save_data[begin_index-3]);
//             index = 0;
//           }
// #endif
        }
      }
    }

    NewDataReady = 0;
    // If we reached the end of the circle buffer, reset
    if (begin_index >= (RING_BUFFER_SIZE)) {
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
        ring_array_index += (RING_BUFFER_SIZE);
      }
#if NORMALIZED
      input[i] = save_data[ring_array_index]/2000.0;
#else
      input[i] = save_data[ring_array_index];
#endif
      // input[i] = (save_data[ring_array_index]-means[i])/std_deviations[i];
      // Serial.print(input[i]);
      // Serial.print(",");
    }
    // Serial.print("\n");
    return true;
  }
  
  return false;
}
