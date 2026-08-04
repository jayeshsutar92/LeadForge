from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.user import AuthResponse, UserCreate, UserLogin, UserResponse
from app.services.auth import AuthService, ACCESS_TTL_MIN

router = APIRouter()

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

@router.post("/register", response_model=AuthResponse)
async def register(
    payload: UserCreate,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    try:
        user = await service.register(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    token = service.create_access_token(user.id, user.email)
    _set_cookie(response, token)
    
    return AuthResponse.model_validate({
        "id": str(user.id),
        "email": user.email,
        "name": user.full_name,
        "role": user.role,
        "access_token": token,
    })

@router.post("/login", response_model=AuthResponse)
async def login(
    payload: UserLogin,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session)
):
    service = AuthService(session)
    client_host = request.client.host if request.client else "unknown"
    identifier = f"{client_host}:{payload.email.lower()}"
    
    await service.check_brute_force(identifier)
    
    try:
        user = await service.authenticate(payload.email, payload.password)
        if not user:
            await service.register_failed_attempt(identifier)
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        await service.clear_failed_attempts(identifier)
        token = service.create_access_token(user.id, user.email)
        _set_cookie(response, token)
        
        return AuthResponse.model_validate({
            "id": str(user.id),
            "email": user.email,
            "name": user.full_name,
            "role": user.role,
            "access_token": token,
        })
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(get_current_user)
):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}

@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate({
        "id": str(user.id),
        "email": user.email,
        "name": user.full_name,
        "role": user.role,
    })
