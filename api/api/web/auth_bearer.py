from typing import Dict

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from api.settings import settings
import time
from datetime import timedelta


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = decode_jwt(jwt_token)
        except Exception:
            payload = None

        if payload:
            is_token_valid = True
        return is_token_valid


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}


def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + timedelta(days=1).seconds
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token
