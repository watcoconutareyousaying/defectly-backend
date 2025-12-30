import random
import string
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.otp import OTP
from app.models.user import User
from app.core.config import settings


def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


def create_otp(db: Session, user_id: int) -> OTP:
    db.query(OTP).filter(OTP.user_id == user_id,
                         OTP.is_used == False).update({"is_used": True})

    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)  # OTP expires in 10 minutes

    db_otp = OTP(
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp


async def send_otp_email(email: str, otp_code: str):
    message = MIMEMultipart()
    message["From"] = "noreply@defectly.com"
    message["To"] = email
    message["Subject"] = "Verify Your Account - OTP Code"

    body = f"""
    <html>
        <body>
            <h2>Account Verification</h2>
            <p>Your OTP code is: <strong>{otp_code}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </body>
    </html>
    """

    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def verify_otp(db: Session, email: str, otp_code: str) -> bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False

    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.otp_code == otp_code,
        OTP.is_used == False,
        OTP.expires_at > datetime.now(timezone.utc)
    ).first()

    if otp:
        otp.is_used = True
        user.is_active = True
        user.is_verified = True
        db.commit()
        return True
    return False


async def send_welcome_email(email: str, name: str):
    message = MIMEMultipart()
    message["From"] = "noreply@defectly.com"
    message["To"] = email
    message["Subject"] = "Welcome to Defectly!"

    body = f"""
    <html>
        <body>
            <h2>Welcome, {name}!</h2>
            <p>Thank you for verifying your account. 🎉</p>
            <p>You can now log in and start using Defectly.</p>
            <p>If you need any help, feel free to contact our support team.</p>
            <br>
            <p>Best regards,<br>Defectly Team</p>
        </body>
    </html>
    """

    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


async def send_password_reset_email(email: str, otp_code: str):
    message = MIMEMultipart()
    message["From"] = 'noreply@defectly.com'
    message["To"] = email
    message["Subject"] = "Password Rest Request"

    body = f"""
    <html>
        <body>
            <h2>Password Rest</h2>
            <p>Your OTP code to reset password is: <strong>{otp_code}</strong></p>
            <p>If you didn’t request this, please ignore this email.</p>
        </body>
    </html>
    """

    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        print(f"Error sending reset email: {e}")
        return False


async def send_password_reset_success_email(email: str, name: str):
    message = MIMEMultipart()
    message["From"] = "noreply@defectly.com"
    message["To"] = email
    message["Subject"] = "Your password has been reset"

    body = f"""
    <html>
        <body>
            <h2>Password Reset Successful</h2>
            <p>Hello {name},</p>
            <p>Your password has been successfully reset.</p>
            <p>If you did not perform this action, please contact our support team immediately.</p>
            <br>
            <p>Best regards,<br>Defectly Team</p>
        </body>
    </html>
    """

    message.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        return True
    except Exception as e:
        print(f"Error sending password reset success email: {e}")
        return False
