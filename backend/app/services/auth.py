from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis_client, build_redis_key
from app.core.security import TokenType, create_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, AuthResponse
import uuid

ACCESS_TTL_MIN = 60 * 24
LOCKOUT_MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()

    async def register(self, payload: UserCreate) -> User:
        existing_user = await self.get_user_by_email(payload.email)
        if existing_user is not None:
            raise ValueError("Email already registered")

        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name or payload.name,
            hashed_password=hash_password(payload.password),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.get_user_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    async def refresh(self, refresh_token: str) -> str:
        """Validate a refresh token and return a new access token."""
        payload = self.decode_expected_token(refresh_token, TokenType.REFRESH)
        user = await self.get_user_from_token_payload(payload)
        token_version = int(payload.get("token_version", -1))
        if token_version != user.refresh_token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self.create_access_token(user.id, user.email)

    async def logout(self, user: User) -> None:
        user.refresh_token_version += 1
        await self.session.commit()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    def create_access_token(self, user_id: UUID, email: str) -> str:
        return create_token(
            subject=str(user_id),
            token_type=TokenType.ACCESS,
            expires_delta=timedelta(minutes=ACCESS_TTL_MIN),
        )
    async def check_brute_force(self, identifier: str) -> None:
        redis = get_redis_client()
        key = build_redis_key("auth", "brute_force", identifier)
        count = await redis.get(key)
        if count and int(count) >= LOCKOUT_MAX_ATTEMPTS:
            raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")

    async def register_failed_attempt(self, identifier: str) -> None:
        redis = get_redis_client()
        key = build_redis_key("auth", "brute_force", identifier)
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, LOCKOUT_MINUTES * 60)
        elif count >= LOCKOUT_MAX_ATTEMPTS:
            await redis.expire(key, LOCKOUT_MINUTES * 60)

    async def clear_failed_attempts(self, identifier: str) -> None:
        redis = get_redis_client()
        key = build_redis_key("auth", "brute_force", identifier)
        await redis.delete(key)

    def decode_expected_token(self, token: str, token_type: TokenType) -> dict:
        try:
            payload = decode_token(token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        if payload.get("type") != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    async def get_user_from_token_payload(self, payload: dict) -> User:
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = UUID(subject)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
