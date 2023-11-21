import numpy as np

# # Create a sample signal
# sample_rate = 1000  # Sampling rate in Hz
# duration = 1  # Duration of the signal in seconds
# frequency = 5  # Frequency of the signal in Hz

# # Generate a sinusoidal signal with the specified frequency
# t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # Time vector
# signal = np.sin(2 * np.pi * frequency * t)  # Sinusoidal signal

x = np.load('x.npy',allow_pickle=True)
data1 = np.load('FBG1.npy',allow_pickle=True)
data1 = data1[1::]
data2 = np.load('FBG2.npy',allow_pickle=True)
data2 = data2[1::]

# Sample data
sample_rate = 100
x = x[145*100:155*100]  # X-axis values
signal1 = data1[145*100:155*100] # Random data for signal 1 (left y-axis)
signal2 = data2[145*100:155*100]  # Random data for signal 2 (right y-axis, scaled for better visualization)
# Perform FFT
fft_result = np.fft.fft(signal2)
frequencies = np.fft.fftfreq(len(fft_result), 1 / sample_rate)  # Frequency values corresponding to FFT result

# Plot the original signal and its FFT result
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

# Plot the original signal
plt.subplot(2, 1, 1)
plt.plot(x, signal2)
plt.title("Original Signal")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

# Plot the FFT result
plt.subplot(2, 1, 2)
plt.plot(frequencies, np.abs(fft_result))
plt.title("FFT Result")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")

plt.tight_layout()
plt.show()


