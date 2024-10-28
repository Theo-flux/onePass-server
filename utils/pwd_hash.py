from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_pwd_hash(pwd: str) -> str:
    """
    utility function to create a hash password
    from a plain password.

    Args:
        pwd (str): plain password

    Returns:
        _type_: _description_
    """
    return pwd_ctx.hash(pwd)


def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    """
    utility function to verify password by comparing
    the plain password with the hashed version.

    Args:
        plain_pwd (str): _description_
        hashed_pwd (str): _description_

    Returns:
        bool: true or false
    """
    return pwd_ctx.verify(secret=plain_pwd, hash=hashed_pwd)
