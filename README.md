**Flight Telemetry API** — A REST API built with FastAPI and SQLite that ingests real-time aircraft telemetry data, supports filtering by ICAO, altitude, and speed, and automatically detects anomalous altitude drops.

**Tech Stack** 
* Python
* FastAPI
* SQLModel
* SQLite

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
```

**Code**
```bash
http://127.0.0.1:8000/docs
```
