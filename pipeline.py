from load_raster import load_10m_data
from mask_water_features import mask_water_features
from ndvi import calculate_ndvi
from extract import extract_stats

lon_min, lon_max = -105.694362, -105.052774
lat_min, lat_max = 39.908, 40.262785
number_days = 10
water_features = "Lakes_and_Reservoirs.geojson"

load_10m_data(lon_min, lon_max, lat_min, lat_max, number_days)

mask_water_features(water_features)

calculate_ndvi()

extract_stats()