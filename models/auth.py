from enum import Enum
from pydantic import BaseModel, field_validator
from datetime import datetime
from email_validator import validate_email, EmailNotValidError, EmailSyntaxError


class RegisterModel(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validatedEmail = validate_email(value)
            return validatedEmail.email
        except EmailNotValidError:
            raise EmailSyntaxError("Invalid Email format")


class LoginModel(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validatedEmail = validate_email(value)
            return validatedEmail.email
        except EmailNotValidError:
            raise EmailSyntaxError("Invalid Email format")


class ForgotPwdModel(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validatedEmail = validate_email(value)
            return validatedEmail.email
        except EmailNotValidError:
            raise EmailSyntaxError("Invalid Email format")


class ResetPwdModel(BaseModel):
    password: str


class UserResponseModel(BaseModel):
    id: int
    name: str
    avatar: str | None
    email: str
    created_at: datetime
    updated_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str


class TokenTypeModel(str, Enum):
    ACCESS_TOKEN = "ACCESS_TOKEN"
    REFRESH_TOKEN = "REFRESH_TOKEN"
    EMAIL_VERIFICATION_TOKEN = "EMAIL_VERIFICATION_TOKEN"
    PASSWORD_RESET_TOKEN = "PASSWORD_RESET_TOKEN"
