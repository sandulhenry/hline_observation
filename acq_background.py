import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from rtlsdr import RtlSdr
from scipy.signal import welch

# This script generates a background acquisition. While running, make sure your
# setup is pointing towards no significant source of radition (i.e. empty sky).
# When subtracted from future obsevations, it makes the graph more intutive by
# removing parts that are considiered "background" in space, the impedence of 
# the antenna, etc.

# --- Define Variables ---
NFFT = 1024
# sdr.read_samples(x) pulls an x number of samples
# at 256*1024/2.048e6 = 0.128 seconds per iteration
# for 300 iterations, this is 38.4 seconds, times SIGNIFICANT processing time
num_iterations = 1000 #originally 300

# --- Setup SDR ---
print("Setting up SDR...")
sdr = RtlSdr()
sdr.sample_rate = 2.048e6  # Hz = 2048000
sdr.center_freq = 1420.405751768e6 - 0.51e6  # Hz
sdr.freq_correction = 20  # PPM
sdr.gain = 'auto'

floor_freq = 1420.405751768e6 - 0.5e6
ceiling_freq = 1420.405751768e6 + 0.5e6

avg_Pxx = None

# --- Estimate PSD ---
print(f"Running on center frequency {sdr.center_freq / 1e6} MHz, for an iterations of {num_iterations}")

for _ in range(num_iterations):
    print(f"Running on iteration {_}")
    samples = sdr.read_samples(256 * 1024)  # or appropriate size
    

    freqs, Pxx = welch(samples, 
                        fs=sdr.sample_rate, 
                        nperseg=NFFT, 
                        noverlap=NFFT//2, 
                        return_onesided=False)
    
    if avg_Pxx is None:
        avg_Pxx = Pxx
    else:
        avg_Pxx += Pxx

avg_Pxx /= num_iterations

print(freqs)

freqs_centered = freqs + sdr.center_freq
print(freqs_centered)
mask = (freqs_centered >= floor_freq) & (freqs_centered <= ceiling_freq)

# Apply mask first
freqs_centered = freqs_centered[mask] / 1e6
print(freqs_centered)
avg_Pxx = avg_Pxx[mask]

# Then sort
sorted_indices = np.argsort(freqs_centered)
freqs_centered = freqs_centered[sorted_indices]
avg_Pxx = avg_Pxx[sorted_indices]

print(freqs_centered)

avg_Pxx_dB = 10 * np.log10(avg_Pxx + 1e-12)

sdr.close()

print("NaNs in Pxx_dB:", np.any(np.isnan(avg_Pxx_dB)))
print("Infs in Pxx_dB:", np.any(np.isinf(avg_Pxx_dB)))

print("freqs dtype:", freqs_centered.dtype)
print("Pxx dtype:", avg_Pxx_dB.dtype)

print("freqs length", len(freqs_centered))

# --- Save baseline for reuse ---
np.save('baseline_psd_dB.npy', avg_Pxx_dB)
np.save('baseline_freqs.npy', freqs_centered)

fig, ax = plt.subplots()

# Plot PSD
ax.plot(freqs_centered, avg_Pxx_dB)

# Format x-axis
ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.ticklabel_format(style='plain', axis='x')
ax.tick_params(axis='x', labelrotation=45)

# Label axes
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Relative power (dB)')
ax.set_title('Baseline PSD')

# Highlight hydrogen line
hydrogen_freq = 1420.405751768
ax.axvline(x=hydrogen_freq, color='red', linestyle='--', linewidth=1.5, label='Hydrogen Line')
ax.legend()

plt.tight_layout()
plt.savefig("Acquired Background.png")
plt.show()
