from sqlalchemy import Column, Integer, String, Enum
import enum
from .database import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"



class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)


