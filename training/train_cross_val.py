import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Reshape, Conv2D, MaxPooling2D, GlobalAveragePooling2D
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import numpy as np

# If this is true create a CNN. If its false create an LSTM
cnn = True
if cnn:
	path_name = "cnn_6_3"
else:
	path_name = "lstm_10"

kfold = KFold(n_splits=10, shuffle=True)

data_path = "./training/trainingsdata/traintestval/"

# This data is for training the model
with open(data_path + 'all_data.pkl', 'rb') as file:
    X, y = pickle.load(file)

print("start cross validated training ...")

def create_model():
	model = Sequential()
	if cnn:
		############################ build CNN model ##############################
		model.add(Reshape((20,8,8), input_shape=(20,64)))
		# model.add(Conv2D(12,(3,3), activation='relu'))
		# model.add(Reshape((-1,4)))
		# model.add(LSTM(16, unroll=False, batch_size=1)) # the input of the lstm layer is 20 frames with 64 values each (as the ToF records in 8x8)
		# model.add(MaxPooling2D((2, 2)))
		model.add(Conv2D(6,(3,3), activation='relu'))
		model.add(Conv2D(3,(3,3), activation='relu'))
		model.add(GlobalAveragePooling2D())
		model.add(Dense(1, activation='sigmoid')) # Sigmoid-Aktivierung für binäre Klassifikation
	else:
		############################ build LSTM model ############################
		model.add(LSTM(10, return_sequences=False, input_shape=(20,64), unroll=False, batch_size=1)) # the input of the lstm layer is 20 frames with 64 values each (as the ToF records in 8x8)
		# model.add(Reshape((-1,16)))
		# model.add(LSTM(16, return_sequences=False, unroll=False))
		model.add(Dense(1, activation='sigmoid')) # Sigmoid-Aktivierung für binäre Klassifikation

	tf.keras.utils.plot_model(
		model,
		to_file='training/models/'+path_name+'/model.png',
		show_shapes=True,
	)

	# Modell kompilieren
	model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', 
			tf.keras.metrics.Precision(name='precision'),
			tf.keras.metrics.Recall(name='recall'),
			tf.keras.metrics.AUC(name='auc')])
	
	return model

# Convert model to tflite
def convert_tflite_model(model):
	converter = tf.lite.TFLiteConverter.from_keras_model(model)
	tflite_model = converter.convert()
	return tflite_model

def save_tflite_model(tflite_model, save_dir, model_name):
	import os
	if not os.path.exists(save_dir):
		os.makedirs(save_dir)
	save_path = os.path.join(save_dir, model_name)
	with open(save_path, "wb") as f:
		f.write(tflite_model)
	print("Tflite model saved to %s", save_dir)

def test_tflite(tflite_model):
	interpreter = tf.lite.Interpreter(model_content=tflite_model)
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
	print("TensorFlow Lite model:")
	accuracy = (true_pos+true_neg) / total_predictions
	if (true_pos + false_pos) > 0:
		precision = (true_pos) / (true_pos + false_pos)
	else:
		precision = 0.0
	if (true_pos + false_neg) > 0:
		recall = (true_pos) / (true_pos + false_neg)
	else:
		recall = 0.0
	return accuracy,precision,recall

# K-fold Cross Validation model evaluation
fold_no = 1
results = []
for train, test in tqdm(kfold.split(X, y), total = 10):
	X_train, y_train, X_test, y_test = X[train], y[train], X[test], y[test]
	X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

	model = create_model()
	
	# Define early stopping callback to monitor validation loss
	early_stopping = EarlyStopping(monitor='val_loss', patience=7)

	# train model
	history = model.fit(X_train, y_train, epochs=200, batch_size=64, validation_data=(X_val, y_val), callbacks=[early_stopping], verbose=0)

	metrics = model.evaluate(X_test, y_test, return_dict=True)
	print(metrics)

	tflite_model = convert_tflite_model(model)

	accuracy,precision,recall = test_tflite(tflite_model)
	print('tflite: acc={:f}, prec={:f}, reca={:f}'.format(accuracy,precision,recall))

	result = {
		'metrics': metrics,
		'tflite_metrics': {
			'accuracy': accuracy,
			'precision': precision,
			'recall': recall
		}
	}
	results.append(result)

	fold_no = fold_no + 1

accuracies = np.array([d['metrics']['accuracy'] for d in results])
precisions = np.array([d['metrics']['precision'] for d in results])
recalls = np.array([d['metrics']['recall'] for d in results])
aucs = np.array([d['metrics']['auc'] for d in results])
losses = np.array([d['metrics']['loss'] for d in results])
tflite_accuracies = np.array([d['tflite_metrics']['accuracy'] for d in results])
tflite_precisions = np.array([d['tflite_metrics']['precision'] for d in results])
tflite_recalls = np.array([d['tflite_metrics']['recall'] for d in results])

# print final metrics and tflite metrics
with open('./training/models/'+path_name+'/test_results.txt', 'w') as f:
	f.write('Average scores for tensorflow model:\n')
	f.write(f'> Accuracy: {np.mean(accuracies)} (+- {np.std(accuracies)})\n')
	f.write(f'> Precision: {np.mean(precisions)} (+- {np.std(precisions)})\n')
	f.write(f'> Recall: {np.mean(recalls)} (+- {np.std(recalls)})\n')
	f.write(f'> AUC: {np.mean(aucs)} (+- {np.std(aucs)})\n')
	f.write(f'> Loss: {np.mean(losses)} (+- {np.std(losses)})\n')
	f.write('Average scores for tflite:\n')
	f.write(f'> Accuracy: {np.mean(tflite_accuracies)} (+- {np.std(tflite_accuracies)})\n')
	f.write(f'> Precision: {np.mean(tflite_precisions)} (+- {np.std(tflite_precisions)})\n')
	f.write(f'> Recall: {np.mean(tflite_recalls)} (+- {np.std(tflite_recalls)})\n')


X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=42)
model = create_model()
# Define early stopping callback to monitor validation loss
early_stopping = EarlyStopping(monitor='val_loss', patience=7)
# train model
history = model.fit(X_train, y_train, epochs=200, batch_size=64, validation_data=(X_val, y_val), callbacks=[early_stopping], verbose=0)
model.summary()

# Model speichern
model.save('training/models/'+path_name+'/model.keras')

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.savefig('training/models/'+path_name+'/loss_accuracy_plot.png')
plt.clf()
plt.plot(history.history['precision'], label='Training precision')
plt.plot(history.history['val_precision'], label='Validation precision')
plt.plot(history.history['recall'], label='Training recall')
plt.plot(history.history['val_recall'], label='Validation recall')
plt.xlabel('Epoch')
plt.legend()
plt.savefig('training/models/'+path_name+'/precision_recall_plot.png')
     
tflite_model = convert_tflite_model(model)

save_tflite_model(tflite_model, './training/models/'+path_name, 'model.tflite')
model.save_weights('./training/models/'+path_name+'/model')

# after converting to tflite convert it to tflite for micro with the following:
# xxd -i models/model.tflite > models/model.cc
