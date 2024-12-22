from os import environ
from dotenv import load_dotenv
from enum import Enum

load_dotenv(),


OnepassEnvs = {
    # Environment
    "ENV": environ.get("ENV", "development"),
    # Database
    "DB_NAME": environ.get("DB_NAME"),
    "DB_USER": environ.get("DB_USER"),
    "DB_HOSTNAME": environ.get("DB_HOSTNAME"),
    "DB_PWD": environ.get("DB_PWD"),
    # Auth Envs
    "ACCESS_TOKEN_SECRET_KEY": environ.get("ACCESS_TOKEN_SECRET_KEY"),
    "REFRESH_TOKEN_SECRET_KEY": environ.get("REFRESH_TOKEN_SECRET_KEY"),
    "EMAIL_VERIFICATION_TOKEN_SECRET_KEY": environ.get(
        "EMAIL_VERIFICATION_TOKEN_SECRET_KEY", ""
    ),
    "PASSWORD_RESET_TOKEN_SECRET_KEY": environ.get(
        "PASSWORD_RESET_TOKEN_SECRET_KEY", ""
    ),
    "ALGORITHM": environ.get("ALGORITHM", "HS256"),
    "ACCESS_TOKEN_EXP_MINUTES": int(
        environ.get("ACCESS_TOKEN_EXP_MINUTES"),
    ),
    "REFRESH_TOKEN_EXP_MINUTES": int(
        environ.get("REFRESH_TOKEN_EXP_MINUTES"),
    ),
    "EMAIL_VERIFICATION_EXP_MINUTES": int(
        environ.get("EMAIL_VERIFICATION_EXP_MINUTES"),
    ),
    "PASSWORD_RESET_EXP_MINUTES": int(
        environ.get("PASSWORD_RESET_EXP_MINUTES"),
    ),
    # Email Envs
    "EMAIL_USERNAME": environ.get("EMAIL_USERNAME"),
    "EMAIL_PASSWORD": environ.get("EMAIL_PASSWORD"),
    "EMAIL_PORT": int(
        environ.get("EMAIL_PORT"),
    ),
    "EMAIL_FROM_NAME": environ.get("EMAIL_FROM_NAME"),
    "EMAIL_SERVER": environ.get("EMAIL_SERVER"),
    "EMAIL_FROM": environ.get("EMAIL_FROM"),
    "EMAIL_USE_TLS": True,
}
