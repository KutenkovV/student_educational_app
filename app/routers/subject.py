from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_current_user_with_permissions, require_permission
from app.db import async_session
from app.models import Subject
from app.schemas import SubjectCreate, SubjectUpdate, SubjectOut

router = APIRouter(prefix="/subjects", 
                   tags=["Subject"], 
                   dependencies=[Depends(get_current_user_with_permissions)]
                )

async def get_session():
    async with async_session() as session:
        yield session

# CREATE
@router.post("/", dependencies=[Depends(require_permission("subjects.create"))], response_model=SubjectOut)
async def create_subject(data: SubjectCreate, session: AsyncSession = Depends(get_session)):
    try:
        subject = Subject(**data.dict())
        session.add(subject)
        await session.commit()
        await session.refresh(subject)

    except Exception as e:
        msg = str(e)

        # оставим только часть после двоеточи
        if ":" in msg:
            msg = msg.split(":", 1)[1].strip()

        raise HTTPException(status_code=400, detail=msg)
    
    return subject

# READ ALL
@router.get("/", dependencies=[Depends(require_permission("subjects.get"))], response_model=SubjectOut, )
async def get_all_subjects(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Subject))
    return result.scalars().all()


# READ ONE
@router.get("/{id_subject}", dependencies=[Depends(require_permission("subjects.get"))], response_model=SubjectOut)
async def get_subject(id_subject: int, session: AsyncSession = Depends(get_session)):
    result = await session.get(Subject, id_subject)
    if not result:
        raise HTTPException(404, "Subject not found")
    return result

# UPDATE
@router.put("/{id_subject}", dependencies=[Depends(require_permission("subjects.update"))], response_model=SubjectOut)
async def update_subject(id_subject: int, data: SubjectUpdate, session: AsyncSession = Depends(get_session)):
    subject = await session.get(Subject, id_subject)
    if not subject:
        raise HTTPException(404, "Subject not found")

    for key, value in data.dict().items():
        setattr(subject, key, value)

    await session.commit()
    await session.refresh(subject)
    return subject

# DELETE
@router.delete("/{id_subject}", dependencies=[Depends(require_permission("subjects.delete"))])
async def delete_subject(id_subject: int, session: AsyncSession = Depends(get_session)):
    subject = await session.get(Subject, id_subject)
    if not subject:
        raise HTTPException(404, "Subject not found")

    await session.delete(subject)
    await session.commit()
    return {"status": "deleted"}