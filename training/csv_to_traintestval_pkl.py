# TODO: refactor this code
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import numpy as np
from datetime import datetime
from joblib import dump
import time
import pickle
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os
from sklearn.utils import resample
from datetime import datetime
from joblib import load
from sklearn.exceptions import DataConversionWarning
from tqdm import tqdm


print("Erzeugen der Datensplits...")


# Einladen der Daten
data = pd.read_csv('./trainingsdaten/unprocessed/Fahrraeder.csv')

data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%H:%M:%S.%f', errors="coerce").fillna(pd.to_datetime(data['Timestamp'], format='%H:%M:%S', errors="coerce"))
data['Timestamp'] = data['Timestamp'].dt.time

# WICHTIG: Hier ist ein Beispiel für das Umkehren von Daten
# Die Daten dafür sind jedoch für Github zu groß
data_b = pd.read_csv('./trainingsdaten/unprocessed/Fahrraeder_reversed.csv')
data_b['Timestamp'] = pd.to_datetime(data_b['Timestamp'], format='%H:%M:%S.%f', errors="coerce").fillna(pd.to_datetime(data_b['Timestamp'], format='%H:%M:%S', errors="coerce"))
data_b['Timestamp'] = data_b['Timestamp'].dt.time  

data_ab = pd.concat([data, data_b])

data_c = pd.read_csv('./trainingsdaten/unprocessed/Fahrraeder_rotated_90.csv')
data_c['Timestamp'] = pd.to_datetime(data_c['Timestamp'], format='%H:%M:%S.%f', errors="coerce").fillna(pd.to_datetime(data_c['Timestamp'], format='%H:%M:%S', errors="coerce"))
data_c['Timestamp'] = data_c['Timestamp'].dt.time

data_abc = pd.concat([data_ab, data_c])

data_d = pd.read_csv('./trainingsdaten/unprocessed/Fahrraeder_rotated_90.csv')
data_d['Timestamp'] = pd.to_datetime(data_d['Timestamp'], format='%H:%M:%S.%f', errors="coerce").fillna(pd.to_datetime(data_d['Timestamp'], format='%H:%M:%S', errors="coerce"))
data_d['Timestamp'] = data_d['Timestamp'].dt.time

data_balancedT2 = pd.concat([data_abc, data_d])

# Optional: Unter-Sampling der überrepräsentierten Klasse
class_0 = data_balancedT2[data_balancedT2['Label'] == 0]
class_1 = data_balancedT2[data_balancedT2['Label'] == 1]

n_class_1 = len(class_1)
class_0_sample = class_0.sample(n_class_1)
data_balanced = data_balancedT2 # pd.concat([class_0_sample, class_1])



# Daten für Features und Labels aufteilen
X = data_balanced.iloc[:, :-2].values
y = data_balanced.iloc[:, -1].values


# Daten normalisieren
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Daten in das erforderliche Format umwandeln
X = X.reshape((-1, 20, 64))

# Daten in Trainings- und Testsets aufteilen
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)


# speichern der Daten um Zeit zu sparen
with open(data_path + 'train_data.pkl', 'wb') as file:
    pickle.dump((X_train, y_train), file)

with open(data_path +'test_data.pkl', 'wb') as file:
    pickle.dump((X_test, y_test), file)

with open(data_path + 'val_data.pkl', 'wb') as file:
    pickle.dump((X_val, y_val), file)