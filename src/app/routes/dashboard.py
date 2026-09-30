import calendar
from decimal import Decimal
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db

from app.core.security import get_db_user
from app.db.budget import Budget
from app.db.expense import Expense
from sqlalchemy.orm import Session

from app.models.dashboard import CategoryExpense, DashboardResponse, DashboardSummary, MonthlyExpense, RecentExpense
from app.models.user import UserModel
from sqlalchemy import and_, extract, or_

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("monthly/{year_month}", response_model=DashboardResponse)
def get_dashboard_data_by_month_year(year_month: str, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    monthly_budget = (
        session.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            or_(
                Budget.month == year_month,
                Budget.month.is_(None)
            )
        )
        .all()
    )

    if not monthly_budget:
        raise HTTPException(status_code=404, detail="Monthly budgets not found")

    year, month = map(int, year_month.split("-"))

    expenses = (
        session.query(Expense)
        .filter(
            Expense.user_id == current_user.id,
            extract("year", Expense.transaction_date) == year,
            extract("month", Expense.transaction_date) == month
        )
        .all()
    )

    if not expenses:
        raise HTTPException(status_code=404, detail="Expenses not found")

    # Generate last 6 months including selected month
    months = []

    for i in range(5, -1, -1):
        m = month - i
        y = year

        while m <= 0:
            m += 12
            y -= 1

        months.append((y, m))

    # Build filter for the 6 months
    month_filters = [
        and_(
            extract("year", Expense.transaction_date) == y,
            extract("month", Expense.transaction_date) == m
        )
        for y, m in months
    ]

    # Get all transactions for the last 6 months
    transactions = (
        session.query(Expense)
        .filter(
            Expense.user_id == current_user.id,
            or_(*month_filters)
        )
        .all()
    )

    # Initialize all months with 0
    monthly_expenses = {
        (y, m): Decimal("0")
        for y, m in months
    }

    # Calculate monthly expenses
    for transaction in transactions:
        if transaction.withdrawal is not None:
            key = (
                transaction.transaction_date.year,
                transaction.transaction_date.month
            )

            monthly_expenses[key] += Decimal(
                str(transaction.withdrawal)
            )

    monthly_expense_data: List[MonthlyExpense] = []

    for y, m in months:
        monthly_expense_data.append(
            MonthlyExpense(
                year=y,
                month=m,
                month_name=calendar.month_name[m],
                amount=monthly_expenses[(y, m)]
            )
        )

    category_expenses = {}

    for expense in expenses:
        if expense.withdrawal is None:
            continue

        category_id = expense.category_id
        category_name = expense.category.name

        if category_id not in category_expenses:
            category_expenses[category_id] = {
                "category_id": category_id,
                "category_name": category_name,
                "amount": Decimal("0")
            }

        category_expenses[category_id]["amount"] += Decimal(
            str(expense.withdrawal)
        )

    category_data = []

    total_monthly_expenses = sum(
        (Decimal(str(expense.withdrawal)) for expense in expenses),
        Decimal("0")
    )

    for data in category_expenses.values():
        percentage = (
            (data["amount"] / total_monthly_expenses) * 100
            if total_monthly_expenses
            else Decimal("0")
        )

        category_data.append(
            CategoryExpense(
                category_id=data["category_id"],
                category_name=data["category_name"],
                amount=data["amount"],
                percentage=percentage
            )
        )

    recent_expenses = sorted(
        expenses,
        key=lambda expense: expense.transaction_date,
        reverse=True
    )[:5]

    recent_expense_data = [
        RecentExpense(
            id=expense.id,
            date=expense.transaction_date.date(),
            description=expense.description,
            category_name=expense.category.name,
            amount=Decimal(str(expense.withdrawal))
        )
        for expense in recent_expenses
        if expense.withdrawal is not None
    ]

    budget = next(
        (b for b in monthly_budget if b.month == year_month and b.category_id is None),
        next(
            (b for b in monthly_budget if b.month is None and b.category_id is None),
            None
        )
    )

    budget_amount = budget.amount if budget else 0
    budget_amount = Decimal(str(budget_amount))
    budget_remaining = budget_amount - total_monthly_expenses
    transactions = len(expenses)

    summary = DashboardSummary(
        total_expenses=Decimal("0"),
        monthly_expenses=total_monthly_expenses,
        budget=budget_amount,
        budget_remaining=budget_remaining,
        transactions=transactions
    )

    response = DashboardResponse(
        summary=summary,
        monthly_expenses=monthly_expense_data,
        category_expenses=category_data,
        recent_expenses=recent_expense_data
    )

    return response
