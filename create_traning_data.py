# This code is to generate the training data from IR_data nc file set.
# Generated data (.npy) will be in data folder.
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Proj
import pandas as pd
from datetime import datetime
import os
import cv2

def crop_hurricane_image_save(local_folder, hurricane_name, timestamp, nc_path, target_lat, target_lon, size_km):
    ds = xr.open_dataset(nc_path)
    
    # get the CMI data and coordinate transformation information
    ir_data = ds['CMI']
    h = ds.goes_imager_projection.perspective_point_height

    proj_info = ds.goes_imager_projection
    p = Proj(proj='geos', 
            h=proj_info.perspective_point_height, 
            lon_0=proj_info.longitude_of_projection_origin, 
            sweep=proj_info.sweep_angle_axis)
    center_x, center_y = p(target_lon, target_lat)

    half_width = size_km/2*1000
    x_min = (center_x - half_width) / h
    x_max = (center_x + half_width) / h
    y_min = (center_y - half_width) / h
    y_max = (center_y + half_width) / h

    ir_subset = ir_data.sel(x=slice(x_min, x_max), y=slice(y_max, y_min))

    ir_numpy = ir_subset.values

    # Due to projection method on different latitude,
    # An important procedure is that the input size should be standardized
    # Again, I use the linear interpolation method to modify the size slightly.
    # In 400x400 km case, targer_px = 200
    target_px = 200
    ir_resized = cv2.resize(ir_numpy, (target_px, target_px), interpolation=cv2.INTER_LINEAR)
    
    # CNN input format requirement: (Height, Width, Channels): (200, 200, 1)
    # Add more channel in the future to test multi-channel experiments.
    ir_final = np.expand_dims(ir_resized, axis=-1)

    npy_filename = f"{local_folder}/{hurricane_name}_{timestamp}.npy"
    np.save(npy_filename, ir_final)
    print(f"Image shape: {ir_final.shape}, creating file: {npy_filename}")

    ds.close()

def create_training_dataset(local_folder, root_dir, ir_data_dir):
    # Folder Handle
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # central lat/lon dataset fetch
    df = pd.read_csv("filtered_hurricane_tracks_2018_2020.csv")
    df['time'] = pd.to_datetime(df['time'])

    # get hurricane list
    hurricane_folders = [f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))]
    for hurricane_folder in hurricane_folders:
        hurricane_name = hurricane_folder.split('_')[-1].upper()

        # get that hurricane's lifetime track data (every 3 hr)
        storm_tracks = df[df['name'] == hurricane_name].sort_values('time')
        
        if storm_tracks.empty:
            print(f"Couldn't {hurricane_name}'s track data")
            continue
        
        # Important: I use linear interpolation to get higher
        # time-resolution data. Since WSProfile is made every 1 hr
        # (3hr -> 1hr) 
        # ----------------
        storm_tracks = storm_tracks.set_index('time').sort_index()
        hourly_range = pd.date_range(start=storm_tracks.index.min(), end=storm_tracks.index.max(), freq='1h')
        storm_tracks_hourly = storm_tracks[['lat', 'lon']].reindex(hourly_range).interpolate(method='linear')
        # ----------------
        
        # find all timestamp's IR image correspondingly
        subdir_path = os.path.join(root_dir, hurricane_folder)
        for filename in os.listdir(subdir_path):
            timestamp_str = filename.replace('.txt', '')
            target_time = datetime.strptime(timestamp_str, '%Y-%m-%d_%H')

            interp_lat = storm_tracks_hourly.loc[target_time, 'lat']
            interp_lon = storm_tracks_hourly.loc[target_time, 'lon']

            nc_path = os.path.join(ir_data_dir, f"{timestamp_str}.nc")

            crop_hurricane_image_save(
                        local_folder=local_folder,
                        hurricane_name=hurricane_name,
                        timestamp=timestamp_str,
                        nc_path=nc_path,
                        target_lat=interp_lat,
                        target_lon=interp_lon,
                        size_km=400
                    )
            
if __name__ == "__main__":
    create_training_dataset('data', 'WSProfile', 'IR_data')