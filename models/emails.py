from typing import List, Dict, Any
from pydantic import BaseModel, EmailStr


class EmailType:
    def __init__(self, _subject: str, _template: str):
        self.subject = _subject
        self.template = _template


class EmailTypes:
    REGISTRATION = EmailType("Welcome to onepass", "register.html")


class EmailModel(BaseModel):
    email_to: List[EmailStr]
    template_body: Dict[str, Any]
    subject: str
    template_name: str
    # content: Dict[str, str]
