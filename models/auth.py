from pydantic import BaseModel, EmailStr, field_validator
from email_validator import validate_email, EmailNotValidError, EmailSyntaxError


class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except EmailNotValidError:
            raise EmailSyntaxError("Invalid Email format")


class LoginModel(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except EmailNotValidError:
            raise EmailSyntaxError("Invalid Email format")


class ForgotPwdModel(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except EmailNotValidError:
            raise EmailSyntaxError("Invalid Email format")


class ResetPwdModel(BaseModel):
    password: str
