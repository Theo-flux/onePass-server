from os import environ
from dotenv import load_dotenv
from typing import Dict
from datetime import datetime, timedelta
from fastapi import Security, security, Depends, status
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlmodel import Session, select
from utils.db import get_db
from models.auth import TokenTypeModel, UserResponseModel
from schemas import Users

load_dotenv()


class Authentication:
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    ACCESS_TOKEN_SECRET_KEY = environ.get("ACCESS_TOKEN_SECRET_KEY")
    REFRESH_TOKEN_SECRET_KEY = environ.get("REFRESH_TOKEN_SECRET_KEY")
    ALGORITHM = environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(environ.get("REFRESH_TOKEN_EXPIRE_MINUTES"))

    auth_scheme = HTTPBearer()

    def generate_access_token(self, data: Dict[str, str]) -> str:
        """
        generate access token

        Args:
            data (Dict[str, str]): _description_

        Returns:
            str: _description_
        """
        payload = data.copy()
        curr_date = datetime.now()
        payload.update(
            {
                "exp": curr_date + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
                "iat": curr_date,
            }
        )

        token: str = jwt.encode(payload, self.ACCESS_TOKEN_SECRET_KEY, self.ALGORITHM)

        return token

    def generate_refresh_token(self, data: Dict[str, str]) -> str:
        """
        generate refresh token

        Args:
            data (Dict[str, str]): _description_

        Returns:
            str: _description_
        """
        payload = data.copy()
        curr_date = datetime.now()
        payload.update(
            {
                "exp": curr_date + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_MINUTES),
                "iat": curr_date,
            }
        )

        refresh_token: str = jwt.encode(
            payload, self.REFRESH_TOKEN_SECRET_KEY, self.ALGORITHM
        )

        return refresh_token

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
            key = (
                self.ACCESS_TOKEN_SECRET_KEY
                if token_type == TokenTypeModel.ACCESS_TOKEN
                else self.REFRESH_TOKEN_SECRET_KEY
            )
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

        return result
