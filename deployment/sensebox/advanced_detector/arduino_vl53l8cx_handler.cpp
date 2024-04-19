
#include "vl53l8cx_handler.h"

#include <Arduino.h>
#include <Wire.h>
#include <vl53l8cx_class.h>

#define DEV_I2C Wire
#define LPN_PIN 4
#define I2C_RST_PIN -1
#define PWREN_PIN 2
VL53L8CX sensor_VL53L8CX_top(&DEV_I2C, LPN_PIN, I2C_RST_PIN);

#include <Adafruit_GFX.h>
#include <Adafruit_NeoMatrix.h>
#include <Adafruit_NeoPixel.h>

#define PIN 2

Adafruit_NeoMatrix RGBMatrix = Adafruit_NeoMatrix(12, 8, PIN,
  NEO_MATRIX_TOP     + NEO_MATRIX_LEFT +
  NEO_MATRIX_ROWS + NEO_MATRIX_ZIGZAG,
  NEO_GRB            + NEO_KHZ800);

void measure(void);
String dataStr = "";

VL53L8CX_DetectionThresholds thresholds[VL53L8CX_NB_THRESHOLDS];
const int res = VL53L8CX_RESOLUTION_8X8;

bool EnableAmbient = false;
bool EnableSignal = false;
char report[256];
volatile int interruptCount = 0;

uint8_t number_of_zones = res;
int8_t i, j, k, l;
uint8_t zones_per_line = (number_of_zones == 16) ? 4 : 8;

#include "constants.h"

// A buffer holding the last 200 sets of 3-channel values
const int RING_BUFFER_SIZE = 1920;
float save_data[RING_BUFFER_SIZE] = {0.0};
// Most recent position in the save_data buffer
int begin_index = 0;
// True if there is not yet enough data to run inference
bool pending_initial_data = true;
// How often we should save a measurement during downsampling
int sample_every_n;
// The number of measurements since we last saved one
int sample_skip_counter = 1;


void setLedColorHSV(int h, double s, double v, int x, int y) {
  //this is the algorithm to convert from RGB to HSV
  double r=0; 
  double g=0; 
  double b=0;

  double hf=h/60.0;

  int i=(int)floor(h/60.0);
  double f = h/60.0 - i;
  double pv = v * (1 - s);
  double qv = v * (1 - s*f);
  double tv = v * (1 - s * (1 - f));

  switch (i)
  {
  case 0: //rojo dominante
    r = v;
    g = tv;
    b = pv;
    break;
  case 1: //verde
    r = qv;
    g = v;
    b = pv;
    break;
  case 2: 
    r = pv;
    g = v;
    b = tv;
    break;
  case 3: //azul
    r = pv;
    g = qv;
    b = v;
    break;
  case 4:
    r = tv;
    g = pv;
    b = v;
    break;
  case 5: //rojo
    r = v;
    g = pv;
    b = qv;
    break;
  }

  //set each component to a integer value between 0 and 255
  int red=constrain((int)255*r,0,255);
  int green=constrain((int)255*g,0,255);
  int blue=constrain((int)255*b,0,255);

  RGBMatrix.drawPixel(x+2,y, RGBMatrix.Color(red, green, blue));
}


void print_result(VL53L8CX_ResultsData *Result)
{
  int8_t i, j, k, l;
  uint8_t zones_per_line;
  uint8_t number_of_zones = VL53L8CX_RESOLUTION_8X8;

  zones_per_line = (number_of_zones == 16) ? 4 : 8;
  dataStr = "";

  for (j = 0; j < number_of_zones; j += zones_per_line)
  {
    for (l = 0; l < VL53L8CX_NB_TARGET_PER_ZONE; l++)
    {
      for (k = (zones_per_line - 1); k >= 0; k--)
      {
        if((long)Result->target_status[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l] ==255){
          RGBMatrix.drawPixel((j+1)/8+2, k, RGBMatrix.Color(150, 150, 150));
        } else {
          long distance = (long)Result->distance_mm[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l];
          int maxDist = distance;
          if (maxDist > 1000) {
            maxDist = 0;
          }
          int colVal = map(maxDist,0,2000,10,310);
          setLedColorHSV(colVal,1,1,(j+1)/8, k);
        }
      }
    }
  }

  RGBMatrix.show();
}


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

  RGBMatrix.setBrightness(15);
  RGBMatrix.begin();

  return true;
}


VL53L8CX_ResultsData Results;
uint8_t NewDataReady = 0;
uint8_t status;
int lastReading = 0;
bool ReadVL53L8CX(float* input,
                       int length, bool reset_buffer) {
                        // Clear the buffer if required, e.g. after a successful prediction
  if (reset_buffer) {
    memset(save_data, 0, RING_BUFFER_SIZE * sizeof(float)*64);
    begin_index = 0;
    pending_initial_data = true;
  }
  bool new_data = false;
  // int currentFrame[res];
  status = sensor_VL53L8CX_top.vl53l8cx_check_data_ready(&NewDataReady);
  if ((!status) && (NewDataReady != 0)) {

    status = sensor_VL53L8CX_top.vl53l8cx_get_ranging_data(&Results);
    print_result(&Results);
    for (int8_t j = 0; j < number_of_zones; j += zones_per_line)
    {
      for (int8_t k = (zones_per_line - 1); k >= 0; k--)
      {
        //perform data processing here...
        if((long)(&Results)->target_status[j] !=255){
          if((long)(&Results)->distance_mm[j]>1000.0) {
            save_data[begin_index++] = 0.0;
          } else {
            save_data[begin_index++] = (long)(&Results)->distance_mm[j];
          }
        }
      }
    }

    NewDataReady = 0;
    // If we reached the end of the circle buffer, reset
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
  }
  
  return false;
}
