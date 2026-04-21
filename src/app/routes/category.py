from typing import List

from fastapi import APIRouter, Depends
from app.db.database import SessionLocal, get_db
from sqlalchemy.orm import Session

from app.db.category import Category
from app.models.category import CategoryModel

router = APIRouter(prefix="/category", tags=["Categories"])

@router.post("")
def add_category(categoryRequest: CategoryModel):
    db = SessionLocal()

    new_category = Category(
        name=categoryRequest.name,
        description=categoryRequest.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@router.get("/{id}")
def get_category_by_id(id: int):
    db = SessionLocal()
    try:
        category = db.get(Category, id)

        if not category:
            return {"error": "Category not found"}

        return category
    finally:
        db.close()

@router.get("", response_model=List[CategoryModel])
def get_all_category(session: Session = Depends(get_db)):
    categories = session.query(Category).all()

    if not categories:
        return {"error": "Categories not found"}

    return [
        CategoryModel(
            id=c.id,
            name=c.name,
            description=c.description
        )
        for c in categories
    ]