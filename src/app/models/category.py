from typing import Optional

from pydantic import BaseModel, Field

class CategoryModel(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    name: str = Field(default=None, alias="name")
    description: str = Field(default=None, alias="description")