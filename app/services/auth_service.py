import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.security import create_access_token
from app.core.config import settings
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.otp_service import create_otp, send_otp_email
from app.crud import token


async def register_user(db: Session, user_data: UserCreate) -> dict:
    # Check if user exists
    if user_crud.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = user_crud.create_user(db, user_data)

    # Generate and send OTP
    otp = create_otp(db, user.id)
    email_sent = await send_otp_email(user.email, otp.otp_code)

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email"
        )

    return {
        "message": "User registered successfully. Please check your email for OTP verification.",
        "user_id": user.id
    }


def login_user(db: Session, user_data: UserLogin) -> Token:
    user = user_crud.authenticate_user(db, user_data.email, user_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active or not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not verified. Please verify your email first.",
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    jti = str(uuid.uuid4())
    
    access_token = create_access_token(
        subject=user.email, 
        expires_delta=access_token_expires,
        jti=jti
    )
    
    token.create_token(
        db=db,
        jti=jti,
        user_id=user.id,
        expires_at=datetime.utcnow() + access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
