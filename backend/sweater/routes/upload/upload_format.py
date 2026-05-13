import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session


from sweater.routes.upload.read_csv_with_fallbacks import read_csv_with_fallbacks
from sweater.services.process.process_instance_service import create_process_instance

from sweater.models.Dictionaries.format import Format
from sweater.services.dictionaries.dictionaries_service import get_funnel_stage_id_by_name, get_retailer_id_by_name

def parse_format_file(filename: str, content: bytes) -> pd.DataFrame:
    lower_name = filename.lower()

    if lower_name.endswith(".csv"):
        df = read_csv_with_fallbacks(content)
    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
        df = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("Unsupported file type. Only CSV, XLSX and XLS are allowed.")

    df.columns = [str(col).strip() for col in df.columns]

    required_columns = ["retailer", "format", "funnel_stage", "sov"]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    return df[required_columns].copy()

def save_format_dataframe_to_db(db: Session, df, process_id=None) -> int:
    rows = []
    print(df)
    for _, row in df.iterrows():
        retailer = row.get("retailer")
        format = row.get("format")
        funnel_stage = row.get("funnel_stage")
        sov = row.get("sov")

        if format is None or pd.isna(format) or funnel_stage is None or retailer is None:
            print(f"[REFERENCE UPLOAD DEBUG] Skipping row due to missing required fields: {row.to_dict()}")
            continue
        retailer_id = get_retailer_id_by_name(db, retailer) if retailer else None
        funnel_stage_id = get_funnel_stage_id_by_name(db, funnel_stage) if funnel_stage else None

        format = str(format).strip().upper() if format is not None else None
        sov = str(sov).strip().upper() if sov is not None else None

        
        print(f"[REFERENCE UPLOAD DEBUG] Processing row with format='{format}', sov='{sov}' retailer_id='{retailer_id}', funnel_stage_id='{funnel_stage_id}'")
        if not format or not sov or not retailer_id or not funnel_stage_id:
            continue
        ecom_format = db.query(Format).filter(Format.format == format, Format.retailer_id == retailer_id).first()
        
        if not ecom_format:
            db_type = Format(format=format, retailer_id=retailer_id, funnel_stage_id=funnel_stage_id, sov=sov)
            db.add(db_type)
            db.commit()
            db.refresh(db_type)
            ecom_format = db_type

        db_row = Format(
            format=format,
            retailer_id=retailer_id,
            funnel_stage_id=funnel_stage_id,
            sov=sov,
        )
        rows.append(db_row)
    print (f"[REFERENCE UPLOAD DEBUG] Total valid rows to insert: {len(rows)}")
    db.add_all(rows)
    db.commit()

    return len(rows)

def proceed_format_file_upload(db: Session, filename: str, content: bytes, user_id: str):
    df = parse_format_file(filename, content)

    process = create_process_instance(
        db,
        type_name="file",
        comment=filename,
        initiator_id=user_id,
    )

    inserted_rows = save_format_dataframe_to_db(db, df, process_id=process.id)
    return inserted_rows
