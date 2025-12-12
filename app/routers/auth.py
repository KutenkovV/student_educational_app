from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.db import async_session
from uuid import UUID
from sqlalchemy import select

from app.models import User
from app.schemas import UserCreate, UserOut, UserUpdate, LoginRequest

router = APIRouter(prefix="/users", tags=["Auth"])

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/register")
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

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
 
 
# READ ALL
@router.get("/", response_model=list[UserOut])
async def get_all_user(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    return result.scalars().all()


# READ ONE
@router.get("/{id}", response_model=UserOut)
async def get_user(id: UUID, session: AsyncSession = Depends(get_session)):
    result = await session.get(User, id)
    if not result:
        raise HTTPException(404, "User not found")
    return result

# UPDATE
@router.put("/{id}", response_model=UserOut)
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
@router.delete("/{id}")
async def delete_user(id: UUID, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, id)
    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()
    return {"status": "deleted"}