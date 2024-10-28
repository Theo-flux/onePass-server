from fastapi import APIRouter
from models import auth

router = APIRouter(tags=["auth"])


@router.get("/me")
async def me():
    """
    user me endpoint function
    """
    pass


@router.post("/login")
async def login(new_user: auth.LoginModel):
    """
    user login endpoint function.
    """
    pass


@router.post("/register")
async def register(user: auth.RegisterModel):
    """
    register user endpoint function.
    """
    pass


@router.post("/forgot_pwd")
async def forgot_pwd(f_pwd: auth.ForgotPwdModel):
    """
    forgot password endpoint function
    """
    pass


@router.post("/reset_pwd")
async def reset_pwd(r_pwd: auth.ResetPwdModel):
    """
    reset password endpoint function.
    """
    pass
