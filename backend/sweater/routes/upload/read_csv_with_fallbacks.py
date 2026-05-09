
import pandas as pd
from io import BytesIO

def read_csv_with_fallbacks(content: bytes) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp1251", "windows-1251", "latin1"]

    last_error = None
    for encoding in encodings:
        try:
            return pd.read_csv(BytesIO(content), encoding=encoding)
        except Exception as e:
            last_error = e

    raise ValueError(f"Failed to read CSV file: {last_error}")
