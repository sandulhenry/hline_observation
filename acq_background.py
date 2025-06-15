import numpy as np
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
from matplotlib.mlab import psd

# --- Define Variables ---
NFFT = 1024
 
# sdr.read_samples(x) pulls an x number of samples
# at 256*1024/2.048e6 = 0.128 seconds per iteration
# for 300 iterations, this is 38.4 seconds, times SIGNIFICANT processing time
num_iterations = 150

# --- Setup SDR ---
print("setting up SDR...\n")
sdr = RtlSdr()
sdr.sample_rate = 2.048e6  # Hz
sdr.center_freq = 1420.405751768e6  # Hz
sdr.bandwidth = 5e6 #Hz, 2 MHz
sdr.freq_correction = 60  # PPM
sdr.gain = 'auto'

avg_Pxx = None

# --- Estimate PSD ---
for _ in range(num_iterations):
    print(f"Running on iteration {_} \n")
    samples = sdr.read_samples(256 * 1024)  # or appropriate size
    Pxx, freqs = psd(samples, NFFT=NFFT, Fs=sdr.sample_rate/1e6)
    freqs += sdr.center_freq / 1e6  # Shift to true RF center frequency
    
    if avg_Pxx is None:
        avg_Pxx = Pxx
    else:
        avg_Pxx += Pxx

avg_Pxx /= num_iterations

sdr.close()

# --- Save baseline for reuse ---
np.save('baseline_psd.npy', avg_Pxx)
np.save('baseline_freqs.npy', freqs)

# --- Plot it ---
plt.plot(freqs, avg_Pxx)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.title('Baseline PSD')
plt.show()
