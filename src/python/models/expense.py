from pydantic import BaseModel
from datetime import datetime

class ExpenseRequest(BaseModel):
    amount: float
    category: str
    description: str
    source: str
    merchant: str
    transaction_date: datetime