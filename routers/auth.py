from fastapi import APIRouter, Depends, Body, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from datetime import datetime
from models.auth import (
    TokenModel,
    RegisterModel,
    ForgotPwdModel,
    ResetPwdModel,
    LoginModel,
    TokenTypeModel,
    UserResponseModel,
)
from utils.db import get_db
from utils.authentication import Authentication
from schemas import Users

router = APIRouter(prefix="/auth", tags=["auth"])
auth_handler = Authentication()


@router.get("/me")
async def me(user: UserResponseModel = Depends(auth_handler.get_me)):
    """
    user me endpoint function
    """
    return user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_cred: LoginModel = Body(...), db: Session = Depends(get_db)):
    """
    user login endpoint function.
    """
    email = user_cred.email.lower()
    statement = select(Users).where(Users.email == email)
    result = db.exec(statement=statement).one_or_none()

    if result:
        if auth_handler.verify_pwd(user_cred.password, result.password):
            access_token = auth_handler.generate_access_token({"email": result.email})
            refresh_token = auth_handler.generate_access_token({"email": result.email})

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"access_token": access_token, "refresh_token": refresh_token},
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password!",
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="user doesn't exist!",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: RegisterModel = Body(...), db: Session = Depends(get_db)):
    """
    register user endpoint function.
    """
    statement = select(Users).where(Users.email == user.email.lower())
    result = db.exec(statement=statement)

    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account with this email already exists!",
        )

    secret_pwd = auth_handler.get_pwd_hash(user.password)
    curr_date = datetime.now()
    new_user = Users(
        name=user.name.lower(),
        email=user.email.lower(),
        password=secret_pwd,
        created_at=curr_date,
        updated_at=curr_date,
    )

    db.add(new_user)
    db.commit()
    db.close()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content={"message": "user created!"}
    )


@router.post("/forgot_pwd", status_code=status.HTTP_200_OK)
async def forgot_pwd(f_pwd: ForgotPwdModel = Body(...), db: Session = Depends(get_db)):
    """
    forgot password endpoint function
    """
    mail = f_pwd.email.lower()
    statement = select(Users).where(Users.email == mail)
    result = db.exec(statement=statement).one_or_none()

    if result:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "a link has been sent to your mail."},
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Invalid email address!",
    )
    pass


@router.post("/reset_pwd/{reset_token}")
async def reset_pwd(new_pwd: ResetPwdModel = Body(...), db: Session = Depends(get_db)):
    """
    reset password endpoint function.
    """
    pass


@router.get("/refresh/{token}", response_model=TokenModel)
async def refresh_token(token: str = Body(...), db: Session = Depends(get_db)):
    email = auth_handler.decode_token(token, TokenTypeModel.REFRESH_TOKEN)

    if email:
        statement = select(Users).where(Users.email == email)
        result = db.exec(statement=statement).one_or_none()

        if result:
            access_token = auth_handler.generate_access_token({"email": email})
            refresh_token = auth_handler.generate_refresh_token({"email": email})

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"access_token": access_token, "refresh_token": refresh_token},
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token!"
    )
