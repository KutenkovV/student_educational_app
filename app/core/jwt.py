from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "verysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)