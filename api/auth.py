# api/auth.py
"""
Módulo de autenticação JWT.
Fornece endpoints: /auth/login e /auth/refresh
E dependência para proteger rotas (get_current_user).
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from jose import jwt, JWTError
from api.config import settings

# Secret e configurações vindas do settings
JWT_SECRET = settings.JWT_SECRET or "change_this_secret"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES or 60)
REFRESH_EXPIRE_MIN = int(settings.REFRESH_TOKEN_EXPIRE_MINUTES or 1440)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

# Função utilitária para criar tokens
def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_EXPIRE_MIN)
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import Body
# Endpoint de login (usuário + senha via form data ou JSON)
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest = Body(...)):
    """
    Autentica usuário admin e retorna access_token + refresh_token.
    Recebe JSON com { "username": "...", "password": "..." }.
    """
    admin_user = settings.ADMIN_USER or "admin"
    admin_pass = settings.ADMIN_PASSWORD or "admin123"

    username = credentials.username
    password = credentials.password

    if username != admin_user or password != admin_pass:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    payload = {"sub": username, "scope": "admin"}

    access_token = create_token(payload, expires_delta=timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh_token = create_token(payload, expires_delta=timedelta(minutes=REFRESH_EXPIRE_MIN))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires_in": ACCESS_EXPIRE_MIN * 60
    }

# Endpoint de refresh: recebe refresh_token e devolve novo access token
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshRequest):
    try:
        payload = jwt.decode(req.refresh_token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    new_payload = {"sub": username, "scope": "admin"}
    access_token = create_token(new_payload, expires_delta=timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh_token = create_token(new_payload, expires_delta=timedelta(minutes=REFRESH_EXPIRE_MIN))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires_in": ACCESS_EXPIRE_MIN * 60
    }

# Dependência para proteger rotas - valida o Authorization: Bearer <token>
from fastapi import Header

def get_current_user(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        # retorna claim básico (poderia retornar user object)
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")