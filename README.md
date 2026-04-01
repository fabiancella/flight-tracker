**Flight Telemetry API** — A REST API built with FastAPI and PostgreSQL that ingests real-time aircraft telemetry data, supports filtering by ICAO, altitude, and speed, and 
automatically detects anomalous altitude drops.

**Architecture**
A local cron job runs every 5 minutes, pulling live ADS-B flight data from the OpenSky Network API and posting it to the deployed API. The API runs on an AWS EC2 instance and persists data to a PostgreSQL database hosted on AWS RDS. OpenSky blocks AWS IP ranges, so the feeder runs locally and posts to the public EC2 endpoint rather than running on the server itself.

**Tech Stack** 
* Python
* FastAPI
* SQLModel
* PostgreSQL (AWS RDS)

**Features**
* Ingest and store aircraft telemetry data
* Retrieve all telemetry records
* Filter by ICAO, Callsign, altitude range, and speed range
* Automatic anomaly detection for sudden altitude drops
* Alert storage and retrieval for flagged anomalies
* Input validation and error handling

**Setup**
```bash
git clone <repo-url>
cd flight_tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
Create a .env file in the project root with DB_PASSWORD=yourpassword before starting the server.
```

**Code**
```bash
http://127.0.0.1:8000/docs
```
