# api/auth.py
"""
Módulo de autenticação JWT.
Fornece endpoints: /auth/login e /auth/refresh
E dependência para proteger rotas (get_current_user).
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Body, Security
from pydantic import BaseModel
from jose import jwt, JWTError
from api.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configurações JWT
JWT_SECRET = settings.JWT_SECRET or "change_this_secret"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES or 60)
REFRESH_EXPIRE_MIN = int(settings.REFRESH_TOKEN_EXPIRE_MINUTES or 1440)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# --- Esquema de segurança compatível com FastAPI/Pydantic v2 ---
security = HTTPBearer()

# Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

class LoginRequest(BaseModel):
    username: str
    password: str


# --- Função utilitária para gerar tokens ---
def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_EXPIRE_MIN))
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


# --- Endpoint de login ---
@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest = Body(...)):
    """
    Autentica usuário admin e retorna access_token + refresh_token.
    Recebe JSON: {"username": "...", "password": "..."}
    """
    admin_user = settings.ADMIN_USER or "admin"
    admin_pass = settings.ADMIN_PASSWORD or "admin123"

    if credentials.username != admin_user or credentials.password != admin_pass:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    payload = {"sub": credentials.username, "scope": "admin"}
    access_token = create_token(payload, timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh_token = create_token(payload, timedelta(minutes=REFRESH_EXPIRE_MIN))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires_in": ACCESS_EXPIRE_MIN * 60,
    }


# --- Endpoint de refresh ---
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
    access_token = create_token(new_payload, timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh_token = create_token(new_payload, timedelta(minutes=REFRESH_EXPIRE_MIN))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires_in": ACCESS_EXPIRE_MIN * 60,
    }


# --- Dependência de autenticação protegida ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Valida o token JWT no cabeçalho Authorization: Bearer <token>.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")