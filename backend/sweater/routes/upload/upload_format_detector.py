import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session


from sweater.routes.upload.read_csv_with_fallbacks import read_csv_with_fallbacks
from sweater.services.process.process_instance_service import create_process_instance

from sweater.models.Dictionaries.detector_format_comparison import DetectorFormatComparison
from sweater.services.dictionaries.dictionaries_service import  get_retailer_id_by_name, get_format_id

def parse_format_file(filename: str, content: bytes) -> pd.DataFrame:
    lower_name = filename.lower()

    if lower_name.endswith(".csv"):
        df = read_csv_with_fallbacks(content)
    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
        df = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("Unsupported file type. Only CSV, XLSX and XLS are allowed.")

    df.columns = [str(col).strip() for col in df.columns]

    required_columns = ["retailer", "format_detector", "format"]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    return df[required_columns].copy()

def save_format_dataframe_to_db(db: Session, df, process_id=None) -> int:
    rows = []
    for _, row in df.iterrows():
        retailer = row.get("retailer")
        format_detector = row.get("format_detector")
        format = row.get("format")

        retailer_id = get_retailer_id_by_name(db, retailer) if retailer else None
        format_detector = str(format_detector).strip().upper() if format_detector is not None else None

        format = str(format).strip().upper() if format is not None else None

        if not format or not format_detector or not retailer_id:
            continue

        format_id = get_format_id(db, retailer_id, format, {})  
        
        print(f"[REFERENCE UPLOAD DEBUG] Processing row with format='{format}', format_detector='{format_detector}' retailer_id='{retailer_id}'")

        ecom_format = db.query(DetectorFormatComparison).filter(DetectorFormatComparison.format_id == format_id, DetectorFormatComparison.retailer_id == retailer_id).first()
        
        if not ecom_format:
            db_type = DetectorFormatComparison(format_id=format_id, retailer_id=retailer_id, detector_format=format_detector)
            db.add(db_type)
            db.commit()
            db.refresh(db_type)
            ecom_format = db_type

        db_row = DetectorFormatComparison(
            format_id=format_id,
            retailer_id=retailer_id,
            detector_format=format_detector,
        )
        rows.append(db_row)

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
