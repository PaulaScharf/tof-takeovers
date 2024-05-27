import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Reshape, Conv2D, GlobalAveragePooling2D
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np

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

# TODO: should I transpose or not?? The resulting accuracies are similar, although transposing it makes more sense in my head. transposing means that I would have to rewrite it on the mc. 
# X_train = np.transpose(X_train,(0,2,1))
# X_val = np.transpose(X_val,(0,2,1))
# X_test = np.transpose(X_test,(0,2,1))

model = Sequential()
model.add(Reshape((20,8,8), input_shape=(20,64)))
model.add(Conv2D(10,(3,3), activation='relu'))
# model.add(Reshape((-1,4)))
# model.add(LSTM(16, unroll=False, batch_size=1)) # the input of the lstm layer is 20 frames with 64 values each (as the ToF records in 8x8)
model.add(Conv2D(5,(3,3), activation='relu'))
model.add(GlobalAveragePooling2D())
model.add(Dense(1, activation='sigmoid')) # Sigmoid-Aktivierung für binäre Klassifikation
model.summary()

tf.keras.utils.plot_model(
    model,
    to_file='training/model_cnn.png',
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

# X_train = X_train.reshape(X_train.shape[0],X_train.shape[1],8,8)
# Modell trainieren
history = model.fit(X_train, y_train, epochs=200, batch_size=64, validation_data=(X_val, y_val), callbacks=[early_stopping])

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.savefig('training/models/cnn/loss_accuracy_plot.png')
plt.clf()
plt.plot(history.history['precision'], label='Training precision')
plt.plot(history.history['val_precision'], label='Validation precision')
plt.plot(history.history['recall'], label='Training recall')
plt.plot(history.history['val_recall'], label='Validation recall')
plt.xlabel('Epoch')
plt.legend()
plt.savefig('training/models/cnn/precision_recall_plot.png')


# Modell evaluieren
metrics = model.evaluate(X_test, y_test, return_dict=True)
print(metrics)

# Model speichern
model.save('training/models/cnn/model.keras')

# Convert model to tflite
def convert_tflite_model(model):
	import tensorflow as tf
	converter = tf.lite.TFLiteConverter.from_keras_model(model)
	converter.optimizations = [tf.lite.Optimize.DEFAULT]
	converter.experimental_new_converter=True
	converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS,
	tf.lite.OpsSet.SELECT_TF_OPS]
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

save_tflite_model(tflite_model, './training/models/cnn', 'model_lstm.tflite')
model.save_weights('./training/models/cnn/model_lstm')

# after converting to tflite convert it to tflite for micro with the following:
# xxd -i models/cnn/model_lstm.tflite > models/cnn/model_lstm.cc
