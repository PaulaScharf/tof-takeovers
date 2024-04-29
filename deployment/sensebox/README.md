This folder contains three similar implementations of running the trained model on the senseBox for live detection of takeover manouvres. Live readings from a connected ToF are stored in a ring buffer and then continuously fed into the neural network model.

# mini_detector
Refactored version of the code from advanced detector. This is more readable and only uses arduino files. Just edit the `model_data.ino` file and the means and std_deviations arrays in the `arduino_vl53l8cx_handler.ino` if you have trained a new model.

At the top of the `mini_detector.ino` there is a defined variable "BLUETOOTH". Per default it is set to false, which means that the prediction values will be send out through the serial connection. If it set to true, the prediction values will be send out via bluetooth low energy.

# advanced_detector
This code is more closely based on the [magic wand](https://github.com/petewarden/magic_wand) example code and contains a bit more overhead code and structuiring, that might come in handy sometime.

# mini_detector_sdcard
With this code you can predict on data coming from the sdcard instead of the sensor. The data should be in a file called "Data.txt" on the sdcard. Each row should contain one frame of distance measurements, seperated by commas. The script will save all prediction in a new file on the sdcard called "Output.txt".
