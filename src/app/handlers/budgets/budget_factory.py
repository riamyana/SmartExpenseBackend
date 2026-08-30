from app.handlers.budgets.categorical_budget_recurring_handler import CategoricalBudgetRecurring
from app.handlers.budgets.total_budget_recurring_handler import TotalBudgetRecurring
from app.handlers.budgets.total_budget_monthly_handler import TotalBudgetMonthly
from app.handlers.budgets.categorical_budget_monthly_handler import CategoricalBudgetMonthly
from app.models.budget import BudgetModel
from app.handlers.budgets.budget_base import BudgetBase
from sqlalchemy.orm import Session
from uuid import UUID


def get_budget_handler(session: Session, request: BudgetModel, user_id: UUID) -> BudgetBase:
    key = (
        request.category_id is not None,
        request.month is not None
    )

    handler_map = {
        (False, False): TotalBudgetRecurring(session, request, user_id),
        (False, True): TotalBudgetMonthly(session, request, user_id),
        (True, False): CategoricalBudgetRecurring(session, request, user_id),
        (True, True): CategoricalBudgetMonthly(session, request, user_id),
    }

    handler_class: BudgetBase = handler_map.get(key)

    if not handler_class:
        raise ValueError("Invalid budget request")

    return handler_class