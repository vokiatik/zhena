import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from sweater.routes.upload.upload_format import proceed_format_file_upload
from sweater.routes.upload.upload_reference import proceed_reference_file_upload

from sweater.routes.upload.upload_format_detector import parse_format_file, save_format_dataframe_to_db
from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles

from sweater.schemas.fileUpload.file_upload_shcema import (
    UploadResponse,
)

router = APIRouter(prefix="/upload", tags=["file_uploading"])

@router.post("/{type}")
async def upload_file(
    type: str,
    file: UploadFile = File(...),
    user: dict = Depends(require_roles("admin", "marketing_specialist")),
    db: Session = Depends(get_reference_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is missing.")

    lower_name = file.filename.lower()
    if not (lower_name.endswith(".csv") or lower_name.endswith(".xlsx") or lower_name.endswith(".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only CSV, XLSX and XLS are allowed.",
        )
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if type == "reference":
            inserted_rows = proceed_reference_file_upload(db, file.filename, content, user["id"])
        elif type == "ecom_format":
            inserted_rows = proceed_format_file_upload(db, file.filename, content, user["id"])
        elif type == "ecom_format_for_detector":
            df = parse_format_file(file.filename, content)
            inserted_rows = save_format_dataframe_to_db(db, df)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown upload type: {type}")

        return UploadResponse(
            ok=True,
            message="File uploaded and saved successfully.",
            inserted_rows=inserted_rows,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")