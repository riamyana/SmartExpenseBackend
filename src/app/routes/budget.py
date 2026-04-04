from fastapi import APIRouter
from app.database import SessionLocal

from app.db.budget import Budget
from app.models.budget import BudgetModel

router = APIRouter()

@router.post("/budget")
def add_budget(budgetRequest: BudgetModel):
    db = SessionLocal()

    # Todo: start tomorrow from here. Check if budget is categorical or not. Write logic accordingly.
    
    # Note: A global budget can be either categorical or non-categorical. Can not save both in the same time for simplicity.
    if budgetRequest.is_categorical:
        pass

    if budgetRequest.is_recurring:
        existing = db.query(Budget).filter(Budget.is_recurring == True, Budget.category_id == budgetRequest.category_id).first()

        if existing:
            if existing.category_id is not None and existing.category_id > 0:
                pass

    budget = Budget(
        amount=budgetRequest.amount,
        month=budgetRequest.month,
        is_recurring=budgetRequest.is_recurring
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return budget

@router.get("/budget/{id}")
def get_budget_by_id(id: int):
    db = SessionLocal()
    try:
        budget = db.get(Budget, id)

        if not budget:
            return {"error": "Source not found"}

        return budget
    finally:
        db.close()
