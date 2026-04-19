# This code is to fetch the IR chennel data from the GOES-16 cloud database
# -----------------------------
import boto3
import os
import shutil
from botocore import UNSIGNED
from datetime import datetime, timedelta
from botocore.config import Config

def get_nc_file_name(year, doy, hour):
    date_obj = datetime(year, 1, 1) + timedelta(days=int(doy) - 1)
    file_name = date_obj.strftime(f"%Y-%m-%d_{int(hour):02d}.nc")
    
    return file_name

def download_goes16_ir(year, doy, hour, channel, local_folder='data'):

    # Folder Handle
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
    
    # s3 client setup
    s3 = boto3.client('s3', 
                      region_name='us-east-1', 
                      config=Config(signature_version=UNSIGNED))
    
    bucket_name = 'noaa-goes16'
    prefix = f'ABI-L2-CMIPF/{year}/{str(doy).zfill(3)}/{str(hour).zfill(2)}/'
    
    # List all data in that hour
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    if 'Contents' not in response:
        print("Couldn't find data from prefix.")
        return

    target_files = [obj['Key'] for obj in response['Contents'] if f'M6{channel}' in obj['Key'] or f'M3{channel}' in obj['Key']]
    # print(target_files)
    if not target_files:
        print(f"Didn't find {channel} file")
        return

    # only fetch the first data within one hour
    target_files.sort()
    file_key = target_files[0]
    file_name = get_nc_file_name(year, doy, hour)
    local_path = os.path.join(local_folder, file_name)

    print(f"Downloading: {file_name}")
    s3.download_file(bucket_name, file_key, local_path)
    return local_path

def process_all_timestamps(root_dir='WSProfile'):
    unique_timestamps = set()
    
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        
        if os.path.isdir(subdir_path):
            for filename in os.listdir(subdir_path):
                if filename.endswith('.txt'):
                    try:
                        time_part = filename.replace('.txt', '')
                        dt_obj = datetime.strptime(time_part, '%Y-%m-%d_%H')
                        
                        year = dt_obj.year
                        doy = dt_obj.timetuple().tm_yday
                        hour = dt_obj.hour
                        
                        unique_timestamps.add((year, doy, hour))
                    except ValueError:
                        print(f"Error file: {filename}")

    sorted_timestamps = sorted(list(unique_timestamps))
    print(f"Find {len(sorted_timestamps)} total non-repeated timestamp")

    for y, d, h in sorted_timestamps:
        print(f"Processed: {y} Year, {d} DOY, {h} Hour...")
        download_goes16_ir(y, d, h, channel='C14')

if __name__ == "__main__":
    process_all_timestamps('WSProfile')