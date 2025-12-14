from fastapi import FastAPI
from app.db import engine, Base
from fastapi.middleware.cors import CORSMiddleware

from app.routers.speciality import router as speciality_router
from app.routers.student import router as student_router
from app.routers.curriculum import router as curriculum_router
from app.routers.statement import router as statement_router
from app.routers.subject import router as subject_router
from app.routers.role import router as role_router
from app.routers.auth import router as auth_router
from app.routers.auth import protected_router as user_router
from app.routers.student_card import router as student_card_router
from app.routers.school_plan import router as school_plan
from app.routers.attestation_plan import router as attestation_plan
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Student Educational App API",
    description="API для работы с образовательной системой: студенты, предметы, учебные планы, аттестации",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # Redoc
    openapi_url="/openapi.json",
    swagger_ui_init_oauth={}
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(speciality_router)
app.include_router(student_router)
app.include_router(curriculum_router)
app.include_router(statement_router)
app.include_router(subject_router)
app.include_router(role_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(student_card_router)
app.include_router(school_plan)
app.include_router(attestation_plan)