from datetime import datetime, timezone
import requests

OPENSKY_URL = "https://opensky-network.org/api/states/all"
PARAMS = {
    "lamin" : 24.0,
    "lomin" : -87.0,
    "lamax" : 31.0,
    "lomax" : -80.0,
}

response = requests.get(OPENSKY_URL, params=PARAMS)
data = response.json()

API_URL = "http://100.48.102.102:8000/telemetry"

for state in data["states"]:
    if state[7] is None or state[9] is None:
        continue
    
    payload = {
        "icao" : state[0],
        "callsign": state[1].strip(),
        "timestamp" : datetime.fromtimestamp(state[3], tz=timezone.utc).isoformat(),
        "longitude" : state[5],
        "latitude" : state[6],
        "altitude_ft" : state[7] * 3.281,
        "groundspeed_kt" : state[9] * 1.944,  
        "heading" : state[10]
    }
    
    response = requests.post(API_URL, json=payload)
    
    
