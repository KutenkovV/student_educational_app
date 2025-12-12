from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import text
from app.db import async_session
from app.models import Statement
from app.schemas import StatementCreate, StatementUpdate, StatementOut

router = APIRouter(prefix="/statements", tags=["Statement"])


async def get_session():
    async with async_session() as session:
        yield session


# CREATE
@router.post("/", response_model=StatementOut)
async def create_statement(data: StatementCreate, session: AsyncSession = Depends(get_session)):
    try:
        statement = Statement(**data.dict())
        session.add(statement)
        await session.commit()
        await session.refresh(statement)

    except Exception as e:
        msg = str(e)

        # оставим только часть после двоеточи
        if ":" in msg:
            msg = msg.split(":", 1)[1].strip()

        raise HTTPException(status_code=400, detail=msg)
    
    return statement


# READ ALL
@router.get("/", response_model=list[StatementOut])
async def get_all_statements(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Statement))
    return result.scalars().all()


# READ ONE
@router.get("/{id_statement}", response_model=StatementOut)
async def get_statement(id_statement: int, session: AsyncSession = Depends(get_session)):
    result = await session.get(Statement, id_statement)
    if not result:
        raise HTTPException(404, "Statement not found")
    return result


# UPDATE
@router.put("/{id_statement}", response_model=StatementOut)
async def update_statement(id_statement: int, data: StatementUpdate, session: AsyncSession = Depends(get_session)):
    statement = await session.get(Statement, id_statement)
    if not statement:
        raise HTTPException(404, "Statement not found")

    for key, value in data.dict().items():
        setattr(statement, key, value)

    await session.commit()
    await session.refresh(statement)
    return statement


# DELETE
@router.delete("/{id_statement}")
async def delete_statement(id_statement: int, session: AsyncSession = Depends(get_session)):
    statement = await session.get(Statement, id_statement)
    if not statement:
        raise HTTPException(404, "Statement not found")

    await session.delete(statement)
    await session.commit()
    return {"status": "deleted"}
