import enum
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# Определяем Python Enum, соответствующий user_role_enum в БД
class UserRoleEnum(enum.Enum):
    Administrator = 'Administrator'
    Manager = 'Manager'
    Staff = 'Staff'
    Guest = 'Guest'

class Role(Base):
    """Модель для таблицы Role."""
    __tablename__ = 'role'

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    # Используем SQLEnum для связи с типом ENUM в PostgreSQL
    role_name = Column(SQLEnum(UserRoleEnum, name='user_role_enum', create_type=False), nullable=False)
    description = Column(String)
    permissions = Column(String)

    def __repr__(self):
        return f"<Role(role_id={self.role_id}, role_name='{self.role_name.value}')>"

class User(Base):
    """Модель для таблицы Users."""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('role.role_id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    is_blocked = Column(Boolean, nullable=False, default=False)
    failed_attempts = Column(Integer, nullable=False, default=0)
    last_login = Column(TIMESTAMP(timezone=False), nullable=True)

    # Связь "многие к одному": у пользователя одна роль
    role = relationship("Role")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, login='{self.login}', role_id={self.role_id})>"