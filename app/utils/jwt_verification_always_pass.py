# dependencies/auth.py

from fastapi import Request
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import JWT_SECRET

def verify_token_always_pass(request: Request):
    # Set default values
    request.state.hd = False
    request.state.jwt = {"success": False, "message": "Token not found!"}

    token = request.cookies.get("access_token")  # 🍪 Read from cookie

    if not token:
        return  # No token provided

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        request.state.user = payload  # Optional: attach user info to request
        request.state.hd = True
        request.state.jwt = {"success": True, "message": "Token verified."}
        return payload
    except ExpiredSignatureError:
        request.state.jwt = {"success": False, "message": "Token has expired!"}
    except JWTError:
        request.state.jwt = {"success": False, "message": "Invalid token!"}
