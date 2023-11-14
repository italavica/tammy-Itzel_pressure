import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyarrow.feather as feather
from tqdm import tqdm
import pingouin as pg
from scipy.signal import medfilt, savgol_filter


FBG=pd.read_csv('FBG_data1.csv')

def R_peak_detect(PPG,fs,plot=True):
    # AC=DC_filter(PPG)
    AC=PPG
    L=len(AC)
    t= np.arange(0, L/fs, 1/fs)
    def slope(x1,x2,y1,y2):
        m=(y2-y1)/(x2-x1)
        return m
    s=15
    r_peak=[]
    s_peak=[]
    RR=[]
    m3=[]
    AvgRR=int(fs/6)
    c=0
    i=0
    w=1
    for x in range(0,len(AC),int(2*fs)):
        window = AC[x:x+int(2*fs)]
        m = np.mean(window)
        for i in range(x,x+int(2*fs)):
            sfreqsle_studied = AC[i:i+s]
            if i<len(AC)-2:
                if AC[i]>abs(m*w):                 
                    s1=slope(i-1,i,AC[i-1],AC[i])
                    s2=slope(i,i+1,AC[i],AC[i+1])

                    if s1>0 and s2<0:
                        r=int(i)
                        if len(r_peak)>=1:
                            if abs(r-r_peak[len(r_peak)-1])<fs/2.166:
                                pass
                            else:
                                r_peak= np.append(r_peak,r)
                                r_peak = r_peak.astype(int)
                                m_prev = m
                        else:
                            r_peak= np.append(r_peak,r)
                            r_peak = r_peak.astype(int)
                            m_prev = m
                        # plt.figure()
                        # plt.plot(t,AC)
                        # plt.plot(t[r_peak],AC[r_peak],'ro')
                        # plt.plot(t[i], abs(m*w),'bo')
                        # plt.title('R_peak detection algorithm w:'+ str(w))
                        # plt.xlabel('Time (s)')
                        # plt.ylabel('freqslitude')
                        # plt.show()
                    if AC[i-1] == AC[i]:
                        if AC[i+1] == AC[i]:
                                r=int(i+1)
                                if len(r_peak)==0:
                                    r_peak= np.append(r_peak,r)
                                    r_peak = r_peak.astype(int)
                                elif r==r_peak[len(r_peak)-1]:
                                    pass
                                elif abs(r-r_peak[len(r_peak)-1])<fs/2.166 and abs(r-r_peak[len(r_peak)-1])>fs*2.166:
                                    pass
                                else:
                                    r_peak= np.append(r_peak,r)
                                    r_peak = r_peak.astype(int)
                        else:
                                # breakpoint()
                                r=int(i)
                                if len(r_peak)==0:
                                    r_peak= np.append(r_peak,r)
                                    r_peak = r_peak.astype(int)
                                elif r==r_peak[len(r_peak)-1]:
                                    pass
                                elif abs(r-r_peak[len(r_peak)-1])<fs/2.166:
                                    pass
                                else:
                                    r_peak= np.append(r_peak,r)
                                    r_peak = r_peak.astype(int)
    RRs=[]
    for i in range(len(r_peak)-1):
        RR=(((abs(r_peak[i]-r_peak[i+1]))/fs)**-1)*60
        RRs.append(RR)
    HRs=RRs

    
    if plot:
        plt.figure(figsize=(19.4, 9.6))
        plt.plot(t,AC)
        plt.plot(t[r_peak],AC[r_peak],'bo')
        plt.title('E')
        plt.xlabel('Time (s)')
        plt.ylabel('amplitude')
        plt.show()
    return np.median(HRs),HRs,r_peak


breakpoint()


def DC_filter(PPG):
    # Apply a median filter
    PPG_filt_1 = medfilt(PPG, kernel_size=3)
    
    # Apply a Savitzky-Golay filter for DC estimation
    DC = savgol_filter(PPG_filt_1, window_length=300, polyorder=2)

    # Calculate AC component
    AC = PPG_filt_1 - DC
    AC = savgol_filter(AC, window_length=10, polyorder=2)
    fbg_filtered = savgol_filter(PPG, window_length=10, polyorder=2)
    return AC,fbg_filtered

AC,fbg_filtered=DC_filter(-FBG['FBG (nm)'])

R_peak_detect(fbg_filtered,20,plot=True)