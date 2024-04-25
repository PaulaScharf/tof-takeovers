import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping

data_path = "./training/trainingsdata/traintestval/"

# This data is for training the model
with open(data_path + 'train_data.pkl', 'rb') as file:
    X_train, y_train = pickle.load(file)
# This data is used during training to validate the current status of the model and keep from overfitting on the trainingsdata
with open(data_path + 'val_data.pkl', 'rb') as file:
    X_val, y_val = pickle.load(file)
# This data is used to evaluate the final trained model
with open(data_path + 'test_data.pkl', 'rb') as file:
    X_test, y_test = pickle.load(file)


print("Daten geladen...")

# Modell aufbauen
model = Sequential()
model.add(LSTM(10, return_sequences=False, input_shape=(20, 64), unroll=False, batch_size=1)) # the input of the lstm layer is 20 frames with 64 values each (as the ToF records in 8x8)
model.add(Dense(1, activation='sigmoid')) # Sigmoid-Aktivierung für binäre Klassifikation

tf.keras.utils.plot_model(
    model,
    to_file='training/model_lstm.png',
	show_shapes=True,
)

# Modell kompilieren
print("Starte Training...")
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', 
        tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall'),
        tf.keras.metrics.AUC(name='auc')])

# Define early stopping callback to monitor validation loss
early_stopping = EarlyStopping(monitor='val_loss', patience=7)

# Modell trainieren
history = model.fit(X_train, y_train, epochs=200, batch_size=64, validation_data=(X_val, y_val), callbacks=[early_stopping])

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.savefig('training/models/training_validation_plot.png')


# Modell evaluieren
metrics = model.evaluate(X_test, y_test, return_dict=True)
print(metrics)

# Model speichern
model.save('training/models/model.keras')

# Convert model to tflite
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

save_tflite_model(tflite_model, './training/models', 'model_lstm.tflite')
model.save_weights('./training/models/model_lstm')

# after converting to tflite convert it to tflite for micro with the following:
# xxd -i models/model_lstm.tflite > models/model_lstm.cc
