from typing import Optional

from pydantic import BaseModel, Field
from datetime import date

from uuid import UUID

class UserModel(BaseModel):
    id: UUID | None = None
    auth_id: str
    username: str
    email: str | None = None