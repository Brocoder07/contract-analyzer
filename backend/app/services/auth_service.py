from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password, decode_token
from app.db.mongodb import get_users_collection
from app.models.auth_schemas import UserCreateRequest, UserPublic, TokenResponse


class AuthService:
    @staticmethod
    def _users_collection_or_503():
        try:
            return get_users_collection()
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication database is unavailable",
            ) from exc

    @staticmethod
    def _to_public_user(user_doc: Dict[str, Any]) -> UserPublic:
        return UserPublic(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            created_at=user_doc["created_at"],
        )

    async def register_user(self, payload: UserCreateRequest) -> UserPublic:
        users = self._users_collection_or_503()

        existing = await users.find_one({"email": payload.email.lower()})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        document = {
            "email": payload.email.lower(),
            "full_name": payload.full_name.strip(),
            "hashed_password": hash_password(payload.password),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
        }

        try:
            result = await users.insert_one(document)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            ) from exc

        created = await users.find_one({"_id": result.inserted_id})
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create user")

        return self._to_public_user(created)

    async def authenticate(self, email: str, password: str) -> TokenResponse:
        users = self._users_collection_or_503()
        user = await users.find_one({"email": email.lower()})

        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        public_user = self._to_public_user(user)
        token = create_access_token(subject=str(user["_id"]), extra_claims={"email": user["email"]})

        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=public_user,
        )

    async def get_current_user_from_token(self, token: str) -> UserPublic:
        payload = decode_token(token)
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        users = self._users_collection_or_503()

        # id is stored as ObjectId in Mongo
        from bson import ObjectId

        try:
            user = await users.find_one({"_id": ObjectId(subject)})
        except Exception:
            user = None

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        if not user.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

        return self._to_public_user(user)


auth_service = AuthService()
