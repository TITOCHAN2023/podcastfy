from .base import BaseSchema
from .users import UserSchema
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

class SessionSchema(BaseSchema):
    __tablename__ = "session"
    sid: int = Column(Integer, primary_key=True, autoincrement=True)
    uid: int = Column(Integer, ForeignKey(UserSchema.uid, ondelete="CASCADE"), nullable=False)
    voice: str = Column(String(255), nullable=False)
    sessionname: str = Column(String(255), nullable=False)
    create_at: datetime = Column(DateTime, default=datetime.now)