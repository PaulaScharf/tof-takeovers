import pickle
import tensorflow as tf
import numpy as np

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

print("confusion matrix for >60% probability")
confusion = tf.math.confusion_matrix(labels=y_test, predictions=[1 if x > 0.6 else 0 for x in model(X_test)], num_classes=2)
print(confusion)

######################################## TFLITE ###################################
# Load the TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path='./training/models/model_lstm.tflite')
interpreter.allocate_tensors()

# Get input and output tensors
input_tensor_index = interpreter.get_input_details()[0]['index']
output_tensor_index = interpreter.get_output_details()[0]['index']

# Run inference on test data
true_pos = 0
true_neg = 0
false_pos = 0
false_neg = 0
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
        if predicted_label == 1:
            true_pos += 1
        else:
            true_neg += 1
    else:
        if predicted_label == 1:
            false_pos += 1
        else:
            false_neg += 1
    # else:
    #      print("lite model predicted: ", lite_predictions[0])
    #      print("org model predicted:  ", model.predict(np.array( [X_test[i],]),verbose = 0)[0][0])
         

# Compute accuracy
accuracy = (true_pos+true_neg) / total_predictions
precision = (true_pos) / (true_pos + false_pos)
recall = (true_pos) / (true_pos + false_neg)
print("TensorFlow Lite model:")
print(" accuracy:", round(accuracy*100,2))
print(" precision:", round(precision*100,2))
print(" recall:", round(recall*100,2))
