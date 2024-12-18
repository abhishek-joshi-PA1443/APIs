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