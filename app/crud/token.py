from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from app.models.tokens import Token


def create_token(db: Session, jti: str, user_id: int, expires_at: datetime) -> Token:
    db_token = Token(jti=jti, user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def deactivate_token(db: Session, jti: str) -> None:
    token = db.query(Token).filter(Token.jti == jti, Token.is_active == True).first()
    if token:
        token.is_active = False
        db.commit()


def get_active_token(db: Session, jti: str) -> Optional[Token]:
    return db.query(Token).filter(
        Token.jti == jti,
        Token.is_active == True,
        Token.expires_at > datetime.now(timezone.utc)
    ).first()
