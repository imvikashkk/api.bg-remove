from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import JWT_SECRET, JWT_EXPIRE_MINUTES, JWT_EXPIRE_MINUTES_REMEMBER

def create_access_token(data: dict, remember: bool = False):
    to_encode = data.copy()
    expire_time = JWT_EXPIRE_MINUTES_REMEMBER if remember else JWT_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_time)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256"), expire_time
