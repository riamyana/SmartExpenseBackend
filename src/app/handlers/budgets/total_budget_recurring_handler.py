from app.handlers.budgets.budget_base import BudgetBase, BudgetResponse
from app.db.budget import Budget


class TotalBudgetRecurring(BudgetBase):
    def execute(self) -> BudgetResponse:
        existing_recurrings = self.get_existing_recurring_budget()
        is_below_allocation, existing_monthly = self.is_total_budget_below_category_allocation(existing_recurrings)

        if existing_recurrings and is_below_allocation:
            return BudgetResponse(success=False, message="The total of all recurring categorical budgets exceeds the total recurring budget.")

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