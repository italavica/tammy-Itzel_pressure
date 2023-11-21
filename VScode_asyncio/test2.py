import json
import numpy as np
import pandas as pd

#Sample data (replace with your actual data)
x = np.load('x.npy',allow_pickle=True)
data1 = np.load('FBG1.npy',allow_pickle=True)
data1 = data1[1::]
data2 = np.load('FBG2.npy',allow_pickle=True)
data2 = data2[1::]

# Sample data
x = x[145*100:155*100]  # X-axis values
signal1 = data1[145*100:155*100] # Random data for signal 1 (left y-axis)
signal2 = data2[145*100:155*100]  # Random data for signal 2 (right y-axis, scaled for better visualization)

# Example: Calculate the moving average (replace this with your calculation logic)
window_size = 15
data_points =[]
data_y1 =[]
saved_data = []

i = 0

while True:

    x_point = x[i]  # Get new data point in real-time
    y1_point = signal1[i]
    y2_point = signal2[i]
    d = {'x': x_point, 'y1': y1_point, 'y2': y2_point}

    # print(d['y1'])
    data_points.append(d)

    
    i = i+1
    
    # # Maintain the window size
    if len(data_points) > window_size:

        for j in range(0,len(data_points)):
            data_y1.append(float(data_points[j]['y1']))
        # print(data_y1)

        signal1_series = pd.Series(data_y1)
        smoothed_wave1 = signal1_series.rolling(window=window_size,min_periods=1).mean()
        smoothed_wave1 = smoothed_wave1.values

        for j in range(0,len(data_points)):
            print(data_points[j]['y1'])
            data_points[j]['y1'] = data_y1[j]
        
        print(data_y1)

        json_data = json.dumps(data_points)
        # print(len(data_y1))

        # print(len(data_points))
        data_points = []
        data_y1 = []

        

    if i == len(signal1):
        break