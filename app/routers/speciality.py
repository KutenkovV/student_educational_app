from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import text
from app.core.dependencies import get_current_user_with_permissions, require_permission
from app.db import async_session
from app.models import Speciality
from app.schemas import SpecialityCreate, SpecialityUpdate, SpecialityOut

router = APIRouter(prefix="/speciality", 
                   tags=["Speciality"],
                   dependencies=[Depends(get_current_user_with_permissions)]
                )


async def get_session():
    async with async_session() as session:
        yield session


# CREATE
@router.post("/", response_model=SpecialityOut, dependencies=[Depends(require_permission(["speciality.create"]))])
async def create_speciality(data: SpecialityCreate, session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(
            text("CALL insert_speciality(:speciality_name)"),
            {"speciality_name": data.speciality_name}
        )
        await session.commit()
        
        result = await session.execute(
            select(Speciality).where(Speciality.speciality_name == data.speciality_name)
        )
        speciality = result.scalar_one()
    except Exception as e:
        msg = str(e)

        # оставим только часть после двоеточи
        if ":" in msg:
            msg = msg.split(":", 1)[1].strip()

        raise HTTPException(status_code=400, detail=msg)
    
    return speciality




# READ ALL
@router.get("/", response_model=list[SpecialityOut], dependencies=[Depends(require_permission("speciality.get"))])
async def get_all_specialities(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Speciality))
    return result.scalars().all()


# READ ONE
@router.get("/{id_speciality}", response_model=SpecialityOut, dependencies=[Depends(require_permission("speciality.get"))])
async def get_speciality(id_speciality: int, session: AsyncSession = Depends(get_session)):
    result = await session.get(Speciality, id_speciality)
    if not result:
        raise HTTPException(404, "Speciality not found")
    return result


# UPDATE
@router.put("/{speciality_id}", response_model=SpecialityOut, dependencies=[Depends(require_permission("speciality.update"))])
async def update_speciality(speciality_id: int, data: SpecialityUpdate, session: AsyncSession = Depends(get_session)):
    speciality = await session.get(Speciality, speciality_id)
    if not speciality:
        raise HTTPException(404, "Speciality not found")

    for key, value in data.dict().items():
        setattr(speciality, key, value)

    await session.commit()
    await session.refresh(speciality)
    return speciality


# DELETE
@router.delete("/{id_speciality}", dependencies=[Depends(require_permission("speciality.delete"))])
async def delete_speciality(id_speciality: int, session: AsyncSession = Depends(get_session)):
    speciality = await session.get(Speciality, id_speciality)
    if not speciality:
        raise HTTPException(404, "Speciality not found")

    await session.delete(speciality)
    await session.commit()
    return {"status": "deleted"}
