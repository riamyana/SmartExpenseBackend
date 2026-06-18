from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import jwt

from app.core.database import get_db
from app.db.user import User
from app.helpers.user_helper import create_user, get_by_auth_id
from app.models.current_user import User
from uuid import uuid4

security = HTTPBearer()

async def get_current_user(credentials: str = Depends(security)) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return User(
            id="",
            auth_id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_db_user(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
) -> User:

    user = get_by_auth_id(
        db,
        current_user.auth_id
    )

    if not user:
        user = create_user(
            db,
            id=str(uuid4()),
            auth_id=current_user.auth_id,
            username=current_user.username,
            email=current_user.email
        )

    return user