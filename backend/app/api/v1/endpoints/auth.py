from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.auth_schemas import (
    AuthMessageResponse,
    TokenResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserPublic,
)
from app.services.auth_service import auth_service

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=AuthMessageResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreateRequest):
    user = await auth_service.register_user(payload)
    return AuthMessageResponse(message="User registered successfully", user=user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest):
    return await auth_service.authenticate(payload.email, payload.password)


@router.get("/me", response_model=UserPublic)
async def me(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    return await auth_service.get_current_user_from_token(credentials.credentials)
