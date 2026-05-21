from typing import Optional

from pydantic import BaseModel, Field

class CategoryModel(BaseModel):
    id: Optional[int] = Field(default=None, serialization_alias="id")
    name: str = Field(default=None, serialization_alias="name")
    description: str = Field(default=None, serialization_alias="description")
    is_system: bool = Field(default=False, serialization_alias="isSystem")