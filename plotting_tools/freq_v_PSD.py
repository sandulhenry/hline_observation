from pylab import *
import numpy as np
from datetime import datetime
from scipy.signal import medfilt

def freq_v_PSD(file_path):
    time_vals = np.load(file_path + "/time_vals.npy")
    freqs = np.load(file_path + "/freqs.npy")
    power_mtx = np.load(file_path + "/power_mtx.npy")

    # --- Convert to arrays and meshgrid ---
    time_vals = np.array(time_vals)  # shape (T,)
    freqs = np.array(freqs)          # shape (F,)
    power_matrix = np.array(power_mtx)  # shape ()

    for i in range(power_matrix.shape[0]):
        power_matrix[i] = medfilt(power_matrix[i], kernel_size=45)

    for i in range(power_matrix.shape[0]):
        plt.plot(freqs, power_matrix[i])

    plt.xlabel("Frequency (MHz)")
    plt.xticks(ticks = [1419.906, 1420.156, 1420.406, 1420.656, 1420.906])
    plt.ticklabel_format(axis='x', style='plain', useOffset=False)
    plt.ylabel("Relative Intensity (dB)")

    title_string = f"Observation for {datetime.utcfromtimestamp(time_vals[0]).strftime('%d,%m,%Y - %H:%M:%S')}"

    plt.title("Frequencies vs intensity at times")

    save_path = "../observations_img/time_v_PSD/" + title_string + ".png"

    plt.savefig(save_path)

if __name__ == "__main__":
    freq_v_PSD("../observations_raw")