from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import async_session
from app.core.jwt import SECRET_KEY, ALGORITHM
from app.schemas import UserWithPermissions
from fastapi.security import HTTPBearer

security = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# ----------- SESSION DEPENDENCY -----------

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# ----------- DECODE TOKEN & GET USER ID -----------

async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> str:
    try:
        print(f"Decoding token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
        

        return user_id

    except JWTError:
            raise HTTPException(401, "Invalid token")


# ----------- LOAD USER + ROLE + PERMISSIONS -----------

async def get_current_user_with_permissions(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
) -> UserWithPermissions:
    print(f"Loading permissions for user_id: {user_id}")    
    query = text("""
        SELECT r.name AS role_name,
               ARRAY(
                   SELECT p.name
                   FROM role_permissions rp
                   JOIN permissions p ON rp.permission_id = p.id
                   WHERE rp.role_id = r.id
               ) AS permissions
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.id = :uid
    """)

    result = await session.execute(query, {"uid": user_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(401, "User not found")

    return UserWithPermissions(
        id=user_id,
        role=row.role_name,
        permissions=row.permissions
    )


# ----------- PERMISSION CHECK DEPENDENCY -----------

def require_permission(permission: str):
    async def checker(
        user: UserWithPermissions = Depends(get_current_user_with_permissions)
    ):
        # Super admin имеет все права
        if user.role == "super_admin":
            return user
        
        if permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' denied"
            )
        return user

    return checker
