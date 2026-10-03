from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_expenses: Decimal
    monthly_expenses: Decimal
    budget: Decimal
    budget_remaining: Decimal
    transactions: int


class MonthlyExpense(BaseModel):
    month: int
    month_name: str
    year: int
    amount: Decimal


class CategoryExpense(BaseModel):
    category_id: int | None
    category_name: str
    amount: Decimal
    percentage: Decimal


class RecentExpense(BaseModel):
    id: int
    date: date
    description: str
    category_name: str
    amount: Decimal


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    monthly_expenses: list[MonthlyExpense]
    category_expenses: list[CategoryExpense]
    recent_expenses: list[RecentExpense]