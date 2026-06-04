from typing import Optional

from pydantic import BaseModel, Field
from datetime import date

class TransactionModel(BaseModel):
    id: int = Field(alias="id")
    transaction_date: Optional[date] = Field(default=None, alias="date")
    category: int = Field(default=0, alias="category")
    description: Optional[str] = Field(default=None, alias="description")
    withdrawal: Optional[float] = Field(default=None, alias="withdrawal")
    deposit: Optional[float] = Field(default=None, alias="deposit")