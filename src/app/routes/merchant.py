from fastapi import APIRouter
from app.db.merchant import Merchant
from app.models.merchant import MerchantModel
from app.database import SessionLocal

router = APIRouter()

@router.post("/merchant")
def add_merchant(merchant: MerchantModel):
    db = SessionLocal()

    merchant = Merchant(
        name=merchant.name,
        description=merchant.description
    )

    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    return merchant

@router.get("/merchant/{id}")
def get_merchant_by_id(id: int):
    db = SessionLocal()
    try:
        source = db.get(Merchant, id)

        if not source:
            return {"error": "Source not found"}

        return source
    finally:
        db.close()
