from fastapi import BackgroundTasks, FastAPI
from datetime import datetime
from routers import emails
from fastapi.staticfiles import StaticFiles
from routers import auth
from utils.db import engine, SQLModel
from routers.emails import templates


SQLModel.metadata.create_all(engine)
app = FastAPI(
    title="onePass server",
    description="onePass is a password manager server.",
    version="0.0.1",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# Add global context processor
@app.middleware("http")
async def add_global_context(request, call_next):
    response = await call_next(request)
    templates.env.globals["copyright_text"] = (
        f"Copyright © {datetime.now().year}. FluxTech, All rights reserved."
    )
    return response


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}


app.include_router(auth.router)
app.include_router(emails.router)
