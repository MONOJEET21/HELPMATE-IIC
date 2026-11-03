from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MarketplaceListing, User
from app.schemas import ListingCreate, ListingOut
from app.security import get_current_user
router = APIRouter(prefix="/api/marketplace", tags=["AgriBrain Marketplace"])

@router.get("", response_model=list[ListingOut])
def listings(search: str | None = None, db: Session = Depends(get_db)):
    q = db.query(MarketplaceListing)
    if search: q = q.filter(MarketplaceListing.title.ilike(f"%{search}%"))
    return q.order_by(MarketplaceListing.created_at.desc()).all()

@router.post("", response_model=ListingOut)
def create_listing(data: ListingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "farmer": raise HTTPException(403, "Farmer account required")
    listing = MarketplaceListing(**data.model_dump(), seller_id=user.id)
    db.add(listing); db.commit(); db.refresh(listing)
    return listing
