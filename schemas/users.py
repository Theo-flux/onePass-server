from typing import Optional
from pydantic import EmailStr
from datetime import datetime
from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    avatar: str | None = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
