import pandas as pd
from io import BytesIO

from sqlalchemy.orm import Session
from sweater.services.process.process_instance_service import create_process_instance
from sweater.routes.upload.read_csv_with_fallbacks import read_csv_with_fallbacks


from sweater.models.retail.Retail_model import Retail, FILE_COL_TO_DB_COL, EXPECTED_COLUMNS


def parse_retail_file(filename: str, content: bytes) -> pd.DataFrame:
    lower_name = filename.lower()

    if lower_name.endswith(".csv"):
        df = read_csv_with_fallbacks(content)
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
