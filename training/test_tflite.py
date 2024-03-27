import pickle
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

data_path = "./training/trainingsdata/traintestval/"

# This data is used to evaluate the final trained model
with open(data_path + 'test_data.pkl', 'rb') as file:
    X_test, y_test = pickle.load(file)

######################################## ORG MODEL ###################################
# Modell aufbauen
model = tf.keras.models.load_model('./training/models/model.keras')
# Weights laden
model.load_weights('./training/models/model_lstm')
# Compute accuracy
metrics = model.evaluate(X_test, y_test, return_dict=True)
print(metrics)

######################################## TFLITE ###################################
# Load the TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path='./training/models/model_lstm.tflite')
interpreter.allocate_tensors()

# Get input and output tensors
input_tensor_index = interpreter.get_input_details()[0]['index']
output_tensor_index = interpreter.get_output_details()[0]['index']

# Run inference on test data
correct_predictions = 0
total_predictions = len(X_test)

for i in range(total_predictions):
    input_data = np.expand_dims(X_test[i], axis=0).astype(np.float32)
    interpreter.set_tensor(input_tensor_index, input_data)
    interpreter.invoke()
    lite_predictions = interpreter.get_tensor(output_tensor_index)[0]
    
    # Compare predicted label with true label
    predicted_label = round(lite_predictions[0],0)
    true_label = y_test[i]
    
    if predicted_label == true_label:
        correct_predictions += 1
    # else:
    #      print("lite model predicted: ", lite_predictions[0])
    #      print("org model predicted:  ", model.predict(np.array( [X_test[i],]),verbose = 0)[0][0])
         

# Compute accuracy
accuracy = correct_predictions / total_predictions
print("TensorFlow Lite model accuracy:", accuracy)
