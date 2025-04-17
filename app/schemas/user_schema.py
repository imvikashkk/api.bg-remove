from pydantic import BaseModel, EmailStr, Field,  model_validator, field_validator, root_validator
from datetime import datetime, timedelta,  timezone
from typing import Optional, Literal

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    confirmpassword: str
    agree: bool = Field(default=True)
    notify: bool = Field(default=False)
    verified: bool = Field(default=False)
    otp: Optional[str] = None
    otp_type: Optional[Literal["verify", "forgotPass"]] = None
    otp_expiry: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Always update updated_at on any modification
    @model_validator(mode="before")
    @classmethod
    def set_updated_at(cls, values: dict) -> dict:
        values = dict(values)
        values["updated_at"] = datetime.now(timezone.utc)
        return values

    # Set creation defaults (without otp_expiry logic)
    @model_validator(mode="before")
    @classmethod
    def set_creation_defaults(cls, values: dict) -> dict:
        current_time = datetime.now(timezone.utc)
        
        # Ensure creation time is set only during creation
        if "created_at" not in values or values["created_at"] is None:
            values.setdefault("agree", True)
            values.setdefault("notify", False)
            values.setdefault("verified", False)
            values["created_at"] = current_time
        
        return values

    # ✅ Automatically set otp_expiry if OTP is provided and not already set
    @model_validator(mode="after")
    def set_otp_expiry_auto(self) -> "UserCreate":
        if self.otp and not self.otp_expiry:
            self.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        return self

    # Ensure agree is True
    @model_validator(mode="after")
    def check_agree(self) -> "UserCreate":
        if not self.agree:
            raise ValueError("You must agree to the terms and conditions and privacy policy.")
        return self
    


class UserResponse(BaseModel):
    firstname:str
    lastname:str
    email: EmailStr
    id: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool

class LoginResponse(BaseModel):
    success:bool
    message:str
    data: UserResponse

class Email_OTP_Request(BaseModel):
    email:EmailStr

class Email_Verify_Request(BaseModel):
    email:EmailStr
    otp:str

class ForgotPassSetPass_Req(BaseModel):
    email:EmailStr
    otp:str
    password:str
    confirmpassword:str

class SubscriberCreate(BaseModel):
    email:EmailStr
    force:bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None