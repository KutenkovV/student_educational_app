from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db import get_session, async_session

from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook

router = APIRouter(prefix="/reports", tags=["Reports"])

async def get_session():
    async with async_session() as session:
        yield session
        
@router.get("/school-plan")
async def get_school_plan(
    id_speciality: int,
    start_year: int,
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT *
        FROM report_school_plan(:id_speciality, :start_year)
    """)
    result = await session.execute(
        query,
        {"id_speciality": id_speciality, "start_year": start_year}
    )

    rows = result.mappings().all()
    return rows

@router.get("/school-plan/xlsx")
async def download_school_plan_xlsx(
    id_speciality: int,
    start_year: int,
    session: AsyncSession = Depends(get_session)
):
    query = text("""
        SELECT *
        FROM report_school_plan(:id_speciality, :start_year)
    """)
    result = await session.execute(
        query,
        {"id_speciality": id_speciality, "start_year": start_year}
    )

    rows = result.mappings().all()

    wb = Workbook()
    ws = wb.active
    ws.title = "School Plan"

    headers = [
        "Специальность",
        "Год начала",
        "Предмет",
        "Часы",
        "Семестр",
        "Тип аттестации"
    ]
    ws.append(headers)

    for row in rows:
        ws.append([
            row["speciality_name"],
            row["start_year"],
            row["subject_name"],
            row["hours_amount"],
            row["semester"],
            row["attestation_type"]
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=school_plan.xlsx"
        }
    )