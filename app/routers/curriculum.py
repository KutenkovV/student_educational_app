from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import text
from app.core.dependencies import get_current_user_with_permissions, require_permission
from app.db import async_session
from app.models import Curriculum
from app.schemas import CurriculumCreate, CurriculumUpdate, CurriculumOut

router = APIRouter(prefix="/curriculums", 
                   tags=["Curriculum"], 
                   dependencies=[Depends(get_current_user_with_permissions)]
                )


async def get_session():
    async with async_session() as session:
        yield session


# CREATE
@router.post("/", response_model=CurriculumOut, dependencies=[Depends(require_permission("curriculums.create"))])
async def create_curriculum(data: CurriculumCreate, session: AsyncSession = Depends(get_session)):
    try:
        curriculum = Curriculum(**data.dict())
        session.add(curriculum)
        await session.commit()
        await session.refresh(curriculum)

    except Exception as e:
        msg = str(e)

        # оставим только часть после двоеточи
        if ":" in msg:
            msg = msg.split(":", 1)[1].strip()

        raise HTTPException(status_code=400, detail=msg)
    
    return curriculum


# READ ALL
@router.get("/", response_model=list[CurriculumOut], dependencies=[Depends(require_permission("curriculums.get"))])
async def get_all_curriculums(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Curriculum))
    return result.scalars().all()


# READ ONE
@router.get("/{id_curriculum}", response_model=CurriculumOut, dependencies=[Depends(require_permission("curriculums.get"))])
async def get_curriculum(id_curriculum: int, session: AsyncSession = Depends(get_session)):
    result = await session.get(Curriculum, id_curriculum)
    if not result:
        raise HTTPException(404, "Curriculum not found")
    return result


# UPDATE
@router.put("/{id_curriculum}", response_model=CurriculumOut, dependencies=[Depends(require_permission("curriculums.update"))])
async def update_curriculum(id_curriculum: int, data: CurriculumUpdate, session: AsyncSession = Depends(get_session)):
    curriculum = await session.get(Curriculum, id_curriculum)
    if not curriculum:
        raise HTTPException(404, "Curriculum not found")

    for key, value in data.dict().items():
        setattr(curriculum, key, value)

    await session.commit()
    await session.refresh(curriculum)
    return curriculum


# DELETE
@router.delete("/{id_curriculum}", dependencies=[Depends(require_permission("curriculums.delete"))])
async def delete_curriculum(id_curriculum: int, session: AsyncSession = Depends(get_session)):
    curriculum = await session.get(Curriculum, id_curriculum)
    if not curriculum:
        raise HTTPException(404, "curriculum not found")

    await session.delete(curriculum)
    await session.commit()
    return {"status": "deleted"}
