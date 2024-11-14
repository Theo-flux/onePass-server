import httpx
from fastapi import (
    APIRouter,
    Depends,
    Body,
    status,
    HTTPException,
    Query,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from datetime import datetime
from models.auth import (
    TokenModel,
    RegisterModel,
    ForgotPwdModel,
    ResetPwdModel,
    TokenTypeModel,
    UserResponseModel,
    LoginModel,
)

from models.emails import EmailTypes, EmailModel
from utils.db import get_db
from utils.authentication import Authentication

from utils.mail import send_email_with_template
from schemas import Users

router = APIRouter(prefix="/auth", tags=["auth"])
auth_handler = Authentication()


def get_tokens(email: str) -> TokenModel:
    """
    generate access, refren and token type.

    Args:
        email (str): _description_

    Returns:
        TokenModel: _description_
    """
    access_token = auth_handler.generate_token(
        TokenTypeModel.ACCESS_TOKEN,
        {"email": email},
    )
    refresh_token = auth_handler.generate_token(
        TokenTypeModel.REFRESH_TOKEN, {"email": email}
    )

    content: TokenModel = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

    return content


@router.get("/me")
async def me(user: UserResponseModel = Depends(auth_handler.get_me)):
    """
    user me endpoint function
    """
    return user


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenModel)
async def login(user_cred: LoginModel, db: Session = Depends(get_db)):
    """
    user login endpoint function.
    """
    email = user_cred.email.lower()
    statement = select(Users).where(Users.email == email)
    result = db.exec(statement=statement).one_or_none()

    if result:
        if result.is_verified:
            if auth_handler.verify_pwd(user_cred.password, result.password):
                token = get_tokens(result.email)

                return token

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password!",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email has not been verified yet.",
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="user doesn't exist!",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: RegisterModel = Body(...),
    db: Session = Depends(get_db),
):
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

    # trigger email verification
    email_data = EmailModel(
        subject=EmailTypes.REGISTRATION.subject,
        email_to=[user.email],
        template_body={"name": user.name},
        template_name=EmailTypes.REGISTRATION.template,
    )

    try:
        db.commit()
        # TODO: Call the emailbackground endpoint here.
        async with httpx.AsyncClient() as client:
            await client.post("http://localhost:8000/emailbackground", json=email_data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "A link has been sent to your mail for verification."})
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to complete registration at this time. Please try again later.",
        ) from e
    finally:
        db.close()


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


@router.post("/emailbackground")
async def send_in_background(
    background_tasks: BackgroundTasks, email_data: EmailModel
) -> JSONResponse:

    background_tasks.add_task(send_email_with_template(email_data))

    return JSONResponse(status_code=200, content={"message": "email has been sent"})


@router.post("/reset_pwd/{reset_token}")
async def reset_pwd(new_pwd: ResetPwdModel = Body(...), db: Session = Depends(get_db)):
    """
    reset password endpoint function.
    """
    pass


@router.get(
    "/refresh/{token}", status_code=status.HTTP_200_OK, response_model=TokenModel
)
async def refresh_token(token: str, db: Session = Depends(get_db)):
    email = auth_handler.decode_token(
        token=token, token_type=TokenTypeModel.REFRESH_TOKEN, credential_exception=None
    )

    if email:
        statement = select(Users).where(Users.email == email)
        result = db.exec(statement=statement).one_or_none()

        if result:
            token = get_tokens(result.email)
            return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token!"
    )


@router.get("/verify", status_code=status.HTTP_200_OK)
async def acct_verification(
    token: str = Query(description="email token verification"),
    db: Session = Depends(get_db),
):
    pass


@router.get("/resend_verify")
async def resend_verify(
    email: str = Query(description="email to resend verification."),
    db: Session = Depends(get_db),
):
    statement = select(Users).where(Users.email == email.lower())
    result = db.exec(statement=statement).one_or_none()

    if result:
        if result.is_verified:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Email already verified"},
            )
        else:
            # resend the link to their mail.
            pass

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with email, {email} doesn't exist in our database.",
    )
