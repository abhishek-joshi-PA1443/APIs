from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel
from .db_connection import Base


class Employee(Base):
    __tablename__ = "employees"


    id = Column(Integer,primary_key=True, index=True)
    name = Column(String(25), index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String(20), index=True)
    role = Column(String, index=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)


class EmployeeCreate(BaseModel):
    name : str
    email : str
    password : str
    role : str
    manager_id : int | None=None


class EmployeeResponse(BaseModel):
    id :int
    name : str
    email : str
    password : str
    role : str
    manager_id : int

    class Config:
        orm_mode = True


class EmployeeUpdate(BaseModel):
    role : str
    manager_id : int

    class Config:
        orm_mode = True
