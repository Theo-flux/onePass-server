from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/emails", tags=["emails"])

templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"name": "Theo", "link": "https://samplelink.com"},
    )
