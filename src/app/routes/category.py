from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import SessionLocal, get_db
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_db_user
from app.db.category import Category
from app.models.category import CategoryModel
from app.models.user import UserModel

router = APIRouter(prefix="/category", tags=["Categories"])

@router.post("")
def add_category(categoryRequest: CategoryModel, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    new_category = Category(
        name=categoryRequest.name,
        description=categoryRequest.description,
        is_system=0,
        user_id=current_user.id
    )

    session.add(new_category)
    session.commit()
    # session.refresh(new_category)

    return new_category

@router.get("/{id}")
def get_category_by_id(id: int, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    category = session.get(Category, id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.user_id != current_user.id and not category.is_system:
        raise HTTPException(status_code=403, detail="You do not have permission to access this category")

    return category

@router.get("", response_model=List[CategoryModel])
def get_all_category(session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    categories = session.query(Category).filter((Category.user_id == current_user.id) | (Category.is_system == 1)).all()

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
def delete_category_by_id(id: int, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    category = session.get(Category, id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.user_id != current_user.id and not category.is_system:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this category")

    if category.is_system == True:
        raise HTTPException(status_code=402, detail="System categories cannot be deleted")

    session.delete(category)
    session.commit()

    return category

@router.put("/{id}")
def update_category_by_id(id: int, categoryRequest: CategoryModel, session: Session = Depends(get_db), current_user: UserModel = Depends(get_db_user)):
    category = session.get(Category, id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.user_id != current_user.id and not category.is_system:
        raise HTTPException(status_code=403, detail="You do not have permission to update this category")

    if category.is_system == True:
        raise HTTPException(status_code=402, detail="System categories cannot be updated")

    category.name = categoryRequest.name
    category.description = categoryRequest.description
    session.commit()

    return category
