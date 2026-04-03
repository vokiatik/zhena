from sqlalchemy.orm import Session
from sweater.models.retail.Retail_model import Retail


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