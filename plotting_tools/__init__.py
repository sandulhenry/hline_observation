from .threed_plot import make_3d_plot
from .freq_v_PSD import freq_v_PSD
from .heatmap import make_heatmap

import traceback

__all__ = ["make_3d_plot","freq_v_PSD","make_heatmap"]

# path below refers to the raw data (.npy) files
# hash refers to the hash value assigned to the experiment at birth
def plot_all(path, hash):
    
    print("creating all 3 plots, hash value of = " + str(hash))
    
    try:
        print("Attempting to make freq v PSD plot...")
        freq_v_PSD("/home/pi/Documents/HLINE/hline_observation/observations_raw", hash)
    except Exception as e:
        print(f"Attempt failed due to error {e}")
        
    try:
        print("Attempting to make 3D plot...")
        make_3d_plot("/home/pi/Documents/HLINE/hline_observation/observations_raw", hash)
    except Exception as e:
        print(f"Attempt failed due to error {e}")
        
    try:
        print("Attempting to make a heatmap...")
        make_heatmap("/home/pi/Documents/HLINE/hline_observation/observations_raw", hash)
    except Exception as e:
        print(f"Attempt failed due to error {e}")