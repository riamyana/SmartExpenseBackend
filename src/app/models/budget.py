from typing import List, Optional

from pydantic import BaseModel, Field

class BudgetModel(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    amount: float = Field(default=None, alias="amount")
    month: Optional[str] = Field(default=None, alias="month")
    category_id: Optional[int] = Field(default=None, alias="category_id")
    is_recurring: bool = Field(default=None, alias="is_recurring")


class BudgetResponse(BudgetModel):
    category_name: Optional[str] = Field(default=None, alias="category_name")
