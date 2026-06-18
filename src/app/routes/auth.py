from fastapi import APIRouter, Depends, Request
import jwt
from app.core.database import SessionLocal

from app.core.security import get_current_user
from app.models.current_user import User
from app.models.source import SourceModel
from app.db.source import Source

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/test")
def test_auth(request: Request):
    auth_header = request.headers.get("Authorization")
   
    if not auth_header:
       return {"error": "Authorization header missing"}

    token = auth_header.split(" ")[1]

    payload = jwt.decode(token, options={"verify_signature": False})

    return payload

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return current_user