from app.handlers.budgets.budget_base import BudgetBase, BudgetResponse
from app.db.budget import Budget


class TotalBudgetRecurring(BudgetBase):
    def execute(self) -> BudgetResponse:
        existing_monthly = self.get_existing_total_monthly_recurring_budget()

        if existing_monthly:
            self.update_budget(existing_monthly)
            return BudgetResponse(id=existing_monthly.id, success=True)

        id = self.save_new_budget()
        return BudgetResponse(id=id, success=True)

    def get_existing_total_monthly_recurring_budget(self):
        return self.session.query(Budget).filter(
            Budget.month == None,
            Budget.category_id == None,
            Budget.is_recurring == True,
            Budget.user_id == self.user_id,
        ).first()

    @property
    def description(self):
        return "Total Budget Recurring"