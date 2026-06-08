from datetime import datetime
from io import StringIO
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.handlers.statements.statement_base import StatementModel
from app.handlers.statements.statement_factory import get_statement_handler
from app.models.expense import ExpenseModel
from app.db.expense import Expense
from app.db.database import SessionLocal, get_db
import csv
from sqlalchemy.orm import Session

from app.models.transactions import TransactionModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post("")
def add_expense(expense: ExpenseModel):
    db = SessionLocal()

    new_expense = Expense(
        transaction_date=expense.transaction_date,
        withdrawal=expense.withdrawal if expense.withdrawal else 0,
        deposit=expense.deposit if expense.deposit else 0,
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

@router.get("/{id}")
def get_expense_by_id(id: int):
    db = SessionLocal()
    try:
        expense = db.get(Expense, id)

        if not expense:
            return {"error": "Expense not found"}

        return expense
    finally:
        db.close()

@router.delete("/{id}")
def delete_expense_by_id(id: int):
    db = SessionLocal()
    try:
        expense = db.get(Expense, id)

        if not expense:
            return {"error": "Expense not found"}

        db.delete(expense)
        db.commit()

        return {"message": "Expense deleted successfully"}
    finally:
        db.close()

@router.put("/{id}")
def update_expense_by_id(id: int, expenseRequest: ExpenseModel):
    db = SessionLocal()
    try:
        expense = db.get(Expense, id)

        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        expense.transaction_date = expenseRequest.transaction_date
        expense.withdrawal = expenseRequest.withdrawal if expenseRequest.withdrawal else 0
        expense.deposit = expenseRequest.deposit if expenseRequest.deposit else 0
        expense.description = expenseRequest.description
        expense.category_id = expenseRequest.category_id
        expense.source_id = expenseRequest.source_id
        expense.merchant_id = expenseRequest.merchant_id

        db.commit()
        db.refresh(expense)

        return {"message": "Expense updated successfully", "expense": expense}
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
            withdrawal=float(row["amount"]) if row["amount"] else 0,
            deposit=0,
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

@router.post("/statements/upload", response_model=List[TransactionModel])
def upload_statements(file: UploadFile = File(...), session: Session = Depends(get_db)):
    request = StatementModel(
        file = file
    )
    handler = get_statement_handler(session, request)

    logger.info(f"Executing {handler.description}.")

    response = handler.process()

    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)

    return response.transactions

@router.post("/save")
def save_expenses(data: List[TransactionModel], session: Session = Depends(get_db)):
    for transaction in data:
        new_category = Expense(
            transaction_date=transaction.transaction_date,
            withdrawal=transaction.withdrawal if transaction.withdrawal else 0,
            deposit=transaction.deposit if transaction.deposit else 0,
            description=transaction.description,
            category_id=transaction.category,
            source_id=None,
            merchant_id=None
        )
        session.add(new_category)

    session.commit()
    return {"success": True}

@router.get("/yearly")
def get_yearly_expenses(year: int, page: int = 1, limit: int = 10):
    db = SessionLocal()

    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    offset = (page - 1) * limit

    expenses = (
        db.query(Expense)
        .filter(
            Expense.transaction_date >= start_date,
            Expense.transaction_date < end_date
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    data = [
        ExpenseModel(
            id=e.id,
            transaction_date=e.transaction_date,
            withdrawal=e.withdrawal if e.withdrawal else 0,
            deposit=e.deposit if e.deposit else 0,
            description=e.description,
            # TODO: Update Foreign keys for category, source, merchant, etc.
            category_id=None,
            source_id=None,
            merchant=None
        )
        for e in expenses
    ]
    
    total = (
        db.query(Expense)
        .filter(
            Expense.transaction_date >= start_date,
            Expense.transaction_date < end_date
        )
        .count()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }