from datetime import datetime
from io import StringIO

from fastapi import APIRouter, UploadFile, File
from models.expense import ExpenseRequest
from db.expense import Expense
from database import SessionLocal
import csv

router = APIRouter()

@router.post("/expenses")
def add_expense(expense: ExpenseRequest):
    db = SessionLocal()

    new_expense = Expense(
        transaction_date=expense.transaction_date,
        amount=expense.amount,
        description=expense.description,
        # TODO: Update Foreign keys for category, source, merchant, etc.
        category=None,
        source=None,
        merchant=None
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

@router.post("/upload-csv")
def upload_csv(file: UploadFile = File(...)):
    db = SessionLocal()

    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(content))

    expenses = []

    for row in csv_reader:
        expense = Expense(
            transaction_date=datetime.strptime(row["date"], "%Y-%m-%d"),
            amount=row["amount"],
            description=row["description"],
            # TODO: Update Foreign keys for category, source, merchant, etc.
            category=None,
            source=None,
            merchant=None
        )

        db.add(expense)
        expenses.append(expense)

    db.commit()

    return {"message": "CSV uploaded", "count": len(expenses)}