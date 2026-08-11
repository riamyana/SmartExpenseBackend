from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import datetime

class ExpenseModel(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    withdrawal: float = Field(default=None, alias="withdrawal")
    deposit: float = Field(default=None, alias="deposit")
    description: str = Field(default=None, alias="description")
    category_id: int = Field(default=None, alias="category_id")
    category_name: str = Field(default=None, alias="category_name")
    source_id: int = Field(default=None, alias="sourceId")
    merchant_id: int = Field(default=None, alias="merchantId")
    transaction_date: datetime = Field(default=None, alias="transaction_date")


class ExpenseResponse(BaseModel):
    total: int = Field(default=None, alias="total")
    page: int = Field(default=None, alias="page")
    page_size: int = Field(default=None, alias="page_size")
    data: List[ExpenseModel] = Field(default=None, alias="data")