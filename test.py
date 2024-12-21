import asyncio
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="theoifedev@gmail.com",
    MAIL_PASSWORD="evbsvellovhweivx",
    MAIL_FROM="theoifedev@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="onepassserver",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def test_email():
    fm = FastMail(conf)
    message = MessageSchema(
        subject="Test Email",
        recipients=["tifluse@gmail.com"],
        template_body={"name": "Theo", "link": "https://www.google.com"},
        subtype="html",
    )
    await fm.send_message(message=message, template_name="register.html")


asyncio.run(test_email())
