from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    clients = relationship("Client", back_populates="owner")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="clients")
    tasks = relationship("Task", back_populates="client")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    status = Column(String)  # pending, ongoing, completed
    priority = Column(Integer)
    client_id = Column(Integer, ForeignKey("clients.id"))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    client = relationship("Client", back_populates="tasks")