## Preprocessing the data
Use the `label_csv.py` to label the csv files according to given timestamps (given by Luca). Then use `csv_to_traintestval_pkl.py` to randomly split the data from the csv files into training, testing and validation sets and store these sets as pkl for future easy access.

The resulting pkl files are normalized to aid the training of the model. The normalization is done by dividing each value by 2000. This also has to be done with the live data during deployment.

---

## Training the model
Use either `train_lstm.py` or `train_cnn.py` to train a model with the pkl files from the previous step. To turn the resulting trained tflite model into an array of bytes for running it on a microcontroller use the following command:

`xxd -i models/model_lstm.tflite > models/model_lstm.cc` or `xxd -i models/model_cnn.tflite > models/model_cnn.cc`

The lstm model is structured as follows:

![lstm model](model_lstm.png)

The cnn model is a WIP.

---

## Testing the model
Use `test_tflite.py` to test the performance of a trained model and its corresponding tflite version.
