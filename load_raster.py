import openeo
from datetime import datetime, timedelta
from openeo.processes import ProcessBuilder

def load_10m_data(lon_min, lon_max, lat_min, lat_max, number_days):
    connection = openeo.connect("openeo.dataspace.copernicus.eu")
    connection.authenticate_oidc()

    # coordinates of the bounding box, specified in pipeline.py
    spatial_extent = {
            "west": lon_min, "south": lat_min,
            "east": lon_max, "north": lat_max}

    #selecting temporal extent
    today_date = datetime.now().date()
    window_data = today_date -timedelta(days=number_days)
    temporal_extent = [str(window_data),str(today_date)]
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

    # remove SCL band

    # sentinel2_cube = sentinel2_cube.drop_bands("SCL")

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