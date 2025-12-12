import secrets
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta

from sqlalchemy import text

SECRET_KEY = "verysecretkey"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRES_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token():
    token = secrets.token_hex(32)  # безопасный random 64 chars
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return token, expires