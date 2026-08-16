# app/models/login.py
from sqlalchemy import Column, String, Integer
from app.models import Base

class Login(Base):
    __tablename__ = "login"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    pwd = Column(String, nullable=False)
    code = Column(String, nullable=False)
    role = Column(String, nullable=False)
