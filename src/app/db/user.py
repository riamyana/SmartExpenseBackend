from sqlalchemy import UUID, Column, String, DateTime
from app.core.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    auth_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    category = relationship("Category", back_populates="user")
