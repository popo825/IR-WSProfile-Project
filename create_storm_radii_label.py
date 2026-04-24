import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Proj
import pandas as pd
from datetime import datetime
from scipy.interpolate import interp1d
import os

def create_storm_radius_label(local_folder, root_dir, quadrant):
    # Folder Handle
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    KT_TO_MS = 0.514444
    v_targets = np.array([34, 50, 64]) * KT_TO_MS
    
    # get hurricane list
    hurricane_folders = [f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))]
    for hurricane_folder in hurricane_folders:
        hurricane_name = hurricane_folder.split('_')[-1].upper()

        # find all timestamp's wind radii correspondingly
        subdir_path = os.path.join(root_dir, hurricane_folder)
        for filename in os.listdir(subdir_path):
            timestamp_str = filename.replace('.txt', '')

            file_full_path = os.path.join(subdir_path, filename)
            data = np.genfromtxt(file_full_path, delimiter=',', skip_header=1)
            radius_col = data[:, 0]
            col_map = {'Mean': 1, 'NE': 2, 'SE': 3, 'SW': 4, 'NW': 5}
            wind_speed_col = data[:, col_map[quadrant]]

            labels = []
            for v_t in v_targets:
                # if the max wind speed < R34/R50/R64, then the radius = 0
                if wind_speed_col.max() < v_t:
                    labels.append(0.0)
                else:
                    # Here, I use linear interpolation to get the radius
                    # (I should change it later since it's derived from parameterization)
                    # (Also need to check whether double/triple peak)
                    # I use [::-1] to make sure the radius is the outermost

                    idx_max = np.argmax(wind_speed_col)
                    # assume one peak, only check the descend part
                    outer_wind = wind_speed_col[idx_max:]
                    outer_radius = radius_col[idx_max:]

                    f = interp1d(outer_wind[::-1], outer_radius[::-1], kind='linear', fill_value="extrapolate")
                    r_interp = f(v_t)
                    labels.append(float(r_interp))

            label_data = np.array(labels, dtype=np.float32)

            npy_filename = f"{local_folder}/{hurricane_name}_{timestamp_str}_{quadrant}.npy"
            np.save(npy_filename, label_data)

            print(f"{npy_filename}-> R34:{label_data[0]:.1f}, R50:{label_data[1]:.1f}, R64:{label_data[2]:.1f}")

if __name__ == "__main__":
    create_storm_radius_label('data', 'WSProfile', 'NE')
    create_storm_radius_label('data', 'WSProfile', 'SE')
    create_storm_radius_label('data', 'WSProfile', 'SW')
    create_storm_radius_label('data', 'WSProfile', 'NW')