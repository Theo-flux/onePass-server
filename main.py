from fastapi import FastAPI
from routers import emails
from fastapi.staticfiles import StaticFiles
from routers import auth
from utils.db import engine, SQLModel


SQLModel.metadata.create_all(engine)
app = FastAPI(
    title="onePass server",
    description="onePass is a password manager server.",
    version="0.0.1",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


app.include_router(auth.router)
app.include_router(emails.router)
