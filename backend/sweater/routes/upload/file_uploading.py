import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from sweater.models.retail.Retail_model import FILE_COL_TO_DB_COL
from sweater.routes.upload.upload_format import proceed_format_file_upload
from sweater.routes.upload.upload_reference import proceed_reference_file_upload
from sweater.routes.upload.upload_retail import (
    parse_retail_file,
    proceed_retail_file_upload,
    proceed_retail_file_upload_with_df,
)
from sweater.routes.upload.upload_format_detector import parse_format_file, save_format_dataframe_to_db
from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles

from sweater.schemas.fileUpload.file_upload_shcema import (
    ConfirmDecision,
    UploadResponse,
)
from sweater.services.upload.attribute_validation_service import (
    apply_decisions_to_df,
    save_new_reference_values,
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

        if type == "retail":
            inserted_rows = proceed_retail_file_upload(db, file.filename, content, user["id"])
        elif type == "reference":
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

@router.post("/retail/confirm", response_model=UploadResponse)
async def confirm_retail_file_upload(
    file: UploadFile = File(...),
    filetype: str = Form(...),
    decisions: str = Form(...),
    user: dict = Depends(require_roles("admin", "marketing_specialist")),
    db: Session = Depends(get_reference_db),
):
    """
    Re-upload the same file together with the user's decisions about missing
    reference values.  Saves new reference values, applies replacements in the
    DataFrame, then proceeds with the normal pipeline.
    """
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

        try:
            raw_decisions = json.loads(decisions)
            decision_list = [ConfirmDecision(**d) for d in raw_decisions]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid decisions payload.")

        if filetype == "retail":
            df = parse_retail_file(file.filename, content)
            save_new_reference_values(db, decision_list)
            # Decisions reference DB column names — apply on renamed df, then rename back
            db_col_to_file_col = {v: k for k, v in FILE_COL_TO_DB_COL.items()}
            df_db_cols = df.rename(columns=FILE_COL_TO_DB_COL)
            df_db_cols = apply_decisions_to_df(df_db_cols, decision_list)
            df = df_db_cols.rename(columns=db_col_to_file_col)
            inserted_rows = proceed_retail_file_upload_with_df(db, df, file.filename, user["id"])
        else:
            raise HTTPException(status_code=400, detail="Confirm endpoint only supports retail filetype.")

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