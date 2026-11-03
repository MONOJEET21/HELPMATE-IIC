from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

async def predict_crop_disease(file: UploadFile) -> dict:
    # DEMO PLACEHOLDER: replace with preprocessing and inference from a validated trained model.
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "crop.jpg").suffix[:12] or ".jpg"
    content = await file.read()
    if len(content) > 8 * 1024 * 1024:
        raise ValueError("Image must be 8 MB or smaller")
    (Path(settings.upload_dir) / f"crop_upload{suffix}").write_bytes(content)
    return {
        "status": "demo_placeholder",
        "message": "Image received. No trained disease model is connected yet.",
        "prediction": None,
        "confidence": None,
        "next_step": "Connect and validate the AgriBrain model before using this for farm decisions."
    }
