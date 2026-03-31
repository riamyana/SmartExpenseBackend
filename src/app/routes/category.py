from fastapi import APIRouter
from app.database import SessionLocal

from app.db.category import Category
from app.models.category import CategoryModel

router = APIRouter()

@router.post("/category")
def add_category(category: CategoryModel):
    db = SessionLocal()

    new_category = Category(
        name=category.name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@router.get("/category/{id}")
def get_category_by_id(id: int):
    db = SessionLocal()
    try:
        category = db.get(Category, id)

        if not category:
            return {"error": "Category not found"}

        return category
    finally:
        db.close()
