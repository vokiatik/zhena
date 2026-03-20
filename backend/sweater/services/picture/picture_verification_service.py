from sqlalchemy.orm import Session
from sweater.schemas.picture.picture_verification_scheme import VerifyRequest
from sweater.models.Retail_model import Retail

def getUnverifiedPictures(db: Session):
    return db.query(Retail).filter_by(verified=False).order_by(Retail.created_at).all()

def verifyPicture(db: Session, values: Retail):
    picture = db.query(Retail).filter_by(id=values.id).first()
    picture.retailer_clean = values.retailer_clean
    picture.advertiser_producer = values.advertiser_producer
    picture.brands_list = values.brands_list
    picture.brands_list_clean = values.brands_list_clean
    picture.ferrero_category = values.ferrero_category
    picture.ferrero_category_range = values.ferrero_category_range
    picture.ferrero_category_multibrand = values.ferrero_category_multibrand
    picture.first_screen_date = values.first_screen_date
    picture.last_screen_date = values.last_screen_date
    picture.advertisement_id = values.advertisement_id
    picture.verified = True
    db.commit()

def getUnverifiedPictureById(db: Session, picture_id: str):
    return db.query(Retail).filter_by(id=picture_id).first()