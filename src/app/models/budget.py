from typing import Optional

from pydantic import BaseModel, Field

class BudgetModel(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    amount: str = Field(default=None, alias="amount")
    month: str = Field(default=None, alias="month")
    category_id: int = Field(default=None, alias="categoryId")
    is_categorical: bool = Field(default=None, alias="isCategorical")
    is_recurring: bool = Field(default=None, alias="isRecurring")