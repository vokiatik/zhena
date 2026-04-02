from requests import Session
from fastapi import APIRouter, Depends, Form, HTTPException

from sweater.models.retail.Retail_model import Retail
from sweater.schemas.fileUpload.file_upload_shcema import UploadResponse
from sweater.database.base_db import get_db

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles

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

def parse_uploaded_file(filename: str, content: bytes) -> pd.DataFrame:
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


def _read_csv_with_fallbacks(content: bytes) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp1251", "windows-1251", "latin1"]

    last_error = None
    for encoding in encodings:
        try:
            return pd.read_csv(BytesIO(content), encoding=encoding)
        except Exception as e:
            last_error = e

    raise ValueError(f"Failed to read CSV file: {last_error}")

def save_dataframe_to_db(db: Session, df) -> int:
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
        )
        rows.append(db_row)

    db.add_all(rows)
    db.commit()

    return len(rows)


@router.post("/retail-file", response_model=UploadResponse)
async def upload_retail_file(
    file: UploadFile = File(...),
    filetype: str = Form(...),
    user: dict = Depends(require_roles("admin", "marketing_specialist")),
    db: Session = Depends(get_db),
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

        df = parse_uploaded_file(file.filename, content)
        inserted_rows = save_dataframe_to_db(db, df)

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