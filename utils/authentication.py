from os import environ
from dotenv import load_dotenv
from typing import Dict
from datetime import datetime, timedelta
from fastapi import Depends, status
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlmodel import Session, select
from config.env import OnepassEnvs
from utils.db import get_db
from models.auth import TokenTypeModel, UserResponseModel
from schemas import Users

load_dotenv()


class Authentication:
    ACCESS_TOKEN_SECRET_KEY = OnepassEnvs.get("ACCESS_TOKEN_SECRET_KEY")
    REFRESH_TOKEN_SECRET_KEY = OnepassEnvs.get("REFRESH_TOKEN_SECRET_KEY")
    EMAIL_VERIFICATION_TOKEN_SECRET_KEY = OnepassEnvs.get(
        "EMAIL_VERIFICATION_TOKEN_SECRET_KEY"
    )
    PASSWORD_RESET_TOKEN_SECRET_KEY = OnepassEnvs.get("PASSWORD_RESET_TOKEN_SECRET_KEY")

    ALGORITHM = OnepassEnvs.get("ALGORITHM")

    ACCESS_TOKEN_EXP_MINUTES = OnepassEnvs.get("ACCESS_TOKEN_EXP_MINUTES")
    REFRESH_TOKEN_EXP_MINUTES = OnepassEnvs.get("REFRESH_TOKEN_EXP_MINUTES")
    EMAIL_VERIFICATION_EXP_MINUTES = OnepassEnvs.get("EMAIL_VERIFICATION_EXP_MINUTES")
    PASSWORD_RESET_EXP_MINUTES = OnepassEnvs.get("PASSWORD_RESET_EXP_MINUTES")

    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth_scheme = HTTPBearer()

    def generate_token(self, token_type: TokenTypeModel, data: Dict[str, str]) -> str:
        payload = data.copy()
        curr_date = datetime.now()
        minutes = 0
        token = ""

        if token_type == TokenTypeModel.ACCESS_TOKEN:
            minutes = self.ACCESS_TOKEN_EXP_MINUTES
        elif token_type == TokenTypeModel.REFRESH_TOKEN:
            minutes = self.REFRESH_TOKEN_EXP_MINUTES
        elif token_type == TokenTypeModel.EMAIL_VERIFICATION_TOKEN:
            minutes = self.EMAIL_VERIFICATION_EXP_MINUTES
        elif token_type == TokenTypeModel.PASSWORD_RESET_TOKEN:
            minutes = self.PASSWORD_RESET_EXP_MINUTES

        payload.update(
            {"exp": curr_date + timedelta(minutes=minutes), "iat": curr_date}
        )

        if token_type == TokenTypeModel.ACCESS_TOKEN:
            token = jwt.encode(payload, self.ACCESS_TOKEN_SECRET_KEY, self.ALGORITHM)
        elif token_type == TokenTypeModel.REFRESH_TOKEN:
            token = jwt.encode(payload, self.REFRESH_TOKEN_SECRET_KEY, self.ALGORITHM)
        elif token_type == TokenTypeModel.EMAIL_VERIFICATION_TOKEN:
            token = jwt.encode(
                payload, self.EMAIL_VERIFICATION_TOKEN_SECRET_KEY, self.ALGORITHM
            )
        elif token_type == TokenTypeModel.PASSWORD_RESET_TOKEN:
            token = jwt.encode(
                payload, self.PASSWORD_RESET_TOKEN_SECRET_KEY, self.ALGORITHM
            )

        return token

    def decode_token(
        self,
        token: str,
        token_type: TokenTypeModel,
        credential_exception: HTTPException | None,
    ) -> str:
        """
        function to decode jwt token,

        Args:
            token (str): jwt token
            token_type (TokenTypeModel): access token or refresh token
            credential_exception (HTTPException | None): callback to raise exception

        Raises:
            credential_exception: _description_
            HTTPException: _description_
            credential_exception: _description_
            HTTPException: _description_

        Returns:
            str: _description_
        """
        try:

            key = ""

            if token_type == TokenTypeModel.ACCESS_TOKEN:
                key = self.ACCESS_TOKEN_SECRET_KEY
            elif token_type == TokenTypeModel.REFRESH_TOKEN:
                key = self.REFRESH_TOKEN_SECRET_KEY
            elif token_type == TokenTypeModel.EMAIL_VERIFICATION_TOKEN:
                key = self.EMAIL_VERIFICATION_TOKEN_SECRET_KEY
            elif token_type == TokenTypeModel.PASSWORD_RESET_TOKEN:
                key = self.PASSWORD_RESET_TOKEN_SECRET_KEY

            payload = jwt.decode(token, key=key, algorithms=[self.ALGORITHM])
            return payload["email"]
        except jwt.ExpiredSignatureError:
            if credential_exception:
                raise credential_exception
            else:
                raise HTTPException(status_code=401, detail="Signature has expired!")
        except JWTError:
            if credential_exception:
                raise credential_exception
            else:
                raise HTTPException(status_code=401, detail="Invalid token!")

    def get_pwd_hash(self, pwd: str) -> str:
        """
        utility function to create a hash password
        from a plain password.

        Args:
            pwd (str): plain password

        Returns:
            _type_: _description_
        """
        return self.pwd_ctx.hash(pwd)

    def verify_pwd(self, plain_pwd: str, hashed_pwd: str) -> bool:
        """
        utility function to verify password by comparing
        the plain password with the hashed version.

        Args:
            plain_pwd (str): _description_
            hashed_pwd (str): _description_

        Returns:
            bool: true or false
        """
        return self.pwd_ctx.verify(secret=plain_pwd, hash=hashed_pwd)

    def get_me(
        self,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
        db: Session = Depends(get_db),
    ) -> UserResponseModel:
        """
        get logged in user.

        Args:
            token (HTTPAuthorizationCredentials, optional): _description_. Defaults to Depends(auth_scheme).
            db (Session, optional): _description_. Defaults to Depends(get_db).

        Returns:
            UserResponseModel: _description_
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized!",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user_email = self.decode_token(
            token=token.credentials,
            token_type=TokenTypeModel.ACCESS_TOKEN,
            credential_exception=credentials_exception,
        )
        statement = select(Users).where(Users.email == user_email)
        result = db.exec(statement=statement).one_or_none()
        return UserResponseModel(**result.__dict__)
