from pydantic import BaseModel
from datetime import datetime

class ExpenseRequest(BaseModel):
    amount: float
    description: str
    category: int
    source: int
    merchant: int
    transaction_date: datetime