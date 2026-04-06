from fastapi import FastAPI, HTTPException, WebSocketException
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# ---- DATABASE SETUP ----
DATABASE_URL = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@flight-tracker-db.ce168m4ccijd.us-east-1.rds.amazonaws.com:5432/postgres?sslmode=require"
# ---- DATABASE SETUP ----

engine = create_engine(DATABASE_URL, echo=True)

# Class to store telemetry, DO NOT CHANGE CLASS NAME. NEW DB WILL BE CREATED
class StoredTelemetry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    icao: str 
    callsign: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude_ft: float
    groundspeed_kt: float
    heading: float

# Class for inputting telemetry
class InputTelemetry(SQLModel):
    icao: str
    callsign: str
    timestamp: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude_ft: float = Field(ge=0)
    groundspeed_kt: float = Field(ge=0, le=700)
    heading: float

# Model to send alert data to database
class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    callsign: str
    icao: str
    timestamp: datetime
    anomaly_type: str
    details: str
    
# ---- CREATE TABLES ----
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Checks for anomalies in altitude  
def check_anomaly(previous, current):
    altitude_drop = 3000
    recorded_drop = previous.altitude_ft - current.altitude_ft
    if recorded_drop >= altitude_drop:
        return True
    else:
        return False
    
    
# ---- ROUTES ----
@app.post("/telemetry", response_model=StoredTelemetry)
def ingest_telemetry(data: InputTelemetry):
    with Session(engine) as session:
        db_telemetry = StoredTelemetry(
            icao = data.icao,
            callsign = data.callsign,
            timestamp = data.timestamp,
            latitude = data.latitude,
            longitude = data.longitude,
            altitude_ft = data.altitude_ft,
            groundspeed_kt = data.groundspeed_kt,
            heading = data.heading
        )
        prev_icao = session.exec(select(StoredTelemetry).where(
            StoredTelemetry.icao == data.icao
        ).order_by(StoredTelemetry.timestamp.desc())).first()
        
            
        try:
            session.add(db_telemetry)
            session.commit()
            session.refresh(db_telemetry)
        except Exception:
            raise HTTPException(status_code=500, detail="Could not save telemetry")
        
        if prev_icao is None:
            pass
        else:
            is_anomaly = check_anomaly(prev_icao, db_telemetry)
            if is_anomaly:
                alert = Alert(
                    icao = data.icao,
                    callsign = data.callsign,
                    timestamp = data.timestamp,
                    anomaly_type = "Altitude drop",
                    details = f"Altitude dropped from {prev_icao.altitude_ft}ft to {data.altitude_ft}ft"
                )
                try:
                    session.add(alert)
                    session.commit()
                except Exception:
                    raise HTTPException(status_code=500, detail="Could not save alert")
                
        return db_telemetry
            
# Sort telemetry by timestamp
@app.get("/telemetry", response_model=list[StoredTelemetry])
def get_all_telemetry(offset: int = 0, limit: int = 10, sort: str = "desc"):
    with Session(engine) as session:
        if sort != "asc" and sort != "desc":
            raise HTTPException(status_code=400, detail="Invalid request")
         
        if sort == "asc":
            ordering = StoredTelemetry.timestamp
            statement = select(StoredTelemetry
            ).order_by(ordering).offset(offset).limit(limit)
        
        elif sort == "desc":
            ordering = StoredTelemetry.timestamp.desc()
            statement = select(StoredTelemetry
            ).order_by(ordering).offset(offset).limit(limit)
        
        results = session.exec(statement).all()
        return results

# GET route filtered by ICAO    
@app.get("/telemetry/icao/{icao}", response_model=list[StoredTelemetry])
def get_icao_telemetry(icao: str):
    with Session(engine) as session:
        statement = select(StoredTelemetry).where(
            StoredTelemetry.icao == icao
        )
        results = session.exec(statement).all()
        if not results:
            raise HTTPException(status_code=404, detail="ICAO not found")
        return results    
    
# GET route filtered by callsign
@app.get("/telemetry/callsign/{callsign}", response_model=list[StoredTelemetry])
def get_callsign_telemetry(callsign: str):
    with Session(engine) as session:
        statement = select(StoredTelemetry).where(
            StoredTelemetry.callsign == callsign
        ).order_by(StoredTelemetry.timestamp.desc())
        
        results = session.exec(statement).all()
        if not results:
            raise HTTPException(status_code=404, detail="Callsign not found")
        return results
 

# GET route sorted by altitude
@app.get("/telemetry/altitude/", response_model=list[StoredTelemetry])
def filtered_altitudes(min_altitude: Optional[int], max_altitude: Optional[int]):
    with Session(engine) as session:
        if min_altitude is not None and max_altitude is not None and min_altitude > max_altitude:
            raise HTTPException(status_code=400, detail="Invalid request, minimum altitude greater than maximum altitude")
        
        statement = select(StoredTelemetry)
        
        if min_altitude is not None:
            statement = statement.where(
                StoredTelemetry.altitude_ft >= min_altitude
            )
            
        if max_altitude is not None:
            statement = statement.where(
                StoredTelemetry.altitude_ft <= max_altitude
            )
        
        results = session.exec(statement).all()
        if not results:
            raise HTTPException(status_code=404, detail="No flight found within range")    
        return results
    
# GET route sorted by speed
@app.get("/telemetry/speed/", response_model=list[StoredTelemetry])
def filtered_speed(min_speed: Optional[int], max_speed: Optional[int]):
    with Session(engine) as session:
        if min_speed is not None and max_speed is not None and min_speed > max_speed:
            raise HTTPException(status_code=400, detail="Invalid request, minimum speed is greater than maximum speed")
        
        statement = select(StoredTelemetry)
        
        if min_speed is not None:
            statement = statement.where(
                StoredTelemetry.groundspeed_kt >= min_speed
            )
        
        if max_speed is not None:
            statement = statement.where(
                StoredTelemetry.groundspeed_kt <= max_speed
            )
        
        results = session.exec(statement).all()
        if not results:
            raise HTTPException(status_code=404, detail="No flight found within range")
        return results

# GET route for alerts / anomalies
@app.get("/telemetry/alert/", response_model=list[Alert])
def get_alert():
    with Session(engine) as session:
        alert = select(Alert)
        results = session.exec(alert).all()  
        if not results:
            raise HTTPException(status_code=404, detail="No alerts found")
        return results

# check server status  
@app.get("/health")
def health_check():
    health = {"status": "ok"}
    return health