This folder contains two similar implementations of running the trained model on the senseBox for live detection of takeover manouvres. Live readings from a connected ToF are stored in a ring buffer and then continuously fed into the neural network model.

# mini_detector
Refactored version of the code from advanced detector. This is more readable and only uses arduino files. Just edit the `model_data.ino` file if you have trained a new model.

# advanced_detector
This code is more closely based on the [magic wand](https://github.com/petewarden/magic_wand) example code and contains a bit more overhead code and structuiring, that might come in handy sometime.