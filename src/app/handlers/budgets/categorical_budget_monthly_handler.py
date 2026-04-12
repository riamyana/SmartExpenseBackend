from app.handlers.budgets.budget_base import BudgetBase, BudgetResponse
from app.db.budget import Budget


class CategoricalBudgetMonthly(BudgetBase):
    def execute(self) -> BudgetResponse:
        existing_monthly = self.get_existing_month_budget()

        if existing_monthly and self.is_categorical_budget_exceeds_total(existing_monthly):
            return BudgetResponse(success=False, message="Categorical budget exceeds the total budget limit.")

        budget = self.get_existing_category_monthly_budget()
        if budget:
            self.update_budget(budget)
            return BudgetResponse(id=budget.id, success=True)

        id = self.save_new_budget()
        return BudgetResponse(id=id, success=True)

    def get_existing_category_monthly_budget(self):
        return self.session.query(Budget).filter(
            Budget.category_id == self.budget_request.category_id,
            Budget.month == self.budget_request.month
        ).first()

    @property
    def description(self):
        self.logger.debug("Categorical Budget Monthly")
