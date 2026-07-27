import numpy as np
import rasterio

file = "inverse_masked_raster.tif"

# 1. Open the Red and NIR raster bands (e.g., Band 4 and Band 8 for Sentinel-2)
with rasterio.open(file) as src_red:
  red = src_red.read(1).astype(np.float32)
  red_nodata = src_red.nodata
  profile = src_red.profile

with rasterio.open(file) as src_nir:
  nir = src_nir.read(2).astype(np.float32)
  nir_nodata = src_nir.nodata

# 2. Build a mask for existing null/no-data values
null_mask = (
    (red == red_nodata)
    | (nir == nir_nodata)
    | np.isnan(red)
    | np.isnan(nir)
    | ((nir + red) == 0)
)

# 3. Calculate NDVI, assigning NaN to null/zero-denominator conditions
ndvi = np.where(null_mask, np.nan, (nir - red) / (nir + red))

# 4. Optional: Save output back to a GeoTIFF with a designated NoData value
profile.update(dtype=rasterio.float32, count=1, nodata=-9999)

ndvi_output = np.where(np.isnan(ndvi), -9999, ndvi)

with rasterio.open("ndvi_output.tif", "w", **profile) as dst:
  dst.write(ndvi_output.astype(rasterio.float32), 1)
