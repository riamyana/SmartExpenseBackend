from typing import Optional

from pydantic import BaseModel, Field

class BudgetModel(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    amount: float = Field(default=None, alias="amount")
    month: str = Field(default=None, alias="month")
    category_id: Optional[int] = Field(default=None, alias="categoryId")