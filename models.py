from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(25))
    description = Column(String(100))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
