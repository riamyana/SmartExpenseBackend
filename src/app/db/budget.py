from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, DateTime
from datetime import datetime
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column( UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    amount = Column(Float)
    month = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="budgets")
    user = relationship("User", back_populates="budgets")
