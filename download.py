# OpenOE
import openeo
# Deps for specifying query parameters
from pyproj import Transformer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
# Deps for scale factor conversion
from openeo.processes import ProcessBuilder

connection = openeo.connect("openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()

collections = connection.list_collection_ids()
sentinel_collections = [c for c in collections if 'SENTINEL' in c]
print("Sentinel collections available:")
print('\n'.join(sentinel_collections))

# coordinates of the bounding box for Boulder County, Colorado, USA
lon_min, lon_max = -105.694362, -105.052774
lat_min, lat_max = 39.912886, 40.262785
spatial_extent = {
        "west": lon_min, "south": lat_min,
        "east": lon_max, "north": lat_max}

#selecting temporal extent
today_date = datetime.now().date()
number_month = 3
month_3_data = today_date -timedelta(days=(number_month*30))
temporal_extent = [str(month_3_data),str(today_date)]
print(spatial_extent)
print(temporal_extent)

#load parameters
sentinel2_cube = connection.load_collection(
    "SENTINEL2_L2A", #collection chosen
    spatial_extent=spatial_extent,
    temporal_extent=temporal_extent,
    bands=["B04", "B08", "SCL"],
    max_cloud_cover=50
)

#prepare for SCL mask processing
sentinel2_cube = sentinel2_cube.process("mask_scl_dilation", data=sentinel2_cube, scl_band_name="SCL")

#reduce the time dimension to get a median composite image
median_image = sentinel2_cube.reduce_dimension(dimension="t", reducer="median")

# Scale factor conversion for Sentinel-2 L2A data (from 0-10000 to 0-1)
# define child process, use ProcessBuilder
def scale_function(x: ProcessBuilder):
    return x * 0.0001

# Convert to reflectance (simple multiplication)
print("Converting to reflectance...")
reflectance_cube= median_image.apply(scale_function)

# Specify the save format 
final_result = reflectance_cube.save_result(format="GTiff")

# Define job title and description
job_title = "R, NIR bands and SCL mask for Boulder County, Colorado, USA"

job = final_result.create_job(
                title=job_title,
                description="This pipeline downloads and processes images of specific fields in Boulder County, Colorado, USA"
            )

# Run Job
try:    
    result = job.start_and_wait(
                    print=lambda msg: print(f"message: [{msg}]"),
                    max_poll_interval=30, 
                    connection_retry_interval=60  
                )
    print(f"✅ Job started with ID: {job.job_id}")
except Exception as e:
    print(f"the job failed {e}")

# Download the result

download_dir = "./result.tiff"

image = job.download_results(download_dir)
print(f"Downloaded files to {download_dir}/")