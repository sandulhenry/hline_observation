from pylab import *
from rtlsdr import *
import numpy as np
from astropy.time import Time
from datetime import datetime
from plotting_tools import make_3d_plot
from scipy.signal import medfilt
from scipy.signal import welch
import gc

def observation(NFFT, num_steps, length_avg):
    # --- Setup SDR ---
    print("Setting up SDR...")
    sdr = RtlSdr()
    sdr.sample_rate = 2.048e6  # Hz
    sdr.center_freq = 1420.405751768e6 - 0.51e6  # Hz
    sdr.freq_correction = -9  # PPM
    sdr.gain = 'auto'

    floor_freq = 1420.405751768e6 - 0.5e6
    ceiling_freq = 1420.405751768e6 + 0.5e6

    # NFFT is defined in the function call
    num_samples = 256*1024 # number of samples per step
    # num_steps is defined in the function call
    # length_avg defined in the function call

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

        #print("Sampling done... moving on to post-processing")
        freqs_centered = freqs + sdr.center_freq # 0 Hz -> center frequency
        mask = (freqs_centered >= floor_freq) & (freqs_centered <= ceiling_freq)

        freqs_centered = freqs_centered[mask] / 1e6
        avg_Pxx = avg_Pxx[mask]

        # welsh's method function doesn't necessairly return an ordered form of 
        # frequencies
        sorted_indices = np.argsort(freqs_centered)
        freqs_centered = freqs_centered[sorted_indices]
        avg_Pxx = avg_Pxx[sorted_indices]

        # Converting to decimals. garuntees we don't take the log of 0
        Pxx_dB = 10 * np.log10(avg_Pxx + 1e-12)

        # subtracting the baseline to get a relative behavior
        Pxx_dB -= bxc_Pxx_dB

        # removes DC spikes. DC Spikes may be caused by the behavior of the SDR,
        # LNA, and even changes with factors like temperature
        Pxx_dB = medfilt(Pxx_dB, kernel_size=13)

        # normalization to the median works better that normalization to the min
        # . The minimum could be spiking downwards, which leads to messy 
        # behavior. In general, the median would never change. This lines up the 
        # measurements at 0. 
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
    np.save("observations_raw/power_mtx.npy", power_mtx)
    #print("Finished sampling. Creating plot.")

def main():
    observation(NFFT = 1024, num_steps = 500, length_avg = 800)
    print("completed observation")

    make_3d_plot("./observations_raw")

if __name__ == "__main__":
    main()
