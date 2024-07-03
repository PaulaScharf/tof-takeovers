#define BLUETOOTH false
// #include <senseBoxIO.h>
// #include <Arduino.h>
#include <Wire.h>
#include <vl53l8cx.h>

#define DEV_I2C Wire
#define SerialPort Serial

#define LPN_PIN 4
#define I2C_RST_PIN -1
#define PWREN_PIN 2

#define BUTTON_PIN 6

#include "Freenove_WS2812_Lib_for_ESP32.h"
#define LED_PIN 1
Freenove_ESP32_WS2812 led = Freenove_ESP32_WS2812(1, LED_PIN, 0, TYPE_GRB);

void print_result(VL53L8CX_ResultsData *Result);
void clear_screen(void);
void handle_cmd(uint8_t cmd);
void display_commands_banner(void);

long measurements = 0;         // Used to calculate actual output rate
long measurementStartTime = 0;

// Components.
VL53L8CX sensor_vl53l8cx_top(&DEV_I2C, LPN_PIN, I2C_RST_PIN);

bool EnableAmbient = false;
bool EnableSignal = false;
uint8_t res = VL53L8CX_RESOLUTION_4X4;
char report[256];
int start = 0;


#include <Adafruit_GFX.h>
#include <Adafruit_NeoMatrix.h>
#include <Adafruit_NeoPixel.h>
#define PIN 2
Adafruit_NeoMatrix RGBMatrix = Adafruit_NeoMatrix(12, 8, PIN,
  NEO_MATRIX_TOP     + NEO_MATRIX_LEFT +
  NEO_MATRIX_ROWS + NEO_MATRIX_ZIGZAG,
  NEO_GRB            + NEO_KHZ800);


const long intervalInterval = 199;
long time_startInterval = 0;
long time_actualInterval = 0;


#if BLUETOOTH
#include <SenseBoxBLE.h>
const char* BLE_CHARACTERISTICS[] = {
  "B944AF10F4954560968F2F0D18CAB522",
  "7973afc7e447492ca2376a08c594b302",
  "7973afc7e447492ca2376a08c594b303",
  "7973afc7e447492ca2376a08c594b304",
  "7973afc7e447492ca2376a08c594b305",
  "7973afc7e447492ca2376a08c594b306",
  "7973afc7e447492ca2376a08c594b307",
  "7973afc7e447492ca2376a08c594b308",
  "7973afc7e447492ca2376a08c594b309",
  "7973afc7e447492ca2376a08c594b310",
  "7973afc7e447492ca2376a08c594b311",
  "7973afc7e447492ca2376a08c594b312",
  "7973afc7e447492ca2376a08c594b313",
  "7973afc7e447492ca2376a08c594b314",
  "7973afc7e447492ca2376a08c594b315",
  "7973afc7e447492ca2376a08c594b316"
};
const int NUM_CHARACTERISTICS = sizeof(BLE_CHARACTERISTICS) / sizeof(BLE_CHARACTERISTICS[0]);
int distanceCharacteristics[NUM_CHARACTERISTICS];
#else
#include <SD.h>
#include "SPI.h"

File Data;
SPIClass sdspi = SPIClass();
String dataStr = "";
String filename = "Data";

#include "time.h"
const char* ssid       = "PaulasHotspot";
const char* password   = "passwortio";
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;
struct tm timeinfo;
#include <WiFi.h>

#endif

void receiveEvent(int bytes) {
  Serial.print("received: ");
  start = Wire.read();    // read one character from the I2C
  Serial.println(start);
}

