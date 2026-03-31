from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime)
    amount = Column(Float)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=True)
    merchant_id = Column(Integer, ForeignKey("merchant.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    time_stamp = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="expenses")
    source = relationship("Source", back_populates="expenses")
    merchant = relationship("Merchant", back_populates="expenses")