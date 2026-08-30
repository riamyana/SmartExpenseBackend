import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import SessionLocal, get_db

from app.core.security import get_db_user
from app.db.budget import Budget
from app.models.budget import BudgetModel, BudgetResponse
from sqlalchemy.orm import Session

from app.handlers.budgets.budget_factory import get_budget_handler
from app.handlers.budgets.budget_base import BudgetBase
from app.models.user import UserModel
from sqlalchemy import or_

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/budget", tags=["Budgets"])

@router.post("")
def save_budget(budgetRequest: BudgetModel, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    handler = get_budget_handler(session, budgetRequest, current_user.id)

    logger.info(f"Executing {handler.description}.")

    response = handler.execute()

    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)

    return response.id

@router.get("/{id}")
def get_budget_by_id(id: int, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    budget = session.get(Budget, id)

    if not budget:
        return {"error": "Source not found"}
    
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this budget.")

    return budget

@router.delete("/{id}")
def delete_budget_by_id(id: int, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    budget = session.get(Budget, id)

    if not budget:
        return {"error": "Source not found"}

    if budget.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this budget.")

    session.delete(budget)
    session.commit()

    return budget

@router.get("/monthly/{month}", response_model=List[BudgetResponse])
def get_budget_by_month(month: str, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    monthly_budgets = (
        session.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            or_(
                Budget.month == month,
                Budget.month.is_(None)
            )
        )
        .all()
    )

    if not monthly_budgets:
        raise HTTPException(status_code=404, detail="Monthly budgets not found")

    return [
        BudgetResponse(
            id=b.id,
            amount=b.amount,
            month=b.month,
            category_id=b.category_id,
            category_name=b.category.name if b.category else None,
            is_recurring=b.is_recurring
        )
        for b in monthly_budgets
    ]