void setLedColorHSV(int h, double s, double v, int x, int y) {
  //this is the algorithm to convert from RGB to HSV
  double r=0; 
  double g=0; 
  double b=0;

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

void setLED(uint8_t r,uint8_t g,uint8_t b) {
  led.setLedColorData(0, r, g, b);
  led.show();
}

/* Setup ---------------------------------------------------------------------*/
void setup()
{
  led.begin();
  led.setBrightness(30);  
  setLED(255,0,0);
  // Initialize serial for output.
  Serial.begin(9600);
  // delay(2000);
 // while(!Serial) ;

  uint8_t status;

  Serial.println("Initializing sensor...");

  // Enable PWREN pin if present
  if (PWREN_PIN >= 0) {
    pinMode(PWREN_PIN, OUTPUT);
    digitalWrite(PWREN_PIN, HIGH);
    delay(10);
  }
  
  Serial.println("I2C Initialized");

  DEV_I2C.begin(39,40);
  DEV_I2C.setClock(1000000); //Sensor has max I2C freq of 1MHz

  // Configure VL53L8CX component.
  sensor_vl53l8cx_top.begin();
  Serial.println("Sensor library started");
  sensor_vl53l8cx_top.init();
  Serial.println("Sensor initialized");


  // Hier kann der Ranging Mode gesetzt werden
  // sensor_vl53l8cx_top.vl53l8cx_set_ranging_mode(VL53L8CX_RANGING_MODE_AUTONOMOUS);
  // if (status) {
  //   snprintf(report, sizeof(report), "vl53l5cx_set_ranging_mode failed, status %u\r\n", status);
  //   SerialPort.print(report);
  // }
  sensor_vl53l8cx_top.set_ranging_frequency_hz(30);
   if (status) {
     snprintf(report, sizeof(report), "vl53l8cx_set_ranging_frequency_hz failed, status %u\r\n", status);
     SerialPort.print(report);
   }
  Serial.println("ranging mode and frequency was set");
  delay(3000);

  // Start Measurements
  sensor_vl53l8cx_top.start_ranging();

  toggle_resolution();
  toggle_signal_and_ambient();

  // RGBMatrix
  RGBMatrix.setBrightness(15);
  RGBMatrix.begin();

#if BLUETOOTH
  // setup bluetooth
  SenseBoxBLE::start("senseBox-takeover-detection"); // prefix "senseBox" muss bleiben, dahinter kannst du es auch anders benennen
  SenseBoxBLE::addService("CF06A218F68EE0BEAD048EBC1EB0BC84");
  for (int i = 0; i < NUM_CHARACTERISTICS; i++) {
    SenseBoxBLE::addService(BLE_CHARACTERISTICS[i]);
    distanceCharacteristics[i] = SenseBoxBLE::addCharacteristic(BLE_CHARACTERISTICS[i]);
  }
  Serial.println("bluetooth successfully setup");
#else
  //connect to WiFi
  Serial.printf("Connecting to %s ", ssid);
  WiFi.begin(ssid, password);
  int maxAttempts = 50;
  int currentAttempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
      currentAttempt = currentAttempt + 1;
      if(currentAttempt>maxAttempts) {
        break;
      }
  }
  if(currentAttempt<=maxAttempts) {
    Serial.println(" CONNECTED");
    
    //init and get the time
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    if(!getLocalTime(&timeinfo)){
      Serial.println("Failed to obtain time");
      return;
    }
    setLED(0,255,0);
    delay(500);
  }

  //disconnect WiFi as it's no longer needed
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);

  // Init SD
  pinMode(SD_ENABLE,OUTPUT);
  digitalWrite(SD_ENABLE,LOW);
  sdspi.begin(VSPI_SCLK,VSPI_MISO,VSPI_MOSI,VSPI_SS);
  SD.begin(VSPI_SS,sdspi);
  filename = String(timeinfo.tm_yday,DEC)+String(timeinfo.tm_hour,DEC)+String(timeinfo.tm_min,DEC)+String(timeinfo.tm_sec,DEC);
  Data = SD.open("/" + filename + ".txt", FILE_WRITE);
  Data.close();
#endif
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.println("Success");

  setLED(0,0,0);
}

void loop()
{
  time_startInterval = millis();


  if (time_startInterval > time_actualInterval + intervalInterval) {
    Serial.println(millis()-time_actualInterval);
    time_actualInterval = millis();
    VL53L8CX_ResultsData Results;
    uint8_t NewDataReady = 0;
    uint8_t status;

    do {
      status = sensor_vl53l8cx_top.check_data_ready(&NewDataReady);
    } while (!NewDataReady);

    if ((!status) && (NewDataReady != 0)) {
      status = sensor_vl53l8cx_top.get_ranging_data(&Results);
      print_result(&Results);

      // Uncomment to display actual measurement rate
      // measurements++;
      // float measurementTime = (millis() - measurementStartTime) / 1000.0;
      // Serial.print("rate: ");
      // Serial.print(measurements/measurementTime, 3);
      // Serial.println("Hz");
    }
  } 
  #if BLUETOOTH
    SenseBoxBLE::poll();
  #endif 
}

