from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime

class ExpenseModel(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    amount: float = Field(default=None, alias="amount")
    description: str = Field(default=None, alias="description")
    category: int = Field(default=None, alias="category")
    source: int = Field(default=None, alias="source")
    merchant: int = Field(default=None, alias="merchant")
    transaction_date: datetime = Field(default=None, alias="transactionDate")