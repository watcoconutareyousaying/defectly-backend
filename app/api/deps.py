from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.core.config import settings
from app.crud import user as user_crud
from app.crud import token as token_crud
from app.models.user import User

# Use HTTP Bearer Auth scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        # Decode the token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        jti = payload.get("jti")

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not email or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is still valid (not revoked/expired)
    db_token = token_crud.get_active_token(db, jti)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user and validate status
    user = user_crud.get_user_by_email(db, email=email)
    if user is None or not user.is_active or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive or unverified user"
        )

    return user


def get_client_ip(request: Request) -> str:
    # Get IP address from the request object
    return request.client.host  # type: ignore


def get_user_agent(request: Request) -> str:
    # Get user-agent header
    return request.headers.get("user-agent", "")
