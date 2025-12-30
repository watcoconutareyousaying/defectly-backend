from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError

from app.db.session import get_db
from app.core.config import settings
from app.crud import user as user_crud, token as token_crud


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,
                                 algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            jti = payload.get("jti")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # You’d need a DB session here, usually sync blocking is bad for middleware
        db = next(get_db())
        db_token = token_crud.get_active_token(db, jti)
        user = user_crud.get_user_by_email(db, email)
        if not db_token or not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user or token")

        request.state.user = user  # attach user for route usage
        return await call_next(request)
