import os
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.user import User
from app.helpers.user_helper import create_user, get_by_auth_id
from app.models.user import UserModel
from uuid import uuid4
from jwt import PyJWKClient

security = HTTPBearer()

async def get_current_user(credentials: str = Depends(security)) -> UserModel:
    token = credentials.credentials
    keycloak_url = os.getenv('KEYCLOAK_URL')
    keycloak_realm = os.getenv('REALM')
    issuer=f"{keycloak_url}/realms/{keycloak_realm}"
    jwks_url = f"{issuer}/protocol/openid-connect/certs"
    jwks_client = PyJWKClient(jwks_url)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=["RS256"], issuer=issuer, audience="account")
        return UserModel(
            id=None,
            auth_id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
        )
    except jwt.ExpiredSignatureError as ex:
        print(ex)
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as ex:
        print(ex)
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as ex:
        print(type(ex))
        print(ex)
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_db_user(
    current_user: UserModel = Depends(
        get_current_user
    ),
    session: Session = Depends(get_db)
) -> User:

    user = get_by_auth_id(
        session,
        current_user.auth_id
    )

    if not user:
        user = create_user(
            session,
            auth_id=current_user.auth_id,
            username=current_user.username,
            email=current_user.email
        )

    return user