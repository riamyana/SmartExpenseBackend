from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class BudgetResponse:
    id: int
    success: bool


class BudgetBase:
    @abstractmethod
    def execute(self) -> BudgetResponse:
        ...

    @property
    @abstractmethod
    def description(self):
        ...
