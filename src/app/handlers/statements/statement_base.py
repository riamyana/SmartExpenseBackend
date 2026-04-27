from abc import abstractmethod
from dataclasses import dataclass
import logging
from typing import List, Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from app.models.transactions import TransactionModel



@dataclass
class StatementModel:
    file: UploadFile = Field()


class StatementResponse(BaseModel):
    transactions: Optional[List[TransactionModel]] = None
    success: bool = False
    message: Optional[str] = "Something went wrong while adding budget."


class StatementBase:
    def __init__(self, session: Session, request: StatementModel):
        self.session = session
        self.request = request
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Processing {self.description}")

    @abstractmethod
    def process(self) -> StatementResponse:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...
