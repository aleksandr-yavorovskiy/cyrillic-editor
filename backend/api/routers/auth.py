import uuid

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user
from api.models import User
from api.schemas import RegisterRequest, TokenResponse


router = APIRouter(prefix="/api/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hash.encode("utf-8"))


def _generate_token() -> str:
    return str(uuid.uuid4())


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        username=req.username,
        password_hash=_hash_password(req.password),
        token=_generate_token(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(token=user.token, user_id=user.id, username=user.username)


@router.post("/token", response_model=TokenResponse)
async def login(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.token:
        user.token = _generate_token()
        await db.commit()

    return TokenResponse(token=user.token, user_id=user.id, username=user.username)


@router.get("/verify")
async def verify_token(user: User = Depends(get_current_user)):
    return {"valid": True, "user_id": user.id, "username": user.username}
