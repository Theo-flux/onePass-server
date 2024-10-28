from os import environ
from dotenv import load_dotenv
from typing import Dict
from datetime import datetime, timedelta
from fastapi import Security, security, Depends, status
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import jwt
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

    oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="login")

    def generate_access_token(self, data: Dict[str, str]) -> str:
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

    def generate_refresh_token(self, data: Dict[str, str]):
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
        except jwt.InvalidTokenError as e:
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

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials, TokenTypeModel.ACCESS_TOKEN)

    def get_me(
        self, token: str = Depends(oauth2_user_scheme), db: Session = Depends(get_db)
    ) -> UserResponseModel:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized!",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user_id = self.decode_token(token, credential_exception=credentials_exception)
        statement = select(Users).where(Users.id == user_id)
        result = db.exec(statement=statement)

        return result
