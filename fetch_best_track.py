# This code is to fetch the best track hurricane center location data
# from ibtrACS.
# The results are in filtered_hurricane_tracks_2018_2020
# -------------------
import xarray as xr
import pandas as pd
import numpy as np
import os

ds = xr.open_dataset('IBTrACS.NA.v04r01.nc')
mask = (ds.season >= 2018) & (ds.season <= 2020)
ds_filtered = ds.isel(storm=mask)

df = ds_filtered[['iso_time', 'lat', 'lon', 'sid', 'name']].stack(all_obs=['storm', 'date_time']).to_dataframe()

df = df.dropna(subset=['iso_time'])

for col in ['iso_time', 'sid', 'name']:
    if df[col].dtype == object:
        df[col] = df[col].str.decode('utf-8')

df['time'] = pd.to_datetime(df['iso_time'])
df = df.sort_values(['sid', 'time'])

# get 2018-2020 hurricane data
tracks = df[['sid', 'name', 'time', 'lat', 'lon']]

# filter the tracks with the only hurricanes under WSProfile folder
wsprofile_path = 'WSProfile'
folder_names = [f for f in os.listdir(wsprofile_path) if os.path.isdir(os.path.join(wsprofile_path, f))]

target_names = [f.split('_')[-1].upper() for f in folder_names]

print(f"From WSProfile: found {len(target_names)} hurricanes: {target_names}")

final_tracks_filtered = tracks[tracks['name'].isin(target_names)].copy()
final_tracks_filtered = final_tracks_filtered.dropna(subset=['lat', 'lon'])

print(f"Yeah! Found {final_tracks_filtered['name'].nunique()} hurricanes, total {len(final_tracks_filtered)} timestamp.")
print(final_tracks_filtered.head())

output_csv = 'filtered_hurricane_tracks_2018_2020.csv'

final_tracks_filtered.to_csv(output_csv, index=False)