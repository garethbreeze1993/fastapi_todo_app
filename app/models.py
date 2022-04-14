from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    deadline = Column(Date())
    completed = Column(Boolean(create_constraint=False), default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id', name='tasks_owner_id_fkey', ondelete='CASCADE'), nullable=False)
    creation_date = Column(DateTime(), server_default=text('now()'))
    last_update = Column(DateTime(), server_default=text('now()'), onupdate=text('now()'))

    owner = relationship('User')
