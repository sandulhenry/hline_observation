from pylab import *
from rtlsdr import *
import numpy as np
from astropy.time import Time
from matplotlib.colors import LightSource

power_matrix = np.load("power_mtx.npy")
time_vals = np.load("time_vals.npy")
freqs = np.load("freqs.npy")

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
ax.set_zlim(-5, 5)
ax.set_xlabel('Time (Unix seconds)')
ax.set_ylabel('Frequency (MHz)')
ax.set_zlabel('Power (dB)')
plt.title("Time-Frequency PSD Surface")

plt.show()
