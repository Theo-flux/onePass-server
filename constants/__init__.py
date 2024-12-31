from config.env import OnepassEnvs

base_url = (
    "http://localhost:8000"
    if OnepassEnvs.get("ENV") == "development"
    else "https://ops-staging.onrender.com"
)
