from datetime import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, Float


class Route(SqlAlchemyBase):
    __tablename__ = 'routs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, index=True, nullable=False)
    path1 = Column(String)
    len1 = Column(Float)
    created_date = Column(DateTime, default=datetime.now)
