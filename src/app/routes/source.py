from fastapi import APIRouter
from app.core.database import SessionLocal

from app.models.source import SourceModel
from app.db.source import Source

router = APIRouter(prefix="/source", tags=["Source"])

@router.post("")
def add_source(sourceRequest: SourceModel):
    db = SessionLocal()

    source = Source(
        name=sourceRequest.name,
        description=sourceRequest.description
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source

@router.get("/{id}")
def get_source_by_id(id: int):
    db = SessionLocal()
    try:
        source = db.get(Source, id)

        if not source:
            return {"error": "Source not found"}

        return source
    finally:
        db.close()
