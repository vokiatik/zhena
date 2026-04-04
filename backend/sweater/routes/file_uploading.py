from fastapi import APIRouter, Depends, Form, HTTPException

from sweater.models.process_settings.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.process_settings.Picture_attribute_reference_type_model import PictureAttributeReferenceType
from sweater.models.retail.Retail_model import Retail
from sweater.schemas.fileUpload.file_upload_shcema import UploadResponse
from sweater.database.references_db import get_reference_db

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles
from sweater.services.process.process_instance_service import create_process_instance

from io import BytesIO
import pandas as pd

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

    required_columns = ["reference_value", "reference_presetting_type"]
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
        reference_value = row.get("reference_value")
        reference_presetting_type = row.get("reference_presetting_type")

        if not reference_value or not reference_presetting_type:
            continue

        reference_type = db.query(PictureAttributeReferenceType).filter(PictureAttributeReferenceType.reference_value == reference_presetting_type).first()
        
        if not reference_type:
            db_type = PictureAttributeReferenceType(reference_value=reference_presetting_type)
            db.add(db_type)
            db.commit()
            db.refresh(db_type)
            reference_type = db_type

        db_row = PictureAttributeReference(
            reference_value=reference_value,
            reference_value_presetting_type_id=reference_type.id,
            process_id=process_id,
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

@router.post("/retail-file", response_model=UploadResponse)
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
            inserted_rows = proceed_retail_file_upload(db, file.filename, content, user["id"])
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