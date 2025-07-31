from pylab import *
import numpy as np
from datetime import datetime
from scipy.signal import medfilt

def make_heatmap(file_path, hash):
    time_vals = np.load(file_path + "/time_vals.npy")
    freqs = np.load(file_path + "/freqs.npy")
    power_mtx = np.load(file_path + "/power_mtx.npy")

    # addition median filtering
    # for i in range(power_mtx.shape[0]):
        # power_mtx[i] = medfilt(power_mtx[i], kernel_size=45)
    

    #convert UNIX time to UTC time representation

    time_labels = [datetime.utcfromtimestamp(t) for t in time_vals]

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(
        power_mtx.T, aspect='auto', origin='lower',
        extent=[0, len(time_vals), freqs[0], freqs[-1]],
        cmap='plasma'
    )

    # X-ticks as time strings
    xtick_indices = np.linspace(0, len(time_vals) - 1, num=10, dtype=int)
    xtick_labels = [time_labels[i].strftime('%H:%M:%S') for i in xtick_indices]
    ax.set_xticks(xtick_indices)
    ax.set_xticklabels(xtick_labels, rotation=30)

    plt.yticks(ticks = [1419.906, 1420.156, 1420.406, 1420.656, 1420.906])
    plt.ticklabel_format(axis='y', style='plain', useOffset=False)

    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Frequency (MHz)")
    ax.set_title("Waterfall (Frequency vs Time)")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Power (dB)")

    title_string = f"Observation for {datetime.utcfromtimestamp(time_vals[0]).strftime('%d,%m,%Y - %H:%M:%S')}"

    plt.tight_layout()

    print("Saving to " + "/home/pi/Documents/HLINE/hline_observation/observations_img/" + str(hash) + "/heatmap.png")
    plt.savefig("/home/pi/Documents/HLINE/hline_observation/observations_img/" + str(hash) + "/heatmap.png")
    plt.close()

    