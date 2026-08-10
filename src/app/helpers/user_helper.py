from sqlalchemy.orm import Session

from app.db.user import User

def get_by_auth_id(session: Session, auth_id: str) -> User:
    return session.query(User).filter(User.auth_id == auth_id).first()

def create_user(session: Session, auth_id: str, username: str, email: str) -> User:
    user = User(
        auth_id=auth_id,
        username=username,
        email=email
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user