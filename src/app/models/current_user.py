from typing import Optional

from pydantic import BaseModel, Field
from datetime import date

class User(BaseModel):
    id: str
    auth_id: str
    username: str
    email: str | None = None