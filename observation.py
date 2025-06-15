from pylab import *
from rtlsdr import *
import numpy as np
from astropy.time import Time
import time
from matplotlib.colors import LightSource

# --- Setup SDR ---
sdr = RtlSdr()
sdr.sample_rate = 2.048e6  # Hz
sdr.center_freq = 1420.405751768e6 - 250e3  # Hz
sdr.bandwidth = 2e6 #Hz, 10 MHz, (+5, -5)
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
        samples = sdr.read_samples(128 * 1024)  # or appropriate size
        Pxx, freqs = psd(samples, NFFT=NFFT, Fs=sdr.sample_rate/1e6)
        freqs += sdr.center_freq / 1e6  # Shift to true RF center frequency
        
        if avg_Pxx is None:
            avg_Pxx = Pxx
        else:
            avg_Pxx += Pxx
    time.sleep(0.2)

    avg_Pxx /= num_iterations

    Pxx_dB = 10 * np.log10(avg_Pxx)
    bxc_Pxx_dB = 10 * np.log10(bxc_Pxx)
    Pxx_obs_dB = Pxx_dB - bxc_Pxx_dB

    return Pxx_obs_dB, freqs

num_steps = 10
time_vals = []
power_matrix = []
freqs = None

for i in range(num_steps):
    print(f"Working on avg FFT {i}")
    time_now = Time.now().iso  # or .jd for Julian Date
    Pxx_dB, freqs = average_sample(500)
    time_vals.append(time_now)
    power_matrix.append(Pxx_dB)

sdr.close()

np.save("power_mtx.npy", power_matrix)
np.save("time_vals.npy", time_vals)
np.save("freqs", freqs)

# --- Convert to arrays and meshgrid ---
time_vals = np.array(time_vals)  # shape (T,)
freqs = np.array(freqs)          # shape (F,)
power_matrix = np.array(power_matrix)  # shape (T, F)

# Meshgrid to match plot_surface input format
T, F = np.meshgrid(time_vals, freqs)

# Transpose power matrix so it matches meshgrid orientation
Z = power_matrix.T  # Now shape (F, T)

# --- Plot ---
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(T, F, Z, cmap=cm.viridis, linewidth=0, antialiased=False)
ax.set_zlim(-5, 20)
ax.set_xlabel('Time (Unix seconds)')
ax.set_ylabel('Frequency (MHz)')
ax.set_zlabel('Power (dB)')
plt.title("Time-Frequency PSD Surface")

plt.show()


'''
Pxx, freqs = average_sample(100)

sdr.close()


# --- Plot ---
plt.clf()
plt.plot(freqs, Pxx)
plt.ylim(-20,20)
plt.xlabel("Frequency (MHz)")
plt.ylabel("Power Difference (dB)")
plt.title("PSD Difference (Observation - Baseline)")
plt.grid()
plt.show()
'''
