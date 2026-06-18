from fastapi import APIRouter
from app.db.merchant import Merchant
from app.models.merchant import MerchantModel
from app.core.database import SessionLocal

router = APIRouter(prefix="/merchant", tags=["Merchant"])

@router.post("")
def add_merchant(merchantRequest: MerchantModel):
    db = SessionLocal()

    merchant = Merchant(
        name=merchantRequest.name,
        description=merchantRequest.description
    )

    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    return merchant

@router.get("/{id}")
def get_merchant_by_id(id: int):
    db = SessionLocal()
    try:
        source = db.get(Merchant, id)

        if not source:
            return {"error": "Source not found"}

        return source
    finally:
        db.close()
