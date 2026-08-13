from datetime import datetime, timezone
import requests

def normalize_plane(plane, timestamp):
    if plane.get('lon') is None or plane.get('lat') is None or plane.get('gs') is None or plane.get('true_heading') is None or plane.get('hex') is None or plane.get('alt_baro') is None:
        return None
    
    callsign = plane.get('flight')   
    if callsign is None:
        callsign = "Unknown"
    
    altitude = plane.get('alt_baro')
    if altitude == "ground":
        altitude = 0 
    
    clean_data = {
        "icao" : plane["hex"],
        "callsign": callsign.strip(),
        "timestamp" : datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).isoformat(),
        "longitude" : plane["lon"],
        "latitude" : plane["lat"],
        "altitude_ft" : altitude,
        "groundspeed_kt" : plane["gs"],  
        "heading" : plane["true_heading"],
    }
    
    return clean_data

AIRPLANES_LIVE_URL = "https://api.airplanes.live/v2/point/27.6648/-81.5158/250"

response = requests.get(AIRPLANES_LIVE_URL)
data = response.json()

API_URL = "https://api.aeroping.net/telemetry"

for plane in data["ac"]:
    payload = normalize_plane(plane, data["now"])
    
    if payload is None:
        continue
    
    response = requests.post(API_URL, json=payload)

print("worked")
