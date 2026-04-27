import os

from sqlalchemy.orm import Session
from app.handlers.statements.pdf_statement import PDFStatement
from app.handlers.statements.statement_base import StatementBase, StatementModel



def get_statement_handler(session: Session, request: StatementModel) -> StatementBase:
    filename = request.file.filename
    
    key = filename.split(".")[-1].lower()

    handler_map = {
        "pdf": PDFStatement(session, request),
        "csv": NotImplementedError(),
        "xls": NotImplementedError(),
    }

    handler_class: StatementBase = handler_map.get(key)

    if not handler_class:
        raise ValueError("Invalid statement request")

    return handler_class