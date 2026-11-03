from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Farm, User
from app.schemas import FarmCreate, FarmOut
from app.security import get_current_user
router = APIRouter(prefix="/api/farms", tags=["AgriBrain Farms / GIS"])

@router.get("", response_model=list[FarmOut])
def my_farms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Farm).filter(Farm.owner_id == user.id).all()

@router.post("", response_model=FarmOut)
def create_farm(data: FarmCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "farmer": raise HTTPException(403, "Farmer account required")
    farm = Farm(**data.model_dump(), owner_id=user.id)
    db.add(farm); db.commit(); db.refresh(farm)
    return farm

@router.get("/map")
def map_features(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    farms = db.query(Farm).filter(Farm.owner_id == user.id).all()
    return {"type":"FeatureCollection","features":[
        {"type":"Feature","geometry":{"type":"Point","coordinates":[f.longitude,f.latitude]},
         "properties":{"id":f.id,"name":f.name,"crop":f.crop}}
        for f in farms if f.latitude is not None and f.longitude is not None
    ]}
