import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
import pickle
import numpy as np
import csv

# The boolean at the end indicates, if the "no takeover"-class should be undersampled or not
# If it is not undersampled, instances of "no takeover" from other files will be removed to make space
labeled_datasets_paths = [
    ['./training/trainingsdata/labeled/paula/autos_1.csv',True],
    ['./training/trainingsdata/labeled/paula/autos_2.csv',True],
    ['./training/trainingsdata/labeled/paula/autos_3.csv',True],
    ['./training/trainingsdata/labeled/paula/autos_4.csv',True],
    ['./training/trainingsdata/labeled/paula/autos_5.csv',True],
    ['./training/trainingsdata/labeled/paula/autos_6.csv',True],
    ['./training/trainingsdata/labeled/paula/autos_7.csv',True],
    ['./training/trainingsdata/labeled/luca/Fahrraeder.csv',True],
    ['./training/trainingsdata/labeled/luca/Fahrraeder_reversed.csv',False],
    ['./training/trainingsdata/labeled/luca/Fahrraeder_rotated_90.csv',False],
    ['./training/trainingsdata/labeled/luca/Fahrraeder_rotated_270.csv',False],
    ['./training/trainingsdata/labeled/paula/indoor_turning.csv',False],
]

# loading data and optionally undersampling
data = []
for [path, undersample] in labeled_datasets_paths:
    temp = pd.read_csv(path)
    temp['Timestamp'] = pd.to_datetime(temp['Timestamp'], format='%H:%M:%S.%f', errors="coerce").fillna(pd.to_datetime(temp['Timestamp'], format='%H:%M:%S', errors="coerce"))
    temp['Timestamp'] = temp['Timestamp'].dt.time
    temp['Path'] = path

    if undersample:
        class_0 = temp[temp['Label'] == 0]
        class_1 = temp[temp['Label'] == 1]
        n_class_1 = len(class_1)
        print(path, "" + str(n_class_1) + " " + str(len(class_0)) + " " + str(round((len(class_1)/len(class_0))*100,2)))
        class_0_sample = class_0.sample(n_class_1*2)
        temp = pd.concat([class_0_sample, class_1])
    else:
        class_0_data = data[data['Label'] == 0]
        class_1_data = data[data['Label'] == 1]
        class_0_temp = temp[temp['Label'] == 0]
        class_1_temp = temp[temp['Label'] == 1]
        n_class_1 = (len(class_0_data)+len(class_1_temp))-len(class_0_temp)
        print(path, "" + str(n_class_1) + " " + str(len(class_1_data)) + " " + str(round((len(class_1_temp)/len(class_0_temp))*100,2)))
        if n_class_1 >= 0:
            class_0_data_sample = class_0_data.sample(round(n_class_1))
            data = pd.concat([class_0_data_sample, class_1_data])
        else:
            data = class_1_data
            class_0_temp_sample = class_0_temp.sample(len(class_0_temp)+n_class_1)
            temp = pd.concat([class_0_temp_sample, class_1_temp])

    if len(data) == 0:
        data = temp
    else:
        data = pd.concat([data,temp])

# split  into features (X) and labels (y)
X = data.iloc[:, :-3].values
y = data.iloc[:, -2:-1].values


# Because we know, that all measured values are constrained below 2000 mm, we can normalize the data by dividing everything by 2000
X = X/2000.0

# reshape data into 20 frames of 64 pixels each
X = X.reshape((-1, 20, 64))

# split into train, test and validation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# print the composition of the data splits
paths = data["Path"]
Paths_train, Paths_test, y_train_2, y_test_2 = train_test_split(paths, y, test_size=0.2, random_state=42)
Paths_train, Paths_val, y_train_2, y_val_2 = train_test_split(Paths_train, y_train_2, test_size=0.2, random_state=42)
print("-----------------------------------------------------------------------")
for [path, undersample] in labeled_datasets_paths:
    train_len = len(Paths_train[Paths_train == path])
    test_len = len(Paths_test[Paths_test == path])
    val_len = len(Paths_val[Paths_val == path])
    print(path, str(train_len+test_len+val_len) + " = " + str(train_len) + " + " + str(test_len) + " + " + str(val_len))

# save data locally
with open('./training/trainingsdata/traintestval/train_data.pkl', 'wb') as file:
    pickle.dump((X_train, y_train), file)

with open('./training/trainingsdata/traintestval/test_data.pkl', 'wb') as file:
    pickle.dump((X_test, y_test), file)

with open('./training/trainingsdata/traintestval/val_data.pkl', 'wb') as file:
    pickle.dump((X_val, y_val), file)