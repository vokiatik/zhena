import json
from io import BytesIO
from typing import Union

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles
from sweater.models.process_settings.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.process_settings.Picture_attribute_reference_type_model import PictureAttributeReferenceType
from sweater.models.retail.Retail_model import Retail
from sweater.schemas.fileUpload.file_upload_shcema import (
    ConfirmDecision,
    UploadResponse,
    ValidationRequiredResponse,
)
from sweater.services.process.process_instance_service import create_process_instance
from sweater.services.upload.attribute_validation_service import (
    apply_decisions_to_df,
    check_missing_reference_values,
    save_new_reference_values,
)

router = APIRouter(prefix="/upload", tags=["file_uploading"])

EXPECTED_COLUMNS = [
    "Ретейлер clean",
    "Advertiser (producer)",
    "Brands list",
    "Brands list clean",
    "!Категория Ферреро",
    "!Категория Ферреро  (Range категорий)",
    "!Категория Ферреро (Мультибренд категорий)",
    "Дата первого скрина",
    "Дата последнего скрина",
    "Advertisement ID",
]

# Maps original file column names → DB/model column names used in ProcessAttributes.title
FILE_COL_TO_DB_COL = {
    "Ретейлер clean": "retailer_clean",
    "Advertiser (producer)": "advertiser_producer",
    "Brands list": "brands_list",
    "Brands list clean": "brands_list_clean",
    "!Категория Ферреро": "ferrero_category",
    "!Категория Ферреро  (Range категорий)": "ferrero_category_range",
    "!Категория Ферреро (Мультибренд категорий)": "ferrero_category_multibrand",
    "Дата первого скрина": "first_screen_date",
    "Дата последнего скрина": "last_screen_date",
    "Advertisement ID": "advertisement_id",
}

def parse_retail_file(filename: str, content: bytes) -> pd.DataFrame:
    lower_name = filename.lower()

    if lower_name.endswith(".csv"):
        df = _read_csv_with_fallbacks(content)
    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
        df = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("Unsupported file type. Only CSV, XLSX and XLS are allowed.")

    df.columns = [str(col).strip() for col in df.columns]

    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    df = df[EXPECTED_COLUMNS].copy()
    df["Дата первого скрина"] = pd.to_datetime(
        df["Дата первого скрина"], errors="coerce"
    ).dt.date
    df["Дата последнего скрина"] = pd.to_datetime(
        df["Дата последнего скрина"], errors="coerce"
    ).dt.date
    df = df.where(pd.notnull(df), None)

    return df

