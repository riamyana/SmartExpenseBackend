from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    month = Column(String, nullable=True)
    category_id = Column(String, nullable=True)
    is_recurring = Column(Integer, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="expenses")
