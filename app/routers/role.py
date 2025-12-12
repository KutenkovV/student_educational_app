from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import async_session
from app.models import Role
from app.schemas import RoleCreate, RoleUpdate, RoleOut

router = APIRouter(prefix="/roles", tags=["Role"])

async def get_session():
    async with async_session() as session:
        yield session


# CREATE
@router.post("/", response_model=RoleOut)
async def create_role(data: RoleCreate, session: AsyncSession = Depends(get_session)):
    try:
        role = Role(name=data.name)
        session.add(role)
        await session.commit()
        await session.refresh(role)
        
    except Exception as e:
        msg = str(e)

        # оставим только часть после двоеточи
        if ":" in msg:
            msg = msg.split(":", 1)[1].strip()

        raise HTTPException(status_code=400, detail=msg)
    
    return role


# READ ALL
@router.get("/", response_model=list[RoleOut])
async def get_all_roles(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Role))
    return result.scalars().all()


# READ ONE
@router.get("/{id}", response_model=RoleOut)
async def get_role(id: str, session: AsyncSession = Depends(get_session)):
    result = await session.get(Role, id)
    if not result:
        raise HTTPException(404, "Role not found")
    return result

# UPDATE
@router.put("/{id}", response_model=RoleOut)
async def update_role(id: str, data: RoleUpdate, session: AsyncSession = Depends(get_session)):
    role = await session.get(Role, id)
    if not role:
        raise HTTPException(404, "Role not found")

    for key, value in data.dict().items():
        setattr(role, key, value)

    await session.commit()
    await session.refresh(role)
    return role


# DELETE
@router.delete("/{id}")
async def delete_role(id: str, session: AsyncSession = Depends(get_session)):
    role = await session.get(Role, id)
    if not role:
        raise HTTPException(404, "Role not found")

    await session.delete(role)
    await session.commit()
    return {"status": "deleted"}
