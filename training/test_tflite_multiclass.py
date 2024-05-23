import pickle
import tensorflow as tf
import numpy as np
from keras.utils import to_categorical
from sklearn.metrics import precision_score, recall_score, accuracy_score, confusion_matrix

data_path = "./training/trainingsdata/traintestval/multiclass/"

# This data is used to evaluate the final trained model
with open(data_path + 'test_data.pkl', 'rb') as file:
    X_test, y_test = pickle.load(file)
y_test = to_categorical(y_test, num_classes=3)

######################################## ORG MODEL ###################################
# Modell aufbauen
model = tf.keras.models.load_model('./training/models/multiclass/model.keras')
# Weights laden
model.load_weights('./training/models/multiclass/model_lstm')
# Compute accuracy
metrics = model.evaluate(X_test, y_test, return_dict=True)
print(metrics)

y_pred = model(X_test)
y_pred = np.argmax(y_pred, axis=1)
y_test = np.argmax(y_test, axis=1)
predictions_tensor = tf.convert_to_tensor(y_pred)
true_labels_tensor = tf.convert_to_tensor(y_test)
confusion_matrix = tf.math.confusion_matrix(true_labels_tensor, predictions_tensor, num_classes=3)
print("confusion matrix")
print(confusion_matrix)

######################################## TFLITE ###################################
# Load the TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path='./training/models/multiclass/model_lstm.tflite')
interpreter.allocate_tensors()

# Get input and output tensors
input_tensor_index = interpreter.get_input_details()[0]['index']
output_tensor_index = interpreter.get_output_details()[0]['index']

# Run inference on test data
total_predictions = len(X_test)
lite_predictions = []

for i in range(total_predictions):
    input_data = np.expand_dims(X_test[i], axis=0).astype(np.float32)
    interpreter.set_tensor(input_tensor_index, input_data)
    interpreter.invoke()
    lite_prediction = interpreter.get_tensor(output_tensor_index)[0]
    
    # Compare predicted label with true label
    lite_predictions.append(np.argmax(lite_prediction))
         
precision = precision_score(y_test, lite_predictions, average=None)
recall = recall_score(y_test, lite_predictions, average=None)
accuracy = accuracy_score(y_test, lite_predictions)

# Compute accuracy
print("TensorFlow Lite model:")
print(" accuracy:", round(accuracy*100,2))
print(" precision:", (precision*100).round(2))
print(" recall:", (recall*100).round(2))

predictions_tensor = tf.convert_to_tensor(lite_predictions)
confusion_matrix = tf.math.confusion_matrix(true_labels_tensor, predictions_tensor, num_classes=3)
print(" confusion matrix")
print(confusion_matrix)
