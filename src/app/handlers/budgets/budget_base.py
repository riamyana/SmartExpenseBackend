from abc import abstractmethod
from dataclasses import dataclass
import logging
from typing import List, Optional

from pydantic import Field

from app.models.budget import BudgetModel
from app.db.budget import Budget
from sqlalchemy.orm import Session



@dataclass
class BudgetResponse:
    id: Optional[int] = Field(default=None, alias="id")
    success: Optional[bool] = Field(default=False, alias="success")
    message: Optional[str] = Field(default="Something went wront while adding budget.", alias="message")


class BudgetBase:
    def __init__(self, session: Session, budget_request: BudgetModel):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.budget_request = budget_request
        self.logger.debug(f"Processing {self.description}")

    @abstractmethod
    def execute(self) -> BudgetResponse:
        ...

    @property
    @abstractmethod
    def description(self):
        ...

    @property
    def is_monthly_budget(self):
        return self.budget_request.month is not None

    def get_existing_month_budget(self):
        if not self.is_monthly_budget:
            return None

        existing = self.session.query(Budget).filter(
            Budget.month == self.budget_request.month,
        )

        return existing

    def get_existing_recurring_budget(self):
        existing = self.session.query(Budget).filter(
            Budget.month == None,
            Budget.is_recurring == True
        )

        return existing

    def is_categorical_budget_exceeds_total(self, existing: List[Budget]):
        total_budget = None
        total_categorical = self.budget_request.amount
        for budget in existing:
            if budget.month != self.budget_request.month:
                continue

            if budget.category_id == self.budget_request.category_id:
                continue
            elif budget.category_id is None:
                total_budget = budget.amount
            else:
                total_categorical += budget.amount

        self.logger.debug(f"Total budget:{total_budget}, Total categorical: {total_categorical}.")
        if not total_budget or total_budget >= total_categorical:
            return False

        self.logger.debug("Invalid total budget exceeded.")
        return True
                    

    def save_new_budget(self):
        new_budget = Budget(
            amount=self.budget_request.amount,
            month=self.budget_request.month,
            category_id=self.budget_request.category_id,
            is_recurring=self.budget_request.month is None,
        )

        self.session.add(new_budget)
        self.session.commit()
        self.session.refresh(new_budget)

        self.logger.debug(f"Saved budget successfully. Id: {new_budget.id}")
        return new_budget.id

    def update_budget(self, existing_budget: Budget):
        existing_budget.amount = self.budget_request.amount
        self.session.commit()
        self.session.refresh(existing_budget)
        self.logger.debug(f"Updated budget successfully to amount: {self.budget_request.amount}.")