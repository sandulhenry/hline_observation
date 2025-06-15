from pylab import *
from rtlsdr import *
import numpy as np

# --- Setup SDR ---
sdr = RtlSdr()
sdr.sample_rate = 2.048e6  # Hz
sdr.center_freq = 1420.405751768e6  # Hz
sdr.bandwidth = 5e6 #Hz, 2 MHz
sdr.freq_correction = 60  # PPM
sdr.gain = 'auto'

NFFT = 1024

# --- Load baseline for reuse ---
bxc_Pxx = np.load('baseline_psd.npy')
bcx_freqs = np.load('baseline_freqs.npy')

def average_sample(num_iterations):
    avg_Pxx = None

    # --- Estimate PSD ---
    for _ in range(num_iterations):
        #print(f"Running on iteration {_} \n")
        samples = sdr.read_samples(32 * 1024)  # or appropriate size
        Pxx, freqs = psd(samples, NFFT=NFFT, Fs=sdr.sample_rate/1e6)
        freqs += sdr.center_freq / 1e6  # Shift to true RF center frequency
        
        if avg_Pxx is None:
            avg_Pxx = Pxx
        else:
            avg_Pxx += Pxx

    avg_Pxx /= num_iterations

    Pxx_dB = 10 * np.log10(avg_Pxx)
    bxc_Pxx_dB = 10 * np.log10(bxc_Pxx)
    Pxx_obs_dB = Pxx_dB - bxc_Pxx_dB

    return Pxx_obs_dB, freqs


# --- Capture Samples ---

# --- Estimate PSD ---
Pxx, freqs = average_sample(300)

# --- Plot it ---
plt.clf()
plt.plot(freqs, Pxx)
plt.xlabel("Frequency (MHz)")
plt.ylabel("Power Difference (dB)")
plt.title("PSD Difference (Observation - Baseline)")
plt.grid()
plt.show()
