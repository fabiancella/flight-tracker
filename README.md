**Flight Telemetry API** — A REST API built with FastAPI and PostgreSQL that ingests real-time aircraft telemetry data, supports filtering by ICAO, altitude, and speed, and 
automatically detects anomalous altitude drops.

**Frontend Link** -
https://fabiancella.github.io/flight-tracker/

**API Base URL** - 
http://api.aeroping.net/telemetry

**Architecture** -
CURRENT USING OPENSKY NETWORK
OpenSky blocks AWS IP ranges, so the feeder currently runs locally and posts telemetry data to the deployed API over HTTPS. The API is hosted on an AWS EC2 instance behind Nginx, exposed through `https://api.aeroping.net`, and persists data to a PostgreSQL database hosted on AWS RDS. The frontend is hosted on GitHub Pages and calls the HTTPS API domain from the browser to display aircraft on an interactive map.

**Tech Stack** 
* Python
* JavaScript
* FastAPI
* SQLModel
* PostgreSQL (AWS RDS)
* AWS EC2
* Nginx
* Let's Encrypt SSL
* Cloudflare DNS
* Leaflet.js

**Features**
* Ingest and store aircraft telemetry data
* Retrieve all telemetry records
* Filter by ICAO, Callsign, altitude range, and speed range
* Automatic anomaly detection for sudden altitude drops
* Alert storage and retrieval for flagged anomalies
* Input validation and error handling
* Interactive map with live flight positions and heading-based plane rotation
* Callsign search to find specific flights
* Adjustable flight count display

**Setup**
```bash
git clone <repo-url>
cd flight_tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**API Docs**
```bash
http://127.0.0.1:8000/docs
```
