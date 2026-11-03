import json
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import get_db
from app.models import SensorReading, Farm, User, DeviceCommand
from app.schemas import SensorInput, SensorOut, DeviceCommandCreate, DeviceCommandOut
from app.security import get_current_user

router = APIRouter(prefix="/api/sensors", tags=["AgriBrain IoT"])

def check_device(key):
    if not key or key != settings.device_ingest_key:
        raise HTTPException(401, "Invalid device key")

@router.post("/ingest", response_model=SensorOut)
def ingest(data: SensorInput, x_device_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    check_device(x_device_key)
    if data.farm_id and not db.get(Farm, data.farm_id): raise HTTPException(404, "Farm not found")
    reading = SensorReading(**data.model_dump())
    db.add(reading); db.commit(); db.refresh(reading)
    return reading

@router.get("/latest", response_model=list[SensorOut])
def latest(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ids = [f.id for f in db.query(Farm).filter(Farm.owner_id == user.id).all()]
    if not ids: return []
    return db.query(SensorReading).filter(SensorReading.farm_id.in_(ids)).order_by(SensorReading.created_at.desc()).limit(100).all()

@router.post("/commands", response_model=DeviceCommandOut)
def create_command(data: DeviceCommandCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "farmer": raise HTTPException(403, "Farmer account required")
    cmd = DeviceCommand(device_id=data.device_id, command=data.command,
                        payload=json.dumps(data.payload), created_by=user.id)
    db.add(cmd); db.commit(); db.refresh(cmd)
    return cmd

@router.get("/devices/{device_id}/commands")
def poll_commands(device_id: str, x_device_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    check_device(x_device_key)
    rows = db.query(DeviceCommand).filter_by(device_id=device_id, status="pending").order_by(DeviceCommand.created_at.asc()).limit(10).all()
    result=[]
    for row in rows:
        row.status="sent"
        result.append({"id":row.id,"command":row.command,"payload":json.loads(row.payload or "{}")})
    db.commit()
    return {"commands":result}

@router.post("/devices/{device_id}/commands/{command_id}/ack")
def acknowledge(device_id: str, command_id: int, x_device_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    check_device(x_device_key)
    row=db.query(DeviceCommand).filter_by(id=command_id,device_id=device_id).first()
    if not row: raise HTTPException(404,"Command not found")
    row.status="acknowledged"; row.acknowledged_at=datetime.utcnow(); db.commit()
    return {"status":"acknowledged","command_id":command_id}
