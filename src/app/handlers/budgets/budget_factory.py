from app.handlers.budgets.categorical_budget_recurring_handler import CategoricalBudgetRecurring
from app.handlers.budgets.total_budget_recurring_handler import TotalBudgetRecurring
from app.handlers.budgets.total_budget_monthly_handler import TotalBudgetMonthly
from app.handlers.budgets.categorical_budget_monthly_handler import CategoricalBudgetMonthly
from app.models.budget import BudgetModel
from app.handlers.budgets.budget_base import BudgetBase
from sqlalchemy.orm import Session


def get_budget_handler(session: Session, request: BudgetModel) -> BudgetBase:
    key = (
        request.category_id is not None,
        request.month is not None
    )

    handler_map = {
        (False, False): TotalBudgetRecurring(session, request),
        (False, True): TotalBudgetMonthly(session, request),
        (True, False): CategoricalBudgetRecurring(session, request),
        (True, True): CategoricalBudgetMonthly(session, request),
    }

    handler_class: BudgetBase = handler_map.get(key)

    if not handler_class:
        raise ValueError("Invalid budget request")

    return handler_class