def parse_reference_file(filename: str, content: bytes) -> pd.DataFrame:
    lower_name = filename.lower()

    if lower_name.endswith(".csv"):
        df = _read_csv_with_fallbacks(content)
    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
        df = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("Unsupported file type. Only CSV, XLSX and XLS are allowed.")

    df.columns = [str(col).strip() for col in df.columns]

    required_columns = ["value", "type"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    return df[required_columns].copy()

def _read_csv_with_fallbacks(content: bytes) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp1251", "windows-1251", "latin1"]

    last_error = None
    for encoding in encodings:
        try:
            return pd.read_csv(BytesIO(content), encoding=encoding)
        except Exception as e:
            last_error = e

    raise ValueError(f"Failed to read CSV file: {last_error}")

def save_retail_dataframe_to_db(db: Session, df, process_id=None) -> int:
    rows = []

    for _, row in df.iterrows():
        db_row = Retail(
            retailer_clean=row.get("Ретейлер clean"),
            advertiser_producer=row.get("Advertiser (producer)"),
            brands_list=row.get("Brands list"),
            brands_list_clean=row.get("Brands list clean"),
            ferrero_category=row.get("!Категория Ферреро"),
            ferrero_category_range=row.get("!Категория Ферреро  (Range категорий)"),
            ferrero_category_multibrand=row.get("!Категория Ферреро (Мультибренд категорий)"),
            first_screen_date=row.get("Дата первого скрина"),
            last_screen_date=row.get("Дата последнего скрина"),
            advertisement_id=str(row.get("Advertisement ID")) if row.get("Advertisement ID") is not None else None,
            verified=False,
            process_id=process_id,
        )
        rows.append(db_row)

    db.add_all(rows)
    db.commit()

    return len(rows)

def save_reference_dataframe_to_db(db: Session, df, process_id=None) -> int:
    rows = []
    for _, row in df.iterrows():
        reference_value = row.get("value")
        reference_presetting_type = row.get("type")

        reference_value = str(reference_value).strip().upper() if reference_value is not None else None
        reference_presetting_type = str(reference_presetting_type).strip().upper() if reference_presetting_type is not None else None

        if not reference_value or not reference_presetting_type:
            continue
        print(f"[REFERENCE UPLOAD DEBUG] Processing row with value='{reference_value}', type='{reference_presetting_type}'")
        reference_type = db.query(PictureAttributeReferenceType).filter(PictureAttributeReferenceType.reference_type_name == reference_presetting_type).first()
        
        if not reference_type:
            db_type = PictureAttributeReferenceType(reference_type_name=reference_presetting_type)
            db.add(db_type)
            db.commit()
            db.refresh(db_type)
            reference_type = db_type

        db_row = PictureAttributeReference(
            reference_value=reference_value,
            reference_type_id=reference_type.id,
        )
        rows.append(db_row)

    db.add_all(rows)
    db.commit()

    return len(rows)

def proceed_retail_file_upload(db: Session, filename: str, content: bytes, user_id: str):
    df = parse_retail_file(filename, content)

    process = create_process_instance(
        db,
        type_name="file",
        comment=filename,
        initiator_id=user_id,
    )

    inserted_rows = save_retail_dataframe_to_db(db, df, process_id=process.id)
    return inserted_rows


def proceed_retail_file_upload_with_df(db: Session, df: "pd.DataFrame", filename: str, user_id: str) -> int:
    process = create_process_instance(
        db,
        type_name="file",
        comment=filename,
        initiator_id=user_id,
    )
    return save_retail_dataframe_to_db(db, df, process_id=process.id)

def proceed_reference_file_upload(db: Session, filename: str, content: bytes, user_id: str):
    df = parse_reference_file(filename, content)

    process = create_process_instance(
        db,
        type_name="file",
        comment=filename,
        initiator_id=user_id,
    )

    inserted_rows = save_reference_dataframe_to_db(db, df, process_id=process.id)
    return inserted_rows

@router.post("/retail-file")
async def upload_retail_file(
    file: UploadFile = File(...),
    filetype: str = Form(...),
    user: dict = Depends(require_roles("admin", "marketing_specialist")),
    db: Session = Depends(get_reference_db),
):
    print(f"Received file: {file.filename}, content type: {file.content_type}, filetype: {filetype}")
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

        if filetype == "retail":
            df = parse_retail_file(file.filename, content)

            # Rename to DB column names so ProcessAttributes.title lookup works
            df_db_cols = df.rename(columns=FILE_COL_TO_DB_COL)
            missing_values, existing_by_type = check_missing_reference_values(db, df_db_cols)
            if missing_values:
                return JSONResponse(
                    status_code=200,
                    content=ValidationRequiredResponse(
                        status="needs_validation",
                        missing_values=[m.model_dump() for m in missing_values],
                        existing_values_by_type=existing_by_type,
                    ).model_dump(),
                )

            inserted_rows = proceed_retail_file_upload_with_df(db, df, file.filename, user["id"])

        elif filetype == "reference":
            inserted_rows = proceed_reference_file_upload(db, file.filename, content, user["id"])
        else:
            raise HTTPException(status_code=400, detail="Invalid file type specified.")

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


@router.post("/retail-file/confirm", response_model=UploadResponse)
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