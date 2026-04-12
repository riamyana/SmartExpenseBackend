from app.handlers.budgets.budget_base import BudgetBase, BudgetResponse
from app.db.budget import Budget


class TotalBudgetMonthly(BudgetBase):
    def execute(self) -> BudgetResponse:
        existing_monthly = self.get_existing_total_monthly_budget()

        if existing_monthly:
            self.update_budget(existing_monthly)
            return BudgetResponse(id=existing_monthly.id, success=True)

        id = self.save_new_budget()
        return BudgetResponse(id=id, success=True)

    def get_existing_total_monthly_budget(self):
        return self.session.query(Budget).filter(
            Budget.month == self.budget_request.month,
            Budget.category_id == None,
            Budget.is_recurring == False,
        ).first()
    
    @property
    def description(self):
        self.logger.debug("Total Budget Monthly")
