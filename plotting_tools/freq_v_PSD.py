from pylab import *
import numpy as np
from datetime import datetime
from scipy.signal import medfilt
import matplotlib.ticker as mticker

def freq_v_PSD(file_path, hash: int):
    time_vals = np.load(file_path + "/time_vals.npy")
    freqs = np.load(file_path + "/freqs.npy")
    power_mtx = np.load(file_path + "/power_mtx.npy")

    # --- Convert to arrays and meshgrid ---
    time_vals = np.array(time_vals)  # shape (T,)
    freqs = np.array(freqs)          # shape (F,)
    power_matrix = np.array(power_mtx)  # shape ()

    #for i in range(power_matrix.shape[0]):
        #power_matrix[i] = medfilt(power_matrix[i], kernel_size=45)

    for i in range(power_matrix.shape[0]):
        plt.plot(freqs, power_matrix[i])

    plt.xlabel("Frequency (MHz)")
    plt.xticks(ticks = [1419.906, 1420.156, 1420.406, 1420.656, 1420.906])
    # plt.ticklabel_format(axis='x', style='plain', useOffset=False)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.ticklabel_format(axis='x', style='plain', useOffset=False)

    plt.ylabel("Relative Intensity (dB)")

    title_string = f"Observation for {datetime.utcfromtimestamp(time_vals[0]).strftime('%d,%m,%Y - %H:%M:%S')}"

    plt.title("Frequencies vs Intensity at Times")

    save_path = "/home/pi/Documents/HLINE/hline_observation/observations_img/" + str(hash) + "/freq_v_PSD.png"

    print("Saving to " + save_path)

    plt.savefig(save_path)