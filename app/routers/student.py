from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_current_user_with_permissions, require_permission
from app.db import async_session
from app.models import Student
from app.schemas import StudentOut, StudentCreate, StudentUpdate

router = APIRouter(prefix="/students", 
                   tags=["Student"],
                   dependencies=[Depends(get_current_user_with_permissions)]
                )

async def get_session():
    async with async_session() as session:
        yield session

# CREATE
@router.post("/", response_model=StudentOut, dependencies=[Depends(require_permission("students.create"))])
async def create_student(data: StudentCreate, session: AsyncSession = Depends(get_session)):
    student = Student(**data.dict())
    session.add(student)
    await session.commit()
    await session.refresh(student)
    
    if not student:
        raise HTTPException(404, "Students not found")
    
    return student

# READ ALL
@router.get("/", dependencies=[Depends(require_permission("students.get"))], response_model=list[StudentOut])
async def get_all_students(session: AsyncSession = Depends(get_session)):
    student = await session.execute(select(Student))
    return student.scalars().all()


# READ ONE
@router.get("/{id_student}", response_model=StudentOut, dependencies=[Depends(require_permission("students.get"))])
async def get_student(id_student: int, session: AsyncSession = Depends(get_session)):
    student = await session.get(Student, id_student)
    if not student:
        raise HTTPException(404, "Students not found")
    return student

# UPDATE
@router.put("/{id_student}", response_model=StudentOut, dependencies=[Depends(require_permission("students.update"))])
async def update_student(id_student: int, data: StudentUpdate, session: AsyncSession = Depends(get_session)):
    student = await session.get(Student, id_student)
    if not student:
        raise HTTPException(404, "Student not found")

    for key, value in data.dict().items():
        setattr(student, key, value)

    await session.commit()
    await session.refresh(student)
    return student

# DELETE
@router.delete("/{id_student}", dependencies=[Depends(require_permission("students.delete"))])
async def delete_student(id_student: int, session: AsyncSession = Depends(get_session)):
    student = await session.get(Student, id_student)
    if not student:
        raise HTTPException(404, "Student not found")

    await session.delete(student)
    await session.commit()
    return {"status": "deleted"}
