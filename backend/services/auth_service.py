"""Authentication utilities: password hashing, JWT, admin seeding, brute-force guard."""
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException, Request

JWT_ALG = "HS256"
ACCESS_TTL_MIN = 60 * 24  # 24h — SaaS convenience
LOCKOUT_MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _secret() -> str:
    return os.environ.get("JWT_SECRET", "leadforge-local-secret-key-2026")


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False


def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TTL_MIN),
        "type": "access",
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[JWT_ALG])


async def get_current_user(request: Request) -> dict:
    token: Optional[str] = request.cookies.get("access_token")
    if not token:
        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            token = header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = request.state.db
    user = await db.users.find_one({"id": payload["sub"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user.pop("_id", None)
    user.pop("password_hash", None)
    return user


async def check_brute_force(db, identifier: str) -> None:
    doc = await db.login_attempts.find_one({"identifier": identifier})
    if not doc:
        return
    if doc.get("count", 0) >= LOCKOUT_MAX_ATTEMPTS:
        locked_until = doc.get("locked_until")
        if locked_until and datetime.now(timezone.utc) < datetime.fromisoformat(locked_until):
            raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")


async def register_failed_attempt(db, identifier: str) -> None:
    doc = await db.login_attempts.find_one({"identifier": identifier})
    count = (doc.get("count", 0) if doc else 0) + 1
    update = {"count": count, "last_at": datetime.now(timezone.utc).isoformat()}
    if count >= LOCKOUT_MAX_ATTEMPTS:
        update["locked_until"] = (datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
    await db.login_attempts.update_one({"identifier": identifier}, {"$set": update}, upsert=True)


async def clear_failed_attempts(db, identifier: str) -> None:
    await db.login_attempts.delete_one({"identifier": identifier})


async def seed_admin(db) -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com").lower()
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": email})
    if not existing:
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": email,
            "name": "Jayesh Sutar",
            "role": "admin",
            "password_hash": hash_password(password),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    elif not verify_password(password, existing.get("password_hash", "")):
        await db.users.update_one(
            {"email": email}, {"$set": {"password_hash": hash_password(password)}}
        )
