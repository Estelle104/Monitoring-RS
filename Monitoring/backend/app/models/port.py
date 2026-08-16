# app/models/port.py
from sqlalchemy import Column, String, Integer, ForeignKey
from app.db import Base

class Port(Base):
    __tablename__ = "port"
    id = Column(String, primary_key=True)
    numero_port = Column(Integer)
    id_vlan = Column(String, ForeignKey("vlan.id"))
