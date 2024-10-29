from enum import Enum
from pydantic import BaseModel, field_validator, Field
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
    username: str
    email: str
    avatar: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenTypeModel(str, Enum):
    ACCESS_TOKEN = "ACCESS_TOKEN"
    REFRESH_TOKEN = "REFRESH_TOKEN"
