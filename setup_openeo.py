import openeo

connection = openeo.connect("openeo.dataspace.copernicus.eu")

try:       
    connection = connection.authenticate_oidc(
        max_poll_time=60,  
    )
    
    print("✅ Authentication successful")
    
except Exception as e:
    print(f"❌ Authentication failed:d {e}")