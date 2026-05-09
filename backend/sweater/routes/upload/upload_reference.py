import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session
from sweater.routes.upload.read_csv_with_fallbacks import read_csv_with_fallbacks

from sweater.models.process_settings.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.process_settings.Picture_attribute_reference_type_model import PictureAttributeReferenceType
from sweater.services.process.process_instance_service import create_process_instance

def parse_reference_file(filename: str, content: bytes) -> pd.DataFrame:
    lower_name = filename.lower()

    if lower_name.endswith(".csv"):
        df = read_csv_with_fallbacks(content)
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
