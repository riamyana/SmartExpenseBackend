from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(DateTime)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    expenses = relationship("Expense", back_populates="merchant")