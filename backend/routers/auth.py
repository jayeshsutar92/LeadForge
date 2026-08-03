"""Auth API routes."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field

from services.auth_service import (
    check_brute_force,
    clear_failed_attempts,
    create_access_token,
    get_current_user,
    hash_password,
    register_failed_attempt,
    verify_password,
    ACCESS_TTL_MIN,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: str = Field(min_length=1, max_length=80)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


def _set_cookie(resp: Response, token: str) -> None:
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=ACCESS_TTL_MIN * 60,
        path="/",
    )


@router.post("/register")
async def register(payload: RegisterIn, request: Request, response: Response):
    db = request.state.db
    email = payload.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": payload.name.strip(),
        "role": "user",
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user)

    token = create_access_token(user["id"], email)
    _set_cookie(response, token)
    return {
        "id": user["id"],
        "email": email,
        "name": user["name"],
        "role": user["role"],
        "access_token": token,
    }


@router.post("/login")
async def login(payload: LoginIn, request: Request, response: Response):
    db = request.state.db
    email = payload.email.lower()
    client_host = request.client.host if request.client else "unknown"
    identifier = f"{client_host}:{email}"

    await check_brute_force(db, identifier)

    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        await register_failed_attempt(db, identifier)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await clear_failed_attempts(db, identifier)
    token = create_access_token(user["id"], email)
    _set_cookie(response, token)
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user.get("name"),
        "role": user.get("role", "user"),
        "access_token": token,
    }


@router.post("/logout")
async def logout(response: Response, user=Depends(get_current_user)):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user
