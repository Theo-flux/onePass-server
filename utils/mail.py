from typing import List
from fastapi import BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from config.env import OnepassEnvs
from models.emails import EmailModel

conf = ConnectionConfig(
    MAIL_USERNAME=OnepassEnvs.get("EMAIL_USERNAME"),
    MAIL_PASSWORD=OnepassEnvs.get("EMAIL_PASSWORD"),
    MAIL_FROM=(OnepassEnvs.get("EMAIL_FROM")),
    MAIL_PORT=OnepassEnvs.get("EMAIL_PORT"),
    MAIL_SERVER=OnepassEnvs.get("EMAIL_SERVER"),
    MAIL_FROM_NAME=OnepassEnvs.get("EMAIL_FROM_NAME"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


async def send_email_with_template(arg: EmailModel):
    """_summary_

    Args:
        arg (EmailModel): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    message = MessageSchema(
        subject=arg.subject,
        recipients=arg.email_to,
        template_body=arg.template_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    await fm.send_message(message=message, template_name=arg.template_name)


def send_mail_in_background(background_tasks: BackgroundTasks, arg: EmailModel):
    """
    background task function to send mails.

    Args:
        background_tasks (BackgroundTasks): _description_
        subject (str): _description_
        email_to (List[str]): _description_
        body (dict): _description_
        template_name (str): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    message = MessageSchema(
        subject=arg.subject,
        recipients=arg.email_to,
        template_body=arg.template_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=arg.template_name)
