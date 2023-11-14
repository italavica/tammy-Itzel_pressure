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


async def handler(websocket, path):
    x = 0
    y = 0

    Edne_byte = ['45', '6e', '64', '65']
    temp = []

    global temp_len
    i = 0
    x = 0
    temp_len = 212
    data_set = read_data('signal1.txt')
    data_set_2 = read_data('signal2.txt')
    data_append = []
    data_points =[]
    data_x = []
    data_y1 = []
    data_y2 = []
    peak1 = []
    peak2 = []
    window_size = 15

    

    a = await websocket.recv()

    if a == 'start':
            # sent
        while True:
            # buffer = uart.read(1)
            buffer = data_set[i]
            buffer_2 = data_set_2[i]
            
            data_element = buffer
            data_element_2 = buffer_2

            # x_point = x[i]  # Get new data point in real-time
            y1_point = data_element
            y2_point = data_element_2
        
            # temp.append(data_element)
            # d = {'x': x, 'y1': y1_point, 'y2':y2_point}
            # print(type(y1_point))
            x = x+0.01
            data_x.append(x)
            data_y1.append(y1_point)
            data_y2.append(y2_point)
            # print(type())
            

            if len(data_x) == 100:

                #  moving average
                signal1_series = pd.Series(data_y1)
                smoothed_wave1 = signal1_series.rolling(window=window_size,min_periods=1).mean()
                smoothed_wave1 = smoothed_wave1.values
                signal2_series = pd.Series(data_y2)
                smoothed_wave2 = signal2_series.rolling(window=window_size,min_periods=1).mean()
                smoothed_wave2 = smoothed_wave2.values
                data_y1 = smoothed_wave1
                data_y2 = smoothed_wave2

                #  Second Derivative
                second_derivative1 = np.gradient(np.gradient(data_y1, data_x), data_x[1] - data_x[0])
                second_derivative2 = np.gradient(np.gradient(data_y2, data_x), data_x[1] - data_x[0])

                sos = signal.butter(2, 5, 'lp', fs=100, output='sos')
                filtered_diffSignal1 = signal.sosfilt(sos, second_derivative1)
                filtered_diffSignal2 = signal.sosfilt(sos, second_derivative2)

                # find peak
                indices_1  = find_peaks(filtered_diffSignal1, distance=100)[0]
                indices_2  = find_peaks(filtered_diffSignal2, distance=100)[0]
                # print(filtered_diffSignal1[indices_1][0])
                # print(len(indices_1), len(indices_2))
                

                for j in range(0,len(data_x)):
                    # if (j%10 == 0) and (j != 0):
                    #     peak1.append(filtered_diffSignal1[indices_1])
                    #     peak2.append(filtered_diffSignal2[indices_2])
                    # else:   
                    #     peak1.append(np.nan)
                    #     peak2.append(np.nan)

                    # d = {'x': str(data_x[j]), 'y1': str(data_y1 [j]), 'y2':str(data_y2[j]),'dy1':str(filtered_diffSignal1[j]),'dy2':str(filtered_diffSignal2[j])}

                    # print(filtered_diffSignal1[indices_1],filtered_diffSignal2[indices_2])
                    
                    
                    # d = {'x': str(data_x[j]), 'y1': str(data_y1 [j]), 'y2':str(data_y2[j]),'dy1':str(filtered_diffSignal1[j]),'dy2':str(filtered_diffSignal2[j]),'p1':str((filtered_diffSignal1[indices_1][0])),'p2':str(filtered_diffSignal2[indices_2][0]),'time':str(data_x[indices_1[0]]-data_x[indices_2[0]])}
                    # d = {'x': str(data_x[j]), 'y1': str(data_y1 [j]), 'y2':str(data_y2[j]),'dy1':str(filtered_diffSignal1[j]),'dy2':str(filtered_diffSignal2[j])}
                    d = {'x': str(data_x[j]), 'y1': str(data_y1 [j]), 'y2':str(data_y2[j]),'dy1':str(filtered_diffSignal1[j]),'dy2':str(filtered_diffSignal2[j])}
                    data_points.append(d)
                    # print(j)
                    aa = 11
                    if (j%aa == 0) and (j != 0):

                        if (j == 99):
                            d['p1']=str(filtered_diffSignal1[indices_1][0])
                            d['p2']=str(filtered_diffSignal2[indices_2][0])
                            d['px1']=str(data_x[indices_1[0]])
                            d['px2']=str(data_x[indices_2[0]])
                            d['time']=str(data_x[indices_1[0]]-data_x[indices_2[0]])
                            data_points.append(d)
                        json_data = json.dumps(data_points[((j%aa)-1)*aa:((j%aa)*aa)-1])
                        # print(json_data)
                        # print(data_points[((j%aa)-1)*aa:((j%aa)*aa)-1])
                        await websocket.send(json_data)
                        # print(json_data)
                data_x = []
                data_y1 = []
                data_y2 = []

            i = i+1

            if i == len(data_set):
                break

            # data = json.dumps(d)

                
            # self.sendMessage('\n')
            # if len(data_append) == 10:
            #         data = json.dumps(data_append)
                    


            #         await websocket.send(data)
            #         # await asyncio.sleep(1)
            #         # print(data)
            #         data_append = []

            # if i == len(data_set):
            #     break
            # self.sendMessage(data_element)
            
            # if(len(temp) ==temp_len) and (temp[temp_len-4:temp_len] == Edne_byte):
                
            #     Wavelength, Intensity, Configure = data_sperate(temp)
            #     sort_byte_WL = byte_sort(Wavelength)

            #     # ------------ 3. Hexideciamal to Integral 
            #     int32_t_WL = data_hex_to_int32(sort_byte_WL)/10000            

            #     int32_ele = int32_t_WL[9]
            #     print('---------waveleng_centre (nm)',int32_ele)

            #     # ------------ 4. Wavelength Shift Calculation
            #     int32_t_WL_shift = wavelength_shift(int32_ele)

            #     int32_t_WL_shift = round(int32_t_WL_shift,6)
            #     print('---------int32_WL_shift(nm)', int32_t_WL_shift)
                

            #     temp = []
            #     end_time = time.time()
            #     total = round(end_time - start_time, 3)
                

            #     d = {'x':total , 'y': int32_t_WL_shift}
            #     # data = json.dumps(d)

            #     data_append.append(d)

            #     print('---------total seconds', total)
                
            #     # self.sendMessage('\n')
            #     if len(data_append) == 10:
            #         data = json.dumps(data_append)
            #         await websocket.send(data)
            #         # await asyncio.sleep(1)
            #         print(data)
            #         data_append = []
                    

                
            #     # b = await websocket.recv()
            #     # if b == 'stop':
            #     #     print('disconnected')
            #     #     await websocket.close()
            #     # cnt = cnt+1
            #     # break
            # if (len(temp) ==temp_len) and (temp[temp_len-4:temp_len] != Edne_byte):
            #     temp = temp[1:]


        # a = await websocket.recv()
        # print(a)
        # if a == 'stop':
        #     print('disconnected')
        # x = x + 1
        # y = y + 0.1
        # d = {'x':x , 'y': y}
        # data = json.dumps(d)
        

        # await websocket.send(data)
        # await websocket.send('\n')

    # except websocket.recv() == 'stop':
    #     print('disconnected')
    #     await websocket.close()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8001):
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