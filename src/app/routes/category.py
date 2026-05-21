from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.db.database import SessionLocal, get_db
from sqlalchemy.orm import Session

from app.db.category import Category
from app.models.category import CategoryModel

router = APIRouter(prefix="/category", tags=["Categories"])

@router.post("")
def add_category(categoryRequest: CategoryModel, session: Session = Depends(get_db)):
    new_category = Category(
        name=categoryRequest.name,
        description=categoryRequest.description,
        is_system=0
    )

    session.add(new_category)
    session.commit()
    session.refresh(new_category)

    return new_category

@router.get("/{id}")
def get_category_by_id(id: int, session: Session = Depends(get_db)):
    category = session.get(Category, id)

    if not category:
        return {"error": "Category not found"}

    return category

@router.get("", response_model=List[CategoryModel])
def get_all_category(session: Session = Depends(get_db)):
    categories = session.query(Category).all()

    if not categories:
        return []

    return [
        CategoryModel(
            id=c.id,
            name=c.name,
            description=c.description,
            is_system=c.is_system
        )
        for c in categories
    ]

@router.delete("/{id}")
def delete_category_by_id(id: int, session: Session = Depends(get_db)):
    category = session.get(Category, id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.is_system == True:
        raise HTTPException(status_code=402, detail="System categories cannot be deleted")

    session.delete(category)
    session.commit()

    return category

@router.put("/{id}")
def update_category_by_id(id: int, categoryRequest: CategoryModel, session: Session = Depends(get_db)):
    category = session.get(Category, id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.is_system == True:
        raise HTTPException(status_code=402, detail="System categories cannot be updated")

    category.name = categoryRequest.name
    category.description = categoryRequest.description
    session.commit()

    return category
