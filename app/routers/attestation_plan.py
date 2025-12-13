from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db import get_session

from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd

router = APIRouter(prefix="/reports/attestation-plan", tags=["Attestation plan"])


@router.get("/")
async def get_attestation_plan(
    id_speciality: int,
    semester: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        text("SELECT * FROM report_attestation_plan(:id_speciality, :semester)"),
        {"id_speciality": id_speciality, "semester": semester}
    )
    return [dict(row) for row in result.mappings()]

@router.get("/xlsx")
async def download_attestation_plan_xlsx(
    id_speciality: int,
    semester: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        text("SELECT * FROM report_attestation_plan(:id_speciality, :semester)"),
        {"id_speciality": id_speciality, "semester": semester}
    )

    rows = result.mappings().all()
    df = pd.DataFrame(rows)

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=attestation_plan.xlsx"
        }
    )