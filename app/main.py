from fastapi import FastAPI
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select

app = FastAPI()

# ---- DATABASE SETUP ----
DATABASE_URL = "sqlite:///app/flight.db"

engine = create_engine(DATABASE_URL, echo=True)

# Class to store telemetry, DO NOT CHANGE CLASS NAME. NEW DB WILL BE CREATED
class StoredTelemetry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    icao: str 
    timestamp: datetime
    latitude: float
    longitude: float
    altitude_ft: int
    groundspeed_kt: int

# Class for inputting telemetry
class InputTelemetry(SQLModel):
    icao: str
    timestamp: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude_ft: int = Field(ge=0)
    groundspeed_kt: int = Field(ge=0, le=700)

# Model to send alert data to database
class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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

# Checks for anomalies in altitude or speed   
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
            timestamp = data.timestamp,
            latitude = data.latitude,
            longitude = data.longitude,
            altitude_ft = data.altitude_ft,
            groundspeed_kt = data.groundspeed_kt
        )
        prev_icao = session.exec(select(StoredTelemetry).where(
            StoredTelemetry.icao == data.icao
        ).order_by(StoredTelemetry.timestamp.desc())).first()
        
            
        session.add(db_telemetry)
        session.commit()
        session.refresh(db_telemetry)
        
        if prev_icao is None:
            pass
        else:
            is_anomaly = check_anomaly(prev_icao, db_telemetry)
            if is_anomaly:
                alert = Alert(
                    icao = data.icao,
                    timestamp = data.timestamp,
                    anomaly_type = "Altitude drop",
                    details = f"Altitude dropped from {prev_icao.altitude_ft}ft to {data.altitude_ft}ft"
                )
                session.add(alert)
                session.commit()
        
        return db_telemetry

            
# Display all telemetry
@app.get("/telemetry", response_model=list[StoredTelemetry])
def get_all_telemetry():
    with Session(engine) as session:
        statement = select(StoredTelemetry)
        results = session.exec(statement).all()
        return results

# GET route filtered by ICAO    
@app.get("/telemetry/{icao}", response_model=list[StoredTelemetry])
def get_icao_telemetry(icao: str):
    with Session(engine) as session:
        statement = select(StoredTelemetry).where(
            StoredTelemetry.icao == icao
        )
        results = session.exec(statement).all()
        return results

# GET route sorted by altitude
@app.get("/telemetry/altitude/", response_model=list[StoredTelemetry])
def filtered_altitudes(min_altitude: int | None = None, max_altitude: int | None = None):
    with Session(engine) as session:
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
        return results
    
# GET route sorted by speed
@app.get("/telemetry/speed/", response_model=list[StoredTelemetry])
def filtered_speed(min_speed: int | None = None, max_speed: int | None = None):
    with Session(engine) as session:
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
        return results

# GET route for alerts / anomalies
@app.get("/telemetry/alert/", response_model=list[Alert])
def get_alert():
    with Session(engine) as session:
        alert = select(Alert)
        results = session.exec(alert).all()  
        return results