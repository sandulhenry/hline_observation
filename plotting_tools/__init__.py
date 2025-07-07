from .threed_plot import make_3d_plot
from .freq_v_PSD import freq_v_PSD
from .heatmap import make_heatmap

__all__ = ["make_3d_plot","freq_v_PSD","make_heatmap"]

def plot_all(path, hash):
    print("creating all 3 plots, hash value of = " + str(hash))
    freq_v_PSD("/home/pi/Documents/HLINE/hline_observation/observations_raw", hash)
    make_3d_plot("/home/pi/Documents/HLINE/hline_observation/observations_raw", hash)
    make_heatmap("/home/pi/Documents/HLINE/hline_observation/observations_raw", hash)