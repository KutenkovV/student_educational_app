from typing import List
from pydantic import BaseModel
from uuid import UUID

class Config:
    orm_mode = True
    
#Специальности
class SpecialityBase(BaseModel):
    id_speciality: int
    speciality_name: str

class SpecialityCreate(SpecialityBase):
    pass

class SpecialityUpdate(SpecialityBase):
    pass

class SpecialityOut(SpecialityBase):
    id_speciality: int 
    speciality_name: str | None = None

#Студенты         
class StudentBase(BaseModel):
    id_student: int
    id_speciality: int
    name: str | None = None
    surname: str | None = None
    otchectvo: str | None = None
    admission_date: int | None = None
    group_number: int | None = None
    group_code: str | None = None
    record_book_number: int | None = None
        
class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass


class StudentOut(StudentBase):
    id_student: int
    id_speciality: int
    name: str | None = None
    surname: str | None = None
    otchectvo: str | None = None
    admission_date: int | None = None
    group_number: int | None = None
    group_code: str | None = None
    record_book_number: int | None = None
    
#Учебный план
class CurriculumBase(BaseModel):
    id_curriculum: int
    id_subject: int
    id_speciality: int
    semester: int
    
class CurriculumCreate(CurriculumBase):
    pass

class CurriculumUpdate(CurriculumBase):
    pass

class CurriculumOut(CurriculumBase):
    id_curriculum: int
    id_subject: int
    id_speciality: int
    semester: int

    
#Ведомость
class StatementBase(BaseModel):
    id_statement: int
    id_student: int
    id_subject: int
    grade: str
    semester: int
    
class StatementOut(StatementBase):
    id_statement: int
    id_student: int
    id_subject: int
    grade: str
    semester: int    

class StatementCreate(StatementBase):
    pass

class StatementUpdate(StatementBase):
    pass
    
#Предметы
class SubjectBase(BaseModel):
    id_subject: int
    subject_name: str
    hours_amount: int
    attestation_type: str

class SubjectOut(SubjectBase):
    id_subject: int
    subject_name: str
    hours_amount: int
    attestation_type: str
    
class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(SubjectBase):
    pass

#Роли
class RoleBase(BaseModel):
    id: UUID
    name: str

class RoleOut(RoleBase):
    pass
    
class RoleCreate(BaseModel):
    name: str

class RoleUpdate(BaseModel):
    name: str

#Пользователи
class UserBase(BaseModel):
    id: UUID
    login: str
    role_id: UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    
class UserCreate(BaseModel):
    login: str
    password: str
    role_id: UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    
class UserOut(UserBase):
    id: UUID
    login: str
    role_id: UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    
class UserUpdate(UserBase):
    id: UUID
    login: str
    password_hash: str
    role_id: UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    
class LoginRequest(BaseModel):
    login: str
    password: str
    
class UserWithPermissions(BaseModel):
    id: str
    role: str
    permissions: List[str]
    
#Рефреш токен
class RefreshTokenBase(BaseModel):
    refresh_token: str
    
class RefreshTokenCreate(RefreshTokenBase):
    pass