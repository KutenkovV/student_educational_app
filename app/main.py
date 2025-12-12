from fastapi import FastAPI

from app.db import engine, Base
from app.routers.speciality import router as speciality_router
from app.routers.student import router as student_router
from app.routers.curriculum import router as curriculum_router
from app.routers.statement import router as statement_router
from app.routers.subject import router as subject_router
from app.routers.role import router as role_router
from app.routers.auth import router as auth_router
from app.routers.auth import protected_router as user_router

app = FastAPI()

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