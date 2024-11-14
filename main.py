from fastapi import FastAPI, BackgroundTasks
from models.emails import EmailModel, EmailTypes
from routers import auth
from utils.db import engine, SQLModel
from utils.mail import send_email_with_template, send_mail_in_background


SQLModel.metadata.create_all(engine)
app = FastAPI(
    title="onePass server",
    description="onePass is a password manager server.",
    version="0.0.1",
)

# trigger email verification
email_data = EmailModel(
    subject=EmailTypes.REGISTRATION.subject,
    email_to=["tifluse@gmail.com"],
    template_body={"name": "Theo"},
    template_name=EmailTypes.REGISTRATION.template,
)


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/send-email/asynchronous")
async def send_email_asynchronous():
    await send_email_with_template(email_data)
    return "Success"


@app.get("/send-email/backgroundtasks")
def send_email_backgroundtasks(background_tasks: BackgroundTasks):
    send_mail_in_background(background_tasks, email_data)
    return "Success"


app.include_router(auth.router)
