from pylab import *
from rtlsdr import *
import numpy as np
from astropy.time import Time
from datetime import datetime
from matplotlib.colors import LightSource
from scipy.signal import medfilt
from scipy.signal import welch
import gc

# --- Setup SDR ---
print("Setting up SDR...")
sdr = RtlSdr()
sdr.sample_rate = 2.048e6  # Hz
sdr.center_freq = 1420.405751768e6 - 0.51e6  # Hz
sdr.freq_correction = 7  # PPM
sdr.gain = 'auto'

floor_freq = 1420.405751768e6 - 0.5e6
ceiling_freq = 1420.405751768e6 + 0.5e6

NFFT = 1024
num_samples = 256*1024 # number of samples per step
num_steps = 150
length_avg = 750

# --- Load baseline for reuse ---
bxc_Pxx_dB = np.load('baseline_psd_dB.npy')
bcx_freqs = np.load('baseline_freqs.npy')

def average_sample(num_iterations):
    avg_Pxx = None

    # --- Estimate PSD ---
    for _ in range(num_iterations):
        #print(f"Running on iteration {_}")
        try:
            samples = sdr.read_samples(num_samples)
        except Exception as e:
            print(f"SDR read error: {e}, at time {Time.now()}")
            continue
        
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

    freqs_centered = freqs + sdr.center_freq
    mask = (freqs_centered >= floor_freq) & (freqs_centered <= ceiling_freq)

    freqs_centered = freqs_centered[mask] / 1e6
    avg_Pxx = avg_Pxx[mask]

    sorted_indices = np.argsort(freqs_centered)
    freqs_centered = freqs_centered[sorted_indices]
    avg_Pxx = avg_Pxx[sorted_indices]

    Pxx_dB = 10 * np.log10(avg_Pxx + 1e-12)

    Pxx_dB -= bxc_Pxx_dB

    Pxx_dB = medfilt(Pxx_dB, kernel_size=11)

    #normalization seems to cause standoffish problems
    median_psd = np.median(Pxx_dB)
    Pxx_dB = Pxx_dB - median_psd

    return Pxx_dB

print(f"SDR launched. Beginning on {num_steps} observations; {length_avg} per average; NFFT={NFFT}")

power_mtx = np.zeros((num_steps, len(bcx_freqs)))
time_vals = np.zeros(num_steps)

for i in range(num_steps):
    print(f"Working on avg FFT {i}, time is now {Time.now()} UTC")
    Pxx_dB = average_sample(length_avg)
    power_mtx[i, :] = Pxx_dB
    time_vals[i] = Time.now().unix
    del Pxx_dB
    gc.collect()

sdr.close()

np.save("observations_raw/time_vals.npy", time_vals)
np.save("observations_raw/freqs.npy", bcx_freqs)

print("Finished sampling. Creating plot.")

# --- Convert to arrays and meshgrid ---
time_vals = np.array(time_vals)  # shape (T,)
freqs = np.array(bcx_freqs)          # shape (F,)
power_matrix = np.array(power_mtx)  # shape (T, F)

# Meshgrid to match plot_surface input format
T, F = np.meshgrid(time_vals, freqs)

# Transpose power matrix so it matches meshgrid orientation
Z = power_matrix.T  # Now shape (F, T)

title_string = f"Observation for {datetime.utcfromtimestamp(time_vals[0]).strftime('%H:%M:%S')}"

# --- Plot ---
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(T, F, Z, cmap=cm.viridis, linewidth=0, antialiased=False)
ax.set_zlim(np.min(Z)-0.25, np.max(Z)+0.5)
ax.set_xlabel('Time (HH:MM:SS) | UTC', labelpad=20)
ax.set_ylabel('Frequency (MHz)')
ax.set_zlabel('Power (dB)')

def format_unix_time(x, _):
    return datetime.utcfromtimestamp(x).strftime('%H:%M:%S')

ax.xaxis.set_major_formatter(FuncFormatter(format_unix_time))
plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
plt.title(title_string)

#ax.view_init(elev=90, azim=90)
file_path = "observations_img/" + title_string + ".png"
plt.savefig(file_path)
