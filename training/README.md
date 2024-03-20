## Preprocessing the data
Use the `label_csv.py` to label the csv files according to given timestamps (given by Luca). Then use `csv_to_traintestval_pkl.py` to randomly split the data from the csv files into training, testing and validation sets and store these sets as pkl for future easy access.

---

## Training the model
Use either `train_lstm.py` or `train_cnn.py` to train a model with the pkl files from the previous step.

The lstm model is structured as follows:

![lstm model](model_lstm.png)

The cnn model is a WIP.

---

## Testing the model
Use `test_tflite.py` to test the performance of a trained model and its corresponding tflite version.