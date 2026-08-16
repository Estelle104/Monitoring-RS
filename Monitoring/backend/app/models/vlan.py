# app/models/vlan.py
from sqlalchemy import Column, String, Integer
from app.db import Base

class VLAN(Base):
    __tablename__ = "vlan"
    id = Column(String, primary_key=True, index=True)
    vlan = Column(Integer, unique=True, nullable=False)
    ip = Column(String, unique=True, nullable=False)
    id_salle = Column(String, nullable=False)
    