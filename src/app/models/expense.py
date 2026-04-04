from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime

class ExpenseModel(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    amount: float = Field(default=None, alias="amount")
    description: str = Field(default=None, alias="description")
    category_id: int = Field(default=None, alias="categoryId")
    source_id: int = Field(default=None, alias="sourceId")
    merchant_id: int = Field(default=None, alias="merchantId")
    transaction_date: datetime = Field(default=None, alias="transactionDate")