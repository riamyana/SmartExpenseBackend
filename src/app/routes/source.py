from fastapi import APIRouter
from app.database import SessionLocal

from app.models.source import SourceModel
from app.db.source import Source

router = APIRouter()

@router.post("/source")
def add_source(source: SourceModel):
    db = SessionLocal()

    source = Source(
        name=source.name,
        description=source.description
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source

@router.get("/source/{id}")
def get_source_by_id(id: int):
    db = SessionLocal()
    try:
        source = db.get(Source, id)

        if not source:
            return {"error": "Source not found"}

        return source
    finally:
        db.close()
