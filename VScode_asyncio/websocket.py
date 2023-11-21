import asyncio
import websockets
import signal, sys
import serial
from binascii import hexlify
import time
import plotly.graph_objects as go
from scipy import signal
from plotly.subplots import make_subplots
from scipy.signal import find_peaks
from scipy.signal import butter, filtfilt
import json
import numpy as np
import pandas as pd


def read_data(file_name):
    data_list = []

    with open(file_name, "r") as file:
        data_string = file.read()
        data_list = data_list = data_string.split()

   # print(data_list)
    return data_list

def data_sperate(data_set):
    i = 0
    n = 0

    cnt_w = 0
    cnt_i = 0
    cnt_c = 0

    Wavelength = []
    Intensity = []
    Configure = []

    # print (len(data_set))
    if len(data_set) == temp_len:
        for i in range(int(temp_len/4)):
            # Wavelength
            if( i < 50) and (n %2 == 0):
                Wavelength[4*cnt_w:4*cnt_w+4] =  data_set[4*n:4*n+4]
                cnt_w = cnt_w+1
            # Intensity
            elif (i < 50) and (n %2 != 0):
                Intensity[4*cnt_i:4*cnt_i+4] = data_set[4*n:4*n+4]
                cnt_i = cnt_i+1
            # Other data: Offset, tempreture etc.
            elif (i >  49):
                Configure[4*cnt_c:4*cnt_c+4] = data_set[4*n:4*n+4]
                cnt_c = cnt_c+1
            n = n+1
    
    return Wavelength, Intensity, Configure

def byte_sort(data_set):
    temp = []
    temp_sort = []
    sort_byte = []
    

    for i in range(int(len(data_set)/4)):

        # Sorting hexacdecimal to Middle-Little Endian
        # 1. for example read ['43', '3B', '7B', '00']
        temp = data_set[4*i:4*i+4]
        
        # 2. sort ['43', '3B', '7B', '00'] to ['3B', '43', '00', '7B']
        temp_sort.append(temp [1])
        temp_sort.append(temp [0])
        temp_sort.append(temp [3])
        temp_sort.append(temp [2])

        # 3. sort ['3B', '43', '00', '7B'] to ['00', '7B', '3B', '43']
        temp[2:4] = temp_sort[4*i:4*i+2]
        temp[0:2] = temp_sort[4*i+2:4*i+4]

        sort_byte.append(temp)


    return sort_byte

def data_hex_to_int32(data_set):
    int32_t = []
    for i in range(len(data_set)):
        hex_list = data_set [i]
        combined_hex = ''.join(hex_list)
        result = int(combined_hex, 16)

        int32_t.append(result)
    int32_t = np.array(int32_t)
    return int32_t

def wavelength_shift(data_set):
    # FBG_peak = 834.946 835.047
    FBG_peak = 834.946 # the center peak using 3MB baudrate
    WL_shift = data_set - FBG_peak
    return WL_shift

def moving_average(json_data):
    parsed_data = json.loads(json_data)
    x =  parsed_data[0]
    y1 = parsed_data[1]['y1']
    y2 = parsed_data[2]

    print(y1)
    # smoothing
    window_size = 10
    signal1_series = pd.Series(y1)
    smoothed_wave1 = signal1_series.rolling(window=window_size,min_periods=1).mean()
    smoothed_wave1 = smoothed_wave1.values

    print()

    window_size = 10
    signal2_series = pd.Series(y2)
    smoothed_wave2 = signal2_series.rolling(window=window_size,min_periods=1).mean()
    smoothed_wave2 = smoothed_wave2.values

    return x,smoothed_wave1,smoothed_wave2

