import uuid  # Import Python's uuid module
from sqlalchemy import Column, Integer, String
from .db import Base
from sqlalchemy.dialects.postgresql import UUID  # Import Postgres UUID type

#Таблица "Специальности"
class Speciality(Base):
    __tablename__ = "speciality"

    id_speciality = Column(Integer, primary_key=True)
    speciality_name = Column(String, nullable=True)
    
    
#Таблица "Студенты"
class Student(Base):
    __tablename__ = "student"

    id_student = Column(Integer, primary_key=True)
    id_speciality = Column(Integer, nullable=False)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    otchectvo = Column(String, nullable=True)
    admission_date = Column(Integer, nullable=True)
    group_number = Column(Integer, nullable=True)
    group_code = Column(String, nullable=True)
    record_book_number = Column(Integer, nullable=True)

#Таблица "Учебный план"    
class Curriculum(Base):
    __tablename__ = "curriculum"

    id_curriculum = Column(Integer, primary_key=True)
    id_subject = Column(Integer, nullable=False)
    id_speciality = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)

#Таблица "Ведомость"
class Statement(Base):
    __tablename__ = "statement"

    id_statement = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)
    id_subject = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)

#Таблица "Предметы"    
class Subject(Base):
    __tablename__ = "subject"

    id_subject = Column(Integer, primary_key=True)
    subject_name = Column(String, nullable=False)
    hours_amount = Column(Integer, nullable=False)
    attestation_type = Column(String, nullable=False)
    
#Таблица "Пользователи"
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)

def generate_uuid():
    return str(uuid.uuid4())
   
#Таблица "Роли"
class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)