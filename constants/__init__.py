from config.env import OnepassEnvs

base_url = (
    "http://localhost:8000"
    if OnepassEnvs.get("ENV") == "development"
    else "https://ops-staging.onrender.com"
)

origins = ["http://localhost:5173", "https://ops-6wwv.onrender.com"]
