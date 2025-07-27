from pylab import *
from rtlsdr import *
import numpy as np
from astropy.time import Time
from datetime import datetime, timezone
from plotting_tools import plot_all
from scipy.signal import medfilt
from scipy.signal import welch
import gc
import os, os.path
import subprocess
from experiment import Experiment
from makeemail import send_email

# Globally used variables
ppm = 1 # default PPM correction. 1 ppm -> 1 MHz offset

# 1 MHz bandwidth
center = 1420.405751768e6 - 0.51e6 # offset from the hline to avoid the DC spike
floor_freq = 1420.405751768e6 - 0.5e6
ceiling_freq = 1420.405751768e6 + 0.5e6

bxc_Pxx_dB = np.load('baseline_psd_dB.npy')
bcx_freqs = np.load('baseline_freqs.npy')

def get_ppm():
    # check if getppm (exec) exists in the same directory
    file_path = "/home/pi/Documents/HLINE/hline_observation/getppm"

    if os.path.exists(file_path):
        print(f"The file '{file_path}' exists.")
    else:
        print(f"The file '{file_path}' does not exist.")

    subprocess.run(file_path)

    try:
        with open('/home/pi/Documents/HLINE/hline_observation/ppm.dat', 'r') as file:
            # Read the first line and remove leading/trailing whitespace
            line = file.readline().strip() 
            
            # Convert the cleaned string to an integer
            global ppm
            ppm = int(line)

            if(ppm == 0):
                ppm = 1 #Can't set PPM correction to 0 
            print(f"Successfully read ppm val: {ppm}")
    except FileNotFoundError:
        print("Error: The file 'ppm.dat' was not found.")
    except ValueError:
        print("Error: The content in the file is not a valid integer.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

# The average sample function is used in both explicitly defined observations, 
# and time defined observations. It is based on Welch's method. While not an 
# explicit Fourier Transform, Welch's method yields a smoother Power Spectral 
# Density graph, by taking the FFT of many overlapping windows of a time-valued
# signal, and taking the average of those. This is important because if a 
# frequency is present in only one part of a signal, its effect in the frequency
# domain is downplayed  in Welch's method. 
# 
# sdr - the sdr object. Instead of recreating it inside avg_sample, let the 
#       calling function pass this object.
# num_iterations - the number of PSD to create, and to take the average of those
# num_samples - the number of samples the SDR is expected to draw. 
# NFFT - the resolution. For this program's bandwidth, this yields 500 
#        frequencies (i think)
def average_sample(sdr, num_iterations, num_samples, NFFT):
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
    Pxx_dB = medfilt(Pxx_dB, kernel_size=45)

    # Normalization to the median should work better than normalization to the 
    # minimum. If there is a spike downwards, that could create a problem for a 
    # minimum normalization. Due to factors like temperature and environment, 
    # the noise floor of the system may change. By adding a median filter, the 
    # "center" of the frequency-domain signal should remain relatively at 0, as 
    # the median of the signal should particularly change. 
    median_psd = np.median(Pxx_dB)
    Pxx_dB = Pxx_dB - median_psd

    return Pxx_dB


def observation(NFFT, num_steps, length_avg):
    # --- Setup SDR ---
    print("Setting up SDR...")
    sdr = RtlSdr()
    sdr.sample_rate = 2.048e6  # Hz
    sdr.center_freq = center  # Hz
    sdr.freq_correction = ppm  # PPM
    sdr.gain = 'auto'

    # NFFT is defined in the function call
    num_samples = 256*1024 # number of samples per step
    # num_steps is defined in the function call
    # length_avg defined in the function call

    print(f"SDR launched. Beginning on {num_steps} observations; {length_avg} per average; NFFT={NFFT}")

    power_mtx = np.zeros((num_steps, len(bcx_freqs)))
    time_vals = np.zeros(num_steps)

    for i in range(num_steps):
        print(f"Working on avg FFT {i}, time is now {Time.now()} UTC")
        Pxx_dB = average_sample(sdr, length_avg, num_samples, NFFT)
        power_mtx[i, :] = Pxx_dB
        time_vals[i] = Time.now().unix
        del Pxx_dB
        gc.collect()

    sdr.close()

    np.save("observations_raw/time_vals.npy", time_vals)
    np.save("observations_raw/freqs.npy", bcx_freqs)
    np.save("observations_raw/power_mtx.npy", power_mtx)
    #print("Finished sampling. Creating plot.")

def timeexp(start: datetime, end:datetime , NFFT: int, length_avg: int):

    print("Getting PPM correction for accuracy (est. 240 seconds)")
    get_ppm()
    print("Beginning time based observation...")
    print(f"Start time: {datetime.fromtimestamp(start, timezone.utc)}")
    print(f"End time:  {datetime.fromtimestamp(end, timezone.utc)}")

    # --- Setup SDR ---
    print("Setting up SDR...")
    sdr = RtlSdr()
    sdr.sample_rate = 2.048e6  # Hz
    sdr.center_freq = center  # Hz
    sdr.freq_correction = ppm  # PPM
    sdr.gain = 'auto'

    # NFFT is defined in the function call
    num_samples = 256*1024 # number of samples per step
    # length_avg defined in the function call

    # --- Load baseline for reuse ---
    num_FFTs = 0
    
    # because the number of steps is unknown, incrementally build a list
    # previously, it was convenient to have a defined array because we knew
    # the length of averages, and the number of averages we would take
    power_mtx = []
    time_vals = []

    while (datetime.now(timezone.utc).timestamp() < end):
        print(f"Working on avg FFT {num_FFTs}, time is now {Time.now()} UTC")
        Pxx_dB = average_sample(sdr, length_avg, num_samples, NFFT)
        power_mtx.append(Pxx_dB)
        time_vals.append(Time.now().unix)
        del Pxx_dB
        gc.collect()
        num_FFTs += 1

    print("Finished sampling. Saving.")

    power_mtx = np.array(power_mtx)
    time_vals = np.array(time_vals)
    sdr.close()
    np.save("observations_raw/time_vals.npy", time_vals)
    np.save("observations_raw/freqs.npy", bcx_freqs)
    np.save("observations_raw/power_mtx.npy", power_mtx)