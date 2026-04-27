from app.handlers.budgets.budget_base import BudgetBase, BudgetResponse
from app.db.budget import Budget


class CategoricalBudgetRecurring(BudgetBase):
    def execute(self) -> BudgetResponse:
        existing_recurrings = self.get_existing_recurring_budget()

        if existing_recurrings and self.is_categorical_budget_exceeds_total(existing_recurrings):
            return BudgetResponse(success=False)

        budget = self.get_existing_category_recurring_budget()
        if budget:
            self.update_budget(budget)
            return BudgetResponse(id=budget.id, success=True)

        id = self.save_new_budget()
        return BudgetResponse(id=id, success=True)

    def get_existing_category_recurring_budget(self):
        return self.session.query(Budget).filter(
            Budget.category_id == self.budget_request.category_id,
            Budget.is_recurring == True
        ).first()

    @property
    def description(self):
        return "Categorical Budget Recurring"
