import logging

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import SessionLocal, get_db

from app.db.budget import Budget
from app.models.budget import BudgetModel
from sqlalchemy.orm import Session

from app.handlers.budgets.budget_factory import get_budget_handler
from app.handlers.budgets.budget_base import BudgetBase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/budget", tags=["Budgets"])

@router.post("")
def add_budget(budgetRequest: BudgetModel, session: Session = Depends(get_db)):
    handler = get_budget_handler(session, budgetRequest)

    logger.info(f"Executing {handler.description}.")

    response = handler.execute()
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)

    return response.id

@router.get("/{id}")
def get_budget_by_id(id: int):
    db = SessionLocal()
    try:
        budget = db.get(Budget, id)

        if not budget:
            return {"error": "Source not found"}

        return budget
    finally:
        db.close()
