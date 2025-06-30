from matplotlib.colors import LightSource
from matplotlib.ticker import ScalarFormatter
from pylab import *
import numpy as np
from datetime import datetime
from scipy.signal import medfilt

def make_3d_plot(file_path):
    time_vals = np.load(file_path + "/time_vals.npy")
    freqs = np.load(file_path + "/freqs.npy")
    power_mtx = np.load(file_path + "/power_mtx.npy")

    # --- Convert to arrays and meshgrid ---
    time_vals = np.array(time_vals)  # shape (T,)
    freqs = np.array(freqs)          # shape (F,)
    power_matrix = np.array(power_mtx)  # shape ()

    for i in range(power_matrix.shape[0]):
        power_matrix[i] = medfilt(power_matrix[i], kernel_size=45)

    # Meshgrid to match plot_surface input format
    T, F = np.meshgrid(time_vals, freqs)

    # Transpose power matrix so it matches meshgrid orientation
    Z = power_matrix.T  # Now shape (F, T)

    title_string = f"Observation for {datetime.utcfromtimestamp(time_vals[0]).strftime('%d,%m,%Y - %H:%M:%S')}"

    # --- Plot ---
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(T, F, Z, cmap=cm.viridis, linewidth=0, antialiased=False)
    ax.set_zlim(np.min(Z)-0.1, np.max(Z)+0.1)
    ax.set_xlabel('Time (HH:MM:SS) | UTC', labelpad=20)
    yticks = [1419.906, 1420.156, 1420.406, 1420.656, 1420.906]

    ax.set_yticks(yticks, minor=False)
    ax.set_ylabel('Frequency (MHz)', labelpad = 15)

    ax.set_zlabel('Power (dB)')

    def format_unix_time(x, _):
        return datetime.utcfromtimestamp(x).strftime('%H:%M:%S')

    ax.xaxis.set_major_formatter(FuncFormatter(format_unix_time))
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
    plt.title(title_string)

    #ax.view_init(elev=90, azim=90)
    save_path = "/home/pi/Documents/HLINE/hline_observation/observations_img/" + title_string + ".png"

    print("Saving into path " + save_path)
    plt.savefig(save_path)

if __name__ == "__main__":
    make_3d_plot("../observations_raw")