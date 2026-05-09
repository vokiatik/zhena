import math

from sqlalchemy.orm import Session
from sweater.models.process_settings.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.process_settings.Picture_attribute_reference_type_model import PictureAttributeReferenceType
from sweater.models.Dictionaries.funnel_stage import FunnelStage

def get_retailer_id_by_name(db: Session, retailer_name):
    if retailer_name is None:
        return None

    ref_type = db.query(PictureAttributeReferenceType).filter(
        PictureAttributeReferenceType.reference_type_name == 'RETAILER_CLEAN'
    ).first()
    if not ref_type:
        return None

    row = db.query(PictureAttributeReference).filter(
        PictureAttributeReference.reference_value == retailer_name,
        PictureAttributeReference.reference_type_id == ref_type.id,
    ).first()
    return row.id if row else None


def get_funnel_stage_id_by_name(db: Session, funnel_stage_name: str):
    funnel_stage = db.query(FunnelStage).filter(FunnelStage.funnel_stage_name == funnel_stage_name).first()
    return funnel_stage.id if funnel_stage else None