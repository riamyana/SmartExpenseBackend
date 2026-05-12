from pydantic import BaseModel, Field
from datetime import date

class TransactionModel(BaseModel):
    id: int = Field(alias="id")
    transaction_date: date = Field(default=None, alias="date")
    description: str = Field(default=None, alias="description")
    withdrawal: float = Field(default=None, alias="withdrawal")
    deposit: float = Field(default=None, alias="deposit")