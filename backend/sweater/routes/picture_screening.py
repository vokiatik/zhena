import uuid

from fastapi import APIRouter, Depends, HTTPException
from requests import Session

from sweater.database.database import get_db
from sweater.routes.auth import get_current_user
from sweater.services.picture.picture_verification_service import getUnverifiedPictureById, getUnverifiedPictures, verifyPicture

router = APIRouter(prefix="/pictures", tags=["pictures"])
from sweater.schemas.picture.picture_verification_scheme import VerifyRequest

# ── Routes ───────────────────────────────────────────────────────────

@router.get("/{role}")
async def get_unverified_pictures(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    role: str = None
):
    pictures = getUnverifiedPictures(db)
    print(role)
    results = []
    for p in pictures:
        item: dict = {k: (str(v) if isinstance(v, uuid.UUID) else v) for k, v in dict(p).items()}
        results.append(item)
    return results


@router.post("/verify")
async def verify_picture(
    body: VerifyRequest,
    db: Session = Depends(get_db),
):
    picture_id = body.id
    picture = getUnverifiedPictureById(db, picture_id)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    
    picture_dict = dict(picture)
    for key, value in body.extra.items():
        if key in picture_dict:
            setattr(picture, key, value)

    verifyPicture(db, picture)
    
    return {"ok": True}
