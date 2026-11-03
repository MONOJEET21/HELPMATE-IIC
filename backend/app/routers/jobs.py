from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, JobApplication, User
from app.schemas import JobCreate, JobOut, ApplicationCreate
from app.security import get_current_user
router = APIRouter(prefix="/api/jobs", tags=["HelpMate Jobs"])

@router.get("", response_model=list[JobOut])
def list_jobs(search: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Job)
    if search: q = q.filter(Job.title.ilike(f"%{search}%") | Job.location.ilike(f"%{search}%"))
    if category: q = q.filter(Job.category == category)
    return q.order_by(Job.created_at.desc()).all()

@router.post("", response_model=JobOut)
def create_job(data: JobCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "customer": raise HTTPException(403, "Only customer accounts can post jobs")
    item = Job(**data.model_dump(), owner_id=user.id)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.post("/{job_id}/apply")
def apply(job_id: int, data: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "worker": raise HTTPException(403, "Only worker accounts can apply")
    if not db.get(Job, job_id): raise HTTPException(404, "Job not found")
    if db.query(JobApplication).filter_by(job_id=job_id, applicant_id=user.id).first():
        raise HTTPException(409, "Already applied")
    item = JobApplication(job_id=job_id, applicant_id=user.id, message=data.message)
    db.add(item); db.commit(); db.refresh(item)
    return {"message": "Application submitted", "application_id": item.id}
