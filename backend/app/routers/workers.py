from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WorkerProfile, User
from app.schemas import WorkerProfileUpdate
from app.security import get_current_user

router=APIRouter(prefix="/api/workers",tags=["HelpMate Worker Profiles"])

@router.get("/me")
def my_profile(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user.role!="worker": raise HTTPException(403,"Worker account required")
    p=db.query(WorkerProfile).filter_by(user_id=user.id).first()
    return {"name":user.name,"phone":user.phone,**({k:getattr(p,k) for k in ["skills","experience_years","preferred_location","expected_salary","bio"]} if p else {})}

@router.put("/me")
def update_profile(data:WorkerProfileUpdate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user.role!="worker": raise HTTPException(403,"Worker account required")
    p=db.query(WorkerProfile).filter_by(user_id=user.id).first()
    if not p: p=WorkerProfile(user_id=user.id);db.add(p)
    for k,v in data.model_dump().items(): setattr(p,k,v)
    db.commit();db.refresh(p)
    return {"message":"Worker profile saved","profile_id":p.id}

@router.get("")
def discover_workers(location:str|None=None,skill:str|None=None,db:Session=Depends(get_db)):
    q=db.query(WorkerProfile,User).join(User,WorkerProfile.user_id==User.id)
    if location:q=q.filter(WorkerProfile.preferred_location.ilike(f"%{location}%"))
    if skill:q=q.filter(WorkerProfile.skills.ilike(f"%{skill}%"))
    return [{"id":u.id,"name":u.name,"phone":u.phone,"skills":p.skills,"experience_years":p.experience_years,"preferred_location":p.preferred_location,"expected_salary":p.expected_salary,"bio":p.bio} for p,u in q.limit(100).all()]
