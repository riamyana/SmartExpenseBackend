from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    user_id = Column( UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    is_system = Column(Integer, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    user = relationship("User", back_populates="category")