from fastapi import Depends, HTTPException, Request
from jose import jwt, ExpiredSignatureError, JWTError
from app.core.config import JWT_SECRET  # Ensure JWT_SECRET is correctly loaded

def verify_token(request: Request):
    token = request.cookies.get("access_token")  # 🍪 Read token from cookie

    if not token:
        raise HTTPException(status_code=401, detail={"success": False, "message": "Token not found"})

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        request.state.user = payload
        request.state.hd = True
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"success": False, "message": "Token has expired"})
    except JWTError:
        raise HTTPException(status_code=401, detail={"success": False, "message": "Invalid token"})
