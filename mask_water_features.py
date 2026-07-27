import json
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# 1. Open the raster dataset
raster_path = "result.tiff"
src = rasterio.open(raster_path)

# 2. Load the polygon layer using GeoPandas
vector_path = "Lakes_and_Reservoirs.geojson"
gdf = gpd.read_file(vector_path)

# 3. Reproject polygon to match the raster's CRS
if gdf.crs != src.crs:
  gdf = gdf.to_crs(src.crs)

# 4. Extract geometries into GeoJSON-format list expected by rasterio
geoms = [feature["geometry"] for feature in gdf.iterfeatures()]
# Note: For multiple features, use: [feature["geometry"] for feature in gdf.iterfeatures()]

# 5. Apply the INVERSE mask (invert=True keeps areas OUTSIDE the polygon)
out_image, out_transform = mask(
    dataset=src, shapes=geoms, invert=True, crop=False
)

# 6. Copy and update metadata for the output file
out_meta = src.meta.copy()
out_meta.update({
    "driver": "GTiff",
    "height": out_image.shape[1],
    "width": out_image.shape[2],
    "transform": out_transform,
})

# 7. Save the masked raster to a new file
output_path = "inverse_masked_raster.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
  dest.write(out_image)

src.close()
