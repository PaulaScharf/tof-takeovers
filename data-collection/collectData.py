import cv2
import numpy as np
import serial
import time
from datetime import datetime
import csv
import math


# Dieser Code wird für die Datenakquisition genutzt.
# Die Abstandsdaten werden in einer CSV gespeichert und lokal abgespeichert
# Um den Code auszuführen wird der VL53L8CX-Sensor und eine Videokamera benötigt


# Aufbau der seriellen Schnittstelle
serial_recorder = serial.Serial('/dev/ttyACM0', 115200)
serial_predictor = serial.Serial('/dev/ttyACM1', 115200)


# Erstellen des Headers für die CSV-Datei mit 1280 Werten sowie Zeitstempel und Label
headers = []
for i in range(1, 21):  # Für jede der 20 Matrizen
    for j in range(1, 65):  # Für jeden der 64 Werte in der Matrix
        name = f"Matrix{i}_Wert{j}"
        headers.append(name)
headers.append("Timestamp")
headers.append("Label")

# Erstellen der CSV-Datei
with open('test.csv', 'w', newline='') as file:
                           writer = csv.writer(file)
                           writer.writerow(headers)

# Variablendefinition
anzahlMessungen = 0
matritzen = []

def num_to_rgb(val, max_val=3):
    i = (val * 255 / 2000)
    r = round(math.sin(0.024 * i + 0) * 127 + 128)
    g = round(math.sin(0.024 * i + 2) * 127 + 128)
    b = round(math.sin(0.024 * i + 4) * 127 + 128)
    return [r,g,b]

# Funktionzum Auslesen der Sensordaten
def get_sensor_data(timestamp, prediction):
    sensor_data = np.zeros((480, 640, 3), dtype=np.uint8)
    try:

        # Auslesen der Daten
        data = serial_recorder.readline().decode('utf-8').strip()
        if data:
            global anzahlMessungen
            print(anzahlMessungen)
            anzahlMessungen = anzahlMessungen + 1
            if anzahlMessungen > 0: 

                # Verarbeitung der Sensordaten und Speicherung der Abstandsdaten
                value_groups = data.split(";")
                distances = [int(group) if group else 0 for group in value_groups]
                distances = distances[:-1]

                if len(distances) == 64:

                    # Umwandlung der Daten in ein 8*8-Format
                    my_sensor_data = np.array(distances).reshape((8, 8))
                    block_size_x = sensor_data.shape[1] // 8
                    block_size_y = sensor_data.shape[0] // 8
                        
                    for i in range(8):
                        for j in range(8):
                            value = my_sensor_data[i, j]
                            # Störende Werte rausfiltern
                            if value > 2000 or value == 0:
                                value = 0
                                my_sensor_data[i, j] = 0

                            # Farbwertberechnung für die Sensorvisualisuerng
                            color_value = int(value * 255 / 2000)
                            sensor_data[(7-i)*block_size_y:((7-i)+1)*block_size_y, j*block_size_x:(j+1)*block_size_x] = num_to_rgb(value, 2000)
                                
                            # Textvorbereitung für Sensordaten
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            font_scale = 0.5  
                            font_color = (255-color_value, 255-color_value, 255-color_value) 
                            font_thickness = 1 

                            text = f"{value}"

                            # Berechnen der Position, an der der Text eingefügt werden soll
                            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                            text_x = j * block_size_x + (block_size_x - text_size[0]) // 2
                            text_y = (7-i) * block_size_y + (block_size_y + text_size[1]) // 2

                            cv2.putText(sensor_data, text, (text_x, text_y), font, font_scale, font_color, font_thickness)

            
                    matritzen.append(my_sensor_data.flatten())
                    # Überprüfe, ob die Queue 20 Matrizen (Eine Sequenz) enthält
                    if len(matritzen) == 20:
                        # Konvertiere die Queue in eine Zeile für die CSV-Datei
                        row = np.concatenate(matritzen).astype(str).tolist()
                        row.append(timestamp)
                        row.append(prediction) 

                        # Schreiben der Zeile in die CSV-Datei
                        with open('test.csv', 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow(row)

                        # Entferne die älteste Matrix aus der Queue
                        matritzen.pop(0)
                    
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        
    return sensor_data

def get_prediction():
    prediction = -1.0
    try:
        # Auslesen der Daten
        data = serial_predictor.readline().decode('utf-8').strip()
        if data:
             prediction = float(data)
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
    return prediction
# Initialisieren der Kamera

# ggfs. Zahl anpassen, wenn keine Webcam genutzt wird
cap = cv2.VideoCapture(4)

while True:

    now = datetime.now()

    # Timestamp zum labeln
    timestamp = now.strftime("%H:%M:%S") + ".{:03d}".format(int(now.microsecond / 1000))

    # Kamerabild
    ret, camera_frame = cap.read()
    
    # Prediction
    prediction = get_prediction()

    # Sensorbild
    sensor_frame = get_sensor_data(timestamp, prediction)
    
    # Einfügen des Timestamps in das Sensorbild
    cv2.putText(sensor_frame, timestamp, (10, sensor_frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    
    if sensor_frame.shape[0] != camera_frame.shape[0]:
        sensor_frame = cv2.resize(sensor_frame, (sensor_frame.shape[1], camera_frame.shape[0]))
    
    combined_frame = np.hstack((camera_frame, sensor_frame))

    cv2.putText(combined_frame, str(prediction), (combined_frame.shape[1]-40, combined_frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow('Camera and Sensor Data', combined_frame)

    # Abbruch des Programms mit 'q'. Die Daten werden gespeichert
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
