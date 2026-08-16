from sqlalchemy import Column, String, ForeignKey
from app.db import Base

class Machine(Base):
    __tablename__ = "machine"
    id = Column(String, primary_key=True)
    mac = Column(String, unique=True, nullable=False)
    etu = Column(String)
    hostname = Column(String)
    id_quota = Column(String, ForeignKey("quota.id"))
