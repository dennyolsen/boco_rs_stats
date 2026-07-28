import geopandas as gpd
import rasterio
from rasterstats import zonal_stats


# 1. Load your raster and polygon files
raster_path = "ndvi_output.tif"
vector_path = "ParksWork_-7031856640992189817.geojson"

raster = rasterio.open(raster_path)
polygons = gpd.read_file(vector_path)

# 2. Reproject polygons to match the raster's CRS
if polygons.crs != raster.crs:
    polygons = polygons.to_crs(raster.crs)

# 3. Read raster band and affine transform
band_array = raster.read(1) #should this be zero or one?  internet says one...
affine_transform = raster.transform

# 4. Calculate zonal statistics (mean/average)
stats = zonal_stats(
    polygons,
    band_array,
    affine=affine_transform,
    stats=["mean"],
    nodata=raster.nodata,
    geojson_out=True
)

# 5. View results
for feature in stats:
    print("Feature: " + feature['properties']['ParkGroupDescription'])
    print("Average NDVI: " + str(feature['properties']['mean']))
