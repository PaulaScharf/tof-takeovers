import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


data_path = "./trainingsdaten/fahrrader_and_fahrraeder_reversed/"

# Öffnen der geseicherten Trainings-/Test-/Valdaten
with open(data_path + 'train_data.pkl', 'rb') as file:
    X_train, y_train = pickle.load(file)

with open(data_path + 'test_data.pkl', 'rb') as file:
    X_test, y_test = pickle.load(file)

with open(data_path + 'val_data.pkl', 'rb') as file:
    X_val, y_val = pickle.load(file)


print("Daten geladen...")

# Modell aufbauen
model = Sequential()
model.add(LSTM(10, return_sequences=False, input_shape=(20, 64), unroll=False, batch_size=1))  
model.add(Dense(1, activation='sigmoid'))  # Sigmoid-Aktivierung für binäre Klassifikation

tf.keras.utils.plot_model(
    model,
    to_file='model_lstm.png',
	show_shapes=True,
)

# Modell kompilieren
print("Starte Training...")
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', 
        tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall'),
        tf.keras.metrics.AUC(name='auc')])

# Modell trainieren
model.fit(X_train, y_train, epochs=50, batch_size=64, validation_data=(X_test, y_test))

# Modell evaluieren
metrics = model.evaluate(X_val, y_val, return_dict=True)
print(metrics)

# Model speichern
model.save('model.keras')

def convert_tflite_model(model):
	import tensorflow as tf
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
     
tflite_model = convert_tflite_model(model)

save_tflite_model(tflite_model, 'model', 'model_lstm.tflite')
model.save_weights('./model/model_lstm')
# after converting to tflite convert it to tflite for micro with the following:
# xxd -i model_lstm.tflite > model_lstm.cc
