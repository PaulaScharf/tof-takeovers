import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle


print("Erzeugen der Datensplits...")

labeled_datasets_paths = [
    './training/trainingsdata/labeled/paula/stadtlohnweg_autos_1.csv',
    './training/trainingsdata/labeled/paula/stadtlohnweg_autos_2.csv',
    './training/trainingsdata/labeled/luca/Fahrraeder.csv',
    './training/trainingsdata/labeled/luca/Fahrraeder_reversed.csv',
    './training/trainingsdata/labeled/luca/Fahrraeder_rotated_90.csv',
    './training/trainingsdata/labeled/luca/Fahrraeder_rotated_270.csv',
    './training/trainingsdata/labeled/paula/indoor_turning.csv',
]

# Einladen der Daten
data = []
for path in labeled_datasets_paths:
    temp = pd.read_csv(path)
    temp['Timestamp'] = pd.to_datetime(temp['Timestamp'], format='%H:%M:%S.%f', errors="coerce").fillna(pd.to_datetime(temp['Timestamp'], format='%H:%M:%S', errors="coerce"))
    temp['Timestamp'] = temp['Timestamp'].dt.time
    if len(data) == 0:
        data = temp
    else:
        data = pd.concat([data,temp])

# Optional: Unter-Sampling der überrepräsentierten Klasse
class_0 = data[data['Label'] == 0]
class_1 = data[data['Label'] == 1]

n_class_1 = len(class_1)
class_0_sample = class_0.sample(n_class_1)
data_balanced = pd.concat([class_0_sample, class_1])



# Daten für Features und Labels aufteilen
X = data_balanced.iloc[:, :-2].values
y = data_balanced.iloc[:, -1].values


# TODO: Luca normalised the data in his code. Why?? Do we need to do that?
# scaler = StandardScaler()
# X = scaler.fit_transform(X)

# Daten in das erforderliche Format umwandeln
X = X.reshape((-1, 20, 64))

# Daten in Trainings- und Testsets aufteilen
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)


# speichern der Daten um Zeit zu sparen
with open('./training/trainingsdata/traintestval/train_data.pkl', 'wb') as file:
    pickle.dump((X_train, y_train), file)

with open('./training/trainingsdata/traintestval/test_data.pkl', 'wb') as file:
    pickle.dump((X_test, y_test), file)

with open('./training/trainingsdata/traintestval/val_data.pkl', 'wb') as file:
    pickle.dump((X_val, y_val), file)