async def server_logic(websocket, path):
    data_generation_task = None
    data_points = []
    collect_data = False  # Flag to start/stop collecting data
    collected_data = []  # Store collected data
    async def start_data_generation():
        nonlocal data_generation_task, collect_data, collected_data
        max_collect_points = 1000  # Number of points to collect

        i = 0
        time_step = 0
        x = 0
        y = 0

        Edne_byte = ['45', '6e', '64', '65']
        temp = []

        global temp_len
        i = 0
        x = 0
        temp_len = 212
        data_set_x = read_data('time.txt')
        data_set = read_data('shifted_fbg2_data.txt')
        data_set_2 = read_data('FBG2_part.txt')
        data_append = []
        data_points =[]
        data_x = []
        data_y1 = []
        data_y2 = []
        peak1 = []
        peak2 = []
        window_size = 15


        while True:
            # buffer = uart.read(1)
            buffer = data_set[i]
            buffer_2 = data_set_2[i]
            buffer_x = data_set_x[i]
            
            i = i + 1

            data_element_x = buffer_x
            data_element = buffer
            data_element_2 = buffer_2

            # x_point = x[i]  # Get new data point in real-time
            y1_point = data_element
            y2_point = data_element_2
            x = x+0.01
            

            d = {'x':x , 'y1': y1_point,'y2':y2_point}

            data_append.append(d)
            # print(d)
                # self.sendMessage('\n')
            if len(data_append) == 10:
                    # data = json.dumps(data_append)
                    data = json.dumps({'type': 'regular', 'data': data_append})
                    
                    await websocket.send(data)
                    
                    
                    await asyncio.sleep(0.1)
                    # print(data)
                    data_append = []
                        
            if collect_data:
                
                data_x.append(x)
                data_y1.append(y1_point)
                data_y2.append(y2_point)

                if len(data_x) >= max_collect_points:


                    
                    

                    window_size = 10
                    signal1_series = pd.Series(data_y1)
                    smoothed_wave1 = signal1_series.rolling(window=window_size,min_periods=1).mean()
                    smoothed_wave1 = smoothed_wave1.values

                    signal1_series = pd.Series(data_y2)
                    smoothed_wave2 = signal1_series.rolling(window=window_size,min_periods=1).mean()
                    smoothed_wave2 = smoothed_wave2.values

                    for j in range(0,len(data_x)):
                        dd = {'x': str(data_x[j]), 'dy1':str(smoothed_wave1[j]),'dy2':str(smoothed_wave2[j])}
                        collected_data.append(dd)
                    data_x = []
                    data_y1 = []
                    data_y2 = []

                    collected_data_json = json.dumps({'type': 'collected', 'data': collected_data})
                    await websocket.send(collected_data_json)  
                    
                    print(collected_data)
                    print(len(collected_data))
                    collect_data = False  # Reset flag
                    collected_data = []  # Reset collected data
        
            if i == len(data_set):
                i = 0


    async for message in websocket:
        if message == "start":
            print(message)
            if not data_generation_task or data_generation_task.done():
                data_generation_task = asyncio.create_task(start_data_generation())
        if message == "collect":
            print(message)
            collect_data = True
            collected_data = []  # Reset collected data when starting new collection
        elif message == "stop":
            print(message)
            # if data_generation_task and not data_generation_task.done():
            #     data_generation_task.cancel()
            #     await data_generation_task
        elif message == "disconnect":
            print(message)
            break


async def main():
    async with websockets.serve(server_logic, '0.0.0.0', 8001):
        await asyncio.Future()  

if __name__ == '__main__':

    # uart=serial.Serial()
    # uart.baudrate=3000000
    # uart.port='/dev/ttyUSB0'
    # uart.open()
    # # 1. Setting Parameters
    # uart.write(b'iz,10000>')
    # print('iz,10000>')
    # uart.write(b'Pv,1>')
    # print('Pv,1>')
    # uart.write(b'PNg,0.5>')
    # print('PNg,0.5>')


    # # 2. Give command for recieving data

    # global start_time
    # start_time = time.time()
    # uart.write(b'P>') # Peak shift
    # print('P>')
    # uart.write(b'DauSe,1>')
    # print('DauSe,1>') 
    asyncio.run(main())