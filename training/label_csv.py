# TODO: refactor this code
import pandas as pd
from tqdm import tqdm
import numpy as np
import json

to_reverse = False
to_rotate_90 = False
to_rotate_270 = False

with open('training/trainingsdata/unlabeled/paula/timestamps_autos_4.json', 'r') as json_file:
    time_pairs = json.load(json_file)

data = pd.read_csv('./training/trainingsdata/unlabeled/paula/autos_4.csv')

data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%H:%M:%S.%f')
data['Timestamp'] = data['Timestamp'].dt.time

X = data.iloc[:, :-2].values
data = data.astype({'Label': 'int32'})
for index, row in tqdm(data.iterrows(), total=data.shape[0]):
    if to_reverse:
        for j in range(0, len(X[index]), 8): 
            X[index, j:j+8] = X[index, j:j+8][::-1]
    elif to_rotate_90:
        for k in range(0,20):
            original_array = X[index][k*64:(k+1)*64]
            original_matrix = original_array.reshape(8,8)
            rotated_matrix = np.rot90(original_matrix)
            rotated_array = rotated_matrix.flatten()
            X[index][k*64:(k+1)*64] = rotated_array
    elif to_rotate_270:
        for k in range(0,20):
            original_array = X[index][k*64:(k+1)*64]
            original_matrix = original_array.reshape(8,8)
            rotated_matrix = np.rot90(original_matrix,3)
            rotated_array = rotated_matrix.flatten()
            X[index][k*64:(k+1)*64] = rotated_array
    data.at[index, 'Label'] = 0
    for start, end in time_pairs:
        start_datetime = pd.to_datetime(start, format='%H:%M:%S.%f')

        
        start_time = start_datetime.time()
        end_datetime = pd.to_datetime(end, format='%H:%M:%S.%f')
        end_time = end_datetime.time()
    
        # if start_time <= row['Timestamp'] <= end_time:
        #     data.at[index, 'Label'] = 2
        if to_reverse or to_rotate_90 or to_rotate_270:
            if start_time <= row['Timestamp'] <= end_time:
                data.at[index, 'Label'] = 1
        else:
            if start_time <= row['Timestamp'] <= end_time:
                data.at[index, 'Label'] = 1

data.iloc[:, :-2] = X

if to_reverse or to_rotate_90 or to_rotate_270:
    data = data[data['Label'] != 0] 
    data['Label'] = 0

data.to_csv('./training/trainingsdata/labeled/paula/autos_4.csv', encoding='utf-8', index=False)