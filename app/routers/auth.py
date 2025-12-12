from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user_with_permissions, require_permission
from app.core.jwt import create_access_token, create_refresh_token
from app.core.security import hash_password, verify_password
from app.db import async_session
from uuid import UUID
from sqlalchemy import select, text

from app.models import User
from app.schemas import RefreshTokenBase, UserCreate, UserOut, UserUpdate, LoginRequest

router = APIRouter(tags=["Auth"])

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/register", dependencies=[Depends(require_permission(["users.create"]))])
async def register(data: UserCreate, session: AsyncSession = Depends(get_session)):
    hashed = hash_password(data.password)

    user = User(
        login=data.login,
        password_hash=hashed,
        role_id=data.role_id,
        first_name=data.first_name,
        middle_name=data.middle_name,
        last_name=data.last_name
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"message": "User created", "id": user.id}

@router.post("/login")
async def login(form: LoginRequest, session: AsyncSession = Depends(get_session)):
    query = select(User).where(User.login == form.login)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(404, "Неверный логин или пароль")

    # Создаём access token
    access = create_access_token({"sub": str(user.id)})

    # Создаём refresh token
    refresh, expires = create_refresh_token()

    # Сохраняем refresh token в БД
    await session.execute(
        text("""
            INSERT INTO refresh_tokens (user_id, token, expires_at)
            VALUES (:uid, :token, :expires)
        """),
        {"uid": user.id, "token": refresh, "expires": expires}
    )
    await session.commit()
    
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }
    
@router.post("/refresh")
async def refresh_token(refresh_token: str, session: AsyncSession = Depends(get_session)):
    
    query = text("""
        SELECT user_id, expires_at
        FROM refresh_tokens
        WHERE token = :token
    """)

    result = await session.execute(query, {"token": refresh_token})
    row = result.fetchone()

    if not row:
        raise HTTPException(401, "Invalid refresh token")

    user_id, expires_at = row

    # Проверяем срок действия
    from datetime import datetime
    if expires_at < datetime.utcnow():
        raise HTTPException(401, "Refresh token expired")

    # Генерируем новый access token
    new_access = create_access_token({"sub": str(user_id)})

    return {"access_token": new_access, "token_type": "bearer"}

# LOGOUT
@router.post("/logout")
async def logout(data: RefreshTokenBase, session: AsyncSession = Depends(get_session)):

    await session.execute(
        text("DELETE FROM refresh_tokens WHERE token = :token"),
        {"token": data.refresh_token}
    )
    await session.commit()

    return {"detail": "Logged out"}
 
protected_router = APIRouter(prefix="/users", 
                             tags=["User"],
                             dependencies=[Depends(get_current_user_with_permissions)]
                            )
 
# READ ALL
@protected_router.get("/", response_model=list[UserOut], dependencies=[Depends(require_permission(["users.get"]))])
async def get_all_user(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    return result.scalars().all()


# READ ONE
@protected_router.get("/{id}", response_model=UserOut, dependencies=[Depends(require_permission(["users.get"]))])
async def get_user(id: UUID, session: AsyncSession = Depends(get_session)):
    result = await session.get(User, id)
    if not result:
        raise HTTPException(404, "User not found")
    return result

# UPDATE
@protected_router.put("/{id}", response_model=UserOut, dependencies=[Depends(require_permission(["users.update"]))])
async def update_user(id: UUID, data: UserUpdate, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")

    for key, value in data.dict().items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user

# DELETE
@protected_router.delete("/{id}", dependencies=[Depends(require_permission(["users.delete"]))])
async def delete_user(id: UUID, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()
    return {"status": "deleted"}