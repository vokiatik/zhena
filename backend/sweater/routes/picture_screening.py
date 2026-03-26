import uuid

from fastapi import APIRouter, Depends, HTTPException
from requests import Session

from sweater.database.base_db import get_db
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
    return pictures


@router.post("/verify")
async def verify_picture(
    body: VerifyRequest,
    db: Session = Depends(get_db),
):
    picture_id = body.id
    picture = getUnverifiedPictureById(db, picture_id)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    
    for key, value in body.extra.items():
        setattr(picture, key, value)

    print(picture)
    verifyPicture(db, picture)
    
    return {"ok": True}

@router.post("/unverify")
async def unverify_picture(
    body: VerifyRequest,
    db: Session = Depends(get_db),
):
    picture_id = body.id
    picture = getUnverifiedPictureById(db, picture_id)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    
    for key, value in body.extra.items():
        setattr(picture, key, value)

    print(picture)
    unverify_picture(db, picture)
    
    return {"ok": True}
