from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt
from app.db.session import get_db
from app.core.config import settings
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.otp import OTPVerify
from app.services.auth_service import register_user, login_user
from app.services.otp_service import verify_otp
from app.services.activity_log_service import log_activity
from app.api.deps import get_current_user, get_client_ip, get_user_agent, security
from app.models.user import User
from app.crud import token as token_crud

router = APIRouter()


@router.post("/signup", response_model=dict)
async def signup(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    result = await register_user(db, user_data)

    # Log signup activity
    log_activity(
        db=db,
        user_id=result["user_id"],
        user_name=user_data.name,
        activity_type="signup",
        description=f"User {user_data.name} registered",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return result


@router.post("/verify-otp", response_model=dict)
def verify_otp_endpoint(
    otp_data: OTPVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    is_verified = verify_otp(db, otp_data.email, otp_data.otp_code)

    if not is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Get user for logging
    from app.crud.user import get_user_by_email
    user = get_user_by_email(db, otp_data.email)

    # Log OTP verification activity
    log_activity(
        db=db,
        user_id=user.id if user else None,
        activity_type="verify_otp",
        description=f"OTP verified for {otp_data.email}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return {"message": "Account verified successfully"}


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    token = login_user(db, user_data)

    # Get user for logging
    from app.crud.user import get_user_by_email
    user = get_user_by_email(db, user_data.email)

    # Log login activity
    log_activity(
        db=db,
        user_id=user.id if user else None,
        user_name=user.name if user else None,
        activity_type="login",
        description=f"User {user_data.email} logged in",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return token


@router.post("/logout", response_model=dict)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = jwt.decode(token, settings.SECRET_KEY,
                         algorithms=[settings.ALGORITHM])
    jti = payload.get("jti")

    if not jti:  # 🔑 validate before passing
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )

    token_crud.deactivate_token(db, jti)

    log_activity(
        db=db,
        user_id=current_user.id,
        user_name=current_user.name,
        activity_type="logout",
        description=f"User {current_user.email} logged out",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