void print_result(VL53L8CX_ResultsData *Result)
{
  int8_t i, j, k, l;
  uint8_t zones_per_line;
  uint8_t number_of_zones = res;

  zones_per_line = (number_of_zones == 16) ? 4 : 8;

#if BLUETOOTH
  int index = 0;
  int characteristic = 0;
  int begin_index = 0;
  float save_data[64] = {0.0};
#else
  dataStr = "";
#endif

  for (j = 0; j < number_of_zones; j += zones_per_line)
  {
    for (l = 0; l < VL53L8CX_NB_TARGET_PER_ZONE; l++)
    {
      for (k = (zones_per_line - 1); k >= 0; k--)
      {
        //perform data processing here...
        if((long)Result->target_status[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l] ==255){
#if BLUETOOTH
          save_data[begin_index] = 0;
          index = index+1;
          if(index>=4) {
            bool isConnected = SenseBoxBLE::write(distanceCharacteristics[characteristic++], save_data[begin_index], save_data[begin_index-1], save_data[begin_index-2], save_data[begin_index-3]);
            index = 0;
          }
          begin_index = begin_index + 1;
#else
          dataStr += String(0) + ",";
#endif
          RGBMatrix.drawPixel((j+1)/8+2, k, RGBMatrix.Color(150, 150, 150));
        } else {
#if BLUETOOTH
          save_data[begin_index] = (float)Result->distance_mm[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l];
          Serial.print((float)Result->distance_mm[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l]);
          Serial.print(" ");
          Serial.print(save_data[begin_index]);
          Serial.print(" ");
          Serial.println(begin_index);
          index = index+1;
          if(index>=4) {
            bool isConnected = SenseBoxBLE::write(distanceCharacteristics[characteristic++], save_data[begin_index], save_data[begin_index-1], save_data[begin_index-2], save_data[begin_index-3]);
            index = 0;
          }
          begin_index = begin_index + 1;
#else
          dataStr += String((long)Result->distance_mm[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l]) + ",";
#endif
          long distance = (long)Result->distance_mm[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l];
          int maxDist = distance;
          if (maxDist > 1000) {
            maxDist = 0;
          }
          int colVal = map(maxDist,0,2000,10,310);
          setLedColorHSV(colVal,1,1,(j+1)/8, k);
        }
        // dataStr += String((long)Result->target_status[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l]) + ";";
        // dataStr += String((long)Result->signal_per_spad[(VL53L8CX_NB_TARGET_PER_ZONE * (j+k)) + l]) + ";";
        // dataStr += String((long)Result->ambient_per_spad[j+k]) + ", ";
      }
    }
  }

#if not BLUETOOTH
  getLocalTime(&timeinfo);
  dataStr += String(timeinfo.tm_hour,DEC)+":"+String(timeinfo.tm_min,DEC)+":"+String(timeinfo.tm_sec,DEC)+"."+String(millis()-measurementStartTime, 6) + "," + String(1-digitalRead(BUTTON_PIN)) + "\n";
  // Serial.print(dataStr);
  Data = SD.open("/" + filename + ".txt", FILE_APPEND);
  Data.print(dataStr);
  Data.close();
#endif
  RGBMatrix.show();
}

void toggle_resolution(void)
{
  sensor_vl53l8cx_top.stop_ranging();

  switch (res)
  {
    case VL53L8CX_RESOLUTION_4X4:
      res = VL53L8CX_RESOLUTION_8X8;
      break;

    case VL53L8CX_RESOLUTION_8X8:
      res = VL53L8CX_RESOLUTION_4X4;
      break;

    default:
      break;
  }
  sensor_vl53l8cx_top.set_resolution(res);
  sensor_vl53l8cx_top.start_ranging();
}

void toggle_signal_and_ambient(void)
{
  EnableAmbient = (EnableAmbient) ? false : true;
  EnableSignal = (EnableSignal) ? false : true;
}

void clear_screen(void)
{
  snprintf(report, sizeof(report),"%c[2J", 27); /* 27 is ESC command */
  SerialPort.print(report);
}

void display_commands_banner(void)
{
  snprintf(report, sizeof(report),"%c[2H", 27); /* 27 is ESC command */
  SerialPort.print(report);

  Serial.print("53L7A1 Simple Ranging demo application\n");
  Serial.print("--------------------------------------\n\n");

  Serial.print("Use the following keys to control application\n");
  Serial.print(" 'r' : change resolution\n");
  Serial.print(" 's' : enable signal and ambient\n");
  Serial.print(" 'c' : clear screen\n");
  Serial.print("\n");
}

void handle_cmd(uint8_t cmd)
{
  switch (cmd)
  {
    case 'r':
      toggle_resolution();
      clear_screen();
      break;

    case 's':
      toggle_signal_and_ambient();
      clear_screen();
      break;

    case 'c':
      clear_screen();
      break;

    default:
      break;
  }
}