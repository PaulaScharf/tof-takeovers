# Data Collection

## Option A: record data via serial connection

**Hardware setup:**
- one senseBox on a bicycle carrier recording and streaming data either with the `vl53l8cx_konfiguration` arduino script (used by Luca) or the `data_collection_serial_monitor` arduino script (used by Paula)
- one webcam on the bicycle carrier which is oriented to have a similar view as the VL53L8CX of the senseBox (the views of the sensor and the camera dont have to be perfectly aligned. The webcam is only used for labeling)
- Optional: one senseBox on a bicycle carrier predicting live on data from its VL53L8CX sensor and streaming the predictions to console (using e.g. the `deplyoment/sensebox/mini_detector` script). A seperate senseBox is used for prediction because streaming live data and predicting at the same time decreases the framerate
- one notebook in a backpack of the cyclist connected to the webcam and senseBox(es). This notebook runs the `collectData.py` script and screen records the output of the script. The screen recording is used for labeling the csv file produced by the `collectData.py` script

**Warning:** It often happened to me that I lost connection to one of the senseBoxes or the webcam (either cause of an unplugged cable or an overflow of the serial monitor). Be sure to check the notebook regularly to see if its still recording properly.

### /collectData.py

This script is currently configured to receive data over serial connection from two senseBoxes: One senseBox for streaming the live sensordata and one senseBox for streaming live predictions of sensor data. If you are not interested in the live predictions you need to adjust the code.

This script outputs a csv file "test.csv" with the live sensordata and predictions. Be aware that if you rerun the script the old "test.csv" file will be overwritten.

### /vl53l8cx_konfiguration

This script was originally used by Luca for recording his data.

### /data_collection_serial_monitor

This script is an adjustment of the `vl53l8cx_konfiguration` script. Unlike the original script it records data in a fixed intervall of 65ms (as this is the framerate that the `mini_detector`currently achieves). It also allows to connect an RGB-LED-Matrix to view the current sensor recording.


## Option B: record data on sdcards

**Hardware setup:**
- one senseBox on a bicycle carrier powered by a battery and recording data on a sdcard with the script `data_collection_sdcard`. A wifi network (e.g. through a portable hotspot) is required to give the senseBox the current time and date, to record that for each datapoint. Configure name and password of the wifi network in the `data_collection_sdcard` script.
- a camera (e.g. a gopro) recording a similar view as the VL53L8CX of the senseBox on a sdcard along with the current date and time

This setup has not been tested yet, but would in theory be more comfortable for data recording

## Visualizing the recorded data and prediction in the Processing IDE

Use the script `visualize_recordings.pde` to visualise a recorded csv file. The script shows all 20 recorded frames at once. The newest frame will be on the bottom right and the oldest on the top left.
