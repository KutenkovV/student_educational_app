from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import async_session
from app.schemas import StudentPersonalCard

from fastapi.responses import StreamingResponse
import openpyxl
from io import BytesIO

router = APIRouter(prefix="/reports", tags=["Student card"])


async def get_session():
    async with async_session() as session:
        yield session

@router.get("/student-card/{record_book_number}", response_model=list[StudentPersonalCard])
async def get_student_personal_card(
    record_book_number: int,
    session: AsyncSession = Depends(get_session),
):
    query = text("""
        SELECT *
        FROM student_personal_card(:record_book_number)
    """)

    result = await session.execute(
        query, {"record_book_number": record_book_number}
    )

    return result.mappings().all()

#Скачать карточку студента в .xlsx
@router.get("student-card/{record_book_number}/xlsx")
async def download_student_card_xlsx(
    record_book_number: int,
    db: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT * 
        FROM student_personal_card(:record_book_number)
    """)

    result = await db.execute(query, {"record_book_number": record_book_number})
    rows = result.mappings().all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student card"

    headers = rows[0].keys() if rows else []
    ws.append(list(headers))

    for row in rows:
        ws.append(list(row.values()))

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=student_card_{record_book_number}.xlsx"
        }
    )