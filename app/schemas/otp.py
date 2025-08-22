from pydantic import BaseModel
from datetime import datetime

class OTPCreate(BaseModel):
    user_id: int
    otp_code: str

class OTPVerify(BaseModel):
    email: str
    otp_code: str

class OTPResponse(BaseModel):
    id: int
    otp_code: str
    is_used: bool
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True