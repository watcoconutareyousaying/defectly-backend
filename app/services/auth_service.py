import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.security import create_access_token, get_password_hash
from app.core.config import settings
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserLogin, Token, ForgotPasswordRequest, ResetPasswordRequest
from app.services.otp_service import create_otp, send_otp_email, send_password_reset_email, send_password_reset_success_email
from app.crud import token
from app.models.otp import OTP


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
    email_sent = send_otp_email(user.email, otp.otp_code)

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email"
        )

    return {
        "message": "User registered successfully. Please check your email for OTP verification.",
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
        expires_at=datetime.now(timezone.utc) + access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


async def forgot_password(db: Session, data: ForgotPasswordRequest):
    user = user_crud.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = create_otp(db, user.id)
    email_sent = await send_password_reset_email(user.email, otp.otp_code)

    if not email_sent:
        raise HTTPException(
            status_code=500, detail="Failed to send reset email")

    return {"message": "Password reset OTP sent to email"}


async def reset_password(db: Session, data: ResetPasswordRequest):
    user = user_crud.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_valid = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.otp_code == data.otp_code,
        OTP.is_used == False,
        OTP.expires_at > datetime.now(timezone.utc)
    ).first()

    if not otp_valid:
        db.query(OTP).filter(
            OTP.user_id == user.id,
            ((OTP.is_used == True) | (OTP.expires_at <= datetime.now(timezone.utc)))
        ).delete()
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    db.delete(otp_valid)

    user_crud.update_password(db, user, data.new_password)
    db.commit()

    await send_password_reset_success_email(user.email, user.name)

    return {"message": "Password reset successfully"}
