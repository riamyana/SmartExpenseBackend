from app.handlers.budgets.categorical_budget_recurring_handler import CategoricalBudgetRecurring
from app.handlers.budgets.total_budget_recurring_handler import TotalBudgetRecurring
from app.handlers.budgets.total_budget_monthly_handler import TotalBudgetMonthly
from app.handlers.budgets.categorical_budget_monthly_handler import CategoricalBudgetMonthly


def get_budget_handler(request):
    key = (
        request.category_id is not None,
        request.month is not None
    )

    handler_map = {
        (False, False): TotalBudgetRecurring,
        (False, True): TotalBudgetMonthly,
        (True, False): CategoricalBudgetRecurring,
        (True, True): CategoricalBudgetMonthly,
    }

    handler_class = handler_map.get(key)

    if not handler_class:
        raise ValueError("Invalid budget request")

    return handler_class()