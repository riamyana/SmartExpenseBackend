from fastapi import APIRouter
from models.expense import ExpenseRequest
from db.expense import Expense
from database import SessionLocal

router = APIRouter()

@router.post("/expenses")
def add_expense(expense: ExpenseRequest):
    db = SessionLocal()

    new_expense = Expense(
        transaction_date=expense.transaction_date,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        source=expense.source,
        merchant=expense.merchant
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

@router.get("/expenses/{id}")
def get_expense(id: int):
    db = SessionLocal()
    try:
        expense = db.get(Expense, id)

        if not expense:
            return {"error": "Expense not found"}

        return expense
    finally:
        db.close()