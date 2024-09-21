# 1. Inladen modules
import requests # HTTP interface
import json     # JSON interface
import psycopg2 # PostgreSQL interface
import geopandas as gpd
from shapely.geometry import Point

# 2. Definiëren fiellablocaties create gdf
gdf = gpd.GeoDataFrame(
    {
        "fieldlab_id": ["21","24","23","25","20","22"],
        "geometry": [
            Point(51.961508262070055, 5.235743804590197),
            Point(51.68645729348589, 5.285388976536408),
            Point(51.590966086371395, 4.315422061885681),
            Point(51.91320718815669, 4.468969628663211),
            Point(51.83836891366415, 4.621807565770182),
            Point(51.90732854994922, 4.940968379523468),
        ],
    },         
     crs="EPSG:4326"
     )



# 3.  HTTP headers
headers = {
    'Content-Type': 'application/json; charset:UTF-8',
}

# 4. Openen database connectie
conn = psycopg2.connect("host=dilab-sb.postgres.database.azure.com dbname=sensoren user=sensordummy password=J2v6mT5m3LGvc6uA port=5432")
cur = conn.cursor()

# 5. Per meteostation:
for index, row in gdf.iterrows():
    fieldlab_id = row['fieldlab_id']

    # 6. Samenstellen HTTP request
    url1 = f'https://api.open-meteo.com/v1/forecast?latitude={row["geometry"].x}&longitude={row["geometry"].y}&timezone=CET&current=temperature_2m,wind_speed_10m,rain,wind_direction_10m,surface_pressure,relativehumidity_2m,windgusts_10m,apparent_temperature'
    url2 = f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={row["geometry"].x}&longitude={row["geometry"].y}&timezone=CET&current=pm10,pm2_5'

    # 7. Uitvoeren HTTP request
    response = requests.get(url1, headers=headers)
    response2 = requests.get(url2, headers=headers)

    if response.status_code == 200 and response2.status_code == 200:
        # 8. Extract and insert data from the JSON responses
        feature1 = response.json()["current"]
        feature2 = response2.json()["current"]

        # 9. Opstellen SQL insert statement
        sql = 'insert into Meteo_gegevens(fieldlab_id, time_stamp, act_temp, wind_snel, wind_richt, regen_hv, lucht_vocht, lucht_druk, pm10, pm2_5) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        # 10. Waardes uit JSON response koppelen aan en uitvoeren van SQL statement
        cur.execute(sql, (
            fieldlab_id,
            feature1["time"],
            feature1["temperature_2m"],
            feature1["wind_speed_10m"],
            feature1["wind_direction_10m"],
            feature1["rain"],
            feature1["relativehumidity_2m"],
            feature1["surface_pressure"],
            feature2["pm10"],
            feature2["pm2_5"]
        ))
    else:
        print('Request failed with error ' + str(response.status_code))
        print('Request failed with error ' + str(response2.status_code))

# 11. Commit
conn.commit()

# 12. Sluiten van database
conn.close()