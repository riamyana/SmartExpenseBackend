from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime)
    amount = Column(Float)
    category = Column(String)
    description = Column(String)
    source = Column(String)
    merchant = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    time_stamp = Column(DateTime, default=datetime.utcnow)