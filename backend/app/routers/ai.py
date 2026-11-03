from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.models import User
from app.security import get_current_user
from app.ai import predict_crop_disease
router = APIRouter(prefix="/api/ai", tags=["AgriBrain AI"])

@router.post("/disease-detection")
async def disease_detection(image: UploadFile = File(...), user: User = Depends(get_current_user)):
    if user.role != "farmer": raise HTTPException(403, "Farmer account required")
    if image.content_type not in {"image/jpeg","image/png","image/webp"}:
        raise HTTPException(415, "Upload JPG, PNG or WEBP")
    try: return await predict_crop_disease(image)
    except ValueError as exc: raise HTTPException(413, str(exc))
