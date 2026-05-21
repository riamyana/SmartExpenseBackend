from sqlalchemy.orm import Session

from app.db.category import Category

SYSTEM_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Salary",
    "Investment",
    "Health",
    "Entertainment",
    "Other"
]

def seed_system_categories(session: Session):

    for category_name in SYSTEM_CATEGORIES:

        exists = session.query(Category).filter(
            Category.name == category_name
        ).first()

        if not exists:
            category = Category(
                name=category_name,
                description=f"System category for {category_name}",
                is_system=True
            )

            session.add(category)

    session.commit()