from typing import List
from fastapi import BackgroundTasks
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from config.env import OnepassEnvs
from models.emails import EmailModel
from datetime import datetime

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
    MAIL_DEBUG=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


async def send_email_with_template(email_data: EmailModel):
    """_summary_

    Args:
        email_data (EmailModel): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """

    email_data.template_body.__setattr__(
        "copyright_text",
        f"Copyright © {datetime.now().year}. FluxTech, All rights reserved.",
    )
    message = MessageSchema(
        subject=email_data.subject,
        recipients=email_data.email_to,
        template_body=email_data.template_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message=message, template_name=email_data.template_name)


def send_mail_in_background(background_tasks: BackgroundTasks, email_data: EmailModel):
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

    email_data.template_body["copyright_text"] = (
        f"Copyright © {datetime.now().year}. FluxTech, All rights reserved.",
    )
    message = MessageSchema(
        subject=email_data.subject,
        recipients=email_data.email_to,
        template_body=email_data.template_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message=message, template_name=email_data.template_name
    )

    print(message, fm, email_data, background_tasks)
    return background_tasks
