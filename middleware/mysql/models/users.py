from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .base import BaseSchema


class UserSchema(BaseSchema):

    __tablename__ = "users"
    uid: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(100), nullable=False)